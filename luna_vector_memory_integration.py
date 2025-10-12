#!/usr/bin/env python3
"""
Luna Vector Memory Integration
Integrates the vector-based memory system with existing Luna memory systems

This module bridges the vector memory system with:
- Hybrid Retrieval System (BM25 + RAG)
- Mind-Map System (Knowledge Graph)
- SQL Memory System (Database storage)
- Memory Reflection System
"""

import sqlite3
import json
import time
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import numpy as np

from luna_vector_memory_system import LunaVectorMemorySystem, VectorMemory
# Removed hybrid_retrieval_system - module not available
# Removed luna_mindmap_system - module not available

class LunaVectorMemoryIntegration:
    """Integrates vector memory system with existing Luna memory systems"""
    
    def __init__(self, vector_db_path: str = "luna_vector_memories.db",
                 main_db_path: str = "luna_memories.db"):
        self.vector_memory = LunaVectorMemorySystem(vector_db_path)
        # Removed hybrid_retrieval and mindmap - modules not available
        self.hybrid_retrieval = None
        self.mindmap = None
        
        # Integration settings
        self.vector_weight = 0.3  # Weight of vector similarity in hybrid scoring
        self.semantic_weight = 0.4  # Weight of semantic similarity
        self.temporal_weight = 0.3  # Weight of temporal relevance
        
        print("🧠 Luna Vector Memory Integration initialized (simplified)")
        print(f"📊 Integration weights: Vector={self.vector_weight}, Semantic={self.semantic_weight}, Temporal={self.temporal_weight}")
    
    def add_memory_with_vector_representation(self, content: str, memory_type: str,
                                            emotion: str = 'neutral', context: str = 'general',
                                            importance: float = 0.5, tags: List[str] = None,
                                            user_id: str = None, platform: str = None) -> Dict[str, str]:
        """Add memory to all systems with vector representation"""
        
        results = {}
        
        # 1. Add to vector memory system
        vector_id = self.vector_memory.add_memory(
            content, memory_type, emotion, context, importance, tags
        )
        results['vector_id'] = vector_id
        
        # 2. Mind-map system disabled
        mindmap_id = None
        print("🧠 Mind-map system disabled")
        results['mindmap_id'] = None
        
        # 3. Add to hybrid retrieval system (if it has an add method)
        try:
            # This would depend on the hybrid retrieval system's interface
            # For now, we'll store the content for later retrieval
            hybrid_id = self._add_to_hybrid_system(content, memory_type, importance)
            results['hybrid_id'] = hybrid_id
        except Exception as e:
            print(f"⚠️ Error adding to hybrid system: {e}")
            results['hybrid_id'] = None
        
        # 4. Create cross-system connections
        self._create_cross_system_connections(results, content, memory_type, emotion)
        
        print(f"✅ Memory added to all systems: {vector_id[:12]}...")
        return results
    
    def _map_memory_type_to_node_type(self, memory_type: str) -> str:
        """Map vector memory types to mind-map node types"""
        mapping = {
            'episodic': 'memory',
            'semantic': 'preference',
            'procedural': 'skill',
            'emotional': 'memory',
            'social': 'relationship',
            'creative': 'memory'
        }
        return mapping.get(memory_type, 'memory')
    
    def _add_to_hybrid_system(self, content: str, memory_type: str, importance: float) -> str:
        """Add memory to hybrid retrieval system"""
        # This is a placeholder - the actual implementation would depend on
        # the hybrid retrieval system's interface
        hybrid_id = f"hybrid_{int(time.time() * 1000)}"
        
        # Store in a simple format for hybrid retrieval
        memory_data = {
            'id': hybrid_id,
            'content': content,
            'type': memory_type,
            'importance': importance,
            'timestamp': datetime.now().isoformat()
        }
        
        # This would be stored in the hybrid system's database
        # For now, we'll return the ID
        return hybrid_id
    
    def _create_cross_system_connections(self, results: Dict[str, str], content: str,
                                       memory_type: str, emotion: str):
        """Create connections between systems"""
        vector_id = results.get('vector_id')
        mindmap_id = results.get('mindmap_id')
        
        if vector_id and mindmap_id:
            # Store cross-system mapping
            cross_reference = {
                'vector_id': vector_id,
                'mindmap_id': mindmap_id,
                'content': content[:100],  # Truncated for storage
                'type': memory_type,
                'emotion': emotion,
                'created_at': datetime.now().isoformat()
            }
            
            # Store in vector memory metadata
            if vector_id in self.vector_memory.memories:
                self.vector_memory.memories[vector_id].metadata['cross_system_refs'] = cross_reference
    
    def search_memories_hybrid(self, query: str, memory_type: str = None,
                             emotion: str = None, context: str = None,
                             limit: int = 10, include_visualization: bool = False) -> Dict[str, Any]:
        """Search memories using hybrid approach combining all systems"""
        
        results = {
            'vector_results': [],
            'mindmap_results': [],
            'hybrid_results': [],
            'visualization_path': None
        }
        
        # 1. Vector-based search
        vector_results = self.vector_memory.search_memories_by_vector(
            query, memory_type, emotion, context, limit
        )
        results['vector_results'] = [
            {
                'id': memory.id,
                'content': memory.content,
                'type': memory.memory_type,
                'position': memory.position,
                'color': memory.color,
                'score': score,
                'system': 'vector'
            }
            for memory, score in vector_results
        ]
        
        # 2. Mind-map search
        # Mind-map system disabled
        results['mindmap_results'] = []
        print("🧠 Mind-map search disabled")
        
        # 3. Hybrid scoring and ranking
        hybrid_results = self._combine_search_results(
            results['vector_results'], results['mindmap_results'], query
        )
        results['hybrid_results'] = hybrid_results[:limit]
        
        # 4. Generate visualization if requested
        if include_visualization:
            viz_path = f"luna_memory_search_{int(time.time())}.png"
            self._create_search_visualization(vector_results, viz_path)
            results['visualization_path'] = viz_path
        
        return results
    
    def _combine_search_results(self, vector_results: List[Dict], mindmap_results: List[Dict],
                               query: str) -> List[Dict]:
        """Combine results from different systems with hybrid scoring"""
        
        # Create a combined score for each unique memory
        memory_scores = {}
        
        # Process vector results
        for result in vector_results:
            memory_id = result['id']
            vector_score = result['score']
            
            # Apply system weight
            weighted_score = vector_score * self.vector_weight
            
            memory_scores[memory_id] = {
                'id': memory_id,
                'content': result['content'],
                'type': result['type'],
                'vector_score': vector_score,
                'mindmap_score': 0.0,
                'hybrid_score': weighted_score,
                'system': 'vector'
            }
        
        # Process mind-map results
        for result in mindmap_results:
            memory_id = result['id']
            mindmap_score = result['importance'] / 5.0  # Normalize to 0-1
            
            # Apply system weight
            weighted_score = mindmap_score * self.semantic_weight
            
            if memory_id in memory_scores:
                # Update existing entry
                memory_scores[memory_id]['mindmap_score'] = mindmap_score
                memory_scores[memory_id]['hybrid_score'] += weighted_score
                memory_scores[memory_id]['system'] = 'both'
            else:
                # Create new entry
                memory_scores[memory_id] = {
                    'id': memory_id,
                    'content': result['content'],
                    'type': result['type'],
                    'vector_score': 0.0,
                    'mindmap_score': mindmap_score,
                    'hybrid_score': weighted_score,
                    'system': 'mindmap'
                }
        
        # Apply temporal weighting
        for memory_id, data in memory_scores.items():
            if memory_id in self.vector_memory.memories:
                memory = self.vector_memory.memories[memory_id]
                temporal_score = self.vector_memory._calculate_recency_boost(memory.last_accessed)
                data['hybrid_score'] += temporal_score * self.temporal_weight
        
        # Sort by hybrid score
        sorted_results = sorted(memory_scores.values(), key=lambda x: x['hybrid_score'], reverse=True)
        
        return sorted_results
    
    def _create_search_visualization(self, vector_results: List[Tuple], output_path: str):
        """Create visualization highlighting search results"""
        
        # Create a modified visualization that highlights search results
        img = np.ones((1024, 1024, 3), dtype=np.uint8) * 255  # White background
        
        # Draw all connections first
        for connection in self.vector_memory.connections:
            if connection['strength'] > 0.3:
                self.vector_memory._draw_connection(img, connection, 1024, 1024)
        
        # Draw all memories (dimmed)
        for memory in self.vector_memory.memories.values():
            # Dim non-search-result memories
            original_opacity = memory.opacity
            memory.opacity = original_opacity * 0.3  # Dim to 30%
            self.vector_memory._draw_memory(img, memory, 1024, 1024)
            memory.opacity = original_opacity  # Restore original
        
        # Highlight search result memories
        for memory, score in vector_results:
            # Bright highlight for search results
            original_opacity = memory.opacity
            memory.opacity = 1.0  # Full opacity for highlights
            self.vector_memory._draw_memory(img, memory, 1024, 1024)
            memory.opacity = original_opacity  # Restore original
        
        # Save image
        from PIL import Image
        Image.fromarray(img).save(output_path)
        print(f"🎨 Search visualization saved to: {output_path}")
    
    def get_memory_insights(self, user_id: str = None, platform: str = None) -> Dict[str, Any]:
        """Get insights about memory patterns and clusters"""
        
        insights = {
            'total_memories': len(self.vector_memory.memories),
            'memory_types': {},
            'emotion_distribution': {},
            'context_distribution': {},
            'memory_clusters': [],
            'recent_activity': [],
            'strongest_connections': []
        }
        
        # Analyze memory types
        for memory in self.vector_memory.memories.values():
            mem_type = memory.memory_type
            insights['memory_types'][mem_type] = insights['memory_types'].get(mem_type, 0) + 1
        
        # Analyze emotions and contexts from colors
        for memory in self.vector_memory.memories.values():
            # Map colors back to emotions/contexts (simplified)
            emotion = self._color_to_emotion(memory.color)
            context = self._color_to_context(memory.color)
            
            insights['emotion_distribution'][emotion] = insights['emotion_distribution'].get(emotion, 0) + 1
            insights['context_distribution'][context] = insights['context_distribution'].get(context, 0) + 1
        
        # Get memory clusters
        clusters = self.vector_memory.get_memory_clusters()
        insights['memory_clusters'] = [
            {
                'cluster_id': i,
                'size': len(cluster),
                'memories': [mem.id for mem in cluster],
                'center_position': self._calculate_cluster_center(cluster)
            }
            for i, cluster in enumerate(clusters)
        ]
        
        # Get recent activity
        recent_memories = sorted(
            self.vector_memory.memories.values(),
            key=lambda x: x.last_accessed,
            reverse=True
        )[:10]
        
        insights['recent_activity'] = [
            {
                'id': mem.id,
                'content': mem.content[:50] + "..." if len(mem.content) > 50 else mem.content,
                'type': mem.memory_type,
                'last_accessed': mem.last_accessed
            }
            for mem in recent_memories
        ]
        
        # Get strongest connections
        strong_connections = sorted(
            self.vector_memory.connections,
            key=lambda x: x['strength'],
            reverse=True
        )[:10]
        
        insights['strongest_connections'] = [
            {
                'from': conn['from_memory'],
                'to': conn['to_memory'],
                'type': conn['connection_type'],
                'strength': conn['strength']
            }
            for conn in strong_connections
        ]
        
        return insights
    
    def _color_to_emotion(self, color: Tuple[float, float, float]) -> str:
        """Map color back to emotion (simplified)"""
        r, g, b = color
        
        if r > 0.7 and g > 0.7 and b < 0.3:
            return 'happy'
        elif r < 0.4 and g < 0.4 and b > 0.7:
            return 'sad'
        elif r > 0.7 and g > 0.4 and b < 0.3:
            return 'excited'
        elif r < 0.5 and g > 0.7 and b > 0.5:
            return 'calm'
        else:
            return 'neutral'
    
    def _color_to_context(self, color: Tuple[float, float, float]) -> str:
        """Map color back to context (simplified)"""
        r, g, b = color
        
        if g > 0.7 and r < 0.5 and b < 0.5:
            return 'gaming'
        elif r > 0.7 and g < 0.5 and b > 0.7:
            return 'streaming'
        elif b > 0.7 and r < 0.5 and g < 0.5:
            return 'learning'
        elif r > 0.7 and g > 0.5 and b < 0.5:
            return 'personal'
        else:
            return 'general'
    
    def _calculate_cluster_center(self, cluster: List[VectorMemory]) -> Tuple[float, float]:
        """Calculate center position of a memory cluster"""
        if not cluster:
            return (0.0, 0.0)
        
        x_sum = sum(memory.position[0] for memory in cluster)
        y_sum = sum(memory.position[1] for memory in cluster)
        
        return (x_sum / len(cluster), y_sum / len(cluster))
    
    def export_memory_analysis(self, output_path: str = "luna_memory_analysis.json"):
        """Export comprehensive memory analysis"""
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'system_info': {
                'vector_memories': len(self.vector_memory.memories),
                'connections': len(self.vector_memory.connections),
                'integration_weights': {
                    'vector': self.vector_weight,
                    'semantic': self.semantic_weight,
                    'temporal': self.temporal_weight
                }
            },
            'insights': self.get_memory_insights(),
            'top_memories': self._get_top_memories_by_importance(),
            'memory_evolution': self._analyze_memory_evolution()
        }
        
        with open(output_path, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"📊 Memory analysis exported to: {output_path}")
        return analysis
    
    def _get_top_memories_by_importance(self, limit: int = 20) -> List[Dict]:
        """Get top memories by importance (size + opacity + connections)"""
        
        memory_scores = []
        
        for memory in self.vector_memory.memories.values():
            # Calculate importance score
            importance_score = (
                memory.size * 0.4 +           # Size factor
                memory.opacity * 0.4 +        # Opacity factor
                len(memory.connections) * 0.1 + # Connection factor
                memory.access_count * 0.1     # Access count factor
            )
            
            memory_scores.append({
                'id': memory.id,
                'content': memory.content[:100] + "..." if len(memory.content) > 100 else memory.content,
                'type': memory.memory_type,
                'importance_score': importance_score,
                'size': memory.size,
                'opacity': memory.opacity,
                'connections': len(memory.connections),
                'access_count': memory.access_count
            })
        
        # Sort by importance score
        memory_scores.sort(key=lambda x: x['importance_score'], reverse=True)
        return memory_scores[:limit]
    
    def _analyze_memory_evolution(self) -> Dict[str, Any]:
        """Analyze how memories have evolved over time"""
        
        evolution = {
            'creation_timeline': {},
            'type_evolution': {},
            'emotional_evolution': {},
            'growth_rate': 0.0
        }
        
        # Analyze creation timeline
        for memory in self.vector_memory.memories.values():
            try:
                creation_date = datetime.fromisoformat(memory.created_at).date()
                date_str = creation_date.isoformat()
                evolution['creation_timeline'][date_str] = evolution['creation_timeline'].get(date_str, 0) + 1
            except:
                continue
        
        # Analyze type evolution
        for memory in self.vector_memory.memories.values():
            try:
                creation_date = datetime.fromisoformat(memory.created_at).date()
                month_key = creation_date.strftime('%Y-%m')
                
                if month_key not in evolution['type_evolution']:
                    evolution['type_evolution'][month_key] = {}
                
                mem_type = memory.memory_type
                evolution['type_evolution'][month_key][mem_type] = evolution['type_evolution'][month_key].get(mem_type, 0) + 1
            except:
                continue
        
        # Calculate growth rate (memories per day over last 30 days)
        recent_count = 0
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        for memory in self.vector_memory.memories.values():
            try:
                creation_date = datetime.fromisoformat(memory.created_at)
                if creation_date >= thirty_days_ago:
                    recent_count += 1
            except:
                continue
        
        evolution['growth_rate'] = recent_count / 30.0  # Memories per day
        
        return evolution

