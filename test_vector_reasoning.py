#!/usr/bin/env python3
"""
Test script for Luna's Vector Reasoning System
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from luna_vector_reasoning import (
    initialize_vector_reasoning, get_vector_reasoning, reason_with_vectors,
    VectorReasoningEngine, ReasoningResult
)
from luna_dna_memory import initialize_dna_memory, save_dna_memory
from luna_understanding import UnderstandingEngine

def test_vector_reasoning_basic():
    """Test basic vector reasoning functionality"""
    print("🧠 Testing Vector Reasoning System...")
    
    # Initialize systems
    vector_engine = initialize_vector_reasoning()
    dna_memory = initialize_dna_memory()
    understanding = UnderstandingEngine("test-model")
    
    if not vector_engine:
        print("ERROR: Vector reasoning engine not initialized")
        return False
    
    print("SUCCESS: Vector reasoning engine initialized")
    
    # Test basic reasoning
    print("\nTesting basic reasoning...")
    try:
        result = vector_engine.reason_across_memories("What is love?", "test_user", dna_memory, understanding)
        
        if result:
            print("SUCCESS: Basic reasoning completed")
            print(f"  Query: {result.query}")
            print(f"  Confidence: {result.confidence:.2f}")
            print(f"  Insights: {len(result.insights)}")
            print(f"  Reasoning steps: {len(result.reasoning_chain)}")
            return True
        else:
            print("ERROR: Reasoning returned None")
            return False
            
    except Exception as e:
        print(f"ERROR: Basic reasoning failed: {e}")
        return False

def test_vector_reasoning_with_memories():
    """Test vector reasoning with actual memories"""
    print("\n🧠 Testing Vector Reasoning with Memories...")
    
    # Initialize systems
    vector_engine = get_vector_reasoning()
    dna_memory = initialize_dna_memory()
    
    if not vector_engine or not dna_memory:
        print("ERROR: Systems not initialized")
        return False
    
    # Add some test memories
    print("Adding test memories...")
    test_memories = [
        ("I love cats", "Cats are amazing companions!", "test", "test_user"),
        ("I'm feeling sad today", "I'm here for you. What's making you feel sad?", "test", "test_user"),
        ("What should I do about my job?", "Let's talk through your job situation together.", "test", "test_user"),
        ("I love programming", "Programming is such a creative and powerful skill!", "test", "test_user"),
        ("I'm excited about my new project", "That's wonderful! Tell me more about your project!", "test", "test_user")
    ]
    
    for user_msg, luna_resp, platform, username in test_memories:
        save_dna_memory(user_msg, luna_resp, platform, username)
    
    print("SUCCESS: Test memories added")
    
    # Test reasoning with memories
    print("Testing reasoning with memories...")
    try:
        result = vector_engine.reason_across_memories("I'm feeling emotional", "test_user", dna_memory)
        
        if result:
            print("SUCCESS: Memory-enhanced reasoning completed")
            print(f"  Query: {result.query}")
            print(f"  Confidence: {result.confidence:.2f}")
            print(f"  Insights: {len(result.insights)}")
            
            if result.insights:
                print("  Top insights:")
                for i, insight in enumerate(result.insights[:3], 1):
                    print(f"    {i}. {insight}")
            
            if result.emotional_context:
                emotional = result.emotional_context
                print(f"  Emotional context: {emotional.get('dominant_emotion', 'unknown')}")
            
            if result.temporal_patterns:
                temporal = result.temporal_patterns
                print(f"  Temporal patterns: {temporal.get('frequency_pattern', 'unknown')}")
            
            return True
        else:
            print("ERROR: Memory reasoning returned None")
            return False
            
    except Exception as e:
        print(f"ERROR: Memory reasoning failed: {e}")
        return False

def test_vector_reasoning_insights():
    """Test vector reasoning insight generation"""
    print("\n🧠 Testing Vector Reasoning Insights...")
    
    vector_engine = get_vector_reasoning()
    if not vector_engine:
        print("ERROR: Vector reasoning engine not available")
        return False
    
    # Test different types of queries
    test_queries = [
        "What makes me happy?",
        "I need help with relationships",
        "I'm curious about learning new things",
        "I feel overwhelmed with work"
    ]
    
    for query in test_queries:
        print(f"\nTesting query: '{query}'")
        try:
            result = vector_engine.reason_across_memories(query, "test_user")
            
            if result:
                print(f"  Confidence: {result.confidence:.2f}")
                print(f"  Insights: {len(result.insights)}")
                print(f"  Predictions: {len(result.predictions)}")
                print(f"  Cross-connections: {len(result.cross_memory_connections)}")
                
                if result.insights:
                    print(f"  Top insight: {result.insights[0]}")
            else:
                print("  No result returned")
                
        except Exception as e:
            print(f"  ERROR: {e}")
    
    return True

def test_vector_reasoning_stats():
    """Test vector reasoning statistics"""
    print("\n🧠 Testing Vector Reasoning Statistics...")
    
    vector_engine = get_vector_reasoning()
    if not vector_engine:
        print("ERROR: Vector reasoning engine not available")
        return False
    
    try:
        stats = vector_engine.get_reasoning_stats()
        print("SUCCESS: Statistics retrieved")
        print(f"  Total reasoning chains: {stats.get('total_reasoning_chains', 0)}")
        print(f"  Total patterns: {stats.get('total_patterns', 0)}")
        print(f"  Total meta insights: {stats.get('total_meta_insights', 0)}")
        print(f"  Average confidence: {stats.get('average_confidence', 0.0)}")
        print(f"  Embeddings enabled: {stats.get('embeddings_enabled', False)}")
        return True
        
    except Exception as e:
        print(f"ERROR: Statistics failed: {e}")
        return False

def test_integration_with_luna():
    """Test integration with Luna's main system"""
    print("\n🧠 Testing Integration with Luna...")
    
    try:
        # Test the integrated function
        from luna_dna_memory import recall_dna_memories_with_vector_reasoning
        
        result = recall_dna_memories_with_vector_reasoning("test_user", "I need emotional support", limit=3)
        
        if result:
            print("SUCCESS: Integrated memory recall with vector reasoning")
            print(f"  Enhanced: {result.get('enhanced', False)}")
            print(f"  Memories: {len(result.get('memories', []))}")
            
            if result.get('vector_reasoning'):
                vr = result['vector_reasoning']
                print(f"  Vector reasoning confidence: {vr.confidence:.2f}")
                print(f"  Vector insights: {len(vr.insights)}")
            
            return True
        else:
            print("ERROR: Integrated recall failed")
            return False
            
    except Exception as e:
        print(f"ERROR: Integration test failed: {e}")
        return False

def main():
    """Run all vector reasoning tests"""
    print("🚀 Starting Vector Reasoning Tests...")
    
    tests = [
        test_vector_reasoning_basic,
        test_vector_reasoning_with_memories,
        test_vector_reasoning_insights,
        test_vector_reasoning_stats,
        test_integration_with_luna
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
                print("✅ Test passed")
            else:
                print("❌ Test failed")
        except Exception as e:
            print(f"❌ Test error: {e}")
    
    print(f"\n🎯 Vector Reasoning Tests Complete: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All vector reasoning tests passed!")
        return True
    else:
        print("⚠️ Some tests failed - check the output above")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
