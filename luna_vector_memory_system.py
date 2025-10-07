#!/usr/bin/env python3
"""
Luna's Vector-Based Memory System
Inspired by vector graphics mathematics to create geometric memory representations

Concept: Memories are represented as vector shapes with:
- Palette: Emotional/contextual color coding
- Layers: Different memory types (episodic, semantic, procedural)
- Vectorization: Geometric relationships between memories
- Flattening: Compression and optimization of memory structures

Credits: Inspired by vector_image.py system for geometric memory representation
"""

import os
import time
import json
import sqlite3
import numpy as np
import torch
from PIL import Image
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import math
import hashlib

# Set seeds for reproducible vector generation
torch.manual_seed(209)
np.random.seed(209)

@dataclass
class VectorMemory:
    """Represents a memory as a vector shape with geometric properties"""
    id: str
    content: str
    memory_type: str  # 'episodic', 'semantic', 'procedural', 'emotional'
    
    # Vector properties
    position: Tuple[float, float]  # 2D position in memory space
    shape: str  # 'circle', 'triangle', 'square', 'polygon'
    vertices: List[Tuple[float, float]]  # Vector vertices defining the shape
    color: Tuple[float, float, float]  # RGB color representing emotion/context
    opacity: float  # Importance/relevance (0.0-1.0)
    size: float  # Memory strength/significance
    
    # Temporal properties
    created_at: str
    last_accessed: str
    access_count: int
    
    # Relationships
    connections: List[str]  # IDs of connected memories
    layer_depth: int  # Depth in memory hierarchy
    
    # Metadata
    tags: List[str]
    metadata: Dict[str, Any]

@dataclass
class MemoryPalette:
    """Color palette for memory types and emotions"""
    colors: Dict[str, Tuple[float, float, float]]
    emotions: Dict[str, Tuple[float, float, float]]
    contexts: Dict[str, Tuple[float, float, float]]

