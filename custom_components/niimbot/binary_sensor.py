"""Support for niimbot BLE binary sensors."""

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import CONNECTION_BLUETOOTH
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN
from .niimprint import BLEData

_LOGGER = logging.getLogger(__name__)

BINARY_SENSORS: tuple[BinarySensorEntityDescription, ...] = (
    BinarySensorEntityDescription(
        key="connection_status",
        name="Connection Status",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Niimbot BLE binary sensors."""
    coordinator: DataUpdateCoordinator[BLEData] = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]

    entities = [
        NiimbotBinarySensor(coordinator, coordinator.data, description)
        for description in BINARY_SENSORS
    ]

    async_add_entities(entities)


class NiimbotBinarySensor(
    CoordinatorEntity[DataUpdateCoordinator[BLEData]], BinarySensorEntity
):
    """Niimbot BLE binary sensors for the device."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DataUpdateCoordinator[BLEData],
        ble_data: BLEData,
        description: BinarySensorEntityDescription,
    ) -> None:
        """Populate the niimbot entity with relevant data."""
        super().__init__(coordinator)
        self.entity_description = description

        name = f"{ble_data.name} {ble_data.identifier}"
        self._attr_unique_id = f"{name}_{description.key}"

        self._attr_device_info = DeviceInfo(
            connections={
                (
                    CONNECTION_BLUETOOTH,
                    ble_data.address,
                )
            },
            name=name,
            manufacturer="Niimbot",
            model=ble_data.model,
            hw_version=ble_data.hw_version,
            sw_version=ble_data.sw_version,
            serial_number=ble_data.serial_number,
        )

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        return self.coordinator.data.sensors.get(self.entity_description.key)
