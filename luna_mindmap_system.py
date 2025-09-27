#!/usr/bin/env python3
"""
Luna's Mind-Map System for Long-Term Memory Organization
Creates a knowledge graph to organize user profile information and memories
"""

import sqlite3
import json
import time
import re
from collections import defaultdict, deque
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import networkx as nx
from datetime import datetime, timedelta

@dataclass
class MemoryNode:
    """Represents a node in Luna's mind-map"""
    id: str
    content: str
    node_type: str  # 'user_profile', 'preference', 'event', 'relationship', 'skill', 'interest', 'memory'
    importance: int  # 1-5 scale
    created_at: str
    last_accessed: str
    tags: List[str]
    connections: List[str]  # IDs of connected nodes
    metadata: Dict[str, Any]

@dataclass
class MemoryConnection:
    """Represents a connection between memory nodes"""
    from_node: str
    to_node: str
    relationship_type: str  # 'related_to', 'caused_by', 'part_of', 'similar_to', 'opposite_of', 'temporal'
    strength: float  # 0.0-1.0
    created_at: str

class LunaMindMap:
    """Luna's mind-map system for organizing long-term memories"""
    
    def __init__(self, db_path: str = "luna_memories.db"):
        self.db_path = db_path
        self.graph = nx.DiGraph()  # Directed graph for relationships
        self.nodes: Dict[str, MemoryNode] = {}
        self.connections: Dict[str, MemoryConnection] = {}
        self.user_profile_nodes: Set[str] = set()
        self.last_update = 0
        
        # Node type categories
        self.node_categories = {
            'user_profile': ['name', 'age', 'location', 'occupation', 'personality'],
            'preference': ['likes', 'dislikes', 'favorites', 'habits', 'routines'],
            'event': ['meeting', 'conversation', 'achievement', 'milestone', 'experience'],
            'relationship': ['family', 'friend', 'colleague', 'acquaintance', 'romantic'],
            'skill': ['ability', 'talent', 'expertise', 'knowledge', 'capability'],
            'interest': ['hobby', 'passion', 'curiosity', 'topic', 'subject'],
            'memory': ['shared_memory', 'personal_story', 'experience', 'moment']
        }
        
        # Relationship types and their weights
        self.relationship_weights = {
            'related_to': 0.8,
            'caused_by': 0.9,
            'part_of': 0.7,
            'similar_to': 0.6,
            'opposite_of': 0.5,
            'temporal': 0.4,
            'influences': 0.8,
            'depends_on': 0.7
        }
        
        print("🧠 Luna's Mind-Map System initialized")
    
    def _extract_entities(self, text: str) -> List[Tuple[str, str]]:
        """Extract entities and their types from text"""
        entities = []
        
        # Simple entity extraction patterns
        patterns = {
            'name': r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # Proper names
            'location': r'\b(in|at|from|to|near)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
            'date': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}\b',
            'number': r'\b\d+\b',
            'emotion': r'\b(happy|sad|angry|excited|worried|nervous|confident|proud|disappointed|surprised)\b',
            'activity': r'\b(playing|working|studying|reading|watching|listening|cooking|traveling|exercising)\b'
        }
        
        for entity_type, pattern in patterns.items():
            matches = re.findall(pattern, text.lower())
            for match in matches:
                if isinstance(match, tuple):
                    entities.append((match[1] if len(match) > 1 else match[0], entity_type))
                else:
                    entities.append((match, entity_type))
        
        return entities
    
    def _calculate_node_importance(self, content: str, node_type: str, metadata: Dict) -> int:
        """Calculate importance score for a memory node"""
        importance = 1
        
        # Base importance by node type
        type_importance = {
            'user_profile': 5,
            'preference': 4,
            'event': 3,
            'relationship': 4,
            'skill': 3,
            'interest': 2,
            'memory': 2
        }
        importance = type_importance.get(node_type, 1)
        
        # Boost for emotional content
        emotional_words = ['love', 'hate', 'important', 'special', 'never', 'always', 'favorite', 'best', 'worst']
        if any(word in content.lower() for word in emotional_words):
            importance += 1
        
        # Boost for personal information
        personal_words = ['i', 'my', 'me', 'myself', 'personal', 'private']
        if any(word in content.lower() for word in personal_words):
            importance += 1
        
        # Boost for specific details
        if len(content.split()) > 20:  # Detailed content
            importance += 1
        
        return min(importance, 5)  # Cap at 5
    
    def _find_related_nodes(self, new_node: MemoryNode) -> List[Tuple[str, str, float]]:
        """Find nodes that should be connected to the new node"""
        related = []
        new_content_lower = new_node.content.lower()
        new_tags = set(new_node.tags)
        
        for node_id, existing_node in self.nodes.items():
            if node_id == new_node.id:
                continue
            
            # Check content similarity
            existing_content_lower = existing_node.content.lower()
            common_words = set(new_content_lower.split()) & set(existing_content_lower.split())
            
            # Check tag overlap
            common_tags = new_tags & set(existing_node.tags)
            
            # Calculate relationship strength
            strength = 0.0
            
            # Content similarity
            if len(common_words) > 0:
                strength += len(common_words) / max(len(new_content_lower.split()), len(existing_content_lower.split()))
            
            # Tag similarity
            if common_tags:
                strength += len(common_tags) / max(len(new_tags), len(existing_node.tags))
            
            # Same node type
            if new_node.node_type == existing_node.node_type:
                strength += 0.3
            
            # Temporal proximity (if both have timestamps)
            if 'timestamp' in new_node.metadata and 'timestamp' in existing_node.metadata:
                try:
                    new_time = datetime.fromisoformat(new_node.metadata['timestamp'])
                    existing_time = datetime.fromisoformat(existing_node.metadata['timestamp'])
                    time_diff = abs((new_time - existing_time).days)
                    if time_diff < 7:  # Within a week
                        strength += 0.2
                except:
                    pass
            
            if strength > 0.3:  # Threshold for creating connection
                relationship_type = self._determine_relationship_type(new_node, existing_node)
                related.append((node_id, relationship_type, strength))
        
        return related
    
    def _determine_relationship_type(self, node1: MemoryNode, node2: MemoryNode) -> str:
        """Determine the type of relationship between two nodes"""
        # Same type nodes
        if node1.node_type == node2.node_type:
            if node1.node_type == 'event':
                return 'temporal'
            elif node1.node_type == 'preference':
                return 'similar_to'
            else:
                return 'related_to'
        
        # Different types
        type_relationships = {
            ('user_profile', 'preference'): 'part_of',
            ('user_profile', 'skill'): 'part_of',
            ('user_profile', 'interest'): 'part_of',
            ('event', 'memory'): 'caused_by',
            ('preference', 'event'): 'influences',
            ('skill', 'interest'): 'related_to'
        }
        
        key = tuple(sorted([node1.node_type, node2.node_type]))
        return type_relationships.get(key, 'related_to')
    
    def add_memory_node(self, content: str, node_type: str, metadata: Dict = None, tags: List[str] = None) -> str:
        """Add a new memory node to the mind-map"""
        if metadata is None:
            metadata = {}
        if tags is None:
            tags = []
        
        # Generate unique ID
        node_id = f"{node_type}_{int(time.time() * 1000)}"
        
        # Extract additional tags from content
        entities = self._extract_entities(content)
        for entity, entity_type in entities:
            if entity_type not in tags:
                tags.append(entity_type)
        
        # Calculate importance
        importance = self._calculate_node_importance(content, node_type, metadata)
        
        # Create memory node
        memory_node = MemoryNode(
            id=node_id,
            content=content,
            node_type=node_type,
            importance=importance,
            created_at=datetime.now().isoformat(),
            last_accessed=datetime.now().isoformat(),
            tags=tags,
            connections=[],
            metadata=metadata
        )
        
        # Add to graph and storage
        self.nodes[node_id] = memory_node
        self.graph.add_node(node_id, **asdict(memory_node))
        
        # Find and create connections
        related_nodes = self._find_related_nodes(memory_node)
        for related_id, relationship_type, strength in related_nodes:
            self.create_connection(node_id, related_id, relationship_type, strength)
        
        # Update user profile nodes if applicable
        if node_type == 'user_profile':
            self.user_profile_nodes.add(node_id)
        
        print(f"🧠 Added memory node: {node_type} - {content[:50]}...")
        return node_id
    
    def create_connection(self, from_node: str, to_node: str, relationship_type: str, strength: float = 0.5):
        """Create a connection between two memory nodes"""
        if from_node not in self.nodes or to_node not in self.nodes:
            return
        
        connection_id = f"{from_node}_{to_node}_{relationship_type}"
        
        connection = MemoryConnection(
            from_node=from_node,
            to_node=to_node,
            relationship_type=relationship_type,
            strength=strength,
            created_at=datetime.now().isoformat()
        )
        
        self.connections[connection_id] = connection
        self.graph.add_edge(from_node, to_node, 
                          relationship_type=relationship_type, 
                          strength=strength)
        
        # Update node connections
        if to_node not in self.nodes[from_node].connections:
            self.nodes[from_node].connections.append(to_node)
        if from_node not in self.nodes[to_node].connections:
            self.nodes[to_node].connections.append(from_node)
    
    def search_mindmap(self, query: str, limit: int = 10) -> List[Dict]:
        """Search the mind-map for relevant nodes"""
        query_lower = query.lower()
        results = []
        
        for node_id, node in self.nodes.items():
            score = 0.0
            
            # Content match
            if query_lower in node.content.lower():
                score += 1.0
            
            # Tag match
            for tag in node.tags:
                if query_lower in tag.lower():
                    score += 0.5
            
            # Type match
            if query_lower in node.node_type.lower():
                score += 0.3
            
            # Importance boost
            score += node.importance * 0.1
            
            if score > 0:
                results.append({
                    'node_id': node_id,
                    'node': node,
                    'score': score,
                    'content': node.content,
                    'type': node.node_type,
                    'importance': node.importance,
                    'tags': node.tags
                })
        
        # Sort by score and return top results
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:limit]
    
    def get_user_profile_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of the user's profile"""
        profile_summary = {
            'basic_info': {},
            'preferences': [],
            'interests': [],
            'skills': [],
            'relationships': [],
            'recent_events': [],
            'important_memories': []
        }
        
        for node_id in self.user_profile_nodes:
            node = self.nodes[node_id]
            if node.node_type == 'user_profile':
                profile_summary['basic_info'][node_id] = node.content
            elif node.node_type == 'preference':
                profile_summary['preferences'].append(node.content)
            elif node.node_type == 'interest':
                profile_summary['interests'].append(node.content)
            elif node.node_type == 'skill':
                profile_summary['skills'].append(node.content)
            elif node.node_type == 'relationship':
                profile_summary['relationships'].append(node.content)
            elif node.node_type == 'event':
                profile_summary['recent_events'].append(node.content)
            elif node.node_type == 'memory' and node.importance >= 4:
                profile_summary['important_memories'].append(node.content)
        
        return profile_summary
    
    def get_related_memories(self, node_id: str, depth: int = 2) -> List[MemoryNode]:
        """Get memories related to a specific node through graph traversal"""
        if node_id not in self.nodes:
            return []
        
        visited = set()
        related = []
        queue = deque([(node_id, 0)])  # (node_id, depth)
        
        while queue:
            current_id, current_depth = queue.popleft()
            
            if current_id in visited or current_depth > depth:
                continue
            
            visited.add(current_id)
            if current_id != node_id:  # Don't include the starting node
                related.append(self.nodes[current_id])
            
            # Add connected nodes to queue
            for neighbor in self.graph.neighbors(current_id):
                if neighbor not in visited:
                    queue.append((neighbor, current_depth + 1))
        
        return related
    
    def save_to_database(self):
        """Save the mind-map to the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create mind-map tables if they don't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mindmap_nodes (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    node_type TEXT NOT NULL,
                    importance INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    last_accessed TEXT NOT NULL,
                    tags TEXT NOT NULL,
                    connections TEXT NOT NULL,
                    metadata TEXT NOT NULL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mindmap_connections (
                    id TEXT PRIMARY KEY,
                    from_node TEXT NOT NULL,
                    to_node TEXT NOT NULL,
                    relationship_type TEXT NOT NULL,
                    strength REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (from_node) REFERENCES mindmap_nodes (id),
                    FOREIGN KEY (to_node) REFERENCES mindmap_nodes (id)
                )
            ''')
            
            # Clear existing data
            cursor.execute('DELETE FROM mindmap_connections')
            cursor.execute('DELETE FROM mindmap_nodes')
            
            # Insert nodes
            for node in self.nodes.values():
                cursor.execute('''
                    INSERT INTO mindmap_nodes 
                    (id, content, node_type, importance, created_at, last_accessed, tags, connections, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    node.id, node.content, node.node_type, node.importance,
                    node.created_at, node.last_accessed, json.dumps(node.tags),
                    json.dumps(node.connections), json.dumps(node.metadata)
                ))
            
            # Insert connections
            for conn_id, conn in self.connections.items():
                cursor.execute('''
                    INSERT INTO mindmap_connections 
                    (id, from_node, to_node, relationship_type, strength, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    conn_id,
                    conn.from_node, conn.to_node, conn.relationship_type,
                    conn.strength, conn.created_at
                ))
            
            conn.commit()
            conn.close()
            
            self.last_update = time.time()
            print(f"💾 Mind-map saved to database: {len(self.nodes)} nodes, {len(self.connections)} connections")
            
        except Exception as e:
            print(f"❌ Error saving mind-map: {e}")
    
    def load_from_database(self):
        """Load the mind-map from the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='mindmap_nodes'")
            if not cursor.fetchone():
                print("⚠️ Mind-map tables don't exist yet")
                return
            
            # Load nodes
            cursor.execute('SELECT * FROM mindmap_nodes')
            nodes_data = cursor.fetchall()
            
            for row in nodes_data:
                node = MemoryNode(
                    id=row[0],
                    content=row[1],
                    node_type=row[2],
                    importance=row[3],
                    created_at=row[4],
                    last_accessed=row[5],
                    tags=json.loads(row[6]),
                    connections=json.loads(row[7]),
                    metadata=json.loads(row[8])
                )
                self.nodes[node.id] = node
                self.graph.add_node(node.id, **asdict(node))
                
                if node.node_type == 'user_profile':
                    self.user_profile_nodes.add(node.id)
            
            # Load connections
            cursor.execute('SELECT * FROM mindmap_connections')
            connections_data = cursor.fetchall()
            
            for row in connections_data:
                connection = MemoryConnection(
                    from_node=row[1],
                    to_node=row[2],
                    relationship_type=row[3],
                    strength=row[4],
                    created_at=row[5]
                )
                self.connections[row[0]] = connection
                self.graph.add_edge(connection.from_node, connection.to_node,
                                  relationship_type=connection.relationship_type,
                                  strength=connection.strength)
            
            conn.close()
            
            print(f"📂 Mind-map loaded from database: {len(self.nodes)} nodes, {len(self.connections)} connections")
            
        except Exception as e:
            print(f"❌ Error loading mind-map: {e}")
    
    def get_mindmap_stats(self) -> Dict[str, Any]:
        """Get statistics about the mind-map"""
        return {
            'total_nodes': len(self.nodes),
            'total_connections': len(self.connections),
            'node_types': {node_type: len([n for n in self.nodes.values() if n.node_type == node_type]) 
                          for node_type in self.node_categories.keys()},
            'user_profile_nodes': len(self.user_profile_nodes),
            'graph_density': nx.density(self.graph) if len(self.graph) > 0 else 0,
            'last_update': self.last_update
        }

