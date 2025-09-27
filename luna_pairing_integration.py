#!/usr/bin/env python3
"""
Luna Pairing Engine Integration
Integrates the advanced pairing engine with Luna's existing memory systems
"""

import json
import os
import re
import random
import numpy as np
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Set
from difflib import SequenceMatcher
from collections import defaultdict, Counter

# Import Luna's existing memory systems
try:
    from bm25_memory_system import get_bm25_system
    from hybrid_retrieval_system import hybrid_search_memories
    from luna_mindmap_system import get_mindmap_system
    # Note: get_memory_compressor function doesn't exist, using memory_compressor class directly
    from memory_compression import MemoryCompressor
    LUNA_MEMORY_SYSTEMS_AVAILABLE = True
    print("🧠 Luna memory systems available for pairing integration")
except ImportError as e:
    LUNA_MEMORY_SYSTEMS_AVAILABLE = False
    print(f"⚠️ Luna memory systems not available: {e}")

# Try to import sentence-transformers, fall back to simple embedding if not available
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDING_AVAILABLE = True
    print("🔤 Sentence transformers available for semantic matching")
except ImportError:
    EMBEDDING_AVAILABLE = False
    print("⚠️ Sentence transformers not available. Using simple embedding fallback.")

class LunaPairingEngine:
    """Luna's integrated pairing engine for conversation matching"""
    
    def __init__(self, db_path: str = "luna_memories.db"):
        self.db_path = db_path
        self.embeddings = {}
        self.responses = {}
        self.stats = {
            "total_embeddings": 0,
            "total_queries": 0,
            "average_similarity": 0.0,
            "successful_matches": 0
        }
        
        # Initialize embedding model if available
        if EMBEDDING_AVAILABLE:
            try:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                print("✅ Sentence transformer model loaded")
            except Exception as e:
                print(f"⚠️ Failed to load sentence transformer: {e}")
                self.embedding_model = None
        else:
            self.embedding_model = None
        
        # Initialize Luna memory systems
        self.bm25_system = None
        self.mindmap_system = None
        self.memory_compressor = None
        
        if LUNA_MEMORY_SYSTEMS_AVAILABLE:
            try:
                self.bm25_system = get_bm25_system()
                self.mindmap_system = get_mindmap_system()
                self.memory_compressor = MemoryCompressor()
                print("✅ Luna memory systems connected to pairing engine")
            except Exception as e:
                print(f"⚠️ Could not connect to Luna memory systems: {e}")
        
        # Load existing data
        self.load()
        
        print("🎯 Luna Pairing Engine initialized and ready!")
    
    def encode(self, text: str) -> np.ndarray:
        """Encode text to embedding vector"""
        if self.embedding_model:
            return self.embedding_model.encode(text)
        else:
            # Simple fallback embedding using word frequency
            return self._simple_embedding(text)
    
    def _simple_embedding(self, text: str) -> np.ndarray:
        """Simple fallback embedding using word frequency"""
        words = re.findall(r'\b\w+\b', text.lower())
        word_freq = Counter(words)
        
        # Create a simple 100-dimensional embedding
        embedding = np.zeros(100)
        for i, (word, freq) in enumerate(word_freq.items()):
            if i < 100:
                embedding[i] = freq
        
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding
    
    def add_conversation_pair(self, user_input: str, luna_response: str, metadata: Dict = None) -> str:
        """Add a conversation pair to Luna's pairing database"""
        if not user_input.strip() or not luna_response.strip():
            return None
        
        # Create unique ID
        pair_id = f"pair_{len(self.embeddings) + 1}_{int(datetime.now().timestamp())}"
        
        # Create embedding for the user input
        embedding = self.encode(user_input)
        
        # Store the pair
        self.embeddings[pair_id] = embedding
        self.responses[pair_id] = {
            "user_input": user_input,
            "luna_response": luna_response,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "usage_count": 0,
            "success_count": 0,
            "source": metadata.get("source", "unknown") if metadata else "unknown"
        }
        
        self.stats["total_embeddings"] = len(self.embeddings)
        self.save()
        
        print(f"💾 Added conversation pair: {pair_id}")
        return pair_id
    
    def find_best_response(self, user_input: str, top_k: int = 3, min_similarity: float = 0.3) -> List[Tuple[str, float, Dict]]:
        """Find best matching responses using semantic similarity"""
        if not self.embeddings:
            return []
        
        self.stats["total_queries"] += 1
        
        # Encode the user input
        query_vec = self.encode(user_input)
        
        # Calculate similarities
        similarities = []
        for pair_id, embedding in self.embeddings.items():
            # Cosine similarity
            similarity = np.dot(query_vec, embedding) / (np.linalg.norm(query_vec) * np.linalg.norm(embedding))
            
            if similarity >= min_similarity:
                response_data = self.responses[pair_id]
                similarities.append((pair_id, similarity, response_data))
        
        # Sort by similarity and return top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_matches = similarities[:top_k]
        
        # Update statistics
        if top_matches:
            avg_sim = sum(sim for _, sim, _ in top_matches) / len(top_matches)
            self.stats["average_similarity"] = avg_sim
            self.stats["successful_matches"] += 1
        
        return top_matches
    
    def hybrid_search_with_luna_memory(self, user_input: str, limit: int = 5) -> List[Dict]:
        """Enhanced search combining pairing engine with Luna's memory systems"""
        results = []
        
        # 1. Get pairing engine results
        pairing_results = self.find_best_response(user_input, top_k=limit, min_similarity=0.2)
        for pair_id, similarity, data in pairing_results:
            results.append({
                "content": data["luna_response"],
                "similarity": similarity,
                "source": "pairing_engine",
                "metadata": data["metadata"],
                "type": "conversation_pair"
            })
        
        # 2. Get BM25 results if available
        if self.bm25_system:
            try:
                bm25_results = self.bm25_system.search_memories(user_input, limit=limit)
                for result in bm25_results:
                    results.append({
                        "content": result["content"],
                        "similarity": result["score"],
                        "source": "bm25",
                        "metadata": result.get("metadata", {}),
                        "type": "memory"
                    })
            except Exception as e:
                print(f"⚠️ BM25 search error: {e}")
        
        # 3. Get hybrid retrieval results if available
        if LUNA_MEMORY_SYSTEMS_AVAILABLE:
            try:
                hybrid_results = hybrid_search_memories(user_input, self.bm25_system, limit=limit)
                for result in hybrid_results:
                    results.append({
                        "content": result["content"],
                        "similarity": result["score"],
                        "source": "hybrid_retrieval",
                        "metadata": result.get("metadata", {}),
                        "type": "hybrid_memory"
                    })
            except Exception as e:
                print(f"⚠️ Hybrid retrieval error: {e}")
        
        # 4. Get mind-map results if available
        if self.mindmap_system:
            try:
                mindmap_results = self.mindmap_system.search_related_memories(user_input, limit=limit)
                for result in mindmap_results:
                    results.append({
                        "content": result["content"],
                        "similarity": result["relevance_score"],
                        "source": "mindmap",
                        "metadata": result.get("metadata", {}),
                        "type": "knowledge_graph"
                    })
            except Exception as e:
                print(f"⚠️ Mind-map search error: {e}")
        
        # Sort all results by similarity
        results.sort(key=lambda x: x["similarity"], reverse=True)
        
        # Remove duplicates and return top results
        seen_content = set()
        unique_results = []
        for result in results:
            content_hash = hash(result["content"][:100])  # Use first 100 chars as hash
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                unique_results.append(result)
                if len(unique_results) >= limit:
                    break
        
        return unique_results
    
    def learn_from_conversation(self, user_input: str, luna_response: str, success: bool = True, source: str = "gui"):
        """Learn from a conversation by adding it to the pairing database"""
        try:
            # Add the conversation pair
            metadata = {
                "source": source,
                "success": success,
                "timestamp": datetime.now().isoformat()
            }
            
            pair_id = self.add_conversation_pair(user_input, luna_response, metadata)
            
            if pair_id:
                # Update success count if the response was successful
                if success:
                    self.responses[pair_id]["success_count"] += 1
                
                # Update usage count
                self.responses[pair_id]["usage_count"] += 1
                
                print(f"🧠 Learned from conversation: {source} - Success: {success}")
                
                # Save the updated data
                self.save()
                
                return True
        except Exception as e:
            print(f"⚠️ Error learning from conversation: {e}")
            return False
    
    def get_conversation_suggestions(self, user_input: str, limit: int = 3) -> List[str]:
        """Get conversation suggestions based on similar past interactions"""
        matches = self.find_best_response(user_input, top_k=limit, min_similarity=0.4)
        
        suggestions = []
        for _, similarity, data in matches:
            if similarity > 0.5:  # Only suggest high-similarity matches
                suggestions.append(data["luna_response"])
        
        return suggestions
    
    def get_statistics(self) -> Dict:
        """Get pairing engine statistics"""
        return {
            **self.stats,
            "total_pairs": len(self.embeddings),
            "embedding_model": "sentence-transformers" if self.embedding_model else "simple_fallback",
            "luna_memory_integration": LUNA_MEMORY_SYSTEMS_AVAILABLE,
            "bm25_connected": self.bm25_system is not None,
            "mindmap_connected": self.mindmap_system is not None
        }
    
    def save(self):
        """Save pairing data to file"""
        try:
            data = {
                "embeddings": {k: v.tolist() for k, v in self.embeddings.items()},
                "responses": self.responses,
                "stats": self.stats,
                "last_updated": datetime.now().isoformat()
            }
            
            with open("luna_pairing_data.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print("💾 Pairing data saved")
        except Exception as e:
            print(f"⚠️ Error saving pairing data: {e}")
    
    def load(self):
        """Load pairing data from file"""
        try:
            if os.path.exists("luna_pairing_data.json"):
                with open("luna_pairing_data.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Load embeddings
                self.embeddings = {k: np.array(v) for k, v in data.get("embeddings", {}).items()}
                
                # Load responses
                self.responses = data.get("responses", {})
                
                # Load stats
                self.stats.update(data.get("stats", {}))
                
                print(f"📂 Loaded {len(self.embeddings)} conversation pairs")
            else:
                print("📂 No existing pairing data found, starting fresh")
        except Exception as e:
            print(f"⚠️ Error loading pairing data: {e}")

# Global instance
_luna_pairing_engine = None

def get_luna_pairing_engine() -> LunaPairingEngine:
    """Get the global Luna pairing engine instance"""
    global _luna_pairing_engine
    if _luna_pairing_engine is None:
        _luna_pairing_engine = LunaPairingEngine()
    return _luna_pairing_engine

def initialize_luna_pairing_engine():
    """Initialize the Luna pairing engine"""
    global _luna_pairing_engine
    if _luna_pairing_engine is None:
        _luna_pairing_engine = LunaPairingEngine()
        print("🎯 Luna Pairing Engine initialized!")
    return _luna_pairing_engine

if __name__ == "__main__":
    # Test the pairing engine
    engine = initialize_luna_pairing_engine()
    
    # Test adding a conversation pair
    engine.add_conversation_pair(
        "Hello Luna, how are you?",
        "Hello! I'm doing great, thank you for asking! How are you doing today?",
        {"source": "test", "mood": "happy"}
    )
    
    # Test finding matches
    matches = engine.find_best_response("Hi Luna, how are you feeling?")
    print(f"Found {len(matches)} matches")
    
    # Test hybrid search
    hybrid_results = engine.hybrid_search_with_luna_memory("Hello")
    print(f"Hybrid search found {len(hybrid_results)} results")
    
    # Show statistics
    stats = engine.get_statistics()
    print(f"Pairing engine statistics: {stats}")
