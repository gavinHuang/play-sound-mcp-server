# Client Configuration Guide

This guide shows how to configure MCP clients like Claude Desktop and Cursor to use the MCP Play Sound Server.

## Development Setup

### For Claude Desktop

Add this configuration to your Claude Desktop MCP settings file:

**Location**: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)

**Option 1: Using uv (Recommended)**
```json
{
  "mcpServers": {
    "play-sound": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/your/play-sound-mcp-server",
        "run",
        "mcp-server-play-sound"
      ]
    }
  }
}
```

**Option 2: Direct Python (Alternative)**
```json
{
  "mcpServers": {
    "play-sound": {
      "command": "/path/to/your/play-sound-mcp-server/.venv/bin/python",
      "args": ["-m", "mcp_server_play_sound"]
    }
  }
}
```

**Option 3: Future uvx Package**
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

### For Cursor

Add this to your Cursor MCP configuration:

**Location**: Cursor Settings → Extensions → MCP → Add Server

```json
{
  "name": "play-sound",
  "command": "python",
  "args": ["/path/to/your/play-sound-mcp-server/src/mcp_server_play_sound/__main__.py"],
  "env": {
    "PYTHONPATH": "/path/to/your/play-sound-mcp-server/src"
  }
}
```

## Available Tools

Once configured, you'll have access to these tools in your MCP client:

### 1. `play_notification_sound`
Play a notification sound to get your attention.

**Parameters:**
- `custom_sound_path` (optional): Path to a custom audio file
- `message` (optional): Context message for the notification

**Example usage in Claude:**
> "Play a notification sound when you're done with this task"

### 2. `get_audio_status`
Check the current audio system status and configuration.

**Example usage:**
> "Check if the audio system is working properly"

### 3. `test_audio_playback`
Test audio playback functionality.

**Parameters:**
- `use_custom` (optional): Test with custom sound if configured

**Example usage:**
> "Test the audio system to make sure it's working"

## Environment Variables (Optional)

You can customize the server behavior with these environment variables:

```bash
# Audio settings
export VOLUME_LEVEL=0.8                    # Volume (0.0 to 1.0)
export CUSTOM_SOUND_PATH="/path/to/sound.wav"  # Custom notification sound
export ENABLE_FALLBACK=true               # Use default sound if custom fails

# Advanced settings
export AUDIO_BACKEND=auto                 # auto, afplay, simpleaudio
export PLAYBACK_TIMEOUT_SECONDS=30        # Playback timeout
export MAX_FILE_SIZE_MB=10                # Max audio file size

# Security settings
export RESTRICT_TO_USER_HOME=true         # Restrict file access to home directory
export ALLOWED_AUDIO_EXTENSIONS=wav,mp3,flac,ogg,m4a  # Allowed file types
```

## Testing the Configuration

1. **Restart your MCP client** (Claude Desktop/Cursor) after adding the configuration
2. **Test the connection** by asking: "Can you play a notification sound?"
3. **Check status** by asking: "What's the status of the audio system?"

## Troubleshooting

### Common Issues

**"Server not found" or "Connection failed":**
- Check that the path to your project directory is correct
- Ensure the virtual environment is activated if using `.venv/bin/python`
- Verify that `mcp_server_play_sound` can be imported

**"No audio backends available":**
- On macOS: `afplay` should be available by default
- Install simpleaudio: `pip install simpleaudio`
- Check audio permissions in System Preferences

**"Permission denied" errors:**
- Make sure the Python executable has the correct permissions
- Check that audio files are readable
- Verify `RESTRICT_TO_USER_HOME` setting if using custom sounds

### Debug Mode

Add this to see detailed logs:

```json
{
  "mcpServers": {
    "play-sound": {
      "command": "/path/to/your/play-sound-mcp-server/.venv/bin/python",
      "args": ["-m", "mcp_server_play_sound"],
      "cwd": "/path/to/your/play-sound-mcp-server",
      "env": {
        "PYTHONPATH": "/path/to/your/play-sound-mcp-server/src",
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

## Package Distribution Plan

### Current Status: Development
- ✅ Local development setup (this guide)
- ✅ Source code installation from repository

### Phase 1: PyPI Package (Coming Soon)
Once we complete testing and documentation:

```bash
# Install from PyPI (future)
pip install mcp-server-play-sound

# Simple configuration (future)
{
  "mcpServers": {
    "play-sound": {
      "command": "mcp-server-play-sound"
    }
  }
}
```

### Phase 2: Pre-built Distributions
- **NPX package**: `npx mcp-server-play-sound` (cross-platform)
- **Homebrew**: `brew install mcp-server-play-sound` (macOS)
- **Docker**: `docker run mcp-server-play-sound` (all platforms)

### Phase 3: MCP Registry
- Listed in the official MCP server registry
- One-click installation in MCP clients
- Automatic updates and version management

The goal is to make installation as simple as possible while maintaining the flexibility for custom configurations during development.
