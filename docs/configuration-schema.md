# Configuration Schema

## Overview

The Play Sound MCP Server uses environment variables for configuration, following MCP best practices for server configuration. All configuration options are optional with sensible defaults.

## Environment Variables

### Core Configuration

#### `CUSTOM_SOUND_PATH`
- **Type**: String (file path)
- **Default**: None (uses bundled default sound)
- **Description**: Path to custom audio file for notifications
- **Example**: `/Users/username/sounds/notification.wav`
- **Validation**: 
  - File must exist and be readable
  - Must be a supported audio format
  - File size must be under `MAX_FILE_SIZE_MB`

#### `VOLUME_LEVEL`
- **Type**: Float
- **Default**: `0.8`
- **Range**: `0.0` to `1.0`
- **Description**: Playback volume level (0.0 = silent, 1.0 = maximum)
- **Example**: `0.5`
- **Validation**: Must be between 0.0 and 1.0 inclusive

#### `ENABLE_FALLBACK`
- **Type**: Boolean
- **Default**: `true`
- **Description**: Enable fallback to default sound if custom sound fails
- **Example**: `false`
- **Validation**: Must be `true`, `false`, `1`, `0`, `yes`, `no` (case-insensitive)

### Advanced Configuration

#### `MAX_FILE_SIZE_MB`
- **Type**: Integer
- **Default**: `10`
- **Range**: `1` to `100`
- **Description**: Maximum allowed file size for custom audio files (in MB)
- **Example**: `5`
- **Validation**: Must be positive integer between 1 and 100

#### `PLAYBACK_TIMEOUT_SECONDS`
- **Type**: Integer
- **Default**: `30`
- **Range**: `1` to `300`
- **Description**: Maximum time to wait for audio playback completion
- **Example**: `15`
- **Validation**: Must be positive integer between 1 and 300

#### `AUDIO_BACKEND`
- **Type**: String
- **Default**: `auto`
- **Options**: `auto`, `simpleaudio`, `pydub`, `system`
- **Description**: Preferred audio backend for playback
- **Example**: `simpleaudio`
- **Validation**: Must be one of the supported backend options

#### `ENABLE_AUDIO_CACHE`
- **Type**: Boolean
- **Default**: `true`
- **Description**: Enable caching of loaded audio files for better performance
- **Example**: `false`
- **Validation**: Must be boolean value

#### `CACHE_SIZE_LIMIT`
- **Type**: Integer
- **Default**: `5`
- **Range**: `1` to `20`
- **Description**: Maximum number of audio files to keep in cache
- **Example**: `3`
- **Validation**: Must be positive integer between 1 and 20

### Security Configuration

#### `ALLOWED_AUDIO_EXTENSIONS`
- **Type**: String (comma-separated)
- **Default**: `.wav,.mp3,.flac,.ogg,.m4a`
- **Description**: Allowed file extensions for custom audio files
- **Example**: `.wav,.mp3`
- **Validation**: Must be comma-separated list of extensions starting with dots

#### `RESTRICT_TO_USER_HOME`
- **Type**: Boolean
- **Default**: `true`
- **Description**: Restrict custom audio files to user's home directory
- **Example**: `false`
- **Validation**: Must be boolean value

## Configuration Examples

### Basic Configuration (Claude Desktop)

```json
{
  "mcpServers": {
    "play-sound": {
      "command": "uvx",
      "args": ["mcp-server-play-sound"],
      "env": {
        "CUSTOM_SOUND_PATH": "/Users/username/notification.wav",
        "VOLUME_LEVEL": "0.7"
      }
    }
  }
}
```

### Advanced Configuration

```json
{
  "mcpServers": {
    "play-sound": {
      "command": "uvx",
      "args": ["mcp-server-play-sound"],
      "env": {
        "CUSTOM_SOUND_PATH": "/Users/username/sounds/alert.mp3",
        "VOLUME_LEVEL": "0.6",
        "ENABLE_FALLBACK": "true",
        "MAX_FILE_SIZE_MB": "5",
        "PLAYBACK_TIMEOUT_SECONDS": "15",
        "AUDIO_BACKEND": "simpleaudio",
        "ENABLE_AUDIO_CACHE": "true",
        "CACHE_SIZE_LIMIT": "3"
      }
    }
  }
}
```

### Security-Focused Configuration

