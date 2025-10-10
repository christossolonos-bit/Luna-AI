"""
Luna Lambda Architecture
Implements a Lambda-style data processing architecture for Luna's memory and response system

Architecture:
- Speed Layer: Real-time, fast responses with cached data
- Batch Layer: Comprehensive, deep memory analysis
- Serving Layer: Merges both for optimal responses

Author: Luna AI System
"""

import time
import threading
import sqlite3
from collections import deque
from typing import Dict, List, Optional, Tuple, Any
import json

# ============================================================================
# SPEED LAYER - Real-time, Fast Path
# ============================================================================

class SpeedLayer:
    """
    Speed Layer: Handles real-time data with minimal latency
    - In-memory caching
    - Recent conversation context (last 10 messages)
    - Quick emotional state
    - Fast user context lookup
    """
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        self.recent_conversations = deque(maxlen=50)  # Last 50 exchanges
        self.recent_users = {}  # {username: {last_seen, message_count, platform}}
        self.hot_memories = deque(maxlen=20)  # Last 20 important memories
        self.lock = threading.Lock()
        
        print("⚡ Speed Layer initialized - real-time fast path active")
    
    def add_conversation(self, username: str, user_message: str, luna_response: str, 
                        platform: str, emotion: str = 'neutral'):
        """Add conversation to speed layer (hot data)"""
        with self.lock:
            timestamp = time.time()
            
            # Add to recent conversations
            self.recent_conversations.append({
                'timestamp': timestamp,
                'username': username,
                'platform': platform,
                'user_message': user_message,
                'luna_response': luna_response,
                'emotion': emotion
            })
            
            # Update user tracking (hot users)
            if username not in self.recent_users:
                self.recent_users[username] = {
                    'first_seen': timestamp,
                    'last_seen': timestamp,
                    'message_count': 0,
                    'platform': platform,
                    'recent_topics': []
                }
            
            self.recent_users[username]['last_seen'] = timestamp
            self.recent_users[username]['message_count'] += 1
            
            # Extract topics from message (simple keyword extraction)
            keywords = [word.lower() for word in user_message.split() if len(word) > 4][:3]
            self.recent_users[username]['recent_topics'] = keywords
            
            print(f"⚡ Speed Layer: Added conversation from {username} ({platform})")
    
    def get_recent_context(self, username: str, platform: str, limit: int = 5) -> str:
        """Get recent context for a user (FAST - O(n) scan of hot data)"""
        with self.lock:
            # Get recent conversations with this user
            user_convs = [
                conv for conv in self.recent_conversations
                if conv['username'] == username and conv['platform'] == platform
            ][-limit:]
            
            if not user_convs:
                return ""
            
            # Build context string
            context_parts = []
            for conv in user_convs:
                context_parts.append(f"User: {conv['user_message'][:100]}")
                context_parts.append(f"Luna: {conv['luna_response'][:100]}")
            
            return " | ".join(context_parts[-10:])  # Last 5 exchanges
    
    def get_user_stats(self, username: str) -> Dict:
        """Get quick user stats from hot data"""
        with self.lock:
            if username in self.recent_users:
                user_data = self.recent_users[username]
                return {
                    'message_count': user_data['message_count'],
                    'last_seen': user_data['last_seen'],
                    'time_since_last': time.time() - user_data['last_seen'],
                    'recent_topics': user_data['recent_topics'],
                    'platform': user_data['platform']
                }
            return {}
    
    def cache_response(self, query_key: str, response: Any):
        """Cache a response for fast retrieval"""
        with self.lock:
            self.cache[query_key] = {
                'response': response,
                'timestamp': time.time()
            }
            
            # Clean old cache entries
            current_time = time.time()
            self.cache = {
                k: v for k, v in self.cache.items()
                if current_time - v['timestamp'] < self.cache_ttl
            }
    
    def get_cached_response(self, query_key: str) -> Optional[Any]:
        """Get cached response if still valid"""
        with self.lock:
            if query_key in self.cache:
                cached = self.cache[query_key]
                if time.time() - cached['timestamp'] < self.cache_ttl:
                    return cached['response']
                else:
                    del self.cache[query_key]
            return None


