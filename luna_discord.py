"""
Luna Discord Bot Module
Connects Luna AI to Discord for real-time chat interactions
"""

import discord
from discord.ext import commands
import asyncio
import json
import os
import time
from datetime import datetime
import logging
from typing import Optional, Dict, Any
import threading
import queue

# Import Discord user tracker
try:
    from discord_user_tracker import (
        track_discord_message, get_discord_user_context, get_discord_chat_context,
        get_recent_discord_users, get_discord_mention_suggestions
    )
    DISCORD_TRACKER_AVAILABLE = True
    print("📊 Discord user tracker loaded")
except ImportError as e:
    DISCORD_TRACKER_AVAILABLE = False
    print(f"⚠️ Discord user tracker not available: {e}")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LunaDiscordBot:
    def __init__(self, token: str, luna_ai_callback=None, config=None, ui_callback=None):
        """
        Initialize Luna Discord Bot
        
        Args:
            token: Discord bot token
            luna_ai_callback: Function to call for AI responses
            config: Discord configuration dictionary
            ui_callback: Function to send messages to Luna's UI
        """
        self.token = token
        self.luna_ai_callback = luna_ai_callback
        self.config = config or {}
        self.ui_callback = ui_callback
        self.bot = None
        self.is_connected = False
        self.message_queue = queue.Queue()
        self.response_queue = queue.Queue()
        self.voice_client = None
        self.current_voice_channel = None
        
        # Voice connection settings (load from config)
        voice_settings = self.config.get('voice_settings', {})
        self.enable_voice_tts = voice_settings.get('enable_voice_tts', True)
        self.tts_cleanup_delay = voice_settings.get('tts_cleanup_delay', 1.0)
        self.max_tts_length = voice_settings.get('max_tts_length', 500)
        
        # TTS voice settings (use same Ava voice as Luna)
        self.tts_voice = voice_settings.get('tts_voice', 'en-US-AvaMultilingualNeural')
        self.tts_rate = voice_settings.get('tts_rate', '+0%')
        self.tts_volume = voice_settings.get('tts_volume', '+0%')
        self.tts_pitch = voice_settings.get('tts_pitch', '+0%')
        
        # JavaScript voice helper integration
        self.use_js_voice_helper = voice_settings.get('use_js_voice_helper', True)
        self.js_voice_bridge = None
        
        # Voice connection persistence
        self.voice_keepalive_task = None
        self.voice_keepalive_interval = 30.0  # Check every 30 seconds
        self.voice_connection_lost = False
        self.voice_reconnect_attempts = 0
        self.max_voice_reconnect_attempts = 5
        
        # Voice connection state
        self.voice_connection_active = False
        
        
        # Bot configuration
        self.intents = discord.Intents.default()
        self.intents.message_content = True
        self.intents.guilds = True
        self.intents.members = True
        
        # Rate limiting
        self.last_response_time = {}
        self.response_cooldown = 2.0  # 2 seconds between responses per channel
        
        # Message tracking to prevent loops
        self.processed_messages = set()  # Track message IDs we've already responded to
        self.max_processed_messages = 1000  # Limit memory usage
        
        # Statistics
        self.stats = {
            'messages_processed': 0,
            'responses_sent': 0,
            'channels_active': set(),
            'start_time': None
        }
        
    async def start_bot(self):
        """Start the Discord bot"""
        try:
            self.bot = commands.Bot(
                command_prefix='!',
                intents=self.intents,
                help_command=None
            )
            
            # Event handlers
            self.bot.event(self.on_ready)
            self.bot.event(self.on_message)
            self.bot.event(self.on_command_error)
            self.bot.event(self.on_voice_state_update)
            
            # Add commands
            self._add_commands()
            
            # Start JavaScript voice helper if enabled
            if self.use_js_voice_helper:
                await self._start_js_voice_helper()
            
            # Start the bot
            await self.bot.start(self.token)
            
        except Exception as e:
            logger.error(f"❌ Failed to start Discord bot: {e}")
            raise
    
    def _add_commands(self):
        """Add Discord slash commands and text commands"""
        
        @self.bot.command(name='ping')
        async def ping(ctx):
            """Check if Luna is responsive"""
            latency = round(self.bot.latency * 1000)
            await ctx.send(f"🏓 Pong! Latency: {latency}ms")
        
        @self.bot.command(name='status')
        async def status(ctx):
            """Get Luna's current status"""
            uptime = time.time() - (self.stats['start_time'] or time.time())
            uptime_str = f"{int(uptime//3600)}h {int((uptime%3600)//60)}m {int(uptime%60)}s"
            
            embed = discord.Embed(
                title="🤖 Luna's Status",
                color=0x9B59B6,
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="📊 Messages Processed", value=self.stats['messages_processed'], inline=True)
            embed.add_field(name="💬 Responses Sent", value=self.stats['responses_sent'], inline=True)
            embed.add_field(name="⏱️ Uptime", value=uptime_str, inline=True)
            embed.add_field(name="🌐 Active Channels", value=len(self.stats['channels_active']), inline=True)
            embed.add_field(name="🔗 Connected", value="✅ Online" if self.is_connected else "❌ Offline", inline=True)
            embed.add_field(name="🏓 Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
            
            await ctx.send(embed=embed)
        
        @self.bot.command(name='help')
        async def help_command(ctx):
            """Show available commands"""
            embed = discord.Embed(
                title="🤖 Luna's Commands",
                description="Here are the commands you can use with me:",
                color=0x9B59B6
            )
            embed.add_field(
                name="💬 Chat Commands",
                value="• Just mention me or reply to my messages to chat!\n• I'll respond naturally to conversations",
                inline=False
            )
            embed.add_field(
                name="🔧 Utility Commands",
                value="• `!ping` - Check if I'm responsive\n• `!status` - View my current status\n• `!help` - Show this help message",
                inline=False
            )
            embed.add_field(
                name="🎤 Voice Commands",
                value="• `!joinvoice` - Join your voice channel\n• `!leave` - Leave voice channel\n• `!voiceinfo` - Check voice connection status\n• `!reconnectvoice` - Manually reconnect to voice\n• `!testvoice` - Test voice TTS\n• `!voiceconfig` - Show voice TTS settings\n• `!voicediag` - Run voice connection diagnostics\n• `!forcejoin` - Force join voice channel\n• `!testconnection` - Test connection with diagnostics",
                inline=False
            )
            embed.add_field(
                name="🎮 Features",
                value="• Real-time AI conversations\n• Context-aware responses\n• Voice channel TTS\n• Memory of past conversations",
                inline=False
            )
            embed.set_footer(text="Luna AI Assistant • Made with ❤️")
            
            await ctx.send(embed=embed)
        
        
        @self.bot.command(name='joinvoice')
        async def join_voice_command(ctx):
            """Join the voice channel the user is in"""
            try:
                # Check if user is in a voice channel
                if not ctx.author.voice:
                    await ctx.send("❌ You need to be in a voice channel for me to join!")
                    return
                
                # Check if already connected to a voice channel
                if self.voice_client and self.voice_client.is_connected():
                    await ctx.send("✅ I'm already connected to a voice channel!")
                    return
                
                # Join the voice channel with timeout and retry logic
                channel = ctx.author.voice.channel
                
                # Send initial message
                status_msg = await ctx.send("🔄 Connecting to voice channel...")
                
                try:
                    # Try JavaScript voice helper first if enabled
                    if self.use_js_voice_helper and self.js_voice_bridge:
                        success = await self._connect_js_voice(channel)
                        if success:
                            self.current_voice_channel = channel
                            await status_msg.edit(content=f"🎤 Successfully joined voice channel: **{channel.name}**\n🔄 JavaScript voice helper active")
                            logger.info(f"🎤 Joined voice channel via JS helper: {channel.name}")
                            return
                        else:
                            logger.warning("⚠️ JavaScript voice helper failed, falling back to Python")
                    
                    # Fallback to Python voice connection
                    self.voice_client = await self._connect_to_voice_with_retry(channel)
                    self.current_voice_channel = channel
                    
                    # Start keepalive monitoring to maintain connection
                    await self._start_voice_keepalive()
                    
                    await status_msg.edit(content=f"🎤 Successfully joined voice channel: **{channel.name}**\n🔄 Connection monitoring active")
                    logger.info(f"🎤 Joined voice channel: {channel.name}")
                    
                except Exception as e:
                    await status_msg.edit(content=f"❌ Failed to join voice channel: {str(e)}")
                    logger.error(f"❌ Voice connection failed: {e}")
                    return
                
            except Exception as e:
                await ctx.send(f"❌ Error joining voice channel: {str(e)}")
                logger.error(f"❌ Error joining voice channel: {e}")
        
        @self.bot.command(name='leave')
        async def leave_voice_command(ctx):
            """Leave the current voice channel"""
            try:
                if not self.voice_client or not self.voice_client.is_connected():
                    await ctx.send("❌ I'm not connected to any voice channel!")
                    return
                
                channel_name = self.current_voice_channel.name if self.current_voice_channel else "Unknown"
                
                # Stop keepalive monitoring first
                await self._stop_voice_keepalive()
                
                # Disconnect from voice channel
                await self.voice_client.disconnect()
                self.voice_client = None
                self.current_voice_channel = None
                self.voice_connection_lost = False
                self.voice_reconnect_attempts = 0
                
                await ctx.send(f"👋 Left voice channel: **{channel_name}**\n🛑 Connection monitoring stopped")
                logger.info(f"👋 Left voice channel: {channel_name}")
                
            except Exception as e:
                await ctx.send(f"❌ Error leaving voice channel: {str(e)}")
                logger.error(f"❌ Error leaving voice channel: {e}")
        
        @self.bot.command(name='voiceinfo')
        async def voice_info_command(ctx):
            """Get voice connection information and troubleshoot"""
            try:
                embed = discord.Embed(
                    title="🎤 Voice Connection Status",
                    color=0x9B59B6,
                    timestamp=datetime.utcnow()
                )
                
                # Voice client status
                if self.voice_client and self.voice_client.is_connected():
                    embed.add_field(
                        name="🔗 Connection Status", 
                        value="✅ Connected", 
                        inline=True
                    )
                    embed.add_field(
                        name="📢 Channel", 
                        value=self.current_voice_channel.name if self.current_voice_channel else "Unknown", 
                        inline=True
                    )
                    embed.add_field(
                        name="🏓 Latency", 
                        value=f"{round(self.voice_client.latency * 1000)}ms", 
                        inline=True
                    )
                else:
                    embed.add_field(
                        name="🔗 Connection Status", 
                        value="❌ Not Connected", 
                        inline=True
                    )
                
                # Voice settings
                embed.add_field(
                    name="⏱️ Timeout", 
                    value=f"{self.voice_timeout}s", 
                    inline=True
                )
                embed.add_field(
                    name="🔄 Retry Attempts", 
                    value=str(self.voice_retry_attempts), 
                    inline=True
                )
                embed.add_field(
                    name="🎵 TTS Enabled", 
                    value="✅ Yes" if self.enable_voice_tts else "❌ No", 
                    inline=True
                )
                
                # Keepalive status
                keepalive_status = "✅ Active" if (self.voice_keepalive_task and not self.voice_keepalive_task.done()) else "❌ Inactive"
                embed.add_field(
                    name="🔄 Keepalive", 
                    value=keepalive_status, 
                    inline=True
                )
                embed.add_field(
                    name="🔁 Reconnect Attempts", 
                    value=f"{self.voice_reconnect_attempts}/{self.max_voice_reconnect_attempts}", 
                    inline=True
                )
                embed.add_field(
                    name="📡 Connection Status", 
                    value="❌ Lost" if self.voice_connection_lost else "✅ Healthy", 
                    inline=True
                )
                
                # Troubleshooting tips
                if not self.voice_client or not self.voice_client.is_connected():
                    embed.add_field(
                        name="💡 Troubleshooting",
                        value="• Make sure you're in a voice channel\n• Check your internet connection\n• Try the `!joinvoice` command\n• Ensure Luna has voice permissions",
                        inline=False
                    )
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                await ctx.send(f"❌ Error getting voice info: {str(e)}")
                logger.error(f"❌ Error getting voice info: {e}")
        
        @self.bot.command(name='reconnectvoice')
        async def reconnect_voice_command(ctx):
            """Manually reconnect to voice channel"""
            try:
                if not self.current_voice_channel:
                    await ctx.send("❌ No voice channel to reconnect to!")
                    return
                
                await ctx.send("🔄 Attempting to reconnect to voice channel...")
                
                # Stop current keepalive
                await self._stop_voice_keepalive()
                
                # Disconnect if connected
                if self.voice_client and self.voice_client.is_connected():
                    await self.voice_client.disconnect()
                
                # Reconnect
                self.voice_client = await self._connect_to_voice_with_retry(self.current_voice_channel)
                if self.voice_client:
                    await self._start_voice_keepalive()
                    await ctx.send(f"✅ Successfully reconnected to voice channel: **{self.current_voice_channel.name}**")
                else:
                    await ctx.send("❌ Failed to reconnect to voice channel")
                
            except Exception as e:
                await ctx.send(f"❌ Error reconnecting to voice channel: {str(e)}")
                logger.error(f"❌ Error reconnecting to voice channel: {e}")
        
        @self.bot.command(name='testvoice')
        async def test_voice_command(ctx, *, message: str = "Hello! This is a test of Luna's voice in Discord."):
            """Test voice TTS in the current voice channel"""
            try:
                if not self.voice_client or not self.voice_client.is_connected():
                    await ctx.send("❌ I'm not connected to any voice channel! Use `!joinvoice` first.")
                    return
                
                await ctx.send(f"🎤 Testing voice TTS: {message}")
                logger.info(f"🎤 Testing voice TTS: {message}")
                
                # Play TTS in voice channel
                success = await self.play_tts_in_voice(message)
                if success:
                    await ctx.send("✅ Voice TTS test completed successfully!")
                else:
                    await ctx.send("❌ Voice TTS test failed. Check logs for details.")
                
            except Exception as e:
                await ctx.send(f"❌ Error testing voice TTS: {str(e)}")
                logger.error(f"❌ Error testing voice TTS: {e}")
        
        @self.bot.command(name='voiceconfig')
        async def voice_config_command(ctx):
            """Show voice TTS configuration"""
            try:
                embed = discord.Embed(
                    title="🎤 Voice TTS Configuration",
                    color=0x9B59B6,
                    timestamp=datetime.utcnow()
                )
                
                # Voice TTS settings
                embed.add_field(
                    name="🎵 Voice TTS Enabled", 
                    value="✅ Yes" if self.enable_voice_tts else "❌ No", 
                    inline=True
                )
                
                # Discord TTS settings (using Ava voice)
                embed.add_field(
                    name="🎭 Voice", 
                    value=f"`{self.tts_voice}`", 
                    inline=True
                )
                embed.add_field(
                    name="⚡ Rate", 
                    value=f"`{self.tts_rate}`", 
                    inline=True
                )
                embed.add_field(
                    name="🔊 Volume", 
                    value=f"`{self.tts_volume}`", 
                    inline=True
                )
                embed.add_field(
                    name="🎵 Pitch", 
                    value=f"`{self.tts_pitch}`", 
                    inline=True
                )
                embed.add_field(
                    name="🧹 Cleanup Delay", 
                    value=f"{self.tts_cleanup_delay}s", 
                    inline=True
                )
                embed.add_field(
                    name="🔧 Edge TTS Status", 
                    value="✅ Available (Ava Voice)", 
                    inline=True
                )
                
                # Voice connection status
                if self.voice_client and self.voice_client.is_connected():
                    embed.add_field(
                        name="🔗 Voice Connection", 
                        value="✅ Connected", 
                        inline=True
                    )
                    embed.add_field(
                        name="📢 Channel", 
                        value=self.current_voice_channel.name if self.current_voice_channel else "Unknown", 
                        inline=True
                    )
                else:
                    embed.add_field(
                        name="🔗 Voice Connection", 
                        value="❌ Not Connected", 
                        inline=True
                    )
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                await ctx.send(f"❌ Error getting voice config: {str(e)}")
                logger.error(f"❌ Error getting voice config: {e}")
        
        @self.bot.command(name='voicediag')
        async def voice_diag_command(ctx):
            """Run voice connection diagnostics"""
            try:
                embed = discord.Embed(
                    title="🔍 Voice Connection Diagnostics",
                    color=0x9B59B6,
                    timestamp=datetime.utcnow()
                )
                
                # Check bot permissions
                if ctx.guild:
                    bot_member = ctx.guild.get_member(self.bot.user.id)
                    permissions = ctx.channel.permissions_for(bot_member)
                    
                    embed.add_field(
                        name="🔐 Bot Permissions",
                        value=f"Connect: {'✅' if permissions.connect else '❌'}\nSpeak: {'✅' if permissions.speak else '❌'}\nView Channel: {'✅' if permissions.view_channel else '❌'}",
                        inline=True
                    )
                
                # Check voice channel info
                if ctx.author.voice and ctx.author.voice.channel:
                    channel = ctx.author.voice.channel
                    embed.add_field(
                        name="📢 Voice Channel Info",
                        value=f"Name: {channel.name}\nID: {channel.id}\nType: {channel.type}\nUser Limit: {channel.user_limit if channel.user_limit else 'None'}",
                        inline=True
                    )
                else:
                    embed.add_field(
                        name="📢 Voice Channel Info",
                        value="❌ You're not in a voice channel",
                        inline=True
                    )
                
                # Check network connectivity
                try:
                    import socket
                    import time
                    
                    # Test DNS resolution
                    start_time = time.time()
                    socket.gethostbyname('discord.com')
                    dns_time = time.time() - start_time
                    
                    embed.add_field(
                        name="🌐 Network Status",
                        value=f"DNS Resolution: ✅ ({dns_time:.2f}s)\nDiscord API: ✅ Connected\nVoice Servers: 🔍 Testing...",
                        inline=True
                    )
                except Exception as e:
                    embed.add_field(
                        name="🌐 Network Status",
                        value=f"❌ Network issues detected: {str(e)[:50]}...",
                        inline=True
                    )
                
                # Check Discord.py version
                try:
                    import discord
                    embed.add_field(
                        name="📦 Discord.py Version",
                        value=f"Version: {discord.__version__}\nStatus: {'✅' if discord.__version__ >= '2.0.0' else '⚠️ Old version'}",
                        inline=True
                    )
                except:
                    embed.add_field(
                        name="📦 Discord.py Version",
                        value="❌ Unable to check version",
                        inline=True
                    )
                
                # Current voice connection status
                if self.voice_client and self.voice_client.is_connected():
                    embed.add_field(
                        name="🔗 Current Connection",
                        value=f"Status: ✅ Connected\nChannel: {self.voice_client.channel.name if self.voice_client.channel else 'Unknown'}\nLatency: {round(self.voice_client.latency * 1000)}ms",
                        inline=True
                    )
                else:
                    embed.add_field(
                        name="🔗 Current Connection",
                        value="❌ Not connected",
                        inline=True
                    )
                
                # Troubleshooting recommendations
                recommendations = []
                if not permissions.connect if ctx.guild else True:
                    recommendations.append("• Grant 'Connect' permission to the bot")
                if not permissions.speak if ctx.guild else True:
                    recommendations.append("• Grant 'Speak' permission to the bot")
                if not ctx.author.voice:
                    recommendations.append("• Join a voice channel first")
                if discord.__version__ < '2.0.0':
                    recommendations.append("• Update discord.py to version 2.0.0 or higher")
                
                if not recommendations:
                    recommendations.append("• Try the `!joinvoice` command")
                    recommendations.append("• Check your internet connection")
                    recommendations.append("• Try a different voice channel")
                
                embed.add_field(
                    name="💡 Recommendations",
                    value="\n".join(recommendations[:5]),  # Limit to 5 recommendations
                    inline=False
                )
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                await ctx.send(f"❌ Error running voice diagnostics: {str(e)}")
                logger.error(f"❌ Error running voice diagnostics: {e}")
        
        @self.bot.command(name='forcejoin')
        async def force_join_command(ctx):
            """Force join voice channel, bypassing current connection state"""
            try:
                if not ctx.author.voice:
                    await ctx.send("❌ You need to be in a voice channel for me to join!")
                    return
                
                channel = ctx.author.voice.channel
                await ctx.send(f"🔄 Force joining voice channel: **{channel.name}**...")
                
                # Stop any existing keepalive
                await self._stop_voice_keepalive()
                
                # Disconnect any existing connection
                if self.voice_client:
                    try:
                        await self.voice_client.disconnect()
                    except:
                        pass
                    self.voice_client = None
                
                # Reset connection state
                self.voice_connection_lost = False
                self.voice_reconnect_attempts = 0
                
                # Force a fresh connection
                try:
                    self.voice_client = await self._connect_to_voice_with_retry(channel)
                    self.current_voice_channel = channel
                    
                    if self.voice_client:
                        await self._start_voice_keepalive()
                        await ctx.send(f"✅ Force joined voice channel: **{channel.name}**\n🔄 Connection monitoring active")
                        logger.info(f"✅ Force joined voice channel: {channel.name}")
                    else:
                        await ctx.send("❌ Failed to force join voice channel")
                        
                except Exception as e:
                    await ctx.send(f"❌ Error force joining voice channel: {str(e)}")
                    logger.error(f"❌ Error force joining voice channel: {e}")
                
            except Exception as e:
                await ctx.send(f"❌ Error in force join command: {str(e)}")
                logger.error(f"❌ Error in force join command: {e}")
        
        @self.bot.command(name='testconnection')
        async def test_connection_command(ctx):
            """Test voice connection with detailed diagnostics"""
            try:
                if not ctx.author.voice:
                    await ctx.send("❌ You need to be in a voice channel for me to join!")
                    return
                
                channel = ctx.author.voice.channel
                await ctx.send(f"🔬 Testing voice connection to **{channel.name}** with detailed diagnostics...")
                
                # Run diagnostics first
                start_time = time.time()
                
                # Test warmup
                warmup_start = time.time()
                warmup_success = await self._warmup_voice_connection(channel)
                warmup_time = time.time() - warmup_start
                
                if warmup_success:
                    await ctx.send(f"✅ Connection warmup successful ({warmup_time:.2f}s)")
                else:
                    await ctx.send(f"⚠️ Connection warmup failed ({warmup_time:.2f}s)")
                
                # Test connection
                connection_start = time.time()
                try:
                    self.voice_client = await self._connect_to_voice_with_retry(channel)
                    connection_time = time.time() - connection_start
                    total_time = time.time() - start_time
                    
                    if self.voice_client:
                        self.current_voice_channel = channel
                        await self._start_voice_keepalive()
                        
                        await ctx.send(f"✅ **Connection test successful!**\n"
                                     f"⏱️ Warmup: {warmup_time:.2f}s\n"
                                     f"⏱️ Connection: {connection_time:.2f}s\n"
                                     f"⏱️ Total: {total_time:.2f}s\n"
                                     f"🏓 Latency: {round(self.voice_client.latency * 1000)}ms")
                    else:
                        await ctx.send("❌ Connection test failed - no voice client returned")
                        
                except Exception as e:
                    connection_time = time.time() - connection_start
                    total_time = time.time() - start_time
                    await ctx.send(f"❌ **Connection test failed!**\n"
                                 f"⏱️ Warmup: {warmup_time:.2f}s\n"
                                 f"⏱️ Connection: {connection_time:.2f}s\n"
                                 f"⏱️ Total: {total_time:.2f}s\n"
                                 f"❌ Error: {str(e)}")
                
            except Exception as e:
                await ctx.send(f"❌ Error in connection test: {str(e)}")
                logger.error(f"❌ Error in connection test: {e}")
        
        # Slash commands (Discord.py 2.0+)
        @self.bot.tree.command(name="ping", description="Check if Luna is responsive")
        async def ping_slash(interaction: discord.Interaction):
            """Slash command version of ping"""
            latency = round(self.bot.latency * 1000)
            await interaction.response.send_message(f"🏓 Pong! Latency: {latency}ms")
        
        @self.bot.tree.command(name="status", description="Get Luna's current status")
        async def status_slash(interaction: discord.Interaction):
            """Slash command version of status"""
            uptime = time.time() - (self.stats['start_time'] or time.time())
            uptime_str = f"{int(uptime//3600)}h {int((uptime%3600)//60)}m {int(uptime%60)}s"
            
            embed = discord.Embed(
                title="🤖 Luna's Status",
                color=0x9B59B6,
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="📊 Messages Processed", value=self.stats['messages_processed'], inline=True)
            embed.add_field(name="💬 Responses Sent", value=self.stats['responses_sent'], inline=True)
            embed.add_field(name="⏱️ Uptime", value=uptime_str, inline=True)
            embed.add_field(name="🌐 Active Channels", value=len(self.stats['channels_active']), inline=True)
            embed.add_field(name="🔗 Connected", value="✅ Online" if self.is_connected else "❌ Offline", inline=True)
            embed.add_field(name="🏓 Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
            
            await interaction.response.send_message(embed=embed)
        
        @self.bot.tree.command(name="chat", description="Have a conversation with Luna")
        async def chat_slash(interaction: discord.Interaction, message: str):
            """Slash command for direct chat with Luna"""
            if not self.luna_ai_callback:
                await interaction.response.send_message("❌ AI system not available")
                return
            
            # Defer response for longer processing
            await interaction.response.defer()
            
            try:
                # Get AI response - use actual Discord username for personal responses
                # Let main system handle Discord context
                luna_input = message
                
                if asyncio.iscoroutinefunction(self.luna_ai_callback):
                    response = await self.luna_ai_callback(luna_input, interaction.user.display_name, "discord")
                else:
                    response = self.luna_ai_callback(luna_input, interaction.user.display_name, "discord")
                
                if response and len(response.strip()) > 0:
                    # Limit response length for Discord
                    if len(response) > 2000:
                        response = response[:1997] + "..."
                    
                    await interaction.followup.send(response)
                    self.stats['responses_sent'] += 1
                else:
                    await interaction.followup.send("🤔 I'm not sure how to respond to that...")
                    
            except Exception as e:
                logger.error(f"❌ Error in slash chat: {e}")
                await interaction.followup.send("❌ Sorry, I encountered an error processing your message.")
        
        
        @self.bot.tree.command(name="activity", description="Update Luna's activity status")
        async def activity_slash(interaction: discord.Interaction, activity_type: str, activity_text: str):
            """Update bot activity status"""
            valid_types = ['playing', 'watching', 'listening', 'streaming']
            
            if activity_type.lower() not in valid_types:
                await interaction.response.send_message(
                    f"❌ Invalid activity type. Valid types: {', '.join(valid_types)}"
                )
                return
            
            try:
                await self.update_activity(activity_type.lower(), activity_text)
                await interaction.response.send_message(
                    f"✅ Updated activity to: **{activity_type}** {activity_text}"
                )
            except Exception as e:
                await interaction.response.send_message(f"❌ Error updating activity: {str(e)}")
        
        @self.bot.tree.command(name="servers", description="List servers Luna is connected to")
        async def servers_slash(interaction: discord.Interaction):
            """List all servers the bot is connected to"""
            if not self.bot.guilds:
                await interaction.response.send_message("❌ Not connected to any servers")
                return
            
            embed = discord.Embed(
                title="🏠 Servers Luna is Connected To",
                color=0x9B59B6,
                timestamp=datetime.utcnow()
            )
            
            for guild in self.bot.guilds:
                member_count = guild.member_count
                owner = guild.owner.display_name if guild.owner else "Unknown"
                
                embed.add_field(
                    name=f"🏠 {guild.name}",
                    value=f"👥 {member_count} members\n👑 Owner: {owner}",
                    inline=True
                )
            
            embed.set_footer(text=f"Total: {len(self.bot.guilds)} servers")
            await interaction.response.send_message(embed=embed)
        
        @self.bot.tree.command(name="joinvoice", description="Join the voice channel you're in")
        async def join_voice_slash(interaction: discord.Interaction):
            """Slash command version of join voice"""
            try:
                # Check if user is in a voice channel
                if not interaction.user.voice:
                    await interaction.response.send_message("❌ You need to be in a voice channel for me to join!")
                    return
                
                # Check if already connected to a voice channel
                if self.voice_client and self.voice_client.is_connected():
                    await interaction.response.send_message("✅ I'm already connected to a voice channel!")
                    return
                
                # Defer response for longer processing
                await interaction.response.defer()
                
                # Join the voice channel with timeout and retry logic
                channel = interaction.user.voice.channel
                
                try:
                    # Try to connect with retry logic
                    self.voice_client = await self._connect_to_voice_with_retry(channel)
                    self.current_voice_channel = channel
                    
                    # Start keepalive monitoring to maintain connection
                    await self._start_voice_keepalive()
                    
                    await interaction.followup.send(f"🎤 Successfully joined voice channel: **{channel.name}**\n🔄 Connection monitoring active")
                    logger.info(f"🎤 Joined voice channel: {channel.name}")
                    
                except Exception as e:
                    await interaction.followup.send(f"❌ Failed to join voice channel: {str(e)}")
                    logger.error(f"❌ Voice connection failed: {e}")
                    return
                
            except Exception as e:
                await interaction.response.send_message(f"❌ Error joining voice channel: {str(e)}")
                logger.error(f"❌ Error joining voice channel: {e}")
        
        @self.bot.tree.command(name="leave", description="Leave the current voice channel")
        async def leave_voice_slash(interaction: discord.Interaction):
            """Slash command version of leave voice"""
            try:
                if not self.voice_client or not self.voice_client.is_connected():
                    await interaction.response.send_message("❌ I'm not connected to any voice channel!")
                    return
                
                channel_name = self.current_voice_channel.name if self.current_voice_channel else "Unknown"
                
                # Stop keepalive monitoring first
                await self._stop_voice_keepalive()
                
                # Disconnect from voice channel
                await self.voice_client.disconnect()
                self.voice_client = None
                self.current_voice_channel = None
                self.voice_connection_lost = False
                self.voice_reconnect_attempts = 0
                
                await interaction.response.send_message(f"👋 Left voice channel: **{channel_name}**\n🛑 Connection monitoring stopped")
                logger.info(f"👋 Left voice channel: {channel_name}")
                
            except Exception as e:
                await interaction.response.send_message(f"❌ Error leaving voice channel: {str(e)}")
                logger.error(f"❌ Error leaving voice channel: {e}")
        
        @self.bot.tree.command(name="voiceinfo", description="Get voice connection information and troubleshoot")
        async def voice_info_slash(interaction: discord.Interaction):
            """Slash command version of voice info"""
            try:
                embed = discord.Embed(
                    title="🎤 Voice Connection Status",
                    color=0x9B59B6,
                    timestamp=datetime.utcnow()
                )
                
                # Voice client status
                if self.voice_client and self.voice_client.is_connected():
                    embed.add_field(
                        name="🔗 Connection Status", 
                        value="✅ Connected", 
                        inline=True
                    )
                    embed.add_field(
                        name="📢 Channel", 
                        value=self.current_voice_channel.name if self.current_voice_channel else "Unknown", 
                        inline=True
                    )
                    embed.add_field(
                        name="🏓 Latency", 
                        value=f"{round(self.voice_client.latency * 1000)}ms", 
                        inline=True
                    )
                else:
                    embed.add_field(
                        name="🔗 Connection Status", 
                        value="❌ Not Connected", 
                        inline=True
                    )
                
                # Voice settings
                embed.add_field(
                    name="⏱️ Timeout", 
                    value=f"{self.voice_timeout}s", 
                    inline=True
                )
                embed.add_field(
                    name="🔄 Retry Attempts", 
                    value=str(self.voice_retry_attempts), 
                    inline=True
                )
                embed.add_field(
                    name="🎵 TTS Enabled", 
                    value="✅ Yes" if self.enable_voice_tts else "❌ No", 
                    inline=True
                )
                
                # Keepalive status
                keepalive_status = "✅ Active" if (self.voice_keepalive_task and not self.voice_keepalive_task.done()) else "❌ Inactive"
                embed.add_field(
                    name="🔄 Keepalive", 
                    value=keepalive_status, 
                    inline=True
                )
                embed.add_field(
                    name="🔁 Reconnect Attempts", 
                    value=f"{self.voice_reconnect_attempts}/{self.max_voice_reconnect_attempts}", 
                    inline=True
                )
                embed.add_field(
                    name="📡 Connection Status", 
                    value="❌ Lost" if self.voice_connection_lost else "✅ Healthy", 
                    inline=True
                )
                
                # Troubleshooting tips
                if not self.voice_client or not self.voice_client.is_connected():
                    embed.add_field(
                        name="💡 Troubleshooting",
                        value="• Make sure you're in a voice channel\n• Check your internet connection\n• Try the `/joinvoice` command\n• Ensure Luna has voice permissions",
                        inline=False
                    )
                
                await interaction.response.send_message(embed=embed)
                
            except Exception as e:
                await interaction.response.send_message(f"❌ Error getting voice info: {str(e)}")
                logger.error(f"❌ Error getting voice info: {e}")
        
        @self.bot.tree.command(name="reconnectvoice", description="Manually reconnect to voice channel")
        async def reconnect_voice_slash(interaction: discord.Interaction):
            """Slash command version of reconnect voice"""
            try:
                if not self.current_voice_channel:
                    await interaction.response.send_message("❌ No voice channel to reconnect to!")
                    return
                
                await interaction.response.defer()
                
                # Stop current keepalive
                await self._stop_voice_keepalive()
                
                # Disconnect if connected
                if self.voice_client and self.voice_client.is_connected():
                    await self.voice_client.disconnect()
                
                # Reconnect
                self.voice_client = await self._connect_to_voice_with_retry(self.current_voice_channel)
                if self.voice_client:
                    await self._start_voice_keepalive()
                    await interaction.followup.send(f"✅ Successfully reconnected to voice channel: **{self.current_voice_channel.name}**")
                else:
                    await interaction.followup.send("❌ Failed to reconnect to voice channel")
                
            except Exception as e:
                await interaction.response.send_message(f"❌ Error reconnecting to voice channel: {str(e)}")
                logger.error(f"❌ Error reconnecting to voice channel: {e}")
        
        @self.bot.tree.command(name="testvoice", description="Test voice TTS in the current voice channel")
        async def test_voice_slash(interaction: discord.Interaction, message: str = "Hello! This is a test of Luna's voice in Discord."):
            """Slash command version of test voice"""
            try:
                if not self.voice_client or not self.voice_client.is_connected():
                    await interaction.response.send_message("❌ I'm not connected to any voice channel! Use `/joinvoice` first.")
                    return
                
                await interaction.response.defer()
                
                logger.info(f"🎤 Testing voice TTS: {message}")
                
                # Play TTS in voice channel
                success = await self.play_tts_in_voice(message)
                if success:
                    await interaction.followup.send(f"✅ Voice TTS test completed successfully!\n🎤 Tested: {message}")
                else:
                    await interaction.followup.send("❌ Voice TTS test failed. Check logs for details.")
                
            except Exception as e:
                await interaction.response.send_message(f"❌ Error testing voice TTS: {str(e)}")
                logger.error(f"❌ Error testing voice TTS: {e}")
        
        @self.bot.tree.command(name="voiceconfig", description="Show voice TTS configuration")
        async def voice_config_slash(interaction: discord.Interaction):
            """Slash command version of voice config"""
            try:
                embed = discord.Embed(
                    title="🎤 Voice TTS Configuration",
                    color=0x9B59B6,
                    timestamp=datetime.utcnow()
                )
                
                # Voice TTS settings
                embed.add_field(
                    name="🎵 Voice TTS Enabled", 
                    value="✅ Yes" if self.enable_voice_tts else "❌ No", 
                    inline=True
                )
                
                # Try to get Edge TTS config
                try:
                    from edge_tts_integration import get_edge_tts_config
                    edge_config = get_edge_tts_config()
                    
                    embed.add_field(
                        name="🎭 Voice", 
                        value=edge_config.get('voice', 'Default'), 
                        inline=True
                    )
                    embed.add_field(
                        name="⚡ Rate", 
                        value=edge_config.get('rate', 'Default'), 
                        inline=True
                    )
                    embed.add_field(
                        name="🔊 Volume", 
                        value=edge_config.get('volume', 'Default'), 
                        inline=True
                    )
                    embed.add_field(
                        name="🎵 Pitch", 
                        value=edge_config.get('pitch', 'Default'), 
                        inline=True
                    )
                    embed.add_field(
                        name="🔧 Edge TTS Status", 
                        value="✅ Available", 
                        inline=True
                    )
                    
                except ImportError:
                    embed.add_field(
                        name="🔧 Edge TTS Status", 
                        value="❌ Not Available", 
                        inline=True
                    )
                
                # Voice connection status
                if self.voice_client and self.voice_client.is_connected():
                    embed.add_field(
                        name="🔗 Voice Connection", 
                        value="✅ Connected", 
                        inline=True
                    )
                    embed.add_field(
                        name="📢 Channel", 
                        value=self.current_voice_channel.name if self.current_voice_channel else "Unknown", 
                        inline=True
                    )
                else:
                    embed.add_field(
                        name="🔗 Voice Connection", 
                        value="❌ Not Connected", 
                        inline=True
                    )
                
                await interaction.response.send_message(embed=embed)
                
            except Exception as e:
                await interaction.response.send_message(f"❌ Error getting voice config: {str(e)}")
                logger.error(f"❌ Error getting voice config: {e}")
    
    async def on_ready(self):
        """Called when bot is ready"""
        self.is_connected = True
        self.stats['start_time'] = time.time()
        
        # Set bot activity based on config
        activity_type = self._get_activity_type()
        activity_text = self._get_activity_text()
        
        activity = discord.Activity(
            type=activity_type,
            name=activity_text
        )
        await self.bot.change_presence(activity=activity)
        
        # Sync slash commands
        try:
            synced = await self.bot.tree.sync()
            logger.info(f"✅ Synced {len(synced)} slash commands")
        except Exception as e:
            logger.error(f"❌ Failed to sync slash commands: {e}")
        
        logger.info(f"🤖 Luna Discord Bot is ready!")
        logger.info(f"📊 Connected to {len(self.bot.guilds)} servers")
        logger.info(f"👥 Serving {len(self.bot.users)} users")
        
        # Print server list
        for guild in self.bot.guilds:
            logger.info(f"🏠 Server: {guild.name} (ID: {guild.id})")
    
    async def handle_bot_message(self, message):
        """Handle messages from other Discord bots"""
        try:
            # Check if we've already processed this message
            if self._is_message_processed(message.id):
                print(f"🤖 Skipping already processed bot message: {message.id}")
                return
            
            # Get bot information
            bot_name = message.author.display_name or message.author.name
            bot_id = message.author.id
            
            # Check if this is a bot Luna should interact with
            if await self._should_interact_with_bot(message):
                # Mark message as processed BEFORE sending response
                self._mark_message_processed(message.id)
                
                # Send the bot's message directly without paraphrasing
                if self.luna_ai_callback:
                    if asyncio.iscoroutinefunction(self.luna_ai_callback):
                        response = await self.luna_ai_callback(message.content, bot_name, "discord_bot")
                    else:
                        response = self.luna_ai_callback(message.content, bot_name, "discord_bot")
                    
                    if response and len(response.strip()) > 0:
                        # Send response to the bot
                        await message.channel.send(response)
                        print(f"🤖 Luna responded to bot {bot_name}: {response[:50]}...")
            
        except Exception as e:
            print(f"❌ Error handling bot message: {e}")
    
    def _is_message_processed(self, message_id):
        """Check if we've already processed this message"""
        return message_id in self.processed_messages
    
    def _mark_message_processed(self, message_id):
        """Mark a message as processed and clean up old messages if needed"""
        self.processed_messages.add(message_id)
        
        # Clean up old messages to prevent memory bloat
        if len(self.processed_messages) > self.max_processed_messages:
            # Remove oldest 100 messages (simple cleanup)
            messages_to_remove = list(self.processed_messages)[:100]
            for msg_id in messages_to_remove:
                self.processed_messages.discard(msg_id)
    
    async def _should_interact_with_bot(self, message):
        """Determine if Luna should interact with a specific bot"""
        bot_name = message.author.display_name or message.author.name
        bot_id = message.author.id
        
        # EXCLUDE Luna's own bot to prevent self-response loops
        if "luna" in bot_name.lower() or "luna bot" in bot_name.lower():
            print(f"🚫 Skipping Luna's own bot message: {bot_name}")
            return False
        
        # Only interact with specific approved bots
        approved_bots = [
            "connor app", "connor_app", "connor-app",
            "roommate app", "roommate_app", "roommate-app",
            "solen app", "solen_app", "solen-app"
        ]
        
        # Check if bot name matches approved bots
        bot_name_lower = bot_name.lower()
        for approved_bot in approved_bots:
            if approved_bot in bot_name_lower:
                print(f"✅ Approved bot detected: {bot_name}")
                return True
        
        # Check if message content contains specific interaction keywords
        message_lower = message.content.lower()
        interaction_keywords = [
            "luna", "hello", "hi", "hey", "talk", "chat"
        ]
        
        for keyword in interaction_keywords:
            if keyword in message_lower:
                print(f"✅ Bot message contains interaction keyword: {keyword}")
                return True
        
        print(f"🚫 Bot not approved for interaction: {bot_name}")
        return False
    
    async def on_message(self, message):
        """Handle incoming messages"""
        # Process commands first
        await self.bot.process_commands(message)
        
        # Check if we've already processed this message
        if self._is_message_processed(message.id):
            print(f"👤 Skipping already processed message: {message.id}")
            return
        
        # Check if Luna should respond to this message (users and bots)
        should_respond = await self._should_respond_to_message(message)
        if not should_respond:
            return
        
        # Rate limiting
        channel_id = message.channel.id
        current_time = time.time()
        if channel_id in self.last_response_time:
            time_since_last = current_time - self.last_response_time[channel_id]
            if time_since_last < self.response_cooldown:
                return
        
        # Update statistics
        self.stats['messages_processed'] += 1
        self.stats['channels_active'].add(channel_id)
        self.last_response_time[channel_id] = current_time
        
        # Track Discord user message
        if DISCORD_TRACKER_AVAILABLE:
            try:
                track_discord_message(
                    message.author.display_name, 
                    message.content, 
                    message.channel.name,
                    message.guild.name if message.guild else "DM"
                )
                print(f"📊 Tracked Discord message from {message.author.display_name}")
            except Exception as tracker_error:
                print(f"⚠️ Could not track Discord message: {tracker_error}")
        
        # Mark message as processed BEFORE sending response
        self._mark_message_processed(message.id)
        
        # Get AI response
        try:
            response = await self._get_ai_response(message)
            if response:
                # Send response directly to Discord
                await message.channel.send(response)
                self.stats['responses_sent'] += 1
                
                # Send Discord message to Luna's UI for display only (no auto-response)
                if self.ui_callback:
                    try:
                        discord_message = f"[Discord] {message.author.display_name} in #{message.channel.name}: {message.content}"
                        luna_response = f"Luna: {response}"
                        # Send both message and response to UI for display
                        self.ui_callback(f"{discord_message}\n{luna_response}")
                    except Exception as e:
                        logger.error(f"❌ Error sending message to UI: {e}")
                
                # Play TTS in voice channel if connected
                if self.voice_client and self.voice_client.is_connected():
                    try:
                        await self.play_tts_in_voice(response)
                    except Exception as e:
                        logger.error(f"❌ Error playing TTS in voice: {e}")
                
        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")
            await message.channel.send("❌ Sorry, I encountered an error processing your message.")
    
    async def _should_respond_to_message(self, message) -> bool:
        """Determine if Luna should respond to a message"""
        content = message.content.lower()
        
        # ONLY respond in "chris-chat" channel (case-insensitive)
        channel_name = message.channel.name.lower() if hasattr(message.channel, 'name') else ""
        if channel_name != "chris-chat":
            print(f"🚫 Ignoring message from channel '{message.channel.name}' - only responding in 'chris-chat'")
            return False
        
        # If we reach here, we're in the chris-chat channel
        sender_type = "bot" if message.author.bot else "user"
        print(f"✅ Message from {sender_type} '{message.author.display_name}' in '{message.channel.name}' - processing in chris-chat channel")
        
        # Don't respond to our own messages
        if message.author == self.bot.user:
            return False
        
        # Always respond if mentioned
        if self.bot.user.mentioned_in(message):
            return True
        
        # Respond to direct replies
        if message.reference and message.reference.resolved:
            if message.reference.resolved.author == self.bot.user:
                return True
        
        # Always respond when "Luna" is mentioned (if enabled in config)
        if hasattr(self, 'config') and self.config.get('respond_to_luna_mention', True) and 'luna' in content:
            return True
        
        # For chris-chat channel, respond to all messages (users and bots) but only once
        return True
        
        # Respond to certain keywords (optional)
        luna_keywords = ['ai', 'assistant', 'help']
        if any(keyword in content for keyword in luna_keywords):
            # 30% chance to respond to keywords
            import random
            return random.random() < 0.3
        
        return False
    
    async def _get_ai_response(self, message) -> Optional[str]:
        """Get AI response from Luna"""
        if not self.luna_ai_callback:
            return "❌ AI system not available"
        
        try:
            # Prepare context for Luna
            context = {
                'user': message.author.display_name,
                'channel': message.channel.name,
                'guild': message.guild.name if message.guild else 'DM',
                'message': message.content,
                'timestamp': message.created_at.isoformat()
            }
            
            # Get Discord context for Luna
            discord_context = ""
            if DISCORD_TRACKER_AVAILABLE:
                try:
                    user_context = get_discord_user_context(message.author.display_name)
                    chat_context = get_discord_chat_context()
                    recent_users = get_recent_discord_users(3)
                    
                    discord_context = f"""
This is a message from a Discord user: {user_context}
{chat_context}
Recent Discord users: {', '.join(recent_users) if recent_users else 'None'}
I should respond personally to {message.author.display_name} and use their name naturally
I should remember them and care about their messages
I should give only ONE response - no alternatives or multiple options
"""
                except Exception as context_error:
                    print(f"⚠️ Could not get Discord context: {context_error}")
                    discord_context = f"This is a message from a Discord user named {message.author.display_name}. I should respond naturally but use their username {message.author.display_name} instead of calling them Chris."
            else:
                discord_context = f"This is a message from a Discord user named {message.author.display_name}. I should respond naturally but use their username {message.author.display_name} instead of calling them Chris."
            
            # Create input for Luna - let main system handle Discord context
            luna_input = message.content
            
            # Get response from Luna with the actual Discord username
            if asyncio.iscoroutinefunction(self.luna_ai_callback):
                response = await self.luna_ai_callback(luna_input, message.author.display_name, "discord")
            else:
                response = self.luna_ai_callback(luna_input, message.author.display_name, "discord")
            
            # Process response
            if response and len(response.strip()) > 0:
                # Add natural mention if the response doesn't already include the username
                if message.author.display_name.lower() not in response.lower() and DISCORD_TRACKER_AVAILABLE:
                    try:
                        mention_suggestions = get_discord_mention_suggestions(message.author.display_name)
                        if mention_suggestions:
                            natural_mention = mention_suggestions[0]
                            # Add mention at the end if it's a short response, or beginning if longer
                            if len(response) < 100:
                                response = f"{response} {natural_mention}"
                            else:
                                response = f"{natural_mention} {response}"
                    except Exception as mention_error:
                        print(f"⚠️ Could not add Discord mention: {mention_error}")
                
                # Limit response length for Discord
                if len(response) > 2000:
                    response = response[:1997] + "..."
                
                return response
            else:
                # Provide more specific error information
                if response is None:
                    logger.warning(f"⚠️ Discord response was None from Luna AI callback")
                elif response == "":
                    logger.warning(f"⚠️ Discord response was empty string from Luna AI callback")
                else:
                    logger.warning(f"⚠️ Discord response was invalid: '{response}' (type: {type(response)})")
                
                # Retry once with a simpler input
                logger.info("🔄 Retrying Discord response generation...")
                try:
                    # Create a simpler input for retry
                    simple_input = f"User {message.author.display_name} said: {message.content}"
                    
                    # Retry with simpler input
                    if asyncio.iscoroutinefunction(self.luna_ai_callback):
                        retry_response = await self.luna_ai_callback(simple_input, message.author.display_name, "discord")
                    else:
                        retry_response = self.luna_ai_callback(simple_input, message.author.display_name, "discord")
                    
                    if retry_response and len(retry_response.strip()) > 0:
                        logger.info("✅ Discord retry successful!")
                        # Limit response length for Discord
                        if len(retry_response) > 2000:
                            retry_response = retry_response[:1997] + "..."
                        return retry_response
                    else:
                        logger.warning("⚠️ Discord retry also failed")
                except Exception as retry_error:
                    logger.error(f"❌ Discord retry error: {retry_error}")
                
                # Final fallback response
                return f"Sorry {message.author.display_name}, I'm having trouble thinking right now. Can you try asking me something else?"
            
        except Exception as e:
            logger.error(f"❌ Error getting AI response: {e}")
            return f"Sorry, I'm having trouble thinking right now. Error: {str(e)[:100]}"
        
        return None
    
    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore unknown commands
        
        logger.error(f"❌ Command error: {error}")
        await ctx.send(f"❌ Error: {str(error)}")
    
    async def on_voice_state_update(self, member, before, after):
        """Handle voice state updates for connection monitoring"""
        await self._on_voice_state_update(member, before, after)
    
    async def send_message_to_channel(self, channel_id: int, message: str):
        """Send a message to a specific channel"""
        try:
            channel = self.bot.get_channel(channel_id)
            if channel:
                await channel.send(message)
                return True
        except Exception as e:
            logger.error(f"❌ Error sending message to channel {channel_id}: {e}")
        return False
    
    async def send_dm_to_user(self, user_id: int, message: str):
        """Send a direct message to a user"""
        try:
            user = self.bot.get_user(user_id)
            if user:
                await user.send(message)
                return True
        except Exception as e:
            logger.error(f"❌ Error sending DM to user {user_id}: {e}")
        return False
    
    async def send_message_to_discord_channel(self, channel_id: int, message: str):
        """Send a message to a specific Discord channel"""
        try:
            if not self.bot or not self.is_connected:
                logger.error(f"❌ Discord bot not connected")
                return False
                
            channel = self.bot.get_channel(channel_id)
            if not channel:
                logger.error(f"❌ Discord channel {channel_id} not found")
                return False
                
            await channel.send(message)
            logger.info(f"✅ Message sent to Discord channel {channel_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error sending message to Discord channel {channel_id}: {e}")
        return False
    
    async def _connect_to_voice_with_retry(self, channel, max_attempts=None):
        """Simple voice connection - just connect and stay connected like any Discord bot"""
        logger.info(f"🎤 Connecting to voice channel: {channel.name}")
        
        try:
            # Check if already connected to this channel
            if self.voice_client and self.voice_client.is_connected() and self.voice_client.channel == channel:
                logger.info("✅ Already connected to this voice channel")
                return self.voice_client
            
            # Disconnect from current channel if connected to a different one
            if self.voice_client and self.voice_client.is_connected():
                logger.info("🔄 Disconnecting from current voice channel first")
                await self.voice_client.disconnect()
            
            # Simple connection with infinite timeout
            voice_client = await channel.connect(timeout=float('inf'))
            logger.info("✅ Connected to voice channel successfully")
            
            return voice_client
            
        except Exception as e:
            logger.error(f"❌ Error connecting to voice channel: {e}")
            raise e

    async def _warmup_voice_connection(self, channel):
        """Warm up voice connection to prevent Discord timeouts"""
        if not self.voice_connection_warmup:
            return True
            
        try:
            logger.info("🔥 Warming up voice connection...")
            
            # Pre-warm the connection by checking channel permissions and state
            if hasattr(channel, 'permissions_for'):
                bot_member = channel.guild.get_member(self.bot.user.id)
                if bot_member:
                    permissions = channel.permissions_for(bot_member)
                    if not permissions.connect:
                        raise Exception("Bot lacks 'Connect' permission")
                    if not permissions.speak:
                        raise Exception("Bot lacks 'Speak' permission")
                    logger.info("✅ Voice permissions verified")
            
            # Check if channel is available
            if hasattr(channel, 'user_limit') and channel.user_limit > 0:
                connected_users = len([m for m in channel.members if not m.bot])
                if connected_users >= channel.user_limit:
                    raise Exception(f"Voice channel is full ({connected_users}/{channel.user_limit})")
                logger.info(f"✅ Voice channel has space ({connected_users}/{channel.user_limit})")
            
            # Small delay to let Discord prepare
            await asyncio.sleep(0.5)
            logger.info("✅ Voice connection warmed up")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Voice connection warmup failed: {e}")
            return False

    async def _start_voice_keepalive(self):
        """Start voice connection keepalive monitoring (simplified)"""
        # Simplified - just log that we're connected
        logger.info("✅ Voice connection established - no keepalive needed")

    async def _stop_voice_keepalive(self):
        """Stop voice connection keepalive monitoring (simplified)"""
        logger.info("🔄 Voice connection monitoring stopped")

    async def _voice_keepalive_loop(self):
        """Main voice keepalive loop to maintain connection"""
        logger.info("🔄 Voice keepalive loop started")
        
        while True:
            try:
                await asyncio.sleep(self.voice_keepalive_interval)
                
                if not self.voice_client or not self.voice_client.is_connected():
                    logger.warning("⚠️ Voice client disconnected, attempting to reconnect...")
                    success = await self._attempt_voice_reconnect()
                    if not success:
                        # If reconnection failed, wait longer before next attempt
                        logger.warning("⚠️ Reconnection failed, waiting 10 seconds before next attempt...")
                        await asyncio.sleep(10)
                    continue
                
                # Check if voice client is still healthy
                try:
                    # Send a ping to check connection health
                    if hasattr(self.voice_client, 'ping'):
                        latency = self.voice_client.ping
                        logger.debug(f"🏓 Voice ping: {latency}ms")
                    
                    # Check if we're still in the same channel
                    if self.current_voice_channel and self.voice_client.channel != self.current_voice_channel:
                        logger.warning("⚠️ Voice client moved to different channel, reconnecting...")
                        await self._attempt_voice_reconnect()
                        continue
                    
                    logger.debug("✅ Voice connection healthy")
                    self.voice_connection_lost = False
                    self.voice_reconnect_attempts = 0
                    
                except Exception as e:
                    logger.warning(f"⚠️ Voice connection health check failed: {e}")
                    await self._attempt_voice_reconnect()
                    
            except asyncio.CancelledError:
                logger.info("🛑 Voice keepalive loop cancelled")
                break
            except Exception as e:
                logger.error(f"❌ Error in voice keepalive loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying

    async def _attempt_voice_reconnect(self):
        """Attempt to reconnect to voice channel"""
        if not self.current_voice_channel:
            logger.warning("⚠️ No voice channel to reconnect to")
            return False
        
        if self.voice_reconnect_attempts >= self.max_voice_reconnect_attempts:
            logger.error(f"❌ Max voice reconnection attempts ({self.max_voice_reconnect_attempts}) reached")
            self.voice_connection_lost = True
            return False
        
        self.voice_reconnect_attempts += 1
        logger.info(f"🔄 Attempting voice reconnection {self.voice_reconnect_attempts}/{self.max_voice_reconnect_attempts}")
        
        try:
            # Disconnect existing client if any
            if self.voice_client:
                try:
                    await self.voice_client.disconnect()
                except:
                    pass
                self.voice_client = None
            
            # Wait a moment before reconnecting to avoid rapid reconnection attempts
            await asyncio.sleep(2.0)
            
            # Reconnect to the channel
            self.voice_client = await self._connect_to_voice_with_retry(self.current_voice_channel)
            if self.voice_client:
                logger.info("✅ Voice reconnection successful")
                self.voice_connection_lost = False
                self.voice_reconnect_attempts = 0
                # Restart keepalive monitoring
                await self._start_voice_keepalive()
                return True
            else:
                logger.error("❌ Voice reconnection failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Voice reconnection error: {e}")
            return False

    async def _on_voice_state_update(self, member, before, after):
        """Handle voice state updates for connection monitoring"""
        if member == self.bot.user:
            if before.channel != after.channel:
                if after.channel:
                    logger.info(f"🎤 Joined voice channel: {after.channel.name}")
                    # Update current voice channel
                    self.current_voice_channel = after.channel
                    # Update voice client reference - get the actual voice client from the bot
                    self.voice_client = self.bot.voice_clients[0] if self.bot.voice_clients else None
                    logger.info(f"🔊 Voice client updated: {self.voice_client is not None}")
                    # Start keepalive monitoring
                    await self._start_voice_keepalive()
                else:
                    logger.info(f"👋 Left voice channel: {before.channel.name if before.channel else 'Unknown'}")
                    # DON'T clear current_voice_channel here - keep it for reconnection attempts
                    # Only clear it when we explicitly disconnect via !leave command
                    # Clear voice client reference
                    self.voice_client = None
                    # Stop keepalive monitoring
                    await self._stop_voice_keepalive()

    async def play_tts_in_voice(self, text: str):
        """Play TTS audio in the current voice channel using Edge TTS"""
        try:
            # Check if we should use JavaScript voice helper
            if self.use_js_voice_helper and self.js_voice_bridge:
                return await self._play_tts_js_voice(text)
            
            # Fallback to Python voice client
            if not self.voice_client or not self.voice_client.is_connected():
                logger.warning("⚠️ Not connected to voice channel, cannot play TTS")
                return False
            
            # Check if voice TTS is enabled
            if not self.enable_voice_tts:
                logger.info("🎵 Voice TTS disabled, skipping audio generation")
                return False
            
            # Import Edge TTS functions
            try:
                from edge_tts_integration import edge_tts_manager
                
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
                
                logger.info(f"🎤 Generating Edge TTS with Ava voice for: {clean_text[:50]}...")
                
                # Use Edge TTS with default settings (normal pitch, no parameter changes)
                audio_file = await edge_tts_manager.generate_speech(clean_text, tts_path)
                if not audio_file or not os.path.exists(audio_file):
                    logger.error("❌ Failed to generate Edge TTS audio")
                    return False
                
                logger.info(f"✅ Edge TTS generated: {audio_file}")
                
                # Play audio in voice channel using FFmpeg
                audio_source = discord.FFmpegPCMAudio(audio_file)
                
                # Check if voice client is still connected before playing
                if not self.voice_client.is_connected():
                    logger.warning("⚠️ Voice client disconnected while generating TTS")
                    return False
                
                self.voice_client.play(audio_source)
                
                # Wait for audio to finish playing
                while self.voice_client.is_playing():
                    await asyncio.sleep(0.1)
                
                logger.info(f"🎤 Successfully played TTS in voice channel: {clean_text[:50]}...")
                
                # Clean up audio file after a short delay
                try:
                    await asyncio.sleep(self.tts_cleanup_delay)  # Configurable delay to ensure playback is complete
                    if os.path.exists(audio_file):
                        os.remove(audio_file)
                        logger.debug(f"🗑️ Cleaned up TTS file: {audio_file}")
                except Exception as cleanup_error:
                    logger.warning(f"⚠️ Could not clean up TTS file: {cleanup_error}")
                
                return True
                
            except ImportError as import_error:
                logger.error(f"❌ Edge TTS not available: {import_error}")
                # Fallback to basic voice engine if available
                try:
                    from voice_engine import generate_tts_audio
                    audio_file = generate_tts_audio(text)
                    if audio_file and os.path.exists(audio_file):
                        audio_source = discord.FFmpegPCMAudio(audio_file)
                        self.voice_client.play(audio_source)
                        while self.voice_client.is_playing():
                            await asyncio.sleep(0.1)
                        os.remove(audio_file)
                        return True
                except ImportError:
                    pass
                return False
                
        except Exception as e:
            logger.error(f"❌ Error playing TTS in voice channel: {e}")
            return False
    
    def _clean_discord_text_for_tts(self, text: str) -> str:
        """Clean Discord text for better TTS synthesis"""
        import re
        
        # Remove Discord formatting
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # **bold** → bold
        text = re.sub(r'\*([^*]+)\*', r'\1', text)      # *italic* → italic
        text = re.sub(r'`([^`]+)`', r'\1', text)        # `code` → code
        text = re.sub(r'#{1,6}\s*', '', text)           # Remove headers
        text = re.sub(r'<@!?(\d+)>', 'user', text)      # @mentions → user
        text = re.sub(r'<#(\d+)>', 'channel', text)     # #channel → channel
        text = re.sub(r'<@&(\d+)>', 'role', text)       # @role → role
        text = re.sub(r'<:(\w+):\d+>', r':\1:', text)  # Custom emojis → :name:
        
        # Remove URLs but keep the text
        text = re.sub(r'https?://\S+', '', text)
        
        # Clean up extra whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Remove excessive punctuation
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
        text = re.sub(r'[.]{2,}', '.', text)
        
        # Limit length for faster synthesis
        if len(text) > self.max_tts_length:
            # Split at sentence boundaries and take first part
            sentences = text.split('.')
            result = ""
            for sentence in sentences:
                if len(result + sentence) < self.max_tts_length - 100:  # Leave some buffer
                    result += sentence + ". "
                else:
                    break
            text = result.strip()
        
        return text
    
    def _get_activity_type(self) -> discord.ActivityType:
        """Get activity type from config"""
        activity_type_str = getattr(self, 'activity_type', 'watching')
        
        activity_map = {
            'playing': discord.ActivityType.playing,
            'watching': discord.ActivityType.watching,
            'listening': discord.ActivityType.listening,
            'streaming': discord.ActivityType.streaming
        }
        
        return activity_map.get(activity_type_str, discord.ActivityType.watching)
    
    def _get_activity_text(self) -> str:
        """Get activity text from config"""
        return getattr(self, 'activity_text', 'your desktop 👀')
    
    async def update_activity(self, activity_type: str = None, activity_text: str = None):
        """Update bot activity"""
        if not self.bot:
            return
        
        if activity_type:
            self.activity_type = activity_type
        if activity_text:
            self.activity_text = activity_text
        
        activity = discord.Activity(
            type=self._get_activity_type(),
            name=self._get_activity_text()
        )
        await self.bot.change_presence(activity=activity)
        logger.info(f"🔄 Updated activity: {self.activity_type} {self.activity_text}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get bot statistics"""
        uptime = time.time() - (self.stats['start_time'] or time.time())
        return {
            'connected': self.is_connected,
            'messages_processed': self.stats['messages_processed'],
            'responses_sent': self.stats['responses_sent'],
            'channels_active': len(self.stats['channels_active']),
            'uptime_seconds': uptime,
            'guilds': len(self.bot.guilds) if self.bot else 0,
            'users': len(self.bot.users) if self.bot else 0,
            'activity_type': getattr(self, 'activity_type', 'watching'),
            'activity_text': getattr(self, 'activity_text', 'your desktop 👀')
        }
    
    async def _start_js_voice_helper(self):
        """Start the JavaScript voice helper"""
        try:
            from discord_voice_bridge import start_voice_bridge
            logger.info("🎤 Starting JavaScript voice helper...")
            success = await start_voice_bridge(self.token)
            if success:
                self.js_voice_bridge = True
                logger.info("✅ JavaScript voice helper started")
            else:
                logger.warning("⚠️ Failed to start JavaScript voice helper, falling back to Python voice")
                self.use_js_voice_helper = False
        except ImportError:
            logger.warning("⚠️ Discord voice bridge not available, using Python voice only")
            self.use_js_voice_helper = False
        except Exception as e:
            logger.error(f"❌ Error starting JavaScript voice helper: {e}")
            self.use_js_voice_helper = False

    async def _stop_js_voice_helper(self):
        """Stop the JavaScript voice helper"""
        try:
            if self.js_voice_bridge:
                from discord_voice_bridge import stop_voice_bridge
                await stop_voice_bridge()
                self.js_voice_bridge = None
                logger.info("🛑 JavaScript voice helper stopped")
        except Exception as e:
            logger.error(f"❌ Error stopping JavaScript voice helper: {e}")

    async def _connect_js_voice(self, channel):
        """Connect to voice channel using JavaScript helper"""
        try:
            from discord_voice_bridge import connect_to_voice_channel
            guild_id = str(channel.guild.id)
            channel_id = str(channel.id)
            return await connect_to_voice_channel(guild_id, channel_id)
        except Exception as e:
            logger.error(f"❌ Error connecting via JS voice helper: {e}")
            return False

    async def _disconnect_js_voice(self):
        """Disconnect from voice channel using JavaScript helper"""
        try:
            from discord_voice_bridge import disconnect_from_voice_channel
            return await disconnect_from_voice_channel()
        except Exception as e:
            logger.error(f"❌ Error disconnecting via JS voice helper: {e}")
            return False

    async def _play_js_audio(self, audio_path):
        """Play audio using JavaScript helper"""
        try:
            from discord_voice_bridge import play_audio_in_voice
            return await play_audio_in_voice(audio_path)
        except Exception as e:
            logger.error(f"❌ Error playing audio via JS voice helper: {e}")
            return False

    async def _play_tts_js_voice(self, text: str):
        """Play TTS audio using JavaScript voice helper"""
        try:
            # Check if voice TTS is enabled
            if not self.enable_voice_tts:
                logger.info("🎵 Voice TTS disabled, skipping audio generation")
                return False
            
            # Import Edge TTS functions
            try:
                from edge_tts_integration import edge_tts_manager
                
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
                
                logger.info(f"🎤 Generating Edge TTS with Ava voice for JS voice: {clean_text[:50]}...")
                
                # Use Edge TTS with default settings (normal pitch, no parameter changes)
                audio_file = await edge_tts_manager.generate_speech(clean_text, tts_path)
                if not audio_file or not os.path.exists(audio_file):
                    logger.error("❌ Failed to generate Edge TTS audio")
                    return False
                
                logger.info(f"✅ Edge TTS generated for JS voice: {audio_file}")
                
                # Play audio using JavaScript voice helper
                success = await self._play_js_audio(audio_file)
                
                # Clean up audio file after a short delay
                try:
                    await asyncio.sleep(self.tts_cleanup_delay)
                    if os.path.exists(audio_file):
                        os.remove(audio_file)
                        logger.debug(f"🗑️ Cleaned up TTS file: {audio_file}")
                except Exception as cleanup_error:
                    logger.warning(f"⚠️ Could not clean up TTS file: {cleanup_error}")
                
                return success
                
            except ImportError as import_error:
                logger.error(f"❌ Edge TTS not available: {import_error}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error playing TTS via JS voice helper: {e}")
            return False

    async def stop_bot(self):
        """Stop the Discord bot"""
        if self.bot:
            # Stop voice keepalive monitoring
            await self._stop_voice_keepalive()
            
            # Stop JavaScript voice helper
            if self.use_js_voice_helper:
                await self._stop_js_voice_helper()
            
            # Disconnect from voice if connected
            if self.voice_client and self.voice_client.is_connected():
                try:
                    await self.voice_client.disconnect()
                    logger.info("👋 Disconnected from voice channel on shutdown")
                except Exception as e:
                    logger.error(f"❌ Error disconnecting from voice on shutdown: {e}")
            
            await self.bot.close()
            self.is_connected = False
            logger.info("🤖 Discord bot stopped")

# Global bot instance
luna_discord_bot = None

async def start_discord_bot(token: str, luna_ai_callback=None, config=None, ui_callback=None):
    """Start the Discord bot"""
    global luna_discord_bot
    
    if luna_discord_bot:
        logger.warning("⚠️ Discord bot already running")
        return luna_discord_bot
    
    luna_discord_bot = LunaDiscordBot(token, luna_ai_callback, config, ui_callback)
    
    try:
        await luna_discord_bot.start_bot()
    except Exception as e:
        logger.error(f"❌ Failed to start Discord bot: {e}")
        luna_discord_bot = None
        raise
    
    return luna_discord_bot

async def stop_discord_bot():
    """Stop the Discord bot"""
    global luna_discord_bot
    
    if luna_discord_bot:
        await luna_discord_bot.stop_bot()
        luna_discord_bot = None
        logger.info("🤖 Discord bot stopped")

def get_discord_bot():
    """Get the current Discord bot instance"""
    return luna_discord_bot

async def send_to_discord_channel(channel_id: int, message: str):
    """Send a message to a Discord channel from Luna's UI"""
    global luna_discord_bot
    
    if luna_discord_bot and luna_discord_bot.is_connected:
        return await luna_discord_bot.send_message_to_discord_channel(channel_id, message)
    else:
        logger.error("❌ Discord bot not connected")
        return False

async def play_tts_in_discord_voice(text: str):
    """Play TTS audio in Discord voice channel from Luna's UI"""
    global luna_discord_bot
    
    if luna_discord_bot and luna_discord_bot.is_connected:
        return await luna_discord_bot.play_tts_in_voice(text)
    else:
        logger.error("❌ Discord bot not connected or not in voice channel")
        return False

# Bot interaction commands (standalone functions)
@commands.command(name='luna_bots')
async def luna_bots_command(ctx):
    """List Discord bots that Luna can interact with"""
    try:
        # Get all bots in the server
        bots = [member for member in ctx.guild.members if member.bot]
        
        if not bots:
            await ctx.send("🤖 No other bots found in this server.")
            return
        
        embed = discord.Embed(
            title="🤖 Discord Bots in Server",
            description="Bots that Luna can potentially interact with:",
            color=0x00ff00
        )
        
        for bot in bots:
            status = "🟢 Active" if bot.status == discord.Status.online else "🔴 Offline"
            embed.add_field(
                name=f"{bot.display_name}",
                value=f"ID: {bot.id}\nStatus: {status}\nLuna can interact: {'Yes' if await should_interact_with_bot_by_name(bot.display_name) else 'No'}",
                inline=True
            )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error listing bots: {e}")

@commands.command(name='luna_bot_status')
async def luna_bot_status_command(ctx):
    """Check Luna's bot interaction status"""
    embed = discord.Embed(
        title="🤖 Luna Bot Interaction Status",
        description="Current bot interaction settings:",
        color=0x00ff00
    )
    
    embed.add_field(
        name="Bot Recognition",
        value="✅ Enabled - Luna can recognize other Discord bots",
        inline=False
    )
    
    embed.add_field(
        name="Interaction Criteria",
        value="• **Approved bots only**: Connor APP, RoomMate APP, Solen APP\n• **Excluded**: Luna's own bot (prevents loops)\n• **Keywords**: luna, hello, hi, hey, talk, chat",
        inline=False
    )
    
    embed.add_field(
        name="Response Style",
        value="• Professional AI-to-AI communication\n• Technical and direct responses\n• Acknowledges both systems as AI",
        inline=False
    )
    
    embed.add_field(
        name="Anti-Loop Protection",
        value="• Message tracking: **Enabled**\n• One response per message: **✅**\n• Prevents response loops: **✅**\n• Memory efficient tracking: **✅**",
        inline=False
    )
    
    await ctx.send(embed=embed)

async def should_interact_with_bot_by_name(bot_name):
    """Check if Luna should interact with a bot by name only"""
    # EXCLUDE Luna's own bot to prevent self-response loops
    if "luna" in bot_name.lower() or "luna bot" in bot_name.lower():
        return False
    
    # Only interact with specific approved bots
    approved_bots = [
        "connor app", "connor_app", "connor-app",
        "roommate app", "roommate_app", "roommate-app",
        "solen app", "solen_app", "solen-app"
    ]
    
    bot_name_lower = bot_name.lower()
    for approved_bot in approved_bots:
        if approved_bot in bot_name_lower:
            return True
    return False

# Configuration functions
def load_discord_config() -> Dict[str, Any]:
    """Load Discord configuration from file"""
    config_file = "discord_config.json"
    
    default_config = {
        "bot_token": "",
        "enabled": False,
        "response_cooldown": 2.0,
        "auto_respond": True,
        "respond_to_mentions": True,
        "respond_to_replies": True,
        "respond_to_keywords": True,
        "keyword_response_chance": 0.3
    }
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        except Exception as e:
            logger.error(f"❌ Error loading Discord config: {e}")
    
    return default_config

def save_discord_config(config: Dict[str, Any]):
    """Save Discord configuration to file"""
    config_file = "discord_config.json"
    
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info("✅ Discord config saved")
    except Exception as e:
        logger.error(f"❌ Error saving Discord config: {e}")

if __name__ == "__main__":
    # Test the Discord bot
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python luna_discord.py <bot_token>")
        sys.exit(1)
    
    token = sys.argv[1]
    
    async def test_callback(message):
        return f"Luna received: {message}"
    
    async def main():
        try:
            await start_discord_bot(token, test_callback)
        except KeyboardInterrupt:
            print("\n🛑 Stopping Discord bot...")
            await stop_discord_bot()
    
    asyncio.run(main())
