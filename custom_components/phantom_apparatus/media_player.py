"""Media player platform for The Phantom Apparatus."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    MediaType,
)
from homeassistant.core import HomeAssistant, callback

from .entity import PhantomApparatusEntity

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import PhantomApparatusDataUpdateCoordinator
    from .data import PhantomApparatusConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: PhantomApparatusConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the media player platform."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities([PhantomApparatusMediaPlayer(coordinator, entry)])


class PhantomApparatusMediaPlayer(PhantomApparatusEntity, MediaPlayerEntity):
    """Media player implementation for The Phantom Apparatus."""

    _attr_device_class = MediaPlayerDeviceClass.TV
    _attr_has_entity_name = True
    _attr_name = None

    def __init__(
        self,
        coordinator: PhantomApparatusDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the media player."""
        super().__init__(coordinator, "media_player")
        self._entry = entry
        self._tv_entity_id = entry.data.get("tv_entity")
        self._jellyfin_entity_id = entry.data.get("jellyfin_entity")
        self._ghosttube_entity_id = entry.data.get("ghosttube_entity")

    @property
    def supported_features(self) -> MediaPlayerEntityFeature:  # noqa: PLR0912
        """Return supported features based on TV capabilities."""
        if not self.coordinator.data:
            return MediaPlayerEntityFeature(0)

        features = MediaPlayerEntityFeature(0)
        tv_attrs = self.coordinator.data.get("tv_attributes", {})
        tv_features = tv_attrs.get("supported_features", 0)

        # Map TV features to our features
        if tv_features & MediaPlayerEntityFeature.TURN_ON:
            features |= MediaPlayerEntityFeature.TURN_ON
        if tv_features & MediaPlayerEntityFeature.TURN_OFF:
            features |= MediaPlayerEntityFeature.TURN_OFF
        if tv_features & MediaPlayerEntityFeature.VOLUME_SET:
            features |= MediaPlayerEntityFeature.VOLUME_SET
        if tv_features & MediaPlayerEntityFeature.VOLUME_STEP:
            features |= MediaPlayerEntityFeature.VOLUME_STEP
        if tv_features & MediaPlayerEntityFeature.VOLUME_MUTE:
            features |= MediaPlayerEntityFeature.VOLUME_MUTE
        if tv_features & MediaPlayerEntityFeature.SELECT_SOURCE:
            features |= MediaPlayerEntityFeature.SELECT_SOURCE
        if tv_features & MediaPlayerEntityFeature.PLAY:
            features |= MediaPlayerEntityFeature.PLAY
        if tv_features & MediaPlayerEntityFeature.PAUSE:
            features |= MediaPlayerEntityFeature.PAUSE
        if tv_features & MediaPlayerEntityFeature.STOP:
            features |= MediaPlayerEntityFeature.STOP
        if tv_features & MediaPlayerEntityFeature.NEXT_TRACK:
            features |= MediaPlayerEntityFeature.NEXT_TRACK
        if tv_features & MediaPlayerEntityFeature.PREVIOUS_TRACK:
            features |= MediaPlayerEntityFeature.PREVIOUS_TRACK

        # Add seek feature if active app supports it
        active_app_attrs = self._get_active_app_attributes()
        if active_app_attrs:
            app_features = active_app_attrs.get("supported_features", 0)
            if app_features & MediaPlayerEntityFeature.SEEK:
                features |= MediaPlayerEntityFeature.SEEK

        return features

    def _get_active_app_attributes(self) -> dict[str, Any] | None:
        """Get attributes from the currently active app."""
        if not self.coordinator.data:
            return None

        tv_attrs = self.coordinator.data.get("tv_attributes", {})
        current_source = tv_attrs.get("source")

        if current_source == "Jellyfin":
            return self.coordinator.data.get("jellyfin_attributes", {})
        if current_source == "Ghost Tube":
            return self.coordinator.data.get("ghosttube_attributes", {})
        return None

    def _get_active_app_state(self) -> str | None:
        """Get state from the currently active app."""
        if not self.coordinator.data:
            return None

        tv_attrs = self.coordinator.data.get("tv_attributes", {})
        current_source = tv_attrs.get("source")

        if current_source == "Jellyfin":
            return self.coordinator.data.get("jellyfin_state")
        if current_source == "Ghost Tube":
            return self.coordinator.data.get("ghosttube_state")
        return None

    @property
    def state(self) -> MediaPlayerState | None:
        """Return the state of the media player."""
        if not self.coordinator.data:
            return MediaPlayerState.OFF

        tv_state = self.coordinator.data.get("tv_state")

        # If TV is off, we're off
        if tv_state == "off":
            return MediaPlayerState.OFF

        # Check active app state
        app_state = self._get_active_app_state()
        if app_state == "playing":
            return MediaPlayerState.PLAYING
        if app_state == "paused":
            return MediaPlayerState.PAUSED
        if app_state in {"idle", "standby"}:
            return MediaPlayerState.IDLE

        # Default to idle if TV is on but no app state
        return MediaPlayerState.IDLE

    @property
    def volume_level(self) -> float | None:
        """Return the volume level."""
        if not self.coordinator.data:
            return None
        tv_attrs = self.coordinator.data.get("tv_attributes", {})
        return tv_attrs.get("volume_level")

    @property
    def is_volume_muted(self) -> bool | None:
        """Return true if volume is muted."""
        if not self.coordinator.data:
            return None
        tv_attrs = self.coordinator.data.get("tv_attributes", {})
        return tv_attrs.get("is_volume_muted")

    @property
    def source(self) -> str | None:
        """Return the current input source."""
        if not self.coordinator.data:
            return None
        tv_attrs = self.coordinator.data.get("tv_attributes", {})
        return tv_attrs.get("source")

    @property
    def source_list(self) -> list[str] | None:
        """Return the list of available input sources."""
        if not self.coordinator.data:
            return None

        tv_attrs = self.coordinator.data.get("tv_attributes", {})
        current_source = tv_attrs.get("source")

        # Always include Jellyfin and Ghost Tube
        sources = ["Jellyfin", "Ghost Tube"]

        # If current source is something else, include it too
        if current_source and current_source not in sources:
            sources.append(current_source)

        return sources

    # Media properties from active app
    @property
    def media_title(self) -> str | None:
        """Return the title of current playing media."""
        active_attrs = self._get_active_app_attributes()
        if active_attrs:
            return active_attrs.get("media_title")
        return None

    @property
    def media_content_type(self) -> MediaType | str | None:
        """Return the content type of current playing media."""
        active_attrs = self._get_active_app_attributes()
        if active_attrs:
            return active_attrs.get("media_content_type")
        return None

    @property
    def media_content_id(self) -> str | None:
        """Return the content ID of current playing media."""
        active_attrs = self._get_active_app_attributes()
        if active_attrs:
            return active_attrs.get("media_content_id")
        return None

    @property
    def media_duration(self) -> int | None:
        """Return the duration of current playing media in seconds."""
        active_attrs = self._get_active_app_attributes()
        if active_attrs:
            return active_attrs.get("media_duration")
        return None

    @property
    def media_position(self) -> int | None:
        """Return the position of current playing media in seconds."""
        active_attrs = self._get_active_app_attributes()
        if active_attrs:
            return active_attrs.get("media_position")
        return None

    @property
    def media_position_updated_at(self) -> Any | None:
        """Return when the position was last updated."""
        active_attrs = self._get_active_app_attributes()
        if active_attrs:
            return active_attrs.get("media_position_updated_at")
        return None

    @property
    def media_image_url(self) -> str | None:
        """Return the image URL of current playing media."""
        active_attrs = self._get_active_app_attributes()
        if active_attrs:
            return active_attrs.get("entity_picture")
        return None

    @property
    def media_artist(self) -> str | None:
        """Return the artist of current playing media."""
        active_attrs = self._get_active_app_attributes()
        if active_attrs:
            return active_attrs.get("media_artist")
        return None

    @property
    def media_album_name(self) -> str | None:
        """Return the album name of current playing media."""
        active_attrs = self._get_active_app_attributes()
        if active_attrs:
            return active_attrs.get("media_album_name")
        return None

    @property
    def media_series_title(self) -> str | None:
        """Return the series title of current playing media."""
        active_attrs = self._get_active_app_attributes()
        if active_attrs:
            return active_attrs.get("media_series_title")
        return None

    @property
    def media_season(self) -> str | None:
        """Return the season of current playing media."""
        active_attrs = self._get_active_app_attributes()
        if active_attrs:
            return active_attrs.get("media_season")
        return None

    @property
    def media_episode(self) -> str | None:
        """Return the episode of current playing media."""
        active_attrs = self._get_active_app_attributes()
        if active_attrs:
            return active_attrs.get("media_episode")
        return None

    # Control methods - TV controls
    async def async_turn_on(self) -> None:
        """Turn on the media player."""
        # Use Wake on LAN to turn on the TV
        await self.hass.services.async_call(
            "shell_command",
            "wake_living_room_tv",
            {},
            blocking=True,
        )

    async def async_turn_off(self) -> None:
        """Turn off the media player."""
        await self.hass.services.async_call(
            "media_player",
            "turn_off",
            {"entity_id": self._tv_entity_id},
            blocking=True,
        )

    async def async_set_volume_level(self, volume: float) -> None:
        """Set volume level, range 0..1."""
        await self.hass.services.async_call(
            "media_player",
            "volume_set",
            {"entity_id": self._tv_entity_id, "volume_level": volume},
            blocking=True,
        )

    async def async_volume_up(self) -> None:
        """Increase volume."""
        await self.hass.services.async_call(
            "media_player",
            "volume_up",
            {"entity_id": self._tv_entity_id},
            blocking=True,
        )

    async def async_volume_down(self) -> None:
        """Decrease volume."""
        await self.hass.services.async_call(
            "media_player",
            "volume_down",
            {"entity_id": self._tv_entity_id},
            blocking=True,
        )

    async def async_mute_volume(self, mute: bool) -> None:  # noqa: FBT001
        """Mute or unmute the volume."""
        await self.hass.services.async_call(
            "media_player",
            "volume_mute",
            {"entity_id": self._tv_entity_id, "is_volume_muted": mute},
            blocking=True,
        )

    async def async_select_source(self, source: str) -> None:
        """Select input source."""
        await self.hass.services.async_call(
            "media_player",
            "select_source",
            {"entity_id": self._tv_entity_id, "source": source},
            blocking=True,
        )

    async def async_media_play(self) -> None:
        """Send play command to TV."""
        await self.hass.services.async_call(
            "media_player",
            "media_play",
            {"entity_id": self._tv_entity_id},
            blocking=True,
        )

    async def async_media_pause(self) -> None:
        """Send pause command to TV."""
        await self.hass.services.async_call(
            "media_player",
            "media_pause",
            {"entity_id": self._tv_entity_id},
            blocking=True,
        )

    async def async_media_stop(self) -> None:
        """Send stop command to TV."""
        await self.hass.services.async_call(
            "media_player",
            "media_stop",
            {"entity_id": self._tv_entity_id},
            blocking=True,
        )

    async def async_media_next_track(self) -> None:
        """Send next track command to TV."""
        await self.hass.services.async_call(
            "media_player",
            "media_next_track",
            {"entity_id": self._tv_entity_id},
            blocking=True,
        )

    async def async_media_previous_track(self) -> None:
        """Send previous track command to TV."""
        await self.hass.services.async_call(
            "media_player",
            "media_previous_track",
            {"entity_id": self._tv_entity_id},
            blocking=True,
        )

    async def async_media_seek(self, position: float) -> None:
        """Send seek command to active app."""
        # Determine which app is active
        tv_attrs = (
            self.coordinator.data.get("tv_attributes", {})
            if self.coordinator.data
            else {}
        )
        current_source = tv_attrs.get("source")

        target_entity = None
        if current_source == "Jellyfin":
            target_entity = self._jellyfin_entity_id
        elif current_source == "Ghost Tube":
            target_entity = self._ghosttube_entity_id

        if target_entity:
            await self.hass.services.async_call(
                "media_player",
                "media_seek",
                {"entity_id": target_entity, "seek_position": position},
                blocking=True,
            )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()
