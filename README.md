# MCP Play Sound Server

A Model Context Protocol (MCP) server that provides audio playback functionality for AI agents. This server enables AI agents to play sound notifications when coding tasks are completed.

> **⚠️ Early Version / Proof of Concept**
> This is an early implementation currently tested only on macOS. Future versions will support additional platforms.

## Features

- **Audio Notifications**: Play sound alerts when AI tasks complete
- **Default Sound**: Bundled notification sound for immediate use
- **Custom Audio**: Support for custom audio files (WAV, MP3, FLAC, OGG, M4A)
- **Intelligent Fallback**: Automatic fallback to default sound if custom audio fails
- **macOS Support**: Currently tested on macOS using AFPlay and SimpleAudio

## Installation & Setup

### Development Setup

1. **Clone and install**:
```bash
git clone <repository-url>
cd play-sound-mcp-server
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

2. **Configure Claude Desktop**:
Add to your `claude_desktop_config.json`:

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

3. **Test**: Restart Claude Desktop and ask: "Can you play a notification sound?"

## Configuration

Environment variables (optional):
- `CUSTOM_SOUND_PATH`: Path to custom audio file
- `VOLUME_LEVEL`: Playback volume (0.0-1.0, default: 0.8)
- `ENABLE_FALLBACK`: Enable fallback to default sound (default: true)

## Available Tools

### `play_notification_sound`
Plays a notification sound to alert the user.

**Parameters:**
- `custom_sound_path` (optional): Path to custom audio file
- `message` (optional): Context message for the notification

### `get_audio_status`
Returns current audio system status and configuration.

### `test_audio_playback`
Tests audio playback functionality.

**Parameters:**
- `use_custom` (optional): Test with custom sound if configured

## Development

### Prerequisites
- Python 3.10+
- uv (recommended) or pip

### Testing
```bash
pytest tests/
```

## License

MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io/) by Anthropic
- Python audio library maintainers
