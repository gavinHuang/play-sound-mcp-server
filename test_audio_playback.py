#!/usr/bin/env python3
"""
Test script to actually play a sound using the WinSound backend.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add the source directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import audio player components directly
from mcp_server_play_sound.audio_player import WinSoundBackend

async def test_audio_playback():
    """Test actual audio playback with WinSound backend."""
    print(f"Testing WinSound audio playback...\n")
    
    # Initialize backend
    backend = WinSoundBackend()
    
    if not backend.is_available():
        print("❌ WinSound backend not available")
        return False
    
    print("✅ WinSound backend is available")
    
    # Find the notification sound file
    sound_file = Path(__file__).parent / "src" / "mcp_server_play_sound" / "assets" / "notification.wav"
    
    if not sound_file.exists():
        print(f"❌ Sound file not found: {sound_file}")
        return False
    
    print(f"✅ Sound file found: {sound_file}")
    
    # Try to play the sound
    print("🔊 Playing sound...")
    try:
        result = await backend.play(sound_file, volume=0.8, timeout=10)
        
        print(f"Status: {result.status.value}")
        print(f"Message: {result.message}")
        print(f"Backend used: {result.backend_used}")
        
        if result.status.value == "success":
            print("✅ Audio playback successful!")
            return True
        else:
            print("❌ Audio playback failed")
            return False
            
    except Exception as e:
        print(f"❌ Exception during playback: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_audio_playback())
    sys.exit(0 if success else 1)
