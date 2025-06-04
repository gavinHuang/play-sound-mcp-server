"""
MCP Server for Audio Playback Notifications

A Model Context Protocol server that provides audio playback functionality
for agentic coding agents. Enables AI agents to play sound notifications
when coding tasks are completed.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .server import PlaySoundServer
from .config import ServerConfig
from .audio_player import AudioPlayer, PlaybackResult

__all__ = [
    "PlaySoundServer",
    "ServerConfig", 
    "AudioPlayer",
    "PlaybackResult",
]