# Global mind-map instance
luna_mindmap = None

def initialize_mindmap_system(db_path: str = "luna_memories.db") -> LunaMindMap:
    """Initialize the global mind-map system"""
    global luna_mindmap
    luna_mindmap = LunaMindMap(db_path)
    luna_mindmap.load_from_database()
    return luna_mindmap

def get_mindmap_system() -> Optional[LunaMindMap]:
    """Get the global mind-map system instance"""
    return luna_mindmap

def add_user_memory(content: str, memory_type: str, metadata: Dict = None, tags: List[str] = None) -> str:
    """Add a user-related memory to the mind-map"""
    if luna_mindmap is None:
        initialize_mindmap_system()
    
    return luna_mindmap.add_memory_node(content, memory_type, metadata, tags)

def search_user_profile(query: str, limit: int = 5) -> List[Dict]:
    """Search the user's profile in the mind-map"""
    if luna_mindmap is None:
        initialize_mindmap_system()
    
    return luna_mindmap.search_mindmap(query, limit)

def get_user_profile_summary() -> Dict[str, Any]:
    """Get a comprehensive summary of the user's profile"""
    if luna_mindmap is None:
        initialize_mindmap_system()
    
    return luna_mindmap.get_user_profile_summary()

if __name__ == "__main__":
    # Test the mind-map system
    print("🧠 Testing Luna's Mind-Map System")
    print("=" * 50)
    
    # Initialize system
    mindmap = initialize_mindmap_system()
    
    # Add some test memories
    test_memories = [
        ("Chris loves gaming, especially RPGs and strategy games", "preference", {"category": "gaming"}, ["gaming", "rpg", "strategy"]),
        ("Chris is a software developer who works from home", "user_profile", {"category": "occupation"}, ["work", "developer", "remote"]),
        ("Chris mentioned he's learning Python programming", "skill", {"category": "programming"}, ["python", "learning", "programming"]),
        ("Chris has a cat named Luna", "relationship", {"category": "pet"}, ["cat", "pet", "luna"]),
        ("Chris prefers coffee over tea in the morning", "preference", {"category": "beverage"}, ["coffee", "morning", "beverage"]),
        ("Chris mentioned he's planning a vacation to Japan", "event", {"category": "travel"}, ["vacation", "japan", "travel"])
    ]
    
    print("Adding test memories...")
    for content, memory_type, metadata, tags in test_memories:
        mindmap.add_memory_node(content, memory_type, metadata, tags)
    
    # Save to database
    mindmap.save_to_database()
    
    # Test search
    print("\n🔍 Testing search functionality...")
    search_queries = ["gaming", "work", "cat", "coffee", "vacation"]
    
    for query in search_queries:
        results = mindmap.search_mindmap(query, limit=3)
        print(f"\nQuery: '{query}'")
        for result in results:
            print(f"  - {result['type']}: {result['content']} (score: {result['score']:.2f})")
    
    # Get user profile summary
    print("\n👤 User Profile Summary:")
    summary = mindmap.get_user_profile_summary()
    for category, items in summary.items():
        if items:
            print(f"\n{category.replace('_', ' ').title()}:")
            for item in items[:3]:  # Show first 3 items
                print(f"  - {item}")
    
    # Show stats
    stats = mindmap.get_mindmap_stats()
    print(f"\n📊 Mind-Map Statistics:")
    print(f"  Total nodes: {stats['total_nodes']}")
    print(f"  Total connections: {stats['total_connections']}")
    print(f"  Graph density: {stats['graph_density']:.3f}")
    print(f"  Node types: {stats['node_types']}")
    
    print("\n✅ Mind-map system test completed!")