class VectorMemoryGenerator:
    """Generates vector representations for memories using geometric algorithms"""
    
    def __init__(self):
        self.palette = self._create_memory_palette()
        self.shape_templates = self._create_shape_templates()
        
    def _create_memory_palette(self) -> MemoryPalette:
        """Create color palette for different memory types and emotions"""
        return MemoryPalette(
            colors={
                'episodic': (0.8, 0.2, 0.2),    # Red - personal experiences
                'semantic': (0.2, 0.8, 0.2),    # Green - facts and knowledge
                'procedural': (0.2, 0.2, 0.8),  # Blue - skills and procedures
                'emotional': (0.8, 0.8, 0.2),   # Yellow - emotional memories
                'social': (0.8, 0.2, 0.8),      # Magenta - social interactions
                'creative': (0.2, 0.8, 0.8),    # Cyan - creative thoughts
            },
            emotions={
                'happy': (1.0, 0.8, 0.0),       # Bright yellow
                'sad': (0.3, 0.3, 0.8),         # Deep blue
                'excited': (1.0, 0.4, 0.0),     # Orange
                'calm': (0.4, 0.8, 0.6),        # Teal
                'angry': (0.8, 0.2, 0.2),       # Red
                'curious': (0.6, 0.4, 1.0),     # Purple
                'nostalgic': (0.8, 0.6, 0.4),   # Warm brown
            },
            contexts={
                'gaming': (0.4, 0.8, 0.4),      # Green
                'streaming': (0.8, 0.4, 0.8),   # Pink
                'learning': (0.4, 0.4, 0.8),    # Blue
                'personal': (0.8, 0.6, 0.2),    # Gold
                'work': (0.6, 0.6, 0.6),        # Gray
                'social': (0.8, 0.2, 0.8),      # Magenta
            }
        )
    
    def _create_shape_templates(self) -> Dict[str, List[Tuple[float, float]]]:
        """Create geometric shape templates for different memory types"""
        return {
            'circle': [(0.0, 0.0)],  # Center point for circles
            'triangle': [(0.0, 0.5), (-0.433, -0.25), (0.433, -0.25)],
            'square': [(0.0, 0.0), (0.5, 0.0), (0.5, 0.5), (0.0, 0.5)],
            'pentagon': [(0.0, 0.5), (-0.476, 0.154), (-0.294, -0.405), (0.294, -0.405), (0.476, 0.154)],
            'hexagon': [(0.0, 0.5), (-0.433, 0.25), (-0.433, -0.25), (0.0, -0.5), (0.433, -0.25), (0.433, 0.25)],
        }
    
    def generate_memory_vector(self, memory_id: str, content: str, memory_type: str, 
                             emotion: str = 'neutral', context: str = 'general',
                             importance: float = 0.5) -> VectorMemory:
        """Generate vector representation for a memory"""
        
        # Determine position based on content hash (for consistency)
        content_hash = hashlib.md5(content.encode()).hexdigest()
        x_pos = (int(content_hash[:8], 16) / 0xffffffff) * 2 - 1  # -1 to 1
        y_pos = (int(content_hash[8:16], 16) / 0xffffffff) * 2 - 1  # -1 to 1
        
        # Choose shape based on memory type
        shape_map = {
            'episodic': 'circle',
            'semantic': 'square', 
            'procedural': 'triangle',
            'emotional': 'pentagon',
            'social': 'hexagon',
            'creative': 'triangle'
        }
        shape = shape_map.get(memory_type, 'circle')
        
        # Get base vertices and scale by importance
        base_vertices = self.shape_templates[shape].copy()
        scale_factor = 0.1 + (importance * 0.4)  # Scale between 0.1 and 0.5
        vertices = [(x * scale_factor + x_pos, y * scale_factor + y_pos) 
                   for x, y in base_vertices]
        
        # Determine color based on type, emotion, and context
        base_color = self.palette.colors.get(memory_type, (0.5, 0.5, 0.5))
        emotion_color = self.palette.emotions.get(emotion, (0.5, 0.5, 0.5))
        context_color = self.palette.contexts.get(context, (0.5, 0.5, 0.5))
        
        # Blend colors (weighted average)
        final_color = (
            (base_color[0] + emotion_color[0] + context_color[0]) / 3,
            (base_color[1] + emotion_color[1] + context_color[1]) / 3,
            (base_color[2] + emotion_color[2] + context_color[2]) / 3
        )
        
        return VectorMemory(
            id=memory_id,
            content=content,
            memory_type=memory_type,
            position=(x_pos, y_pos),
            shape=shape,
            vertices=vertices,
            color=final_color,
            opacity=importance,
            size=scale_factor,
            created_at=datetime.now().isoformat(),
            last_accessed=datetime.now().isoformat(),
            access_count=1,
            connections=[],
            layer_depth=0,
            tags=[],
            metadata={}
        )

class MemoryLayerGenerator:
    """Generates layered memory structures similar to vector graphics layering"""
    
    def __init__(self, vector_generator: VectorMemoryGenerator):
        self.vector_generator = vector_generator
        self.layers = {
            'background': [],    # Core personality and preferences
            'semantic': [],      # Facts and knowledge
            'episodic': [],      # Personal experiences
            'procedural': [],    # Skills and habits
            'emotional': [],     # Emotional memories
            'social': [],        # Social interactions
            'creative': [],      # Creative thoughts and ideas
            'foreground': []     # Recent and highly relevant memories
        }
    
    def add_memory_to_layer(self, memory: VectorMemory, layer_name: str = None):
        """Add memory to appropriate layer"""
        if layer_name is None:
            layer_name = memory.memory_type
        
        if layer_name in self.layers:
            # Set layer depth based on layer type
            depth_map = {
                'background': 0,
                'semantic': 1,
                'episodic': 2,
                'procedural': 2,
                'emotional': 3,
                'social': 3,
                'creative': 4,
                'foreground': 5
            }
            memory.layer_depth = depth_map.get(layer_name, 2)
            self.layers[layer_name].append(memory)
        else:
            # Default to semantic layer
            memory.layer_depth = 1
            self.layers['semantic'].append(memory)
    
    def find_related_memories(self, memory: VectorMemory, radius: float = 0.3) -> List[VectorMemory]:
        """Find memories within geometric radius of given memory"""
        related = []
        memory_pos = memory.position
        
        for layer_memories in self.layers.values():
            for other_memory in layer_memories:
                if other_memory.id == memory.id:
                    continue
                
                other_pos = other_memory.position
                distance = math.sqrt((memory_pos[0] - other_pos[0])**2 + 
                                   (memory_pos[1] - other_pos[1])**2)
                
                if distance <= radius:
                    related.append(other_memory)
        
        return related
    
    def calculate_memory_clusters(self) -> List[List[VectorMemory]]:
        """Calculate clusters of related memories using geometric proximity"""
        clusters = []
        processed = set()
        
        for layer_memories in self.layers.values():
            for memory in layer_memories:
                if memory.id in processed:
                    continue
                
                cluster = [memory]
                processed.add(memory.id)
                
                # Find all memories within cluster radius
                to_check = [memory]
                while to_check:
                    current = to_check.pop(0)
                    related = self.find_related_memories(current, radius=0.2)
                    
                    for related_memory in related:
                        if related_memory.id not in processed:
                            cluster.append(related_memory)
                            processed.add(related_memory.id)
                            to_check.append(related_memory)
                
                if len(cluster) > 1:  # Only keep clusters with multiple memories
                    clusters.append(cluster)
        
        return clusters

