#!/usr/bin/env python3
"""
Simple test to verify the MCP server works.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_server_play_sound.config import ServerConfig
from mcp_server_play_sound.audio_player import AudioPlayer
from mcp_server_play_sound.server import PlaySoundServer

def test_server_creation():
    """Test that we can create the server without errors."""
    print("🧪 Testing MCP Play Sound Server Creation")
    print("=" * 40)
    
    try:
        # Create configuration
        config = ServerConfig.from_environment()
        print(f"✅ Configuration loaded")
        
        # Validate configuration
        config.validate()
        print(f"✅ Configuration validated")
        
        # Create server
        server = PlaySoundServer(config)
        print(f"✅ Server created successfully")
        
        # Get server info
        info = server.get_server_info()
        print(f"✅ Server info: {info['name']} v{info['version']}")
        print(f"   - Tools: {info['tools_count']}")
        print(f"   - Backends: {info['backends_available']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_server_creation()
    print(f"\n{'✅ All tests passed!' if success else '❌ Tests failed!'}")
    sys.exit(0 if success else 1)
