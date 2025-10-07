# twitch_api_chat.py
"""
Twitch API integration for Luna AI using direct HTTP requests
Allows Luna to connect to Twitch chat and respond to viewer messages via Twitch API
"""

import asyncio
import threading
import time
import re
import requests
import websocket
import json
import logging
from typing import Optional, Callable, Dict, Any, List
from datetime import datetime
from urllib.parse import quote

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TwitchAPIChat:
    """Twitch chat integration using direct API calls"""
    
    def __init__(self, token: str, client_id: str, nick: str, channels: list = None, callback: Callable = None):
        """
        Initialize Twitch API chat
        
        Args:
            token: OAuth token for Twitch (with chat:read, chat:edit scopes)
            client_id: Twitch client ID
            nick: Bot nickname
            channels: List of channels to join
            callback: Callback function for chat messages
        """
        self.token = token.replace('oauth:', '') if token.startswith('oauth:') else token
        self.client_id = client_id
        self.nick = nick
        self.channels = channels or []
        self.callback = callback
        
        self.is_connected = False
        self.chat_enabled = True
        self.message_count = 0
        self.last_message_time = 0
        self.rate_limit_delay = 1.0  # Minimum delay between responses
        
        # WebSocket connection
        self.ws = None
        self.ws_thread = None
        self.running = False
        
        # Message filtering
        self.ignored_users = set()
        self.ignored_words = {
            "nigga", "nigger", "n1gga", "n1gger", "n!gga", "n!gger", 
            "n1gg3r", "nigg3r", "n!gg3r", "nigg@", "n!gg@", "n1gg@"
        }
        
        # Chat statistics
        self.stats = {
            "messages_received": 0,
            "messages_responded": 0,
            "commands_used": 0,
            "start_time": time.time()
        }
        
        # Rate limiting
        self.message_queue = []
        self.last_send_time = 0
        
        print(f"Twitch API chat initialized for channels: {self.channels}")
    
    def get_user_id(self, username: str) -> Optional[str]:
        """Get user ID from username using Twitch API"""
        try:
            headers = {
                'Client-ID': self.client_id,
                'Authorization': f'Bearer {self.token}'
            }
            
            url = f"https://api.twitch.tv/helix/users?login={username}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('data'):
                    return data['data'][0]['id']
            
            logger.warning(f"Could not get user ID for {username}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting user ID for {username}: {e}")
            return None
    
    def send_message(self, channel: str, message: str) -> bool:
        """Send a message to Twitch chat via IRC WebSocket"""
        try:
            # Rate limiting
            current_time = time.time()
            if current_time - self.last_send_time < self.rate_limit_delay:
                time.sleep(self.rate_limit_delay - (current_time - self.last_send_time))
            
            # Use IRC WebSocket to send message (same connection we use for reading)
            if self.ws and self.is_connected:
                # Truncate message if too long for Twitch (500 char limit)
                if len(message) > 500:
                    message = message[:497] + "..."
                
                # Send via IRC WebSocket
                irc_message = f"PRIVMSG #{channel} :{message}"
                self.ws.send(irc_message)
                
                self.stats["messages_responded"] += 1
                self.last_send_time = current_time
                print(f"Sent to {channel}: {message}")
                return True
            else:
                logger.error(f"WebSocket not connected - cannot send message to {channel}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending message to {channel}: {e}")
            return False
    
    def connect_websocket(self):
        """Connect to Twitch IRC WebSocket for real-time chat"""
        try:
            # Twitch IRC WebSocket URL
            ws_url = "wss://irc-ws.chat.twitch.tv:443"
            
            def on_message(ws, message):
                self._handle_irc_message(message)
            
            def on_error(ws, error):
                print(f"❌ Twitch WebSocket error: {error}")
                logger.error(f"WebSocket error: {error}")
            
            def on_close(ws, close_status_code, close_msg):
                print(f"⚠️ Twitch WebSocket closed (code: {close_status_code}, msg: {close_msg})")
                logger.info("WebSocket connection closed")
                self.is_connected = False
                
                # Auto-reconnect if still running
                if self.running:
                    print("🔄 Attempting to reconnect to Twitch in 5 seconds...")
                    time.sleep(5)
                    if self.running:
                        print("🔄 Reconnecting to Twitch...")
                        self.connect_websocket()
            
            def on_open(ws):
                print("✅ Twitch WebSocket connection opened!")
                logger.info("WebSocket connection opened")
                # Send authentication
                print(f"🔑 Authenticating as {self.nick}...")
                ws.send(f"PASS oauth:{self.token}")
                ws.send(f"NICK {self.nick}")
                
                # Request capabilities for tags (to get display-name)
                ws.send("CAP REQ :twitch.tv/tags twitch.tv/commands")
                print("📋 Requested Twitch IRC capabilities (tags + commands)")
                
                # Join channels
                for channel in self.channels:
                    ws.send(f"JOIN #{channel}")
                    print(f"✅ Joined Twitch channel: #{channel}")
                    logger.info(f"Joined channel: #{channel}")
                
                self.is_connected = True
                print(f"🎮 Twitch chat is now connected and listening to: {', '.join(self.channels)}")
            
            # Create WebSocket connection
            self.ws = websocket.WebSocketApp(
                ws_url,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
                on_open=on_open
            )
            
            # Run WebSocket in a separate thread
            def run_websocket():
                self.ws.run_forever()
            
            self.ws_thread = threading.Thread(target=run_websocket, daemon=True)
            self.ws_thread.start()
            
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to Twitch WebSocket: {e}")
            return False
    
    def _handle_irc_message(self, message: str):
        """Handle incoming IRC messages"""
        try:
            # Debug: Print raw IRC message
            print(f"🔍 Raw IRC message: {message}")
            
            # Handle PING - critical for keeping connection alive
            if message.startswith("PING"):
                print("🏓 PING received, sending PONG")
                self.ws.send("PONG :tmi.twitch.tv")
                return
            
            # Also handle PING in different format
            if "PING" in message and ":tmi.twitch.tv" in message:
                print("🏓 PING (alternate format) received, sending PONG")
                self.ws.send("PONG :tmi.twitch.tv")
                return
            
            # Check for PRIVMSG (chat message) - can appear anywhere in the message
            if " PRIVMSG " not in message:
                print(f"🔍 Not a PRIVMSG, skipping")
                return
            
            print(f"🔍 PRIVMSG detected in message!")
            
            # Extract display name from tags if available
            username = None
            if message.startswith('@'):
                # Parse tags to get display-name
                tags_end = message.find(' :')
                if tags_end > 0:
                    tags = message[1:tags_end]
                    for tag in tags.split(';'):
                        if tag.startswith('display-name='):
                            username = tag.split('=', 1)[1]
                            break
            
            # Extract channel and message from PRIVMSG format
            # Format: ... PRIVMSG #channel :message
            privmsg_index = message.find(' PRIVMSG ')
            if privmsg_index == -1:
                return
            
            # Get the part after PRIVMSG
            after_privmsg = message[privmsg_index + 9:]  # +9 to skip " PRIVMSG "
            parts = after_privmsg.split(' :', 1)
            
            if len(parts) < 2:
                print(f"🔍 Could not parse channel and message")
                return
            
            channel = parts[0].lstrip('#').strip()
            full_message = parts[1].strip()
            
            # If we didn't get username from tags, try to extract from sender info
            if not username:
                # Look for username in format :username!username@username.tmi.twitch.tv
                sender_match = re.search(r':([^!]+)!', message)
                if sender_match:
                    username = sender_match.group(1)
                else:
                    username = "Unknown"
            
            # Update stats
            self.stats["messages_received"] += 1
            print(f"📨 Received message from {username} in #{channel}: {full_message}")
            
            # Check if message should be ignored
            if self._should_ignore_message(username, full_message):
                print(f"🚫 Ignoring message from {username}: {full_message}")
                return
            
            # Filter offensive words from message
            filtered_message = self._filter_message(full_message)
            if filtered_message != full_message:
                print(f"🔧 Filtered message from {username}: {filtered_message}")
            
            # Call callback if available
            if self.callback and self.chat_enabled:
                try:
                    print(f"🎮 Calling callback for {username}: {filtered_message}")
                    response = self.callback(username, filtered_message, channel)
                    if response:
                        print(f"✅ Got response from callback, sending to channel: {response}")
                        self.send_message(channel, response)
                except Exception as e:
                    logger.error(f"Error in callback: {e}")
            
        except Exception as e:
            logger.error(f"Error handling IRC message: {e}")
    
    def _filter_message(self, message: str) -> str:
        """Filter offensive words from message, replacing with 'Filtered'"""
        filtered_message = message
        message_lower = message.lower()
        
        for word in self.ignored_words:
            if word in message_lower:
                # Replace the word with "Filtered" (case-insensitive)
                import re
                pattern = re.compile(re.escape(word), re.IGNORECASE)
                filtered_message = pattern.sub("Filtered", filtered_message)
        
        return filtered_message
    
    def _should_ignore_message(self, username: str, message: str) -> bool:
        """Check if message should be ignored"""
        # Check ignored users
        if username.lower() in self.ignored_users:
            return True
        
        # Rate limiting - don't respond to too many messages too quickly
        current_time = time.time()
        if current_time - self.last_message_time < 0.5:  # 0.5 second cooldown (more responsive)
            return True
        
        self.last_message_time = current_time
        return False
    
    def validate_token(self) -> bool:
        """Validate OAuth token with Twitch"""
        try:
            headers = {
                'Authorization': f'OAuth {self.token}'
            }
            response = requests.get('https://id.twitch.tv/oauth2/validate', headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Token valid - User: {data.get('login')}, Scopes: {data.get('scopes')}")
                return True
            elif response.status_code == 401:
                print(f"❌ Token is invalid or expired!")
                print(f"💡 You may need to refresh your OAuth token")
                return False
            else:
                print(f"⚠️ Token validation returned status: {response.status_code}")
                return False
        except Exception as e:
            print(f"⚠️ Could not validate token: {e}")
            return False
    
    def start(self) -> bool:
        """Start the Twitch chat connection"""
        if self.running:
            return True
        
        # Validate token before connecting
        print("🔑 Validating OAuth token...")
        if not self.validate_token():
            print("⚠️ Token validation failed, but attempting to connect anyway...")
        
        self.running = True
        
        # Connect to WebSocket
        if self.connect_websocket():
            print("SUCCESS: Twitch API chat started successfully!")
            return True
        else:
            print("FAILED: Failed to start Twitch API chat")
            self.running = False
            return False
    
    def stop(self):
        """Stop the Twitch chat connection"""
        self.running = False
        self.chat_enabled = False
        
        if self.ws:
            self.ws.close()
        
        if self.ws_thread and self.ws_thread.is_alive():
            self.ws_thread.join(timeout=5)
        
        self.is_connected = False
        print("STOPPED: Twitch API chat stopped")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get chat statistics"""
        uptime = time.time() - self.stats["start_time"]
        return {
            **self.stats,
            "uptime_seconds": uptime,
            "is_connected": self.is_connected,
            "channels": self.channels.copy()
        }
    
    def add_ignored_user(self, username: str):
        """Add user to ignored list"""
        self.ignored_users.add(username.lower())
    
    def remove_ignored_user(self, username: str):
        """Remove user from ignored list"""
        self.ignored_users.discard(username.lower())
    
    def add_ignored_word(self, word: str):
        """Add word to ignored list"""
        self.ignored_words.add(word.lower())
    
    def remove_ignored_word(self, word: str):
        """Remove word from ignored list"""
        self.ignored_words.discard(word.lower())

# Global instance
twitch_api_manager = None

def initialize_twitch_api_chat(token: str, client_id: str, nick: str, channels: list = None, callback: Callable = None) -> bool:
    """Initialize Twitch API chat"""
    global twitch_api_manager
    
    try:
        twitch_api_manager = TwitchAPIChat(
            token=token,
            client_id=client_id,
            nick=nick,
            channels=channels or [],
            callback=callback
        )
        return True
    except Exception as e:
        logger.error(f"Error initializing Twitch API chat: {e}")
        return False

def start_twitch_api_chat() -> bool:
    """Start Twitch API chat"""
    global twitch_api_manager
    
    if not twitch_api_manager:
        logger.error("Twitch API chat not initialized")
        return False
    
    return twitch_api_manager.start()

def stop_twitch_api_chat():
    """Stop Twitch API chat"""
    global twitch_api_manager
    
    if twitch_api_manager:
        twitch_api_manager.stop()

def send_twitch_api_message(channel: str, message: str) -> bool:
    """Send message to Twitch chat"""
    global twitch_api_manager
    
    if not twitch_api_manager:
        logger.error("Twitch API chat not initialized")
        return False
    
    return twitch_api_manager.send_message(channel, message)

def is_twitch_api_connected() -> bool:
    """Check if Twitch API chat is connected"""
    global twitch_api_manager
    
    return twitch_api_manager.is_connected if twitch_api_manager else False

def get_twitch_api_stats() -> Dict[str, Any]:
    """Get Twitch API chat statistics"""
    global twitch_api_manager
    
    return twitch_api_manager.get_stats() if twitch_api_manager else {}

def enable_twitch_api_chat():
    """Enable Twitch API chat responses"""
    global twitch_api_manager
    
    if twitch_api_manager:
        twitch_api_manager.chat_enabled = True

def disable_twitch_api_chat():
    """Disable Twitch API chat responses"""
    global twitch_api_manager
    
    if twitch_api_manager:
        twitch_api_manager.chat_enabled = False