class MemoryVectorizer:
    """Vectorizes memory relationships and generates geometric connections"""
    
    def __init__(self):
        self.connection_types = {
            'temporal': {'color': (0.8, 0.8, 0.8), 'weight': 0.3},      # Gray - time-based
            'semantic': {'color': (0.2, 0.8, 0.2), 'weight': 0.5},      # Green - meaning-based
            'emotional': {'color': (0.8, 0.8, 0.2), 'weight': 0.6},     # Yellow - emotion-based
            'causal': {'color': (0.8, 0.2, 0.2), 'weight': 0.7},        # Red - cause-effect
            'spatial': {'color': (0.2, 0.2, 0.8), 'weight': 0.4},       # Blue - location-based
            'social': {'color': (0.8, 0.2, 0.8), 'weight': 0.5},        # Magenta - social
        }
    
    def vectorize_memory_connections(self, memory1: VectorMemory, memory2: VectorMemory,
                                   connection_type: str = 'semantic') -> Dict[str, Any]:
        """Create vector connection between two memories"""
        
        # Calculate connection vector
        pos1, pos2 = memory1.position, memory2.position
        connection_vector = (pos2[0] - pos1[0], pos2[1] - pos1[1])
        
        # Calculate connection strength based on various factors
        distance = math.sqrt(connection_vector[0]**2 + connection_vector[1]**2)
        time_diff = self._calculate_time_difference(memory1.created_at, memory2.created_at)
        semantic_similarity = self._calculate_semantic_similarity(memory1.content, memory2.content)
        
        # Connection strength (0.0 to 1.0)
        strength = self._calculate_connection_strength(
            distance, time_diff, semantic_similarity, connection_type
        )
        
        # Get connection properties
        conn_props = self.connection_types.get(connection_type, self.connection_types['semantic'])
        
        return {
            'from_memory': memory1.id,
            'to_memory': memory2.id,
            'connection_type': connection_type,
            'vector': connection_vector,
            'strength': strength,
            'color': conn_props['color'],
            'weight': conn_props['weight'] * strength,
            'distance': distance,
            'created_at': datetime.now().isoformat()
        }
    
    def _calculate_time_difference(self, time1: str, time2: str) -> float:
        """Calculate normalized time difference between memories"""
        try:
            dt1 = datetime.fromisoformat(time1)
            dt2 = datetime.fromisoformat(time2)
            diff_days = abs((dt2 - dt1).days)
            # Normalize to 0-1 scale (1 year = 1.0)
            return min(1.0, diff_days / 365.0)
        except:
            return 0.5  # Default neutral value
    
    def _calculate_semantic_similarity(self, content1: str, content2: str) -> float:
        """Calculate semantic similarity between memory contents"""
        # Simple word overlap similarity
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _calculate_connection_strength(self, distance: float, time_diff: float,
                                     semantic_similarity: float, connection_type: str) -> float:
        """Calculate overall connection strength"""
        
        # Distance factor (closer = stronger)
        distance_factor = max(0.0, 1.0 - distance / 2.0)  # Normalize distance
        
        # Time factor (recent = stronger, but not too strong)
        time_factor = max(0.0, 1.0 - time_diff)
        
        # Semantic similarity factor
        semantic_factor = semantic_similarity
        
        # Type-specific weights
        type_weights = {
            'temporal': {'distance': 0.2, 'time': 0.7, 'semantic': 0.1},
            'semantic': {'distance': 0.3, 'time': 0.2, 'semantic': 0.5},
            'emotional': {'distance': 0.4, 'time': 0.3, 'semantic': 0.3},
            'causal': {'distance': 0.2, 'time': 0.4, 'semantic': 0.4},
            'spatial': {'distance': 0.6, 'time': 0.2, 'semantic': 0.2},
            'social': {'distance': 0.3, 'time': 0.3, 'semantic': 0.4},
        }
        
        weights = type_weights.get(connection_type, type_weights['semantic'])
        
        strength = (weights['distance'] * distance_factor + 
                   weights['time'] * time_factor + 
                   weights['semantic'] * semantic_factor)
        
        return max(0.0, min(1.0, strength))

