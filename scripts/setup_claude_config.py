#!/usr/bin/env python3
"""
Setup script to automatically configure Claude Desktop for development.
"""

import json
import sys
from pathlib import Path


def get_claude_config_path():
    """Get the Claude Desktop configuration file path."""
    if sys.platform == "darwin":  # macOS
        return Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
    elif sys.platform == "win32":  # Windows
        return Path.home() / "AppData/Roaming/Claude/claude_desktop_config.json"
    else:  # Linux
        return Path.home() / ".config/Claude/claude_desktop_config.json"


def get_project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent.resolve()


def create_mcp_config():
    """Create the MCP server configuration."""
    project_root = get_project_root()

    # Use uv with --directory flag (recommended pattern)
    return {
        "command": "uv",
        "args": [
            "--directory",
            str(project_root),
            "run",
            "mcp-server-play-sound"
        ]
    }


def main():
    """Main setup function."""
    print("🔧 MCP Play Sound Server - Claude Desktop Setup")
    print("=" * 50)
    
    # Get configuration paths
    config_path = get_claude_config_path()
    project_root = get_project_root()
    
    print(f"Project root: {project_root}")
    print(f"Claude config: {config_path}")
    
    # Create configuration directory if it doesn't exist
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing configuration or create new one
    if config_path.exists():
        print("📖 Loading existing Claude configuration...")
        with open(config_path, 'r') as f:
            config = json.load(f)
    else:
        print("📝 Creating new Claude configuration...")
        config = {}
    
    # Ensure mcpServers section exists
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    
    # Add our server configuration
    mcp_config = create_mcp_config()
    config["mcpServers"]["play-sound"] = mcp_config
    
    # Write configuration back
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Configuration updated successfully!")
    print("\nAdded MCP server configuration:")
    print(json.dumps({"play-sound": mcp_config}, indent=2))
    
    print("\n📋 Next Steps:")
    print("1. Restart Claude Desktop")
    print("2. Test by asking: 'Can you play a notification sound?'")
    print("3. Check status with: 'What's the audio system status?'")
    
    print("\n🔧 To customize, set environment variables:")
    print("   export VOLUME_LEVEL=0.5")
    print("   export CUSTOM_SOUND_PATH='/path/to/your/sound.wav'")
    
    print(f"\n📁 Configuration saved to: {config_path}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
