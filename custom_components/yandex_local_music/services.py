from __future__ import annotations

from homeassistant.core import HomeAssistant, ServiceCall

from .const import (
    DOMAIN,
    SERVICE_REBUILD_INDEX,
    SERVICE_PLAY_RANDOM,
    SERVICE_PLAY_SPECIFIC,
    ATTR_TRACK_ID,
    ATTR_VOLUME,
    ATTR_TARGET_PLAYER,
)

_SERVICES_REGISTERED: bool = False


def _get_all_coordinators(hass: HomeAssistant):
    """Return all coordinators for this integration."""
    return list(hass.data.get(DOMAIN, {}).values())


async def async_setup_services(hass: HomeAssistant) -> None:
    """Register services for Yandex Local Music."""
    global _SERVICES_REGISTERED

    if _SERVICES_REGISTERED:
        return

    async def handle_rebuild(call: ServiceCall) -> None:
        for coordinator in _get_all_coordinators(hass):
            await coordinator.async_rebuild_index()

    async def handle_play_random(call: ServiceCall) -> None:
        volume = call.data.get(ATTR_VOLUME)
        target_player = call.data.get(ATTR_TARGET_PLAYER)

        for coordinator in _get_all_coordinators(hass):
            # Если указана конкретная колонка — играем только на ней
            if target_player and coordinator.player_entity_id != target_player:
                continue

            track = coordinator.pick_random_track()
            if track is None:
                continue

            # Optional volume preset
            if volume is not None:
                await hass.services.async_call(
                    "media_player",
                    "volume_set",
                    {
                        "entity_id": coordinator.player_entity_id,
                        "volume_level": float(volume),
                    },
                    blocking=True,
                )

            # Play selected track (silent, direct mp3)
            await hass.services.async_call(
                "media_player",
                "play_media",
                {
                    "entity_id": coordinator.player_entity_id,
                    "media": {
                        "media_content_id": track.media_content_id,
                        "media_content_type": track.mime,
                        "metadata": {
                            "title": track.title,
                            "media_class": "music",
                        },
                    },
                },
                blocking=False,
            )

    async def handle_play_specific(call: ServiceCall) -> None:
        track_id = call.data.get(ATTR_TRACK_ID)
        target_player = call.data.get(ATTR_TARGET_PLAYER)

        if not track_id:
            return

        for coordinator in _get_all_coordinators(hass):
            if target_player and coordinator.player_entity_id != target_player:
                continue

            await hass.services.async_call(
                "media_player",
                "play_media",
                {
                    "entity_id": coordinator.player_entity_id,
                    "media": {
                        "media_content_id": track_id,
                        "media_content_type": "audio/mpeg",
                        "metadata": {
                            "media_class": "music",
                        },
                    },
                },
                blocking=False,
            )

    hass.services.async_register(
        DOMAIN,
        SERVICE_REBUILD_INDEX,
        handle_rebuild,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_PLAY_RANDOM,
        handle_play_random,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_PLAY_SPECIFIC,
        handle_play_specific,
    )

    _SERVICES_REGISTERED = True


async def async_unload_services(hass: HomeAssistant) -> None:
    """Unregister services."""
    global _SERVICES_REGISTERED

    if not _SERVICES_REGISTERED:
        return

    hass.services.async_remove(DOMAIN, SERVICE_REBUILD_INDEX)
    hass.services.async_remove(DOMAIN, SERVICE_PLAY_RANDOM)
    hass.services.async_remove(DOMAIN, SERVICE_PLAY_SPECIFIC)

    _SERVICES_REGISTERED = False