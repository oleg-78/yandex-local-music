from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries

from .const import DOMAIN


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title="Yandex Local Music",
                data=user_input,
            )

        schema = vol.Schema(
            {
                vol.Required("player_entity_id"): str,
                vol.Required("media_folder_id"): str,
                vol.Optional("max_history", default=10): vol.Coerce(int),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
        )