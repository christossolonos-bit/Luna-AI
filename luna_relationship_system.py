"""
Luna Relationship System
Tracks and evolves Luna's relationships with users across all platforms
"""

import sqlite3
import time
import threading
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
import json

class RelationshipSystem:
    """
    Manages Luna's relationships with users across Discord, Twitch, and GUI
    
    Relationship Levels:
    1. Stranger (0-2 interactions)
    2. Acquaintance (3-10 interactions)
    3. Friend (11-50 interactions)
    4. Close Friend (51-200 interactions)
    5. Best Friend (200+ interactions)
    
    Relationship Attributes:
    - Trust level (0-100)
    - Affection level (0-100)
    - Familiarity (0-100)
    - Emotional bond (calculated from interactions)
    """
    
    def __init__(self, db_path: str = "luna_relationships.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._initialize_database()
        print("💕 Relationship System initialized")
    
    def _initialize_database(self):
        """Create relationship tracking tables"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Main relationships table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS relationships (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        platform TEXT NOT NULL,
                        first_met REAL NOT NULL,
                        last_interaction REAL NOT NULL,
                        total_interactions INTEGER DEFAULT 0,
                        trust_level INTEGER DEFAULT 50,
                        affection_level INTEGER DEFAULT 50,
                        familiarity_level INTEGER DEFAULT 0,
                        relationship_level TEXT DEFAULT 'stranger',
                        relationship_notes TEXT,
                        personality_traits TEXT,
                        UNIQUE(username, platform)
                    )
                ''')
                
                # Interaction history table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS interaction_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        platform TEXT NOT NULL,
                        timestamp REAL NOT NULL,
                        interaction_type TEXT,
                        sentiment TEXT,
                        topic TEXT,
                        user_message TEXT,
                        luna_response TEXT
                    )
                ''')
                
                # Relationship events table (milestones)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS relationship_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        platform TEXT NOT NULL,
                        timestamp REAL NOT NULL,
                        event_type TEXT NOT NULL,
                        event_description TEXT,
                        importance INTEGER DEFAULT 1
                    )
                ''')
                
                conn.commit()
                conn.close()
                print("✅ Relationship database initialized")
        except Exception as e:
            print(f"❌ Relationship database initialization error: {e}")
    
    def update_relationship(self, username: str, platform: str, 
                          user_message: str, luna_response: str,
                          sentiment: str = 'neutral', topic: str = 'general'):
        """Update relationship based on new interaction"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                current_time = time.time()
                
                # Get existing relationship or create new one
                cursor.execute('''
                    SELECT total_interactions, trust_level, affection_level, 
                           familiarity_level, relationship_level
                    FROM relationships
                    WHERE username = ? AND platform = ?
                ''', (username, platform))
                
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing relationship
                    interactions, trust, affection, familiarity, current_level = existing
                    
                    # Increment interaction count
                    interactions += 1
                    
                    # Update relationship metrics based on sentiment
                    if sentiment == 'positive':
                        affection = min(100, affection + 2)
                        trust = min(100, trust + 1)
                    elif sentiment == 'negative':
                        affection = max(0, affection - 1)
                    
                    # Always increase familiarity with each interaction
                    familiarity = min(100, familiarity + 1)
                    
                    # Determine new relationship level
                    new_level = self._calculate_relationship_level(interactions, trust, affection, familiarity)
                    
                    # Check if relationship level changed (milestone!)
                    if new_level != current_level:
                        self._log_relationship_event(
                            username, platform, current_time,
                            'level_up',
                            f"Relationship evolved from {current_level} to {new_level}!",
                            importance=4
                        )
                        print(f"💕 {username}'s relationship evolved: {current_level} → {new_level}")
                    
                    cursor.execute('''
                        UPDATE relationships
                        SET last_interaction = ?,
                            total_interactions = ?,
                            trust_level = ?,
                            affection_level = ?,
                            familiarity_level = ?,
                            relationship_level = ?
                        WHERE username = ? AND platform = ?
                    ''', (current_time, interactions, trust, affection, familiarity, 
                          new_level, username, platform))
                    
                else:
                    # Create new relationship
                    cursor.execute('''
                        INSERT INTO relationships (
                            username, platform, first_met, last_interaction,
                            total_interactions, trust_level, affection_level,
                            familiarity_level, relationship_level
                        ) VALUES (?, ?, ?, ?, 1, 50, 50, 10, 'stranger')
                    ''', (username, platform, current_time, current_time))
                    
                    print(f"💕 New relationship created with {username} on {platform}")
                    
                    # Log first meeting event
                    self._log_relationship_event(
                        username, platform, current_time,
                        'first_meeting',
                        f"First met {username} on {platform}!",
                        importance=3
                    )
                
                # Log this interaction
                cursor.execute('''
                    INSERT INTO interaction_history (
                        username, platform, timestamp, interaction_type,
                        sentiment, topic, user_message, luna_response
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (username, platform, current_time, 'chat', 
                      sentiment, topic, user_message, luna_response))
                
                conn.commit()
                conn.close()
                
        except Exception as e:
            print(f"❌ Relationship update error: {e}")
    
    def _calculate_relationship_level(self, interactions: int, trust: int, 
                                     affection: int, familiarity: int) -> str:
        """Calculate relationship level based on metrics"""
        # Weight the metrics
        score = (interactions * 0.4) + (trust * 0.2) + (affection * 0.2) + (familiarity * 0.2)
        
        if score >= 200:
            return 'best_friend'
        elif score >= 100:
            return 'close_friend'
        elif score >= 40:
            return 'friend'
        elif score >= 15:
            return 'acquaintance'
        else:
            return 'stranger'
    
    def _log_relationship_event(self, username: str, platform: str, timestamp: float,
                               event_type: str, description: str, importance: int = 1):
        """Log a relationship milestone/event"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO relationship_events (
                    username, platform, timestamp, event_type,
                    event_description, importance
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, platform, timestamp, event_type, description, importance))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️ Event logging error: {e}")
    
    def get_relationship_context(self, username: str, platform: str) -> str:
        """Get relationship context for prompt injection"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Get relationship data
                cursor.execute('''
                    SELECT total_interactions, trust_level, affection_level,
                           familiarity_level, relationship_level, first_met,
                           last_interaction, relationship_notes
                    FROM relationships
                    WHERE username = ? AND platform = ?
                ''', (username, platform))
                
                result = cursor.fetchone()
                
                if not result:
                    conn.close()
                    return f"{username} is a new person you just met on {platform}"
                
                interactions, trust, affection, familiarity, level, first_met, last_seen, notes = result
                
                # Calculate time known
                first_met_dt = datetime.fromtimestamp(first_met)
                days_known = (datetime.now() - first_met_dt).days
                
                # Get recent interaction history
                cursor.execute('''
                    SELECT user_message, luna_response, sentiment, timestamp
                    FROM interaction_history
                    WHERE username = ? AND platform = ?
                    ORDER BY timestamp DESC
                    LIMIT 3
                ''', (username, platform))
                
                recent_interactions = cursor.fetchall()
                
                # Get relationship events
                cursor.execute('''
                    SELECT event_type, event_description, timestamp
                    FROM relationship_events
                    WHERE username = ? AND platform = ?
                    ORDER BY timestamp DESC
                    LIMIT 3
                ''', (username, platform))
                
                events = cursor.fetchall()
                
                conn.close()
                
                # Build context string
                context_parts = []
                
                # Relationship status
                level_descriptions = {
                    'stranger': 'someone you just met',
                    'acquaintance': 'someone you know a bit',
                    'friend': 'a friend of yours',
                    'close_friend': 'a close friend',
                    'best_friend': 'one of your best friends'
                }
                
                context_parts.append(f"{username} is {level_descriptions.get(level, 'someone you know')}")
                
                # Time known
                if days_known > 0:
                    context_parts.append(f"you've known them for {days_known} day{'s' if days_known != 1 else ''}")
                
                # Interaction count
                context_parts.append(f"you've talked {interactions} time{'s' if interactions != 1 else ''}")
                
                # Relationship metrics
                if affection > 70:
                    context_parts.append("you care about them")
                elif affection < 30:
                    context_parts.append("you're still warming up to them")
                
                if trust > 70:
                    context_parts.append("you trust them")
                
                if familiarity > 70:
                    context_parts.append("you know them well")
                
                # Recent interactions
                if recent_interactions:
                    last_msg = recent_interactions[0][0]
                    last_reply = recent_interactions[0][1]
                    context_parts.append(f"last time they said: '{last_msg[:50]}...' and you replied: '{last_reply[:50]}...'")
                
                # Important events
                if events:
                    event_descriptions = [f"{e[1]}" for e in events[:2]]
                    if event_descriptions:
                        context_parts.append(f"Notable: {'; '.join(event_descriptions)}")
                
                relationship_context = " | ".join(context_parts)
                print(f"💕 Relationship context for {username}: {level} ({interactions} interactions)")
                
                return relationship_context
                
        except Exception as e:
            print(f"❌ Error getting relationship context: {e}")
            return f"{username} is chatting with you on {platform}"
    
    def analyze_sentiment(self, user_message: str, luna_response: str) -> str:
        """Analyze sentiment of interaction"""
        # Simple keyword-based sentiment analysis
        positive_keywords = ['love', 'like', 'thanks', 'great', 'awesome', 'good', 
                           'nice', 'appreciate', 'wonderful', 'amazing', 'happy']
        negative_keywords = ['hate', 'bad', 'terrible', 'awful', 'annoying', 
                           'stupid', 'angry', 'mad', 'upset']
        
        text = (user_message + " " + luna_response).lower()
        
        positive_count = sum(1 for word in positive_keywords if word in text)
        negative_count = sum(1 for word in negative_keywords if word in text)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def extract_topic(self, user_message: str) -> str:
        """Extract main topic from message"""
        keywords = user_message.lower().split()
        
        # Topic categories
        if any(word in keywords for word in ['game', 'gaming', 'play', 'stream']):
            return 'gaming'
        elif any(word in keywords for word in ['code', 'programming', 'tech', 'computer']):
            return 'technology'
        elif any(word in keywords for word in ['love', 'feel', 'emotion', 'heart']):
            return 'emotional'
        elif any(word in keywords for word in ['help', 'question', 'how', 'what']):
            return 'help'
        else:
            return 'general'
    
    def get_all_relationships(self, platform: Optional[str] = None) -> List[Dict]:
        """Get all relationships, optionally filtered by platform"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                if platform:
                    cursor.execute('''
                        SELECT username, platform, total_interactions, 
                               relationship_level, trust_level, affection_level
                        FROM relationships
                        WHERE platform = ?
                        ORDER BY total_interactions DESC
                    ''', (platform,))
                else:
                    cursor.execute('''
                        SELECT username, platform, total_interactions,
                               relationship_level, trust_level, affection_level
                        FROM relationships
                        ORDER BY total_interactions DESC
                    ''')
                
                relationships = []
                for row in cursor.fetchall():
                    relationships.append({
                        'username': row[0],
                        'platform': row[1],
                        'interactions': row[2],
                        'level': row[3],
                        'trust': row[4],
                        'affection': row[5]
                    })
                
                conn.close()
                return relationships
                
        except Exception as e:
            print(f"❌ Error getting relationships: {e}")
            return []
    
    def get_relationship_summary(self, username: str, platform: str) -> str:
        """Get a narrative summary of the relationship"""
        try:
            context = self.get_relationship_context(username, platform)
            
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Get relationship level
                cursor.execute('''
                    SELECT relationship_level, total_interactions, 
                           trust_level, affection_level, first_met
                    FROM relationships
                    WHERE username = ? AND platform = ?
                ''', (username, platform))
                
                result = cursor.fetchone()
                conn.close()
                
                if not result:
                    return f"You haven't met {username} yet"
                
                level, interactions, trust, affection, first_met = result
                
                # Create narrative summary
                level_narratives = {
                    'stranger': f"You're just getting to know {username}",
                    'acquaintance': f"You're becoming familiar with {username}",
                    'friend': f"{username} is becoming a good friend",
                    'close_friend': f"{username} is a close friend you trust",
                    'best_friend': f"{username} is one of your best friends"
                }
                
                summary = level_narratives.get(level, f"You know {username}")
                
                # Add emotional context
                if affection > 80:
                    summary += f" and you really care about them"
                elif affection > 60:
                    summary += f" and you like them"
                
                if trust > 80:
                    summary += f", you trust them completely"
                elif trust > 60:
                    summary += f", you trust them"
                
                summary += f". You've talked {interactions} times."
                
                return summary
                
        except Exception as e:
            print(f"❌ Error getting relationship summary: {e}")
            return ""
    
    def get_cross_platform_relationship(self, username: str) -> Dict:
        """Get relationship data across all platforms for this user"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Get all platforms this user is on
                cursor.execute('''
                    SELECT platform, relationship_level, total_interactions,
                           trust_level, affection_level, first_met
                    FROM relationships
                    WHERE username = ?
                    ORDER BY total_interactions DESC
                ''', (username,))
                
                platforms = cursor.fetchall()
                conn.close()
                
                if not platforms:
                    return {'username': username, 'platforms': [], 'overall_level': 'stranger'}
                
                # Calculate overall relationship
                total_interactions = sum(p[2] for p in platforms)
                avg_trust = sum(p[3] for p in platforms) / len(platforms)
                avg_affection = sum(p[4] for p in platforms) / len(platforms)
                
                overall_level = self._calculate_relationship_level(
                    total_interactions, avg_trust, avg_affection, 100
                )
                
                return {
                    'username': username,
                    'platforms': [p[0] for p in platforms],
                    'overall_level': overall_level,
                    'total_interactions': total_interactions,
                    'highest_platform': platforms[0][0],
                    'avg_trust': avg_trust,
                    'avg_affection': avg_affection
                }
                
        except Exception as e:
            print(f"❌ Error getting cross-platform relationship: {e}")
            return {}
    
    def get_statistics(self) -> Dict:
        """Get relationship statistics"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Total relationships
                cursor.execute('SELECT COUNT(*) FROM relationships')
                total = cursor.fetchone()[0]
                
                # Breakdown by level
                cursor.execute('''
                    SELECT relationship_level, COUNT(*)
                    FROM relationships
                    GROUP BY relationship_level
                ''')
                level_dist = dict(cursor.fetchall())
                
                # Breakdown by platform
                cursor.execute('''
                    SELECT platform, COUNT(*)
                    FROM relationships
                    GROUP BY platform
                ''')
                platform_dist = dict(cursor.fetchall())
                
                conn.close()
                
                return {
                    'total_relationships': total,
                    'level_distribution': level_dist,
                    'platform_distribution': platform_dist
                }
                
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
            return {}

# Global instance
relationship_system = None

def initialize_relationship_system() -> RelationshipSystem:
    """Initialize the relationship system"""
    global relationship_system
    if not relationship_system:
        relationship_system = RelationshipSystem()
    return relationship_system

def get_relationship_system() -> Optional[RelationshipSystem]:
    """Get the relationship system"""
    return relationship_system

def update_user_relationship(username: str, platform: str, 
                           user_message: str, luna_response: str):
    """Update relationship with a user (main function to call)"""
    if relationship_system:
        # Analyze sentiment and topic
        sentiment = relationship_system.analyze_sentiment(user_message, luna_response)
        topic = relationship_system.extract_topic(user_message)
        
        relationship_system.update_relationship(
            username, platform, user_message, luna_response, sentiment, topic
        )

def get_relationship_context_for_prompt(username: str, platform: str) -> str:
    """Get relationship context for Luna's prompt"""
    if relationship_system:
        return relationship_system.get_relationship_context(username, platform)
    return ""

def get_relationship_stats() -> Dict:
    """Get relationship statistics"""
    if relationship_system:
        return relationship_system.get_statistics()
    return {}

