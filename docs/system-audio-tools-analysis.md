# System Audio Tools Analysis

## Overview

This document provides an in-depth analysis of system command-line audio tools that could be used as the foundation for cross-platform audio playback in the MCP Play Sound Server.

## Platform-Specific Audio Tools

### macOS Built-in Audio Tools

#### 1. **afplay** (✅ Primary Recommendation)

**Location**: `/usr/bin/afplay`
**Availability**: Built into macOS since 10.5 (Leopard)

**Supported Formats:**
- WAV (uncompressed)
- MP3 (MPEG-1/2 Layer 3)
- AAC (Advanced Audio Coding)
- FLAC (Free Lossless Audio Codec)
- AIFF (Audio Interchange File Format)
- CAF (Core Audio Format)
- M4A (MPEG-4 Audio)

**Command Syntax:**
```bash
afplay [options] audio_file
```

**Key Options:**
- `-v volume` - Set volume (0.0 to 1.0)
- `-t time` - Play for specified duration
- `-r rate` - Set playback rate
- `-q` - Quiet mode (no output)

**Pros:**
- ✅ Always available on macOS
- ✅ Excellent format support
- ✅ Reliable and stable
- ✅ Low latency
- ✅ Volume control
- ✅ No additional installation required

**Cons:**
- ❌ macOS only
- ❌ Limited to basic playback (no effects)

**Example Usage:**
```typescript
// Basic playback
spawn('afplay', ['notification.wav']);

// With volume control (50%)
spawn('afplay', ['-v', '0.5', 'notification.wav']);

// With timeout (5 seconds max)
spawn('afplay', ['-t', '5', 'notification.wav']);
```

#### 2. **say** (Alternative for TTS)

**Location**: `/usr/bin/say`
**Purpose**: Text-to-speech synthesis

**Usage for Notifications:**
```bash
say "Task completed successfully"
say -v "Alex" "Build finished"
```

**Pros:**
- ✅ Built-in to macOS
- ✅ No audio files needed
- ✅ Multiple voice options

**Cons:**
- ❌ Text-to-speech only
- ❌ Less professional than audio files
- ❌ Language/accent limitations

### Windows Audio Tools

#### 1. **PowerShell Media.SoundPlayer** (✅ Recommended)

**Availability**: Windows PowerShell (built-in since Windows 7)

**Command Syntax:**
```powershell
(New-Object Media.SoundPlayer "file.wav").PlaySync()
```

**Supported Formats:**
- WAV (primary support)
- Limited other formats

**Pros:**
- ✅ Built into Windows
- ✅ Synchronous playback control
- ✅ No additional installation

**Cons:**
- ❌ Limited format support (mainly WAV)
- ❌ PowerShell startup overhead
- ❌ No volume control

**Implementation:**
```typescript
function playOnWindows(filePath: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const command = `(New-Object Media.SoundPlayer "${filePath}").PlaySync()`;
    const process = spawn('powershell', ['-Command', command]);
    
    process.on('close', (code) => {
      if (code === 0) resolve();
      else reject(new Error(`PowerShell audio failed: ${code}`));
    });
  });
}
```

#### 2. **Windows Media Player CLI** (❌ Not Recommended)

**Issues:**
- Inconsistent availability
- Complex command-line interface
- Reliability problems
- May open GUI windows

#### 3. **cmdmp3** (⚠️ Third-party Option)

**Description**: Lightweight command-line MP3 player
**Size**: ~500KB
**License**: Freeware

**Pros:**
- ✅ Small size
- ✅ MP3 support
- ✅ Command-line interface

**Cons:**
- ❌ Third-party dependency
- ❌ Limited format support
- ❌ Distribution licensing concerns

### Linux Audio Tools

#### 1. **play (SoX)** (✅ Primary Recommendation)

**Package**: `sox`
**Installation**: 
```bash
# Ubuntu/Debian
sudo apt-get install sox

# CentOS/RHEL
sudo yum install sox

# Arch Linux
sudo pacman -S sox
```

**Supported Formats:**
- WAV, FLAC, OGG, MP3 (with plugins)
- Raw audio formats
- Many others via plugins

**Command Syntax:**
```bash
play [options] input_file
```

**Key Options:**
- `-v volume` - Set volume
- `-t type` - Specify file type
- `-q` - Quiet mode
- `trim start duration` - Play portion of file

**Pros:**
- ✅ Excellent format support
- ✅ Audio processing capabilities
- ✅ Widely available
- ✅ Volume and effect controls

