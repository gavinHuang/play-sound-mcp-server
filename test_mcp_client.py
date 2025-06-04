#!/usr/bin/env python3
"""
Test the MCP server using the FastMCP client.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from fastmcp import Client
from mcp_server_play_sound.server import PlaySoundServer
from mcp_server_play_sound.config import ServerConfig


async def test_mcp_server():
    """Test the MCP server using in-memory client."""
    print("🧪 Testing MCP Play Sound Server with Client")
    print("=" * 45)
    
    try:
        # Create server
        config = ServerConfig.from_environment()
        config.validate()
        server = PlaySoundServer(config)
        print("✅ Server created successfully")
        
        # Connect with in-memory client
        async with Client(server.app) as client:
            print("✅ Client connected to server")
            
            # List available tools
            tools = await client.list_tools()
            print(f"✅ Available tools: {[tool.name for tool in tools]}")
            
            # Test get_audio_status tool
            print("\n🔍 Testing get_audio_status...")
            status_result = await client.call_tool("get_audio_status", {})
            print(f"✅ Audio status: {status_result.content[0].text}")
            
            # Test play_notification_sound tool
            print("\n🔊 Testing play_notification_sound...")
            play_result = await client.call_tool("play_notification_sound", {
                "message": "Test notification from MCP client!"
            })
            print(f"✅ Play result: {play_result.content[0].text}")
            
            # Test test_audio_playback tool
            print("\n🧪 Testing test_audio_playback...")
            test_result = await client.call_tool("test_audio_playback", {
                "use_custom": False
            })
            print(f"✅ Test result: {test_result.content[0].text}")
            
        print("\n🎉 All MCP tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_mcp_server())
    sys.exit(0 if success else 1)
