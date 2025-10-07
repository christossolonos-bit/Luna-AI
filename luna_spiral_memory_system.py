#!/usr/bin/env python3
"""
Luna's Spiral Vector Memory System
Mathematical equations stored as infinite spiral coordinates from a central point

Concept: Memories are represented as points on mathematical spirals:
- Golden Spiral: φ = a × φ^(b×θ) for natural growth patterns
- Logarithmic Spiral: r = a × e^(b×θ) for continuous expansion
- Archimedean Spiral: r = a + b×θ for linear growth
- Each memory type uses different spiral equations
- Infinite scalability from central point (0,0,0)
"""

import math
import numpy as np
import sqlite3
import json
import time
import hashlib
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import threading

@dataclass
class SpiralMemory:
    """Represents a memory as a point on a mathematical spiral"""
    id: str
    content: str
    memory_type: str
    
    # Spiral coordinates (3D for depth)
    theta: float  # Angle in radians
    radius: float  # Distance from center
    z_depth: float  # Depth in 3D space
    
    # Mathematical properties
    spiral_type: str  # 'golden', 'logarithmic', 'archimedean', 'fibonacci'
    spiral_equation: str  # Mathematical equation as string
    spiral_params: Dict[str, float]  # Parameters for the spiral equation
    
    # Memory properties
    importance: float  # 0.0 to 1.0
    emotional_weight: float  # -1.0 to 1.0 (negative = sad, positive = happy)
    temporal_decay: float  # How quickly memory fades
    
    # Metadata
    created_at: str
    last_accessed: str
    access_count: int
    connections: List[str]  # Connected memory IDs
    
    # Vector properties for efficiency
    cartesian_coords: Tuple[float, float, float]  # (x, y, z)
    memory_vector: np.ndarray  # Mathematical representation

class SpiralEquationGenerator:
    """Generates mathematical spiral equations for different memory types"""
    
    def __init__(self):
        self.spiral_types = {
            'episodic': 'golden',      # Natural growth for personal experiences
            'semantic': 'logarithmic', # Continuous expansion for knowledge
            'procedural': 'archimedean', # Linear growth for skills
            'emotional': 'fibonacci',   # Fibonacci spiral for emotional patterns
            'social': 'golden',        # Golden ratio for social connections
            'creative': 'logarithmic'   # Logarithmic for creative expansion
        }
        
        # Mathematical constants
        self.golden_ratio = (1 + math.sqrt(5)) / 2
        self.e = math.e
    
    def generate_spiral_coordinates(self, memory_type: str, content: str, 
                                  importance: float, emotional_weight: float) -> Dict[str, Any]:
        """Generate spiral coordinates using mathematical equations"""
        
        spiral_type = self.spiral_types.get(memory_type, 'golden')
        
        # Generate theta based on content hash for consistency
        content_hash = hashlib.md5(content.encode()).hexdigest()
        theta_base = (int(content_hash[:8], 16) / 0xffffffff) * 4 * math.pi  # 0 to 4π
        
        # Add importance and emotional weighting to theta
        theta = theta_base + (importance * math.pi) + (emotional_weight * math.pi / 2)
        
        # Generate spiral parameters based on memory type
        if spiral_type == 'golden':
            # Golden spiral: r = φ^(θ/π)
            a = 1.0 + importance  # Scale factor
            b = self.golden_ratio
            radius = a * (b ** (theta / math.pi))
            equation = f"r = {a:.3f} × φ^({theta/math.pi:.3f})"
            params = {'a': a, 'b': b, 'theta': theta}
            
        elif spiral_type == 'logarithmic':
            # Logarithmic spiral: r = a × e^(b×θ)
            a = 0.5 + importance * 0.5
            b = 0.3 + emotional_weight * 0.2
            radius = a * math.exp(b * theta)
            equation = f"r = {a:.3f} × e^({b:.3f}×θ)"
            params = {'a': a, 'b': b, 'theta': theta}
            
        elif spiral_type == 'archimedean':
            # Archimedean spiral: r = a + b×θ
            a = 1.0
            b = 0.1 + importance * 0.2
            radius = a + b * theta
            equation = f"r = {a:.3f} + {b:.3f}×θ"
            params = {'a': a, 'b': b, 'theta': theta}
            
        elif spiral_type == 'fibonacci':
            # Fibonacci-inspired spiral using golden ratio
            a = 1.0 + importance * 0.5
            b = self.golden_ratio
            radius = a * math.pow(b, theta / (2 * math.pi))
            equation = f"r = {a:.3f} × φ^({theta/(2*math.pi):.3f})"
            params = {'a': a, 'b': b, 'theta': theta}
        
        # Generate z-depth for 3D spiral
        z_depth = math.sin(theta) * importance + math.cos(theta * 2) * emotional_weight
        
        # Convert to Cartesian coordinates
        x = radius * math.cos(theta)
        y = radius * math.sin(theta)
        z = z_depth
        
        # Create memory vector for mathematical operations
        memory_vector = np.array([x, y, z, importance, emotional_weight, theta])
        
        return {
            'theta': theta,
            'radius': radius,
            'z_depth': z_depth,
            'spiral_type': spiral_type,
            'spiral_equation': equation,
            'spiral_params': params,
            'cartesian_coords': (x, y, z),
            'memory_vector': memory_vector
        }

