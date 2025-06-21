# VS Code MCP Tool Call Fix - Summary

## Problem
The MCP Play Sound Server worked in Claude Desktop but tool calls would hang indefinitely in VS Code due to async subprocess execution patterns that VS Code's MCP client couldn't handle properly.

## Root Cause
VS Code's MCP client had issues with:
1. **Async subprocess execution** (`asyncio.create_subprocess_exec`)
2. **Nested async awaits** in tool call chains
3. **Process communication async patterns** (`process.communicate()`)
4. **Timeout handling** with `asyncio.wait_for` on subprocesses

## Fixes Applied

### 1. Replaced Async Subprocess with Thread Executor Pattern
**Before (problematic):**
```python
# This pattern caused hanging in VS Code
process = await asyncio.create_subprocess_exec(*cmd, ...)
stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
```

**After (fixed):**
```python
# Use thread executor to run subprocess synchronously
loop = asyncio.get_event_loop()
with concurrent.futures.ThreadPoolExecutor() as executor:
    result = await asyncio.wait_for(
        loop.run_in_executor(executor, self._run_afplay_sync, cmd, timeout),
        timeout=timeout + 5
    )
```

### 2. Made Audio Device Switching Synchronous
**Before:**
```python
async def _switch_audio_device(self, device_name: str) -> bool:
    process = await asyncio.create_subprocess_exec(...)
    stdout, stderr = await process.communicate()
```

**After:**
```python
def _switch_audio_device_sync(self, device_name: str) -> bool:
    result = subprocess.run([...], capture_output=True, timeout=10)
```

### 3. Added Windows Audio Backend
Added `WindowsAudioBackend` using `winsound` for Windows compatibility, avoiding the problematic `simpleaudio` dependency that requires Visual C++ build tools.

### 4. Made SimpleAudio Optional
Moved `simpleaudio` to optional dependencies to prevent build failures:
```toml
[project.optional-dependencies]
audio = [
    "simpleaudio>=1.0.4",
]
```

## Files Modified

1. **`src/mcp_server_play_sound/audio_player.py`**:
   - Replaced `AFPlayBackend.play()` async subprocess calls with thread executor
   - Added synchronous helper methods for device switching
   - Updated `get_available_audio_devices()` to use thread executor
   - Added `WindowsAudioBackend` class
   - Improved error handling and logging

2. **`pyproject.toml`**:
   - Made `simpleaudio` optional to avoid Windows build issues

## Key Technical Changes

### Thread Executor Pattern
Instead of direct async subprocess execution, all system calls now use:
```python
loop = asyncio.get_event_loop()
with concurrent.futures.ThreadPoolExecutor() as executor:
    result = await loop.run_in_executor(executor, sync_function, *args)
```

This pattern ensures:
- VS Code's MCP client can properly track async operations
- No hanging on subprocess communication
- Proper timeout handling
- Clean resource management

### Synchronous System Calls
All external tool calls (afplay, SwitchAudioSource, system_profiler) now use:
```python
subprocess.run([...], capture_output=True, timeout=timeout)
```

## Testing
The fix has been verified to:
- ✅ Maintain compatibility with Claude Desktop
- ✅ Resolve hanging issues in VS Code  
- ✅ Provide cross-platform audio support (macOS/Windows)
- ✅ Handle timeouts properly
- ✅ Graceful fallback when backends unavailable

## Usage in VS Code
After applying these fixes, the MCP server should work correctly in VS Code with tool calls completing normally instead of hanging indefinitely.
