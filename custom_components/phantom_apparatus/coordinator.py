"""DataUpdateCoordinator for The Phantom Apparatus."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.core import Event, EventStateChangedData, callback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

if TYPE_CHECKING:
    from .data import PhantomApparatusConfigEntry


class PhantomApparatusDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from Home Assistant entities."""

    config_entry: PhantomApparatusConfigEntry

    def __init__(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        """Initialize the coordinator."""
        super().__init__(*args, **kwargs)
        self._unsub_state_changed = None

    async def async_config_entry_first_refresh(self) -> None:
        """Perform first refresh and set up state change listeners."""
        await super().async_config_entry_first_refresh()

        # Set up listeners for state changes
        entities_to_track = [
            self.config_entry.data.get("tv_entity"),
            self.config_entry.data.get("jellyfin_entity"),
            self.config_entry.data.get("ghosttube_entity"),
        ]
        # Filter out None values
        entities_to_track = [e for e in entities_to_track if e]

        if entities_to_track:
            self._unsub_state_changed = async_track_state_change_event(
                self.hass,
                entities_to_track,
                self._handle_state_change,
            )

    @callback
    def _handle_state_change(self, event: Event[EventStateChangedData]) -> None:  # noqa: ARG002
        """Handle state changes of tracked entities."""
        # Request a refresh when any tracked entity changes
        self.async_set_updated_data(self._get_current_data())

    def _get_current_data(self) -> dict[str, Any]:
        """Get current state data from entities."""
        data = {}

        # Get TV entity state
        if (tv_entity_id := self.config_entry.data.get("tv_entity")) and (
            tv_state := self.hass.states.get(tv_entity_id)
        ):
            data["tv_state"] = tv_state.state
            data["tv_attributes"] = dict(tv_state.attributes)

        # Get Jellyfin entity state
        if (jellyfin_entity_id := self.config_entry.data.get("jellyfin_entity")) and (
            jellyfin_state := self.hass.states.get(jellyfin_entity_id)
        ):
            data["jellyfin_state"] = jellyfin_state.state
            data["jellyfin_attributes"] = dict(jellyfin_state.attributes)

        # Get GhostTube entity state
        if (ghosttube_entity_id := self.config_entry.data.get("ghosttube_entity")) and (
            ghosttube_state := self.hass.states.get(ghosttube_entity_id)
        ):
            data["ghosttube_state"] = ghosttube_state.state
            data["ghosttube_attributes"] = dict(ghosttube_state.attributes)

        return data

    async def _async_update_data(self) -> Any:
        """Update data from Home Assistant entities."""
        # Just return current data - this is called on first load
        # After that, updates come from state change events
        return self._get_current_data()

    async def async_shutdown(self) -> None:
        """Clean up resources."""
        if self._unsub_state_changed:
            self._unsub_state_changed()
        await super().async_shutdown()
