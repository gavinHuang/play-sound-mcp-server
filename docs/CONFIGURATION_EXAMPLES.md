# MCP Configuration Examples

This document shows the correct configuration patterns for different deployment scenarios.

## Development (Local Source)

### Using uv (Recommended)
```json
{
  "mcpServers": {
    "play-sound": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/play-sound-mcp-server",
        "run",
        "mcp-server-play-sound"
      ]
    }
  }
}
```

### Direct Python (Alternative)
```json
{
  "mcpServers": {
    "play-sound": {
      "command": "/path/to/play-sound-mcp-server/.venv/bin/python",
      "args": ["-m", "mcp_server_play_sound"]
    }
  }
}
```

## Production (PyPI Package)

### Using uvx (Recommended)
```json
{
  "mcpServers": {
    "play-sound": {
      "command": "uvx",
      "args": ["mcp-server-play-sound"]
    }
  }
}
```

### Using npx (Alternative)
```json
{
  "mcpServers": {
    "play-sound": {
      "command": "npx",
      "args": ["mcp-server-play-sound"]
    }
  }
}
```

### Using pip install + direct command
```json
{
  "mcpServers": {
    "play-sound": {
      "command": "mcp-server-play-sound"
    }
  }
}
```

## With Environment Variables

### Custom Sound Configuration
```json
{
  "mcpServers": {
    "play-sound": {
      "command": "uvx",
      "args": ["mcp-server-play-sound"],
      "env": {
        "CUSTOM_SOUND_PATH": "/Users/username/sounds/notification.wav",
        "VOLUME_LEVEL": "0.6",
        "ENABLE_FALLBACK": "true"
      }
    }
  }
}
```

### Debug Mode
```json
{
  "mcpServers": {
    "play-sound": {
      "command": "uvx",
      "args": ["mcp-server-play-sound"],
      "env": {
        "LOG_LEVEL": "DEBUG",
        "AUDIO_BACKEND": "afplay"
      }
    }
  }
}
```

## Platform-Specific Examples

### macOS with Homebrew (Future)
```json
{
  "mcpServers": {
    "play-sound": {
      "command": "/opt/homebrew/bin/mcp-server-play-sound"
    }
  }
}
```

### Windows
```json
{
  "mcpServers": {
    "play-sound": {
      "command": "uvx",
      "args": ["mcp-server-play-sound"],
      "env": {
        "CUSTOM_SOUND_PATH": "C:\\Users\\username\\sounds\\notification.wav"
      }
    }
  }
}
```

### Linux
```json
{
  "mcpServers": {
    "play-sound": {
      "command": "uvx",
      "args": ["mcp-server-play-sound"],
      "env": {
        "AUDIO_BACKEND": "simpleaudio"
      }
    }
  }
}
```

## Docker (Future)

### Using Docker Image
```json
{
  "mcpServers": {
    "play-sound": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "--device", "/dev/snd",
        "mcp-server-play-sound:latest"
      ]
    }
  }
}
```

## Key Configuration Patterns

1. **Command**: The executable to run
   - `uvx` for PyPI packages (recommended)
   - `npx` for npm packages
   - Direct path for local development
   - Package name for globally installed packages

2. **Args**: Arguments passed to the command
   - Package name for uvx/npx
   - Script path for local development
   - Additional flags if needed

3. **Env**: Environment variables
   - Configuration options
   - Debug settings
   - Custom paths

4. **No cwd**: Current working directory is not typically needed with proper packaging

## Migration Path

### Current (Development)
```json
{
  "command": "uv",
  "args": [
    "--directory",
    "/path/to/play-sound-mcp-server",
    "run",
    "mcp-server-play-sound"
  ]
}
```

### Phase 1 (PyPI)
```json
{
  "command": "uvx",
  "args": ["mcp-server-play-sound"]
}
```

### Phase 2 (Registry)
```json
{
  "command": "mcp-server-play-sound"
}
```

This progression shows how the configuration becomes simpler as the package becomes more widely available.
