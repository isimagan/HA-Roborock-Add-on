"""Helpers shared by Roborock Add-ons entities."""

from dataclasses import dataclass
from datetime import time
from typing import Any

from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import Event, HomeAssistant, State, callback
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_state_change_event

from .const import ROBOROCK_DOMAIN, SOURCE_KEYS


@dataclass(frozen=True)
class RoborockVacuumInfo:
    """Entity registry information for a Roborock vacuum."""

    entity_id: str
    unique_id: str
    device_entry: dr.AnyDeviceEntry
    sources: dict[str, str]


def async_get_roborock_vacuums(hass: HomeAssistant) -> list[RoborockVacuumInfo]:
    """Find Roborock vacuum entities and their related source entities."""
    entity_registry = er.async_get(hass)
    device_registry = dr.async_get(hass)
    vacuums: list[RoborockVacuumInfo] = []

    for roborock_entry in hass.config_entries.async_entries(ROBOROCK_DOMAIN):
        for vacuum_entry in er.async_entries_for_config_entry(
            entity_registry, roborock_entry.entry_id
        ):
            if (
                vacuum_entry.domain != "vacuum"
                or vacuum_entry.platform != ROBOROCK_DOMAIN
                or vacuum_entry.device_id is None
            ):
                continue

            device = device_registry.async_get(vacuum_entry.device_id)
            if device is None:
                continue

            sources: dict[str, str] = {}
            for source_entry in er.async_entries_for_device(
                entity_registry,
                vacuum_entry.device_id,
                include_disabled_entities=True,
            ):
                for key in SOURCE_KEYS:
                    if source_entry.unique_id.startswith(f"{key}_"):
                        sources[key] = source_entry.entity_id
                        break

            vacuums.append(
                RoborockVacuumInfo(
                    entity_id=vacuum_entry.entity_id,
                    unique_id=vacuum_entry.unique_id,
                    device_entry=device,
                    sources=sources,
                )
            )

    return vacuums


def parse_time_state(state: State | None) -> time | None:
    """Parse the state of a time entity."""
    if state is None or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
        return None
    try:
        return time.fromisoformat(state.state)
    except ValueError:
        return None


def time_is_in_window(now: time, start: time, end: time) -> bool:
    """Return whether now is inside a time window that may cross midnight."""
    if start < end:
        return start <= now < end
    return now >= start or now < end


class RoborockAddonEntity(Entity):
    """Base class for an entity derived from a Roborock vacuum."""

    _attr_has_entity_name = True

    def __init__(
        self,
        vacuum: RoborockVacuumInfo,
        key: str,
        source_keys: tuple[str, ...] = (),
    ) -> None:
        """Initialize an add-on entity."""
        self.vacuum = vacuum
        self._attr_unique_id = f"{vacuum.unique_id}_{key}"
        # Attach directly to the device owned by the official Roborock
        # integration. This follows Home Assistant's helper-entity model and
        # avoids creating a separate Roborock Add-ons device.
        self.device_entry = vacuum.device_entry
        self._source_entity_ids = {
            vacuum.entity_id,
            *(vacuum.sources[key] for key in source_keys if key in vacuum.sources),
        }

    @property
    def available(self) -> bool:
        """Return whether the source vacuum is available."""
        state = self.hass.states.get(self.vacuum.entity_id)
        return state is not None and state.state not in (
            STATE_UNAVAILABLE,
            STATE_UNKNOWN,
        )

    def source_state(self, key: str) -> State | None:
        """Return a source entity state."""
        if (entity_id := self.vacuum.sources.get(key)) is None:
            return None
        return self.hass.states.get(entity_id)

    async def async_added_to_hass(self) -> None:
        """Subscribe to source state changes."""
        await super().async_added_to_hass()
        self.async_on_remove(
            async_track_state_change_event(
                self.hass,
                self._source_entity_ids,
                self._handle_source_update,
            )
        )

    @callback
    def _handle_source_update(self, event: Event[Any]) -> None:
        """Write state when a source entity changes."""
        self.async_write_ha_state()
