"""Config flow for Roborock Add-ons."""

import voluptuous as vol

from homeassistant import config_entries

from .const import DOMAIN, ROBOROCK_DOMAIN


class RoborockAddonsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Roborock Add-ons."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, object] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle setup initiated by the user."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if not self.hass.config_entries.async_entries(ROBOROCK_DOMAIN):
            return self.async_abort(reason="roborock_not_configured")

        if user_input is not None:
            return self.async_create_entry(title="Roborock Add-ons", data={})

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
        )
