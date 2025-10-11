# luna_knowledge_graph.py
"""
Luna's Knowledge Graph System
=============================
Structured knowledge representation using graph databases for entity extraction,
relationship inference, and knowledge reasoning.

Features:
- Entity extraction and recognition
- Relationship mapping and inference
- Knowledge reasoning and traversal
- Dynamic graph updates from conversations
- Semantic relationship types
- Graph visualization and querying
"""

import sqlite3
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional, Set
import re
from collections import defaultdict, deque

# Try to import NetworkX for graph operations
try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    print("⚠️ NetworkX not available - install with: pip install networkx")


class LunaKnowledgeGraph:
    """
    Luna's Knowledge Graph System - Structured knowledge representation
    """
    
    def __init__(self, db_path: str = "luna_knowledge_graph.db"):
        self.db_path = db_path
        self.graph = nx.MultiDiGraph() if NETWORKX_AVAILABLE else None
        self._initialize_database()
        self._load_graph_from_db()
        
        # Predefined relationship types
        self.relationship_types = {
            'IS_A': 'type/category relationship',
            'HAS_A': 'possession/attribute relationship',
            'PART_OF': 'component relationship',
            'RELATED_TO': 'general association',
            'CAUSES': 'causation relationship',
            'LOCATED_IN': 'location relationship',
            'CREATED_BY': 'creator relationship',
            'USED_FOR': 'purpose relationship',
            'OPPOSED_TO': 'opposition relationship',
            'SIMILAR_TO': 'similarity relationship',
            'FRIEND_OF': 'friendship relationship',
            'LOVES': 'love relationship',
            'WORKS_ON': 'project/work relationship',
            'MEMBER_OF': 'membership relationship',
            'KNOWS_ABOUT': 'knowledge relationship',
            'INTERACTED_WITH': 'interaction relationship',
        }
        
        # Entity types
        self.entity_types = {
            'PERSON': ['user', 'friend', 'creator', 'streamer', 'viewer'],
            'CONCEPT': ['idea', 'topic', 'subject', 'theme'],
            'OBJECT': ['thing', 'item', 'tool', 'device'],
            'PLACE': ['location', 'platform', 'space'],
            'EVENT': ['happening', 'occurrence', 'activity'],
            'EMOTION': ['feeling', 'mood', 'sentiment'],
            'GAME': ['video game', 'board game', 'sport'],
            'TECHNOLOGY': ['software', 'hardware', 'platform'],
            'MEDIA': ['movie', 'show', 'music', 'video'],
        }
    
    def _initialize_database(self):
        """Initialize SQLite database for knowledge graph persistence"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Entities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entities (
                entity_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                entity_type TEXT,
                attributes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                importance_score REAL DEFAULT 1.0
            )
        ''')
        
        # Relationships table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS relationships (
                relationship_id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_entity TEXT NOT NULL,
                target_entity TEXT NOT NULL,
                relationship_type TEXT NOT NULL,
                confidence REAL DEFAULT 1.0,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(source_entity, target_entity, relationship_type)
            )
        ''')
        
        # Knowledge facts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_facts (
                fact_id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                predicate TEXT NOT NULL,
                object TEXT NOT NULL,
                confidence REAL DEFAULT 1.0,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Indices for faster queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_relationships_source ON relationships(source_entity)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_relationships_target ON relationships(target_entity)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_facts_subject ON knowledge_facts(subject)')
        
        conn.commit()
        conn.close()
        print("✅ Knowledge Graph database initialized")
    
    def _load_graph_from_db(self):
        """Load the knowledge graph from database into NetworkX graph"""
        if not NETWORKX_AVAILABLE:
            print("⚠️ NetworkX not available - graph operations limited")
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Load entities as nodes
        cursor.execute('SELECT name, entity_type, attributes, importance_score FROM entities')
        entities = cursor.fetchall()
        for name, entity_type, attributes_json, importance in entities:
            attrs = json.loads(attributes_json) if attributes_json else {}
            attrs['entity_type'] = entity_type
            attrs['importance_score'] = importance
            self.graph.add_node(name, **attrs)
        
        # Load relationships as edges
        cursor.execute('SELECT source_entity, target_entity, relationship_type, confidence, metadata FROM relationships')
        relationships = cursor.fetchall()
        for source, target, rel_type, confidence, metadata_json in relationships:
            metadata = json.loads(metadata_json) if metadata_json else {}
            metadata['confidence'] = confidence
            self.graph.add_edge(source, target, relationship_type=rel_type, **metadata)
        
        conn.close()
        print(f"✅ Loaded {self.graph.number_of_nodes()} entities and {self.graph.number_of_edges()} relationships")
    
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract entities from text using pattern matching and heuristics
        Returns list of entities with their types
        """
        entities = []
        text_lower = text.lower()
        
        # Extract proper nouns (capitalized words)
        proper_nouns = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        for noun in proper_nouns:
            if len(noun) > 2:  # Filter out short words
                entity_type = self._infer_entity_type(noun, text_lower)
                entities.append({
                    'name': noun,
                    'type': entity_type,
                    'confidence': 0.8
                })
        
        # Extract quoted phrases (often important concepts)
        quoted = re.findall(r'"([^"]+)"', text)
        for quote in quoted:
            entities.append({
                'name': quote,
                'type': 'CONCEPT',
                'confidence': 0.7
            })
        
        # Extract common entity patterns
        patterns = {
            r'\b(user|streamer|viewer|friend|creator)\s+(\w+)': 'PERSON',
            r'\b(game|video game|board game)\s+([A-Za-z0-9\s]+)': 'GAME',
            r'\b(platform|website|app)\s+(\w+)': 'TECHNOLOGY',
            r'\b(movie|show|series|video)\s+([A-Za-z0-9\s]+)': 'MEDIA',
        }
        
        for pattern, entity_type in patterns.items():
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                entity_name = match.group(2).strip()
                if len(entity_name) > 2:
                    entities.append({
                        'name': entity_name.title(),
                        'type': entity_type,
                        'confidence': 0.9
                    })
        
        return entities
    
    def _infer_entity_type(self, entity_name: str, context: str) -> str:
        """Infer entity type based on context and keywords"""
        entity_lower = entity_name.lower()
        
        # Check for known entity types based on context
        for entity_type, keywords in self.entity_types.items():
            for keyword in keywords:
                if keyword in context:
                    return entity_type
        
        # Default heuristics
        if any(word in entity_lower for word in ['chris', 'luna', 'user', 'streamer', 'viewer']):
            return 'PERSON'
        elif any(word in entity_lower for word in ['twitch', 'discord', 'youtube', 'twitter']):
            return 'TECHNOLOGY'
        elif any(word in entity_lower for word in ['game', 'play', 'gaming']):
            return 'GAME'
        
        return 'CONCEPT'  # Default
    
    def add_entity(self, name: str, entity_type: str = 'CONCEPT', attributes: Dict = None) -> bool:
        """Add or update an entity in the knowledge graph"""
        if not NETWORKX_AVAILABLE:
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        attributes_json = json.dumps(attributes) if attributes else '{}'
        
        try:
            cursor.execute('''
                INSERT INTO entities (name, entity_type, attributes, last_updated)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    entity_type = excluded.entity_type,
                    attributes = excluded.attributes,
                    last_updated = excluded.last_updated,
                    importance_score = importance_score + 0.1
            ''', (name, entity_type, attributes_json, datetime.now()))
            
            conn.commit()
            
            # Add to graph
            attrs = attributes.copy() if attributes else {}
            attrs['entity_type'] = entity_type
            if self.graph.has_node(name):
                # Update existing node
                self.graph.nodes[name].update(attrs)
            else:
                # Add new node
                self.graph.add_node(name, **attrs)
            
            return True
        except Exception as e:
            print(f"⚠️ Error adding entity {name}: {e}")
            return False
        finally:
            conn.close()
    
    def add_relationship(self, source: str, target: str, relationship_type: str, 
                        confidence: float = 1.0, metadata: Dict = None) -> bool:
        """Add or update a relationship between entities"""
        if not NETWORKX_AVAILABLE:
            return False
        
        # Ensure both entities exist
        self.add_entity(source)
        self.add_entity(target)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        metadata_json = json.dumps(metadata) if metadata else '{}'
        
        try:
            cursor.execute('''
                INSERT INTO relationships (source_entity, target_entity, relationship_type, confidence, metadata, last_updated)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(source_entity, target_entity, relationship_type) DO UPDATE SET
                    confidence = MAX(confidence, excluded.confidence),
                    metadata = excluded.metadata,
                    last_updated = excluded.last_updated
            ''', (source, target, relationship_type, confidence, metadata_json, datetime.now()))
            
            conn.commit()
            
            # Add to graph
            edge_attrs = metadata.copy() if metadata else {}
            edge_attrs['confidence'] = confidence
            self.graph.add_edge(source, target, relationship_type=relationship_type, **edge_attrs)
            
            return True
        except Exception as e:
            print(f"⚠️ Error adding relationship {source} -> {target}: {e}")
            return False
        finally:
            conn.close()
    
    def add_knowledge_fact(self, subject: str, predicate: str, obj: str, 
                          confidence: float = 1.0, source: str = None) -> bool:
        """Add a knowledge fact (triple) to the graph"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO knowledge_facts (subject, predicate, object, confidence, source)
                VALUES (?, ?, ?, ?, ?)
            ''', (subject, predicate, obj, confidence, source))
            
            conn.commit()
            
            # Also add as a relationship
            self.add_relationship(subject, obj, predicate, confidence)
            
            return True
        except Exception as e:
            print(f"⚠️ Error adding knowledge fact: {e}")
            return False
        finally:
            conn.close()
    
    def get_entity_relationships(self, entity_name: str, relationship_type: str = None) -> List[Dict]:
        """Get all relationships for an entity"""
        if not NETWORKX_AVAILABLE or not self.graph.has_node(entity_name):
            return []
        
        relationships = []
        
        # Outgoing edges
        for _, target, data in self.graph.out_edges(entity_name, data=True):
            if relationship_type is None or data.get('relationship_type') == relationship_type:
                relationships.append({
                    'direction': 'outgoing',
                    'source': entity_name,
                    'target': target,
                    'type': data.get('relationship_type'),
                    'confidence': data.get('confidence', 1.0)
                })
        
        # Incoming edges
        for source, _, data in self.graph.in_edges(entity_name, data=True):
            if relationship_type is None or data.get('relationship_type') == relationship_type:
                relationships.append({
                    'direction': 'incoming',
                    'source': source,
                    'target': entity_name,
                    'type': data.get('relationship_type'),
                    'confidence': data.get('confidence', 1.0)
                })
        
        return relationships
    
    def find_path(self, source: str, target: str, max_length: int = 5) -> List[List[str]]:
        """Find paths between two entities"""
        if not NETWORKX_AVAILABLE or not self.graph.has_node(source) or not self.graph.has_node(target):
            return []
        
        try:
            # Find all simple paths up to max_length
            paths = list(nx.all_simple_paths(self.graph, source, target, cutoff=max_length))
            return paths[:10]  # Limit to 10 paths
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return []
    
    def get_related_entities(self, entity_name: str, max_depth: int = 2, limit: int = 20) -> List[Dict]:
        """Get entities related to the given entity up to max_depth"""
        if not NETWORKX_AVAILABLE or not self.graph.has_node(entity_name):
            return []
        
        related = []
        visited = {entity_name}
        queue = deque([(entity_name, 0)])
        
        while queue and len(related) < limit:
            current, depth = queue.popleft()
            
            if depth >= max_depth:
                continue
            
            # Get neighbors
            for neighbor in self.graph.neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    
                    # Get edge data
                    edge_data = self.graph.get_edge_data(current, neighbor)
                    if edge_data:
                        # Get the first edge (in case of multi-edges)
                        first_edge = list(edge_data.values())[0]
                        related.append({
                            'entity': neighbor,
                            'depth': depth + 1,
                            'relationship': first_edge.get('relationship_type', 'RELATED_TO'),
                            'confidence': first_edge.get('confidence', 1.0)
                        })
                    
                    queue.append((neighbor, depth + 1))
        
        return related
    
    def reason_about_entity(self, entity_name: str) -> str:
        """Generate reasoning about an entity based on its knowledge graph"""
        if not NETWORKX_AVAILABLE or not self.graph.has_node(entity_name):
            return f"I don't have much knowledge about {entity_name} yet."
        
        # Get entity attributes
        entity_data = self.graph.nodes[entity_name]
        entity_type = entity_data.get('entity_type', 'unknown')
        
        # Get relationships
        relationships = self.get_entity_relationships(entity_name)
        
        # Build reasoning
        reasoning_parts = [f"Let me think about {entity_name}..."]
        
        if entity_type != 'unknown':
            reasoning_parts.append(f"{entity_name} is a {entity_type}.")
        
        # Group relationships by type
        rel_groups = defaultdict(list)
        for rel in relationships[:10]:  # Limit to 10 most relevant
            rel_groups[rel['type']].append(rel)
        
        # Describe relationships
        for rel_type, rels in rel_groups.items():
            if rel_type in self.relationship_types:
                if rels[0]['direction'] == 'outgoing':
                    targets = [r['target'] for r in rels]
                    reasoning_parts.append(f"{entity_name} {rel_type.lower().replace('_', ' ')} {', '.join(targets[:3])}.")
                else:
                    sources = [r['source'] for r in rels]
                    reasoning_parts.append(f"{', '.join(sources[:3])} {rel_type.lower().replace('_', ' ')} {entity_name}.")
        
        # Get related entities
        related = self.get_related_entities(entity_name, max_depth=2, limit=5)
        if related:
            related_names = [r['entity'] for r in related[:3]]
            reasoning_parts.append(f"It's also connected to {', '.join(related_names)}.")
        
        return " ".join(reasoning_parts)
    
    def learn_from_conversation(self, username: str, message: str, response: str) -> Dict[str, int]:
        """Extract and add knowledge from a conversation"""
        stats = {'entities': 0, 'relationships': 0, 'facts': 0}
        
        # Extract entities from both message and response
        message_entities = self.extract_entities(message)
        response_entities = self.extract_entities(response)
        
        all_entities = message_entities + response_entities
        
        # Add entities
        for entity in all_entities:
            if self.add_entity(entity['name'], entity['type']):
                stats['entities'] += 1
        
        # Create relationships between user and entities they mention
        for entity in message_entities:
            if self.add_relationship(username, entity['name'], 'KNOWS_ABOUT', confidence=0.7):
                stats['relationships'] += 1
        
        # Create relationships between entities mentioned together
        if len(all_entities) >= 2:
            for i in range(len(all_entities) - 1):
                entity1 = all_entities[i]
                entity2 = all_entities[i + 1]
                if entity1['name'] != entity2['name']:
                    if self.add_relationship(entity1['name'], entity2['name'], 'RELATED_TO', confidence=0.5):
                        stats['relationships'] += 1
        
        # Extract simple facts (subject-verb-object patterns)
        fact_patterns = [
            r'(\w+)\s+(is|are|was|were)\s+(\w+)',
            r'(\w+)\s+(has|have|had)\s+(\w+)',
            r'(\w+)\s+(likes|loves|hates|enjoys)\s+(\w+)',
        ]
        
        combined_text = f"{message} {response}"
        for pattern in fact_patterns:
            matches = re.finditer(pattern, combined_text.lower())
            for match in matches:
                subject, predicate, obj = match.groups()
                if len(subject) > 2 and len(obj) > 2:
                    if self.add_knowledge_fact(subject.title(), predicate.upper(), obj.title(), confidence=0.6, source='conversation'):
                        stats['facts'] += 1
        
        return stats
    
    def get_context_for_prompt(self, query: str, username: str, limit: int = 5) -> str:
        """Get knowledge graph context relevant to a query"""
        if not NETWORKX_AVAILABLE:
            return ""
        
        # Extract entities from query
        query_entities = self.extract_entities(query)
        
        if not query_entities:
            # If no entities found, try to get user's knowledge
            if self.graph.has_node(username):
                relationships = self.get_entity_relationships(username, 'KNOWS_ABOUT')
                if relationships:
                    entities_str = ', '.join([r['target'] for r in relationships[:3]])
                    return f"\n🧠 Knowledge: {username} knows about {entities_str}.\n"
            return ""
        
        # Build context from entities
        context_parts = []
        for entity_data in query_entities[:limit]:
            entity_name = entity_data['name']
            
            if self.graph.has_node(entity_name):
                # Get key facts about this entity
                relationships = self.get_entity_relationships(entity_name)
                if relationships:
                    rel_desc = []
                    for rel in relationships[:3]:
                        if rel['direction'] == 'outgoing':
                            rel_desc.append(f"{entity_name} {rel['type'].lower().replace('_', ' ')} {rel['target']}")
                        else:
                            rel_desc.append(f"{rel['source']} {rel['type'].lower().replace('_', ' ')} {entity_name}")
                    
                    if rel_desc:
                        context_parts.append("; ".join(rel_desc))
        
        if context_parts:
            return f"\n🧠 Knowledge Graph Context:\n" + "\n".join([f"• {part}" for part in context_parts]) + "\n"
        
        return ""
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge graph statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM entities')
        entity_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM relationships')
        relationship_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM knowledge_facts')
        fact_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT entity_type, COUNT(*) FROM entities GROUP BY entity_type')
        entities_by_type = dict(cursor.fetchall())
        
        conn.close()
        
        stats = {
            'total_entities': entity_count,
            'total_relationships': relationship_count,
            'total_facts': fact_count,
            'entities_by_type': entities_by_type,
            'graph_density': 0.0
        }
        
        if NETWORKX_AVAILABLE and self.graph:
            stats['graph_nodes'] = self.graph.number_of_nodes()
            stats['graph_edges'] = self.graph.number_of_edges()
            if stats['graph_nodes'] > 1:
                stats['graph_density'] = nx.density(self.graph)
        
        return stats


# Global knowledge graph instance
_knowledge_graph_instance = None


def initialize_knowledge_graph(db_path: str = "luna_knowledge_graph.db") -> LunaKnowledgeGraph:
    """Initialize the global knowledge graph instance"""
    global _knowledge_graph_instance
    if _knowledge_graph_instance is None:
        _knowledge_graph_instance = LunaKnowledgeGraph(db_path)
    return _knowledge_graph_instance


def get_knowledge_graph() -> Optional[LunaKnowledgeGraph]:
    """Get the global knowledge graph instance"""
    return _knowledge_graph_instance


# Convenience functions
def add_entity(name: str, entity_type: str = 'CONCEPT', attributes: Dict = None) -> bool:
    """Add an entity to the knowledge graph"""
    kg = get_knowledge_graph()
    return kg.add_entity(name, entity_type, attributes) if kg else False


def add_relationship(source: str, target: str, relationship_type: str, confidence: float = 1.0) -> bool:
    """Add a relationship to the knowledge graph"""
    kg = get_knowledge_graph()
    return kg.add_relationship(source, target, relationship_type, confidence) if kg else False


def reason_about(entity_name: str) -> str:
    """Generate reasoning about an entity"""
    kg = get_knowledge_graph()
    return kg.reason_about_entity(entity_name) if kg else f"I don't know much about {entity_name}."


def learn_from_conversation(username: str, message: str, response: str) -> Dict[str, int]:
    """Learn from a conversation and update the knowledge graph"""
    kg = get_knowledge_graph()
    return kg.learn_from_conversation(username, message, response) if kg else {}


def get_knowledge_context(query: str, username: str, limit: int = 5) -> str:
    """Get knowledge graph context for a query"""
    kg = get_knowledge_graph()
    return kg.get_context_for_prompt(query, username, limit) if kg else ""


if __name__ == "__main__":
    # Test the knowledge graph system
    print("🧠 Testing Luna Knowledge Graph System\n")
    
    kg = initialize_knowledge_graph()
    
    # Add some test entities and relationships
    print("Adding test knowledge...")
    kg.add_entity("Chris", "PERSON", {"role": "user", "preference": "gaming"})
    kg.add_entity("Luna", "PERSON", {"role": "AI assistant", "personality": "playful"})
    kg.add_entity("Twitch", "TECHNOLOGY", {"platform": "streaming"})
    kg.add_entity("Discord", "TECHNOLOGY", {"platform": "chat"})
    
    kg.add_relationship("Chris", "Luna", "INTERACTED_WITH")
    kg.add_relationship("Chris", "Twitch", "USES")
    kg.add_relationship("Luna", "Twitch", "WORKS_ON")
    kg.add_relationship("Luna", "Discord", "WORKS_ON")
    
    # Test reasoning
    print("\n🧠 Reasoning about Chris:")
    print(kg.reason_about_entity("Chris"))
    
    print("\n🧠 Reasoning about Luna:")
    print(kg.reason_about_entity("Luna"))
    
    # Test learning from conversation
    print("\n📚 Learning from conversation...")
    stats = kg.learn_from_conversation(
        "Chris",
        "I love playing Elden Ring on my PC",
        "That's awesome! Elden Ring is an amazing game. The open world is incredible."
    )
    print(f"Learned: {stats}")
    
    # Get statistics
    print("\n📊 Knowledge Graph Statistics:")
    stats = kg.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")

