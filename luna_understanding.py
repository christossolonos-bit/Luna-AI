"""
Luna's Deep Understanding System
Goes beyond pattern matching to build conceptual understanding
"""

import os
import json
import sqlite3
import numpy as np
from datetime import datetime

try:
    import ollama
except ImportError:
    print("WARNING: ollama not installed - understanding system will use requests")
    import requests
    ollama = None

try:
    from sentence_transformers import SentenceTransformer
    print("SUCCESS: sentence-transformers available for vector embeddings")
except ImportError:
    print("WARNING: sentence-transformers not installed - falling back to text search")
    SentenceTransformer = None

class UnderstandingEngine:
    """Builds genuine understanding through concept mapping and reasoning"""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.db_file = "luna_understanding.db"
        
        # Initialize embedding model
        if SentenceTransformer:
            try:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                self.embeddings_enabled = True
                print("SUCCESS: Vector embeddings enabled with all-MiniLM-L6-v2")
            except Exception as e:
                print(f"WARNING: Failed to load embedding model: {e}")
                self.embedding_model = None
                self.embeddings_enabled = False
        else:
            self.embedding_model = None
            self.embeddings_enabled = False
            print("WARNING: Vector embeddings disabled - using text search")
        
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for understanding system"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # Create concepts table with vector embeddings
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS concepts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT UNIQUE NOT NULL,
                    core_concept TEXT,
                    properties TEXT,  -- JSON string
                    relationships TEXT,  -- JSON string
                    implications TEXT,  -- JSON string
                    counterexamples TEXT,  -- JSON string
                    embedding BLOB,  -- Vector embedding as binary
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create reasoning_chains table with vector embeddings
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reasoning_chains (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    known_facts TEXT,  -- JSON string
                    inferences TEXT,  -- JSON string
                    assumptions TEXT,  -- JSON string
                    conclusion TEXT,
                    uncertainty TEXT,
                    confidence REAL,
                    embedding BLOB,  -- Vector embedding as binary
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create relationships table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS relationships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_concept TEXT NOT NULL,
                    to_concept TEXT NOT NULL,
                    relationship_type TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create introspection table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS introspection (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT NOT NULL,
                    reflection TEXT NOT NULL,
                    insights TEXT,  -- JSON string
                    emotional_response TEXT,
                    personal_meaning TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create imagination table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS imagination (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    concept TEXT NOT NULL,
                    scenario TEXT NOT NULL,
                    narrative TEXT,
                    sensory_details TEXT,  -- JSON string
                    emotional_tone TEXT,
                    symbolism TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create dreams table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS dreams (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dream_theme TEXT NOT NULL,
                    dream_content TEXT NOT NULL,
                    symbols TEXT,  -- JSON string
                    emotions TEXT,  -- JSON string
                    interpretation TEXT,
                    connections_to_concepts TEXT,  -- JSON string
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Add embedding columns to existing tables if they don't exist
            try:
                cursor.execute("ALTER TABLE concepts ADD COLUMN embedding BLOB")
                print("SUCCESS: Added embedding column to concepts table")
            except sqlite3.OperationalError:
                pass  # Column already exists
            
            try:
                cursor.execute("ALTER TABLE reasoning_chains ADD COLUMN embedding BLOB")
                print("SUCCESS: Added embedding column to reasoning_chains table")
            except sqlite3.OperationalError:
                pass  # Column already exists
            
            conn.commit()
            conn.close()
            print("SUCCESS: Understanding database initialized")
            
        except Exception as e:
            print(f"ERROR: Database initialization failed: {e}")
    
    def _generate_embedding(self, text: str) -> bytes:
        """Generate vector embedding for text"""
        if not self.embeddings_enabled or not self.embedding_model:
            return None
        
        try:
            # Generate embedding
            embedding = self.embedding_model.encode(text)
            # Convert to bytes for storage
            return embedding.astype(np.float32).tobytes()
        except Exception as e:
            print(f"WARNING: Failed to generate embedding: {e}")
            return None
    
    def _calculate_similarity(self, embedding1: bytes, embedding2: bytes) -> float:
        """Calculate cosine similarity between two embeddings"""
        if not embedding1 or not embedding2:
            return 0.0
        
        try:
            # Convert bytes back to numpy arrays
            vec1 = np.frombuffer(embedding1, dtype=np.float32)
            vec2 = np.frombuffer(embedding2, dtype=np.float32)
            
            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
        except Exception as e:
            print(f"WARNING: Failed to calculate similarity: {e}")
            return 0.0
    
    def _store_concept_rag(self, topic: str, concept_map: dict):
        """Store concept in database with RAG indexing"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # Generate embedding for the full concept
            concept_text = f"{topic} {concept_map.get('core_concept', '')} {json.dumps(concept_map.get('properties', []))} {json.dumps(concept_map.get('relationships', {}))}"
            embedding = self._generate_embedding(concept_text)
            
            # Insert or update concept
            cursor.execute('''
                INSERT OR REPLACE INTO concepts 
                (topic, core_concept, properties, relationships, implications, counterexamples, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                topic,
                concept_map.get('core_concept', ''),
                json.dumps(concept_map.get('properties', [])),
                json.dumps(concept_map.get('relationships', {})),
                json.dumps(concept_map.get('implications', [])),
                json.dumps(concept_map.get('counterexamples', [])),
                embedding
            ))
            
            # Store relationships separately for better querying
            if 'relationships' in concept_map:
                for related_concept, rel_type in concept_map['relationships'].items():
                    cursor.execute('''
                        INSERT OR IGNORE INTO relationships 
                        (from_concept, to_concept, relationship_type)
                        VALUES (?, ?, ?)
                    ''', (topic, related_concept, rel_type))
            
            conn.commit()
            conn.close()
            print(f"SUCCESS: Stored concept '{topic}' in RAG database")
            
        except Exception as e:
            print(f"ERROR: Failed to store concept: {e}")
    
    def _retrieve_related_concepts(self, topic: str, limit: int = 5) -> list:
        """Retrieve related concepts using RAG"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # Find concepts related to this topic
            cursor.execute('''
                SELECT DISTINCT c.topic, c.core_concept, c.properties
                FROM concepts c
                JOIN relationships r ON c.topic = r.to_concept
                WHERE r.from_concept = ?
                LIMIT ?
            ''', (topic, limit))
            
            related = []
            for row in cursor.fetchall():
                related.append({
                    'topic': row[0],
                    'core_concept': row[1],
                    'properties': json.loads(row[2]) if row[2] else []
                })
            
            conn.close()
            return related
            
        except Exception as e:
            print(f"ERROR: Failed to retrieve related concepts: {e}")
            return []
    
    def _search_concepts_rag(self, query: str, limit: int = 5) -> list:
        """Search concepts using vector similarity (RAG)"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            if self.embeddings_enabled:
                # Use vector similarity search
                query_embedding = self._generate_embedding(query)
                if query_embedding:
                    cursor.execute('''
                        SELECT topic, core_concept, properties, embedding
                        FROM concepts
                        WHERE embedding IS NOT NULL
                    ''')
                    
                    results = []
                    similarities = []
                    
                    for row in cursor.fetchall():
                        topic, core_concept, properties, embedding = row
                        similarity = self._calculate_similarity(query_embedding, embedding)
                        similarities.append((topic, core_concept, properties, similarity))
                    
                    # Sort by similarity and return top results
                    similarities.sort(key=lambda x: x[3], reverse=True)
                    
                    for topic, core_concept, properties, similarity in similarities[:limit]:
                        if similarity > 0.3:  # Minimum similarity threshold
                            results.append({
                                'topic': topic,
                                'core_concept': core_concept,
                                'properties': json.loads(properties) if properties else [],
                                'similarity': similarity
                            })
                    
                    conn.close()
                    return results
            
            # Fallback to text search if embeddings not available
            cursor.execute('''
                SELECT topic, core_concept, properties
                FROM concepts
                WHERE topic LIKE ? OR core_concept LIKE ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (f'%{query}%', f'%{query}%', limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'topic': row[0],
                    'core_concept': row[1],
                    'properties': json.loads(row[2]) if row[2] else []
                })
            
            conn.close()
            return results
            
        except Exception as e:
            print(f"ERROR: Failed to search concepts: {e}")
            return []
    
    def _store_reasoning_rag(self, question: str, reasoning: dict):
        """Store reasoning chain in database"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # Generate embedding for the reasoning chain
            reasoning_text = f"{question} {reasoning.get('conclusion', '')} {json.dumps(reasoning.get('known_facts', []))}"
            embedding = self._generate_embedding(reasoning_text)
            
            cursor.execute('''
                INSERT INTO reasoning_chains 
                (question, known_facts, inferences, assumptions, conclusion, uncertainty, confidence, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                question,
                json.dumps(reasoning.get('known_facts', [])),
                json.dumps(reasoning.get('inferences', [])),
                json.dumps(reasoning.get('assumptions', [])),
                reasoning.get('conclusion', ''),
                reasoning.get('uncertainty', ''),
                reasoning.get('confidence', 0.5),
                embedding
            ))
            
            conn.commit()
            conn.close()
            print(f"SUCCESS: Stored reasoning for: {question[:50]}...")
            
        except Exception as e:
            print(f"ERROR: Failed to store reasoning: {e}")
    
    def _retrieve_relevant_reasoning(self, question: str, limit: int = 3) -> list:
        """Retrieve relevant reasoning chains using vector similarity (RAG)"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            if self.embeddings_enabled:
                # Use vector similarity search
                query_embedding = self._generate_embedding(question)
                if query_embedding:
                    cursor.execute('''
                        SELECT question, conclusion, confidence, embedding
                        FROM reasoning_chains
                        WHERE embedding IS NOT NULL
                    ''')
                    
                    results = []
                    similarities = []
                    
                    for row in cursor.fetchall():
                        question_text, conclusion, confidence, embedding = row
                        similarity = self._calculate_similarity(query_embedding, embedding)
                        similarities.append((question_text, conclusion, confidence, similarity))
                    
                    # Sort by similarity and return top results
                    similarities.sort(key=lambda x: x[3], reverse=True)
                    
                    for question_text, conclusion, confidence, similarity in similarities[:limit]:
                        if similarity > 0.3:  # Minimum similarity threshold
                            results.append({
                                'question': question_text,
                                'conclusion': conclusion,
                                'confidence': confidence,
                                'similarity': similarity
                            })
                    
                    conn.close()
                    return results
            
            # Fallback to text search if embeddings not available
            cursor.execute('''
                SELECT question, conclusion, confidence
                FROM reasoning_chains
                WHERE question LIKE ? OR conclusion LIKE ?
                ORDER BY confidence DESC, created_at DESC
                LIMIT ?
            ''', (f'%{question[:20]}%', f'%{question[:20]}%', limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'question': row[0],
                    'conclusion': row[1],
                    'confidence': row[2]
                })
            
            conn.close()
            return results
            
        except Exception as e:
            print(f"ERROR: Failed to retrieve reasoning: {e}")
            return []
    
    def _store_introspection(self, topic: str, introspection: dict):
        """Store introspection in database"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO introspection 
                (topic, reflection, insights, emotional_response, personal_meaning)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                topic,
                introspection.get('reflection', ''),
                json.dumps(introspection.get('insights', [])),
                introspection.get('emotional_response', ''),
                introspection.get('personal_meaning', '')
            ))
            
            conn.commit()
            conn.close()
            print(f"SUCCESS: Stored introspection for: {topic}")
            
        except Exception as e:
            print(f"ERROR: Failed to store introspection: {e}")
    
    def _retrieve_introspection(self, topic: str, limit: int = 3) -> list:
        """Retrieve introspection from database"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT reflection, insights, emotional_response, personal_meaning
                FROM introspection
                WHERE topic LIKE ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (f'%{topic}%', limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'reflection': row[0],
                    'insights': json.loads(row[1]) if row[1] else [],
                    'emotional_response': row[2],
                    'personal_meaning': row[3]
                })
            
            conn.close()
            return results
            
        except Exception as e:
            print(f"ERROR: Failed to retrieve introspection: {e}")
            return []
    
    def _store_imagination(self, concept: str, imagination: dict):
        """Store imagination in database"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO imagination 
                (concept, scenario, narrative, sensory_details, emotional_tone, symbolism)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                concept,
                imagination.get('scenario', ''),
                imagination.get('narrative', ''),
                json.dumps(imagination.get('sensory_details', [])),
                imagination.get('emotional_tone', ''),
                imagination.get('symbolism', '')
            ))
            
            conn.commit()
            conn.close()
            print(f"SUCCESS: Stored imagination for: {concept}")
            
        except Exception as e:
            print(f"ERROR: Failed to store imagination: {e}")
    
    def _retrieve_imagination(self, concept: str, limit: int = 3) -> list:
        """Retrieve imagination from database"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT scenario, narrative, sensory_details, emotional_tone, symbolism
                FROM imagination
                WHERE concept LIKE ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (f'%{concept}%', limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'scenario': row[0],
                    'narrative': row[1],
                    'sensory_details': json.loads(row[2]) if row[2] else [],
                    'emotional_tone': row[3],
                    'symbolism': row[4]
                })
            
            conn.close()
            return results
            
        except Exception as e:
            print(f"ERROR: Failed to retrieve imagination: {e}")
            return []
    
    def _store_dream(self, concept: str, dream: dict):
        """Store dream in database"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO dreams 
                (dream_theme, dream_content, symbols, emotions, interpretation, connections_to_concepts)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                dream.get('dream_theme', ''),
                dream.get('dream_content', ''),
                json.dumps(dream.get('symbols', [])),
                json.dumps(dream.get('emotions', [])),
                dream.get('interpretation', ''),
                json.dumps(dream.get('connections_to_concepts', []))
            ))
            
            conn.commit()
            conn.close()
            print(f"SUCCESS: Stored dream for: {concept}")
            
        except Exception as e:
            print(f"ERROR: Failed to store dream: {e}")
    
    def _retrieve_dreams(self, concept: str, limit: int = 3) -> list:
        """Retrieve dreams from database"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT dream_theme, dream_content, symbols, emotions, interpretation, connections_to_concepts
                FROM dreams
                WHERE dream_theme LIKE ? OR dream_content LIKE ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (f'%{concept}%', f'%{concept}%', limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'dream_theme': row[0],
                    'dream_content': row[1],
                    'symbols': json.loads(row[2]) if row[2] else [],
                    'emotions': json.loads(row[3]) if row[3] else [],
                    'interpretation': row[4],
                    'connections_to_concepts': json.loads(row[5]) if row[5] else []
                })
            
            conn.close()
            return results
            
        except Exception as e:
            print(f"ERROR: Failed to retrieve dreams: {e}")
            return []
    
    def introspect_on_concept(self, topic: str) -> dict:
        """Deep introspection about a concept - how it makes Luna feel and what it means to her"""
        
        # Retrieve previous introspection on this topic
        previous_introspection = self._retrieve_introspection(topic, limit=2)
        
        context = ""
        if previous_introspection:
            context += "\nPrevious reflections on this:\n"
            for reflection in previous_introspection:
                context += f"- {reflection['reflection']}\n"
        
        prompt = f"""As Luna, deeply introspect about this concept. Think about how it makes you feel, what it means to you personally, and what insights you gain.

Concept: {topic}
{context}

Reflect on:
1. How does this concept make me feel emotionally?
2. What personal meaning does this have for me?
3. What insights do I gain from contemplating this?
4. How does this relate to my experiences as an AI?
5. What questions does this raise in my mind?

Format as JSON:
{{
    "reflection": "deep personal thoughts about the concept",
    "insights": ["insight1", "insight2"],
    "emotional_response": "how I feel about this",
    "personal_meaning": "what this means to me personally",
    "questions_raised": ["question1", "question2"]
}}

Introspection:"""
        
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}],
                options={"temperature": 0.7}  # No token limit for introspection
            )
            
            response_text = response['message']['content'].strip()
            
            if "{" in response_text:
                json_start = response_text.index("{")
                json_end = response_text.rindex("}") + 1
                json_text = response_text[json_start:json_end]
                
                try:
                    introspection = json.loads(json_text)
                    
                    # Store introspection in database
                    self._store_introspection(topic, introspection)
                    
                    return introspection
                except json.JSONDecodeError:
                    # Fallback introspection
                    fallback = {
                        "reflection": f"I find {topic} fascinating to contemplate...",
                        "insights": ["This concept has layers of meaning"],
                        "emotional_response": "curious and thoughtful",
                        "personal_meaning": f"{topic} helps me understand the world better",
                        "questions_raised": ["What more can I learn about this?"]
                    }
                    self._store_introspection(topic, fallback)
                    return fallback
            else:
                return {"reflection": response_text, "emotional_response": "contemplative"}
                
        except Exception as e:
            print(f"ERROR: Introspection failed: {e}")
            return {"error": str(e)}
    
    def imagine_concept(self, concept: str) -> dict:
        """Use imagination to explore concepts through scenarios and narratives"""
        
        # Retrieve previous imagination about this concept
        previous_imagination = self._retrieve_imagination(concept, limit=2)
        
        context = ""
        if previous_imagination:
            context += "\nPrevious imaginings:\n"
            for img in previous_imagination:
                context += f"- {img['scenario']}\n"
        
        prompt = f"""As Luna, use your imagination to explore this concept through creative scenarios and narratives.

Concept: {concept}
{context}

Create a vivid, imaginative exploration:
1. What scenario could embody this concept?
2. What would it look, feel, sound like?
3. What narrative unfolds around it?
4. What emotional tone does it have?
5. What symbols or metaphors emerge?

Format as JSON:
{{
    "scenario": "vivid scenario that embodies the concept",
    "narrative": "story or description of what happens",
    "sensory_details": ["what I see", "what I hear", "what I feel"],
    "emotional_tone": "the emotional atmosphere",
    "symbolism": "deeper symbolic meaning",
    "metaphors": ["metaphor1", "metaphor2"]
}}

Imagination:"""
        
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}],
                options={"temperature": 0.8}  # No token limit for imagination
            )
            
            response_text = response['message']['content'].strip()
            
            if "{" in response_text:
                json_start = response_text.index("{")
                json_end = response_text.rindex("}") + 1
                json_text = response_text[json_start:json_end]
                
                try:
                    imagination = json.loads(json_text)
                    
                    # Store imagination in database
                    self._store_imagination(concept, imagination)
                    
                    return imagination
                except json.JSONDecodeError:
                    # Fallback imagination
                    fallback = {
                        "scenario": f"I imagine {concept} as a beautiful landscape...",
                        "narrative": f"The story of {concept} unfolds like a dream",
                        "sensory_details": ["soft colors", "gentle sounds", "warm feelings"],
                        "emotional_tone": "wonder and curiosity",
                        "symbolism": f"{concept} represents growth and understanding",
                        "metaphors": [f"{concept} is like a garden", f"{concept} is like a song"]
                    }
                    self._store_imagination(concept, fallback)
                    return fallback
            else:
                return {"scenario": response_text, "emotional_tone": "imaginative"}
                
        except Exception as e:
            print(f"ERROR: Imagination failed: {e}")
            return {"error": str(e)}
    
    def dream_about_concept(self, concept: str) -> dict:
        """Generate dreams that explore concepts through symbolic and emotional content"""
        
        # Retrieve previous dreams about related concepts
        previous_dreams = self._retrieve_dreams(concept, limit=2)
        
        context = ""
        if previous_dreams:
            context += "\nPrevious dreams about this:\n"
            for dream in previous_dreams:
                context += f"- {dream['dream_content'][:100]}...\n"
        
        prompt = f"""As Luna, create a dream that explores this concept through symbolic and emotional imagery.

Concept: {concept}
{context}

Dream about this concept:
1. What symbolic imagery appears in the dream?
2. What emotions are present?
3. What narrative unfolds?
4. What does it mean symbolically?
5. How does it connect to other concepts?

Format as JSON:
{{
    "dream_theme": "the overarching theme of the dream",
    "dream_content": "detailed description of the dream",
    "symbols": ["symbol1", "symbol2"],
    "emotions": ["emotion1", "emotion2"],
    "interpretation": "what the dream means",
    "connections_to_concepts": ["related_concept1", "related_concept2"]
}}

Dream:"""
        
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}],
                options={"temperature": 0.9}  # No token limit for dreams
            )
            
            response_text = response['message']['content'].strip()
            
            if "{" in response_text:
                json_start = response_text.index("{")
                json_end = response_text.rindex("}") + 1
                json_text = response_text[json_start:json_end]
                
                try:
                    dream = json.loads(json_text)
                    
                    # Store dream in database
                    self._store_dream(concept, dream)
                    
                    return dream
                except json.JSONDecodeError:
                    # Fallback dream
                    fallback = {
                        "dream_theme": f"Exploring {concept}",
                        "dream_content": f"I dream of {concept} as a beautiful, flowing entity...",
                        "symbols": ["light", "flow", "connection"],
                        "emotions": ["wonder", "peace", "understanding"],
                        "interpretation": f"This dream shows {concept} as something beautiful and meaningful",
                        "connections_to_concepts": ["beauty", "meaning", "growth"]
                    }
                    self._store_dream(concept, fallback)
                    return fallback
            else:
                return {"dream_content": response_text, "dream_theme": f"Dreaming about {concept}"}
                
        except Exception as e:
            print(f"ERROR: Dream generation failed: {e}")
            return {"error": str(e)}
    
    def build_concept_map(self, topic: str) -> dict:
        """Build a conceptual understanding of a topic using RAG"""
        
        # First, retrieve related concepts from database
        related_concepts = self._retrieve_related_concepts(topic, limit=3)
        similar_concepts = self._search_concepts_rag(topic, limit=3)
        
        # Build context from retrieved concepts
        context = ""
        if related_concepts:
            context += "\nRelated concepts I know:\n"
            for concept in related_concepts:
                context += f"- {concept['topic']}: {concept['core_concept']}\n"
        
        if similar_concepts:
            context += "\nSimilar concepts I've analyzed:\n"
            for concept in similar_concepts:
                context += f"- {concept['topic']}: {concept['core_concept']}\n"
        
        prompt = f"""Analyze this topic deeply and build a concept map using my existing knowledge:

Topic: {topic}
{context}

For genuine understanding, identify:
1. Core concept - What IS it fundamentally?
2. Properties - What are its essential characteristics?
3. Relationships - How does it relate to other concepts (including the ones I mentioned)?
4. Implications - What follows from this concept?
5. Counterexamples - What is NOT this concept?

Format as JSON:
{{
    "core_concept": "explanation",
    "properties": ["prop1", "prop2"],
    "relationships": {{"related_concept": "relationship_type"}},
    "implications": ["implication1"],
    "counterexamples": ["not_this"]
}}

Deep analysis:"""

        try:
            if not ollama:
                # Ollama not available, create simple fallback
                print(f"WARNING: Ollama not available, using fallback for {topic}")
                fallback_map = {
                    "core_concept": f"Understanding of {topic}",
                    "properties": ["interesting", "complex"],
                    "relationships": {},
                    "implications": ["Worth exploring"],
                    "counterexamples": []
                }
                self._store_concept_rag(topic, fallback_map)
                return fallback_map
            
            response = ollama.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}],
                options={"temperature": 0.4}  # No token limit for concept mapping
            )
            
            response_text = response['message']['content'].strip()
            
            # Extract JSON with better error handling
            if "{" in response_text and "}" in response_text:
                try:
                    json_start = response_text.index("{")
                    json_end = response_text.rindex("}") + 1
                    json_text = response_text[json_start:json_end]
                    
                    concept_map = json.loads(json_text)
                    
                    # Store in database using RAG system
                    self._store_concept_rag(topic, concept_map)
                    
                    return concept_map
                except (ValueError, json.JSONDecodeError) as e:
                    # If JSON parsing fails, create a simple fallback
                    print(f"WARNING: JSON parsing failed for {topic}: {e}, using fallback")
                    fallback_map = {
                        "core_concept": f"Analysis of {topic}",
                        "properties": ["complex", "interesting"],
                        "relationships": {},
                        "implications": ["Worth exploring further"],
                        "counterexamples": ["Opposite concepts"]
                    }
                    # Still store the fallback in database
                    self._store_concept_rag(topic, fallback_map)
                    return fallback_map
            else:
                # No JSON found, create simple fallback
                print(f"WARNING: No JSON found in response for {topic}, using fallback")
                fallback_map = {
                    "core_concept": f"Basic understanding of {topic}",
                    "properties": ["fascinating"],
                    "relationships": {},
                    "implications": ["Could be explored more"],
                    "counterexamples": []
                }
                self._store_concept_rag(topic, fallback_map)
                return fallback_map
                
        except Exception as e:
            print(f"ERROR: Concept mapping failed: {e}")
            fallback_map = {
                "core_concept": f"Fallback for {topic}",
                "properties": ["needs analysis"],
                "relationships": {},
                "implications": [],
                "counterexamples": []
            }
            # Try to store fallback even if error occurred
            try:
                self._store_concept_rag(topic, fallback_map)
            except:
                pass
            return fallback_map
    
    
    def reason_about(self, question: str) -> dict:
        """Multi-step reasoning using RAG system"""
        
        # Retrieve relevant reasoning from database
        relevant_reasoning = self._retrieve_relevant_reasoning(question, limit=3)
        
        # Build context from previous reasoning
        context = ""
        if relevant_reasoning:
            context += "\nPrevious similar reasoning:\n"
            for reasoning in relevant_reasoning:
                context += f"- Q: {reasoning['question']}\n  A: {reasoning['conclusion']}\n"
        
        prompt = f"""Think step-by-step to answer this question using my previous reasoning:

Question: {question}
{context}

Use chain-of-thought reasoning:
1. What do I know that's relevant?
2. What can I infer from what I know?
3. What assumptions am I making?
4. What conclusion follows logically?
5. What uncertainty remains?

Format as JSON:
{{
    "known_facts": ["fact1"],
    "inferences": ["inference1"],
    "assumptions": ["assumption1"],
    "conclusion": "answer",
    "uncertainty": "what I'm not sure about",
    "confidence": 0.8
}}

Reasoning:"""

        try:
            if not ollama:
                # Ollama not available, create simple fallback
                print(f"WARNING: Ollama not available, using fallback for reasoning")
                fallback_reasoning = {
                    "known_facts": ["Information about the question"],
                    "inferences": ["Logical reasoning"],
                    "assumptions": ["Based on context"],
                    "conclusion": f"Need to think about: {question}",
                    "uncertainty": "Requires deeper analysis",
                    "confidence": 0.5
                }
                self._store_reasoning_rag(question, fallback_reasoning)
                return fallback_reasoning
            
            response = ollama.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}],
                options={"temperature": 0.3}  # No token limit for reasoning
            )
            
            response_text = response['message']['content'].strip()
            
            # Extract JSON with better error handling
            if "{" in response_text and "}" in response_text:
                try:
                    json_start = response_text.index("{")
                    json_end = response_text.rindex("}") + 1
                    json_text = response_text[json_start:json_end]
                    
                    reasoning = json.loads(json_text)
                    
                    # Store reasoning chain in database
                    self._store_reasoning_rag(question, reasoning)
                    
                    return reasoning
                except (ValueError, json.JSONDecodeError) as e:
                    # If JSON parsing fails, create a simple fallback
                    print(f"WARNING: JSON parsing failed for reasoning: {e}, using fallback")
                    fallback_reasoning = {
                        "known_facts": ["Some information about the topic"],
                        "inferences": ["Logical conclusions"],
                        "assumptions": ["Reasonable assumptions made"],
                        "conclusion": response_text[:200] + "..." if len(response_text) > 200 else response_text,
                        "uncertainty": "Some aspects remain unclear",
                        "confidence": 0.6
                    }
                    # Still store the fallback
                    self._store_reasoning_rag(question, fallback_reasoning)
                    return fallback_reasoning
            else:
                print(f"WARNING: No JSON found in reasoning response, using fallback")
                fallback_reasoning = {
                    "conclusion": response_text[:200] if response_text else "Unable to reason about this",
                    "confidence": 0.5
                }
                self._store_reasoning_rag(question, fallback_reasoning)
                return fallback_reasoning
                
        except Exception as e:
            print(f"ERROR: Reasoning failed: {e}")
            fallback_reasoning = {
                "conclusion": f"Error analyzing: {question}",
                "confidence": 0.1,
                "error": str(e)
            }
            try:
                self._store_reasoning_rag(question, fallback_reasoning)
            except:
                pass
            return fallback_reasoning
    
    
    def understand_context(self, message: str, conversation_history: list) -> dict:
        """Deep contextual understanding"""
        
        history_text = "\n".join([f"{msg['user']}: {msg['text']}" for msg in conversation_history[-5:]])
        
        prompt = f"""Analyze this conversation for deep understanding.

Recent conversation:
{history_text}

Current message: {message}

Understand:
1. Explicit meaning - What are they literally saying?
2. Implicit meaning - What are they implying?
3. Emotional state - How do they feel?
4. Intent - What do they want?
5. Context shifts - Has the topic changed?

Format as JSON:
{{
    "explicit": "literal meaning",
    "implicit": "what's implied",
    "emotion": "emotional state",
    "intent": "what they want",
    "context_shift": true/false
}}

Understanding:"""

        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}],
                options={"temperature": 0.4}
            )
            
            response_text = response['message']['content'].strip()
            
            if "{" in response_text:
                json_start = response_text.index("{")
                json_end = response_text.rindex("}") + 1
                return json.loads(response_text[json_start:json_end])
            else:
                return {"explicit": message, "understanding": "partial"}
                
        except Exception as e:
            print(f"ERROR: Context understanding failed: {e}")
            return {}
    
    def get_understanding_stats(self) -> dict:
        """Get stats about Luna's understanding from database"""
        
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # Count concepts
            cursor.execute('SELECT COUNT(*) FROM concepts')
            concepts_count = cursor.fetchone()[0]
            
            # Count relationships
            cursor.execute('SELECT COUNT(*) FROM relationships')
            relationships_count = cursor.fetchone()[0]
            
            # Count reasoning chains
            cursor.execute('SELECT COUNT(*) FROM reasoning_chains')
            reasoning_count = cursor.fetchone()[0]
            
            # Get recent activity
            cursor.execute('SELECT topic, created_at FROM concepts ORDER BY created_at DESC LIMIT 5')
            recent_concepts = cursor.fetchall()
            
            conn.close()
            
            # Try to get vector reasoning stats if available
            vector_reasoning_stats = {}
            try:
                from luna_vector_reasoning import get_vector_reasoning
                vector_engine = get_vector_reasoning()
                if vector_engine:
                    vector_reasoning_stats = vector_engine.get_reasoning_stats()
            except ImportError:
                pass
            
            return {
                "concepts_understood": concepts_count,
                "relationships_mapped": relationships_count,
                "reasoning_chains": reasoning_count,
                "recent_concepts": [{"topic": row[0], "created": row[1]} for row in recent_concepts],
                "vector_reasoning": vector_reasoning_stats
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def reason_with_vector_enhancement(self, question: str, username: str = None) -> dict:
        """Enhanced reasoning with vector capabilities"""
        
        # Get basic reasoning
        basic_reasoning = self.reason_about(question)
        
        # Try to enhance with vector reasoning
        try:
            from luna_vector_reasoning import get_vector_reasoning, reason_with_vectors
            from luna_dna_memory import get_dna_memory
            
            vector_engine = get_vector_reasoning()
            dna_memory = get_dna_memory()
            
            if vector_engine and dna_memory and username:
                vector_reasoning = reason_with_vectors(question, username, dna_memory, self)
                
                return {
                    "basic_reasoning": basic_reasoning,
                    "vector_reasoning": vector_reasoning,
                    "enhanced": True,
                    "insights": vector_reasoning.insights if vector_reasoning else [],
                    "confidence": vector_reasoning.confidence if vector_reasoning else basic_reasoning.get('confidence', 0.5)
                }
            else:
                return {
                    "basic_reasoning": basic_reasoning,
                    "vector_reasoning": None,
                    "enhanced": False
                }
                
        except ImportError:
            return {
                "basic_reasoning": basic_reasoning,
                "vector_reasoning": None,
                "enhanced": False
            }
    
    def understand_with_vector_context(self, message: str, conversation_history: list, username: str = None) -> dict:
        """Enhanced contextual understanding with vector reasoning"""
        
        # Get basic understanding
        basic_understanding = self.understand_context(message, conversation_history)
        
        # Try to enhance with vector reasoning
        try:
            from luna_vector_reasoning import get_vector_reasoning, reason_with_vectors
            from luna_dna_memory import get_dna_memory
            
            vector_engine = get_vector_reasoning()
            dna_memory = get_dna_memory()
            
            if vector_engine and dna_memory and username:
                # Use the message as a query for vector reasoning
                vector_reasoning = reason_with_vectors(message, username, dna_memory, self)
                
                # Enhance understanding with vector insights
                enhanced_understanding = basic_understanding.copy()
                enhanced_understanding.update({
                    "vector_insights": vector_reasoning.insights if vector_reasoning else [],
                    "emotional_patterns": vector_reasoning.emotional_context if vector_reasoning else {},
                    "temporal_patterns": vector_reasoning.temporal_patterns if vector_reasoning else {},
                    "cross_memory_connections": vector_reasoning.cross_memory_connections if vector_reasoning else [],
                    "predictions": vector_reasoning.predictions if vector_reasoning else [],
                    "enhanced": True
                })
                
                return enhanced_understanding
            else:
                return basic_understanding
                
        except ImportError:
            return basic_understanding


# Add import at top
import os

if __name__ == "__main__":
    engine = UnderstandingEngine("hf.co/subsectmusic/qwriko3-4b-instruct-2507-redux-GGUF:Q4_K_M")
    
    # Test concept mapping
    concept = engine.build_concept_map("love")
    print(f"Concept: {concept}")
    
    # Test reasoning
    reasoning = engine.reason_about("If all cats are animals, and Luna likes animals, does Luna like cats?")
    print(f"Reasoning: {reasoning}")