class SpiralMemoryCluster:
    """Manages clusters of memories on spiral patterns"""
    
    def __init__(self):
        self.cluster_types = {
            'concentric': 'memories on same spiral radius',
            'temporal': 'memories following time-based spiral growth',
            'emotional': 'memories clustered by emotional weight',
            'semantic': 'memories clustered by content similarity'
        }
    
    def find_memory_clusters(self, memories: List[SpiralMemory], 
                           cluster_type: str = 'concentric') -> List[List[SpiralMemory]]:
        """Find clusters of memories based on spiral proximity"""
        
        clusters = []
        processed = set()
        
        for memory in memories:
            if memory.id in processed:
                continue
            
            cluster = [memory]
            processed.add(memory.id)
            
            # Find nearby memories based on spiral distance
            for other_memory in memories:
                if other_memory.id in processed:
                    continue
                
                if self._are_memories_connected(memory, other_memory, cluster_type):
                    cluster.append(other_memory)
                    processed.add(other_memory.id)
            
            if len(cluster) > 1:
                clusters.append(cluster)
        
        return clusters
    
    def _are_memories_connected(self, mem1: SpiralMemory, mem2: SpiralMemory, 
                              cluster_type: str) -> bool:
        """Check if two memories should be in the same cluster"""
        
        if cluster_type == 'concentric':
            # Same spiral radius (within tolerance)
            radius_diff = abs(mem1.radius - mem2.radius)
            return radius_diff < 0.5
            
        elif cluster_type == 'temporal':
            # Similar theta angles (time-based)
            theta_diff = abs(mem1.theta - mem2.theta)
            return theta_diff < math.pi / 4  # 45 degrees
            
        elif cluster_type == 'emotional':
            # Similar emotional weights
            emotion_diff = abs(mem1.emotional_weight - mem2.emotional_weight)
            return emotion_diff < 0.3
            
        elif cluster_type == 'semantic':
            # Similar importance and spiral type
            importance_diff = abs(mem1.importance - mem2.importance)
            return importance_diff < 0.2 and mem1.spiral_type == mem2.spiral_type
        
        return False

