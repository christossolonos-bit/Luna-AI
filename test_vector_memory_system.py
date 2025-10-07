#!/usr/bin/env python3
"""
Test script for Luna's Vector Memory System
Demonstrates the vector-based memory capabilities
"""

import time
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_vector_memory_system():
    """Test the vector memory system with sample data"""
    
    print("🧠 Testing Luna's Vector Memory System")
    print("=" * 50)
    
    try:
        # Import the vector memory system
        from luna_vector_memory_integration import LunaVectorMemoryIntegration
        
        # Initialize the system
        print("🔄 Initializing vector memory system...")
        vector_memory = LunaVectorMemoryIntegration()
        
        # Test adding memories
        print("\n📝 Adding sample memories...")
        
        sample_memories = [
            {
                'content': 'Chris loves playing video games and streaming them to Twitch',
                'memory_type': 'semantic',
                'emotion': 'happy',
                'context': 'gaming',
                'importance': 0.9,
                'tags': ['gaming', 'streaming', 'twitch']
            },
            {
                'content': 'Luna helped debug the vector memory system code',
                'memory_type': 'episodic',
                'emotion': 'excited',
                'context': 'work',
                'importance': 0.8,
                'tags': ['coding', 'debugging', 'help']
            },
            {
                'content': 'Discord community was very active during the stream',
                'memory_type': 'social',
                'emotion': 'excited',
                'context': 'streaming',
                'importance': 0.7,
                'tags': ['discord', 'community', 'streaming']
            },
            {
                'content': 'Learned about vector mathematics for AI memory systems',
                'memory_type': 'semantic',
                'emotion': 'curious',
                'context': 'learning',
                'importance': 0.6,
                'tags': ['learning', 'ai', 'mathematics']
            },
            {
                'content': 'Feeling inspired and creative about the new memory system',
                'memory_type': 'emotional',
                'emotion': 'happy',
                'context': 'creative',
                'importance': 0.8,
                'tags': ['inspiration', 'creativity', 'memory']
            }
        ]
        
        memory_ids = []
        for i, memory_data in enumerate(sample_memories):
            print(f"  Adding memory {i+1}/5: {memory_data['content'][:50]}...")
            
            result = vector_memory.add_memory_with_vector_representation(
                content=memory_data['content'],
                memory_type=memory_data['memory_type'],
                emotion=memory_data['emotion'],
                context=memory_data['context'],
                importance=memory_data['importance'],
                tags=memory_data['tags']
            )
            
            memory_ids.append(result.get('vector_id', 'unknown'))
            print(f"    ✅ Memory ID: {result.get('vector_id', 'unknown')[:12]}...")
        
        # Test memory search
        print("\n🔍 Testing memory search...")
        
        search_queries = [
            ('gaming', 'semantic', 'gaming'),
            ('debugging', 'episodic', 'work'),
            ('discord', 'social', 'streaming'),
            ('learning', 'semantic', 'learning'),
            ('creative', 'emotional', 'creative')
        ]
        
        for query, mem_type, context in search_queries:
            print(f"\n  Searching for: '{query}' (type: {mem_type}, context: {context})")
            
            results = vector_memory.search_memories_hybrid(
                query=query,
                memory_type=mem_type,
                context=context,
                limit=3
            )
            
            print(f"    Found {len(results['hybrid_results'])} results:")
            for i, result in enumerate(results['hybrid_results'][:3]):
                print(f"      {i+1}. {result['content'][:60]}... (score: {result['hybrid_score']:.3f})")
        
        # Test memory insights
        print("\n📊 Getting memory insights...")
        
        insights = vector_memory.get_memory_insights()
        
        print(f"  Total memories: {insights['total_memories']}")
        print(f"  Memory types: {insights['memory_types']}")
        print(f"  Memory clusters: {len(insights['memory_clusters'])}")
        print(f"  Recent activity: {len(insights['recent_activity'])} items")
        print(f"  Strongest connections: {len(insights['strongest_connections'])}")
        
        # Test memory visualization
        print("\n🎨 Creating memory visualization...")
        
        try:
            vector_memory.vector_memory.visualize_memory_space("test_vector_memory_visualization.png")
            print("  ✅ Memory visualization created: test_vector_memory_visualization.png")
        except Exception as e:
            print(f"  ⚠️ Could not create visualization: {e}")
        
        # Test memory analysis export
        print("\n📈 Exporting memory analysis...")
        
        try:
            analysis = vector_memory.export_memory_analysis("test_memory_analysis.json")
            print("  ✅ Memory analysis exported: test_memory_analysis.json")
        except Exception as e:
            print(f"  ⚠️ Could not export analysis: {e}")
        
        print("\n✅ Vector memory system test completed successfully!")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all required dependencies are installed:")
        print("  - numpy")
        print("  - torch")
        print("  - PIL (Pillow)")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_memory_integration():
    """Test integration with main Luna system"""
    
    print("\n🔗 Testing memory integration with main system...")
    
    try:
        # Import main system functions
        from main import save_conversation_to_vector_memory, search_vector_memories, get_memory_insights
        
        print("  ✅ Main system integration functions available")
        
        # Test conversation saving
        print("  📝 Testing conversation saving...")
        
        save_conversation_to_vector_memory(
            user_message="Hey Luna, how are you today?",
            luna_response="Tch... I'm fine, I suppose. It's not like I care what you think or anything!",
            emotion='playful',
            context='general',
            platform='test',
            user_id='test_user'
        )
        
        print("    ✅ Conversation saved to vector memory")
        
        # Test memory search
        print("  🔍 Testing memory search...")
        
        search_results = search_vector_memories("how are you", limit=3)
        print(f"    ✅ Found {len(search_results)} relevant memories")
        
        # Test insights
        print("  📊 Testing memory insights...")
        
        insights = get_memory_insights()
        if 'error' not in insights:
            print(f"    ✅ Got insights: {insights['total_memories']} total memories")
        else:
            print(f"    ⚠️ Insights error: {insights['error']}")
        
        print("  ✅ Memory integration test completed!")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Integration test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Luna Vector Memory System Tests")
    print("=" * 60)
    
    # Test vector memory system
    vector_test_success = test_vector_memory_system()
    
    # Test integration
    integration_test_success = test_memory_integration()
    
    print("\n" + "=" * 60)
    print("📋 Test Results Summary:")
    print(f"  Vector Memory System: {'✅ PASS' if vector_test_success else '❌ FAIL'}")
    print(f"  Integration Test: {'✅ PASS' if integration_test_success else '❌ FAIL'}")
    
    if vector_test_success and integration_test_success:
        print("\n🎉 All tests passed! Vector memory system is ready to use.")
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")
    
    print("\n🧠 Vector Memory System Features:")
    print("  • Geometric memory representation using vector mathematics")
    print("  • Color-coded emotional and contextual memory palettes")
    print("  • Layered memory organization (background to foreground)")
    print("  • Vector-based memory connections and relationships")
    print("  • Hybrid search combining vector, semantic, and temporal factors")
    print("  • Memory clustering and pattern recognition")
    print("  • Visual memory space representation")
    print("  • Integration with existing Luna memory systems")
    print("  • Automatic memory type and emotion detection")
    print("  • Memory insights and analysis export")
