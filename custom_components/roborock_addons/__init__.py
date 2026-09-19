"""Roborock Add-ons integration for Home Assistant."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.helper_integration import async_remove_helper_devices

from .const import PLATFORMS
from .helpers import async_get_roborock_vacuums


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Roborock Add-ons from a config entry."""
    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a Roborock Add-ons config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload an entry after its selected entities change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Move existing helper entities onto their Roborock source devices."""
    if entry.version == 1 and entry.minor_version < 2:
        source_device_ids = {
            vacuum.device_entry.id for vacuum in async_get_roborock_vacuums(hass)
        }
        for source_device_id in source_device_ids:
            async_remove_helper_devices(
                hass,
                helper_config_entry_id=entry.entry_id,
                source_device_id=source_device_id,
            )
        hass.config_entries.async_update_entry(entry, minor_version=2)

    return True
