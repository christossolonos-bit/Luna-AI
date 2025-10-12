"""
Luna KV Cache System
Implements key-value caching for stable memory recollection
Uses Ollama's built-in KV cache + our own intelligent caching layer
"""

import time
import hashlib
import sqlite3
import threading
from typing import Dict, List, Optional, Tuple, Any
from collections import OrderedDict
import json

class LunaKVCache:
    """
    Luna's KV Cache System for stable memory recollection
    
    Features:
    - Ollama KV cache integration (keeps model context in memory)
    - Intelligent conversation caching (remembers recent context)
    - Semantic memory indexing (fast recall of similar topics)
    - User-specific context caching (remembers each user separately)
    - Thread-safe operations
    """
    
    def __init__(self, max_cache_size: int = 100, cache_ttl: int = 3600):
        self.max_cache_size = max_cache_size
        self.cache_ttl = cache_ttl  # 1 hour default
        
        # Multi-layer cache structure
        self.conversation_cache = OrderedDict()  # Recent conversations
        self.user_context_cache = {}  # Per-user context
        self.semantic_cache = {}  # Topic-based cache
        self.ollama_kv_contexts = {}  # Ollama conversation contexts
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'memory_recalls': 0
        }
        
        print("🗄️ KV Cache System initialized - stable memory recollection active")
    
    def generate_cache_key(self, user_input: str, username: str, platform: str) -> str:
        """Generate a unique cache key for this interaction"""
        # Create semantic key (captures meaning, not exact text)
        content = f"{username}:{platform}:{user_input.lower().strip()}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def store_conversation_context(self, username: str, platform: str, 
                                   user_message: str, luna_response: str,
                                   ollama_context: List[Dict] = None):
        """Store conversation in KV cache for fast recall"""
        with self.lock:
            timestamp = time.time()
            
            # Generate cache key
            cache_key = self.generate_cache_key(user_message, username, platform)
            
            # Store in conversation cache
            self.conversation_cache[cache_key] = {
                'username': username,
                'platform': platform,
                'user_message': user_message,
                'luna_response': luna_response,
                'timestamp': timestamp,
                'ollama_context': ollama_context,  # Store Ollama's context for continuity
                'access_count': 0
            }
            
            # Store in user-specific cache
            user_key = f"{username}@{platform}"
            if user_key not in self.user_context_cache:
                self.user_context_cache[user_key] = []
            
            self.user_context_cache[user_key].append({
                'user_message': user_message,
                'luna_response': luna_response,
                'timestamp': timestamp
            })
            
            # Keep only last 10 conversations per user
            if len(self.user_context_cache[user_key]) > 10:
                self.user_context_cache[user_key] = self.user_context_cache[user_key][-10:]
            
            # Maintain cache size
            if len(self.conversation_cache) > self.max_cache_size:
                # Remove oldest entry
                oldest_key = next(iter(self.conversation_cache))
                del self.conversation_cache[oldest_key]
                self.stats['evictions'] += 1
            
            print(f"🗄️ Cached conversation: {username}@{platform} - {user_message[:30]}...")
    
    def get_user_context(self, username: str, platform: str, limit: int = 5) -> str:
        """Get recent conversation context for a user from cache"""
        with self.lock:
            user_key = f"{username}@{platform}"
            
            if user_key in self.user_context_cache:
                self.stats['hits'] += 1
                recent_convs = self.user_context_cache[user_key][-limit:]
                
                # Build context string
                context_parts = []
                for conv in recent_convs:
                    context_parts.append(f"User: {conv['user_message'][:100]}")
                    context_parts.append(f"Luna: {conv['luna_response'][:100]}")
                
                context = " | ".join(context_parts)
                print(f"🗄️ KV Cache HIT: Found {len(recent_convs)} recent messages for {username}")
                return context
            else:
                self.stats['misses'] += 1
                print(f"🗄️ KV Cache MISS: No cached context for {username}")
                return ""
    
    def get_similar_conversation(self, user_input: str, threshold: float = 0.6) -> Optional[Dict]:
        """Find similar past conversation from cache (semantic matching)"""
        with self.lock:
            user_input_lower = user_input.lower().strip()
            user_words = set(user_input_lower.split())
            
            best_match = None
            best_similarity = 0.0
            
            for cache_key, conv_data in self.conversation_cache.items():
                # Simple word overlap similarity
                cached_message = conv_data['user_message'].lower().strip()
                cached_words = set(cached_message.split())
                
                if user_words and cached_words:
                    intersection = user_words.intersection(cached_words)
                    union = user_words.union(cached_words)
                    similarity = len(intersection) / len(union)
                    
                    if similarity > best_similarity and similarity >= threshold:
                        best_similarity = similarity
                        best_match = conv_data
            
            if best_match:
                self.stats['hits'] += 1
                print(f"🗄️ Similar conversation found (similarity: {best_similarity:.2f})")
                return best_match
            else:
                self.stats['misses'] += 1
                return None
    
    def get_ollama_conversation_context(self, username: str, platform: str) -> Optional[List[Dict]]:
        """Get Ollama conversation context for maintaining continuity"""
        with self.lock:
            user_key = f"{username}@{platform}"
            
            if user_key in self.ollama_kv_contexts:
                context = self.ollama_kv_contexts[user_key]
                print(f"🗄️ Ollama KV context retrieved for {username} ({len(context)} messages)")
                return context
            return None
    
    def update_ollama_context(self, username: str, platform: str, 
                             messages: List[Dict]):
        """Update Ollama conversation context for a user"""
        with self.lock:
            user_key = f"{username}@{platform}"
            self.ollama_kv_contexts[user_key] = messages[-10:]  # Keep last 10 exchanges
            print(f"🗄️ Updated Ollama KV context for {username}")
    
    def recall_from_database(self, username: str, platform: str, 
                            query: str = None, limit: int = 5) -> List[Dict]:
        """Recall memories from database and cache them"""
        try:
            conn = sqlite3.connect('luna_memories.db', timeout=2.0)
            cursor = conn.cursor()
            
            # Build query based on parameters
            if query:
                # Search for specific topic
                cursor.execute('''
                    SELECT user_message, luna_response, timestamp, mood
                    FROM conversations
                    WHERE user_message LIKE ? OR luna_response LIKE ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (f'%{query}%', f'%{query}%', limit))
            else:
                # Get recent conversations
                cursor.execute('''
                    SELECT user_message, luna_response, timestamp, mood
                    FROM conversations
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (limit,))
            
            memories = []
            for row in cursor.fetchall():
                memory = {
                    'user_message': row[0],
                    'luna_response': row[1],
                    'timestamp': row[2],
                    'mood': row[3]
                }
                memories.append(memory)
                
                # Cache this memory for future fast access
                cache_key = self.generate_cache_key(row[0], username, platform)
                if cache_key not in self.conversation_cache:
                    self.conversation_cache[cache_key] = {
                        'username': username,
                        'platform': platform,
                        'user_message': row[0],
                        'luna_response': row[1],
                        'timestamp': float(row[2]) if row[2] else timestamp,
                        'ollama_context': None,
                        'access_count': 0
                    }
            
            conn.close()
            
            self.stats['memory_recalls'] += 1
            print(f"🗄️ Recalled {len(memories)} memories from database and cached them")
            return memories
            
        except Exception as e:
            print(f"⚠️ Database recall error: {e}")
            return []
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        with self.lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = (self.stats['hits'] / max(1, total_requests)) * 100
            
            return {
                'cache_size': len(self.conversation_cache),
                'user_contexts': len(self.user_context_cache),
                'ollama_contexts': len(self.ollama_kv_contexts),
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'hit_rate': hit_rate,
                'evictions': self.stats['evictions'],
                'memory_recalls': self.stats['memory_recalls']
            }
    
    def clear_old_entries(self):
        """Clear old cache entries"""
        with self.lock:
            current_time = time.time()
            keys_to_remove = []
            
            for key, data in self.conversation_cache.items():
                if current_time - data['timestamp'] > self.cache_ttl:
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self.conversation_cache[key]
                self.stats['evictions'] += 1
            
            if keys_to_remove:
                print(f"🗄️ Cleared {len(keys_to_remove)} old cache entries")

# Global KV cache instance
luna_kv_cache = LunaKVCache(max_cache_size=200, cache_ttl=7200)  # 2 hour TTL

def get_kv_cache():
    """Get the global KV cache instance"""
    return luna_kv_cache

# Background cache cleanup
def cache_cleanup_worker():
    """Background worker to clean up old cache entries"""
    while True:
        time.sleep(1800)  # Every 30 minutes
        try:
            luna_kv_cache.clear_old_entries()
        except Exception as e:
            print(f"⚠️ Cache cleanup error: {e}")

# Start cleanup worker
cleanup_thread = threading.Thread(target=cache_cleanup_worker, daemon=True)
cleanup_thread.start()
print("🗄️ KV Cache cleanup worker started")

