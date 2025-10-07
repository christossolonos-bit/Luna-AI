# luna_graphiti_integration.py
"""
Luna Graphiti Integration
Integrates Graphiti knowledge graph with Luna's existing memory systems
"""

import sqlite3
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

try:
    from graphiti_core import Graphiti
    from graphiti_core.llm_client.openai_client import OpenAIClient, LLMConfig
    from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig
    from graphiti_core.cross_encoder.openai_reranker_client import OpenAIRerankerClient
    GRAPHITI_AVAILABLE = True
except ImportError:
    GRAPHITI_AVAILABLE = False
    print("⚠️ Graphiti not available - install with: pip install graphiti-core")

class LunaGraphitiIntegration:
    """Integration between Luna's memory system and Graphiti knowledge graph"""
    
    def __init__(self, memory_db_path: str = "luna_memories.db"):
        self.memory_db_path = memory_db_path
        self.graphiti = None
        self.is_initialized = False
        
        if GRAPHITI_AVAILABLE:
            self._initialize_graphiti()
    
    def _initialize_graphiti(self):
        """Initialize Graphiti with Luna's configuration"""
        try:
            # Use Luna's existing Ollama setup for Graphiti
            llm_config = LLMConfig(
                api_key="ollama",
                model="hf.co/NousResearch/Nous-Hermes-2-Mistral-7B-DPO-GGUF:Q5_K_M",
                small_model="hf.co/NousResearch/Nous-Hermes-2-Mistral-7B-DPO-GGUF:Q5_K_M",
                base_url="http://127.0.0.1:11434/v1"
            )
            
            # Initialize Graphiti with in-memory graph (no Neo4j required initially)
            self.graphiti = Graphiti(
                "bolt://localhost:7687",  # Will use in-memory if Neo4j not available
                "neo4j",
                "password",
                llm_client=OpenAIClient(config=llm_config),
                embedder=OpenAIEmbedder(
                    config=OpenAIEmbedderConfig(
                        api_key="ollama",
                        embedding_model="nomic-embed-text",
                        embedding_dim=768,
                        base_url="http://127.0.0.1:11434/v1"
                    )
                ),
                cross_encoder=OpenAIRerankerClient(
                    config=LLMConfig(
                        api_key="ollama",
                        model="hf.co/NousResearch/Nous-Hermes-2-Mistral-7B-DPO-GGUF:Q5_K_M",
                        base_url="http://127.0.0.1:11434/v1"
                    )
                )
            )
            
            self.is_initialized = True
            print("✅ Graphiti integration initialized successfully")
            
        except Exception as e:
            print(f"⚠️ Graphiti initialization failed: {e}")
            print("📝 Using fallback mode - will extract conversations but not use graph features")
            self.is_initialized = False
    
    def extract_conversations_from_db(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """Extract conversations from Luna's memory database"""
        conversations = []
        
        try:
            conn = sqlite3.connect(self.memory_db_path)
            cursor = conn.cursor()
            
            # Get recent conversations with context
            query = """
            SELECT 
                id, user_message, luna_response, emotion, context, 
                platform, user_id, timestamp, memory_type
            FROM memories 
            WHERE user_message IS NOT NULL 
            AND luna_response IS NOT NULL 
            AND memory_type IN ('conversation', 'emotional')
            ORDER BY timestamp DESC 
            LIMIT ?
            """
            
            cursor.execute(query, (limit,))
            rows = cursor.fetchall()
            
            for row in rows:
                conversation = {
                    'id': row[0],
                    'user_message': row[1],
                    'luna_response': row[2],
                    'emotion': row[3],
                    'context': row[4],
                    'platform': row[5],
                    'user_id': row[6],
                    'timestamp': row[7],
                    'memory_type': row[8]
                }
                conversations.append(conversation)
            
            conn.close()
            print(f"📊 Extracted {len(conversations)} conversations from Luna's memory database")
            
        except Exception as e:
            print(f"❌ Error extracting conversations: {e}")
        
        return conversations
    
    def create_episode_from_conversation(self, conversation: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a conversation into a Graphiti episode"""
        episode = {
            "source": f"luna_memory_{conversation['id']}",
            "timestamp": conversation['timestamp'],
            "episode": {
                "type": "conversation",
                "participants": [
                    {
                        "name": conversation['user_id'] or "User",
                        "role": "user",
                        "platform": conversation['platform'] or "gui"
                    },
                    {
                        "name": "Luna",
                        "role": "assistant",
                        "platform": conversation['platform'] or "gui"
                    }
                ],
                "content": [
                    {
                        "type": "text",
                        "content": conversation['user_message'],
                        "participant": conversation['user_id'] or "User"
                    },
                    {
                        "type": "text", 
                        "content": conversation['luna_response'],
                        "participant": "Luna"
                    }
                ],
                "context": {
                    "emotion": conversation['emotion'],
                    "memory_type": conversation['memory_type'],
                    "platform": conversation['platform'],
                    "conversation_id": conversation['id']
                }
            }
        }
        return episode
    
    def import_conversations_to_graphiti(self, conversations: List[Dict[str, Any]]) -> bool:
        """Import conversations into Graphiti knowledge graph"""
        if not self.is_initialized or not self.graphiti:
            print("⚠️ Graphiti not initialized - skipping import")
            return False
        
        try:
            episodes = []
            for conversation in conversations:
                episode = self.create_episode_from_conversation(conversation)
                episodes.append(episode)
            
            # Import episodes into Graphiti
            result = self.graphiti.ingest(episodes)
            print(f"✅ Imported {len(episodes)} conversations into Graphiti knowledge graph")
            return True
            
        except Exception as e:
            print(f"❌ Error importing conversations to Graphiti: {e}")
            return False
    
    def search_graphiti_memories(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search Luna's memories using Graphiti's advanced retrieval"""
        if not self.is_initialized or not self.graphiti:
            # Fallback to simple text search
            return self._fallback_search(query, limit)
        
        try:
            # Use Graphiti's hybrid retrieval
            results = self.graphiti.retrieve(query, limit=limit)
            
            # Format results for Luna's system
            formatted_results = []
            for result in results:
                formatted_result = {
                    'content': result.get('content', ''),
                    'score': result.get('score', 0.0),
                    'type': result.get('type', 'unknown'),
                    'system': 'graphiti',
                    'metadata': result.get('metadata', {})
                }
                formatted_results.append(formatted_result)
            
            print(f"🔍 Graphiti search found {len(formatted_results)} relevant memories")
            return formatted_results
            
        except Exception as e:
            print(f"⚠️ Graphiti search failed: {e}")
            return self._fallback_search(query, limit)
    
    def _fallback_search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Fallback search using direct database queries"""
        results = []
        
        try:
            conn = sqlite3.connect(self.memory_db_path)
            cursor = conn.cursor()
            
            # Simple text search in user messages and Luna responses
            search_query = """
            SELECT user_message, luna_response, emotion, context, platform, timestamp
            FROM memories 
            WHERE (user_message LIKE ? OR luna_response LIKE ?)
            AND user_message IS NOT NULL 
            AND luna_response IS NOT NULL
            ORDER BY timestamp DESC 
            LIMIT ?
            """
            
            search_term = f"%{query}%"
            cursor.execute(search_query, (search_term, search_term, limit))
            rows = cursor.fetchall()
            
            for row in rows:
                result = {
                    'content': f"User: {row[0]}\nLuna: {row[1]}",
                    'score': 0.8,  # Default score for fallback
                    'type': 'conversation',
                    'system': 'database_fallback',
                    'metadata': {
                        'emotion': row[2],
                        'context': row[3],
                        'platform': row[4],
                        'timestamp': row[5]
                    }
                }
                results.append(result)
            
            conn.close()
            print(f"🔍 Fallback search found {len(results)} relevant memories")
            
        except Exception as e:
            print(f"❌ Fallback search failed: {e}")
        
        return results
    
    def get_conversation_insights(self) -> Dict[str, Any]:
        """Get insights about Luna's conversations using Graphiti"""
        if not self.is_initialized or not self.graphiti:
            return {'error': 'Graphiti not initialized'}
        
        try:
            # Get graph statistics and insights
            stats = self.graphiti.get_stats()
            
            insights = {
                'total_nodes': stats.get('nodes', 0),
                'total_edges': stats.get('edges', 0),
                'total_episodes': stats.get('episodes', 0),
                'top_entities': stats.get('top_entities', []),
                'conversation_patterns': stats.get('patterns', []),
                'system': 'graphiti'
            }
            
            return insights
            
        except Exception as e:
            print(f"⚠️ Error getting insights: {e}")
            return {'error': str(e)}
    
    def add_new_conversation(self, user_message: str, luna_response: str, 
                           emotion: str = 'neutral', context: str = 'general',
                           platform: str = 'gui', user_id: str = None) -> bool:
        """Add a new conversation to both Luna's database and Graphiti"""
        if not self.is_initialized or not self.graphiti:
            return False
        
        try:
            # Create episode for new conversation
            conversation = {
                'id': int(time.time() * 1000),  # Generate unique ID
                'user_message': user_message,
                'luna_response': luna_response,
                'emotion': emotion,
                'context': context,
                'platform': platform,
                'user_id': user_id,
                'timestamp': time.time(),
                'memory_type': 'conversation'
            }
            
            episode = self.create_episode_from_conversation(conversation)
            result = self.graphiti.ingest([episode])
            
            print(f"✅ Added new conversation to Graphiti knowledge graph")
            return True
            
        except Exception as e:
            print(f"❌ Error adding conversation to Graphiti: {e}")
            return False

# Global instance
luna_graphiti = None

def initialize_luna_graphiti():
    """Initialize Luna's Graphiti integration"""
    global luna_graphiti
    
    if not GRAPHITI_AVAILABLE:
        print("⚠️ Graphiti not available - install with: pip install graphiti-core")
        return False
    
    try:
        luna_graphiti = LunaGraphitiIntegration()
        
        if luna_graphiti.is_initialized:
            print("🧠 Luna Graphiti integration initialized")
            
            # Import existing conversations
            conversations = luna_graphiti.extract_conversations_from_db(limit=500)
            if conversations:
                luna_graphiti.import_conversations_to_graphiti(conversations)
            
            return True
        else:
            print("⚠️ Luna Graphiti integration failed to initialize")
            return False
            
    except Exception as e:
        print(f"❌ Error initializing Luna Graphiti: {e}")
        return False

def search_luna_graphiti_memories(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Search Luna's memories using Graphiti"""
    global luna_graphiti
    
    if not luna_graphiti:
        return []
    
    return luna_graphiti.search_graphiti_memories(query, limit)

def add_luna_graphiti_conversation(user_message: str, luna_response: str, 
                                 emotion: str = 'neutral', context: str = 'general',
                                 platform: str = 'gui', user_id: str = None) -> bool:
    """Add a new conversation to Luna's Graphiti knowledge graph"""
    global luna_graphiti
    
    if not luna_graphiti:
        return False
    
    return luna_graphiti.add_new_conversation(user_message, luna_response, 
                                            emotion, context, platform, user_id)

def get_luna_graphiti_insights() -> Dict[str, Any]:
    """Get insights from Luna's Graphiti knowledge graph"""
    global luna_graphiti
    
    if not luna_graphiti:
        return {'error': 'Graphiti not initialized'}
    
    return luna_graphiti.get_conversation_insights()
