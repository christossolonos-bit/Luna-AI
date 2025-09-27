# twitch_user_tracker.py
"""
Twitch User Tracker for Luna AI
Tracks Twitch usernames and helps Luna mention them in responses
"""

import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set

class TwitchUserTracker:
    """Tracks Twitch users and their activity for Luna's responses"""
    
    def __init__(self, data_file: str = "twitch_users.json"):
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
                    
                    # Ensure recent_messages is a list
                    if "recent_messages" not in user_data:
                        user_data["recent_messages"] = []
                
                print(f"📊 Loaded {len(self.users)} Twitch users from {self.data_file}")
            else:
                print(f"📊 No existing user data found, starting fresh")
        except Exception as e:
            print(f"❌ Error loading Twitch users: {e}")
            self.users = {}
    
    def save_users(self):
        """Save user data to file"""
        try:
            # Convert sets to lists for JSON serialization
            users_to_save = {}
            for username, user_data in self.users.items():
                user_copy = user_data.copy()
                # Convert channels set to list for JSON
                if isinstance(user_copy.get("channels"), set):
                    user_copy["channels"] = list(user_copy["channels"])
                users_to_save[username] = user_copy
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(users_to_save, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Error saving Twitch users: {e}")
    
    def add_message(self, username: str, message: str, channel: str = "default"):
        """Add a new message from a user"""
        current_time = time.time()
        
        # Update user data
        if username not in self.users:
            self.users[username] = {
                "username": username,
                "first_seen": current_time,
                "last_seen": current_time,
                "message_count": 0,
                "channels": set(),
                "recent_messages": [],
                "favorite_topics": [],
                "interaction_count": 0
            }
        
        # Update user stats
        user_data = self.users[username]
        user_data["last_seen"] = current_time
        user_data["message_count"] += 1
        user_data["channels"].add(channel)
        user_data["interaction_count"] += 1
        
        # Keep recent messages (last 10)
        user_data["recent_messages"].append({
            "message": message,
            "timestamp": current_time,
            "channel": channel
        })
        user_data["recent_messages"] = user_data["recent_messages"][-10:]
        
        # Add to active users
        self.active_users.add(username)
        
        # Add to recent messages
        self.recent_messages.append({
            "username": username,
            "message": message,
            "channel": channel,
            "timestamp": current_time
        })
        
        # Keep only recent messages
        self.recent_messages = self.recent_messages[-self.max_recent_messages:]
        
        # Save periodically
        if user_data["message_count"] % 10 == 0:
            self.save_users()
    
    def get_user_info(self, username: str) -> Optional[Dict]:
        """Get information about a specific user"""
        return self.users.get(username)
    
    def get_active_users(self, minutes: int = 30) -> List[str]:
        """Get users active in the last N minutes"""
        cutoff_time = time.time() - (minutes * 60)
        active = []
        
        for username, user_data in self.users.items():
            if user_data["last_seen"] > cutoff_time:
                active.append(username)
        
        return active
    
    def get_recent_users(self, count: int = 5) -> List[str]:
        """Get the most recent users"""
        sorted_users = sorted(
            self.users.items(), 
            key=lambda x: x[1]["last_seen"], 
            reverse=True
        )
        return [username for username, _ in sorted_users[:count]]
    
    def get_frequent_users(self, count: int = 5) -> List[str]:
        """Get the most frequent users"""
        sorted_users = sorted(
            self.users.items(), 
            key=lambda x: x[1]["message_count"], 
            reverse=True
        )
        return [username for username, _ in sorted_users[:count]]
    
    def get_user_context(self, username: str) -> str:
        """Get context about a user for Luna's responses"""
        user_data = self.users.get(username)
        if not user_data:
            return f"a new viewer named {username}"
        
        # Calculate time since first seen
        first_seen = datetime.fromtimestamp(user_data["first_seen"])
        days_known = (datetime.now() - first_seen).days
        
        # Build context
        context_parts = []
        
        if days_known > 0:
            context_parts.append(f"been here for {days_known} day{'s' if days_known != 1 else ''}")
        
        if user_data["message_count"] > 1:
            context_parts.append(f"sent {user_data['message_count']} messages")
        
        if user_data["message_count"] > 10:
            context_parts.append("regular viewer")
        
        if user_data["message_count"] > 50:
            context_parts.append("very active in chat")
        
        # Get recent message context
        if user_data["recent_messages"]:
            recent_msg = user_data["recent_messages"][-1]["message"]
            if len(recent_msg) < 50:  # Only include short messages
                context_parts.append(f"just said '{recent_msg}'")
        
        if context_parts:
            return f"{username} ({', '.join(context_parts)})"
        else:
            return username
    
    def get_chat_context(self) -> str:
        """Get overall chat context for Luna"""
        active_users = self.get_active_users(10)  # Last 10 minutes
        recent_users = self.get_recent_users(3)   # Last 3 users
        
        context_parts = []
        
        if active_users:
            context_parts.append(f"{len(active_users)} active viewers")
        
        if recent_users:
            context_parts.append(f"recent messages from {', '.join(recent_users)}")
        
        if self.recent_messages:
            total_messages = len(self.recent_messages)
            context_parts.append(f"{total_messages} recent messages")
        
        if context_parts:
            return f"Chat context: {', '.join(context_parts)}"
        else:
            return "Chat context: Quiet chat"
    
    def get_mention_suggestions(self, username: str) -> List[str]:
        """Get suggestions for how Luna should mention a user"""
        user_data = self.users.get(username)
        if not user_data:
            return [f"Hey {username}!", f"Thanks {username}!", f"Welcome {username}!"]
        
        suggestions = []
        
        # Based on message count
        if user_data["message_count"] == 1:
            suggestions.extend([
                f"Welcome {username}!",
                f"Thanks for joining us {username}!",
                f"Hey {username}, glad you're here!"
            ])
        elif user_data["message_count"] < 5:
            suggestions.extend([
                f"Hey {username}!",
                f"Thanks {username}!",
                f"Good to see you {username}!"
            ])
        elif user_data["message_count"] < 20:
            suggestions.extend([
                f"Hey {username}!",
                f"Thanks {username}!",
                f"Always good to hear from you {username}!"
            ])
        else:
            suggestions.extend([
                f"Hey {username}!",
                f"Thanks {username}!",
                f"Great to see you {username}!",
                f"You're always so supportive {username}!"
            ])
        
        # Based on recent activity
        if user_data["last_seen"] > time.time() - 300:  # Active in last 5 minutes
            suggestions.append(f"Thanks for being so active {username}!")
        
        return suggestions
    
    def cleanup_old_data(self, days: int = 30):
        """Clean up old user data"""
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        old_users = []
        
        for username, user_data in self.users.items():
            if user_data["last_seen"] < cutoff_time:
                old_users.append(username)
        
        for username in old_users:
            del self.users[username]
        
        if old_users:
            print(f"🧹 Cleaned up {len(old_users)} old users")
            self.save_users()

# Global tracker instance
twitch_tracker = TwitchUserTracker()

# Convenience functions
def track_twitch_message(username: str, message: str, channel: str = "default"):
    """Track a Twitch message"""
    twitch_tracker.add_message(username, message, channel)

def get_twitch_user_context(username: str) -> str:
    """Get context about a Twitch user"""
    return twitch_tracker.get_user_context(username)

def get_twitch_chat_context() -> str:
    """Get overall Twitch chat context"""
    return twitch_tracker.get_chat_context()

def get_twitch_mention_suggestions(username: str) -> List[str]:
    """Get suggestions for mentioning a Twitch user"""
    return twitch_tracker.get_mention_suggestions(username)

def get_recent_twitch_users(count: int = 5) -> List[str]:
    """Get recent Twitch users"""
    return twitch_tracker.get_recent_users(count)

def get_active_twitch_users(minutes: int = 30) -> List[str]:
    """Get active Twitch users"""
    return twitch_tracker.get_active_users(minutes)
