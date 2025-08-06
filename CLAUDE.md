# CLAUDE.md

This file provides guidance to Claude Code when working with The Phantom Apparatus.

## Project Overview

Home Assistant integration that creates a unified media player by combining:
- WebOS TV entity (hardware controls: power, volume, source selection)
- Jellyfin entity (media playback when active)
- GhostTube entity (media playback when active)

The integration intelligently routes commands and displays media info based on the TV's current source.

## Development Commands

```bash
./scripts/setup     # Install dependencies
./scripts/lint      # Run ruff for formatting and checking
./scripts/develop   # Start HA in debug mode with config in ./config
```

## Architecture

### Core Components

- **Media Player** (`media_player.py`): Main entity that routes commands between TV and app entities
- **Coordinator** (`coordinator.py`): Uses event listeners for instant state updates (no polling)
- **Config Flow** (`config_flow.py`): UI configuration for selecting the three entities

### Key Behaviors

1. **Control Routing**:
   - To TV: power (via WoL), volume, mute, source, play/pause/stop, next/previous
   - To active app: seek position
   - Media info: from whichever app is active

2. **Source List**: Shows Jellyfin and Ghost Tube, plus current source if different

3. **Power On**: Uses `shell_command.wake_living_room_tv` instead of TV's turn_on

## Important Notes

- Domain: `phantom_apparatus`
- No external API dependencies - works entirely with HA entities
- Uses push updates via state change listeners for instant response