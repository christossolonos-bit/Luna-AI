# twitch_chat.py
"""
Twitch chat integration for Luna AI
Allows Luna to connect to Twitch chat and respond to viewer messages
"""

import asyncio
import threading
import time
import re
from typing import Optional, Callable, Dict, Any
from datetime import datetime

try:
    import twitchio
    from twitchio.ext import commands
    from twitchio.ext import routines
    TWITCHIO_AVAILABLE = True
    print("✅ TwitchIO available for chat integration")
except ImportError:
    TWITCHIO_AVAILABLE = False
    print("⚠️ TwitchIO not available. Install with: pip install twitchio")

class TwitchChatBot(commands.Bot):
    """Twitch chat bot for Luna AI"""
    
    def __init__(self, token: str, client_id: str, nick: str, prefix: str = "!", 
                 initial_channels: list = None, callback: Callable = None):
        """
        Initialize Twitch chat bot
        
        Args:
            token: OAuth token for Twitch
            client_id: Twitch client ID
            nick: Bot nickname
            prefix: Command prefix
            initial_channels: List of channels to join
            callback: Callback function for chat messages
        """
        super().__init__(token=token, client_id=client_id, nick=nick, prefix=prefix, 
                        initial_channels=initial_channels or [])
        
        self.callback = callback
        self.is_connected = False
        self.chat_enabled = True
        self.message_count = 0
        self.last_message_time = 0
        self.rate_limit_delay = 1.0  # Minimum delay between responses
        
        # Message filtering
        self.ignored_users = set()
        self.ignored_words = {"bot", "automated", "script"}
        
        # Chat statistics
        self.stats = {
            "messages_received": 0,
            "messages_responded": 0,
            "commands_used": 0,
            "start_time": time.time()
        }
        
        print(f"🎮 Twitch bot initialized for channels: {initial_channels}")
    
    async def event_ready(self):
        """Called when bot is ready"""
        self.is_connected = True
        print(f"✅ Connected to Twitch as {self.nick}")
        print(f"🎮 Joined channels: {[channel.name for channel in self.connected_channels]}")
        
        # Start periodic tasks
        self.update_stream_title.start()
        self.chat_stats.start()
    
    async def event_message(self, message):
        """Handle incoming chat messages"""
        # Add comprehensive null checks for message structure
        if not message:
            print(f"🎮 No message received")
            return
            
        if not hasattr(message, 'author') or not message.author:
            print(f"🎮 Message missing author: {type(message)}")
            return
            
        if not hasattr(message, 'content') or not message.content:
            print(f"🎮 Message has no content: {type(message)}")
            return
            
        # Additional validation for message object
        try:
            # Test if we can access basic properties
            author_name = getattr(message.author, 'name', None)
            content = getattr(message, 'content', None)
            
            if not author_name or not content:
                print(f"🎮 Message missing required fields: author={author_name}, content={bool(content)}")
                return
                
        except Exception as validation_error:
            print(f"🎮 Message validation error: {validation_error}")
            return
            
        print(f"🎮 Raw Twitch message received: {message.author.name}: {message.content}")
        
        if not self.chat_enabled:
            print(f"🎮 Chat disabled, ignoring message from {message.author.name}")
            return
            
        # Ignore bot's own messages
        if message.author.name.lower() == self.nick.lower():
            print(f"🎮 Ignoring bot's own message: {message.content}")
            return
            
        # Basic message filtering
        if self._should_ignore_message(message):
            print(f"🎮 Message filtered out: {message.content}")
            return
            
        self.stats["messages_received"] += 1
        print(f"🎮 Message passed filtering, processing: {message.content}")
        
        # Check rate limiting
        current_time = time.time()
        if current_time - self.last_message_time < self.rate_limit_delay:
            print(f"🎮 Rate limited, ignoring message")
            return
            
        # Process message
        await self._process_chat_message(message)
    
    def _should_ignore_message(self, message) -> bool:
        """Check if message should be ignored"""
        # Ignore specific users
        if message.author.name.lower() in self.ignored_users:
            return True
            
        # Ignore messages with ignored words
        message_lower = message.content.lower()
        if any(word in message_lower for word in self.ignored_words):
            return True
            
        # Ignore very short or very long messages
        if len(message.content) < 2 or len(message.content) > 200:
            return True
            
        return False
    
    async def _process_chat_message(self, message):
        """Process a chat message and generate response"""
        try:
            # Extract message info with null checks
            if not message.author or not hasattr(message.author, 'name'):
                print(f"🎮 Invalid message author: {message}")
                return
                
            if not hasattr(message, 'content') or not message.content:
                print(f"🎮 Invalid message content: {message}")
                return
                
            if not hasattr(message, 'channel') or not message.channel or not hasattr(message.channel, 'name'):
                print(f"🎮 Invalid message channel: {message}")
                return
                
            username = message.author.name
            content = message.content
            channel = message.channel.name
            
            print(f"💬 [{channel}] {username}: {content}")
            
            # Check if it's a question or mention
            is_question = "?" in content
            mentions_luna = any(word in content.lower() for word in ["luna", "ai", "bot"])
            
            # Respond to ALL messages (removed filtering)
            should_respond = True
            
            print(f"🎮 Responding to all messages: {should_respond}")
            
            if should_respond:
                print(f"🎮 Calling callback function for response...")
                # Call the callback function to generate response
                if self.callback:
                    response = await self.callback(username, content, channel)
                    if response:
                        print(f"🎮 Sending response to Twitch: {response}")
                        await self._send_response(channel, response)
                        self.stats["messages_responded"] += 1
                        self.last_message_time = time.time()
                    else:
                        print(f"🎮 No response generated from callback")
                else:
                    print(f"🎮 No callback function available")
            else:
                print(f"🎮 Not responding to this message")
            
        except Exception as e:
            print(f"❌ Error processing chat message: {e}")
    
    def _is_greeting(self, content: str) -> bool:
        """Check if message is a greeting"""
        greetings = ["hello", "hi", "hey", "sup", "yo", "greetings", "good morning", "good evening"]
        content_lower = content.lower()
        return any(greeting in content_lower for greeting in greetings)
    
    def _is_interesting_message(self, content: str) -> bool:
        """Check if message is interesting enough to respond to"""
        # Look for emotional words, questions, or engaging content
        interesting_words = [
            "love", "hate", "amazing", "wow", "cool", "awesome", "sad", "happy",
            "why", "how", "what", "when", "where", "who", "tell", "explain",
            "think", "feel", "believe", "opinion", "idea", "suggestion"
        ]
        content_lower = content.lower()
        return any(word in content_lower for word in interesting_words)
    
    async def _send_response(self, channel: str, response: str):
        """Send a response to chat"""
        try:
            # Truncate response if too long
            if len(response) > 400:
                response = response[:397] + "..."
            
            # Send to channel
            channel_obj = self.get_channel(channel)
            if channel_obj:
                await channel_obj.send(response)
                print(f"🎮 Luna: {response}")
            else:
                print(f"❌ Channel {channel} not found")
                
        except Exception as e:
            print(f"❌ Error sending response: {e}")
    
    @commands.command(name="hello")
    async def hello_command(self, ctx):
        """Respond to !hello command"""
        await ctx.send(f"Hello {ctx.author.name}! 👋")
        self.stats["commands_used"] += 1
    
    @commands.command(name="luna")
    async def luna_command(self, ctx):
        """Respond to !luna command"""
        await ctx.send(f"Hi {ctx.author.name}! I'm Luna, your AI companion! 🌸")
        self.stats["commands_used"] += 1
    
    @commands.command(name="help")
    async def help_command(self, ctx):
        """Show available commands"""
        help_text = "Available commands: !hello, !luna, !help, !stats"
        await ctx.send(help_text)
        self.stats["commands_used"] += 1
    
    @commands.command(name="stats")
    async def stats_command(self, ctx):
        """Show chat statistics"""
        uptime = time.time() - self.stats["start_time"]
        stats_text = f"Chat stats: {self.stats['messages_received']} messages, {self.stats['messages_responded']} responses, {self.stats['commands_used']} commands, {uptime:.0f}s uptime"
        await ctx.send(stats_text)
        self.stats["commands_used"] += 1
    
    @routines.routine(minutes=5)
    async def update_stream_title(self):
        """Periodic task to update stream title"""
        try:
            # This could be used to update stream title or other periodic tasks
            pass
        except Exception as e:
            print(f"❌ Error in update_stream_title: {e}")
    
    @routines.routine(minutes=10)
    async def chat_stats(self):
        """Periodic task to log chat statistics"""
        try:
            uptime = time.time() - self.stats["start_time"]
            print(f"📊 Chat stats: {self.stats['messages_received']} messages, {self.stats['messages_responded']} responses, {uptime:.0f}s uptime")
        except Exception as e:
            print(f"❌ Error in chat_stats: {e}")
    
    def enable_chat(self):
        """Enable chat responses"""
        self.chat_enabled = True
        print("✅ Twitch chat enabled")
    
    def disable_chat(self):
        """Disable chat responses"""
        self.chat_enabled = False
        print("⚠️ Twitch chat disabled")
    
    def add_ignored_user(self, username: str):
        """Add user to ignore list"""
        self.ignored_users.add(username.lower())
        print(f"🚫 Added {username} to ignore list")
    
    def remove_ignored_user(self, username: str):
        """Remove user from ignore list"""
        self.ignored_users.discard(username.lower())
        print(f"✅ Removed {username} from ignore list")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get chat statistics"""
        uptime = time.time() - self.stats["start_time"]
        return {
            **self.stats,
            "uptime_seconds": uptime,
            "uptime_formatted": f"{uptime//3600:.0f}h {(uptime%3600)//60:.0f}m",
            "is_connected": self.is_connected,
            "chat_enabled": self.chat_enabled,
            "connected_channels": [channel.name for channel in self.connected_channels]
        }

class TwitchChatManager:
    """Manager for Twitch chat integration"""
    
    def __init__(self):
        self.bot = None
        self.is_initialized = False
        self.config = {}
        
    def initialize(self, token: str, client_id: str, nick: str, 
                  channels: list, callback: Callable = None) -> bool:
        """Initialize Twitch chat bot"""
        if not TWITCHIO_AVAILABLE:
            print("❌ TwitchIO not available")
            return False
            
        try:
            self.config = {
                "token": token,
                "client_id": client_id,
                "nick": nick,
                "channels": channels
            }
            
            self.bot = TwitchChatBot(
                token=token,
                client_id=client_id,
                nick=nick,
                initial_channels=channels,
                callback=callback
            )
            
            self.is_initialized = True
            print(f"✅ Twitch chat manager initialized for channels: {channels}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize Twitch chat: {e}")
            return False
    
    def start(self):
        """Start the Twitch chat bot"""
        if not self.is_initialized or not self.bot:
            print("❌ Twitch chat not initialized")
            return False
            
        try:
            # Start bot in a separate thread with proper event loop
            def run_bot():
                try:
                    # Create new event loop for this thread
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(self.bot.run())
                    finally:
                        loop.close()
                except Exception as e:
                    print(f"❌ Twitch bot thread error: {e}")
            
            bot_thread = threading.Thread(target=run_bot, daemon=True)
            bot_thread.start()
            
            print("🎮 Twitch chat bot started")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start Twitch chat: {e}")
            return False
    
    def stop(self):
        """Stop the Twitch chat bot"""
        if self.bot:
            try:
                # Stop the bot gracefully
                if hasattr(self.bot, '_closing') and self.bot._closing:
                    self.bot._closing.set()
                print("🎮 Twitch chat bot stopped")
            except Exception as e:
                print(f"❌ Error stopping Twitch chat: {e}")
    
    def send_message(self, channel: str, message: str):
        """Send a message to a specific channel"""
        if not self.bot or not self.bot.is_connected:
            print("❌ Twitch bot not connected")
            return False
            
        try:
            asyncio.create_task(self.bot._send_response(channel, message))
            return True
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get Twitch chat statistics"""
        if not self.bot:
            return {"error": "Bot not initialized"}
        return self.bot.get_stats()
    
    def enable_chat(self):
        """Enable chat responses"""
        if self.bot:
            self.bot.enable_chat()
    
    def disable_chat(self):
        """Disable chat responses"""
        if self.bot:
            self.bot.disable_chat()
    
    def is_connected(self) -> bool:
        """Check if bot is connected"""
        return self.bot and self.bot.is_connected if self.bot else False

