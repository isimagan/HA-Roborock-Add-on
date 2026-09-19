"""Switch entities for Roborock Add-ons."""

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import Event, HomeAssistant, State, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import CONF_ENABLED_ENTITIES, ENTITY_STOP_BEFORE_DOCK
from .helpers import RoborockAddonEntity, RoborockVacuumInfo, async_get_roborock_vacuums

_LOGGER = logging.getLogger(__name__)

STATE_DOCKED = "docked"
STATE_RETURNING = "returning"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up selected Roborock Add-ons switch entities."""
    enabled = entry.options.get(
        CONF_ENABLED_ENTITIES, entry.data.get(CONF_ENABLED_ENTITIES, [])
    )
    if ENTITY_STOP_BEFORE_DOCK not in enabled:
        return
    async_add_entities(
        RoborockStopBeforeDockSwitch(vacuum)
        for vacuum in async_get_roborock_vacuums(hass)
    )


class RoborockStopBeforeDockSwitch(RoborockAddonEntity, SwitchEntity):
    """Stop a Roborock once when it starts returning to its dock."""

    _attr_is_on = False
    _attr_translation_key = "stop_before_dock"

    def __init__(self, vacuum: RoborockVacuumInfo) -> None:
        """Initialize the stop-before-dock switch."""
        super().__init__(vacuum, ENTITY_STOP_BEFORE_DOCK)
        self._stop_in_progress = False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Arm the switch for the next return-to-dock transition."""
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disarm the switch."""
        self._attr_is_on = False
        self.async_write_ha_state()

    @callback
    def _handle_source_update(self, event: Event[Any]) -> None:
        """React to vacuum state changes and refresh availability."""
        new_state: State | None = event.data.get("new_state")
        old_state: State | None = event.data.get("old_state")
        if new_state is None or new_state.entity_id != self.vacuum.entity_id:
            self.async_write_ha_state()
            return

        if new_state.state == STATE_DOCKED:
            if self.is_on:
                self._attr_is_on = False
            self.async_write_ha_state()
            return

        if (
            new_state.state == STATE_RETURNING
            and (old_state is None or old_state.state != STATE_RETURNING)
            and self.is_on
            and not self._stop_in_progress
        ):
            self._stop_in_progress = True
            self.hass.async_create_task(self._async_stop_vacuum())

        self.async_write_ha_state()

    async def _async_stop_vacuum(self) -> None:
        """Stop the vacuum and disarm after the command succeeds."""
        try:
            await self.hass.services.async_call(
                "vacuum",
                "stop",
                {ATTR_ENTITY_ID: self.vacuum.entity_id},
                blocking=True,
            )
        except HomeAssistantError:
            _LOGGER.exception(
                "Unable to stop %s before docking", self.vacuum.entity_id
            )
        else:
            self._attr_is_on = False
        finally:
            self._stop_in_progress = False
            self.async_write_ha_state()