class LunaVectorMemorySystem:
    """Main vector-based memory system for Luna"""
    
    def __init__(self, db_path: str = "luna_vector_memories.db"):
        self.db_path = db_path
        self.vector_generator = VectorMemoryGenerator()
        self.layer_generator = MemoryLayerGenerator(self.vector_generator)
        self.vectorizer = MemoryVectorizer()
        self.memories: Dict[str, VectorMemory] = {}
        self.connections: List[Dict[str, Any]] = []
        
        self._init_database()
        self._load_existing_memories()
    
    def _init_database(self):
        """Initialize database for vector memories"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS vector_memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    position_x REAL NOT NULL,
                    position_y REAL NOT NULL,
                    shape TEXT NOT NULL,
                    vertices TEXT NOT NULL,
                    color_r REAL NOT NULL,
                    color_g REAL NOT NULL,
                    color_b REAL NOT NULL,
                    opacity REAL NOT NULL,
                    size REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    last_accessed TEXT NOT NULL,
                    access_count INTEGER NOT NULL,
                    layer_depth INTEGER NOT NULL,
                    tags TEXT NOT NULL,
                    metadata TEXT NOT NULL
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS memory_connections (
                    id TEXT PRIMARY KEY,
                    from_memory TEXT NOT NULL,
                    to_memory TEXT NOT NULL,
                    connection_type TEXT NOT NULL,
                    vector_x REAL NOT NULL,
                    vector_y REAL NOT NULL,
                    strength REAL NOT NULL,
                    color_r REAL NOT NULL,
                    color_g REAL NOT NULL,
                    color_b REAL NOT NULL,
                    weight REAL NOT NULL,
                    distance REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (from_memory) REFERENCES vector_memories (id),
                    FOREIGN KEY (to_memory) REFERENCES vector_memories (id)
                )
            ''')
            
            conn.commit()
    
    def _load_existing_memories(self):
        """Load existing vector memories from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT * FROM vector_memories')
            for row in cursor.fetchall():
                memory = VectorMemory(
                    id=row[0],
                    content=row[1],
                    memory_type=row[2],
                    position=(row[3], row[4]),
                    shape=row[5],
                    vertices=json.loads(row[6]),
                    color=(row[7], row[8], row[9]),
                    opacity=row[10],
                    size=row[11],
                    created_at=row[12],
                    last_accessed=row[13],
                    access_count=row[14],
                    connections=[],
                    layer_depth=row[15],
                    tags=json.loads(row[16]),
                    metadata=json.loads(row[17])
                )
                self.memories[memory.id] = memory
                self.layer_generator.add_memory_to_layer(memory)
    
    def add_memory(self, content: str, memory_type: str, emotion: str = 'neutral',
                  context: str = 'general', importance: float = 0.5,
                  tags: List[str] = None) -> str:
        """Add a new memory with vector representation"""
        
        memory_id = f"vm_{int(time.time() * 1000)}_{hashlib.md5(content.encode()).hexdigest()[:8]}"
        
        # Generate vector representation
        vector_memory = self.vector_generator.generate_memory_vector(
            memory_id, content, memory_type, emotion, context, importance
        )
        
        if tags:
            vector_memory.tags = tags
        
        # Store in memory
        self.memories[memory_id] = vector_memory
        self.layer_generator.add_memory_to_layer(vector_memory)
        
        # Save to database
        self._save_memory_to_db(vector_memory)
        
        # Find and create connections with related memories
        self._create_memory_connections(vector_memory)
        
        print(f"🧠 Vector memory added: {memory_id[:12]}... ({memory_type}, {emotion})")
        return memory_id
    
    def _save_memory_to_db(self, memory: VectorMemory):
        """Save vector memory to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO vector_memories VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                memory.id, memory.content, memory.memory_type,
                memory.position[0], memory.position[1], memory.shape,
                json.dumps(memory.vertices), memory.color[0], memory.color[1], memory.color[2],
                memory.opacity, memory.size, memory.created_at, memory.last_accessed,
                memory.access_count, memory.layer_depth,
                json.dumps(memory.tags), json.dumps(memory.metadata)
            ))
            conn.commit()
    
    def _create_memory_connections(self, new_memory: VectorMemory):
        """Create connections between new memory and existing memories"""
        related_memories = self.layer_generator.find_related_memories(new_memory, radius=0.4)
        
        for related_memory in related_memories:
            # Determine connection type based on memory types and content
            connection_type = self._determine_connection_type(new_memory, related_memory)
            
            connection = self.vectorizer.vectorize_memory_connections(
                new_memory, related_memory, connection_type
            )
            
            # Only keep strong connections
            if connection['strength'] > 0.3:
                connection_id = f"conn_{new_memory.id}_{related_memory.id}_{connection_type}"
                connection['id'] = connection_id
                self.connections.append(connection)
                self._save_connection_to_db(connection)
                
                # Update memory connections
                new_memory.connections.append(related_memory.id)
                related_memory.connections.append(new_memory.id)
    
    def _determine_connection_type(self, memory1: VectorMemory, memory2: VectorMemory) -> str:
        """Determine the type of connection between two memories"""
        
        # Same type memories
        if memory1.memory_type == memory2.memory_type:
            if memory1.memory_type == 'emotional':
                return 'emotional'
            elif memory1.memory_type == 'social':
                return 'social'
            else:
                return 'semantic'
        
        # Cross-type connections
        if 'emotional' in [memory1.memory_type, memory2.memory_type]:
            return 'emotional'
        elif 'social' in [memory1.memory_type, memory2.memory_type]:
            return 'social'
        else:
            return 'semantic'
    
    def _save_connection_to_db(self, connection: Dict[str, Any]):
        """Save memory connection to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO memory_connections VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                connection['id'], connection['from_memory'], connection['to_memory'],
                connection['connection_type'], connection['vector'][0], connection['vector'][1],
                connection['strength'], connection['color'][0], connection['color'][1], 
                connection['color'][2], connection['weight'], connection['distance'],
                connection['created_at']
            ))
            conn.commit()
    
    def search_memories_by_vector(self, query: str, memory_type: str = None,
                                emotion: str = None, context: str = None,
                                limit: int = 10) -> List[Tuple[VectorMemory, float]]:
        """Search memories using vector similarity"""
        
        # Generate query vector
        query_memory = self.vector_generator.generate_memory_vector(
            "query", query, memory_type or 'semantic', emotion or 'neutral', 
            context or 'general', 0.5
        )
        
        results = []
        
        for memory in self.memories.values():
            # Filter by type if specified
            if memory_type and memory.memory_type != memory_type:
                continue
            
            # Calculate vector similarity
            similarity = self._calculate_vector_similarity(query_memory, memory)
            
            # Apply emotion and context filters
            if emotion and not self._matches_emotion(memory, emotion):
                similarity *= 0.7  # Reduce similarity
            
            if context and not self._matches_context(memory, context):
                similarity *= 0.8  # Reduce similarity
            
            # Boost recent memories
            recency_boost = self._calculate_recency_boost(memory.last_accessed)
            final_score = similarity * (1.0 + recency_boost)
            
            results.append((memory, final_score))
        
        # Sort by score and return top results
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]
    
    def _calculate_vector_similarity(self, memory1: VectorMemory, memory2: VectorMemory) -> float:
        """Calculate similarity between two vector memories"""
        
        # Position similarity (closer = more similar)
        pos1, pos2 = memory1.position, memory2.position
        position_similarity = 1.0 - math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2) / 2.0
        
        # Color similarity (similar colors = similar context/emotion)
        color1, color2 = memory1.color, memory2.color
        color_similarity = 1.0 - math.sqrt((color1[0] - color2[0])**2 + 
                                         (color1[1] - color2[1])**2 + 
                                         (color1[2] - color2[2])**2) / math.sqrt(3)
        
        # Shape similarity (same shape = same type)
        shape_similarity = 1.0 if memory1.shape == memory2.shape else 0.5
        
        # Size similarity (similar importance)
        size_similarity = 1.0 - abs(memory1.size - memory2.size)
        
        # Weighted combination
        similarity = (0.3 * position_similarity + 
                     0.3 * color_similarity + 
                     0.2 * shape_similarity + 
                     0.2 * size_similarity)
        
        return max(0.0, min(1.0, similarity))
    
    def _matches_emotion(self, memory: VectorMemory, emotion: str) -> bool:
        """Check if memory matches given emotion based on color"""
        emotion_colors = self.vector_generator.palette.emotions
        target_color = emotion_colors.get(emotion, (0.5, 0.5, 0.5))
        
        color_diff = math.sqrt(sum((a - b)**2 for a, b in zip(memory.color, target_color)))
        return color_diff < 0.3  # Threshold for emotion matching
    
    def _matches_context(self, memory: VectorMemory, context: str) -> bool:
        """Check if memory matches given context"""
        context_colors = self.vector_generator.palette.contexts
        target_color = context_colors.get(context, (0.5, 0.5, 0.5))
        
        color_diff = math.sqrt(sum((a - b)**2 for a, b in zip(memory.color, target_color)))
        return color_diff < 0.4  # Threshold for context matching
    
    def _calculate_recency_boost(self, last_accessed: str) -> float:
        """Calculate recency boost for memory relevance"""
        try:
            last_access = datetime.fromisoformat(last_accessed)
            days_ago = (datetime.now() - last_access).days
            return max(0.0, 0.2 * (1.0 - days_ago / 30.0))  # 20% boost for recent memories
        except:
            return 0.0
    
    def get_memory_clusters(self) -> List[List[VectorMemory]]:
        """Get clusters of related memories"""
        return self.layer_generator.calculate_memory_clusters()
    
    def visualize_memory_space(self, output_path: str = "luna_memory_visualization.png",
                             width: int = 1024, height: int = 1024):
        """Create visual representation of memory space"""
        
        # Create image
        img = np.ones((height, width, 3), dtype=np.uint8) * 255  # White background
        
        # Draw connections first (so they appear behind memories)
        for connection in self.connections:
            if connection['strength'] > 0.3:  # Only draw strong connections
                self._draw_connection(img, connection, width, height)
        
        # Draw memories
        for memory in self.memories.values():
            self._draw_memory(img, memory, width, height)
        
        # Save image
        Image.fromarray(img).save(output_path)
        print(f"🎨 Memory visualization saved to: {output_path}")
    
    def _draw_connection(self, img: np.ndarray, connection: Dict[str, Any], 
                        width: int, height: int):
        """Draw connection between memories"""
        from_memory = self.memories.get(connection['from_memory'])
        to_memory = self.memories.get(connection['to_memory'])
        
        if not from_memory or not to_memory:
            return
        
        # Convert positions to image coordinates
        x1 = int((from_memory.position[0] + 1) * width / 2)
        y1 = int((from_memory.position[1] + 1) * height / 2)
        x2 = int((to_memory.position[0] + 1) * width / 2)
        y2 = int((to_memory.position[1] + 1) * height / 2)
        
        # Draw line
        color = tuple(int(c * 255) for c in connection['color'])
        thickness = max(1, int(connection['weight'] * 3))
        
        # Simple line drawing (you might want to use cv2.line for better results)
        self._draw_line(img, x1, y1, x2, y2, color, thickness)
    
    def _draw_line(self, img: np.ndarray, x1: int, y1: int, x2: int, y2: int, 
                   color: Tuple[int, int, int], thickness: int):
        """Simple line drawing function"""
        # Bresenham's line algorithm (simplified)
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        x, y = x1, y1
        
        while True:
            # Draw pixel with thickness
            for i in range(-thickness//2, thickness//2 + 1):
                for j in range(-thickness//2, thickness//2 + 1):
                    if 0 <= x + i < img.shape[1] and 0 <= y + j < img.shape[0]:
                        img[y + j, x + i] = color
            
            if x == x2 and y == y2:
                break
            
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
    
    def _draw_memory(self, img: np.ndarray, memory: VectorMemory, width: int, height: int):
        """Draw memory as vector shape"""
        # Convert position to image coordinates
        center_x = int((memory.position[0] + 1) * width / 2)
        center_y = int((memory.position[1] + 1) * height / 2)
        
        # Convert color
        color = tuple(int(c * 255) for c in memory.color)
        
        # Calculate size
        size = int(memory.size * 50)  # Scale size for visualization
        
        # Draw shape based on type
        if memory.shape == 'circle':
            self._draw_circle(img, center_x, center_y, size, color, memory.opacity)
        elif memory.shape == 'triangle':
            self._draw_triangle(img, center_x, center_y, size, color, memory.opacity)
        elif memory.shape == 'square':
            self._draw_square(img, center_x, center_y, size, color, memory.opacity)
        else:
            # Default to circle
            self._draw_circle(img, center_x, center_y, size, color, memory.opacity)
    
    def _draw_circle(self, img: np.ndarray, x: int, y: int, radius: int, 
                    color: Tuple[int, int, int], opacity: float):
        """Draw filled circle"""
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx*dx + dy*dy <= radius*radius:
                    px, py = x + dx, y + dy
                    if 0 <= px < img.shape[1] and 0 <= py < img.shape[0]:
                        img[py, px] = color
    
    def _draw_triangle(self, img: np.ndarray, x: int, y: int, size: int, 
                      color: Tuple[int, int, int], opacity: float):
        """Draw filled triangle"""
        # Simple triangle drawing
        for dy in range(-size, size + 1):
            for dx in range(-size, size + 1):
                if abs(dx) + abs(dy) <= size and dy >= 0:
                    px, py = x + dx, y + dy
                    if 0 <= px < img.shape[1] and 0 <= py < img.shape[0]:
                        img[py, px] = color
    
    def _draw_square(self, img: np.ndarray, x: int, y: int, size: int, 
                    color: Tuple[int, int, int], opacity: float):
        """Draw filled square"""
        for dy in range(-size, size + 1):
            for dx in range(-size, size + 1):
                px, py = x + dx, y + dy
                if 0 <= px < img.shape[1] and 0 <= py < img.shape[0]:
                    img[py, px] = color

# Example usage and testing
if __name__ == "__main__":
    # Initialize vector memory system
    vector_memory = LunaVectorMemorySystem()
    
    # Add some sample memories
    sample_memories = [
        ("Chris loves gaming and streaming", "semantic", "happy", "gaming", 0.8),
        ("Luna helped with coding problems", "episodic", "excited", "work", 0.9),
        ("Discord chat was very active today", "social", "excited", "streaming", 0.7),
        ("Learned about vector graphics", "semantic", "curious", "learning", 0.6),
        ("Feeling creative and inspired", "emotional", "happy", "creative", 0.8),
    ]
    
    for content, mem_type, emotion, context, importance in sample_memories:
        vector_memory.add_memory(content, mem_type, emotion, context, importance)
    
    # Search for memories
    print("\n🔍 Searching for gaming-related memories:")
    results = vector_memory.search_memories_by_vector("gaming", memory_type="semantic", limit=3)
    for memory, score in results:
        print(f"  - {memory.content[:50]}... (score: {score:.3f})")
    
    # Get memory clusters
    clusters = vector_memory.get_memory_clusters()
    print(f"\n🎯 Found {len(clusters)} memory clusters")
    
    # Create visualization
    vector_memory.visualize_memory_space("luna_vector_memory_space.png")
    print("\n✅ Vector memory system test completed!")
