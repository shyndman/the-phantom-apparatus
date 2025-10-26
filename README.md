# The Phantom Apparatus

A Home Assistant integration that unifies WebOS TV controls with media app entities (Jellyfin & GhostTube) into a single media player.

## Features

- Combines TV hardware controls with app media information
- Smart source switching between apps
- Wake-on-LAN support for TV power on
- Instant updates via entity state listeners (no polling)

## Scope & Assumptions

This project intentionally targets a single household setup (LG WebOS TV + Jellyfin + GhostTube). It only exposes those sources and expects a custom Wake-on-LAN shell command, so treat it as a personal automation rather than a drop-in community integration.

```yaml
# configuration.yaml
shell_command:
  wake_living_room_tv: "wakeonlan AA:BB:CC:DD:EE:FF"
```

## Installation

Copy the `custom_components/phantom_apparatus` folder to your Home Assistant's `custom_components` directory and restart.

## Configuration

Add via the Home Assistant UI. You'll need:
- Your WebOS TV media player entity
- Jellyfin media player entity
- GhostTube media player entity

Ensure a matching `shell_command.wake_living_room_tv` exists (see above) so the unified media player can turn your TV on.

## Development

```bash
./scripts/setup     # Install dependencies
./scripts/lint      # Run linting
./scripts/develop   # Start HA for testing
```

*Attribution: The Ghost of Don Don*