**Cons:**
- ❌ Requires installation
- ❌ May not be available by default

**Example Usage:**
```bash
# Basic playback
play notification.wav

# With volume control
play -v 0.5 notification.wav

# Quiet mode
play -q notification.wav
```

#### 2. **aplay (ALSA)** (✅ Fallback Option)

**Package**: `alsa-utils`
**Availability**: Most Linux distributions

**Supported Formats:**
- WAV (primary)
- Raw audio formats

**Command Syntax:**
```bash
aplay [options] file.wav
```

**Pros:**
- ✅ Widely available
- ✅ Reliable for WAV files
- ✅ Part of standard audio stack

**Cons:**
- ❌ Limited format support
- ❌ WAV files only

#### 3. **paplay (PulseAudio)** (✅ Alternative)

**Package**: `pulseaudio-utils`
**Availability**: PulseAudio systems

**Supported Formats:**
- WAV, FLAC, OGG
- Various raw formats

**Command Syntax:**
```bash
paplay file.wav
```

**Pros:**
- ✅ Good format support
- ✅ Integrates with PulseAudio
- ✅ Modern Linux audio

**Cons:**
- ❌ PulseAudio dependency
- ❌ Not universal

#### 4. **mpg123** (MP3 Specialist)

**Package**: `mpg123`
**Purpose**: MP3 playback

**Command Syntax:**
```bash
mpg123 file.mp3
```

**Pros:**
- ✅ Excellent MP3 support
- ✅ Lightweight
- ✅ Fast

**Cons:**
- ❌ MP3 only
- ❌ Additional dependency

## Cross-Platform Detection Strategy

### Tool Detection Algorithm

```typescript
interface AudioTool {
  command: string;
  args: string[];
  formats: string[];
  platform: string;
}

class SystemAudioDetector {
  private static tools: AudioTool[] = [
    // macOS
    { command: 'afplay', args: [], formats: ['wav', 'mp3', 'flac', 'aac'], platform: 'darwin' },
    
    // Windows
    { command: 'powershell', args: ['-Command'], formats: ['wav'], platform: 'win32' },
    
    // Linux
    { command: 'play', args: [], formats: ['wav', 'mp3', 'flac', 'ogg'], platform: 'linux' },
    { command: 'aplay', args: [], formats: ['wav'], platform: 'linux' },
    { command: 'paplay', args: [], formats: ['wav', 'flac', 'ogg'], platform: 'linux' },
    { command: 'mpg123', args: [], formats: ['mp3'], platform: 'linux' },
  ];

  static async detectAvailableTools(): Promise<AudioTool[]> {
    const currentPlatform = process.platform;
    const platformTools = this.tools.filter(tool => 
      tool.platform === currentPlatform || tool.platform === 'all'
    );

    const availableTools: AudioTool[] = [];
    
    for (const tool of platformTools) {
      if (await this.isCommandAvailable(tool.command)) {
        availableTools.push(tool);
      }
    }

    return availableTools;
  }

  private static async isCommandAvailable(command: string): Promise<boolean> {
    try {
      await new Promise((resolve, reject) => {
        const process = spawn(command, ['--version'], { stdio: 'ignore' });
        process.on('close', (code) => {
          // Many audio tools return non-zero for --version, so we just check if they exist
          resolve(undefined);
        });
        process.on('error', reject);
      });
      return true;
    } catch {
      return false;
    }
  }
}
```

### Format-Specific Tool Selection

```typescript
class AudioToolSelector {
  private availableTools: AudioTool[];

  constructor(availableTools: AudioTool[]) {
    this.availableTools = availableTools;
  }

  selectBestTool(filePath: string): AudioTool | null {
    const extension = path.extname(filePath).toLowerCase().slice(1);
    
    // Find tools that support this format
    const compatibleTools = this.availableTools.filter(tool =>
      tool.formats.includes(extension)
    );

    if (compatibleTools.length === 0) {
      return null;
    }

    // Prioritize tools by preference
    const toolPriority = ['afplay', 'play', 'aplay', 'paplay', 'powershell'];
    
    for (const preferredTool of toolPriority) {
      const tool = compatibleTools.find(t => t.command === preferredTool);
      if (tool) {
        return tool;
      }
    }

    // Return first available if no preferred tool found
    return compatibleTools[0];
  }
}
```

## Error Handling and Reliability

