"""Media player platform for The Phantom Apparatus."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
)
from homeassistant.components.media_player.const import (
    MediaPlayerEntityFeature,
    MediaPlayerState,
    MediaType,
)
from homeassistant.core import HomeAssistant, callback

from .const import GHOSTTUBE_IDLE_IMAGE_DATA_URI, JELLYFIN_IDLE_IMAGE_DATA_URI
from .entity import PhantomApparatusEntity

_LOGGER = logging.getLogger(__name__)

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
        _LOGGER.debug(
            "Initialized PhantomApparatusMediaPlayer: entry_id=%s tv_entity=%s "
            "jellyfin_entity=%s ghosttube_entity=%s",
            entry.entry_id,
            self._tv_entity_id,
            self._jellyfin_entity_id,
            self._ghosttube_entity_id,
        )

    @property
    def supported_features(self) -> MediaPlayerEntityFeature:  # noqa: PLR0912
        """Return supported features based on TV capabilities."""
        has_data = self.coordinator.data is not None
        _LOGGER.debug(
            "supported_features requested; coordinator_data_present=%s",
            has_data,
        )
        if not has_data:
            result = MediaPlayerEntityFeature(0)
            _LOGGER.debug("supported_features returning %s (no data)", result)
            return result

        features = MediaPlayerEntityFeature(0)
        tv_attrs = self.coordinator.data.get("tv_attributes", {})
        tv_features = tv_attrs.get("supported_features", 0)

        # Map TV features to our features
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
        app_features = 0
        if active_app_attrs:
            app_features = active_app_attrs.get("supported_features", 0)
            if app_features & MediaPlayerEntityFeature.SEEK:
                features |= MediaPlayerEntityFeature.SEEK
        _LOGGER.debug(
            "supported_features returning %s (tv_features=%s app_features=%s)",
            features,
            tv_features,
            app_features,
        )

        return features

    def _get_active_app_attributes(self) -> dict[str, Any] | None:
        """Get attributes from the currently active app."""
        if not self.coordinator.data:
            _LOGGER.debug(
                "_get_active_app_attributes called without coordinator data",
            )
            return None

        tv_attrs = self.coordinator.data.get("tv_attributes", {})
        current_source = tv_attrs.get("source")
        result: dict[str, Any] | None = None

        if current_source == "Jellyfin":
            result = self.coordinator.data.get("jellyfin_attributes", {})
        elif current_source == "GhostTube":
            result = self.coordinator.data.get("ghosttube_attributes", {})

        _LOGGER.debug(
            "_get_active_app_attributes source=%s returning_keys=%s",
            current_source,
            list(result.keys()) if isinstance(result, dict) else None,
        )
        return result

    def _get_active_app_state(self) -> str | None:
        """Get state from the currently active app."""
        if not self.coordinator.data:
            _LOGGER.debug(
                "_get_active_app_state called without coordinator data",
            )
            return None

        tv_attrs = self.coordinator.data.get("tv_attributes", {})
        current_source = tv_attrs.get("source")
        result: str | None = None

        if current_source == "Jellyfin":
            result = self.coordinator.data.get("jellyfin_state")
        elif current_source == "GhostTube":
            result = self.coordinator.data.get("ghosttube_state")

        _LOGGER.debug(
            "_get_active_app_state source=%s state=%s",
            current_source,
            result,
        )
        return result

    def _get_idle_image_for_source(self, source: str | None) -> str | None:
        """Return idle artwork for known sources."""
        if source == "Jellyfin":
            return JELLYFIN_IDLE_IMAGE_DATA_URI
        if source == "GhostTube":
            return GHOSTTUBE_IDLE_IMAGE_DATA_URI
        return None

    @property
    def state(self) -> MediaPlayerState | None:
        """Return the state of the media player."""
        if not self.coordinator.data:
            result = MediaPlayerState.OFF
            _LOGGER.debug(
                "state requested without coordinator data; returning %s",
                result,
            )
            return result

        tv_state = self.coordinator.data.get("tv_state")

        # If TV is off, we're off
        if tv_state == "off":
            result = MediaPlayerState.OFF
            _LOGGER.debug(
                "state requested; tv_state=%s -> %s",
                tv_state,
                result,
            )
            return result

        # Check active app state
        app_state = self._get_active_app_state()
        if app_state == "playing":
            result = MediaPlayerState.PLAYING
        elif app_state == "paused":
            result = MediaPlayerState.PAUSED
        elif app_state in {"idle", "standby"}:
            result = MediaPlayerState.IDLE
        else:
            # Default to idle if TV is on but no app state
            result = MediaPlayerState.IDLE

        _LOGGER.debug(
            "state requested; tv_state=%s app_state=%s -> %s",
            tv_state,
            app_state,
            result,
        )
        return result

    @property
    def volume_level(self) -> float | None:
        """Return the volume level."""
        if not self.coordinator.data:
            _LOGGER.debug("volume_level requested without coordinator data")
            return None
        tv_attrs = self.coordinator.data.get("tv_attributes", {})
        level = tv_attrs.get("volume_level")
        _LOGGER.debug("volume_level returning %s", level)
        return level

    @property
    def is_volume_muted(self) -> bool | None:
        """Return true if volume is muted."""
        if not self.coordinator.data:
            _LOGGER.debug("is_volume_muted requested without coordinator data")
            return None
        tv_attrs = self.coordinator.data.get("tv_attributes", {})
        muted = tv_attrs.get("is_volume_muted")
        _LOGGER.debug("is_volume_muted returning %s", muted)
        return muted

    @property
    def source(self) -> str | None:
        """Return the current input source."""
        if not self.coordinator.data:
            _LOGGER.debug("source requested without coordinator data")
            return None
        tv_attrs = self.coordinator.data.get("tv_attributes", {})
        current_source = tv_attrs.get("source")
        _LOGGER.debug("source returning %s", current_source)
        return current_source

    @property
    def source_list(self) -> list[str] | None:
        """Return the list of available input sources."""
        tv_attrs = (
            self.coordinator.data.get("tv_attributes", {})
            if self.coordinator.data
            else {}
        )
        current_source = tv_attrs.get("source")

        # Always include Jellyfin and Ghost Tube
        sources = ["Jellyfin", "GhostTube"]

        # If current source is something else, include it too
        if current_source and current_source not in sources:
            sources.append(current_source)

        _LOGGER.debug(
            "source_list returning %s (current_source=%s)",
            sources,
            current_source,
        )
        return sources

    # Media properties from active app
    @property
    def media_title(self) -> str | None:
        """Return the title of current playing media."""
        active_attrs = self._get_active_app_attributes()
        title = active_attrs.get("media_title") if active_attrs else None
        _LOGGER.debug("media_title returning %s", title)
        return title

    @property
    def media_content_type(self) -> MediaType | str | None:
        """Return the content type of current playing media."""
        active_attrs = self._get_active_app_attributes()
        content_type = active_attrs.get("media_content_type") if active_attrs else None
        _LOGGER.debug("media_content_type returning %s", content_type)
        return content_type

    @property
    def media_content_id(self) -> str | None:
        """Return the content ID of current playing media."""
        active_attrs = self._get_active_app_attributes()
        content_id = active_attrs.get("media_content_id") if active_attrs else None
        _LOGGER.debug("media_content_id returning %s", content_id)
        return content_id

    @property
    def media_duration(self) -> int | None:
        """Return the duration of current playing media in seconds."""
        active_attrs = self._get_active_app_attributes()
        duration = active_attrs.get("media_duration") if active_attrs else None
        _LOGGER.debug("media_duration returning %s", duration)
        return duration

    @property
    def media_position(self) -> int | None:
        """Return the position of current playing media in seconds."""
        active_attrs = self._get_active_app_attributes()
        position = active_attrs.get("media_position") if active_attrs else None
        _LOGGER.debug("media_position returning %s", position)
        return position

    @property
    def media_position_updated_at(self) -> Any | None:
        """Return when the position was last updated."""
        active_attrs = self._get_active_app_attributes()
        updated_at = (
            active_attrs.get("media_position_updated_at") if active_attrs else None
        )
        _LOGGER.debug("media_position_updated_at returning %s", updated_at)
        return updated_at

    @property
    def media_image_url(self) -> str | None:
        """Return the image URL of current playing media."""
        active_attrs = self._get_active_app_attributes()
        image_url = active_attrs.get("entity_picture") if active_attrs else None
        if image_url:
            _LOGGER.debug("media_image_url returning %s", image_url)
            return image_url

        app_state = self._get_active_app_state()
        if app_state not in {"playing", "paused"}:
            source = self.source
            idle_image = self._get_idle_image_for_source(source)
            if idle_image:
                _LOGGER.debug(
                    "media_image_url using idle artwork; source=%s state=%s",
                    source,
                    app_state,
                )
                return idle_image

        _LOGGER.debug("media_image_url returning None (no artwork available)")
        return None

    @property
    def media_artist(self) -> str | None:
        """Return the artist of current playing media."""
        active_attrs = self._get_active_app_attributes()
        artist = active_attrs.get("media_artist") if active_attrs else None
        _LOGGER.debug("media_artist returning %s", artist)
        return artist

    @property
    def media_album_name(self) -> str | None:
        """Return the album name of current playing media."""
        active_attrs = self._get_active_app_attributes()
        album = active_attrs.get("media_album_name") if active_attrs else None
        _LOGGER.debug("media_album_name returning %s", album)
        return album

    @property
    def media_series_title(self) -> str | None:
        """Return the series title of current playing media."""
        active_attrs = self._get_active_app_attributes()
        series_title = active_attrs.get("media_series_title") if active_attrs else None
        _LOGGER.debug("media_series_title returning %s", series_title)
        return series_title

    @property
    def media_season(self) -> str | None:
        """Return the season of current playing media."""
        active_attrs = self._get_active_app_attributes()
        season = active_attrs.get("media_season") if active_attrs else None
        _LOGGER.debug("media_season returning %s", season)
        return season

    @property
    def media_episode(self) -> str | None:
        """Return the episode of current playing media."""
        active_attrs = self._get_active_app_attributes()
        episode = active_attrs.get("media_episode") if active_attrs else None
        _LOGGER.debug("media_episode returning %s", episode)
        return episode

    # Control methods - TV controls
    async def async_turn_on(self) -> None:
        """Turn on the media player."""
        # Use Wake on LAN to turn on the TV
        _LOGGER.debug(
            "async_turn_on called; invoking wake_living_room_tv shell_command",
        )
        await self.hass.services.async_call(
            "shell_command",
            "wake_living_room_tv",
            {},
            blocking=True,
        )

    async def async_turn_off(self) -> None:
        """Turn off the media player."""
        _LOGGER.debug(
            "async_turn_off called; tv_entity_id=%s",
            self._tv_entity_id,
        )
        await self.hass.services.async_call(
            "media_player",
            "turn_off",
            {"entity_id": self._tv_entity_id},
            blocking=True,
        )

    async def async_set_volume_level(self, volume: float) -> None:
        """Set volume level, range 0..1."""
        _LOGGER.debug(
            "async_set_volume_level called; tv_entity_id=%s volume=%s",
            self._tv_entity_id,
            volume,
        )
        await self.hass.services.async_call(
            "media_player",
            "volume_set",
            {"entity_id": self._tv_entity_id, "volume_level": volume},
            blocking=True,
        )

    async def async_volume_up(self) -> None:
        """Increase volume."""
        _LOGGER.debug(
            "async_volume_up called; tv_entity_id=%s",
            self._tv_entity_id,
        )
        await self.hass.services.async_call(
            "media_player",
            "volume_up",
            {"entity_id": self._tv_entity_id},
            blocking=True,
        )

    async def async_volume_down(self) -> None:
        """Decrease volume."""
        _LOGGER.debug(
            "async_volume_down called; tv_entity_id=%s",
            self._tv_entity_id,
        )
        await self.hass.services.async_call(
            "media_player",
            "volume_down",
            {"entity_id": self._tv_entity_id},
            blocking=True,
        )

    async def async_mute_volume(self, mute: bool) -> None:  # noqa: FBT001
        """Mute or unmute the volume."""
        _LOGGER.debug(
            "async_mute_volume called; tv_entity_id=%s mute=%s",
            self._tv_entity_id,
            mute,
        )
        await self.hass.services.async_call(
            "media_player",
            "volume_mute",
            {"entity_id": self._tv_entity_id, "is_volume_muted": mute},
            blocking=True,
        )

    async def async_select_source(self, source: str) -> None:
        """Select input source."""
        _LOGGER.debug(
            "async_select_source called; tv_entity_id=%s source=%s",
            self._tv_entity_id,
            source,
        )
        await self.hass.services.async_call(
            "media_player",
            "select_source",
            {"entity_id": self._tv_entity_id, "source": source},
            blocking=True,
        )

    async def async_media_play(self) -> None:
        """Send play command to TV."""
        _LOGGER.debug(
            "async_media_play called; tv_entity_id=%s",
            self._tv_entity_id,
        )
        await self.hass.services.async_call(
            "media_player",
            "media_play",
            {"entity_id": self._tv_entity_id},
            blocking=True,
        )

    async def async_media_pause(self) -> None:
        """Send pause command to TV."""
        _LOGGER.debug(
            "async_media_pause called; tv_entity_id=%s",
            self._tv_entity_id,
        )
        await self.hass.services.async_call(
            "media_player",
            "media_pause",
            {"entity_id": self._tv_entity_id},
            blocking=True,
        )

    async def async_media_stop(self) -> None:
        """Send stop command to TV."""
        _LOGGER.debug(
            "async_media_stop called; tv_entity_id=%s",
            self._tv_entity_id,
        )
        await self.hass.services.async_call(
            "media_player",
            "media_stop",
            {"entity_id": self._tv_entity_id},
            blocking=True,
        )

    async def async_media_next_track(self) -> None:
        """Send next track command to TV."""
        _LOGGER.debug(
            "async_media_next_track called; tv_entity_id=%s",
            self._tv_entity_id,
        )
        await self.hass.services.async_call(
            "media_player",
            "media_next_track",
            {"entity_id": self._tv_entity_id},
            blocking=True,
        )

    async def async_media_previous_track(self) -> None:
        """Send previous track command to TV."""
        _LOGGER.debug(
            "async_media_previous_track called; tv_entity_id=%s",
            self._tv_entity_id,
        )
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
        elif current_source == "GhostTube":
            target_entity = self._ghosttube_entity_id

        _LOGGER.debug(
            "async_media_seek called; position=%s current_source=%s target_entity=%s",
            position,
            current_source,
            target_entity,
        )

        if target_entity:
            await self.hass.services.async_call(
                "media_player",
                "media_seek",
                {"entity_id": target_entity, "seek_position": position},
                blocking=True,
            )
        else:
            _LOGGER.debug(
                "async_media_seek skipped; no target entity available for source %s",
                current_source,
            )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.debug(
            "_handle_coordinator_update called; coordinator_data_present=%s",
            self.coordinator.data is not None,
        )
        self.async_write_ha_state()