class LunaSpiralMemorySystem:
    """Main spiral-based memory system for Luna"""
    
    def __init__(self, db_path: str = "luna_spiral_memories.db"):
        self.db_path = db_path
        self.equation_generator = SpiralEquationGenerator()
        self.cluster_manager = SpiralMemoryCluster()
        self.memories: Dict[str, SpiralMemory] = {}
        self.spiral_cache: Dict[str, np.ndarray] = {}
        self.lock = threading.Lock()
        
        self._init_database()
        self._load_existing_memories()
        
        print("🌀 Luna Spiral Memory System initialized")
        print("📐 Mathematical equations: Golden, Logarithmic, Archimedean, Fibonacci spirals")
    
    def _init_database(self):
        """Initialize database for spiral memories"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS spiral_memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    theta REAL NOT NULL,
                    radius REAL NOT NULL,
                    z_depth REAL NOT NULL,
                    spiral_type TEXT NOT NULL,
                    spiral_equation TEXT NOT NULL,
                    spiral_params TEXT NOT NULL,
                    importance REAL NOT NULL,
                    emotional_weight REAL NOT NULL,
                    temporal_decay REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    last_accessed TEXT NOT NULL,
                    access_count INTEGER NOT NULL,
                    connections TEXT NOT NULL,
                    cartesian_coords TEXT NOT NULL,
                    memory_vector TEXT NOT NULL
                )
            ''')
            conn.commit()
    
    def _load_existing_memories(self):
        """Load existing spiral memories from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT * FROM spiral_memories')
            for row in cursor.fetchall():
                memory = SpiralMemory(
                    id=row[0],
                    content=row[1],
                    memory_type=row[2],
                    theta=row[3],
                    radius=row[4],
                    z_depth=row[5],
                    spiral_type=row[6],
                    spiral_equation=row[7],
                    spiral_params=json.loads(row[8]),
                    importance=row[9],
                    emotional_weight=row[10],
                    temporal_decay=row[11],
                    created_at=row[12],
                    last_accessed=row[13],
                    access_count=row[14],
                    connections=json.loads(row[15]),
                    cartesian_coords=tuple(json.loads(row[16])),
                    memory_vector=np.array(json.loads(row[17]))
                )
                self.memories[memory.id] = memory
    
    def add_memory(self, content: str, memory_type: str, importance: float = 0.5,
                  emotional_weight: float = 0.0, temporal_decay: float = 0.01) -> str:
        """Add a new memory with spiral coordinates"""
        
        with self.lock:
            memory_id = f"spiral_{int(time.time() * 1000)}_{hashlib.md5(content.encode()).hexdigest()[:8]}"
            
            # Generate spiral coordinates
            spiral_data = self.equation_generator.generate_spiral_coordinates(
                memory_type, content, importance, emotional_weight
            )
            
            # Create spiral memory
            memory = SpiralMemory(
                id=memory_id,
                content=content,
                memory_type=memory_type,
                theta=spiral_data['theta'],
                radius=spiral_data['radius'],
                z_depth=spiral_data['z_depth'],
                spiral_type=spiral_data['spiral_type'],
                spiral_equation=spiral_data['spiral_equation'],
                spiral_params=spiral_data['spiral_params'],
                importance=importance,
                emotional_weight=emotional_weight,
                temporal_decay=temporal_decay,
                created_at=datetime.now().isoformat(),
                last_accessed=datetime.now().isoformat(),
                access_count=1,
                connections=[],
                cartesian_coords=spiral_data['cartesian_coords'],
                memory_vector=spiral_data['memory_vector']
            )
            
            # Store memory
            self.memories[memory_id] = memory
            self._save_memory_to_db(memory)
            
            print(f"🌀 Spiral memory added: {memory_id[:12]}...")
            print(f"📐 Equation: {memory.spiral_equation}")
            print(f"📍 Coords: θ={memory.theta:.3f}, r={memory.radius:.3f}, z={memory.z_depth:.3f}")
            
            return memory_id
    
    def _save_memory_to_db(self, memory: SpiralMemory):
        """Save spiral memory to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO spiral_memories VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                memory.id, memory.content, memory.memory_type,
                memory.theta, memory.radius, memory.z_depth,
                memory.spiral_type, memory.spiral_equation,
                json.dumps(memory.spiral_params),
                memory.importance, memory.emotional_weight, memory.temporal_decay,
                memory.created_at, memory.last_accessed, memory.access_count,
                json.dumps(memory.connections),
                json.dumps(memory.cartesian_coords),
                json.dumps(memory.memory_vector.tolist())
            ))
            conn.commit()
    
    def search_spiral_memories(self, query: str, memory_type: str = None,
                             emotional_range: Tuple[float, float] = None,
                             importance_threshold: float = 0.1,
                             limit: int = 10) -> List[Tuple[SpiralMemory, float]]:
        """Search memories using spiral mathematics and vector similarity"""
        
        # Generate query spiral coordinates
        query_importance = 0.5
        query_emotion = 0.0
        query_spiral = self.equation_generator.generate_spiral_coordinates(
            memory_type or 'semantic', query, query_importance, query_emotion
        )
        query_vector = query_spiral['memory_vector']
        
        results = []
        
        for memory in self.memories.values():
            # Filter by type if specified
            if memory_type and memory.memory_type != memory_type:
                continue
            
            # Filter by emotional range if specified
            if emotional_range:
                min_emotion, max_emotion = emotional_range
                if not (min_emotion <= memory.emotional_weight <= max_emotion):
                    continue
            
            # Filter by importance threshold
            if memory.importance < importance_threshold:
                continue
            
            # Calculate spiral similarity using vector mathematics
            similarity = self._calculate_spiral_similarity(query_vector, memory.memory_vector)
            
            # Apply temporal decay
            temporal_factor = self._calculate_temporal_factor(memory.last_accessed)
            final_score = similarity * (1.0 + temporal_factor)
            
            results.append((memory, final_score))
        
        # Sort by score and return top results
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]
    
    def _calculate_spiral_similarity(self, vector1: np.ndarray, vector2: np.ndarray) -> float:
        """Calculate similarity between memory vectors using spiral mathematics"""
        
        # Euclidean distance in 6D space (x, y, z, importance, emotion, theta)
        distance = np.linalg.norm(vector1 - vector2)
        
        # Convert distance to similarity (closer = more similar)
        similarity = math.exp(-distance / 2.0)
        
        return max(0.0, min(1.0, similarity))
    
    def _calculate_temporal_factor(self, last_accessed: str) -> float:
        """Calculate temporal relevance factor"""
        try:
            last_access = datetime.fromisoformat(last_accessed)
            days_ago = (datetime.now() - last_access).days
            # Exponential decay with 30-day half-life
            return math.exp(-days_ago / 30.0) * 0.3
        except:
            return 0.0
    
    def get_spiral_clusters(self, cluster_type: str = 'concentric') -> List[List[SpiralMemory]]:
        """Get clusters of memories based on spiral patterns"""
        return self.cluster_manager.find_memory_clusters(
            list(self.memories.values()), cluster_type
        )
    
    def visualize_spiral_memory_space(self, output_path: str = "luna_spiral_memory_space.png",
                                    width: int = 1024, height: int = 1024):
        """Create 3D spiral visualization of memory space"""
        
        # Create 3D plot using matplotlib
        try:
            import matplotlib.pyplot as plt
            from mpl_toolkits.mplot3d import Axes3D
            
            fig = plt.figure(figsize=(12, 10))
            ax = fig.add_subplot(111, projection='3d')
            
            # Plot memories by spiral type with different colors
            colors = {
                'golden': 'gold',
                'logarithmic': 'blue',
                'archimedean': 'green',
                'fibonacci': 'purple'
            }
            
            for spiral_type, color in colors.items():
                x_coords = []
                y_coords = []
                z_coords = []
                
                for memory in self.memories.values():
                    if memory.spiral_type == spiral_type:
                        x, y, z = memory.cartesian_coords
                        x_coords.append(x)
                        y_coords.append(y)
                        z_coords.append(z)
                
                if x_coords:
                    ax.scatter(x_coords, y_coords, z_coords, c=color, 
                             label=f'{spiral_type.title()} Spiral', s=30, alpha=0.7)
            
            # Draw spiral curves
            self._draw_spiral_curves(ax)
            
            ax.set_xlabel('X (Cosine Component)')
            ax.set_ylabel('Y (Sine Component)')
            ax.set_zlabel('Z (Depth)')
            ax.set_title('Luna\'s Spiral Memory Space\nMathematical Equations from Infinite Point')
            ax.legend()
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"🌀 Spiral memory visualization saved to: {output_path}")
            
        except ImportError:
            print("⚠️ Matplotlib not available for 3D visualization")
    
    def _draw_spiral_curves(self, ax):
        """Draw the mathematical spiral curves"""
        
        theta_range = np.linspace(0, 8*math.pi, 1000)
        
        # Golden spiral
        a, b = 1.0, self.equation_generator.golden_ratio
        r_golden = a * (b ** (theta_range / math.pi))
        x_golden = r_golden * np.cos(theta_range)
        y_golden = r_golden * np.sin(theta_range)
        z_golden = np.sin(theta_range) * 0.5
        
        ax.plot(x_golden, y_golden, z_golden, 'gold', alpha=0.3, linewidth=1)
        
        # Logarithmic spiral
        a, b = 0.5, 0.2
        r_log = a * np.exp(b * theta_range)
        x_log = r_log * np.cos(theta_range)
        y_log = r_log * np.sin(theta_range)
        z_log = np.cos(theta_range * 2) * 0.3
        
        ax.plot(x_log, y_log, z_log, 'blue', alpha=0.3, linewidth=1)
        
        # Archimedean spiral
        a, b = 1.0, 0.1
        r_arch = a + b * theta_range
        x_arch = r_arch * np.cos(theta_range)
        y_arch = r_arch * np.sin(theta_range)
        z_arch = np.sin(theta_range * 3) * 0.2
        
        ax.plot(x_arch, y_arch, z_arch, 'green', alpha=0.3, linewidth=1)
    
    def export_spiral_equations(self, output_path: str = "luna_spiral_equations.json"):
        """Export all spiral equations and their mathematical properties"""
        
        equations_data = {
            'system_info': {
                'total_memories': len(self.memories),
                'spiral_types': list(set(m.spiral_type for m in self.memories.values())),
                'mathematical_constants': {
                    'golden_ratio': self.equation_generator.golden_ratio,
                    'euler_number': self.equation_generator.e,
                    'pi': math.pi
                }
            },
            'spiral_equations': []
        }
        
        for memory in self.memories.values():
            equation_data = {
                'memory_id': memory.id,
                'content': memory.content[:100] + "..." if len(memory.content) > 100 else memory.content,
                'memory_type': memory.memory_type,
                'spiral_type': memory.spiral_type,
                'equation': memory.spiral_equation,
                'parameters': memory.spiral_params,
                'coordinates': {
                    'theta': memory.theta,
                    'radius': memory.radius,
                    'z_depth': memory.z_depth,
                    'cartesian': memory.cartesian_coords
                },
                'properties': {
                    'importance': memory.importance,
                    'emotional_weight': memory.emotional_weight,
                    'temporal_decay': memory.temporal_decay
                }
            }
            equations_data['spiral_equations'].append(equation_data)
        
        with open(output_path, 'w') as f:
            json.dump(equations_data, f, indent=2)
        
        print(f"📐 Spiral equations exported to: {output_path}")
        return equations_data

# Example usage and testing
if __name__ == "__main__":
    # Initialize spiral memory system
    spiral_memory = LunaSpiralMemorySystem()
    
    # Add sample memories with different types
    sample_memories = [
        ("Chris loves gaming and streaming", "semantic", 0.9, 0.7),
        ("Luna helped debug the spiral memory system", "episodic", 0.8, 0.6),
        ("Discord community was very active", "social", 0.7, 0.8),
        ("Learned about spiral mathematics", "semantic", 0.6, 0.4),
        ("Feeling inspired by mathematical beauty", "emotional", 0.8, 0.9),
        ("How to implement spiral algorithms", "procedural", 0.7, 0.3),
        ("Creative ideas for AI memory systems", "creative", 0.8, 0.8)
    ]
    
    print("🌀 Adding memories to spiral system...")
    for content, mem_type, importance, emotion in sample_memories:
        spiral_memory.add_memory(content, mem_type, importance, emotion)
    
    # Search memories
    print("\n🔍 Searching spiral memories...")
    results = spiral_memory.search_spiral_memories("gaming", memory_type="semantic", limit=3)
    for memory, score in results:
        print(f"  - {memory.content[:50]}... (score: {score:.3f})")
        print(f"    Equation: {memory.spiral_equation}")
    
    # Get clusters
    clusters = spiral_memory.get_spiral_clusters('concentric')
    print(f"\n🌀 Found {len(clusters)} spiral clusters")
    
    # Create visualization
    spiral_memory.visualize_spiral_memory_space("luna_spiral_memory_3d.png")
    
    # Export equations
    equations = spiral_memory.export_spiral_equations("luna_spiral_equations.json")
    
    print("\n✅ Spiral memory system test completed!")
    print("🌀 Mathematical spirals: Infinite scalability from central point")
    print("📐 Equations: Golden, Logarithmic, Archimedean, Fibonacci")
    print("🎯 Efficiency: Vector mathematics for fast similarity calculations")