# Global Twitch chat manager instance
twitch_manager = TwitchChatManager()

# Convenience functions
def initialize_twitch_chat(token: str, client_id: str, nick: str, 
                          channels: list, callback: Callable = None) -> bool:
    """Initialize Twitch chat integration"""
    return twitch_manager.initialize(token, client_id, nick, channels, callback)

def start_twitch_chat() -> bool:
    """Start Twitch chat bot"""
    return twitch_manager.start()

def stop_twitch_chat():
    """Stop Twitch chat bot"""
    twitch_manager.stop()

def send_twitch_message(channel: str, message: str) -> bool:
    """Send message to Twitch chat"""
    return twitch_manager.send_message(channel, message)

def get_twitch_stats() -> Dict[str, Any]:
    """Get Twitch chat statistics"""
    return twitch_manager.get_stats()

def enable_twitch_chat():
    """Enable Twitch chat responses"""
    twitch_manager.enable_chat()

def disable_twitch_chat():
    """Disable Twitch chat responses"""
    twitch_manager.disable_chat()

def is_twitch_connected() -> bool:
    """Check if Twitch chat is connected"""
    return twitch_manager.is_connected()

if __name__ == "__main__":
    # Example usage
    print("🎮 Twitch Chat Integration Test")
    print("=" * 40)
    
    if not TWITCHIO_AVAILABLE:
        print("❌ TwitchIO not available!")
        print("Install with: pip install twitchio")
        exit(1)
    
    # Example configuration (you'll need to get these from Twitch)
    TOKEN = "your_oauth_token_here"
    CLIENT_ID = "your_client_id_here"
    NICK = "LunaAI"
    CHANNELS = ["your_channel_name"]
    
    print("📋 Setup Instructions:")
    print("1. Get OAuth token from: https://twitchapps.com/tmi/")
    print("2. Get Client ID from: https://dev.twitch.tv/console")
    print("3. Update the configuration variables above")
    print("4. Run the bot")
    
    # Example callback function
    async def chat_callback(username: str, message: str, channel: str) -> str:
        """Example callback for chat messages"""
        if "hello" in message.lower():
            return f"Hello {username}! 👋"
        elif "?" in message:
            return f"Great question {username}! Let me think about that..."
        else:
            return f"Thanks for the message {username}! 💕"
    
    # Initialize and start (uncomment when configured)
    # if initialize_twitch_chat(TOKEN, CLIENT_ID, NICK, CHANNELS, chat_callback):
    #     start_twitch_chat()
    #     print("🎮 Twitch chat bot running... Press Ctrl+C to stop")
    #     try:
    #         while True:
    #             time.sleep(1)
    #     except KeyboardInterrupt:
    #         stop_twitch_chat()
    #         print("🎮 Twitch chat bot stopped")
