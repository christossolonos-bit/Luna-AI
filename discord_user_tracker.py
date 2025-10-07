# discord_user_tracker.py
"""
Discord User Tracker for Luna AI
Tracks Discord usernames and helps Luna mention them in responses
"""

import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set

class DiscordUserTracker:
    """Tracks Discord users and their activity for Luna's responses"""
    
    def __init__(self, data_file: str = "discord_users.json"):
        self.data_file = data_file
        self.users: Dict[str, Dict] = {}
        self.active_users: Set[str] = set()
        self.recent_messages: List[Dict] = []
        self.max_recent_messages = 50
        
        # Load existing user data
        self.load_users()
    
    def load_users(self):
        """Load user data from file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.users = json.load(f)
                
                # Fix data types after loading from JSON
                for username, user_data in self.users.items():
                    # Convert channels back to set if it's a list
                    if isinstance(user_data.get("channels"), list):
                        user_data["channels"] = set(user_data["channels"])
                    elif "channels" not in user_data:
                        user_data["channels"] = set()
                    
                    # Convert guilds back to set if it's a list
                    if isinstance(user_data.get("guilds"), list):
                        user_data["guilds"] = set(user_data["guilds"])
                    elif "guilds" not in user_data:
                        user_data["guilds"] = set()
                    
                    # Ensure recent_messages is a list
                    if "recent_messages" not in user_data:
                        user_data["recent_messages"] = []
                    
                    # Ensure total_messages exists (for backward compatibility)
                    if "total_messages" not in user_data:
                        user_data["total_messages"] = user_data.get("message_count", 0)
                    
                    # Ensure message_count exists
                    if "message_count" not in user_data:
                        user_data["message_count"] = 0
                    
                    # Ensure last_activity exists
                    if "last_activity" not in user_data:
                        user_data["last_activity"] = user_data.get("last_seen", time.time())
                
                print(f"📊 Loaded {len(self.users)} Discord users from {self.data_file}")
            else:
                print(f"📊 No existing Discord user data found, starting fresh")
        except Exception as e:
            print(f"❌ Error loading Discord users: {e}")
            self.users = {}
    
    def save_users(self):
        """Save user data to file"""
        try:
            # Convert sets to lists for JSON serialization
            users_to_save = {}
            for username, user_data in self.users.items():
                user_copy = user_data.copy()
                if isinstance(user_copy.get("channels"), set):
                    user_copy["channels"] = list(user_copy["channels"])
                users_to_save[username] = user_copy
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(users_to_save, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Saved {len(self.users)} Discord users to {self.data_file}")
        except Exception as e:
            print(f"❌ Error saving Discord users: {e}")
    
    def track_message(self, username: str, message: str, channel: str, guild: str = "Unknown"):
        """Track a message from a Discord user"""
        current_time = time.time()
        
        # Add to active users
        self.active_users.add(username)
        
        # Update user data
        if username not in self.users:
            self.users[username] = {
                "first_seen": current_time,
                "last_seen": current_time,
                "message_count": 0,
                "channels": set(),
                "guilds": set(),
                "recent_messages": [],
                "total_messages": 0,
                "last_activity": current_time
            }
        
        user_data = self.users[username]
        user_data["last_seen"] = current_time
        user_data["message_count"] += 1
        user_data["total_messages"] += 1
        user_data["channels"].add(channel)
        user_data["guilds"].add(guild)
        user_data["last_activity"] = current_time
        
        # Add to recent messages (keep last 10 per user)
        user_data["recent_messages"].append({
            "message": message,
            "channel": channel,
            "guild": guild,
            "timestamp": current_time
        })
        
        # Keep only last 10 messages per user
        if len(user_data["recent_messages"]) > 10:
            user_data["recent_messages"] = user_data["recent_messages"][-10:]
        
        # Add to global recent messages
        self.recent_messages.append({
            "username": username,
            "message": message,
            "channel": channel,
            "guild": guild,
            "timestamp": current_time
        })
        
        # Keep only last 50 global messages
        if len(self.recent_messages) > self.max_recent_messages:
            self.recent_messages = self.recent_messages[-self.max_recent_messages:]
        
        # Save periodically (every 10 messages)
        if user_data["message_count"] % 10 == 0:
            self.save_users()
    
    def get_user_context(self, username: str) -> str:
        """Get context about a Discord user"""
        if username not in self.users:
            return f"New Discord user {username}"
        
        user_data = self.users[username]
        current_time = time.time()
        
        # Calculate time since last seen
        time_since_last = current_time - user_data["last_seen"]
        if time_since_last < 60:
            last_seen = "just now"
        elif time_since_last < 3600:
            last_seen = f"{int(time_since_last/60)} minutes ago"
        elif time_since_last < 86400:
            last_seen = f"{int(time_since_last/3600)} hours ago"
        else:
            last_seen = f"{int(time_since_last/86400)} days ago"
        
        # Get channel info
        channels = list(user_data["channels"])
        channel_info = f"active in {', '.join(channels)}" if channels else "no recent channels"
        
        # Get recent message context
        recent_messages = user_data["recent_messages"][-3:] if user_data["recent_messages"] else []
        recent_context = ""
        if recent_messages:
            recent_topics = [msg["message"][:50] for msg in recent_messages]
            recent_context = f"Recently talked about: {', '.join(recent_topics)}"
        
        return f"Discord user {username} ({user_data['total_messages']} total messages, last seen {last_seen}, {channel_info}). {recent_context}"
    
    def get_chat_context(self) -> str:
        """Get context about recent Discord chat activity"""
        if not self.recent_messages:
            return "No recent Discord activity"
        
        # Get last 5 messages
        recent = self.recent_messages[-5:]
        context_parts = []
        
        for msg in recent:
            time_ago = time.time() - msg["timestamp"]
            if time_ago < 60:
                time_str = "just now"
            elif time_ago < 3600:
                time_str = f"{int(time_ago/60)}m ago"
            else:
                time_str = f"{int(time_ago/3600)}h ago"
            
            context_parts.append(f"{msg['username']} ({time_str}): {msg['message'][:30]}...")
        
        return "Recent Discord chat: " + " | ".join(context_parts)
    
    def get_recent_users(self, count: int = 5) -> List[str]:
        """Get list of recently active Discord users"""
        if not self.recent_messages:
            return []
        
        # Get unique users from recent messages
        recent_users = []
        seen_users = set()
        
        for msg in reversed(self.recent_messages):
            if msg["username"] not in seen_users:
                recent_users.append(msg["username"])
                seen_users.add(msg["username"])
                if len(recent_users) >= count:
                    break
        
        return recent_users
    
    def get_mention_suggestions(self, username: str) -> List[str]:
        """Get natural mention suggestions for a Discord user"""
        if username not in self.users:
            return [f"Hey {username}!", f"Hi {username}!", f"{username}!"]
        
        user_data = self.users[username]
        message_count = user_data["total_messages"]
        
        # Different mention styles based on user activity
        if message_count == 1:
            return [f"Hey {username}!", f"Hi there {username}!", f"Welcome {username}!"]
        elif message_count < 5:
            return [f"Hey {username}!", f"Hi {username}!", f"{username}!"]
        elif message_count < 20:
            return [f"Hey {username}!", f"{username}!", f"Yo {username}!"]
        else:
            return [f"{username}!", f"Hey {username}!", f"Yo {username}!"]
    
    def get_user_stats(self) -> Dict:
        """Get overall Discord user statistics"""
        total_users = len(self.users)
        active_users = len(self.active_users)
        total_messages = sum(user["total_messages"] for user in self.users.values())
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "total_messages": total_messages,
            "recent_messages": len(self.recent_messages)
        }
    
    def cleanup_old_data(self, days: int = 30):
        """Clean up old user data"""
        current_time = time.time()
        cutoff_time = current_time - (days * 24 * 3600)
        
        # Remove old recent messages
        self.recent_messages = [
            msg for msg in self.recent_messages 
            if msg["timestamp"] > cutoff_time
        ]
        
        # Clean up user recent messages
        for username, user_data in self.users.items():
            user_data["recent_messages"] = [
                msg for msg in user_data["recent_messages"]
                if msg["timestamp"] > cutoff_time
            ]
        
        print(f"🧹 Cleaned up Discord data older than {days} days")

# Global instance
discord_user_tracker = DiscordUserTracker()

# Convenience functions
def track_discord_message(username: str, message: str, channel: str, guild: str = "Unknown"):
    """Track a Discord message"""
    discord_user_tracker.track_message(username, message, channel, guild)

def get_discord_user_context(username: str) -> str:
    """Get Discord user context"""
    return discord_user_tracker.get_user_context(username)

def get_discord_chat_context() -> str:
    """Get Discord chat context"""
    return discord_user_tracker.get_chat_context()

def get_recent_discord_users(count: int = 5) -> List[str]:
    """Get recent Discord users"""
    return discord_user_tracker.get_recent_users(count)

def get_discord_mention_suggestions(username: str) -> List[str]:
    """Get Discord mention suggestions"""
    return discord_user_tracker.get_mention_suggestions(username)

def get_discord_user_stats() -> Dict:
    """Get Discord user statistics"""
    return discord_user_tracker.get_user_stats()
