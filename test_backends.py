#!/usr/bin/env python3
"""
Test script to verify audio backends work correctly.
"""

import sys
import os
from pathlib import Path

# Add the source directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import audio player components directly
from mcp_server_play_sound.audio_player import (
    WinSoundBackend, 
    SimpleAudioBackend,
    AFPlayBackend
)

def test_backends():
    """Test all available audio backends."""
    print(f"Python platform: {sys.platform}")
    print(f"Testing audio backends...\n")
    
    # Test WinSound backend
    print("1. Testing WinSound backend:")
    winsound_backend = WinSoundBackend()
    winsound_available = winsound_backend.is_available()
    print(f"   Available: {winsound_available}")
    
    # Test SimpleAudio backend
    print("\n2. Testing SimpleAudio backend:")
    simpleaudio_backend = SimpleAudioBackend()
    simpleaudio_available = simpleaudio_backend.is_available()
    print(f"   Available: {simpleaudio_available}")
    
    # Test AFPlay backend (macOS)
    print("\n3. Testing AFPlay backend:")
    afplay_backend = AFPlayBackend()
    afplay_available = afplay_backend.is_available()
    print(f"   Available: {afplay_available}")
    
    # Summary
    available_backends = []
    if winsound_available:
        available_backends.append("WinSound")
    if simpleaudio_available:
        available_backends.append("SimpleAudio")
    if afplay_available:
        available_backends.append("AFPlay")
    
    print(f"\nSummary:")
    print(f"Available backends: {available_backends}")
    print(f"Total available: {len(available_backends)}")
    
    return len(available_backends) > 0

if __name__ == "__main__":
    success = test_backends()
    sys.exit(0 if success else 1)
