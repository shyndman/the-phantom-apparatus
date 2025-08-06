"""PhantomApparatusEntity class."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN
from .coordinator import PhantomApparatusDataUpdateCoordinator


class PhantomApparatusEntity(CoordinatorEntity[PhantomApparatusDataUpdateCoordinator]):
    """PhantomApparatusEntity class."""

    _attr_attribution = ATTRIBUTION

    def __init__(
        self, coordinator: PhantomApparatusDataUpdateCoordinator, name: str
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{name}"
        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    DOMAIN,
                    coordinator.config_entry.entry_id,
                ),
            },
            name=coordinator.config_entry.data.get("name", "Phantom Apparatus"),
            manufacturer="The Ghost of Don Don",
            model="Phantom Apparatus",
        )
