from __future__ import annotations

import random
from collections import deque
from dataclasses import dataclass
from typing import List

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components import media_source
from homeassistant.helpers.storage import Store

from .const import (
    CONF_MEDIA_FOLDER_ID,
    CONF_PLAYER_ENTITY_ID,
    CONF_MAX_HISTORY,
    DEFAULT_MAX_HISTORY,
)

STORE_VERSION = 1
STORE_KEY_FMT = "yandex_local_music.{entry_id}.index"


@dataclass
class Track:
    media_content_id: str
    title: str
    mime: str


def _guess_mime(filename: str) -> str:
    fn = filename.lower()
    if fn.endswith(".mp3"):
        return "audio/mpeg"
    if fn.endswith(".m4a"):
        return "audio/mp4"
    if fn.endswith(".aac"):
        return "audio/aac"
    if fn.endswith(".ogg") or fn.endswith(".opus"):
        return "audio/ogg"
    if fn.endswith(".wav"):
        return "audio/wav"
    return "audio/mpeg"


class YLMCoordinator:
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry

        self.player_entity_id: str = entry.data[CONF_PLAYER_ENTITY_ID]
        self.folder_id: str = entry.data[CONF_MEDIA_FOLDER_ID]
        self.max_history: int = entry.options.get(
            CONF_MAX_HISTORY, DEFAULT_MAX_HISTORY
        )

        self._store = Store(
            hass,
            STORE_VERSION,
            STORE_KEY_FMT.format(entry_id=entry.entry_id),
        )
        self._tracks: List[Track] = []
        self._history: deque[str] = deque(maxlen=self.max_history)

    async def async_initialize(self) -> None:
        saved = await self._store.async_load()
        if saved and isinstance(saved.get("tracks"), list):
            self._tracks = [Track(**t) for t in saved["tracks"]]

        await self.async_rebuild_index()

    # РЕКУРСИВНЫЙ ОБХОД
    async def _browse_recursive(self, media_id: str, tracks: List[Track]) -> None:
        node = await media_source.async_browse_media(self.hass, media_id)

        for child in getattr(node, "children", []) or []:
            # Папка → уходим глубже
            if getattr(child, "children", None) is not None:
                await self._browse_recursive(child.media_content_id, tracks)
                continue

            # Музыкальный файл
            if getattr(child, "media_class", None) == "music":
                title = child.title or child.media_content_id.rsplit("/", 1)[-1]
                mime = _guess_mime(title)
                tracks.append(
                    Track(
                        media_content_id=child.media_content_id,
                        title=title,
                        mime=mime,
                    )
                )

    async def async_rebuild_index(self) -> int:
        tracks: List[Track] = []
        await self._browse_recursive(self.folder_id, tracks)

        # Сортировка по имени
        tracks.sort(key=lambda t: t.title.lower())

        self._tracks = tracks
        await self._store.async_save({"tracks": [t.__dict__ for t in tracks]})

        return len(tracks)

    def pick_random_track(self) -> Track | None:
        if not self._tracks:
            return None

        # исключаем недавние повторы
        candidates = [
            t for t in self._tracks if t.media_content_id not in self._history
        ]

        if not candidates:
            candidates = self._tracks[:]  # всё уже было — разрешаем повтор

        chosen = random.choice(candidates)
        self._history.append(chosen.media_content_id)
        return chosen