```json
{
  "mcpServers": {
    "play-sound": {
      "command": "uvx",
      "args": ["mcp-server-play-sound"],
      "env": {
        "CUSTOM_SOUND_PATH": "/Users/username/sounds/notification.wav",
        "MAX_FILE_SIZE_MB": "2",
        "ALLOWED_AUDIO_EXTENSIONS": ".wav,.mp3",
        "RESTRICT_TO_USER_HOME": "true",
        "ENABLE_FALLBACK": "true"
      }
    }
  }
}
```

## Configuration Validation

### Validation Rules

The server validates all configuration at startup and provides clear error messages:

```python
class ConfigurationError(Exception):
    """Raised when configuration is invalid."""
    pass

class ServerConfig:
    def validate(self) -> None:
        """Validate all configuration options."""
        self._validate_volume_level()
        self._validate_file_paths()
        self._validate_numeric_ranges()
        self._validate_boolean_values()
        self._validate_security_settings()
```

### Error Messages

**Invalid Volume Level:**
```
Configuration Error: VOLUME_LEVEL must be between 0.0 and 1.0, got: 1.5
```

**Invalid File Path:**
```
Configuration Error: CUSTOM_SOUND_PATH file does not exist: /invalid/path.wav
```

**Invalid File Size:**
```
Configuration Error: Custom audio file exceeds MAX_FILE_SIZE_MB limit (10MB): file.wav (15MB)
```

**Invalid Audio Format:**
```
Configuration Error: Audio file extension '.txt' not in ALLOWED_AUDIO_EXTENSIONS: .wav,.mp3,.flac,.ogg,.m4a
```

## Default Sound Configuration

### Bundled Default Sound

The server includes a bundled default notification sound with these characteristics:

- **Format**: WAV (uncompressed)
- **Sample Rate**: 44.1 kHz
- **Bit Depth**: 16-bit
- **Channels**: Mono
- **Duration**: ~1 second
- **Content**: Pleasant, non-intrusive notification tone
- **File Size**: ~88KB

### Default Sound Customization

While the bundled sound cannot be replaced, users can effectively override it by:

1. Setting `CUSTOM_SOUND_PATH` to their preferred sound
2. Setting `ENABLE_FALLBACK` to `false` to prevent fallback to default
3. Using the `sound_type` parameter in tool calls to specify "custom" explicitly

## Runtime Configuration

### Dynamic Configuration

Some configuration can be overridden at runtime through tool parameters:

```python
# Tool call with runtime configuration
await mcp_client.call_tool("play_notification_sound", {
    "message": "Task completed!",
    "sound_type": "custom",  # Override default behavior
    "volume": 0.5           # Override VOLUME_LEVEL for this call
})
```

### Configuration Precedence

Configuration values are resolved in this order (highest to lowest precedence):

1. **Tool call parameters** (runtime)
2. **Environment variables** (startup)
3. **Default values** (built-in)

## Troubleshooting Configuration

### Common Issues

#### Audio File Not Found
```bash
# Check file exists and is readable
ls -la /path/to/audio/file.wav
```

#### Permission Denied
```bash
# Check file permissions
chmod 644 /path/to/audio/file.wav
```

#### Invalid Audio Format
```bash
# Check file format
file /path/to/audio/file.wav
```

### Debug Mode

Enable debug logging by setting:

```json
{
  "env": {
    "LOG_LEVEL": "DEBUG",
    "ENABLE_CONFIG_LOGGING": "true"
  }
}
```

This will log all configuration values at startup (excluding sensitive data).

## Configuration Schema Validation

### JSON Schema

For tools that support JSON Schema validation:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "CUSTOM_SOUND_PATH": {
      "type": "string",
      "description": "Path to custom audio file"
    },
    "VOLUME_LEVEL": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0,
      "description": "Playback volume level"
    },
    "ENABLE_FALLBACK": {
      "type": "boolean",
      "description": "Enable fallback to default sound"
    },
    "MAX_FILE_SIZE_MB": {
      "type": "integer",
      "minimum": 1,
      "maximum": 100,
      "description": "Maximum file size in MB"
    }
  }
}
```

## Migration Guide

### From Future Versions

When upgrading between versions, configuration migration will be handled automatically with deprecation warnings for removed options.

### Configuration Backup

Before major updates, backup your configuration:

```bash
# Extract current configuration
echo $CUSTOM_SOUND_PATH > config_backup.txt
echo $VOLUME_LEVEL >> config_backup.txt
```
