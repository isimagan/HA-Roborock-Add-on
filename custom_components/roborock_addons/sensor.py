"""Sensor entities for Roborock Add-ons."""

from datetime import timedelta

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_ON, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.util import dt as dt_util

from .const import (
    CONF_ENABLED_ENTITIES,
    ENTITY_CHARGING_STATUS,
    SOURCE_BATTERY,
    SOURCE_OFF_PEAK_END,
    SOURCE_OFF_PEAK_START,
    SOURCE_OFF_PEAK_SWITCH,
)
from .helpers import (
    RoborockAddonEntity,
    RoborockVacuumInfo,
    async_get_roborock_vacuums,
    parse_time_state,
    time_is_in_window,
)

CHARGED = "charged"
CHARGE_PENDING = "charge_pending"
CHARGING = "charging"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up selected Roborock Add-ons sensors."""
    enabled = entry.options.get(
        CONF_ENABLED_ENTITIES, entry.data.get(CONF_ENABLED_ENTITIES, [])
    )
    if ENTITY_CHARGING_STATUS not in enabled:
        return
    async_add_entities(
        RoborockChargingStatusSensor(vacuum)
        for vacuum in async_get_roborock_vacuums(hass)
    )


class RoborockChargingStatusSensor(RoborockAddonEntity, SensorEntity):
    """Summarize the charging state of a Roborock vacuum."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = [CHARGED, CHARGE_PENDING, CHARGING]
    _attr_translation_key = "charging_status"

    def __init__(self, vacuum: RoborockVacuumInfo) -> None:
        """Initialize the charging-status sensor."""
        super().__init__(
            vacuum,
            ENTITY_CHARGING_STATUS,
            (
                SOURCE_BATTERY,
                SOURCE_OFF_PEAK_SWITCH,
                SOURCE_OFF_PEAK_START,
                SOURCE_OFF_PEAK_END,
            ),
        )

    @property
    def available(self) -> bool:
        """Return whether the battery source is usable."""
        battery = self.source_state(SOURCE_BATTERY)
        return (
            super().available
            and battery is not None
            and battery.state not in (STATE_UNAVAILABLE, STATE_UNKNOWN)
        )

    @property
    def native_value(self) -> str | None:
        """Return charged, charge pending, or charging."""
        battery = self.source_state(SOURCE_BATTERY)
        if battery is None:
            return None
        try:
            if float(battery.state) >= 100:
                return CHARGED
        except ValueError:
            return None

        switch = self.source_state(SOURCE_OFF_PEAK_SWITCH)
        start = parse_time_state(self.source_state(SOURCE_OFF_PEAK_START))
        end = parse_time_state(self.source_state(SOURCE_OFF_PEAK_END))
        if switch is not None and switch.state == STATE_ON and start and end:
            if not time_is_in_window(dt_util.now().time(), start, end):
                return CHARGE_PENDING
        return CHARGING

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
