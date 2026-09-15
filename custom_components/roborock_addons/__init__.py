"""Roborock Add-ons integration for Home Assistant."""

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

DOMAIN = "roborock_addons"


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up Roborock Add-ons."""
    return True
