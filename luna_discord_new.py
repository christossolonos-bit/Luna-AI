#!/usr/bin/env python3
"""
Luna Discord Bot - Simplified Voice Connection
No timeouts, no reconnection, no keepalive - just simple voice connection like any Discord bot
"""

import discord
import asyncio
import logging
import json
import os
import queue
import threading
from discord.ext import commands

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LunaDiscordBot(commands.Bot):
    def __init__(self, token, config):
        super().__init__(command_prefix='!', intents=discord.Intents.default())
        self.token = token
        self.config = config
        self.voice_client = None
        self.current_voice_channel = None
        
        # Simple voice settings
        self.enable_voice_tts = config.get('voice_settings', {}).get('enable_voice_tts', True)
        self.tts_cleanup_delay = config.get('voice_settings', {}).get('tts_cleanup_delay', 1.0)
        self.max_tts_length = config.get('voice_settings', {}).get('max_tts_length', 500)
        
        # Message queues for communication with main Luna
        self.message_queue = queue.Queue()
        self.response_queue = queue.Queue()

    async def on_ready(self):
        """Bot is ready"""
        logger.info(f"🤖 {self.user} is ready!")
        logger.info(f"📊 Connected to {len(self.guilds)} servers")
        for guild in self.guilds:
            logger.info(f"🏠 Server: {guild.name} (ID: {guild.id})")

    async def on_voice_state_update(self, member, before, after):
        """Handle voice state updates - but don't try to reconnect"""
        if member == self.user:
            if before.channel != after.channel:
                if after.channel:
                    logger.info(f"🎤 Joined voice channel: {after.channel.name}")
                    self.current_voice_channel = after.channel
                else:
                    logger.info(f"🎤 Left voice channel: {before.channel.name}")
                    self.current_voice_channel = None

    async def connect_to_voice(self, channel):
        """Simple voice connection - just connect and stay connected"""
        try:
            logger.info(f"🎤 Connecting to voice channel: {channel.name}")
            
            # Check if already connected to this channel
            if self.voice_client and self.voice_client.is_connected() and self.voice_client.channel == channel:
                logger.info("✅ Already connected to this voice channel")
                return self.voice_client
            
            # Disconnect from current channel if connected to a different one
            if self.voice_client and self.voice_client.is_connected():
                logger.info("🔄 Disconnecting from current voice channel first")
                await self.voice_client.disconnect()
            
            # Simple connection - no timeouts, no retries, just connect
            voice_client = await channel.connect()
            logger.info("✅ Connected to voice channel successfully")
            
            return voice_client
            
        except Exception as e:
            logger.error(f"❌ Error connecting to voice channel: {e}")
            raise e

    async def disconnect_from_voice(self):
        """Disconnect from voice channel"""
        if self.voice_client and self.voice_client.is_connected():
            await self.voice_client.disconnect()
            logger.info("🎤 Disconnected from voice channel")
            self.voice_client = None
            self.current_voice_channel = None

    @commands.command(name='joinvoice')
    async def join_voice_command(self, ctx, *, channel_name=None):
        """Join a voice channel"""
        try:
            if not ctx.author.voice:
                await ctx.send("❌ You need to be in a voice channel first!")
                return
            
            target_channel = ctx.author.voice.channel
            
            # Connect to voice
            self.voice_client = await self.connect_to_voice(target_channel)
            self.current_voice_channel = target_channel
            
            await ctx.send(f"🎤 Joined voice channel: **{target_channel.name}**")
            logger.info(f"🎤 Successfully joined voice channel: {target_channel.name}")
            
        except Exception as e:
            await ctx.send(f"❌ Error joining voice channel: {e}")
            logger.error(f"❌ Error joining voice channel: {e}")

    @commands.command(name='leave')
    async def leave_voice_command(self, ctx):
        """Leave the current voice channel"""
        try:
            await self.disconnect_from_voice()
            await ctx.send("🎤 Left voice channel")
            
        except Exception as e:
            await ctx.send(f"❌ Error leaving voice channel: {e}")
            logger.error(f"❌ Error leaving voice channel: {e}")

    @commands.command(name='voiceinfo')
    async def voice_info_command(self, ctx):
        """Get voice connection information"""
        try:
            if self.voice_client and self.voice_client.is_connected():
                channel_name = self.voice_client.channel.name
                latency = getattr(self.voice_client, 'latency', 0)
                await ctx.send(f"🎤 **Voice Status:** Connected\n📺 **Channel:** {channel_name}\n🏓 **Latency:** {latency:.3f}s")
            else:
                await ctx.send("🎤 **Voice Status:** Not connected")
                
        except Exception as e:
            await ctx.send(f"❌ Error getting voice info: {e}")

    async def play_tts_in_voice(self, text: str):
        """Play TTS audio in voice channel"""
        try:
            if not self.voice_client or not self.voice_client.is_connected():
                logger.warning("⚠️ Not connected to voice channel, cannot play TTS")
                return False
            
            # Check if voice TTS is enabled
            if not self.enable_voice_tts:
                logger.info("🎵 Voice TTS disabled, skipping audio generation")
                return False
            
            # Import Edge TTS functions
            try:
                from edge_tts_integration import edge_tts_generate
                
                # Clean text for TTS (remove Discord formatting)
                clean_text = self._clean_discord_text_for_tts(text)
                if not clean_text.strip():
                    logger.warning("⚠️ No text to synthesize after cleaning")
                    return False
                
                # Generate unique filename for this TTS request
                import uuid
                tts_filename = f"discord_tts_{uuid.uuid4().hex[:8]}.mp3"
                tts_path = os.path.join("tts_cache", tts_filename)
                
                # Ensure tts_cache directory exists
                os.makedirs("tts_cache", exist_ok=True)
                
                logger.info(f"🎤 Generating Edge TTS for Discord: {clean_text[:50]}...")
                
                # Generate TTS audio file using Edge TTS
                audio_file = await edge_tts_generate(clean_text, tts_path)
                if not audio_file or not os.path.exists(audio_file):
                    logger.error("❌ Failed to generate Edge TTS audio")
                    return False
                
                logger.info(f"✅ Edge TTS generated for Discord: {audio_file}")
                
                # Play audio in voice channel
                source = discord.FFmpegPCMAudio(audio_file)
                self.voice_client.play(source)
                
                # Wait for audio to finish playing
                while self.voice_client.is_playing():
                    await asyncio.sleep(0.1)
                
                # Clean up audio file after a short delay
                try:
                    await asyncio.sleep(self.tts_cleanup_delay)
                    if os.path.exists(audio_file):
                        os.remove(audio_file)
                        logger.debug(f"🗑️ Cleaned up TTS file: {audio_file}")
                except Exception as cleanup_error:
                    logger.warning(f"⚠️ Could not clean up TTS file: {cleanup_error}")
                
                return True
                
            except ImportError as import_error:
                logger.error(f"❌ Edge TTS not available: {import_error}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error playing TTS in voice: {e}")
            return False

    def _clean_discord_text_for_tts(self, text: str) -> str:
        """Clean Discord formatting from text for TTS"""
        import re
        
        # Remove Discord markdown formatting
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic
        text = re.sub(r'__(.*?)__', r'\1', text)      # Underline
        text = re.sub(r'~~(.*?)~~', r'\1', text)      # Strikethrough
        text = re.sub(r'`(.*?)`', r'\1', text)        # Inline code
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)  # Code blocks
        text = re.sub(r'<@!?(\d+)>', r'user', text)   # User mentions
        text = re.sub(r'<#(\d+)>', r'channel', text)  # Channel mentions
        text = re.sub(r'<@&(\d+)>', r'role', text)    # Role mentions
        text = re.sub(r'<:(.*?):(\d+)>', r'\1', text) # Custom emojis
        text = re.sub(r'<a:(.*?):(\d+)>', r'\1', text) # Animated emojis
        
        # Clean up extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    async def start_bot(self):
        """Start the bot"""
        try:
            await self.start(self.token)
        except Exception as e:
            logger.error(f"❌ Error starting bot: {e}")

    async def stop_bot(self):
        """Stop the bot"""
        try:
            if self.voice_client and self.voice_client.is_connected():
                await self.voice_client.disconnect()
            await self.close()
            logger.info("🛑 Bot stopped")
        except Exception as e:
            logger.error(f"❌ Error stopping bot: {e}")

# Example usage
if __name__ == "__main__":
    # Load config
    with open('discord_config.json', 'r') as f:
        config = json.load(f)
    
    # Get bot token
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        logger.error("❌ DISCORD_BOT_TOKEN environment variable not set")
        exit(1)
    
    # Create and start bot
    bot = LunaDiscordBot(token, config)
    
    try:
        asyncio.run(bot.start_bot())
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Bot error: {e}")
