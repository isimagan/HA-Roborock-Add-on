"""Constants for the Roborock Add-ons integration."""

from homeassistant.const import Platform

DOMAIN = "roborock_addons"
ROBOROCK_DOMAIN = "roborock"

CONF_ENABLED_ENTITIES = "enabled_entities"

ENTITY_FAN_SPEED = "fan_speed"
ENTITY_OFF_PEAK = "off_peak"
ENTITY_WATER_EQUIPMENT = "water_equipment"
ENTITY_CHARGING_STATUS = "charging_status"

ALL_ENTITIES = (
    ENTITY_FAN_SPEED,
    ENTITY_OFF_PEAK,
    ENTITY_WATER_EQUIPMENT,
    ENTITY_CHARGING_STATUS,
)

PLATFORMS = (Platform.SELECT, Platform.BINARY_SENSOR, Platform.SENSOR)

SOURCE_BATTERY = "battery"
SOURCE_MOP_ATTACHED = "water_box_carriage_status"
SOURCE_OFF_PEAK_END = "off_peak_end"
SOURCE_OFF_PEAK_START = "off_peak_start"
SOURCE_OFF_PEAK_SWITCH = "off_peak_switch"
SOURCE_WATER_BOX_ATTACHED = "water_box_status"

SOURCE_KEYS = (
    SOURCE_BATTERY,
    SOURCE_MOP_ATTACHED,
    SOURCE_OFF_PEAK_END,
    SOURCE_OFF_PEAK_START,
    SOURCE_OFF_PEAK_SWITCH,
    SOURCE_WATER_BOX_ATTACHED,
)
