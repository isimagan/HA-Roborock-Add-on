"""Roborock cleaning-count select.

This module intentionally contains the complete feature so it can be removed when
cleaning count is supported by the official Roborock integration.
"""

from __future__ import annotations

from typing import Any

from roborock.exceptions import RoborockException
from roborock.roborock_typing import RoborockCommand

from homeassistant.components.roborock.coordinator import (
    RoborockDataUpdateCoordinator,
)
from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import ENTITY_CLEANING_COUNT, ROBOROCK_DOMAIN

# The S8 exposes one or two passes. Keep options injectable so a future
# capability-based implementation can supply a different set per coordinator.
DEFAULT_CLEANING_COUNT_OPTIONS = ("1", "2")


async def async_setup_cleaning_count(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Add cleaning-count selects for current and newly available V1 vacuums."""
    device_registry = dr.async_get(hass)
    added_devices: set[tuple[str, str]] = set()

    @callback
    def async_add_coordinator_entity(
        coordinator: Any, roborock_entry_id: str
    ) -> None:
        """Add an entity when the official integration provides a coordinator."""
        device_key = (roborock_entry_id, getattr(coordinator, "duid", ""))
        if (
            not isinstance(coordinator, RoborockDataUpdateCoordinator)
            or device_key in added_devices
        ):
            return

        device_entry = next(
            (
                device
                for device in dr.async_entries_for_config_entry(
                    device_registry, roborock_entry_id
                )
                if (ROBOROCK_DOMAIN, coordinator.duid) in device.identifiers
            ),
            None,
        )
        if device_entry is None:
            return

        added_devices.add(device_key)
        async_add_entities(
            [
                RoborockCleaningCountSelect(
                    coordinator,
                    device_entry,
                    DEFAULT_CLEANING_COUNT_OPTIONS,
                )
            ]
        )

    for roborock_entry in hass.config_entries.async_entries(ROBOROCK_DOMAIN):
        coordinators = getattr(roborock_entry, "runtime_data", None)
        if coordinators is not None:
            for coordinator in coordinators.values():
                async_add_coordinator_entity(coordinator, roborock_entry.entry_id)

        @callback
        def async_add_entry_coordinator(
            coordinator: Any,
            roborock_entry_id: str = roborock_entry.entry_id,
        ) -> None:
            """Add a coordinator associated with this Roborock config entry."""
            async_add_coordinator_entity(coordinator, roborock_entry_id)

        entry.async_on_unload(
            async_dispatcher_connect(
                hass,
                f"roborock_coordinator_added_{roborock_entry.entry_id}",
                async_add_entry_coordinator,
            )
        )


class RoborockCleaningCountSelect(SelectEntity):
    """Select the number of passes for the next Roborock cleaning."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_has_entity_name = True
    _attr_translation_key = "cleaning_count"

    def __init__(
        self,
        coordinator: RoborockDataUpdateCoordinator,
        device_entry: dr.AnyDeviceEntry,
        options: tuple[str, ...],
    ) -> None:
        """Initialize the cleaning-count select."""
        self.coordinator = coordinator
        self.device_entry = device_entry
        self._attr_unique_id = f"{coordinator.duid_slug}_{ENTITY_CLEANING_COUNT}"
        self._attr_options = list(options)

    @property
    def available(self) -> bool:
        """Return whether a current repeat value is available from the robot."""
        return (
            self.coordinator.last_update_success
            and self.coordinator.properties_api.status.repeat is not None
        )

    @property
    def current_option(self) -> str | None:
        """Return the robot's actual repeat value."""
        repeat = self.coordinator.properties_api.status.repeat
        return str(repeat) if repeat is not None else None

    async def async_added_to_hass(self) -> None:
        """Subscribe to actual Roborock status updates."""
        await super().async_added_to_hass()
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_select_option(self, option: str) -> None:
        """Set repeat on the robot and refresh its actual status."""
        try:
            await self.coordinator.properties_api.command.send(
                RoborockCommand.SET_CLEAN_REPEAT_TIMES,
                params={"repeat": int(option)},
            )
        except RoborockException as err:
            raise HomeAssistantError("Failed to set Roborock cleaning count") from err

        await self.coordinator.async_refresh()
