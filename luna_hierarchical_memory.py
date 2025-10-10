"""
Luna Hierarchical Memory System
Multi-layered memory retrieval with importance ranking and intelligent selection
"""

import sqlite3
import time
import threading
from typing import List, Dict, Any, Optional
from collections import defaultdict
from datetime import datetime, timedelta
import re

class HierarchicalMemorySystem:
    """
    Retrieves memories in layers of importance and lets Luna choose which to use
    
    Layers (highest to lowest priority):
    1. Critical/Emotional memories (importance 4-5)
    2. Recent conversations (last 24 hours)
    3. User-specific history (this exact user)
    4. Topic-relevant memories (semantic match)
    5. General context (background knowledge)
    """
    
    def __init__(self, db_path: str = "luna_memories.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        print("🧠 Hierarchical Memory System initialized")
    
    def get_layered_context(self, 
                           user_input: str, 
                           username: str, 
                           platform: str = 'gui',
                           max_memories_per_layer: int = 3) -> Dict[str, List[Dict]]:
        """
        Get memories organized by importance layers
        Returns: Dict with layers as keys, sorted by importance
        """
        try:
            all_layers = {
                'critical': [],      # Layer 1: Critical/Emotional (importance 4-5)
                'recent': [],        # Layer 2: Recent conversations (24h)
                'user_history': [],  # Layer 3: This user's history
                'topic_relevant': [], # Layer 4: Topic-relevant
                'general': []        # Layer 5: General context
            }
            
            with self.lock:
                conn = sqlite3.connect(self.db_path, timeout=5.0)
                conn.execute('PRAGMA journal_mode=WAL')
                cursor = conn.cursor()
                
                # Layer 1: Critical/Emotional memories
                cursor.execute('''
                    SELECT content, mood, importance, timestamp, memory_type
                    FROM memories
                    WHERE importance >= 4
                    ORDER BY importance DESC, timestamp DESC
                    LIMIT ?
                ''', (max_memories_per_layer,))
                
                for row in cursor.fetchall():
                    all_layers['critical'].append({
                        'content': row[0],
                        'mood': row[1],
                        'importance': row[2],
                        'timestamp': row[3],
                        'type': row[4],
                        'layer': 1,
                        'layer_name': 'critical'
                    })
                
                # Layer 2: Recent conversations (last 24 hours)
                yesterday = (datetime.now() - timedelta(hours=24)).isoformat()
                try:
                    cursor.execute('''
                        SELECT user_message, luna_response, mood, timestamp
                        FROM conversations
                        WHERE timestamp > ?
                        ORDER BY timestamp DESC
                        LIMIT ?
                    ''', (yesterday, max_memories_per_layer))
                    
                    for row in cursor.fetchall():
                        all_layers['recent'].append({
                            'content': f"User: {row[0]} | Luna: {row[1]}",
                            'mood': row[2],
                            'importance': 3,  # Recent = important
                            'timestamp': row[3],
                            'type': 'conversation',
                            'layer': 2,
                            'layer_name': 'recent'
                        })
                except sqlite3.OperationalError as db_error:
                    # Table might not exist yet or schema mismatch
                    print(f"⚠️ Hierarchical Memory: Conversations table not ready - {db_error}")
                    pass
                
                # Layer 3: User-specific history
                try:
                    cursor.execute('''
                        SELECT user_message, luna_response, mood, timestamp
                        FROM conversations
                        WHERE user_message LIKE ? OR luna_response LIKE ?
                        ORDER BY timestamp DESC
                        LIMIT ?
                    ''', (f'%{username}%', f'%{username}%', max_memories_per_layer))
                    
                    for row in cursor.fetchall():
                        all_layers['user_history'].append({
                            'content': f"Conversation with {username}: {row[0]} | Luna: {row[1]}",
                            'mood': row[2],
                            'importance': 3,
                            'timestamp': row[3],
                            'type': 'user_conversation',
                            'layer': 3,
                            'layer_name': 'user_history'
                        })
                except sqlite3.OperationalError as db_error:
                    print(f"⚠️ Hierarchical Memory: User history query failed - {db_error}")
                
                # Layer 4: Topic-relevant memories (semantic search)
                keywords = self._extract_keywords(user_input)
                if keywords:
                    # Build search query
                    search_conditions = []
                    search_params = []
                    for keyword in keywords[:5]:
                        search_conditions.append("(content LIKE ? OR user_message LIKE ? OR luna_response LIKE ?)")
                        search_params.extend([f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'])
                    
                    search_query = " OR ".join(search_conditions)
                    
                    # Search memories
                    cursor.execute(f'''
                        SELECT content, mood, importance, timestamp, memory_type
                        FROM memories
                        WHERE {search_query}
                        ORDER BY importance DESC, timestamp DESC
                        LIMIT ?
                    ''', search_params + [max_memories_per_layer])
                    
                    for row in cursor.fetchall():
                        all_layers['topic_relevant'].append({
                            'content': row[0],
                            'mood': row[1],
                            'importance': row[2],
                            'timestamp': row[3],
                            'type': row[4],
                            'layer': 4,
                            'layer_name': 'topic_relevant'
                        })
                    
                    # Also search conversations
                    try:
                        cursor.execute(f'''
                            SELECT user_message, luna_response, mood, timestamp
                            FROM conversations
                            WHERE {search_query}
                            ORDER BY timestamp DESC
                            LIMIT ?
                        ''', search_params + [max_memories_per_layer])
                        
                        for row in cursor.fetchall():
                            all_layers['topic_relevant'].append({
                                'content': f"Related: {row[0]} | Luna: {row[1]}",
                                'mood': row[2],
                                'importance': 2,
                                'timestamp': row[3],
                                'type': 'topic_conversation',
                                'layer': 4,
                                'layer_name': 'topic_relevant'
                            })
                    except sqlite3.OperationalError as conv_error:
                        print(f"⚠️ Hierarchical Memory: Topic conversations query failed - {conv_error}")
                
                # Layer 5: General context (recent general memories)
                cursor.execute('''
                    SELECT content, mood, importance, timestamp, memory_type
                    FROM memories
                    WHERE importance >= 2
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (max_memories_per_layer,))
                
                for row in cursor.fetchall():
                    all_layers['general'].append({
                        'content': row[0],
                        'mood': row[1],
                        'importance': row[2],
                        'timestamp': row[3],
                        'type': row[4],
                        'layer': 5,
                        'layer_name': 'general'
                    })
                
                conn.close()
                
                # Print layer statistics
                layer_counts = {k: len(v) for k, v in all_layers.items() if v}
                if layer_counts:
                    print(f"🧠 Memory layers retrieved: {layer_counts}")
                
                return all_layers
                
        except Exception as e:
            print(f"❌ Error getting layered context: {e}")
            return {
                'critical': [], 'recent': [], 'user_history': [],
                'topic_relevant': [], 'general': []
            }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text"""
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                     'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 
                     'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
        
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 3]
        return keywords[:10]  # Top 10 keywords
    
    def format_context_for_luna(self, layers: Dict[str, List[Dict]], 
                                max_total_memories: int = 10) -> str:
        """
        Format layered memories into a readable context for Luna with selection guidance
        """
        try:
            context_parts = []
            memory_count = 0
            
            # Layer 1: Critical/Emotional (ALWAYS include if available)
            if layers['critical']:
                context_parts.append("🔴 CRITICAL MEMORIES (Use these first):")
                for mem in layers['critical'][:3]:
                    context_parts.append(f"  - [{mem['type']}] {mem['content'][:150]}...")
                    memory_count += 1
            
            # Layer 2: Recent conversations (High priority)
            if layers['recent'] and memory_count < max_total_memories:
                context_parts.append("\n🟠 RECENT CONVERSATIONS (Last 24 hours):")
                for mem in layers['recent'][:2]:
                    context_parts.append(f"  - {mem['content'][:120]}...")
                    memory_count += 1
            
            # Layer 3: User-specific history (Personalization)
            if layers['user_history'] and memory_count < max_total_memories:
                context_parts.append("\n🟡 YOUR HISTORY WITH THIS USER:")
                for mem in layers['user_history'][:2]:
                    context_parts.append(f"  - {mem['content'][:120]}...")
                    memory_count += 1
            
            # Layer 4: Topic-relevant (Context)
            if layers['topic_relevant'] and memory_count < max_total_memories:
                context_parts.append("\n🟢 RELEVANT MEMORIES:")
                remaining = max_total_memories - memory_count
                for mem in layers['topic_relevant'][:remaining]:
                    context_parts.append(f"  - {mem['content'][:100]}...")
                    memory_count += 1
            
            # Layer 5: General context (Background)
            if layers['general'] and memory_count < max_total_memories:
                context_parts.append("\n🔵 GENERAL CONTEXT:")
                remaining = max_total_memories - memory_count
                for mem in layers['general'][:remaining]:
                    context_parts.append(f"  - {mem['content'][:80]}...")
                    memory_count += 1
            
            if context_parts:
                header = f"📚 LUNA'S MEMORY LAYERS ({memory_count} memories retrieved):\n"
                header += "Choose which memories are most relevant to your response. You don't need to use all of them.\n\n"
                return header + "\n".join(context_parts)
            
            return ""
            
        except Exception as e:
            print(f"❌ Error formatting context: {e}")
            return ""
    
    def get_intelligent_context(self, user_input: str, username: str, 
                               platform: str = 'gui', source: str = 'gui') -> str:
        """
        Get intelligently selected context for Luna's response
        Returns formatted context string ready for prompt injection
        """
        try:
            # Get all layers
            layers = self.get_layered_context(
                user_input=user_input,
                username=username,
                platform=platform,
                max_memories_per_layer=3
            )
            
            # Format for Luna with selection guidance
            formatted_context = self.format_context_for_luna(
                layers=layers,
                max_total_memories=10
            )
            
            if formatted_context:
                print(f"🧠 Hierarchical memory context prepared for {username} ({source})")
                return formatted_context
            else:
                print(f"🧠 No hierarchical memories found for this interaction")
                return ""
                
        except Exception as e:
            print(f"❌ Error getting intelligent context: {e}")
            return ""
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get statistics about memory distribution"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path, timeout=5.0)
                cursor = conn.cursor()
                
                # Get total counts
                cursor.execute('SELECT COUNT(*) FROM memories')
                total_memories = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM conversations')
                total_conversations = cursor.fetchone()[0]
                
                # Get importance distribution
                cursor.execute('''
                    SELECT importance, COUNT(*) 
                    FROM memories 
                    GROUP BY importance 
                    ORDER BY importance DESC
                ''')
                importance_dist = dict(cursor.fetchall())
                
                # Get recent activity
                yesterday = (datetime.now() - timedelta(hours=24)).isoformat()
                cursor.execute('SELECT COUNT(*) FROM conversations WHERE timestamp > ?', (yesterday,))
                recent_conversations = cursor.fetchone()[0]
                
                conn.close()
                
                return {
                    'total_memories': total_memories,
                    'total_conversations': total_conversations,
                    'recent_conversations_24h': recent_conversations,
                    'importance_distribution': importance_dist,
                    'critical_memories': importance_dist.get(5, 0) + importance_dist.get(4, 0)
                }
                
        except Exception as e:
            print(f"❌ Error getting memory statistics: {e}")
            return {}

# Global instance
hierarchical_memory_system = None

def initialize_hierarchical_memory() -> HierarchicalMemorySystem:
    """Initialize the hierarchical memory system"""
    global hierarchical_memory_system
    if not hierarchical_memory_system:
        hierarchical_memory_system = HierarchicalMemorySystem()
    return hierarchical_memory_system

def get_hierarchical_memory() -> Optional[HierarchicalMemorySystem]:
    """Get the hierarchical memory system"""
    return hierarchical_memory_system

def get_intelligent_memory_context(user_input: str, username: str, 
                                   platform: str = 'gui', source: str = 'gui') -> str:
    """
    Get intelligently selected memory context for Luna's response
    This is the main function to call for memory retrieval
    """
    if hierarchical_memory_system:
        return hierarchical_memory_system.get_intelligent_context(
            user_input=user_input,
            username=username,
            platform=platform,
            source=source
        )
    return ""

def get_memory_stats() -> Dict[str, Any]:
    """Get memory statistics"""
    if hierarchical_memory_system:
        return hierarchical_memory_system.get_memory_statistics()
    return {'error': 'System not initialized'}

