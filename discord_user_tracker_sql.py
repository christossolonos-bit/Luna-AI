# discord_user_tracker_sql.py
"""
Discord User Tracker for Luna AI with SQL Database
Tracks Discord usernames and helps Luna mention them in responses
"""

import sqlite3
import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set

class DiscordUserTrackerSQL:
    """Tracks Discord users and their activity using SQL database"""
    
    def __init__(self, db_path: str = "luna_discord_users.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQL database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS discord_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                discord_id TEXT,
                first_seen REAL NOT NULL,
                last_seen REAL NOT NULL,
                total_messages INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS discord_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                channel TEXT NOT NULL,
                guild TEXT NOT NULL,
                timestamp REAL NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES discord_users(id)
            )
        ''')
        
        # Channels table (tracks which channels users are active in)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS discord_user_channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                channel TEXT NOT NULL,
                guild TEXT NOT NULL,
                first_seen REAL NOT NULL,
                last_seen REAL NOT NULL,
                message_count INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES discord_users(id),
                UNIQUE(user_id, channel, guild)
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_discord_users_username ON discord_users(username)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_discord_messages_timestamp ON discord_messages(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_discord_messages_user_id ON discord_messages(user_id)')
        
        conn.commit()
        conn.close()
        print(f"[OK] Discord SQL database initialized: {self.db_path}")
    
    def track_message(self, username: str, message: str, channel: str, guild: str = "Unknown", discord_id: str = None):
        """Track a message from a Discord user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        current_time = time.time()
        
        try:
            # Get or create user
            cursor.execute('SELECT id, total_messages FROM discord_users WHERE username = ?', (username,))
            result = cursor.fetchone()
            
            if result:
                user_id, total_messages = result
                # Update user stats
                cursor.execute('''
                    UPDATE discord_users 
                    SET last_seen = ?, total_messages = total_messages + 1, discord_id = COALESCE(discord_id, ?)
                    WHERE id = ?
                ''', (current_time, discord_id, user_id))
            else:
                # Create new user
                cursor.execute('''
                    INSERT INTO discord_users (username, discord_id, first_seen, last_seen, total_messages)
                    VALUES (?, ?, ?, ?, 1)
                ''', (username, discord_id, current_time, current_time))
                user_id = cursor.lastrowid
            
            # Insert message
            cursor.execute('''
                INSERT INTO discord_messages (user_id, message, channel, guild, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, message, channel, guild, current_time))
            
            # Update channel activity
            cursor.execute('''
                INSERT INTO discord_user_channels (user_id, channel, guild, first_seen, last_seen, message_count)
                VALUES (?, ?, ?, ?, ?, 1)
                ON CONFLICT(user_id, channel, guild) DO UPDATE SET
                    last_seen = excluded.last_seen,
                    message_count = message_count + 1
            ''', (user_id, channel, guild, current_time, current_time))
            
            conn.commit()
            
        except Exception as e:
            print(f"[ERROR] Error tracking Discord message: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def get_user_context(self, username: str) -> str:
        """Get context about a Discord user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT first_seen, last_seen, total_messages
                FROM discord_users
                WHERE username = ?
            ''', (username,))
            
            result = cursor.fetchone()
            if not result:
                return f"New Discord user {username}"
            
            first_seen, last_seen, total_messages = result
            current_time = time.time()
            
            # Calculate time since last seen
            time_since_last = current_time - last_seen
            if time_since_last < 60:
                last_seen_str = "just now"
            elif time_since_last < 3600:
                last_seen_str = f"{int(time_since_last/60)} minutes ago"
            elif time_since_last < 86400:
                last_seen_str = f"{int(time_since_last/3600)} hours ago"
            else:
                last_seen_str = f"{int(time_since_last/86400)} days ago"
            
            # Get channels
            cursor.execute('''
                SELECT channel FROM discord_user_channels
                WHERE user_id = (SELECT id FROM discord_users WHERE username = ?)
                ORDER BY last_seen DESC LIMIT 3
            ''', (username,))
            
            channels = [row[0] for row in cursor.fetchall()]
            channel_info = f"active in {', '.join(channels)}" if channels else "no recent channels"
            
            # Get recent messages
            cursor.execute('''
                SELECT message FROM discord_messages
                WHERE user_id = (SELECT id FROM discord_users WHERE username = ?)
                ORDER BY timestamp DESC LIMIT 3
            ''', (username,))
            
            recent_messages = [row[0][:50] for row in cursor.fetchall()]
            recent_context = f"Recently talked about: {', '.join(recent_messages)}" if recent_messages else ""
            
            return f"Discord user {username} ({total_messages} total messages, last seen {last_seen_str}, {channel_info}). {recent_context}"
            
        finally:
            conn.close()
    
    def get_chat_context(self) -> str:
        """Get context about recent Discord chat activity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT u.username, m.message, m.timestamp
                FROM discord_messages m
                JOIN discord_users u ON m.user_id = u.id
                ORDER BY m.timestamp DESC
                LIMIT 5
            ''')
            
            results = cursor.fetchall()
            if not results:
                return "No recent Discord activity"
            
            context_parts = []
            for username, message, timestamp in results:
                time_ago = time.time() - timestamp
                if time_ago < 60:
                    time_str = "just now"
                elif time_ago < 3600:
                    time_str = f"{int(time_ago/60)}m ago"
                else:
                    time_str = f"{int(time_ago/3600)}h ago"
                
                context_parts.append(f"{username} ({time_str}): {message[:30]}...")
            
            return "Recent Discord chat: " + " | ".join(context_parts)
            
        finally:
            conn.close()
    
    def get_recent_users(self, count: int = 5) -> List[str]:
        """Get list of recently active Discord users"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT DISTINCT u.username
                FROM discord_messages m
                JOIN discord_users u ON m.user_id = u.id
                ORDER BY m.timestamp DESC
                LIMIT ?
            ''', (count,))
            
            return [row[0] for row in cursor.fetchall()]
            
        finally:
            conn.close()
    
    def get_user_stats(self) -> Dict:
        """Get overall Discord user statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Total users
            cursor.execute('SELECT COUNT(*) FROM discord_users')
            total_users = cursor.fetchone()[0]
            
            # Active users (last 24 hours)
            cutoff = time.time() - 86400
            cursor.execute('SELECT COUNT(*) FROM discord_users WHERE last_seen > ?', (cutoff,))
            active_users = cursor.fetchone()[0]
            
            # Total messages
            cursor.execute('SELECT SUM(total_messages) FROM discord_users')
            total_messages = cursor.fetchone()[0] or 0
            
            # Recent messages (last 100)
            cursor.execute('SELECT COUNT(*) FROM discord_messages WHERE timestamp > ?', (cutoff,))
            recent_messages = cursor.fetchone()[0]
            
            return {
                "total_users": total_users,
                "active_users": active_users,
                "total_messages": total_messages,
                "recent_messages": recent_messages
            }
            
        finally:
            conn.close()
    
    def get_all_users(self) -> List[Dict]:
        """Get all Discord users with their stats"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT username, discord_id, first_seen, last_seen, total_messages
                FROM discord_users
                ORDER BY last_seen DESC
            ''')
            
            users = []
            for row in cursor.fetchall():
                username, discord_id, first_seen, last_seen, total_messages = row
                users.append({
                    'username': username,
                    'discord_id': discord_id or 'N/A',
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
            cursor.execute('DELETE FROM discord_messages WHERE timestamp < ?', (cutoff_time,))
            deleted = cursor.rowcount
            conn.commit()
            print(f"[CLEANUP] Cleaned up {deleted} Discord messages older than {days} days")
        finally:
            conn.close()

# Global instance
discord_user_tracker_sql = DiscordUserTrackerSQL()

# Convenience functions
def track_discord_message_sql(username: str, message: str, channel: str, guild: str = "Unknown", discord_id: str = None):
    """Track a Discord message in SQL"""
    discord_user_tracker_sql.track_message(username, message, channel, guild, discord_id)

def get_discord_user_context_sql(username: str) -> str:
    """Get Discord user context from SQL"""
    return discord_user_tracker_sql.get_user_context(username)

def get_discord_chat_context_sql() -> str:
    """Get Discord chat context from SQL"""
    return discord_user_tracker_sql.get_chat_context()

def get_recent_discord_users_sql(count: int = 5) -> List[str]:
    """Get recent Discord users from SQL"""
    return discord_user_tracker_sql.get_recent_users(count)

def get_discord_user_stats_sql() -> Dict:
    """Get Discord user statistics from SQL"""
    return discord_user_tracker_sql.get_user_stats()

def get_all_discord_users_sql() -> List[Dict]:
    """Get all Discord users from SQL"""
    return discord_user_tracker_sql.get_all_users()