### Common Issues and Solutions

#### 1. **Command Not Found**

**Problem**: Audio tool not installed or not in PATH
**Solution**: Graceful fallback to alternative tools

```typescript
async function playWithFallback(filePath: string): Promise<void> {
  const tools = await SystemAudioDetector.detectAvailableTools();
  const selector = new AudioToolSelector(tools);
  
  const tool = selector.selectBestTool(filePath);
  if (!tool) {
    throw new Error(`No compatible audio tool found for ${filePath}`);
  }

  try {
    await this.executeAudioTool(tool, filePath);
  } catch (error) {
    // Try fallback tools
    const fallbackTools = tools.filter(t => t !== tool);
    for (const fallbackTool of fallbackTools) {
      try {
        await this.executeAudioTool(fallbackTool, filePath);
        return; // Success with fallback
      } catch {
        continue; // Try next fallback
      }
    }
    throw new Error(`All audio tools failed: ${error.message}`);
  }
}
```

#### 2. **Audio Device Unavailable**

**Problem**: No audio output device available
**Detection**: Check for audio device before playback

```typescript
async function checkAudioDevice(): Promise<boolean> {
  try {
    // Platform-specific audio device detection
    switch (process.platform) {
      case 'darwin':
        // Check for audio output devices
        const result = await execAsync('system_profiler SPAudioDataType');
        return result.stdout.includes('Output');
      
      case 'linux':
        // Check ALSA devices
        const alsaResult = await execAsync('aplay -l');
        return alsaResult.stdout.includes('card');
      
      case 'win32':
        // Check Windows audio devices
        const winResult = await execAsync('powershell "Get-WmiObject -Class Win32_SoundDevice"');
        return winResult.stdout.length > 0;
      
      default:
        return true; // Assume available
    }
  } catch {
    return false;
  }
}
```

#### 3. **File Format Incompatibility**

**Problem**: Audio tool doesn't support file format
**Solution**: Format conversion or tool selection

```typescript
async function handleFormatIncompatibility(filePath: string): Promise<string> {
  const extension = path.extname(filePath).toLowerCase();
  
  // If not WAV, try to convert to WAV for maximum compatibility
  if (extension !== '.wav') {
    try {
      const wavPath = await convertToWav(filePath);
      return wavPath;
    } catch {
      throw new Error(`Unsupported audio format: ${extension}`);
    }
  }
  
  return filePath;
}
```

## Performance Considerations

### Subprocess Overhead

**Measurement**: Typical subprocess creation overhead
- **macOS**: 10-50ms
- **Windows**: 50-200ms (PowerShell startup)
- **Linux**: 10-30ms

**Optimization Strategies:**

1. **Tool Caching**: Cache detected tools to avoid repeated detection
2. **Process Pooling**: Reuse processes where possible
3. **Async Execution**: Non-blocking audio playback

```typescript
class OptimizedAudioPlayer {
  private toolCache: Map<string, AudioTool> = new Map();
  
  async playSound(filePath: string): Promise<void> {
    const cacheKey = path.extname(filePath);
    
    let tool = this.toolCache.get(cacheKey);
    if (!tool) {
      const tools = await SystemAudioDetector.detectAvailableTools();
      const selector = new AudioToolSelector(tools);
      tool = selector.selectBestTool(filePath);
      
      if (tool) {
        this.toolCache.set(cacheKey, tool);
      }
    }
    
    if (!tool) {
      throw new Error(`No audio tool available for ${filePath}`);
    }
    
    return this.executeAudioTool(tool, filePath);
  }
}
```

## Recommendation Summary

### Primary Strategy: **Multi-Tool Approach**

1. **macOS**: Use `afplay` (always available, excellent support)
2. **Windows**: Use PowerShell Media.SoundPlayer (built-in, WAV support)
3. **Linux**: Detect and use `play` (sox) > `aplay` > `paplay` in order of preference

### Fallback Strategy: **Format Conversion**

- Convert non-WAV files to WAV for maximum compatibility
- Use WAV as the universal fallback format
- Bundle default notification as WAV

### Implementation Priority:

1. ✅ **System tool detection** - Identify available audio tools
2. ✅ **Format-aware selection** - Choose best tool for file format
3. ✅ **Graceful fallback** - Handle tool failures elegantly
4. ✅ **Performance optimization** - Cache tools and minimize overhead

This approach provides robust, cross-platform audio playback while leveraging system capabilities and maintaining reliability.
