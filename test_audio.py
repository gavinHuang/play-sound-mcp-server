#!/usr/bin/env python3
"""
Quick test script to verify audio functionality works.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_server_play_sound.config import ServerConfig
from mcp_server_play_sound.audio_player import AudioPlayer


async def test_audio():
    """Test audio playback functionality."""
    print("🎵 Testing MCP Play Sound Server Audio Functionality")
    print("=" * 50)
    
    # Create configuration
    config = ServerConfig.from_environment()
    print(f"✅ Configuration loaded: volume={config.volume_level}, fallback={config.enable_fallback}")
    
    # Create audio player
    player = AudioPlayer(config)
    print(f"✅ AudioPlayer created with {len(player.backends)} backends:")
    for backend in player.backends:
        print(f"   - {backend.name}")
    
    # Test default sound
    print("\n🔊 Testing default notification sound...")
    result = await player.play_notification()
    
    if result.status.value == "success":
        print(f"✅ Audio played successfully using {result.backend_used}")
    elif result.status.value == "fallback_used":
        print(f"⚠️  Used fallback audio with {result.backend_used}: {result.message}")
    else:
        print(f"❌ Audio playback failed: {result.message}")
        return False
    
    print("\n🎉 Audio test completed successfully!")
    return True


if __name__ == "__main__":
    success = asyncio.run(test_audio())
    sys.exit(0 if success else 1)
