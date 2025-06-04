#!/usr/bin/env python3
"""
Generate a default notification sound for the MCP Play Sound Server.

This script creates a simple, pleasant notification tone as a WAV file
that will be bundled with the package as the default sound.
"""

import math
import wave
import struct
from pathlib import Path


def generate_notification_tone(
    filename: str,
    duration: float = 0.5,
    sample_rate: int = 44100,
    frequency1: float = 800.0,
    frequency2: float = 1000.0,
    volume: float = 0.3
) -> None:
    """
    Generate a pleasant two-tone notification sound.
    
    Args:
        filename: Output WAV file path
        duration: Duration in seconds
        sample_rate: Audio sample rate
        frequency1: First tone frequency in Hz
        frequency2: Second tone frequency in Hz  
        volume: Volume level (0.0 to 1.0)
    """
    # Calculate number of samples
    num_samples = int(duration * sample_rate)
    
    # Generate audio data
    audio_data = []
    
    for i in range(num_samples):
        # Time in seconds
        t = i / sample_rate
        
        # Create a pleasant two-tone notification
        # First half: frequency1, second half: frequency2
        if t < duration / 2:
            freq = frequency1
        else:
            freq = frequency2
        
        # Generate sine wave with envelope
        # Apply fade in/out to avoid clicks
        envelope = 1.0
        fade_time = 0.05  # 50ms fade
        
        if t < fade_time:
            envelope = t / fade_time
        elif t > duration - fade_time:
            envelope = (duration - t) / fade_time
        
        # Generate the tone
        sample = volume * envelope * math.sin(2 * math.pi * freq * t)
        
        # Convert to 16-bit integer
        sample_int = int(sample * 32767)
        audio_data.append(sample_int)
    
    # Write WAV file
    with wave.open(filename, 'w') as wav_file:
        # Set parameters: mono, 16-bit, sample_rate
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        
        # Write audio data
        for sample in audio_data:
            wav_file.writeframes(struct.pack('<h', sample))
    
    print(f"Generated notification sound: {filename}")
    print(f"Duration: {duration}s, Sample rate: {sample_rate}Hz")
    print(f"Frequencies: {frequency1}Hz -> {frequency2}Hz")


def main():
    """Generate the default notification sound."""
    # Determine output path
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    output_path = project_root / "src" / "mcp_server_play_sound" / "assets" / "notification.wav"
    
    # Ensure assets directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Generate the notification sound
    generate_notification_tone(
        str(output_path),
        duration=0.6,  # 600ms
        frequency1=800,  # Pleasant mid-range tone
        frequency2=1000,  # Slightly higher second tone
        volume=0.4  # Moderate volume
    )
    
    # Verify file was created
    if output_path.exists():
        file_size = output_path.stat().st_size
        print(f"File created successfully: {output_path}")
        print(f"File size: {file_size} bytes ({file_size/1024:.1f} KB)")
    else:
        print("ERROR: File was not created!")


if __name__ == "__main__":
    main()
