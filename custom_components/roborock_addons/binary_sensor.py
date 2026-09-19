"""Binary sensor entities for Roborock Add-ons."""

from datetime import timedelta

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_OFF, STATE_ON, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.util import dt as dt_util

from .const import (
    CONF_ENABLED_ENTITIES,
    ENTITY_OFF_PEAK,
    ENTITY_WATER_EQUIPMENT,
    SOURCE_MOP_ATTACHED,
    SOURCE_OFF_PEAK_END,
    SOURCE_OFF_PEAK_START,
    SOURCE_OFF_PEAK_SWITCH,
    SOURCE_WATER_BOX_ATTACHED,
    SOURCE_WATER_SHORTAGE,
)
from .helpers import (
    RoborockAddonEntity,
    RoborockVacuumInfo,
    async_get_roborock_vacuums,
    parse_time_state,
    time_is_in_window,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up selected Roborock Add-ons binary sensors."""
    enabled = entry.options.get(
        CONF_ENABLED_ENTITIES, entry.data.get(CONF_ENABLED_ENTITIES, [])
    )
    entities: list[BinarySensorEntity] = []
    for vacuum in async_get_roborock_vacuums(hass):
        if ENTITY_OFF_PEAK in enabled:
            entities.append(RoborockOffPeakBinarySensor(vacuum))
        if ENTITY_WATER_EQUIPMENT in enabled:
            entities.append(RoborockWaterEquipmentBinarySensor(vacuum))
    async_add_entities(entities)


class RoborockOffPeakBinarySensor(RoborockAddonEntity, BinarySensorEntity):
    """Report whether the current time is in the configured off-peak window."""

    _attr_device_class = BinarySensorDeviceClass.BATTERY_CHARGING
    _attr_translation_key = "off_peak"

    def __init__(self, vacuum: RoborockVacuumInfo) -> None:
        """Initialize the off-peak sensor."""
        super().__init__(
            vacuum,
            ENTITY_OFF_PEAK,
            (SOURCE_OFF_PEAK_SWITCH, SOURCE_OFF_PEAK_START, SOURCE_OFF_PEAK_END),
        )

    @property
    def available(self) -> bool:
        """Return whether off-peak charging is enabled and configured."""
        switch = self.source_state(SOURCE_OFF_PEAK_SWITCH)
        return (
            super().available
            and switch is not None
            and switch.state == STATE_ON
            and parse_time_state(self.source_state(SOURCE_OFF_PEAK_START)) is not None
            and parse_time_state(self.source_state(SOURCE_OFF_PEAK_END)) is not None
        )

    @property
    def is_on(self) -> bool | None:
        """Return whether the current time is inside the off-peak window."""
        start = parse_time_state(self.source_state(SOURCE_OFF_PEAK_START))
        end = parse_time_state(self.source_state(SOURCE_OFF_PEAK_END))
        if start is None or end is None:
            return None
        return time_is_in_window(dt_util.now().time(), start, end)

    async def async_added_to_hass(self) -> None:
        """Also refresh when time advances into or out of the window."""
        await super().async_added_to_hass()
        self.async_on_remove(
            async_track_time_interval(
                self.hass,
                lambda now: self.async_write_ha_state(),
                timedelta(minutes=1),
            )
        )


class RoborockWaterEquipmentBinarySensor(RoborockAddonEntity, BinarySensorEntity):
    """Report missing water-box or mop equipment."""

    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_translation_key = "water_equipment"

    def __init__(self, vacuum: RoborockVacuumInfo) -> None:
        """Initialize the water-equipment sensor."""
        super().__init__(
            vacuum,
            ENTITY_WATER_EQUIPMENT,
            (
                SOURCE_WATER_BOX_ATTACHED,
                SOURCE_MOP_ATTACHED,
                SOURCE_WATER_SHORTAGE,
            ),
        )

    @property
    def available(self) -> bool:
        """Return whether at least one equipment source has a usable state."""
        states = (
            self.source_state(SOURCE_WATER_BOX_ATTACHED),
            self.source_state(SOURCE_MOP_ATTACHED),
            self.source_state(SOURCE_WATER_SHORTAGE),
        )
        return super().available and any(
            state is not None
            and state.state not in (STATE_UNAVAILABLE, STATE_UNKNOWN)
            for state in states
        )

    @property
    def is_on(self) -> bool:
        """Return true when water equipment is missing or out of water."""
        attachment_missing = any(
            state is not None and state.state == STATE_OFF
            for state in (
                self.source_state(SOURCE_WATER_BOX_ATTACHED),
                self.source_state(SOURCE_MOP_ATTACHED),
            )
        )
        water_shortage = self.source_state(SOURCE_WATER_SHORTAGE)
        return attachment_missing or (
            water_shortage is not None and water_shortage.state == STATE_ON
        )

    @property
    def extra_state_attributes(self) -> dict[str, bool | None]:
        """Return normalized water-equipment details."""
        return {
            "mop": self._source_is_on(SOURCE_MOP_ATTACHED),
            "waterbox": self._source_is_on(SOURCE_WATER_BOX_ATTACHED),
            # The Roborock source reports a shortage, so invert it to expose
            # whether water is present.
            "water": self._source_is_on(SOURCE_WATER_SHORTAGE, invert=True),
        }

    def _source_is_on(self, key: str, *, invert: bool = False) -> bool | None:
        """Return a source state as a semantic boolean."""
        state = self.source_state(key)
        if state is None or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            return None
        if state.state == STATE_ON:
            return not invert
        if state.state == STATE_OFF:
            return invert
        return None
