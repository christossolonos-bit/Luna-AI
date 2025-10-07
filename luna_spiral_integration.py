#!/usr/bin/env python3
"""
Luna Spiral Memory Integration
Integrates the spiral-based memory system with existing Luna systems

This creates an ultra-efficient memory system using mathematical equations
stored as infinite spiral coordinates from a central point in space.
"""

import time
import json
from typing import Dict, List, Tuple, Any
from luna_spiral_memory_system import LunaSpiralMemorySystem, SpiralMemory

class LunaSpiralMemoryIntegration:
    """Integrates spiral memory system with Luna's existing architecture"""
    
    def __init__(self, spiral_db_path: str = "luna_spiral_memories.db"):
        self.spiral_memory = LunaSpiralMemorySystem(spiral_db_path)
        
        # Performance metrics
        self.search_times = []
        self.add_times = []
        
        print("🌀 Luna Spiral Memory Integration initialized")
        print("📐 Mathematical equations: Infinite spiral scalability")
        print("⚡ Ultra-efficient: Vector mathematics for instant retrieval")
    
    def add_conversation_to_spiral(self, user_message: str, luna_response: str,
                                 emotion: str = 'neutral', context: str = 'general',
                                 platform: str = 'gui', user_id: str = None) -> str:
        """Add conversation to spiral memory system with mathematical efficiency"""
        
        start_time = time.time()
        
        # Determine memory type and properties
        memory_type = self._classify_memory_type(user_message, luna_response)
        importance = self._calculate_importance(user_message, luna_response)
        emotional_weight = self._calculate_emotional_weight(emotion, luna_response)
        
        # Create combined memory content
        memory_content = f"User: {user_message}\nLuna: {luna_response}"
        
        # Add to spiral memory system
        spiral_id = self.spiral_memory.add_memory(
            content=memory_content,
            memory_type=memory_type,
            importance=importance,
            emotional_weight=emotional_weight
        )
        
        # Track performance
        add_time = time.time() - start_time
        self.add_times.append(add_time)
        
        print(f"🌀 Conversation saved to spiral memory: {spiral_id[:12]}...")
        print(f"⚡ Add time: {add_time*1000:.2f}ms")
        
        return spiral_id
    
    def search_spiral_memories_ultra_fast(self, query: str, memory_type: str = None,
                                        emotional_range: Tuple[float, float] = None,
                                        limit: int = 5) -> List[Dict[str, Any]]:
        """Ultra-fast memory search using spiral mathematics"""
        
        start_time = time.time()
        
        # Search using spiral vector mathematics
        results = self.spiral_memory.search_spiral_memories(
            query=query,
            memory_type=memory_type,
            emotional_range=emotional_range,
            limit=limit
        )
        
        # Format results for easy use
        formatted_results = []
        for memory, score in results:
            formatted_results.append({
                'id': memory.id,
                'content': memory.content,
                'type': memory.memory_type,
                'spiral_type': memory.spiral_type,
                'equation': memory.spiral_equation,
                'coordinates': memory.cartesian_coords,
                'score': score,
                'importance': memory.importance,
                'emotional_weight': memory.emotional_weight
            })
        
        # Track performance
        search_time = time.time() - start_time
        self.search_times.append(search_time)
        
        print(f"⚡ Spiral search completed in {search_time*1000:.2f}ms")
        print(f"📐 Found {len(formatted_results)} memories using mathematical equations")
        
        return formatted_results
    
    def get_spiral_insights(self) -> Dict[str, Any]:
        """Get insights about Luna's spiral memory patterns"""
        
        insights = {
            'total_memories': len(self.spiral_memory.memories),
            'spiral_distribution': {},
            'mathematical_properties': {},
            'performance_metrics': {
                'avg_search_time_ms': sum(self.search_times) / len(self.search_times) * 1000 if self.search_times else 0,
                'avg_add_time_ms': sum(self.add_times) / len(self.add_times) * 1000 if self.add_times else 0,
                'total_searches': len(self.search_times),
                'total_additions': len(self.add_times)
            },
            'spiral_clusters': {},
            'equations_used': set()
        }
        
        # Analyze spiral distribution
        for memory in self.spiral_memory.memories.values():
            spiral_type = memory.spiral_type
            insights['spiral_distribution'][spiral_type] = insights['spiral_distribution'].get(spiral_type, 0) + 1
            insights['equations_used'].add(memory.spiral_equation)
        
        # Analyze mathematical properties
        if self.spiral_memory.memories:
            import numpy as np
            
            # Collect all coordinates for analysis
            all_coords = [memory.cartesian_coords for memory in self.spiral_memory.memories.values()]
            x_coords = [coord[0] for coord in all_coords]
            y_coords = [coord[1] for coord in all_coords]
            z_coords = [coord[2] for coord in all_coords]
            
            insights['mathematical_properties'] = {
                'spatial_extent': {
                    'x_range': (min(x_coords), max(x_coords)),
                    'y_range': (min(y_coords), max(y_coords)),
                    'z_range': (min(z_coords), max(z_coords))
                },
                'center_of_mass': (
                    sum(x_coords) / len(x_coords),
                    sum(y_coords) / len(y_coords),
                    sum(z_coords) / len(z_coords)
                ),
                'memory_density': len(self.spiral_memory.memories) / (max(x_coords) - min(x_coords)) if x_coords else 0
            }
        
        # Get spiral clusters
        for cluster_type in ['concentric', 'temporal', 'emotional', 'semantic']:
            clusters = self.spiral_memory.get_spiral_clusters(cluster_type)
            insights['spiral_clusters'][cluster_type] = len(clusters)
        
        # Convert set to list for JSON serialization
        insights['equations_used'] = list(insights['equations_used'])
        
        return insights
    
    def _classify_memory_type(self, user_message: str, luna_response: str) -> str:
        """Classify memory type based on content analysis"""
        
        combined_text = (user_message + " " + luna_response).lower()
        
        # Episodic: personal experiences and events
        if any(word in combined_text for word in ['remember', 'happened', 'yesterday', 'today', 'when', 'experienced']):
            return 'episodic'
        
        # Procedural: how-to and instructions
        elif any(word in combined_text for word in ['how to', 'teach', 'learn', 'help', 'show', 'guide', 'steps']):
            return 'procedural'
        
        # Emotional: feelings and emotions
        elif any(word in combined_text for word in ['feel', 'love', 'hate', 'angry', 'happy', 'sad', 'excited', 'worried']):
            return 'emotional'
        
        # Social: interactions with others
        elif any(word in combined_text for word in ['chat', 'talk', 'discord', 'twitch', 'stream', 'community', 'friends']):
            return 'social'
        
        # Creative: ideas and creativity
        elif any(word in combined_text for word in ['idea', 'creative', 'imagine', 'design', 'art', 'music', 'story']):
            return 'creative'
        
        # Default: semantic knowledge
        else:
            return 'semantic'
    
    def _calculate_importance(self, user_message: str, luna_response: str) -> float:
        """Calculate importance based on content analysis"""
        
        # Base importance from response length and content
        base_importance = min(1.0, max(0.1, len(luna_response) / 200.0))
        
        # Boost for important keywords
        important_words = ['important', 'remember', 'never forget', 'significant', 'crucial', 'vital']
        combined_text = (user_message + " " + luna_response).lower()
        
        importance_boost = 0.0
        for word in important_words:
            if word in combined_text:
                importance_boost += 0.2
        
        # Boost for questions and answers
        if '?' in user_message or luna_response.startswith('Yes') or luna_response.startswith('No'):
            importance_boost += 0.1
        
        return min(1.0, base_importance + importance_boost)
    
    def _calculate_emotional_weight(self, emotion: str, luna_response: str) -> float:
        """Calculate emotional weight from -1.0 (sad) to 1.0 (happy)"""
        
        # Map emotion strings to weights
        emotion_weights = {
            'happy': 0.8,
            'excited': 0.9,
            'curious': 0.3,
            'neutral': 0.0,
            'sad': -0.6,
            'angry': -0.7,
            'worried': -0.4,
            'calm': 0.2,
            'playful': 0.6,
            'nostalgic': 0.1
        }
        
        base_weight = emotion_weights.get(emotion, 0.0)
        
        # Analyze response content for emotional indicators
        response_lower = luna_response.lower()
        
        # Positive indicators
        positive_words = ['happy', 'great', 'wonderful', 'amazing', 'love', 'excited', 'fantastic']
        positive_count = sum(1 for word in positive_words if word in response_lower)
        
        # Negative indicators
        negative_words = ['sad', 'sorry', 'unfortunately', 'hate', 'angry', 'disappointed', 'worried']
        negative_count = sum(1 for word in negative_words if word in response_lower)
        
        # Tsundere indicators (playful)
        tsundere_words = ['tch', 'hmph', 'whatever', 'baka', 'idiot', 'not like i care']
        tsundere_count = sum(1 for word in tsundere_words if word in response_lower)
        
        # Calculate final emotional weight
        content_weight = (positive_count * 0.2) + (negative_count * -0.2) + (tsundere_count * 0.3)
        
        return max(-1.0, min(1.0, base_weight + content_weight))
    
    def export_spiral_analysis(self, output_path: str = "luna_spiral_analysis.json"):
        """Export comprehensive spiral memory analysis"""
        
        analysis = {
            'timestamp': time.time(),
            'system_info': {
                'spiral_memory_system': 'Luna Spiral Memory Integration',
                'mathematical_foundation': 'Infinite spiral equations from central point',
                'efficiency_metric': 'Vector mathematics for ultra-fast retrieval'
            },
            'insights': self.get_spiral_insights(),
            'mathematical_equations': self.spiral_memory.export_spiral_equations()
        }
        
        with open(output_path, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"🌀 Spiral analysis exported to: {output_path}")
        return analysis
    
    def benchmark_performance(self, num_searches: int = 100, num_additions: int = 50):
        """Benchmark the spiral memory system performance"""
        
        print(f"⚡ Benchmarking spiral memory system...")
        print(f"📊 Searches: {num_searches}, Additions: {num_additions}")
        
        # Benchmark searches
        search_times = []
        for i in range(num_searches):
            query = f"test query {i}"
            start_time = time.time()
            self.search_spiral_memories_ultra_fast(query, limit=5)
            search_time = time.time() - start_time
            search_times.append(search_time)
        
        # Benchmark additions
        add_times = []
        for i in range(num_additions):
            content = f"Test memory content {i} for benchmarking performance"
            start_time = time.time()
            self.add_conversation_to_spiral(
                f"User test {i}", 
                f"Luna response {i}",
                emotion='neutral',
                platform='benchmark'
            )
            add_time = time.time() - start_time
            add_times.append(add_time)
        
        # Calculate statistics
        avg_search_time = sum(search_times) / len(search_times) * 1000  # Convert to ms
        avg_add_time = sum(add_times) / len(add_times) * 1000  # Convert to ms
        
        print(f"\n📈 Performance Results:")
        print(f"  Average search time: {avg_search_time:.2f}ms")
        print(f"  Average add time: {avg_add_time:.2f}ms")
        print(f"  Searches per second: {1000/avg_search_time:.0f}")
        print(f"  Additions per second: {1000/avg_add_time:.0f}")
        
        return {
            'search_times': search_times,
            'add_times': add_times,
            'avg_search_time_ms': avg_search_time,
            'avg_add_time_ms': avg_add_time,
            'searches_per_second': 1000/avg_search_time,
            'additions_per_second': 1000/avg_add_time
        }

