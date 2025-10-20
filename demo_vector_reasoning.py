#!/usr/bin/env python3
"""
Demo script showing Luna's Vector Reasoning capabilities
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def demo_vector_reasoning():
    """Demonstrate Luna's vector reasoning capabilities"""
    print("🧠 Luna Vector Reasoning Demo")
    print("=" * 50)
    
    try:
        # Import Luna's systems
        from luna_vector_reasoning import initialize_vector_reasoning, reason_with_vectors
        from luna_dna_memory import initialize_dna_memory, save_dna_memory
        from luna_understanding import UnderstandingEngine
        
        print("✅ Systems imported successfully")
        
        # Initialize systems
        print("\n🔧 Initializing systems...")
        vector_engine = initialize_vector_reasoning()
        dna_memory = initialize_dna_memory()
        understanding = UnderstandingEngine("demo-model")
        
        print("✅ Systems initialized")
        
        # Add some demo memories to show vector reasoning
        print("\n📝 Adding demo memories...")
        demo_memories = [
            ("I love my cat Luna", "Cats are such wonderful companions! Luna sounds special.", "demo", "demo_user"),
            ("I'm feeling stressed about work", "Work stress can be overwhelming. What's been bothering you most?", "demo", "demo_user"),
            ("I love programming in Python", "Python is such a versatile language! What are you building?", "demo", "demo_user"),
            ("I'm excited about my new project", "That's wonderful! New projects are so energizing. Tell me more!", "demo", "demo_user"),
            ("I feel lonely sometimes", "I'm here for you. Loneliness can be really hard. What helps you feel connected?", "demo", "demo_user"),
            ("I love learning new things", "Learning is one of life's greatest joys! What are you curious about?", "demo", "demo_user"),
            ("I'm worried about the future", "The future can feel uncertain. What specific concerns do you have?", "demo", "demo_user"),
            ("I love spending time with friends", "Friends are so important! Good relationships bring so much joy.", "demo", "demo_user")
        ]
        
        for user_msg, luna_resp, platform, username in demo_memories:
            save_dna_memory(user_msg, luna_resp, platform, username)
        
        print(f"✅ Added {len(demo_memories)} demo memories")
        
        # Demo different types of reasoning
        demo_queries = [
            "I'm feeling emotional today",
            "What makes me happy?",
            "I need some advice about relationships",
            "I'm curious about learning something new"
        ]
        
        for i, query in enumerate(demo_queries, 1):
            print(f"\n🧠 Demo {i}: Vector Reasoning for '{query}'")
            print("-" * 40)
            
            try:
                result = reason_with_vectors(query, "demo_user", dna_memory, understanding)
                
                if result:
                    print(f"📊 Reasoning Confidence: {result.confidence:.2f}")
                    print(f"🔍 Reasoning Steps: {len(result.reasoning_chain)}")
                    
                    if result.insights:
                        print(f"\n💡 Key Insights ({len(result.insights)}):")
                        for j, insight in enumerate(result.insights[:3], 1):
                            print(f"   {j}. {insight}")
                    
                    if result.emotional_context:
                        emotional = result.emotional_context
                        print(f"\n😊 Emotional Analysis:")
                        print(f"   Dominant emotion: {emotional.get('dominant_emotion', 'unknown')}")
                        print(f"   Emotional trajectory: {emotional.get('emotional_trajectory', 'unknown')}")
                    
                    if result.temporal_patterns:
                        temporal = result.temporal_patterns
                        print(f"\n⏰ Temporal Patterns:")
                        print(f"   Frequency pattern: {temporal.get('frequency_pattern', 'unknown')}")
                        print(f"   Total memories: {temporal.get('total_memories', 0)}")
                    
                    if result.predictions:
                        print(f"\n🔮 Predictions ({len(result.predictions)}):")
                        for j, prediction in enumerate(result.predictions[:2], 1):
                            print(f"   {j}. {prediction}")
                    
                    if result.cross_memory_connections:
                        print(f"\n🔗 Cross-Memory Connections: {len(result.cross_memory_connections)} found")
                        for j, connection in enumerate(result.cross_memory_connections[:2], 1):
                            print(f"   {j}. {connection.get('connection_type', 'unknown')} connection")
                            print(f"      Insight: {connection.get('insight', 'N/A')}")
                    
                    if result.meta_cognitive_notes:
                        print(f"\n🧠 Meta-Cognitive Analysis:")
                        for j, note in enumerate(result.meta_cognitive_notes[:2], 1):
                            print(f"   {j}. {note}")
                    
                else:
                    print("❌ No reasoning result returned")
                    
            except Exception as e:
                print(f"❌ Reasoning failed: {e}")
        
        # Show system statistics
        print(f"\n📊 System Statistics:")
        print("-" * 20)
        
        try:
            stats = vector_engine.get_reasoning_stats()
            print(f"Total reasoning chains: {stats.get('total_reasoning_chains', 0)}")
            print(f"Total patterns identified: {stats.get('total_patterns', 0)}")
            print(f"Meta-cognitive insights: {stats.get('total_meta_insights', 0)}")
            print(f"Average confidence: {stats.get('average_confidence', 0.0):.2f}")
            print(f"Vector embeddings enabled: {stats.get('embeddings_enabled', False)}")
        except Exception as e:
            print(f"❌ Statistics error: {e}")
        
        print(f"\n🎉 Vector Reasoning Demo Complete!")
        print("Luna now has advanced reasoning capabilities that can:")
        print("• Analyze patterns across all memories")
        print("• Understand emotional contexts and trajectories")
        print("• Make predictions based on historical patterns")
        print("• Find connections between seemingly unrelated memories")
        print("• Provide meta-cognitive insights about reasoning processes")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install sentence-transformers numpy")
        return False
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

if __name__ == "__main__":
    success = demo_vector_reasoning()
    if not success:
        sys.exit(1)
