# MCP Server Audio Device Configuration Guide for Augment Code

This guide provides comprehensive instructions for setting up and using the enhanced audio device functionality in the MCP (Model Context Protocol) server for audio notifications with Augment Code. The server provides intelligent audio device switching, allowing notifications to play through specific speakers while preserving your normal audio routing.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Testing](#testing)
- [Augment Code Integration](#augment-code-integration)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)

## Prerequisites

Before setting up the MCP server with audio device functionality, ensure you have:

### Required Software

1. **macOS** (this functionality is macOS-specific)
2. **Python 3.8+** with virtual environment support
3. **UV package manager** (for dependency management)
4. **SwitchAudioSource** (for audio device switching)
5. **Homebrew** (for installing dependencies)

### Installation Commands

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install UV package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install SwitchAudioSource for audio device switching
brew install switchaudio-osx

# Add UV to your PATH (add to ~/.zshrc or ~/.bashrc)
export PATH="$HOME/.local/bin:$PATH"
```

## Installation

### 1. Clone and Setup Project

```bash
# Navigate to your project directory
cd Path_to_your/play-sound-mcp-server

# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
uv sync
```

### 2. Generate Default Sound File

```bash
# Generate the default notification sound
python scripts/generate_default_sound.py
```

### 3. Verify Installation

```bash
# Test basic functionality
uv run mcp-server-play-sound --help
```

## Configuration

### Environment Variables

The MCP server supports the following environment variables for audio configuration:

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `AUDIO_DEVICE` | Specific audio output device name | *(current system default)* | `"Mac Studio Speakers"` |
| `VOLUME_LEVEL` | Playback volume (0.0-1.0) | `0.8` | `0.5` |
| `CUSTOM_SOUND_PATH` | Path to custom audio file | *(built-in sound)* | `"/path/to/sound.wav"` |
| `ENABLE_FALLBACK` | Enable fallback to default sound | `true` | `false` |

### Audio Device Configuration Options

#### Option 1: Use Specific Device
```bash
export AUDIO_DEVICE="Mac Studio Speakers"
```

#### Option 2: Use System Default
```bash
export AUDIO_DEVICE="system default"
# or simply don't set AUDIO_DEVICE
```

#### Option 3: No Device Switching
```bash
# Leave AUDIO_DEVICE unset or empty
unset AUDIO_DEVICE
```

### Persistent Configuration

Add to your shell profile (`~/.zshrc` or `~/.bashrc`):

```bash
# Audio device configuration for MCP server
export AUDIO_DEVICE="Mac Studio Speakers"
export VOLUME_LEVEL="0.8"

# Reload with: source ~/.zshrc
```

## Testing

### Using the Enhanced Test Script

The project includes an enhanced `tests/test_audio_devices.py` script with comprehensive testing capabilities.

#### 1. List Available Devices

```bash
# Show all available audio devices and current device
python tests/test_audio_devices.py

# Only list devices (compact view)
python tests/test_audio_devices.py --list-only

# Show only current device
python tests/test_audio_devices.py --current
```

#### 2. Test Specific Device

```bash
# Test with Mac Studio Speakers
python tests/test_audio_devices.py --audio-device "Mac Studio Speakers"

# Test with headphones
python tests/test_audio_devices.py --audio-device "BW01"

# Test with system default (no device switching)
python tests/test_audio_devices.py --audio-device ""
```

#### 3. Test Device Restoration

The test script automatically verifies that:
- ✅ Audio plays through the specified device
- ✅ Original device is restored after playback
- ✅ No audio routing is permanently changed

### Manual Testing

```bash
# Test with environment variable
export AUDIO_DEVICE="Mac Studio Speakers"
source .venv/bin/activate
python -c "
import asyncio
import sys
sys.path.insert(0, 'src')
from mcp_server_play_sound.config import ServerConfig
from mcp_server_play_sound.audio_player import AudioPlayer

async def test():
    config = ServerConfig.from_environment()
    player = AudioPlayer(config)
    result = await player.play_notification()
    print(f'Result: {result.message}')

asyncio.run(test())
"
```

## Augment Code Integration

### Why Use This MCP Server with Augment Code?

Augment Code's advanced AI coding assistant can benefit greatly from audio notifications:

- **Task Completion Alerts** - Get notified when code generation, testing, or analysis completes
- **Error Notifications** - Audio alerts for build failures or critical issues
- **Focus Management** - Audio cues to help manage context switching during coding sessions
- **Accessibility** - Audio feedback for developers who prefer auditory notifications

### Setting up MCP Server in Augment

Augment Code provides a user-friendly interface for configuring MCP servers through the Settings area. You can add the play-sound MCP server using JSON import functionality, which is much easier than manually editing configuration files.

### Step-by-Step Setup

#### 1. Access Augment Settings
1. Open Augment Code
2. Navigate to **Settings** (gear icon or menu)
3. Look for **MCP Servers** or **Extensions** section
4. Click **Add MCP Server** or **Import Configuration**

#### 2. Import MCP Server Configuration

Choose one of the following configurations based on your needs:

##### Basic Configuration (No Audio Device Specified)
Copy and paste this JSON configuration:

```json
{
  "name": "play-sound",
  "description": "Audio notification MCP server",
  "command": "uv",
  "args": [
    "--directory",
    "Path_to_your/play-sound-mcp-server",
    "run",
    "mcp-server-play-sound"
  ],
  "env": {}
}
```

##### With Mac Studio Speakers Configuration
Copy and paste this JSON configuration:

```json
{
  "name": "play-sound",
  "description": "Audio notification MCP server - Mac Studio Speakers",
  "command": "uv",
  "args": [
    "--directory",
    "Path_to_your/play-sound-mcp-server",
    "run",
    "mcp-server-play-sound"
  ],
  "env": {
    "AUDIO_DEVICE": "Mac Studio Speakers",
    "VOLUME_LEVEL": "0.8"
  }
}
```

##### Advanced Configuration with Custom Sound
Copy and paste this JSON configuration:

```json
{
  "name": "play-sound",
  "description": "Audio notification MCP server - Advanced config",
  "command": "uv",
  "args": [
    "--directory",
    "Path_to_your/play-sound-mcp-server",
    "run",
    "mcp-server-play-sound"
  ],
  "env": {
    "AUDIO_DEVICE": "Mac Studio Speakers",
    "VOLUME_LEVEL": "0.7",
    "CUSTOM_SOUND_PATH": "/Users/username/custom-notification.wav",
    "ENABLE_FALLBACK": "true"
  }
}
```

#### 3. Configure Path (Important!)
**⚠️ Update the Directory Path**: Make sure to update the `--directory` path in the `args` section to match your actual installation location:

- If you cloned to a different location, update the path accordingly
- Use the full absolute path to avoid issues
- Example: `Path_to_your/play-sound-mcp-server`

#### 4. Save and Activate
1. Click **Save** or **Import** to add the MCP server
2. The server should appear in your MCP servers list
3. Enable/activate the server if needed
4. Restart Augment Code if prompted

### Verification in Augment

After setup, verify the MCP server is working:

#### 1. Check MCP Server Status
- Look for the "play-sound" server in your MCP servers list
- Status should show as "Connected" or "Active"
- Check for any error messages

#### 2. Test Available Tools
The following tools should be available in Augment:

- **`play_notification_sound`** - Play audio notifications
- **`get_audio_status`** - Check audio system status
- **`test_audio_playback`** - Test audio functionality
- **`list_audio_devices`** - List available audio devices

#### 3. Test Audio Functionality
Try asking Augment to:
- "Play a notification sound"
- "Test the audio system"
- "List available audio devices"
- "Check audio status"

### Alternative: Manual Configuration File

If Augment uses a configuration file similar to Claude Desktop, you can also manually edit the configuration file (usually located in Augment's settings directory):

```json
{
  "mcpServers": {
    "play-sound": {
      "command": "uv",
      "args": [
        "--directory",
        "Path_to_your/play-sound-mcp-server",
        "run",
        "mcp-server-play-sound"
      ],
      "env": {
        "AUDIO_DEVICE": "Mac Studio Speakers",
        "VOLUME_LEVEL": "0.8"
      }
    }
  }
}
```

### Restart Augment

After updating the configuration:
1. Save all changes in Augment Settings
2. Restart Augment Code completely
3. Verify the MCP server appears in the available tools
4. Test audio functionality

## Troubleshooting

### Augment Code Specific Issues

#### 1. MCP Server Not Appearing in Augment
```bash
# Check if the server is properly configured
# In Augment Settings, verify:
# - Server name is "play-sound"
# - Command path is correct
# - Directory path exists and is accessible
```

#### 2. "Command not found: uv" in Augment
```bash
# Ensure UV is in the system PATH
echo $PATH | grep -q "$HOME/.local/bin" && echo "✅ UV path found" || echo "❌ UV path missing"

# Add to system PATH (may require Augment restart)
export PATH="$HOME/.local/bin:$PATH"
```

#### 3. Permission Issues in Augment
```bash
# Ensure Augment has permission to execute the MCP server
chmod +x Path_to_your/play-sound-mcp-server/.venv/bin/mcp-server-play-sound

# Check directory permissions
ls -la Path_to_your
/play-sound-mcp-server/
```

#### 4. MCP Server Shows as "Disconnected" in Augment
- Check the Augment logs/console for error messages
- Verify all prerequisites are installed
- Test the server manually: `uv run mcp-server-play-sound`
- Ensure the directory path in the configuration is correct

### Common System Issues

#### 5. "SwitchAudioSource not found"
```bash
# Install SwitchAudioSource
brew install switchaudio-osx

# Verify installation
which SwitchAudioSource
```

#### 6. "UV not found"
```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
```

#### 7. Device Not Found
```bash
# List available devices
python tests/test_audio_devices.py --list-only

# Check exact device name (case-sensitive)
SwitchAudioSource -a
```

#### 8. Audio Not Playing Through Specified Device
```bash
# Test device switching manually
SwitchAudioSource -c  # Show current
SwitchAudioSource -s "Mac Studio Speakers"  # Switch
afplay /System/Library/Sounds/Glass.aiff  # Test
```

#### 9. Device Not Restoring After Playback
```bash
# Check if restoration logic is working
python tests/test_device_restoration.py

# Manually restore if needed
SwitchAudioSource -s "BW01"  # Replace with your device
```

### Debug Mode

Enable verbose logging:

```bash
export PYTHONPATH="src:$PYTHONPATH"
export LOG_LEVEL="DEBUG"
python tests/test_audio_devices.py --audio-device "Mac Studio Speakers"
```

### Verification Steps

1. **Check Prerequisites**:
   ```bash
   which uv && echo "✅ UV installed" || echo "❌ UV missing"
   which SwitchAudioSource && echo "✅ SwitchAudioSource installed" || echo "❌ SwitchAudioSource missing"
   ```

2. **Test Audio System**:
   ```bash
   python tests/test_audio_devices.py --current
   ```

3. **Test MCP Server**:
   ```bash
   uv run mcp-server-play-sound &
   # Should start without errors
   ```

## Advanced Usage

### Custom Sound Files

```bash
# Use custom notification sound
export CUSTOM_SOUND_PATH="/path/to/your/sound.wav"
export AUDIO_DEVICE="Mac Studio Speakers"
```

### Multiple Device Configurations

Create different shell aliases for different setups:

```bash
# Add to ~/.zshrc
alias mcp-speakers='export AUDIO_DEVICE="Mac Studio Speakers" && uv run mcp-server-play-sound'
alias mcp-headphones='export AUDIO_DEVICE="BW01" && uv run mcp-server-play-sound'
alias mcp-default='unset AUDIO_DEVICE && uv run mcp-server-play-sound'
```

### Scripted Device Management

```bash
# Create a device switching script
cat > switch_audio_for_mcp.sh << 'EOF'
#!/bin/bash
DEVICE="$1"
if [ -z "$DEVICE" ]; then
    echo "Usage: $0 <device-name>"
    echo "Available devices:"
    SwitchAudioSource -a
    exit 1
fi

export AUDIO_DEVICE="$DEVICE"
echo "Starting MCP server with audio device: $DEVICE"
uv run mcp-server-play-sound
EOF

chmod +x switch_audio_for_mcp.sh
```

## Support

For issues or questions:

1. Check the [Troubleshooting](#troubleshooting) section
2. Run the test script: `python tests/test_audio_devices.py`
3. Check the project's GitHub issues
4. Verify your system meets all [Prerequisites](#prerequisites)

---

**Note**: This audio device functionality is designed specifically for macOS and requires the SwitchAudioSource utility for reliable device switching and restoration.