# ============================================================================
# BATCH LAYER - Comprehensive, Accurate Processing
# ============================================================================

class BatchLayer:
    """
    Batch Layer: Handles comprehensive data analysis with accuracy over speed
    - Full database queries
    - Deep memory search
    - Historical pattern analysis
    - Relationship computation
    """
    
    def __init__(self, db_path: str = 'luna_memories.db'):
        self.db_path = db_path
        self.lock = threading.Lock()
        self.last_batch_run = 0
        self.batch_interval = 60  # Run batch jobs every 60 seconds
        
        print("🗄️ Batch Layer initialized - comprehensive deep path active")
    
    def get_deep_user_context(self, username: str, platform: str, limit: int = 20) -> Dict:
        """Get comprehensive user context from database (SLOW but ACCURATE)"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path, timeout=5.0)
                cursor = conn.cursor()
                
                # Get total message count
                cursor.execute('''
                    SELECT COUNT(*) FROM conversations 
                    WHERE user_message LIKE ? OR luna_response LIKE ?
                ''', (f'%{username}%', f'%{username}%'))
                total_messages = cursor.fetchone()[0]
                
                # Get recent conversations (deep history)
                cursor.execute('''
                    SELECT user_message, luna_response, timestamp, mood
                    FROM conversations
                    WHERE user_message LIKE ? OR luna_response LIKE ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (f'%{username}%', f'%{username}%', limit))
                
                conversations = []
                for row in cursor.fetchall():
                    conversations.append({
                        'user_message': row[0],
                        'luna_response': row[1],
                        'timestamp': row[2],
                        'mood': row[3]
                    })
                
                conn.close()
                
                print(f"🗄️ Batch Layer: Retrieved {len(conversations)} conversations for {username}")
                
                return {
                    'total_messages': total_messages,
                    'conversations': conversations,
                    'has_history': total_messages > 0
                }
                
        except Exception as e:
            print(f"⚠️ Batch Layer error: {e}")
            return {'total_messages': 0, 'conversations': [], 'has_history': False}
    
    def get_deep_memories(self, query: str, limit: int = 10) -> List[Dict]:
        """Get deep memory search from database (SLOW but COMPREHENSIVE)"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path, timeout=5.0)
                cursor = conn.cursor()
                
                # Search memories table
                cursor.execute('''
                    SELECT memory_text, category, importance, timestamp
                    FROM memories
                    WHERE memory_text LIKE ?
                    ORDER BY importance DESC, timestamp DESC
                    LIMIT ?
                ''', (f'%{query}%', limit))
                
                memories = []
                for row in cursor.fetchall():
                    memories.append({
                        'text': row[0],
                        'category': row[1],
                        'importance': row[2],
                        'timestamp': row[3]
                    })
                
                conn.close()
                
                print(f"🗄️ Batch Layer: Found {len(memories)} deep memories for '{query[:30]}...'")
                
                return memories
                
        except Exception as e:
            print(f"⚠️ Batch Layer memory search error: {e}")
            return []
    
    def analyze_user_patterns(self, username: str) -> Dict:
        """Analyze user behavior patterns (BATCH JOB)"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path, timeout=5.0)
                cursor = conn.cursor()
                
                # Get all conversations with time analysis
                cursor.execute('''
                    SELECT user_message, timestamp
                    FROM conversations
                    WHERE user_message LIKE ?
                    ORDER BY timestamp
                ''', (f'%{username}%',))
                
                messages = cursor.fetchall()
                conn.close()
                
                if not messages:
                    return {}
                
                # Calculate patterns
                timestamps = [msg[1] for msg in messages if msg[1]]
                if len(timestamps) > 1:
                    # Time between messages
                    intervals = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
                    avg_interval = sum(intervals) / len(intervals) if intervals else 0
                    
                    # Extract common words
                    all_words = []
                    for msg in messages:
                        words = msg[0].lower().split()
                        all_words.extend([w for w in words if len(w) > 4])
                    
                    from collections import Counter
                    common_words = Counter(all_words).most_common(5)
                    
                    return {
                        'total_messages': len(messages),
                        'avg_interval_seconds': avg_interval,
                        'common_topics': [word for word, count in common_words],
                        'first_seen': min(timestamps) if timestamps else 0,
                        'last_seen': max(timestamps) if timestamps else 0
                    }
                
                return {}
                
        except Exception as e:
            print(f"⚠️ Batch Layer pattern analysis error: {e}")
            return {}


# ============================================================================
# SERVING LAYER - Merges Speed + Batch Results
# ============================================================================

class ServingLayer:
    """
    Serving Layer: Merges real-time (speed) and comprehensive (batch) data
    - Prioritizes speed layer for immediate responses
    - Falls back to batch layer for comprehensive data
    - Combines both for optimal accuracy + speed
    """
    
    def __init__(self, speed_layer: SpeedLayer, batch_layer: BatchLayer):
        self.speed_layer = speed_layer
        self.batch_layer = batch_layer
        print("🎯 Serving Layer initialized - merging speed + batch layers")
    
    def get_user_context(self, username: str, platform: str, mode: str = 'hybrid') -> str:
        """
        Get user context with configurable mode
        - 'fast': Speed layer only (< 1ms)
        - 'deep': Batch layer only (10-100ms)
        - 'hybrid': Try speed, fallback to batch (adaptive)
        """
        
        if mode == 'fast':
            # Speed layer only
            context = self.speed_layer.get_recent_context(username, platform, limit=5)
            if context:
                print(f"⚡ Serving Layer: Fast path - {username}")
                return f"Recent context (fast): {context}"
            return ""
        
        elif mode == 'deep':
            # Batch layer only
            deep_context = self.batch_layer.get_deep_user_context(username, platform, limit=10)
            if deep_context['has_history']:
                print(f"🗄️ Serving Layer: Deep path - {username}")
                convs = deep_context['conversations'][:3]
                context_parts = [f"User: {c['user_message'][:80]}... Luna: {c['luna_response'][:80]}..." for c in convs]
                return f"Deep context ({deep_context['total_messages']} total): {' | '.join(context_parts)}"
            return ""
        
        else:  # hybrid
            # Try speed layer first
            speed_context = self.speed_layer.get_recent_context(username, platform, limit=3)
            user_stats = self.speed_layer.get_user_stats(username)
            
            if speed_context and user_stats:
                # We have hot data - use it!
                print(f"⚡ Serving Layer: Hybrid (speed) - {username}")
                return f"Recent: {speed_context} | Stats: {user_stats['message_count']} msgs, topics: {', '.join(user_stats['recent_topics'][:3])}"
            
            # No hot data - fall back to batch layer
            print(f"🗄️ Serving Layer: Hybrid (batch fallback) - {username}")
            deep_context = self.batch_layer.get_deep_user_context(username, platform, limit=5)
            if deep_context['has_history']:
                convs = deep_context['conversations'][:2]
                context_parts = [f"{c['user_message'][:60]}..." for c in convs]
                return f"History ({deep_context['total_messages']} msgs): {' | '.join(context_parts)}"
            
            return ""
    
    def get_response_with_context(self, username: str, user_message: str, platform: str,
                                  require_deep: bool = False) -> Tuple[str, Dict]:
        """
        Get response with appropriate context based on query complexity
        - Simple queries → Speed layer only
        - Complex queries → Speed + Batch merged
        """
        
        # Check if we need deep context
        needs_deep = require_deep or any(word in user_message.lower() for word in 
                                         ['remember', 'history', 'before', 'last time', 'always', 'never'])
        
        if needs_deep:
            # Use hybrid mode for comprehensive context
            context = self.get_user_context(username, platform, mode='hybrid')
            deep_data = self.batch_layer.get_deep_user_context(username, platform, limit=10)
            
            metadata = {
                'path': 'hybrid',
                'speed_layer_used': True,
                'batch_layer_used': True,
                'total_messages': deep_data.get('total_messages', 0)
            }
            
            print(f"🎯 Serving Layer: Hybrid response for {username}")
            return context, metadata
        else:
            # Use fast mode for quick responses
            context = self.get_user_context(username, platform, mode='fast')
            user_stats = self.speed_layer.get_user_stats(username)
            
            metadata = {
                'path': 'fast',
                'speed_layer_used': True,
                'batch_layer_used': False,
                'message_count': user_stats.get('message_count', 0)
            }
            
            print(f"⚡ Serving Layer: Fast response for {username}")
            return context, metadata


# ============================================================================
# LAMBDA ARCHITECTURE COORDINATOR
# ============================================================================

class LunaLambdaArchitecture:
    """
    Main coordinator for Luna's Lambda Architecture
    Manages all three layers and provides unified interface
    """
    
    def __init__(self, db_path: str = 'luna_memories.db'):
        self.speed_layer = SpeedLayer()
        self.batch_layer = BatchLayer(db_path)
        self.serving_layer = ServingLayer(self.speed_layer, self.batch_layer)
        
        # Background batch processing
        self.batch_thread = None
        self.batch_running = False
        
        print("🏗️ Luna Lambda Architecture initialized!")
        print("   ⚡ Speed Layer: Real-time fast path")
        print("   🗄️ Batch Layer: Comprehensive deep path")
        print("   🎯 Serving Layer: Merged intelligent responses")
    
    def process_conversation(self, username: str, user_message: str, luna_response: str,
                           platform: str, emotion: str = 'neutral'):
        """Process a conversation through the lambda pipeline"""
        # Add to speed layer immediately
        self.speed_layer.add_conversation(username, user_message, luna_response, platform, emotion)
        
        # Batch layer will pick it up on next batch run
        print(f"🏗️ Lambda: Processed conversation from {username} ({platform})")
    
    def get_context_for_response(self, username: str, user_message: str, platform: str,
                                mode: str = 'auto') -> Tuple[str, Dict]:
        """
        Get context for generating a response
        mode: 'auto', 'fast', or 'deep'
        """
        if mode == 'auto':
            # Auto-detect based on message complexity
            require_deep = any(word in user_message.lower() for word in 
                             ['remember', 'history', 'before', 'last time', 'always'])
            return self.serving_layer.get_response_with_context(username, user_message, platform, require_deep)
        elif mode == 'fast':
            context = self.serving_layer.get_user_context(username, platform, mode='fast')
            return context, {'path': 'fast'}
        else:  # deep
            context = self.serving_layer.get_user_context(username, platform, mode='deep')
            return context, {'path': 'deep'}
    
    def start_batch_processing(self):
        """Start background batch processing thread"""
        if not self.batch_running:
            self.batch_running = True
            self.batch_thread = threading.Thread(target=self._batch_processing_loop, daemon=True)
            self.batch_thread.start()
            print("🗄️ Batch processing thread started")
    
    def _batch_processing_loop(self):
        """Background batch processing loop"""
        while self.batch_running:
            try:
                time.sleep(60)  # Run every minute
                print("🗄️ Running batch processing cycle...")
                
                # Here you can add batch jobs:
                # - Memory consolidation
                # - Pattern analysis
                # - Database optimization
                # - etc.
                
            except Exception as e:
                print(f"⚠️ Batch processing error: {e}")
    
    def stop_batch_processing(self):
        """Stop background batch processing"""
        self.batch_running = False
        if self.batch_thread:
            self.batch_thread.join(timeout=5)
        print("🗄️ Batch processing stopped")
    
    def get_stats(self) -> Dict:
        """Get architecture statistics"""
        return {
            'speed_layer': {
                'recent_conversations': len(self.speed_layer.recent_conversations),
                'tracked_users': len(self.speed_layer.recent_users),
                'cache_size': len(self.speed_layer.cache)
            },
            'batch_layer': {
                'last_run': self.batch_layer.last_batch_run,
                'interval': self.batch_layer.batch_interval
            },
            'architecture': 'Lambda (Speed + Batch + Serving)'
        }


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

lambda_architecture: Optional[LunaLambdaArchitecture] = None

def initialize_lambda_architecture(db_path: str = 'luna_memories.db') -> LunaLambdaArchitecture:
    """Initialize Luna's Lambda Architecture"""
    global lambda_architecture
    if lambda_architecture is None:
        lambda_architecture = LunaLambdaArchitecture(db_path)
        lambda_architecture.start_batch_processing()
    return lambda_architecture

def get_lambda_architecture() -> Optional[LunaLambdaArchitecture]:
    """Get the lambda architecture instance"""
    return lambda_architecture

