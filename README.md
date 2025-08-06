# The Phantom Apparatus

A Home Assistant integration that unifies WebOS TV controls with media app entities (Jellyfin & GhostTube) into a single media player.

## Features

- Combines TV hardware controls with app media information
- Smart source switching between apps
- Wake-on-LAN support for TV power on
- Instant updates via entity state listeners (no polling)

## Installation

Copy the `custom_components/phantom_apparatus` folder to your Home Assistant's `custom_components` directory and restart.

## Configuration

Add via the Home Assistant UI. You'll need:
- Your WebOS TV media player entity
- Jellyfin media player entity
- GhostTube media player entity

## Development

```bash
./scripts/setup     # Install dependencies
./scripts/lint      # Run linting
./scripts/develop   # Start HA for testing
```

*Attribution: The Ghost of Don Don*