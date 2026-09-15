"""Select entities for Roborock Add-ons."""

from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import CONF_ENABLED_ENTITIES, ENTITY_FAN_SPEED
from .helpers import RoborockAddonEntity, RoborockVacuumInfo, async_get_roborock_vacuums

ATTR_FAN_SPEED = "fan_speed"
ATTR_FAN_SPEED_LIST = "fan_speed_list"


def _display_option(option: str) -> str:
    """Format a Roborock fan-speed option for display."""
    if option.endswith("_plus"):
        option = f"{option[:-5]}+"
    return option.replace("_", " ").title()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up selected Roborock Add-ons select entities."""
    enabled = entry.options.get(
        CONF_ENABLED_ENTITIES, entry.data.get(CONF_ENABLED_ENTITIES, [])
    )
    if ENTITY_FAN_SPEED not in enabled:
        return
    async_add_entities(
        RoborockFanSpeedSelect(vacuum)
        for vacuum in async_get_roborock_vacuums(hass)
    )


class RoborockFanSpeedSelect(RoborockAddonEntity, SelectEntity):
    """Select the fan speed of a Roborock vacuum."""

    _attr_translation_key = "fan_speed"

    def __init__(self, vacuum: RoborockVacuumInfo) -> None:
        """Initialize the fan-speed select."""
        super().__init__(vacuum, ENTITY_FAN_SPEED)

    def _raw_options(self) -> list[str]:
        state = self.hass.states.get(self.vacuum.entity_id)
        if state is None:
            return []
        options = state.attributes.get(ATTR_FAN_SPEED_LIST, [])
        return [option for option in options if isinstance(option, str)]

    @property
    def options(self) -> list[str]:
        """Return formatted fan-speed options."""
        return [_display_option(option) for option in self._raw_options()]

    @property
    def current_option(self) -> str | None:
        """Return the active fan speed."""
        state = self.hass.states.get(self.vacuum.entity_id)
        if state is None:
            return None
        option = state.attributes.get(ATTR_FAN_SPEED)
        return _display_option(option) if isinstance(option, str) else None

    async def async_select_option(self, option: str) -> None:
        """Set the selected fan speed on the source vacuum."""
        raw_option = next(
            (raw for raw in self._raw_options() if _display_option(raw) == option),
            option,
        )
        await self.hass.services.async_call(
            "vacuum",
            "set_fan_speed",
            {ATTR_ENTITY_ID: self.vacuum.entity_id, ATTR_FAN_SPEED: raw_option},
            blocking=True,
        )