# Example usage
if __name__ == "__main__":
    # Initialize integrated system
    integration = LunaVectorMemoryIntegration()
    
    # Add memories with full integration
    sample_memories = [
        ("Chris loves playing games and streaming them", "semantic", "happy", "gaming", 0.9),
        ("Luna helped debug the vector memory system", "episodic", "excited", "work", 0.8),
        ("Discord community was very active today", "social", "excited", "streaming", 0.7),
        ("Learned about vector mathematics for AI", "semantic", "curious", "learning", 0.6),
        ("Feeling inspired by the new memory system", "emotional", "happy", "creative", 0.8),
    ]
    
    print("🧠 Adding memories with full system integration...")
    for content, mem_type, emotion, context, importance in sample_memories:
        results = integration.add_memory_with_vector_representation(
            content, mem_type, emotion, context, importance
        )
        print(f"  ✅ Added: {results['vector_id'][:12]}...")
    
    # Search with hybrid approach
    print("\n🔍 Hybrid memory search:")
    search_results = integration.search_memories_hybrid("gaming", include_visualization=True)
    
    print(f"Vector results: {len(search_results['vector_results'])}")
    print(f"Mind-map results: {len(search_results['mindmap_results'])}")
    print(f"Hybrid results: {len(search_results['hybrid_results'])}")
    
    # Get insights
    print("\n📊 Memory insights:")
    insights = integration.get_memory_insights()
    print(f"Total memories: {insights['total_memories']}")
    print(f"Memory types: {insights['memory_types']}")
    print(f"Memory clusters: {len(insights['memory_clusters'])}")
    
    # Export analysis
    analysis = integration.export_memory_analysis()
    print(f"\n✅ Integration test completed! Analysis saved.")
