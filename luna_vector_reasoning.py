"""
🧠 Luna Vector Reasoning System
==============================

Advanced vector reasoning capabilities that enable Luna to reason across
semantic spaces, combining memory retrieval with logical inference.

Features:
- Semantic reasoning across memory vectors
- Temporal pattern recognition
- Emotional reasoning chains
- Cross-memory insight generation
- Predictive reasoning capabilities
- Meta-cognitive reasoning
"""

import numpy as np
import sqlite3
import json
import time
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any, Union
from dataclasses import dataclass
import hashlib

try:
    from sentence_transformers import SentenceTransformer
    print("SUCCESS: sentence-transformers available for vector reasoning")
except ImportError:
    print("WARNING: sentence-transformers not installed - vector reasoning will use fallback")
    SentenceTransformer = None

@dataclass
class ReasoningResult:
    """Result of vector reasoning operation"""
    query: str
    reasoning_chain: List[Dict]
    insights: List[str]
    confidence: float
    temporal_patterns: Dict
    emotional_context: Dict
    cross_memory_connections: List[Dict]
    predictions: List[str]
    meta_cognitive_notes: List[str]

class VectorReasoningEngine:
    """Advanced vector reasoning engine for Luna"""
    
    def __init__(self, db_path: str = "luna_vector_reasoning.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        
        # Initialize embedding model
        if SentenceTransformer:
            try:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                self.embeddings_enabled = True
                print("SUCCESS: Vector reasoning embeddings enabled")
            except Exception as e:
                print(f"WARNING: Failed to load embedding model: {e}")
                self.embedding_model = None
                self.embeddings_enabled = False
        else:
            self.embedding_model = None
            self.embeddings_enabled = False
            print("WARNING: Vector reasoning using text-based fallback")
        
        self._initialize_reasoning_database()
    
    def _initialize_reasoning_database(self):
        """Initialize database for vector reasoning"""
        cursor = self.conn.cursor()
        
        # Reasoning chains table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reasoning_chains (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_hash TEXT NOT NULL,
                query_text TEXT NOT NULL,
                reasoning_steps TEXT,  -- JSON array
                insights TEXT,  -- JSON array
                confidence REAL,
                temporal_patterns TEXT,  -- JSON
                emotional_context TEXT,  -- JSON
                cross_connections TEXT,  -- JSON
                predictions TEXT,  -- JSON
                meta_notes TEXT,  -- JSON
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reasoning_vector BLOB  -- Vector embedding
            )
        ''')
        
        # Memory reasoning connections
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory_reasoning_connections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_id TEXT NOT NULL,
                reasoning_chain_id INTEGER,
                connection_strength REAL,
                connection_type TEXT,  -- semantic, temporal, emotional, causal
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (reasoning_chain_id) REFERENCES reasoning_chains(id)
            )
        ''')
        
        # Reasoning patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reasoning_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT NOT NULL,  -- temporal, emotional, semantic, causal
                pattern_data TEXT,  -- JSON
                frequency INTEGER DEFAULT 1,
                confidence REAL,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                pattern_vector BLOB
            )
        ''')
        
        # Meta-cognitive insights
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meta_cognitive_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                insight_type TEXT NOT NULL,  -- reasoning_about_reasoning, learning_patterns, etc.
                insight_content TEXT NOT NULL,
                confidence REAL,
                supporting_evidence TEXT,  -- JSON
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        print("SUCCESS: Vector reasoning database initialized")
    
    def _generate_embedding(self, text: str) -> bytes:
        """Generate vector embedding for text"""
        if not self.embeddings_enabled or not self.embedding_model:
            return None
        
        try:
            embedding = self.embedding_model.encode(text)
            return embedding.astype(np.float32).tobytes()
        except Exception as e:
            print(f"WARNING: Failed to generate embedding: {e}")
            return None
    
    def _calculate_similarity(self, embedding1: bytes, embedding2: bytes) -> float:
        """Calculate cosine similarity between embeddings"""
        if not embedding1 or not embedding2:
            return 0.0
        
        try:
            vec1 = np.frombuffer(embedding1, dtype=np.float32)
            vec2 = np.frombuffer(embedding2, dtype=np.float32)
            
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return float(dot_product / (norm1 * norm2))  # Convert to Python float
        except Exception as e:
            print(f"WARNING: Failed to calculate similarity: {e}")
            return 0.0
    
    def _convert_numpy_types(self, obj):
        """Recursively convert numpy types to Python types for JSON serialization"""
        if isinstance(obj, dict):
            return {key: self._convert_numpy_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_numpy_types(item) for item in obj]
        elif hasattr(obj, 'item'):  # numpy scalar
            return obj.item()
        elif hasattr(obj, 'tolist'):  # numpy array
            return obj.tolist()
        elif hasattr(obj, 'dtype'):  # numpy dtype
            return float(obj) if np.issubdtype(obj.dtype, np.floating) else int(obj)
        else:
            return obj
    
    def _get_query_hash(self, query: str) -> str:
        """Generate hash for query"""
        return hashlib.md5(query.encode()).hexdigest()[:12]
    
    def reason_across_memories(self, query: str, username: str, 
                             dna_memory_system=None, understanding_engine=None,
                             usernames: List[str] = None) -> ReasoningResult:
        """Main vector reasoning function. usernames: aliases to merge (e.g. Chris, solonaras)."""
        
        # Generate query embedding
        query_embedding = self._generate_embedding(query)
        query_hash = self._get_query_hash(query)
        
        # Check if we have cached reasoning for this query
        cached_result = self._get_cached_reasoning(query_hash)
        if cached_result:
            return cached_result
        
        # Step 1: Semantic memory retrieval (merge across aliases)
        semantic_memories = self._retrieve_semantic_memories(query, username, dna_memory_system, usernames=usernames)
        
        # Step 2: Temporal pattern analysis
        temporal_patterns = self._analyze_temporal_patterns(semantic_memories, username)
        
        # Step 3: Emotional reasoning
        emotional_context = self._analyze_emotional_patterns(semantic_memories, query)
        
        # Step 4: Cross-memory connections
        cross_connections = self._find_cross_memory_connections(semantic_memories, query)
        
        # Step 5: Build reasoning chain
        reasoning_chain = self._build_reasoning_chain(
            query, semantic_memories, temporal_patterns, 
            emotional_context, cross_connections
        )
        
        # Step 6: Generate insights
        insights = self._generate_insights(reasoning_chain, semantic_memories)
        
        # Step 7: Make predictions
        predictions = self._generate_predictions(reasoning_chain, temporal_patterns, emotional_context)
        
        # Step 8: Meta-cognitive analysis
        meta_notes = self._analyze_meta_cognitive_patterns(reasoning_chain, query)
        
        # Step 9: Calculate confidence
        confidence = self._calculate_reasoning_confidence(
            reasoning_chain, semantic_memories, temporal_patterns
        )
        
        # Create reasoning result
        result = ReasoningResult(
            query=query,
            reasoning_chain=reasoning_chain,
            insights=insights,
            confidence=confidence,
            temporal_patterns=temporal_patterns,
            emotional_context=emotional_context,
            cross_memory_connections=cross_connections,
            predictions=predictions,
            meta_cognitive_notes=meta_notes
        )
        
        # Cache the result
        self._cache_reasoning_result(query_hash, result, query_embedding)
        
        return result
    
    def _retrieve_semantic_memories(self, query: str, username: str, dna_memory_system,
                                   usernames: List[str] = None) -> List[Dict]:
        """Retrieve semantically relevant memories. Merges across usernames (aliases) if provided."""
        if not dna_memory_system:
            return []
        
        try:
            names = list(dict.fromkeys(usernames or [username]))
            seen = set()
            memories = []
            for name in names:
                for mem in dna_memory_system.express_genes(name, query, limit=10):
                    key = (mem.get('user_message', '')[:50], mem.get('luna_response', '')[:50])
                    if key not in seen:
                        seen.add(key)
                        memories.append(mem)
            
            # Enhance with vector similarity if embeddings available
            if self.embeddings_enabled and memories:
                query_embedding = self._generate_embedding(query)
                enhanced_memories = []
                
                for memory in memories:
                    # Generate embedding for memory content
                    memory_text = f"{memory['user_message']} {memory['luna_response']}"
                    memory_embedding = self._generate_embedding(memory_text)
                    
                    if memory_embedding:
                        similarity = self._calculate_similarity(query_embedding, memory_embedding)
                        memory['vector_similarity'] = similarity
                        enhanced_memories.append(memory)
                
                # Sort by vector similarity
                enhanced_memories.sort(key=lambda x: x.get('vector_similarity', 0), reverse=True)
                return enhanced_memories[:8]  # Top 8 most similar
            
            return memories[:10]  # Cap when no embeddings
            
        except Exception as e:
            print(f"ERROR: Failed to retrieve semantic memories: {e}")
            return []
    
    def _analyze_temporal_patterns(self, memories: List[Dict], username: str) -> Dict:
        """Analyze temporal patterns in memories"""
        if not memories:
            return {}
        
        try:
            # Extract timestamps and analyze patterns
            timestamps = [memory.get('timestamp', 0) for memory in memories]
            timestamps.sort()
            
            # Calculate time intervals
            intervals = []
            for i in range(1, len(timestamps)):
                intervals.append(timestamps[i] - timestamps[i-1])
            
            # Analyze frequency patterns
            avg_interval = float(np.mean(intervals)) if intervals else 0.0
            frequency_pattern = "regular" if float(np.std(intervals)) < avg_interval * 0.5 else "irregular"
            
            # Analyze time-of-day patterns (if timestamps are available)
            time_patterns = {}
            for memory in memories:
                if 'timestamp' in memory:
                    dt = datetime.fromtimestamp(memory['timestamp'])
                    hour = dt.hour
                    time_patterns[hour] = time_patterns.get(hour, 0) + 1
            
            most_active_hour = max(time_patterns.items(), key=lambda x: x[1])[0] if time_patterns else None
            
            return {
                "total_memories": len(memories),
                "time_span": timestamps[-1] - timestamps[0] if len(timestamps) > 1 else 0,
                "frequency_pattern": frequency_pattern,
                "avg_interval": avg_interval,
                "most_active_hour": most_active_hour,
                "time_distribution": time_patterns
            }
            
        except Exception as e:
            print(f"ERROR: Failed to analyze temporal patterns: {e}")
            return {}
    
    def _analyze_emotional_patterns(self, memories: List[Dict], query: str) -> Dict:
        """Analyze emotional patterns in memories"""
        if not memories:
            return {}
        
        try:
            # Extract emotional indicators from memories
            emotional_indicators = {
                'positive': 0,
                'negative': 0,
                'neutral': 0,
                'curious': 0,
                'excited': 0,
                'concerned': 0
            }
            
            for memory in memories:
                user_msg = memory.get('user_message', '').lower()
                luna_resp = memory.get('luna_response', '').lower()
                
                # Simple emotional analysis
                if any(word in user_msg for word in ['happy', 'great', 'awesome', 'love', 'amazing']):
                    emotional_indicators['positive'] += 1
                if any(word in user_msg for word in ['sad', 'bad', 'hate', 'angry', 'frustrated']):
                    emotional_indicators['negative'] += 1
                if any(word in user_msg for word in ['?', 'wonder', 'curious', 'how', 'what', 'why']):
                    emotional_indicators['curious'] += 1
                if any(word in user_msg for word in ['!', 'wow', 'amazing', 'incredible']):
                    emotional_indicators['excited'] += 1
                if any(word in user_msg for word in ['worried', 'concerned', 'anxious', 'stress']):
                    emotional_indicators['concerned'] += 1
            
            # Determine dominant emotional pattern
            dominant_emotion = max(emotional_indicators.items(), key=lambda x: x[1])[0]
            
            # Analyze emotional trajectory
            emotional_trajectory = "stable"
            if emotional_indicators['positive'] > emotional_indicators['negative']:
                emotional_trajectory = "positive"
            elif emotional_indicators['negative'] > emotional_indicators['positive']:
                emotional_trajectory = "negative"
            
            return {
                "emotional_indicators": emotional_indicators,
                "dominant_emotion": dominant_emotion,
                "emotional_trajectory": emotional_trajectory,
                "total_emotional_content": sum(emotional_indicators.values())
            }
            
        except Exception as e:
            print(f"ERROR: Failed to analyze emotional patterns: {e}")
            return {}
    
    def _find_cross_memory_connections(self, memories: List[Dict], query: str) -> List[Dict]:
        """Find connections between different memories"""
        connections = []
        
        try:
            # Find semantic connections between memories
            for i, memory1 in enumerate(memories):
                for j, memory2 in enumerate(memories[i+1:], i+1):
                    # Calculate connection strength
                    connection_strength = self._calculate_memory_connection_strength(memory1, memory2)
                    
                    if connection_strength > 0.3:  # Threshold for meaningful connection
                        connections.append({
                            "memory1": memory1.get('user_message', '')[:50],
                            "memory2": memory2.get('user_message', '')[:50],
                            "connection_strength": connection_strength,
                            "connection_type": self._classify_connection_type(memory1, memory2),
                            "insight": self._generate_connection_insight(memory1, memory2)
                        })
            
            return connections[:5]  # Limit to top 5 connections
            
        except Exception as e:
            print(f"ERROR: Failed to find cross-memory connections: {e}")
            return []
    
    def _calculate_memory_connection_strength(self, memory1: Dict, memory2: Dict) -> float:
        """Calculate connection strength between two memories"""
        try:
            # Simple text similarity for now
            text1 = f"{memory1.get('user_message', '')} {memory1.get('luna_response', '')}"
            text2 = f"{memory2.get('user_message', '')} {memory2.get('luna_response', '')}"
            
            if self.embeddings_enabled:
                emb1 = self._generate_embedding(text1)
                emb2 = self._generate_embedding(text2)
                if emb1 and emb2:
                    return self._calculate_similarity(emb1, emb2)
            
            # Fallback to simple word overlap
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            
            return len(intersection) / len(union) if union else 0.0
            
        except Exception as e:
            print(f"ERROR: Failed to calculate connection strength: {e}")
            return 0.0
    
    def _classify_connection_type(self, memory1: Dict, memory2: Dict) -> str:
        """Classify the type of connection between memories"""
        # Simple classification based on content analysis
        text1 = memory1.get('user_message', '').lower()
        text2 = memory2.get('user_message', '').lower()
        
        # Check for semantic similarity
        if any(word in text2 for word in text1.split() if len(word) > 3):
            return "semantic"
        
        # Check for emotional similarity
        emotions1 = self._extract_emotions(text1)
        emotions2 = self._extract_emotions(text2)
        if emotions1 and emotions2 and any(e in emotions2 for e in emotions1):
            return "emotional"
        
        # Check for topic similarity
        topics1 = self._extract_topics(text1)
        topics2 = self._extract_topics(text2)
        if topics1 and topics2 and any(t in topics2 for t in topics1):
            return "topical"
        
        return "general"
    
    def _extract_emotions(self, text: str) -> List[str]:
        """Extract emotions from text"""
        emotions = []
        emotion_words = {
            'happy': ['happy', 'joy', 'excited', 'great', 'awesome'],
            'sad': ['sad', 'depressed', 'down', 'blue'],
            'angry': ['angry', 'mad', 'furious', 'irritated'],
            'curious': ['curious', 'wonder', 'interested', 'intrigued']
        }
        
        for emotion, words in emotion_words.items():
            if any(word in text for word in words):
                emotions.append(emotion)
        
        return emotions
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from text"""
        # Simple topic extraction
        words = text.split()
        topics = [word for word in words if len(word) > 4 and word.isalpha()]
        return topics[:5]  # Top 5 topics
    
    def _generate_connection_insight(self, memory1: Dict, memory2: Dict) -> str:
        """Generate insight from memory connection"""
        try:
            # Simple insight generation
            topic1 = memory1.get('user_message', '')[:30]
            topic2 = memory2.get('user_message', '')[:30]
            
            return f"Connection between '{topic1}...' and '{topic2}...' suggests related interests or patterns"
            
        except Exception as e:
            return "Interesting connection between memories"
    
    def _build_reasoning_chain(self, query: str, memories: List[Dict], 
                              temporal_patterns: Dict, emotional_context: Dict, 
                              cross_connections: List[Dict]) -> List[Dict]:
        """Build step-by-step reasoning chain"""
        reasoning_steps = []
        
        try:
            # Step 1: Query analysis
            reasoning_steps.append({
                "step": 1,
                "type": "query_analysis",
                "content": f"Analyzing query: '{query}'",
                "details": f"Query appears to be asking about: {self._classify_query_intent(query)}"
            })
            
            # Step 2: Memory retrieval
            reasoning_steps.append({
                "step": 2,
                "type": "memory_retrieval",
                "content": f"Retrieved {len(memories)} relevant memories",
                "details": f"Memories span {temporal_patterns.get('time_span', 0)} seconds with {temporal_patterns.get('frequency_pattern', 'unknown')} frequency"
            })
            
            # Step 3: Pattern analysis
            if temporal_patterns:
                reasoning_steps.append({
                    "step": 3,
                    "type": "temporal_analysis",
                    "content": f"Temporal pattern: {temporal_patterns.get('frequency_pattern', 'unknown')}",
                    "details": f"Most active during hour {temporal_patterns.get('most_active_hour', 'unknown')}"
                })
            
            # Step 4: Emotional analysis
            if emotional_context:
                reasoning_steps.append({
                    "step": 4,
                    "type": "emotional_analysis",
                    "content": f"Emotional context: {emotional_context.get('dominant_emotion', 'neutral')}",
                    "details": f"Emotional trajectory: {emotional_context.get('emotional_trajectory', 'stable')}"
                })
            
            # Step 5: Cross-connections
            if cross_connections:
                reasoning_steps.append({
                    "step": 5,
                    "type": "cross_connection_analysis",
                    "content": f"Found {len(cross_connections)} meaningful connections",
                    "details": f"Connection types: {[c.get('connection_type', 'unknown') for c in cross_connections[:3]]}"
                })
            
            # Step 6: Synthesis
            reasoning_steps.append({
                "step": 6,
                "type": "synthesis",
                "content": "Synthesizing insights from all analysis",
                "details": "Combining temporal, emotional, and semantic patterns to form coherent understanding"
            })
            
            return reasoning_steps
            
        except Exception as e:
            print(f"ERROR: Failed to build reasoning chain: {e}")
            return [{"step": 1, "type": "error", "content": f"Reasoning failed: {e}"}]
    
    def _classify_query_intent(self, query: str) -> str:
        """Classify the intent of the query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['what', 'how', 'why', 'when', 'where']):
            return "information_seeking"
        elif any(word in query_lower for word in ['help', 'assist', 'support']):
            return "assistance_request"
        elif any(word in query_lower for word in ['feel', 'emotion', 'mood']):
            return "emotional_support"
        elif any(word in query_lower for word in ['remember', 'recall', 'past']):
            return "memory_request"
        else:
            return "general_conversation"
    
    def _generate_insights(self, reasoning_chain: List[Dict], memories: List[Dict]) -> List[str]:
        """Generate insights from reasoning chain"""
        insights = []
        
        try:
            # Insight 1: Memory patterns
            if len(memories) > 3:
                insights.append(f"User has discussed this topic {len(memories)} times, indicating strong interest or recurring need")
            
            # Insight 2: Temporal patterns
            if reasoning_chain:
                temporal_step = next((step for step in reasoning_chain if step['type'] == 'temporal_analysis'), None)
                if temporal_step:
                    insights.append(f"Temporal pattern suggests: {temporal_step['details']}")
            
            # Insight 3: Emotional patterns
            emotional_step = next((step for step in reasoning_chain if step['type'] == 'emotional_analysis'), None)
            if emotional_step:
                insights.append(f"Emotional context indicates: {emotional_step['details']}")
            
            # Insight 4: Cross-connections
            connection_step = next((step for step in reasoning_chain if step['type'] == 'cross_connection_analysis'), None)
            if connection_step:
                insights.append(f"Cross-memory analysis reveals: {connection_step['details']}")
            
            # Insight 5: Predictive insight
            if len(memories) > 1:
                insights.append("Based on historical patterns, user may benefit from proactive support on this topic")
            
            return insights
            
        except Exception as e:
            print(f"ERROR: Failed to generate insights: {e}")
            return ["Analysis completed with some limitations"]
    
    def _generate_predictions(self, reasoning_chain: List[Dict], temporal_patterns: Dict, 
                            emotional_context: Dict) -> List[str]:
        """Generate predictions based on reasoning"""
        predictions = []
        
        try:
            # Prediction 1: Based on temporal patterns
            if temporal_patterns.get('frequency_pattern') == 'regular':
                predictions.append("User likely to continue this conversation pattern based on regular frequency")
            
            # Prediction 2: Based on emotional context
            if emotional_context.get('emotional_trajectory') == 'positive':
                predictions.append("User appears to be in positive emotional state, likely to respond well to encouragement")
            elif emotional_context.get('emotional_trajectory') == 'negative':
                predictions.append("User may need emotional support or gentle approach")
            
            # Prediction 3: Based on memory patterns
            if len(reasoning_chain) > 3:
                predictions.append("Complex reasoning suggests user may have nuanced needs requiring careful response")
            
            # Prediction 4: Meta-cognitive prediction
            predictions.append("Luna should adapt response style based on detected patterns and emotional context")
            
            return predictions
            
        except Exception as e:
            print(f"ERROR: Failed to generate predictions: {e}")
            return ["Predictive analysis completed with limitations"]
    
    def _analyze_meta_cognitive_patterns(self, reasoning_chain: List[Dict], query: str) -> List[str]:
        """Analyze meta-cognitive patterns in reasoning"""
        meta_notes = []
        
        try:
            # Note 1: Reasoning complexity
            complexity = len(reasoning_chain)
            meta_notes.append(f"Reasoning complexity: {complexity} steps, indicating {'high' if complexity > 4 else 'moderate'} cognitive load")
            
            # Note 2: Query type analysis
            query_intent = self._classify_query_intent(query)
            meta_notes.append(f"Query intent: {query_intent}, requiring {'analytical' if 'information' in query_intent else 'empathetic'} response approach")
            
            # Note 3: Reasoning pattern recognition
            step_types = [step['type'] for step in reasoning_chain]
            unique_patterns = len(set(step_types))
            meta_notes.append(f"Reasoning pattern diversity: {unique_patterns} different analysis types used")
            
            # Note 4: Self-awareness note
            meta_notes.append("Luna's reasoning demonstrates multi-dimensional analysis capability")
            
            return meta_notes
            
        except Exception as e:
            print(f"ERROR: Failed to analyze meta-cognitive patterns: {e}")
            return ["Meta-cognitive analysis completed with limitations"]
    
    def _calculate_reasoning_confidence(self, reasoning_chain: List[Dict], memories: List[Dict], 
                                       temporal_patterns: Dict) -> float:
        """Calculate confidence in reasoning result"""
        try:
            confidence = 0.5  # Base confidence
            
            # Factor 1: Number of memories
            memory_factor = min(len(memories) / 10.0, 1.0)  # More memories = higher confidence
            confidence += memory_factor * 0.2
            
            # Factor 2: Reasoning chain completeness
            chain_factor = min(len(reasoning_chain) / 6.0, 1.0)  # More steps = higher confidence
            confidence += chain_factor * 0.2
            
            # Factor 3: Temporal pattern clarity
            if temporal_patterns.get('frequency_pattern') != 'unknown':
                confidence += 0.1
            
            # Factor 4: Memory quality (if we have vector similarities)
            if memories and any('vector_similarity' in mem for mem in memories):
                avg_similarity = float(np.mean([mem.get('vector_similarity', 0.5) for mem in memories if 'vector_similarity' in mem]))
                confidence += avg_similarity * 0.1
            
            return float(min(confidence, 1.0))  # Cap at 1.0 and ensure Python float
            
        except Exception as e:
            print(f"ERROR: Failed to calculate confidence: {e}")
            return 0.5
    
    def _get_cached_reasoning(self, query_hash: str) -> Optional[ReasoningResult]:
        """Get cached reasoning result"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT reasoning_steps, insights, confidence, temporal_patterns, 
                       emotional_context, cross_connections, predictions, meta_notes
                FROM reasoning_chains 
                WHERE query_hash = ? 
                ORDER BY created_at DESC LIMIT 1
            ''', (query_hash,))
            
            result = cursor.fetchone()
            if result:
                # Reconstruct ReasoningResult from cached data
                return ReasoningResult(
                    query="",  # Will be filled by caller
                    reasoning_chain=json.loads(result[0]) if result[0] else [],
                    insights=json.loads(result[1]) if result[1] else [],
                    confidence=result[2] or 0.5,
                    temporal_patterns=json.loads(result[3]) if result[3] else {},
                    emotional_context=json.loads(result[4]) if result[4] else {},
                    cross_memory_connections=json.loads(result[5]) if result[5] else [],
                    predictions=json.loads(result[6]) if result[6] else [],
                    meta_cognitive_notes=json.loads(result[7]) if result[7] else []
                )
            
            return None
            
        except Exception as e:
            print(f"ERROR: Failed to get cached reasoning: {e}")
            return None
    
    def _cache_reasoning_result(self, query_hash: str, result: ReasoningResult, query_embedding: bytes):
        """Cache reasoning result"""
        try:
            # Convert all numpy types to Python types for JSON serialization
            
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO reasoning_chains 
                (query_hash, query_text, reasoning_steps, insights, confidence, 
                 temporal_patterns, emotional_context, cross_connections, 
                 predictions, meta_notes, reasoning_vector)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                query_hash,
                result.query,
                json.dumps(self._convert_numpy_types(result.reasoning_chain)),
                json.dumps(self._convert_numpy_types(result.insights)),
                float(result.confidence),
                json.dumps(self._convert_numpy_types(result.temporal_patterns)),
                json.dumps(self._convert_numpy_types(result.emotional_context)),
                json.dumps(self._convert_numpy_types(result.cross_memory_connections)),
                json.dumps(self._convert_numpy_types(result.predictions)),
                json.dumps(self._convert_numpy_types(result.meta_cognitive_notes)),
                query_embedding
            ))
            
            self.conn.commit()
            
        except Exception as e:
            print(f"ERROR: Failed to cache reasoning result: {e}")
    
    def get_reasoning_stats(self) -> Dict:
        """Get statistics about reasoning system"""
        try:
            cursor = self.conn.cursor()
            
            # Count reasoning chains
            cursor.execute('SELECT COUNT(*) FROM reasoning_chains')
            total_chains = cursor.fetchone()[0]
            
            # Count patterns
            cursor.execute('SELECT COUNT(*) FROM reasoning_patterns')
            total_patterns = cursor.fetchone()[0]
            
            # Count meta-cognitive insights
            cursor.execute('SELECT COUNT(*) FROM meta_cognitive_insights')
            total_insights = cursor.fetchone()[0]
            
            # Average confidence
            cursor.execute('SELECT AVG(confidence) FROM reasoning_chains')
            avg_confidence = cursor.fetchone()[0] or 0.0
            
            return {
                "total_reasoning_chains": total_chains,
                "total_patterns": total_patterns,
                "total_meta_insights": total_insights,
                "average_confidence": round(avg_confidence, 3),
                "embeddings_enabled": self.embeddings_enabled
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def close(self):
        """Close the reasoning database"""
        self.conn.close()


# Global instance
_vector_reasoning_engine = None

def initialize_vector_reasoning():
    """Initialize the vector reasoning system"""
    global _vector_reasoning_engine
    _vector_reasoning_engine = VectorReasoningEngine()
    return _vector_reasoning_engine

def get_vector_reasoning():
    """Get the vector reasoning engine instance"""
    return _vector_reasoning_engine

def reason_with_vectors(query: str, username: str, dna_memory_system=None, understanding_engine=None,
                       usernames: List[str] = None) -> ReasoningResult:
    """Main function for vector reasoning. usernames: aliases to merge (e.g. Chris, Solonaras)."""
    if _vector_reasoning_engine:
        return _vector_reasoning_engine.reason_across_memories(
            query, username, dna_memory_system, understanding_engine, usernames=usernames
        )
    return None


if __name__ == "__main__":
    # Test the vector reasoning system
    engine = initialize_vector_reasoning()
    
    # Test reasoning
    result = engine.reason_across_memories("What is love?", "test_user")
    print(f"Reasoning result: {result}")
    print(f"Stats: {engine.get_reasoning_stats()}")
