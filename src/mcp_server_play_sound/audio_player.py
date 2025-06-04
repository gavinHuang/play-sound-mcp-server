"""
Audio playback functionality for the MCP Play Sound Server.

This module provides audio playback capabilities with multiple backend support,
fallback mechanisms, and comprehensive error handling.
"""

import logging
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, Union
import asyncio
import concurrent.futures

logger = logging.getLogger(__name__)


class PlaybackStatus(Enum):
    """Status of audio playback operation."""
    SUCCESS = "success"
    FAILED = "failed"
    FALLBACK_USED = "fallback_used"
    TIMEOUT = "timeout"
    FILE_NOT_FOUND = "file_not_found"
    UNSUPPORTED_FORMAT = "unsupported_format"


@dataclass
class PlaybackResult:
    """Result of an audio playback operation."""
    status: PlaybackStatus
    message: str
    duration_ms: Optional[int] = None
    backend_used: Optional[str] = None
    fallback_used: bool = False


class AudioBackend:
    """Base class for audio backends."""
    
    def __init__(self, name: str):
        self.name = name
    
    async def play(self, file_path: Path, volume: float = 1.0, timeout: int = 30) -> PlaybackResult:
        """Play audio file asynchronously."""
        raise NotImplementedError
    
    def is_available(self) -> bool:
        """Check if this backend is available on the current system."""
        raise NotImplementedError


