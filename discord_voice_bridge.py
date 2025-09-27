#!/usr/bin/env python3
"""
Discord Voice Bridge
Python integration with the JavaScript Discord voice helper
This bridges the gap between Python Discord.py and JavaScript voice connections
"""

import subprocess
import json
import os
import time
import asyncio
import logging
from typing import Optional, Dict, Any, Tuple
import threading
import queue

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DiscordVoiceBridge:
    """Bridge between Python and JavaScript Discord voice helper"""
    
    def __init__(self, bot_token: str, node_path: str = "node"):
        self.bot_token = bot_token
        self.node_path = node_path
        self.helper_process = None
        self.is_running = False
        self.connection_status = {
            'is_connected': False,
            'guild_id': None,
            'channel_id': None,
            'connection_status': 'Disconnected',
            'keep_alive_active': False
        }
        self.status_queue = queue.Queue()
        self.command_queue = queue.Queue()
        self.response_queue = queue.Queue()
        
    async def start_helper(self) -> bool:
        """Start the JavaScript Discord voice helper"""
        try:
            if self.is_running:
                logger.warning("Voice helper already running")
                return True
            
            # Set environment variable for bot token
            env = os.environ.copy()
            env['DISCORD_BOT_TOKEN'] = self.bot_token
            
            # Start the Node.js helper process
            self.helper_process = subprocess.Popen(
                [self.node_path, 'discord_voice_helper.js'],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Start monitoring thread
            self.monitor_thread = threading.Thread(target=self._monitor_helper, daemon=True)
            self.monitor_thread.start()
            
            # Wait for helper to start
            await asyncio.sleep(3)
            
            if self.helper_process.poll() is None:
                self.is_running = True
                logger.info("✅ Discord voice helper started")
                return True
            else:
                logger.error("❌ Failed to start Discord voice helper")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error starting voice helper: {e}")
            return False
    
    def _monitor_helper(self):
        """Monitor the helper process output"""
        while self.is_running and self.helper_process:
            try:
                # Read output from helper
                if self.helper_process.stdout:
                    line = self.helper_process.stdout.readline()
                    if line:
                        logger.info(f"Voice Helper: {line.strip()}")
                        
                        # Parse status updates
                        if "Voice Connection Status:" in line:
                            self._parse_status_update(line)
                
                # Check for errors
                if self.helper_process.stderr:
                    error_line = self.helper_process.stderr.readline()
                    if error_line:
                        logger.error(f"Voice Helper Error: {error_line.strip()}")
                
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error monitoring voice helper: {e}")
                break
    
    def _parse_status_update(self, line: str):
        """Parse status updates from the helper"""
        try:
            # Look for JSON status in the output
            if "{" in line and "}" in line:
                json_start = line.find("{")
                json_end = line.rfind("}") + 1
                json_str = line[json_start:json_end]
                status = json.loads(json_str)
                self.connection_status.update(status)
        except Exception as e:
            logger.warning(f"Could not parse status update: {e}")
    
    async def stop_helper(self):
        """Stop the JavaScript Discord voice helper"""
        try:
            if self.helper_process:
                self.is_running = False
                self.helper_process.terminate()
                self.helper_process.wait(timeout=5)
                self.helper_process = None
                logger.info("🛑 Discord voice helper stopped")
        except Exception as e:
            logger.error(f"Error stopping voice helper: {e}")
    
    async def connect_to_voice(self, guild_id: str, channel_id: str) -> bool:
        """Connect to a Discord voice channel"""
        try:
            if not self.is_running:
                logger.error("Voice helper not running")
                return False
            
            # Send connect command to helper
            command = f"connect {guild_id} {channel_id}\n"
            self.helper_process.stdin.write(command)
            self.helper_process.stdin.flush()
            
            # Wait for connection
            await asyncio.sleep(5)
            
            # Check connection status
            status = self.get_connection_status()
            return status['is_connected']
            
        except Exception as e:
            logger.error(f"Error connecting to voice channel: {e}")
            return False
    
    async def disconnect_from_voice(self) -> bool:
        """Disconnect from the current voice channel"""
        try:
            if not self.is_running:
                return False
            
            # Send disconnect command to helper
            command = "disconnect\n"
            self.helper_process.stdin.write(command)
            self.helper_process.stdin.flush()
            
            # Wait for disconnection
            await asyncio.sleep(2)
            
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting from voice channel: {e}")
            return False
    
    async def play_audio(self, audio_path: str) -> bool:
        """Play audio in the voice channel"""
        try:
            if not self.is_running:
                logger.error("Voice helper not running")
                return False
            
            if not os.path.exists(audio_path):
                logger.error(f"Audio file not found: {audio_path}")
                return False
            
            # Send play command to helper
            command = f"play {audio_path}\n"
            self.helper_process.stdin.write(command)
            self.helper_process.stdin.flush()
            
            return True
            
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
            return False
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get current connection status"""
        return self.connection_status.copy()
    
    async def reconnect(self) -> bool:
        """Reconnect to the voice channel"""
        try:
            if not self.is_running:
                return False
            
            # Send reconnect command to helper
            command = "reconnect\n"
            self.helper_process.stdin.write(command)
            self.helper_process.stdin.flush()
            
            # Wait for reconnection
            await asyncio.sleep(5)
            
            return True
            
        except Exception as e:
            logger.error(f"Error reconnecting: {e}")
            return False

# Global bridge instance
voice_bridge = None

async def start_voice_bridge(bot_token: str, node_path: str = "node") -> bool:
    """Start the Discord voice bridge"""
    global voice_bridge
    
    if voice_bridge and voice_bridge.is_running:
        logger.warning("Voice bridge already running")
        return True
    
    voice_bridge = DiscordVoiceBridge(bot_token, node_path)
    return await voice_bridge.start_helper()

async def stop_voice_bridge():
    """Stop the Discord voice bridge"""
    global voice_bridge
    
    if voice_bridge:
        await voice_bridge.stop_helper()
        voice_bridge = None

async def connect_to_voice_channel(guild_id: str, channel_id: str) -> bool:
    """Connect to a Discord voice channel"""
    global voice_bridge
    
    if not voice_bridge:
        logger.error("Voice bridge not started")
        return False
    
    return await voice_bridge.connect_to_voice(guild_id, channel_id)

async def disconnect_from_voice_channel() -> bool:
    """Disconnect from the current voice channel"""
    global voice_bridge
    
    if not voice_bridge:
        return False
    
    return await voice_bridge.disconnect_from_voice()

async def play_audio_in_voice(audio_path: str) -> bool:
    """Play audio in the voice channel"""
    global voice_bridge
    
    if not voice_bridge:
        logger.error("Voice bridge not started")
        return False
    
    return await voice_bridge.play_audio(audio_path)

def get_voice_connection_status() -> Dict[str, Any]:
    """Get current voice connection status"""
    global voice_bridge
    
    if not voice_bridge:
        return {'is_connected': False, 'error': 'Voice bridge not started'}
    
    return voice_bridge.get_connection_status()

# Test function
async def test_voice_bridge():
    """Test the voice bridge functionality"""
    print("🎤 Testing Discord Voice Bridge")
    print("=" * 50)
    
    # You'll need to set your bot token
    bot_token = os.getenv('DISCORD_BOT_TOKEN')
    if not bot_token:
        print("❌ DISCORD_BOT_TOKEN environment variable not set")
        return
    
    # Start the bridge
    success = await start_voice_bridge(bot_token)
    if not success:
        print("❌ Failed to start voice bridge")
        return
    
    print("✅ Voice bridge started")
    
    # Test connection (you'll need to provide actual guild and channel IDs)
    # guild_id = "YOUR_GUILD_ID"
    # channel_id = "YOUR_CHANNEL_ID"
    # 
    # print(f"🔗 Connecting to voice channel {channel_id}...")
    # success = await connect_to_voice_channel(guild_id, channel_id)
    # if success:
    #     print("✅ Connected to voice channel")
    # else:
    #     print("❌ Failed to connect to voice channel")
    
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping voice bridge...")
        await stop_voice_bridge()

if __name__ == "__main__":
    asyncio.run(test_voice_bridge())
