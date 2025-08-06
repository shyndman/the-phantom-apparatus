# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Home Assistant custom component blueprint repository that serves as a template for building custom integrations. The integration currently named "integration_blueprint" should be renamed to match your specific integration's domain.

## Development Commands

```bash
# Install dependencies
./scripts/setup

# Run linting and formatting
./scripts/lint  # Uses ruff for formatting and checking

# Start Home Assistant with the integration for testing
./scripts/develop  # Starts HA in debug mode with config in ./config
```

## Architecture

### Core Integration Structure

The integration follows Home Assistant's standard custom component architecture:

- **Entry Point** (`__init__.py`): Sets up the integration using config entries, initializes the data coordinator, and forwards setup to platforms
- **Data Coordinator** (`coordinator.py`): Manages centralized data fetching using `DataUpdateCoordinator` pattern with 1-hour update intervals
- **API Client** (`api.py`): Handles external API communication with proper error handling for authentication and communication failures
- **Config Flow** (`config_flow.py`): Manages UI-based configuration with username/password authentication
- **Platforms**: Implements sensor, binary_sensor, and switch platforms that share data through the coordinator

### Key Design Patterns

1. **Coordinated Data Updates**: All entities share a single data source updated by `BlueprintDataUpdateCoordinator`
2. **Runtime Data Storage**: Uses `IntegrationBlueprintData` dataclass stored in `entry.runtime_data`
3. **Error Handling**: Distinguishes between authentication errors (triggers reauth) and communication errors (retries)

## Important Notes

- The integration uses the domain `integration_blueprint` - this should be renamed throughout the codebase for actual implementations
- Config is stored in `./config` directory when developing locally
- Uses `PYTHONPATH` manipulation in develop script to maintain the proper structure
- All new code should follow existing patterns for consistency