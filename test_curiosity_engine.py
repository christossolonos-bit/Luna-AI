#!/usr/bin/env python3
"""
Test script for Luna's Curiosity Engine
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from luna_curiosity_engine import (
    initialize_curiosity_engine, get_curiosity_engine, run_curiosity_cycle,
    LunaCuriosityEngine, CuriosityTarget, CuriosityExploration
)
from luna_dna_memory import initialize_dna_memory, save_dna_memory
from luna_understanding import UnderstandingEngine

def test_curiosity_engine_basic():
    """Test basic curiosity engine functionality"""
    print("🔍 Testing Curiosity Engine...")
    
    # Initialize systems
    curiosity_engine = initialize_curiosity_engine()
    dna_memory = initialize_dna_memory()
    understanding = UnderstandingEngine("test-model")
    
    if not curiosity_engine:
        print("ERROR: Curiosity engine not initialized")
        return False
    
    print("SUCCESS: Curiosity engine initialized")
    
    # Test knowledge gap identification
    print("\nTesting knowledge gap identification...")
    try:
        targets = curiosity_engine.identify_knowledge_gaps(dna_memory, understanding)
        
        if targets:
            print(f"SUCCESS: Found {len(targets)} curiosity targets")
            for i, target in enumerate(targets[:3], 1):
                print(f"  Target {i}: {target.topic}")
                print(f"    Curiosity score: {target.curiosity_score:.2f}")
                print(f"    Strategy: {target.exploration_strategy}")
            return True
        else:
            print("WARNING: No curiosity targets found")
            return True
            
    except Exception as e:
        print(f"ERROR: Knowledge gap identification failed: {e}")
        return False

def test_curiosity_engine_with_memories():
    """Test curiosity engine with actual memories"""
    print("\n🔍 Testing Curiosity Engine with Memories...")
    
    # Initialize systems
    curiosity_engine = get_curiosity_engine()
    dna_memory = initialize_dna_memory()
    
    if not curiosity_engine or not dna_memory:
        print("ERROR: Systems not initialized")
        return False
    
    # Add some test memories to trigger curiosity
    print("Adding test memories...")
    test_memories = [
        ("I love learning about psychology", "Psychology is fascinating! What aspects interest you most?", "test", "test_user"),
        ("I'm curious about artificial intelligence", "AI is such an exciting field! What would you like to know?", "test", "test_user"),
        ("I wonder about the nature of consciousness", "Consciousness is one of the deepest mysteries! What are your thoughts?", "test", "test_user"),
        ("I'm interested in creativity and art", "Creativity is so beautiful! Tell me about your artistic interests.", "test", "test_user"),
        ("I love exploring new ideas", "Exploring ideas is wonderful! What new concepts are you discovering?", "test", "test_user")
    ]
    
    for user_msg, luna_resp, platform, username in test_memories:
        save_dna_memory(user_msg, luna_resp, platform, username)
    
    print("SUCCESS: Test memories added")
    
    # Test curiosity cycle
    print("Testing curiosity cycle...")
    try:
        explorations = curiosity_engine.run_curiosity_cycle(dna_memory)
        
        if explorations:
            print(f"SUCCESS: Curiosity cycle completed with {len(explorations)} explorations")
            
            for i, exploration in enumerate(explorations, 1):
                print(f"\nExploration {i}:")
                print(f"  Target: {exploration.target.topic}")
                print(f"  Questions: {len(exploration.questions_generated)}")
                print(f"  Insights: {len(exploration.insights_discovered)}")
                print(f"  Confidence: {exploration.exploration_confidence:.2f}")
                print(f"  Learning value: {exploration.learning_value:.2f}")
                
                if exploration.insights_discovered:
                    print("  Top insights:")
                    for j, insight in enumerate(exploration.insights_discovered[:2], 1):
                        print(f"    {j}. {insight[:80]}...")
            
            return True
        else:
            print("WARNING: No explorations completed")
            return True
            
    except Exception as e:
        print(f"ERROR: Curiosity cycle failed: {e}")
        return False

def test_curiosity_question_generation():
    """Test curiosity question generation"""
    print("\n🔍 Testing Question Generation...")
    
    curiosity_engine = get_curiosity_engine()
    if not curiosity_engine:
        print("ERROR: Curiosity engine not available")
        return False
    
    # Test different types of targets
    test_targets = [
        CuriosityTarget(
            topic="artificial intelligence",
            curiosity_score=0.8,
            knowledge_gap_size=0.6,
            exploration_priority=0.7,
            related_concepts=["machine learning", "neural networks"],
            exploration_strategy="semantic",
            generated_questions=[],
            exploration_depth=0
        ),
        CuriosityTarget(
            topic="human emotions",
            curiosity_score=0.9,
            knowledge_gap_size=0.7,
            exploration_priority=0.8,
            related_concepts=["psychology", "feelings"],
            exploration_strategy="emotional",
            generated_questions=[],
            exploration_depth=0
        )
    ]
    
    for target in test_targets:
        print(f"\nTesting target: {target.topic}")
        try:
            questions = curiosity_engine.generate_curiosity_questions(target)
            
            if questions:
                print(f"SUCCESS: Generated {len(questions)} questions")
                for i, question in enumerate(questions[:3], 1):
                    print(f"  {i}. {question}")
            else:
                print("WARNING: No questions generated")
                
        except Exception as e:
            print(f"ERROR: Question generation failed: {e}")
            return False
    
    return True

def test_curiosity_autonomous_exploration():
    """Test autonomous exploration"""
    print("\n🔍 Testing Autonomous Exploration...")
    
    curiosity_engine = get_curiosity_engine()
    dna_memory = initialize_dna_memory()
    understanding = UnderstandingEngine("test-model")
    
    if not curiosity_engine:
        print("ERROR: Curiosity engine not available")
        return False
    
    # Create a test target
    target = CuriosityTarget(
        topic="the nature of learning",
        curiosity_score=0.8,
        knowledge_gap_size=0.6,
        exploration_priority=0.7,
        related_concepts=["education", "growth", "development"],
        exploration_strategy="semantic",
        generated_questions=[],
        exploration_depth=0
    )
    
    try:
        exploration = curiosity_engine.run_autonomous_exploration(
            target, dna_memory, understanding
        )
        
        if exploration:
            print("SUCCESS: Autonomous exploration completed")
            print(f"  Questions generated: {len(exploration.questions_generated)}")
            print(f"  Insights discovered: {len(exploration.insights_discovered)}")
            print(f"  New connections: {len(exploration.new_connections)}")
            print(f"  Follow-up targets: {len(exploration.follow_up_targets)}")
            print(f"  Exploration confidence: {exploration.exploration_confidence:.2f}")
            print(f"  Learning value: {exploration.learning_value:.2f}")
            
            if exploration.insights_discovered:
                print("  Top insights:")
                for i, insight in enumerate(exploration.insights_discovered[:2], 1):
                    print(f"    {i}. {insight[:80]}...")
            
            return True
        else:
            print("WARNING: No exploration result")
            return True
            
    except Exception as e:
        print(f"ERROR: Autonomous exploration failed: {e}")
        return False

def test_curiosity_stats():
    """Test curiosity statistics"""
    print("\n🔍 Testing Curiosity Statistics...")
    
    curiosity_engine = get_curiosity_engine()
    if not curiosity_engine:
        print("ERROR: Curiosity engine not available")
        return False
    
    try:
        stats = curiosity_engine.get_curiosity_stats()
        print("SUCCESS: Statistics retrieved")
        print(f"  Total targets: {stats.get('total_targets', 0)}")
        print(f"  Total explorations: {stats.get('total_explorations', 0)}")
        print(f"  Total discoveries: {stats.get('total_discoveries', 0)}")
        print(f"  Average learning value: {stats.get('average_learning_value', 0.0):.3f}")
        print(f"  Curiosity level: {stats.get('curiosity_level', 0.0):.2f}")
        print(f"  Exploration energy: {stats.get('exploration_energy', 0.0):.2f}")
        print(f"  Learning momentum: {stats.get('learning_momentum', 0.0):.2f}")
        print(f"  Embeddings enabled: {stats.get('embeddings_enabled', False)}")
        return True
        
    except Exception as e:
        print(f"ERROR: Statistics failed: {e}")
        return False

def main():
    """Run all curiosity engine tests"""
    print("🚀 Starting Curiosity Engine Tests...")
    
    tests = [
        test_curiosity_engine_basic,
        test_curiosity_engine_with_memories,
        test_curiosity_question_generation,
        test_curiosity_autonomous_exploration,
        test_curiosity_stats
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
    
    print(f"\n🎯 Curiosity Engine Tests Complete: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All curiosity engine tests passed!")
        return True
    else:
        print("⚠️ Some tests failed - check the output above")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
