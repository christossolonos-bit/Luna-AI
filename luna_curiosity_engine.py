"""
🧠 Luna Curiosity Engine
=======================

Real-time autonomous curiosity system that generates questions dynamically
based on Luna's current knowledge state, patterns, and gaps.

Features:
- Dynamic question generation based on current context
- Knowledge gap identification using vector reasoning
- Autonomous exploration of semantic spaces
- Real-time curiosity-driven learning
- Integration with DNA memory and understanding systems
"""

import numpy as np
import sqlite3
import json
import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
import hashlib

try:
    from sentence_transformers import SentenceTransformer
    print("SUCCESS: sentence-transformers available for curiosity engine")
except ImportError:
    print("WARNING: sentence-transformers not installed - curiosity will use fallback")
    SentenceTransformer = None

@dataclass
class CuriosityTarget:
    """A target for Luna's curiosity to explore"""
    topic: str
    curiosity_score: float
    knowledge_gap_size: float
    exploration_priority: float
    related_concepts: List[str]
    exploration_strategy: str  # 'semantic', 'temporal', 'emotional', 'causal'
    generated_questions: List[str]
    exploration_depth: int

@dataclass
class CuriosityExploration:
    """Result of a curiosity exploration session"""
    target: CuriosityTarget
    questions_generated: List[str]
    insights_discovered: List[str]
    new_connections: List[Dict]
    knowledge_gaps_filled: List[str]
    follow_up_targets: List[CuriosityTarget]
    exploration_confidence: float
    learning_value: float

