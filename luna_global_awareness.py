# luna_global_awareness.py
"""
Luna Global Awareness System
Tracks conversations across all platforms (Twitch, Discord, GUI) for better context awareness
"""

import sqlite3
import json
import time
import threading
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque

class GlobalAwarenessSystem:
    """Global awareness system that tracks conversations across all platforms"""
    
    def __init__(self, db_path: str = "luna_global_awareness.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        
        # In-memory caches for fast access
        self.recent_conversations = deque(maxlen=100)  # Last 100 conversations
        self.user_activity = defaultdict(lambda: {'last_seen': 0, 'platforms': set(), 'message_count': 0})
        self.platform_stats = defaultdict(int)
        
        # Initialize database
        self._init_database()
        
        print("🌍 Global Awareness System initialized")
    
    def _init_database(self):
        """Initialize the global awareness database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Conversations table - tracks all conversations across platforms
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    platform TEXT NOT NULL,
                    channel TEXT,
                    username TEXT NOT NULL,
                    user_message TEXT NOT NULL,
                    luna_response TEXT NOT NULL,
                    emotion TEXT DEFAULT 'neutral',
                    context TEXT DEFAULT 'general',
                    importance INTEGER DEFAULT 1,
                    user_id TEXT,
                    conversation_id TEXT,
                    UNIQUE(timestamp, platform, username, user_message)
                )
            ''')
            
            # User activity table - tracks user presence across platforms
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_activity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    channel TEXT,
                    last_message_time REAL NOT NULL,
                    message_count INTEGER DEFAULT 1,
                    first_seen REAL NOT NULL,
                    UNIQUE(username, platform, channel)
                )
            ''')
            
            # Platform stats table - tracks activity per platform
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS platform_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    message_count INTEGER DEFAULT 0,
                    unique_users INTEGER DEFAULT 0,
                    UNIQUE(date, platform)
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON conversations(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversations_platform ON conversations(platform)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversations_username ON conversations(username)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_activity_username ON user_activity(username)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_platform_stats_date ON platform_stats(date)')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Error initializing global awareness database: {e}")
    
    def add_conversation(self, platform: str, channel: str, username: str, 
                        user_message: str, luna_response: str, emotion: str = 'neutral',
                        context: str = 'general', importance: int = 1, user_id: str = None):
        """Add a conversation to the global awareness system"""
        try:
            current_time = time.time()
            conversation_id = f"{platform}_{channel}_{username}_{int(current_time)}"
            
            with self.lock:
                # Add to database
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO conversations 
                    (timestamp, platform, channel, username, user_message, luna_response, 
                     emotion, context, importance, user_id, conversation_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (current_time, platform, channel, username, user_message, luna_response,
                      emotion, context, importance, user_id, conversation_id))
                
                # Update user activity
                cursor.execute('''
                    INSERT OR REPLACE INTO user_activity 
                    (username, platform, channel, last_message_time, message_count, first_seen)
                    VALUES (?, ?, ?, ?, 
                        COALESCE((SELECT message_count FROM user_activity 
                                 WHERE username = ? AND platform = ? AND channel = ?), 0) + 1,
                        COALESCE((SELECT first_seen FROM user_activity 
                                 WHERE username = ? AND platform = ? AND channel = ?), ?))
                ''', (username, platform, channel, current_time, username, platform, channel,
                      username, platform, channel, current_time))
                
                # Update platform stats
                today = datetime.now().strftime('%Y-%m-%d')
                cursor.execute('''
                    INSERT OR REPLACE INTO platform_stats 
                    (date, platform, message_count, unique_users)
                    VALUES (?, ?, 
                        COALESCE((SELECT message_count FROM platform_stats 
                                 WHERE date = ? AND platform = ?), 0) + 1,
                        (SELECT COUNT(DISTINCT username) FROM user_activity 
                         WHERE platform = ? AND last_message_time >= ?))
                ''', (today, platform, today, platform, platform, 
                      time.time() - 86400))  # Last 24 hours
                
                conn.commit()
                conn.close()
                
                # Update in-memory caches
                self.recent_conversations.append({
                    'timestamp': current_time,
                    'platform': platform,
                    'channel': channel,
                    'username': username,
                    'user_message': user_message,
                    'luna_response': luna_response,
                    'emotion': emotion,
                    'context': context,
                    'importance': importance
                })
                
                # Update user activity cache
                self.user_activity[username]['last_seen'] = current_time
                self.user_activity[username]['platforms'].add(platform)
                self.user_activity[username]['message_count'] += 1
                
                # Update platform stats cache
                self.platform_stats[platform] += 1
                
                print(f"🌍 Global awareness: Added {platform} conversation from {username}")
                
        except Exception as e:
            print(f"❌ Error adding conversation to global awareness: {e}")
    
    def get_user_conversation_summary(self, username: str, platform: str = None) -> str:
        """Get a text summary of user's conversations for context injection"""
        try:
            context = self.get_user_context(username, platform, limit=5)
            
            if 'error' in context or not context.get('recent_conversations'):
                return ""
            
            # Create concise summary
            summary_parts = []
            
            # Add platform info
            if context.get('platforms'):
                platforms_str = ', '.join(context['platforms'])
                summary_parts.append(f"{username} is active on: {platforms_str}")
            
            # Add recent topics from conversations
            recent_topics = set()
            for conv in context['recent_conversations'][:3]:
                # Extract key words from user messages
                words = conv['user_message'].lower().split()
                for word in words:
                    if len(word) > 4:
                        recent_topics.add(word)
            
            if recent_topics:
                topics_str = ', '.join(list(recent_topics)[:5])
                summary_parts.append(f"Recent topics: {topics_str}")
            
            # Add message count
            if context.get('total_messages', 0) > 0:
                summary_parts.append(f"{context['total_messages']} total messages")
            
            return ". ".join(summary_parts) + "." if summary_parts else ""
            
        except Exception as e:
            print(f"⚠️ Error creating user summary: {e}")
            return ""
    
    def get_user_context(self, username: str, platform: str = None, limit: int = 10) -> Dict:
        """Get comprehensive context about a user across all platforms"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Get recent conversations
                query = '''
                    SELECT timestamp, platform, channel, user_message, luna_response, emotion, context
                    FROM conversations 
                    WHERE username = ?
                '''
                params = [username]
                
                if platform:
                    query += ' AND platform = ?'
                    params.append(platform)
                
                query += ' ORDER BY timestamp DESC LIMIT ?'
                params.append(limit)
                
                cursor.execute(query, params)
                conversations = cursor.fetchall()
                
                # Get user activity across platforms
                cursor.execute('''
                    SELECT platform, channel, last_message_time, message_count, first_seen
                    FROM user_activity 
                    WHERE username = ?
                    ORDER BY last_message_time DESC
                ''', (username,))
                activity = cursor.fetchall()
                
                conn.close()
                
                # Format response
                context = {
                    'username': username,
                    'recent_conversations': [],
                    'platforms': set(),
                    'total_messages': 0,
                    'first_seen': None,
                    'last_seen': 0,
                    'activity_summary': {}
                }
                
                for conv in conversations:
                    timestamp, platform, channel, user_msg, luna_resp, emotion, ctx = conv
                    context['recent_conversations'].append({
                        'timestamp': timestamp,
                        'platform': platform,
                        'channel': channel,
                        'user_message': user_msg,
                        'luna_response': luna_resp,
                        'emotion': emotion,
                        'context': ctx
                    })
                    context['platforms'].add(platform)
                
                for act in activity:
                    platform, channel, last_time, msg_count, first_seen = act
                    context['platforms'].add(platform)
                    context['total_messages'] += msg_count
                    context['last_seen'] = max(context['last_seen'], last_time)
                    if not context['first_seen'] or first_seen < context['first_seen']:
                        context['first_seen'] = first_seen
                    
                    context['activity_summary'][platform] = {
                        'channel': channel,
                        'last_message_time': last_time,
                        'message_count': msg_count,
                        'first_seen': first_seen
                    }
                
                context['platforms'] = list(context['platforms'])
                
                return context
                
        except Exception as e:
            print(f"❌ Error getting user context: {e}")
            return {'username': username, 'error': str(e)}
    
    def get_cross_platform_insights(self, username: str) -> str:
        """Generate insights about user behavior across platforms"""
        try:
            context = self.get_user_context(username)
            
            if 'error' in context:
                return f"I don't have much information about {username} yet."
            
            insights = []
            
            # Platform diversity
            platforms = context['platforms']
            if len(platforms) > 1:
                insights.append(f"{username} is active on {len(platforms)} platforms: {', '.join(platforms)}")
            else:
                insights.append(f"{username} primarily uses {platforms[0] if platforms else 'unknown platform'}")
            
            # Activity level
            total_messages = context['total_messages']
            if total_messages > 50:
                insights.append(f"They're very active with {total_messages} total messages")
            elif total_messages > 10:
                insights.append(f"They're moderately active with {total_messages} messages")
            else:
                insights.append(f"They're a newer user with {total_messages} messages")
            
            # Recent activity
            if context['recent_conversations']:
                latest = context['recent_conversations'][0]
                time_diff = time.time() - latest['timestamp']
                if time_diff < 3600:  # Less than 1 hour
                    insights.append(f"They were just active on {latest['platform']}")
                elif time_diff < 86400:  # Less than 1 day
                    insights.append(f"They were active today on {latest['platform']}")
                else:
                    days_ago = int(time_diff / 86400)
                    insights.append(f"Last seen {days_ago} days ago on {latest['platform']}")
            
            return ". ".join(insights) + "."
            
        except Exception as e:
            print(f"❌ Error generating cross-platform insights: {e}")
            return f"I'm having trouble accessing information about {username}."
    
    def get_recent_activity_summary(self, hours: int = 24) -> Dict:
        """Get summary of recent activity across all platforms"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cutoff_time = time.time() - (hours * 3600)
                
                # Get recent conversations
                cursor.execute('''
                    SELECT platform, COUNT(*) as message_count, COUNT(DISTINCT username) as unique_users
                    FROM conversations 
                    WHERE timestamp >= ?
                    GROUP BY platform
                    ORDER BY message_count DESC
                ''', (cutoff_time,))
                platform_activity = cursor.fetchall()
                
                # Get most active users
                cursor.execute('''
                    SELECT username, platform, COUNT(*) as message_count
                    FROM conversations 
                    WHERE timestamp >= ?
                    GROUP BY username, platform
                    ORDER BY message_count DESC
                    LIMIT 10
                ''', (cutoff_time,))
                active_users = cursor.fetchall()
                
                conn.close()
                
                return {
                    'timeframe_hours': hours,
                    'platform_activity': {platform: {'messages': count, 'users': users} 
                                        for platform, count, users in platform_activity},
                    'most_active_users': [{'username': user, 'platform': platform, 'messages': count} 
                                        for user, platform, count in active_users]
                }
                
        except Exception as e:
            print(f"❌ Error getting recent activity summary: {e}")
            return {'error': str(e)}
    
    def search_conversations(self, query: str, platform: str = None, username: str = None, 
                           limit: int = 10) -> List[Dict]:
        """Search conversations across all platforms"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                sql_query = '''
                    SELECT timestamp, platform, channel, username, user_message, luna_response, emotion, context
                    FROM conversations 
                    WHERE (user_message LIKE ? OR luna_response LIKE ?)
                '''
                params = [f'%{query}%', f'%{query}%']
                
                if platform:
                    sql_query += ' AND platform = ?'
                    params.append(platform)
                
                if username:
                    sql_query += ' AND username = ?'
                    params.append(username)
                
                sql_query += ' ORDER BY timestamp DESC LIMIT ?'
                params.append(limit)
                
                cursor.execute(sql_query, params)
                results = cursor.fetchall()
                
                conn.close()
                
                formatted_results = []
                for result in results:
                    timestamp, platform, channel, username, user_msg, luna_resp, emotion, ctx = result
                    formatted_results.append({
                        'timestamp': timestamp,
                        'platform': platform,
                        'channel': channel,
                        'username': username,
                        'user_message': user_msg,
                        'luna_response': luna_resp,
                        'emotion': emotion,
                        'context': ctx
                    })
                
                return formatted_results
                
        except Exception as e:
            print(f"❌ Error searching conversations: {e}")
            return []
    
    def get_system_stats(self) -> Dict:
        """Get overall system statistics"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Total conversations
                cursor.execute('SELECT COUNT(*) FROM conversations')
                total_conversations = cursor.fetchone()[0]
                
                # Unique users
                cursor.execute('SELECT COUNT(DISTINCT username) FROM conversations')
                unique_users = cursor.fetchone()[0]
                
                # Platform breakdown
                cursor.execute('''
                    SELECT platform, COUNT(*) as count 
                    FROM conversations 
                    GROUP BY platform 
                    ORDER BY count DESC
                ''')
                platform_breakdown = dict(cursor.fetchall())
                
                # Recent activity (last 24 hours)
                cutoff_time = time.time() - 86400
                cursor.execute('SELECT COUNT(*) FROM conversations WHERE timestamp >= ?', (cutoff_time,))
                recent_activity = cursor.fetchone()[0]
                
                conn.close()
                
                return {
                    'total_conversations': total_conversations,
                    'unique_users': unique_users,
                    'platform_breakdown': platform_breakdown,
                    'recent_activity_24h': recent_activity,
                    'database_size': f"{total_conversations} conversations from {unique_users} users"
                }
                
        except Exception as e:
            print(f"❌ Error getting system stats: {e}")
            return {'error': str(e)}

# Global instance
global_awareness = None

def initialize_global_awareness() -> GlobalAwarenessSystem:
    """Initialize the global awareness system"""
    global global_awareness
    if not global_awareness:
        global_awareness = GlobalAwarenessSystem()
    return global_awareness

def get_global_awareness() -> Optional[GlobalAwarenessSystem]:
    """Get the global awareness system instance"""
    return global_awareness

def add_global_conversation(platform: str, channel: str, username: str, 
                           user_message: str, luna_response: str, **kwargs):
    """Add a conversation to global awareness"""
    if global_awareness:
        global_awareness.add_conversation(platform, channel, username, user_message, luna_response, **kwargs)

def get_user_global_context(username: str, platform: str = None) -> Dict:
    """Get user context from global awareness"""
    if global_awareness:
        return global_awareness.get_user_context(username, platform)
    return {'username': username, 'error': 'Global awareness not initialized'}

def get_cross_platform_insights(username: str) -> str:
    """Get cross-platform insights for a user"""
    if global_awareness:
        return global_awareness.get_cross_platform_insights(username)
    return f"I don't have cross-platform information about {username} yet."
