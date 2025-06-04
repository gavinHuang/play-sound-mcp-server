# Play Sound MCP Server

A Model Context Protocol (MCP) server that provides audio playback functionality for agentic coding agents. This server enables AI agents to play sound notifications when coding tasks are completed, enhancing the user experience with auditory feedback.

## 🎯 Project Overview

This MCP server is designed to alert users when coding tasks are completed by playing sound notifications. It supports both default bundled sounds and custom user-specified audio files with intelligent fallback mechanisms.

### Key Features

- **Default Sound Notifications**: Bundled default notification sound for immediate use
- **Custom Audio Support**: Play user-specified audio files via MCP configuration
- **Intelligent Fallback**: Automatic fallback to default sound if custom audio fails
- **Cross-Platform**: Initially targeting macOS with future cross-platform support
- **Lightweight Dependencies**: Uses minimal, permissive-licensed libraries
- **Multiple Audio Formats**: Support for WAV, MP3, FLAC, and other common formats

## 🏗️ Architecture

The server follows MCP best practices with a clean, modular architecture:

```
play-sound-mcp-server/
├── src/
│   ├── play_sound_server/
│   │   ├── __init__.py
│   │   ├── server.py          # Main MCP server implementation
│   │   ├── audio_player.py    # Audio playback logic
│   │   ├── config.py          # Configuration management
│   │   └── utils.py           # Utility functions
│   └── assets/
│       └── default_notification.wav  # Bundled default sound
├── tests/
├── docs/
├── pyproject.toml
├── README.md
└── LICENSE
```

## 🚀 Quick Start

### Installation

```bash
# Using uvx (recommended)
uvx mcp-server-play-sound

# Using pip
pip install mcp-server-play-sound
python -m mcp_server_play_sound
```

### Claude Desktop Configuration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "play-sound": {
      "command": "uvx",
      "args": ["mcp-server-play-sound"],
      "env": {
        "CUSTOM_SOUND_PATH": "/path/to/your/notification.wav"
      }
    }
  }
}
```

## 🔧 Configuration

The server supports configuration through environment variables:

- `CUSTOM_SOUND_PATH`: Path to custom audio file (optional)
- `VOLUME_LEVEL`: Playback volume (0.0-1.0, default: 0.8)
- `ENABLE_FALLBACK`: Enable fallback to default sound (default: true)

## 📖 Documentation

- [Research Findings](docs/research-findings.md) - MCP patterns and audio library analysis
- [Architecture Design](docs/architecture.md) - Detailed system design
- [Implementation Plan](docs/implementation-plan.md) - Development roadmap
- [Configuration Schema](docs/configuration-schema.md) - Complete configuration reference

## 🛠️ Development

### Prerequisites

- Python 3.10+
- uv (recommended) or pip

### Setup

```bash
git clone https://github.com/your-username/play-sound-mcp-server.git
cd play-sound-mcp-server
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

### Testing

```bash
pytest tests/
```

## 📋 MCP Tools

The server exposes the following MCP tools:

### `play_notification_sound`

Plays a notification sound to alert the user.

**Parameters:**
- `message` (optional): Custom message to log with the notification
- `sound_type` (optional): "default" or "custom" (defaults to user configuration)

**Example Usage:**
```python
# In an AI agent workflow
await mcp_client.call_tool("play_notification_sound", {
    "message": "Code compilation completed successfully!"
})
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io/) by Anthropic
- Python audio library maintainers
- Open source community

---

**Status**: 🚧 In Development - See [Implementation Plan](docs/implementation-plan.md) for current progress