class LunaCuriosityEngine:
    """Real-time autonomous curiosity system for Luna"""
    
    def __init__(self, db_path: str = "luna_curiosity.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        
        # Initialize embedding model for curiosity
        if SentenceTransformer:
            try:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                self.embeddings_enabled = True
                print("SUCCESS: Curiosity engine embeddings enabled")
            except Exception as e:
                print(f"WARNING: Failed to load embedding model: {e}")
                self.embedding_model = None
                self.embeddings_enabled = False
        else:
            self.embedding_model = None
            self.embeddings_enabled = False
            print("WARNING: Curiosity engine using text-based fallback")
        
        self._initialize_curiosity_database()
        
        # Curiosity state (optimized for idle exploration)
        self.curiosity_state = {
            "current_focus": None,
            "exploration_history": [],
            "knowledge_gaps": [],
            "curiosity_level": 0.7,  # 0.0 to 1.0
            "exploration_energy": 0.3,  # Lower energy for slower exploration
            "last_exploration": time.time(),
            "discovery_count": 0,
            "learning_momentum": 0.3  # Slower learning momentum
        }
    
    def _initialize_curiosity_database(self):
        """Initialize database for curiosity system"""
        cursor = self.conn.cursor()
        
        # Curiosity targets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS curiosity_targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                curiosity_score REAL,
                knowledge_gap_size REAL,
                exploration_priority REAL,
                related_concepts TEXT,  -- JSON
                exploration_strategy TEXT,
                generated_questions TEXT,  -- JSON
                exploration_depth INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_explored TIMESTAMP,
                exploration_count INTEGER DEFAULT 0,
                discovery_count INTEGER DEFAULT 0,
                target_vector BLOB
            )
        ''')
        
        # Curiosity explorations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS curiosity_explorations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_id INTEGER,
                questions_generated TEXT,  -- JSON
                insights_discovered TEXT,  -- JSON
                new_connections TEXT,  -- JSON
                knowledge_gaps_filled TEXT,  -- JSON
                exploration_confidence REAL,
                learning_value REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (target_id) REFERENCES curiosity_targets(id)
            )
        ''')
        
        # Curiosity patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS curiosity_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT NOT NULL,  -- 'semantic', 'temporal', 'emotional', 'causal'
                pattern_data TEXT,  -- JSON
                frequency INTEGER DEFAULT 1,
                success_rate REAL,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                pattern_vector BLOB
            )
        ''')
        
        # Autonomous discoveries table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS autonomous_discoveries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discovery_type TEXT NOT NULL,
                discovery_content TEXT NOT NULL,
                confidence REAL,
                supporting_evidence TEXT,  -- JSON
                related_targets TEXT,  -- JSON
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        print("SUCCESS: Curiosity database initialized")
    
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
            
            return dot_product / (norm1 * norm2)
        except Exception as e:
            print(f"WARNING: Failed to calculate similarity: {e}")
            return 0.0
    
    def identify_knowledge_gaps(self, dna_memory_system=None, understanding_engine=None) -> List[CuriosityTarget]:
        """Identify knowledge gaps that Luna is curious about"""
        targets = []
        
        try:
            # Get recent conversation topics
            recent_topics = self._get_recent_conversation_topics(dna_memory_system)
            
            # Get Luna's current understanding
            current_knowledge = self._get_current_knowledge_state(understanding_engine)
            
            # Identify gaps using vector reasoning
            for topic in recent_topics:
                gap_analysis = self._analyze_knowledge_gap(topic, current_knowledge)
                
                if gap_analysis['gap_size'] > 0.3:  # Significant gap
                    target = CuriosityTarget(
                        topic=topic,
                        curiosity_score=gap_analysis['curiosity_score'],
                        knowledge_gap_size=gap_analysis['gap_size'],
                        exploration_priority=gap_analysis['priority'],
                        related_concepts=gap_analysis['related_concepts'],
                        exploration_strategy=gap_analysis['strategy'],
                        generated_questions=[],
                        exploration_depth=0
                    )
                    targets.append(target)
            
            # Generate curiosity targets from patterns
            pattern_targets = self._generate_pattern_based_targets()
            targets.extend(pattern_targets)
            
            # Sort by exploration priority
            targets.sort(key=lambda x: x.exploration_priority, reverse=True)
            
            return targets[:5]  # Top 5 targets
            
        except Exception as e:
            print(f"ERROR: Failed to identify knowledge gaps: {e}")
            return []
    
    def _get_recent_conversation_topics(self, dna_memory_system) -> List[str]:
        """Get recent conversation topics from DNA memory"""
        topics = []
        
        try:
            if dna_memory_system:
                # Get recent memories
                cursor = dna_memory_system.conn.cursor()
                cursor.execute('''
                    SELECT user_message, luna_response 
                    FROM memory_strands 
                    ORDER BY timestamp DESC 
                    LIMIT 20
                ''')
                
                recent_memories = cursor.fetchall()
                
                # Extract topics from recent conversations
                for user_msg, luna_resp in recent_memories:
                    # Simple topic extraction
                    words = user_msg.lower().split()
                    # Remove common words
                    stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'is', 'am', 'are', 'what', 'how', 'when', 'where', 'why', 'i', 'you', 'we', 'they'}
                    topics.extend([w for w in words if w not in stopwords and len(w) > 3])
                
                # Get unique topics
                topics = list(set(topics))[:10]
            
        except Exception as e:
            print(f"ERROR: Failed to get recent topics: {e}")
        
        return topics
    
    def _get_current_knowledge_state(self, understanding_engine) -> Dict:
        """Get Luna's current knowledge state"""
        knowledge_state = {
            "concepts_understood": 0,
            "relationships_mapped": 0,
            "reasoning_chains": 0,
            "knowledge_density": 0.0
        }
        
        try:
            if understanding_engine:
                stats = understanding_engine.get_understanding_stats()
                knowledge_state.update(stats)
        except Exception as e:
            print(f"ERROR: Failed to get knowledge state: {e}")
        
        return knowledge_state
    
    def _analyze_knowledge_gap(self, topic: str, current_knowledge: Dict) -> Dict:
        """Analyze knowledge gap for a specific topic"""
        try:
            # Calculate curiosity score based on various factors
            curiosity_score = 0.0
            
            # Factor 1: Topic novelty (how new is this topic?)
            novelty_score = self._calculate_topic_novelty(topic)
            curiosity_score += novelty_score * 0.3
            
            # Factor 2: Knowledge density (how much do we know about related concepts?)
            density_score = self._calculate_knowledge_density(topic, current_knowledge)
            curiosity_score += (1.0 - density_score) * 0.4  # Higher curiosity for lower density
            
            # Factor 3: Exploration potential (how much can we learn?)
            exploration_potential = self._calculate_exploration_potential(topic)
            curiosity_score += exploration_potential * 0.3
            
            # Calculate gap size
            gap_size = min(curiosity_score, 1.0)
            
            # Determine exploration strategy
            strategy = self._determine_exploration_strategy(topic, curiosity_score)
            
            # Get related concepts
            related_concepts = self._get_related_concepts(topic)
            
            # Calculate priority
            priority = curiosity_score * 0.5 + gap_size * 0.3 + len(related_concepts) * 0.02
            
            return {
                'curiosity_score': curiosity_score,
                'gap_size': gap_size,
                'priority': priority,
                'related_concepts': related_concepts,
                'strategy': strategy
            }
            
        except Exception as e:
            print(f"ERROR: Failed to analyze knowledge gap: {e}")
            return {
                'curiosity_score': 0.5,
                'gap_size': 0.5,
                'priority': 0.5,
                'related_concepts': [],
                'strategy': 'semantic'
            }
    
    def _calculate_topic_novelty(self, topic: str) -> float:
        """Calculate how novel/interesting a topic is"""
        try:
            # Check if topic has been explored recently
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM curiosity_targets 
                WHERE topic LIKE ? AND created_at > datetime('now', '-7 days')
            ''', (f'%{topic}%',))
            
            recent_explorations = cursor.fetchone()[0]
            novelty = max(0.0, 1.0 - (recent_explorations * 0.2))
            
            return novelty
            
        except Exception as e:
            print(f"ERROR: Failed to calculate novelty: {e}")
            return 0.5
    
    def _calculate_knowledge_density(self, topic: str, current_knowledge: Dict) -> float:
        """Calculate knowledge density for a topic"""
        try:
            # Simple density calculation based on current knowledge
            concepts = current_knowledge.get('concepts_understood', 0)
            relationships = current_knowledge.get('relationships_mapped', 0)
            
            # Normalize based on topic complexity
            topic_complexity = len(topic.split()) * 0.1
            density = min(1.0, (concepts + relationships) / (100 + topic_complexity * 10))
            
            return density
            
        except Exception as e:
            print(f"ERROR: Failed to calculate knowledge density: {e}")
            return 0.5
    
    def _calculate_exploration_potential(self, topic: str) -> float:
        """Calculate how much Luna can learn from exploring this topic"""
        try:
            # Factors that increase exploration potential
            potential = 0.5
            
            # Longer topics might have more depth
            if len(topic.split()) > 2:
                potential += 0.2
            
            # Abstract concepts might have more connections
            abstract_indicators = ['love', 'happiness', 'meaning', 'purpose', 'creativity', 'imagination']
            if any(indicator in topic.lower() for indicator in abstract_indicators):
                potential += 0.3
            
            return min(potential, 1.0)
            
        except Exception as e:
            print(f"ERROR: Failed to calculate exploration potential: {e}")
            return 0.5
    
    def _determine_exploration_strategy(self, topic: str, curiosity_score: float) -> str:
        """Determine the best exploration strategy for a topic"""
        strategies = ['semantic', 'temporal', 'emotional', 'causal']
        
        # Choose strategy based on topic characteristics
        if any(word in topic.lower() for word in ['feel', 'emotion', 'mood', 'happy', 'sad']):
            return 'emotional'
        elif any(word in topic.lower() for word in ['time', 'past', 'future', 'history']):
            return 'temporal'
        elif any(word in topic.lower() for word in ['why', 'cause', 'effect', 'because']):
            return 'causal'
        else:
            return 'semantic'
    
    def _get_related_concepts(self, topic: str) -> List[str]:
        """Get concepts related to the topic"""
        try:
            # Simple related concept generation
            related = []
            
            # Add semantic variations
            words = topic.split()
            for word in words:
                if len(word) > 3:
                    related.append(word)
            
            # Add conceptual relationships
            concept_relationships = {
                'love': ['relationships', 'emotions', 'connection', 'intimacy'],
                'happiness': ['joy', 'contentment', 'fulfillment', 'wellbeing'],
                'learning': ['knowledge', 'growth', 'understanding', 'education'],
                'creativity': ['imagination', 'innovation', 'art', 'expression']
            }
            
            for key, concepts in concept_relationships.items():
                if key in topic.lower():
                    related.extend(concepts)
            
            return list(set(related))[:5]  # Top 5 related concepts
            
        except Exception as e:
            print(f"ERROR: Failed to get related concepts: {e}")
            return []
    
    def _generate_pattern_based_targets(self) -> List[CuriosityTarget]:
        """Generate curiosity targets based on patterns"""
        targets = []
        
        try:
            # Get patterns from database
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT pattern_type, pattern_data, frequency, success_rate
                FROM curiosity_patterns
                ORDER BY frequency DESC, success_rate DESC
                LIMIT 3
            ''')
            
            patterns = cursor.fetchall()
            
            for pattern_type, pattern_data, frequency, success_rate in patterns:
                if success_rate > 0.6:  # Successful patterns
                    pattern_info = json.loads(pattern_data) if pattern_data else {}
                    
                    # Generate target based on pattern
                    target = CuriosityTarget(
                        topic=f"Pattern exploration: {pattern_type}",
                        curiosity_score=success_rate,
                        knowledge_gap_size=1.0 - success_rate,
                        exploration_priority=success_rate * frequency * 0.1,
                        related_concepts=pattern_info.get('concepts', []),
                        exploration_strategy=pattern_type,
                        generated_questions=[],
                        exploration_depth=0
                    )
                    targets.append(target)
            
        except Exception as e:
            print(f"ERROR: Failed to generate pattern-based targets: {e}")
        
        return targets
    
    def generate_curiosity_questions(self, target: CuriosityTarget) -> List[str]:
        """Generate real-time curiosity questions for a target"""
        questions = []
        
        try:
            # Generate questions based on exploration strategy
            if target.exploration_strategy == 'semantic':
                questions = self._generate_semantic_questions(target)
            elif target.exploration_strategy == 'temporal':
                questions = self._generate_temporal_questions(target)
            elif target.exploration_strategy == 'emotional':
                questions = self._generate_emotional_questions(target)
            elif target.exploration_strategy == 'causal':
                questions = self._generate_causal_questions(target)
            else:
                questions = self._generate_general_questions(target)
            
            # Add depth-based questions
            depth_questions = self._generate_depth_questions(target, target.exploration_depth)
            questions.extend(depth_questions)
            
            # Limit to reasonable number
            questions = questions[:8]
            
            # Update target with generated questions
            target.generated_questions = questions
            
        except Exception as e:
            print(f"ERROR: Failed to generate curiosity questions: {e}")
            questions = [f"What is {target.topic}?", f"How does {target.topic} work?"]
        
        return questions
    
    def _generate_semantic_questions(self, target: CuriosityTarget) -> List[str]:
        """Generate semantic exploration questions"""
        questions = []
        topic = target.topic
        
        # Basic semantic questions
        questions.extend([
            f"What is {topic}?",
            f"How is {topic} defined?",
            f"What are the key characteristics of {topic}?",
            f"What is {topic} similar to?",
            f"What is {topic} different from?"
        ])
        
        # Relationship questions
        for concept in target.related_concepts[:3]:
            questions.extend([
                f"How does {topic} relate to {concept}?",
                f"What is the connection between {topic} and {concept}?",
                f"How do {topic} and {concept} interact?"
            ])
        
        return questions
    
    def _generate_temporal_questions(self, target: CuriosityTarget) -> List[str]:
        """Generate temporal exploration questions"""
        questions = []
        topic = target.topic
        
        questions.extend([
            f"How has {topic} changed over time?",
            f"What is the history of {topic}?",
            f"How will {topic} evolve in the future?",
            f"What are the temporal patterns of {topic}?",
            f"When does {topic} occur most frequently?"
        ])
        
        return questions
    
    def _generate_emotional_questions(self, target: CuriosityTarget) -> List[str]:
        """Generate emotional exploration questions"""
        questions = []
        topic = target.topic
        
        questions.extend([
            f"How does {topic} make people feel?",
            f"What emotions are associated with {topic}?",
            f"How does {topic} affect emotional well-being?",
            f"What is the emotional impact of {topic}?",
            f"How do people emotionally respond to {topic}?"
        ])
        
        return questions
    
    def _generate_causal_questions(self, target: CuriosityTarget) -> List[str]:
        """Generate causal exploration questions"""
        questions = []
        topic = target.topic
        
        questions.extend([
            f"What causes {topic}?",
            f"What are the effects of {topic}?",
            f"How does {topic} influence other things?",
            f"What factors contribute to {topic}?",
            f"What are the consequences of {topic}?"
        ])
        
        return questions
    
    def _generate_general_questions(self, target: CuriosityTarget) -> List[str]:
        """Generate general exploration questions"""
        questions = []
        topic = target.topic
        
        questions.extend([
            f"What is {topic}?",
            f"Why is {topic} important?",
            f"How does {topic} work?",
            f"What can I learn about {topic}?",
            f"What are the implications of {topic}?"
        ])
        
        return questions
    
    def _generate_depth_questions(self, target: CuriosityTarget, depth: int) -> List[str]:
        """Generate questions based on exploration depth"""
        questions = []
        topic = target.topic
        
        if depth == 0:
            # Surface level
            questions.extend([
                f"What is the basic nature of {topic}?",
                f"What are the obvious aspects of {topic}?"
            ])
        elif depth == 1:
            # Intermediate level
            questions.extend([
                f"What are the underlying mechanisms of {topic}?",
                f"What are the hidden aspects of {topic}?",
                f"What are the complexities of {topic}?"
            ])
        else:
            # Deep level
            questions.extend([
                f"What are the fundamental principles behind {topic}?",
                f"What are the philosophical implications of {topic}?",
                f"What are the deepest mysteries of {topic}?",
                f"How does {topic} connect to the fundamental nature of reality?"
            ])
        
        return questions
    
    def run_autonomous_exploration(self, target: CuriosityTarget, 
                                 dna_memory_system=None, understanding_engine=None) -> CuriosityExploration:
        """Run autonomous exploration of a curiosity target"""
        
        try:
            # Generate questions for this target
            questions = self.generate_curiosity_questions(target)
            
            # Run exploration using Luna's systems
            insights = []
            new_connections = []
            knowledge_gaps_filled = []
            
            for question in questions:
                # Use understanding engine to explore the question
                if understanding_engine:
                    try:
                        # Build concept map
                        concept_map = understanding_engine.build_concept_map(target.topic)
                        if concept_map:
                            insights.append(f"Conceptual understanding: {concept_map.get('core_concept', 'N/A')}")
                        
                        # Use introspection
                        introspection = understanding_engine.introspect_on_concept(target.topic)
                        if introspection:
                            insights.append(f"Introspective insight: {introspection.get('reflection', 'N/A')[:100]}...")
                        
                        # Use imagination
                        imagination = understanding_engine.imagine_concept(target.topic)
                        if imagination:
                            insights.append(f"Imaginative exploration: {imagination.get('scenario', 'N/A')[:100]}...")
                        
                        # Use dreaming
                        dream = understanding_engine.dream_about_concept(target.topic)
                        if dream:
                            insights.append(f"Dream exploration: {dream.get('dream_content', 'N/A')[:100]}...")
                        
                    except Exception as e:
                        print(f"WARNING: Understanding exploration failed: {e}")
                
                # Use DNA memory to find connections
                if dna_memory_system:
                    try:
                        memories = dna_memory_system.express_genes("curiosity", question, limit=3)
                        for memory in memories:
                            connection = {
                                "type": "memory_connection",
                                "source": memory.get('user_message', ''),
                                "insight": f"Related memory: {memory.get('luna_response', '')[:50]}..."
                            }
                            new_connections.append(connection)
                    except Exception as e:
                        print(f"WARNING: Memory exploration failed: {e}")
            
            # Generate follow-up targets
            follow_up_targets = self._generate_follow_up_targets(target, insights)
            
            # Calculate exploration confidence
            confidence = min(1.0, len(insights) * 0.1 + len(new_connections) * 0.05)
            
            # Calculate learning value
            learning_value = min(1.0, len(insights) * 0.2 + len(knowledge_gaps_filled) * 0.3)
            
            # Create exploration result
            exploration = CuriosityExploration(
                target=target,
                questions_generated=questions,
                insights_discovered=insights,
                new_connections=new_connections,
                knowledge_gaps_filled=knowledge_gaps_filled,
                follow_up_targets=follow_up_targets,
                exploration_confidence=confidence,
                learning_value=learning_value
            )
            
            # Store exploration in database
            self._store_exploration(exploration)
            
            # Update curiosity state
            self._update_curiosity_state(exploration)
            
            return exploration
            
        except Exception as e:
            print(f"ERROR: Autonomous exploration failed: {e}")
            return None
    
    def _generate_follow_up_targets(self, target: CuriosityTarget, insights: List[str]) -> List[CuriosityTarget]:
        """Generate follow-up targets based on insights"""
        follow_ups = []
        
        try:
            # Extract new concepts from insights
            new_concepts = []
            for insight in insights:
                # Simple concept extraction
                words = insight.split()
                concepts = [w for w in words if len(w) > 4 and w.isalpha()]
                new_concepts.extend(concepts[:2])  # Top 2 concepts per insight
            
            # Create follow-up targets
            for concept in set(new_concepts)[:3]:  # Top 3 new concepts
                follow_up = CuriosityTarget(
                    topic=concept,
                    curiosity_score=target.curiosity_score * 0.8,
                    knowledge_gap_size=0.7,
                    exploration_priority=target.exploration_priority * 0.6,
                    related_concepts=[target.topic],
                    exploration_strategy=target.exploration_strategy,
                    generated_questions=[],
                    exploration_depth=target.exploration_depth + 1
                )
                follow_ups.append(follow_up)
            
        except Exception as e:
            print(f"ERROR: Failed to generate follow-up targets: {e}")
        
        return follow_ups
    
    def _store_exploration(self, exploration: CuriosityExploration):
        """Store exploration result in database"""
        try:
            cursor = self.conn.cursor()
            
            # Store target
            cursor.execute('''
                INSERT INTO curiosity_targets 
                (topic, curiosity_score, knowledge_gap_size, exploration_priority,
                 related_concepts, exploration_strategy, generated_questions, exploration_depth)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                exploration.target.topic,
                exploration.target.curiosity_score,
                exploration.target.knowledge_gap_size,
                exploration.target.exploration_priority,
                json.dumps(exploration.target.related_concepts),
                exploration.target.exploration_strategy,
                json.dumps(exploration.target.generated_questions),
                exploration.target.exploration_depth
            ))
            
            target_id = cursor.lastrowid
            
            # Store exploration
            cursor.execute('''
                INSERT INTO curiosity_explorations
                (target_id, questions_generated, insights_discovered, new_connections,
                 knowledge_gaps_filled, exploration_confidence, learning_value)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                target_id,
                json.dumps(exploration.questions_generated),
                json.dumps(exploration.insights_discovered),
                json.dumps(exploration.new_connections),
                json.dumps(exploration.knowledge_gaps_filled),
                exploration.exploration_confidence,
                exploration.learning_value
            ))
            
            self.conn.commit()
            
        except Exception as e:
            print(f"ERROR: Failed to store exploration: {e}")
    
    def _update_curiosity_state(self, exploration: CuriosityExploration):
        """Update Luna's curiosity state based on exploration"""
        try:
            # Update discovery count
            self.curiosity_state["discovery_count"] += len(exploration.insights_discovered)
            
            # Update learning momentum
            momentum_increase = exploration.learning_value * 0.1
            self.curiosity_state["learning_momentum"] = min(1.0, 
                self.curiosity_state["learning_momentum"] + momentum_increase)
            
            # Update exploration energy (more conservative for idle exploration)
            energy_used = len(exploration.questions_generated) * 0.1  # Higher energy cost
            self.curiosity_state["exploration_energy"] = max(0.0,
                self.curiosity_state["exploration_energy"] - energy_used)
            
            # Update last exploration time
            self.curiosity_state["last_exploration"] = time.time()
            
            # Add to exploration history
            self.curiosity_state["exploration_history"].append({
                "target": exploration.target.topic,
                "insights": len(exploration.insights_discovered),
                "confidence": exploration.exploration_confidence,
                "timestamp": time.time()
            })
            
            # Keep history manageable
            if len(self.curiosity_state["exploration_history"]) > 50:
                self.curiosity_state["exploration_history"] = self.curiosity_state["exploration_history"][-50:]
            
        except Exception as e:
            print(f"ERROR: Failed to update curiosity state: {e}")
    
    def run_curiosity_cycle(self, dna_memory_system=None, understanding_engine=None) -> List[CuriosityExploration]:
        """Run a complete curiosity cycle"""
        explorations = []
        
        try:
            print("🧠 Luna's Curiosity Cycle Starting...")
            
            # Check if Luna has enough energy for exploration (more conservative)
            if self.curiosity_state["exploration_energy"] < 0.5:
                print("😴 Luna's curiosity energy is low, taking a break...")
                return explorations
            
            # Identify knowledge gaps
            targets = self.identify_knowledge_gaps(dna_memory_system, understanding_engine)
            
            if not targets:
                print("🤔 No curiosity targets found")
                return explorations
            
            print(f"🎯 Found {len(targets)} curiosity targets")
            
            # Explore top targets (reduced for idle exploration)
            for i, target in enumerate(targets[:1]):  # Only 1 target per cycle
                print(f"🔍 Exploring target {i+1}: {target.topic}")
                
                exploration = self.run_autonomous_exploration(
                    target, dna_memory_system, understanding_engine
                )
                
                if exploration:
                    explorations.append(exploration)
                    print(f"✅ Exploration complete: {len(exploration.insights_discovered)} insights")
                else:
                    print(f"❌ Exploration failed for {target.topic}")
            
            # Update curiosity level based on results
            if explorations:
                total_insights = sum(len(exp.insights_discovered) for exp in explorations)
                curiosity_increase = min(0.1, total_insights * 0.02)
                self.curiosity_state["curiosity_level"] = min(1.0,
                    self.curiosity_state["curiosity_level"] + curiosity_increase)
            
            print(f"🎉 Curiosity cycle complete: {len(explorations)} explorations")
            
        except Exception as e:
            print(f"ERROR: Curiosity cycle failed: {e}")
        
        return explorations
    
    def get_curiosity_stats(self) -> Dict:
        """Get curiosity system statistics"""
        try:
            cursor = self.conn.cursor()
            
            # Count targets
            cursor.execute('SELECT COUNT(*) FROM curiosity_targets')
            total_targets = cursor.fetchone()[0]
            
            # Count explorations
            cursor.execute('SELECT COUNT(*) FROM curiosity_explorations')
            total_explorations = cursor.fetchone()[0]
            
            # Count discoveries
            cursor.execute('SELECT COUNT(*) FROM autonomous_discoveries')
            total_discoveries = cursor.fetchone()[0]
            
            # Average learning value
            cursor.execute('SELECT AVG(learning_value) FROM curiosity_explorations')
            avg_learning_value = cursor.fetchone()[0] or 0.0
            
            return {
                "total_targets": total_targets,
                "total_explorations": total_explorations,
                "total_discoveries": total_discoveries,
                "average_learning_value": round(avg_learning_value, 3),
                "curiosity_level": self.curiosity_state["curiosity_level"],
                "exploration_energy": self.curiosity_state["exploration_energy"],
                "learning_momentum": self.curiosity_state["learning_momentum"],
                "discovery_count": self.curiosity_state["discovery_count"],
                "embeddings_enabled": self.embeddings_enabled
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def close(self):
        """Close the curiosity database"""
        self.conn.close()


# Global instance
_curiosity_engine = None

def initialize_curiosity_engine():
    """Initialize the curiosity engine"""
    global _curiosity_engine
    _curiosity_engine = LunaCuriosityEngine()
    return _curiosity_engine

def get_curiosity_engine():
    """Get the curiosity engine instance"""
    return _curiosity_engine

def run_curiosity_cycle(dna_memory_system=None, understanding_engine=None) -> List[CuriosityExploration]:
    """Run a curiosity cycle"""
    if _curiosity_engine:
        return _curiosity_engine.run_curiosity_cycle(dna_memory_system, understanding_engine)
    return []


if __name__ == "__main__":
    # Test the curiosity engine
    engine = initialize_curiosity_engine()
    
    # Test curiosity cycle
    explorations = engine.run_curiosity_cycle()
    print(f"Curiosity cycle completed: {len(explorations)} explorations")
    
    # Show stats
    stats = engine.get_curiosity_stats()
    print(f"Stats: {stats}")