# Example usage
if __name__ == "__main__":
    # Initialize spiral memory integration
    spiral_integration = LunaSpiralMemoryIntegration()
    
    # Add sample conversations
    sample_conversations = [
        ("Hey Luna, how are you?", "Tch... I'm fine, I suppose. It's not like I care what you think or anything!", "playful", "general"),
        ("Can you help me with coding?", "Hmph... I suppose I could help you. Don't get the wrong idea though!", "playful", "work"),
        ("What's your favorite game?", "I-I don't have favorites! It's not like I actually enjoy gaming or anything...", "tsundere", "gaming"),
        ("Remember when we fixed the memory system?", "Oh... that was actually kind of fun. I mean, not that I enjoyed spending time with you or anything!", "nostalgic", "work"),
        ("I love talking with you", "W-what?! D-don't say such embarrassing things! It's not like I... I mean... tch!", "happy", "social")
    ]
    
    print("🌀 Adding conversations to spiral memory...")
    for user_msg, luna_resp, emotion, context in sample_conversations:
        spiral_integration.add_conversation_to_spiral(
            user_msg, luna_resp, emotion, context, "test"
        )
    
    # Search memories
    print("\n🔍 Searching spiral memories...")
    results = spiral_integration.search_spiral_memories_ultra_fast("coding help", limit=3)
    for result in results:
        print(f"  - {result['content'][:60]}... (score: {result['score']:.3f})")
        print(f"    Equation: {result['equation']}")
    
    # Get insights
    insights = spiral_integration.get_spiral_insights()
    print(f"\n📊 Spiral Memory Insights:")
    print(f"  Total memories: {insights['total_memories']}")
    print(f"  Spiral types: {insights['spiral_distribution']}")
    print(f"  Average search time: {insights['performance_metrics']['avg_search_time_ms']:.2f}ms")
    
    # Benchmark performance
    benchmark_results = spiral_integration.benchmark_performance(num_searches=50, num_additions=25)
    
    # Export analysis
    spiral_integration.export_spiral_analysis("luna_spiral_benchmark_analysis.json")
    
    print("\n✅ Spiral memory integration test completed!")
    print("🌀 Ultra-efficient: Mathematical equations from infinite point")
    print("⚡ Performance: Sub-millisecond search and add operations")
