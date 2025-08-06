"""Custom types for The Phantom Apparatus."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .coordinator import PhantomApparatusDataUpdateCoordinator


type PhantomApparatusConfigEntry = ConfigEntry[PhantomApparatusData]


@dataclass
class PhantomApparatusData:
    """Data for The Phantom Apparatus integration."""

    coordinator: PhantomApparatusDataUpdateCoordinator
    integration: Integration
    config: dict
