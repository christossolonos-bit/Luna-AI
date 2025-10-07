# twitch_user_tracker_sql.py
"""
Twitch User Tracker for Luna AI with SQL Database
Tracks Twitch usernames and helps Luna mention them in responses
"""

import sqlite3
import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set

class TwitchUserTrackerSQL:
    """Tracks Twitch users and their activity using SQL database"""
    
    def __init__(self, db_path: str = "luna_twitch_users.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQL database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS twitch_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                twitch_id TEXT,
                first_seen REAL NOT NULL,
                last_seen REAL NOT NULL,
                total_messages INTEGER DEFAULT 0,
                is_subscriber BOOLEAN DEFAULT FALSE,
                is_moderator BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS twitch_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                channel TEXT NOT NULL,
                timestamp REAL NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES twitch_users(id)
            )
        ''')
        
        # Channels table (tracks which channels users are active in)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS twitch_user_channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                channel TEXT NOT NULL,
                first_seen REAL NOT NULL,
                last_seen REAL NOT NULL,
                message_count INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES twitch_users(id),
                UNIQUE(user_id, channel)
            )
        ''')
        
        # User topics/interests table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS twitch_user_topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                topic TEXT NOT NULL,
                mention_count INTEGER DEFAULT 1,
                last_mentioned REAL NOT NULL,
                FOREIGN KEY (user_id) REFERENCES twitch_users(id),
                UNIQUE(user_id, topic)
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_twitch_users_username ON twitch_users(username)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_twitch_messages_timestamp ON twitch_messages(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_twitch_messages_user_id ON twitch_messages(user_id)')
        
        conn.commit()
        conn.close()
        print(f"[OK] Twitch SQL database initialized: {self.db_path}")
    
    def track_message(self, username: str, message: str, channel: str = "default", twitch_id: str = None, is_subscriber: bool = False, is_moderator: bool = False):
        """Track a message from a Twitch user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        current_time = time.time()
        
        try:
            # Get or create user
            cursor.execute('SELECT id, total_messages FROM twitch_users WHERE username = ?', (username,))
            result = cursor.fetchone()
            
            if result:
                user_id, total_messages = result
                # Update user stats
                cursor.execute('''
                    UPDATE twitch_users 
                    SET last_seen = ?, 
                        total_messages = total_messages + 1,
                        twitch_id = COALESCE(twitch_id, ?),
                        is_subscriber = ?,
                        is_moderator = ?
                    WHERE id = ?
                ''', (current_time, twitch_id, is_subscriber, is_moderator, user_id))
            else:
                # Create new user
                cursor.execute('''
                    INSERT INTO twitch_users (username, twitch_id, first_seen, last_seen, total_messages, is_subscriber, is_moderator)
                    VALUES (?, ?, ?, ?, 1, ?, ?)
                ''', (username, twitch_id, current_time, current_time, is_subscriber, is_moderator))
                user_id = cursor.lastrowid
            
            # Insert message
            cursor.execute('''
                INSERT INTO twitch_messages (user_id, message, channel, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (user_id, message, channel, current_time))
            
            # Update channel activity
            cursor.execute('''
                INSERT INTO twitch_user_channels (user_id, channel, first_seen, last_seen, message_count)
                VALUES (?, ?, ?, ?, 1)
                ON CONFLICT(user_id, channel) DO UPDATE SET
                    last_seen = excluded.last_seen,
                    message_count = message_count + 1
            ''', (user_id, channel, current_time, current_time))
            
            # Extract and track topics/interests
            self._extract_topics(user_id, message, current_time, cursor)
            
            conn.commit()
            
        except Exception as e:
            print(f"[ERROR] Error tracking Twitch message: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def _extract_topics(self, user_id: int, message: str, timestamp: float, cursor):
        """Extract topics from message and update user interests"""
        message_lower = message.lower()
        topics = []
        
        # Gaming topics
        if any(word in message_lower for word in ['game', 'gaming', 'play', 'valorant', 'league', 'warframe']):
            topics.append('gaming')
        
        # Tech topics
        if any(word in message_lower for word in ['tech', 'computer', 'software', 'hardware', 'pc']):
            topics.append('technology')
        
        # Music topics
        if any(word in message_lower for word in ['music', 'song', 'artist', 'album', 'listen']):
            topics.append('music')
        
        # Entertainment topics
        if any(word in message_lower for word in ['movie', 'show', 'series', 'anime', 'manga']):
            topics.append('entertainment')
        
        # Update topics
        for topic in topics:
            cursor.execute('''
                INSERT INTO twitch_user_topics (user_id, topic, mention_count, last_mentioned)
                VALUES (?, ?, 1, ?)
                ON CONFLICT(user_id, topic) DO UPDATE SET
                    mention_count = mention_count + 1,
                    last_mentioned = excluded.last_mentioned
            ''', (user_id, topic, timestamp))
    
    def get_user_context(self, username: str) -> str:
        """Get context about a Twitch user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT first_seen, last_seen, total_messages, is_subscriber, is_moderator
                FROM twitch_users
                WHERE username = ?
            ''', (username,))
            
            result = cursor.fetchone()
            if not result:
                return f"a new viewer named {username}"
            
            first_seen, last_seen, total_messages, is_subscriber, is_moderator = result
            
            # Calculate time known
            first_seen_dt = datetime.fromtimestamp(first_seen)
            days_known = (datetime.now() - first_seen_dt).days
            
            # Build context
            context_parts = []
            
            if is_moderator:
                context_parts.append("moderator")
            if is_subscriber:
                context_parts.append("subscriber")
            
            if days_known > 0:
                context_parts.append(f"been here for {days_known} day{'s' if days_known != 1 else ''}")
            
            if total_messages > 1:
                context_parts.append(f"sent {total_messages} messages")
            
            if total_messages > 10:
                context_parts.append("regular viewer")
            
            if total_messages > 50:
                context_parts.append("very active in chat")
            
            # Get favorite topics
            cursor.execute('''
                SELECT topic FROM twitch_user_topics
                WHERE user_id = (SELECT id FROM twitch_users WHERE username = ?)
                ORDER BY mention_count DESC LIMIT 2
            ''', (username,))
            
            topics = [row[0] for row in cursor.fetchall()]
            if topics:
                context_parts.append(f"interested in {', '.join(topics)}")
            
            if context_parts:
                return f"{username} ({', '.join(context_parts)})"
            else:
                return username
            
        finally:
            conn.close()
    
    def get_chat_context(self) -> str:
        """Get overall chat context"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Active users (last 10 minutes)
            cutoff = time.time() - 600
            cursor.execute('SELECT COUNT(*) FROM twitch_users WHERE last_seen > ?', (cutoff,))
            active_users = cursor.fetchone()[0]
            
            # Recent users
            cursor.execute('''
                SELECT username FROM twitch_users
                ORDER BY last_seen DESC
                LIMIT 3
            ''')
            recent_users = [row[0] for row in cursor.fetchall()]
            
            # Recent message count
            cursor.execute('SELECT COUNT(*) FROM twitch_messages WHERE timestamp > ?', (cutoff,))
            recent_messages = cursor.fetchone()[0]
            
            context_parts = []
            
            if active_users:
                context_parts.append(f"{active_users} active viewers")
            
            if recent_users:
                context_parts.append(f"recent messages from {', '.join(recent_users)}")
            
            if recent_messages:
                context_parts.append(f"{recent_messages} recent messages")
            
            if context_parts:
                return f"Chat context: {', '.join(context_parts)}"
            else:
                return "Chat context: Quiet chat"
            
        finally:
            conn.close()
    
    def get_recent_users(self, count: int = 5) -> List[str]:
        """Get the most recent users"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT username FROM twitch_users
                ORDER BY last_seen DESC
                LIMIT ?
            ''', (count,))
            
            return [row[0] for row in cursor.fetchall()]
            
        finally:
            conn.close()
    
    def get_user_stats(self) -> Dict:
        """Get overall Twitch user statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Total users
            cursor.execute('SELECT COUNT(*) FROM twitch_users')
            total_users = cursor.fetchone()[0]
            
            # Active users (last 24 hours)
            cutoff = time.time() - 86400
            cursor.execute('SELECT COUNT(*) FROM twitch_users WHERE last_seen > ?', (cutoff,))
            active_users = cursor.fetchone()[0]
            
            # Total messages
            cursor.execute('SELECT SUM(total_messages) FROM twitch_users')
            total_messages = cursor.fetchone()[0] or 0
            
            # Subscribers
            cursor.execute('SELECT COUNT(*) FROM twitch_users WHERE is_subscriber = 1')
            subscribers = cursor.fetchone()[0]
            
            return {
                "total_users": total_users,
                "active_users": active_users,
                "total_messages": total_messages,
                "subscribers": subscribers
            }
            
        finally:
            conn.close()
    
    def get_all_users(self) -> List[Dict]:
        """Get all Twitch users with their stats"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT username, twitch_id, first_seen, last_seen, total_messages, is_subscriber, is_moderator
                FROM twitch_users
                ORDER BY last_seen DESC
            ''')
            
            users = []
            for row in cursor.fetchall():
                username, twitch_id, first_seen, last_seen, total_messages, is_subscriber, is_moderator = row
                
                badges = []
                if is_moderator:
                    badges.append('MOD')
                if is_subscriber:
                    badges.append('SUB')
                
                users.append({
                    'username': username,
                    'twitch_id': twitch_id or 'N/A',
                    'badges': ' '.join(badges) if badges else 'N/A',
                    'first_seen': datetime.fromtimestamp(first_seen).strftime('%Y-%m-%d %H:%M'),
                    'last_seen': datetime.fromtimestamp(last_seen).strftime('%Y-%m-%d %H:%M'),
                    'total_messages': total_messages
                })
            
            return users
            
        finally:
            conn.close()
    
    def cleanup_old_data(self, days: int = 30):
        """Clean up old message data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cutoff_time = time.time() - (days * 24 * 3600)
        
        try:
            cursor.execute('DELETE FROM twitch_messages WHERE timestamp < ?', (cutoff_time,))
            deleted = cursor.rowcount
            conn.commit()
            print(f"[CLEANUP] Cleaned up {deleted} Twitch messages older than {days} days")
        finally:
            conn.close()

# Global instance
twitch_user_tracker_sql = TwitchUserTrackerSQL()

# Convenience functions
def track_twitch_message_sql(username: str, message: str, channel: str = "default", twitch_id: str = None, is_subscriber: bool = False, is_moderator: bool = False):
    """Track a Twitch message in SQL"""
    twitch_user_tracker_sql.track_message(username, message, channel, twitch_id, is_subscriber, is_moderator)

def get_twitch_user_context_sql(username: str) -> str:
    """Get Twitch user context from SQL"""
    return twitch_user_tracker_sql.get_user_context(username)

def get_twitch_chat_context_sql() -> str:
    """Get overall Twitch chat context from SQL"""
    return twitch_user_tracker_sql.get_chat_context()

def get_recent_twitch_users_sql(count: int = 5) -> List[str]:
    """Get recent Twitch users from SQL"""
    return twitch_user_tracker_sql.get_recent_users(count)

def get_twitch_user_stats_sql() -> Dict:
    """Get Twitch user statistics from SQL"""
    return twitch_user_tracker_sql.get_user_stats()

def get_all_twitch_users_sql() -> List[Dict]:
    """Get all Twitch users from SQL"""
    return twitch_user_tracker_sql.get_all_users()