class AFPlayBackend(AudioBackend):
    """macOS afplay backend for audio playback."""
    
    def __init__(self):
        super().__init__("afplay")
    
    def is_available(self) -> bool:
        """Check if afplay is available (macOS only)."""
        if sys.platform != "darwin":
            return False
        
        try:
            result = subprocess.run(
                ["which", "afplay"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    async def play(self, file_path: Path, volume: float = 1.0, timeout: int = 30) -> PlaybackResult:
        """Play audio using afplay."""
        if not file_path.exists():
            return PlaybackResult(
                status=PlaybackStatus.FILE_NOT_FOUND,
                message=f"Audio file not found: {file_path}",
                backend_used=self.name
            )
        
        try:
            # Build afplay command with volume control
            cmd = ["afplay"]
            if volume != 1.0:
                cmd.extend(["-v", str(volume)])
            cmd.append(str(file_path))
            
            logger.debug(f"Executing afplay command: {' '.join(cmd)}")
            
            # Run afplay asynchronously with timeout
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return PlaybackResult(
                    status=PlaybackStatus.TIMEOUT,
                    message=f"Audio playback timed out after {timeout} seconds",
                    backend_used=self.name
                )
            
            if process.returncode == 0:
                return PlaybackResult(
                    status=PlaybackStatus.SUCCESS,
                    message="Audio played successfully",
                    backend_used=self.name
                )
            else:
                error_msg = stderr.decode() if stderr else "Unknown afplay error"
                return PlaybackResult(
                    status=PlaybackStatus.FAILED,
                    message=f"afplay failed: {error_msg}",
                    backend_used=self.name
                )
                
        except Exception as e:
            logger.error(f"Error playing audio with afplay: {e}")
            return PlaybackResult(
                status=PlaybackStatus.FAILED,
                message=f"afplay error: {str(e)}",
                backend_used=self.name
            )


class SimpleAudioBackend(AudioBackend):
    """SimpleAudio backend for cross-platform audio playback."""
    
    def __init__(self):
        super().__init__("simpleaudio")
        self._simpleaudio = None
    
    def is_available(self) -> bool:
        """Check if simpleaudio is available."""
        try:
            import simpleaudio
            self._simpleaudio = simpleaudio
            return True
        except ImportError:
            return False
    
    async def play(self, file_path: Path, volume: float = 1.0, timeout: int = 30) -> PlaybackResult:
        """Play audio using simpleaudio."""
        if not self._simpleaudio:
            if not self.is_available():
                return PlaybackResult(
                    status=PlaybackStatus.FAILED,
                    message="simpleaudio not available",
                    backend_used=self.name
                )
        
        if not file_path.exists():
            return PlaybackResult(
                status=PlaybackStatus.FILE_NOT_FOUND,
                message=f"Audio file not found: {file_path}",
                backend_used=self.name
            )
        
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                result = await asyncio.wait_for(
                    loop.run_in_executor(executor, self._play_sync, file_path, volume),
                    timeout=timeout
                )
            return result
            
        except asyncio.TimeoutError:
            return PlaybackResult(
                status=PlaybackStatus.TIMEOUT,
                message=f"Audio playback timed out after {timeout} seconds",
                backend_used=self.name
            )
        except Exception as e:
            logger.error(f"Error playing audio with simpleaudio: {e}")
            return PlaybackResult(
                status=PlaybackStatus.FAILED,
                message=f"simpleaudio error: {str(e)}",
                backend_used=self.name
            )
    
    def _play_sync(self, file_path: Path, volume: float) -> PlaybackResult:
        """Synchronous audio playback for thread execution."""
        try:
            # Load and play WAV file
            wave_obj = self._simpleaudio.WaveObject.from_wave_file(str(file_path))
            play_obj = wave_obj.play()
            play_obj.wait_done()
            
            return PlaybackResult(
                status=PlaybackStatus.SUCCESS,
                message="Audio played successfully",
                backend_used=self.name
            )
        except Exception as e:
            return PlaybackResult(
                status=PlaybackStatus.FAILED,
                message=f"simpleaudio playback error: {str(e)}",
                backend_used=self.name
            )


class AudioPlayer:
    """Main audio player with multiple backend support and fallback."""
    
    def __init__(self, config):
        """Initialize audio player with configuration."""
        self.config = config
        self.backends = []
        self._setup_backends()
        self._default_sound_path = self._get_default_sound_path()
        
        logger.info(f"AudioPlayer initialized with {len(self.backends)} available backends")
    
    def _setup_backends(self) -> None:
        """Set up available audio backends based on configuration and platform."""
        # Always try AFPlay first on macOS (most reliable)
        afplay = AFPlayBackend()
        if afplay.is_available():
            self.backends.append(afplay)
            logger.debug("AFPlay backend available")
        
        # Add SimpleAudio as fallback
        simpleaudio = SimpleAudioBackend()
        if simpleaudio.is_available():
            self.backends.append(simpleaudio)
            logger.debug("SimpleAudio backend available")
        
        if not self.backends:
            logger.warning("No audio backends available!")
    
    def _get_default_sound_path(self) -> Path:
        """Get path to default notification sound."""
        # Default sound should be bundled with the package
        package_dir = Path(__file__).parent
        default_sound = package_dir / "assets" / "notification.wav"
        
        if not default_sound.exists():
            logger.warning(f"Default sound file not found: {default_sound}")
        
        return default_sound
    
    async def play_notification(self, custom_path: Optional[str] = None) -> PlaybackResult:
        """
        Play notification sound with fallback support.
        
        Args:
            custom_path: Optional path to custom audio file
            
        Returns:
            PlaybackResult with status and details
        """
        # Determine which file to play
        if custom_path and self.config.custom_sound_path:
            audio_path = Path(self.config.custom_sound_path)
            use_custom = True
        elif custom_path:
            audio_path = Path(custom_path)
            use_custom = True
        else:
            audio_path = self._default_sound_path
            use_custom = False
        
        logger.info(f"Playing audio: {audio_path} (custom={use_custom})")
        
        # Try to play the requested file
        result = await self._play_with_backends(audio_path)
        
        # If custom file failed and fallback is enabled, try default
        if (result.status != PlaybackStatus.SUCCESS and 
            use_custom and 
            self.config.enable_fallback and 
            audio_path != self._default_sound_path):
            
            logger.info("Custom audio failed, trying default fallback")
            fallback_result = await self._play_with_backends(self._default_sound_path)
            
            if fallback_result.status == PlaybackStatus.SUCCESS:
                fallback_result.fallback_used = True
                fallback_result.status = PlaybackStatus.FALLBACK_USED
                fallback_result.message = f"Custom audio failed, used fallback: {result.message}"
                return fallback_result
        
        return result
    
    async def _play_with_backends(self, file_path: Path) -> PlaybackResult:
        """Try to play audio file with available backends."""
        if not self.backends:
            return PlaybackResult(
                status=PlaybackStatus.FAILED,
                message="No audio backends available"
            )
        
        last_result = None
        for backend in self.backends:
            logger.debug(f"Trying backend: {backend.name}")
            result = await backend.play(
                file_path, 
                volume=self.config.volume_level,
                timeout=self.config.playback_timeout_seconds
            )
            
            if result.status == PlaybackStatus.SUCCESS:
                return result
            
            last_result = result
            logger.debug(f"Backend {backend.name} failed: {result.message}")
        
        # All backends failed
        return last_result or PlaybackResult(
            status=PlaybackStatus.FAILED,
            message="All audio backends failed"
        )
