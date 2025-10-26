"""
The Phantom Apparatus - Media Hardware Control for Home Assistant.

Control your media hardware through Home Assistant entities.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.const import Platform
from homeassistant.loader import async_get_loaded_integration

from .const import DOMAIN, LOGGER
from .coordinator import PhantomApparatusDataUpdateCoordinator
from .data import PhantomApparatusData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import PhantomApparatusConfigEntry

PLATFORMS: list[Platform] = [
    Platform.MEDIA_PLAYER,
]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(
    hass: HomeAssistant,
    entry: PhantomApparatusConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    coordinator = PhantomApparatusDataUpdateCoordinator(
        hass=hass,
        logger=LOGGER,
        name=DOMAIN,
        config_entry=entry,
        # No update_interval needed - we use state change events
    )
    entry.runtime_data = PhantomApparatusData(
        integration=async_get_loaded_integration(hass, entry.domain),
        coordinator=coordinator,
        config=entry.data,
    )

    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: PhantomApparatusConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: PhantomApparatusConfigEntry,
) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)
