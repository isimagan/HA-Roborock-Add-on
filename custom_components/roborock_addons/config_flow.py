"""Config flow for Roborock Add-ons."""

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry, ConfigFlowResult, OptionsFlow
from homeassistant.core import callback

from .const import ALL_ENTITIES, CONF_ENABLED_ENTITIES, DOMAIN, ROBOROCK_DOMAIN


def _selection_schema(selected: set[str]) -> vol.Schema:
    """Return the entity-selection schema."""
    return vol.Schema(
        {
            vol.Optional(entity, default=entity in selected): bool
            for entity in ALL_ENTITIES
        }
    )


def _enabled_entities(user_input: dict[str, Any]) -> list[str]:
    """Return enabled entity keys from a completed form."""
    return [entity for entity in ALL_ENTITIES if user_input.get(entity, False)]


class RoborockAddonsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Roborock Add-ons."""

    VERSION = 1
    MINOR_VERSION = 2

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle setup initiated by the user."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if not self.hass.config_entries.async_entries(ROBOROCK_DOMAIN):
            return self.async_abort(reason="roborock_not_configured")

        if user_input is not None:
            return self.async_create_entry(
                title="Roborock Add-ons",
                data={CONF_ENABLED_ENTITIES: _enabled_entities(user_input)},
            )

        return self.async_show_form(
            step_id="user",
            data_schema=_selection_schema(set(ALL_ENTITIES)),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Return the options flow."""
        return RoborockAddonsOptionsFlow(config_entry)


class RoborockAddonsOptionsFlow(OptionsFlow):
    """Handle Roborock Add-ons options."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize the options flow."""
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Allow the enabled entities to be changed."""
        if user_input is not None:
            return self.async_create_entry(
                title="",
                data={CONF_ENABLED_ENTITIES: _enabled_entities(user_input)},
            )

        selected = set(
            self._config_entry.options.get(
                CONF_ENABLED_ENTITIES,
                self._config_entry.data.get(CONF_ENABLED_ENTITIES, ALL_ENTITIES),
            )
        )
        return self.async_show_form(
            step_id="init",
            data_schema=_selection_schema(selected),
        )
