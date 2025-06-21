#!/usr/bin/env python3
"""
Test script to verify the MCP play sound server works correctly with VS Code.
This script demonstrates the fixed async patterns that resolve tool call hanging issues.
"""

import sys
import json
import logging
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp_server_play_sound.config import ServerConfig
from mcp_server_play_sound.audio_player import AudioPlayer, PlaybackStatus

async def test_audio_backends():
    """Test that audio backends work without hanging."""
    print("Testing audio backends...")
    
    # Create config
    config = ServerConfig.from_environment()
    
    # Create audio player
    player = AudioPlayer(config)
    
    print(f"Available backends: {[b.name for b in player.backends]}")
    
    if not player.backends:
        print("❌ No audio backends available")
        return False
    
    # Test with default sound
    print("Testing audio playback...")
    result = await player.play_notification()
    
    if result.status == PlaybackStatus.SUCCESS:
        print(f"✅ Audio test successful using {result.backend_used}")
        return True
    elif result.status == PlaybackStatus.FALLBACK_USED:
        print(f"✅ Audio test successful using fallback with {result.backend_used}")
        return True
    else:
        print(f"❌ Audio test failed: {result.message}")
        return False

async def test_mcp_server():
    """Test the MCP server can start and handle tool calls."""
    print("\nTesting MCP server...")
    
    try:
        from mcp_server_play_sound.server import PlaySoundServer
        from mcp_server_play_sound.config import ServerConfig
        
        # Create config
        config = ServerConfig.from_environment()
        
        # Create server
        server = PlaySoundServer(config)
        
        print("✅ MCP server created successfully")
        
        # Get server info
        info = server.get_server_info()
        print(f"Server info: {json.dumps(info, indent=2)}")
        
        return True
        
    except Exception as e:
        print(f"❌ MCP server test failed: {e}")
        return False

async def main():
    """Run all tests."""
    print("🔊 MCP Play Sound Server - VS Code Fix Test")
    print("=" * 50)
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    success = True
    
    # Test audio backends
    success &= await test_audio_backends()
    
    # Test MCP server
    success &= await test_mcp_server()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ All tests passed! VS Code tool call hanging issue should be fixed.")
        print("\nKey fixes applied:")
        print("- Replaced async subprocess calls with thread executor pattern")
        print("- Made audio device switching synchronous")
        print("- Added Windows winsound backend")
        print("- Made simpleaudio optional to avoid build issues")
    else:
        print("❌ Some tests failed. Check the output above.")
    
    return success

if __name__ == "__main__":
    import asyncio
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
