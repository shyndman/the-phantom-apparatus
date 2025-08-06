"""Config flow for The Phantom Apparatus."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.helpers import selector
from slugify import slugify

from .const import DOMAIN


class PhantomApparatusFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for The Phantom Apparatus."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            # Validate entity selections
            for entity_key in ["tv_entity", "jellyfin_entity", "ghosttube_entity"]:
                if (
                    entity_id := user_input.get(entity_key)
                ) and not self.hass.states.get(entity_id):
                    _errors[entity_key] = "entity_not_found"

            if not _errors:
                await self.async_set_unique_id(slugify(user_input[CONF_NAME]))
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_NAME,
                        default=(user_input or {}).get(CONF_NAME, "Living Room TV"),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                    vol.Required(
                        "tv_entity",
                        default=(user_input or {}).get(
                            "tv_entity", "media_player.lg_webos_tv_nano80upa"
                        ),
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain="media_player",
                        ),
                    ),
                    vol.Required(
                        "jellyfin_entity",
                        default=(user_input or {}).get(
                            "jellyfin_entity", "media_player.jellyfin_living_room_tv"
                        ),
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain="media_player",
                        ),
                    ),
                    vol.Required(
                        "ghosttube_entity",
                        default=(user_input or {}).get(
                            "ghosttube_entity", "media_player.living_room_tv_ghosttube"
                        ),
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain="media_player",
                        ),
                    ),
                },
            ),
            errors=_errors,
        )
