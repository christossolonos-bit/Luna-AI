#!/usr/bin/env python3
"""
Luna Voice Chat Integration
Connects voice transcription with Luna's AI system and Discord
"""

import asyncio
import json
import os
import time
import logging
from datetime import datetime
from typing import Optional, Dict, Any, Callable
import threading

# Import our modules
from voice_chat_transcriber import start_voice_transcriber, stop_voice_transcriber, get_transcriber_stats
from luna_discord import get_discord_bot, send_to_discord_channel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LunaVoiceChatIntegration:
    """Integrates voice chat transcription with Luna's AI system"""
    
    def __init__(self, config_file: str = "voice_chat_integration_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        
        # State management
        self.is_running = False
        self.luna_ai_callback = None
        self.discord_bot = None
        
        # Response management
        self.last_response_time = 0
        self.response_cooldown = self.config.get('response_cooldown', 3.0)
        self.max_response_length = self.config.get('max_response_length', 500)
        
        # Statistics
        self.stats = {
            'total_transcriptions': 0,
            'total_responses': 0,
            'start_time': None,
            'last_activity': None
        }
    
    def load_config(self) -> Dict[str, Any]:
        """Load integration configuration"""
        default_config = {
            'enabled': True,
            'response_cooldown': 3.0,
            'max_response_length': 500,
            'auto_respond': True,
            'use_discord_tts': True,
            'discord_channel_id': None,
            'luna_ai_enabled': True,
            'voice_activity_threshold': 0.5,
            'response_delay': 1.0,
            'debug_mode': False
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                logger.error(f"Error loading integration config: {e}")
        
        return default_config
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """Save integration configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            self.config = config
            return True
        except Exception as e:
            logger.error(f"Error saving integration config: {e}")
            return False
    
    def set_luna_ai_callback(self, callback: Callable[[str, str, str], str]):
        """Set Luna AI callback function"""
        self.luna_ai_callback = callback
    
    def set_discord_bot(self, bot):
        """Set Discord bot instance"""
        self.discord_bot = bot
    
    async def start_integration(self) -> bool:
        """Start the voice chat integration"""
        if self.is_running:
            logger.warning("Voice chat integration already running")
            return True
        
        if not self.config.get('enabled', True):
            logger.info("Voice chat integration disabled in config")
            return False
        
        try:
            # Start voice transcriber
            logger.info("🎤 Starting voice chat integration...")
            
            success = start_voice_transcriber(
                transcription_callback=self._on_transcription,
                error_callback=self._on_error
            )
            
            if not success:
                logger.error("Failed to start voice transcriber")
                return False
            
            self.is_running = True
            self.stats['start_time'] = time.time()
            
            logger.info("✅ Voice chat integration started")
            return True
            
        except Exception as e:
            logger.error(f"Error starting voice chat integration: {e}")
            return False
    
    async def stop_integration(self):
        """Stop the voice chat integration"""
        if not self.is_running:
            return
        
        logger.info("🛑 Stopping voice chat integration...")
        
        stop_voice_transcriber()
        self.is_running = False
        
        logger.info("✅ Voice chat integration stopped")
    
    def _on_transcription(self, text: str):
        """Handle transcription results"""
        try:
            if not text.strip():
                return
            
            logger.info(f"📝 Voice transcription: {text}")
            self.stats['total_transcriptions'] += 1
            self.stats['last_activity'] = time.time()
            
            # Check cooldown
            current_time = time.time()
            if current_time - self.last_response_time < self.response_cooldown:
                logger.debug("Response on cooldown, skipping")
                return
            
            # Process with Luna AI
            asyncio.create_task(self._process_with_luna(text))
            
        except Exception as e:
            logger.error(f"Error handling transcription: {e}")
    
    def _on_error(self, error: str):
        """Handle errors"""
        logger.error(f"Voice transcriber error: {error}")
    
    async def _process_with_luna(self, text: str):
        """Process transcription with Luna AI"""
        try:
            if not self.config.get('luna_ai_enabled', True):
                logger.debug("Luna AI disabled, skipping processing")
                return
            
            if not self.luna_ai_callback:
                logger.warning("No Luna AI callback set")
                return
            
            # Prepare context for Luna
            voice_context = f"This is a voice message from Discord voice chat. The user said: {text}"
            
            # Get Luna's response
            logger.info("🤖 Getting Luna's response...")
            
            # Call Luna AI (assuming it's async)
            if asyncio.iscoroutinefunction(self.luna_ai_callback):
                response = await self.luna_ai_callback(voice_context, "Voice Chat User", "voice_chat")
            else:
                response = self.luna_ai_callback(voice_context, "Voice Chat User", "voice_chat")
            
            if response and response.strip():
                # Limit response length
                if len(response) > self.max_response_length:
                    response = response[:self.max_response_length-3] + "..."
                
                logger.info(f"🤖 Luna's response: {response}")
                self.stats['total_responses'] += 1
                self.last_response_time = time.time()
                
                # Send to Discord
                await self._send_to_discord(response)
                
                # Play TTS in voice channel if available
                if self.config.get('use_discord_tts', True):
                    await self._play_voice_tts(response)
            else:
                logger.debug("No response from Luna AI")
                
        except Exception as e:
            logger.error(f"Error processing with Luna: {e}")
    
    async def _send_to_discord(self, response: str):
        """Send response to Discord"""
        try:
            if not self.config.get('discord_channel_id'):
                logger.debug("No Discord channel configured")
                return
            
            channel_id = self.config['discord_channel_id']
            
            # Add voice chat indicator
            message = f"🎤 **Voice Chat Response:** {response}"
            
            # Send to Discord
            if self.discord_bot:
                success = await send_to_discord_channel(channel_id, message)
                if success:
                    logger.info("✅ Sent response to Discord")
                else:
                    logger.warning("Failed to send response to Discord")
            else:
                logger.warning("Discord bot not available")
                
        except Exception as e:
            logger.error(f"Error sending to Discord: {e}")
    
    async def _play_voice_tts(self, text: str):
        """Play TTS in Discord voice channel"""
        try:
            if not self.discord_bot:
                logger.debug("Discord bot not available for TTS")
                return
            
            # Get Discord bot instance
            from luna_discord import get_discord_bot
            discord_bot = get_discord_bot()
            
            if discord_bot and hasattr(discord_bot, 'play_tts_in_voice'):
                success = await discord_bot.play_tts_in_voice(text)
                if success:
                    logger.info("✅ Played TTS in voice channel")
                else:
                    logger.debug("Failed to play TTS in voice channel")
            else:
                logger.debug("TTS not available")
                
        except Exception as e:
            logger.error(f"Error playing voice TTS: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get integration statistics"""
        transcriber_stats = get_transcriber_stats()
        uptime = time.time() - (self.stats['start_time'] or time.time())
        
        return {
            'is_running': self.is_running,
            'total_transcriptions': self.stats['total_transcriptions'],
            'total_responses': self.stats['total_responses'],
            'uptime_seconds': uptime,
            'last_activity': self.stats['last_activity'],
            'transcriber_stats': transcriber_stats,
            'config': self.config
        }
    
    def update_config(self, new_config: Dict[str, Any]) -> bool:
        """Update configuration"""
        try:
            # Merge with existing config
            updated_config = {**self.config, **new_config}
            return self.save_config(updated_config)
        except Exception as e:
            logger.error(f"Error updating config: {e}")
            return False

# Global integration instance
voice_chat_integration = LunaVoiceChatIntegration()

async def start_luna_voice_chat(luna_ai_callback: Callable[[str, str, str], str] = None,
                               discord_bot = None) -> bool:
    """Start Luna voice chat integration"""
    if luna_ai_callback:
        voice_chat_integration.set_luna_ai_callback(luna_ai_callback)
    if discord_bot:
        voice_chat_integration.set_discord_bot(discord_bot)
    
    return await voice_chat_integration.start_integration()

async def stop_luna_voice_chat():
    """Stop Luna voice chat integration"""
    await voice_chat_integration.stop_integration()

def get_voice_chat_stats() -> Dict[str, Any]:
    """Get voice chat statistics"""
    return voice_chat_integration.get_stats()

def update_voice_chat_config(config: Dict[str, Any]) -> bool:
    """Update voice chat configuration"""
    return voice_chat_integration.update_config(config)

# Test function
async def test_voice_chat_integration():
    """Test the voice chat integration"""
    print("🎤 Testing Luna Voice Chat Integration")
    print("=" * 50)
    
    # Mock Luna AI callback
    def mock_luna_ai(text: str, user: str, source: str) -> str:
        return f"Luna heard: {text} (from {user} via {source})"
    
    # Start integration
    success = await start_luna_voice_chat(mock_luna_ai)
    
    if success:
        print("✅ Voice chat integration started")
        print("Speak into your microphone...")
        
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping integration...")
            await stop_luna_voice_chat()
    else:
        print("❌ Failed to start voice chat integration")

if __name__ == "__main__":
    asyncio.run(test_voice_chat_integration())
