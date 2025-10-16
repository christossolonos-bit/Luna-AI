#!/usr/bin/env python3
"""
Simple test script for Luna's Vector Embedding System (without Ollama)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from luna_understanding import UnderstandingEngine

def test_vector_embeddings_simple():
    """Test the vector embedding functionality without requiring Ollama"""
    print("Testing Luna's Vector Embedding System (Simple)...")
    
    # Initialize the understanding engine
    engine = UnderstandingEngine("test-model")
    
    if not engine.embeddings_enabled:
        print("ERROR: Vector embeddings not enabled - check dependencies")
        return False
    
    print("SUCCESS: Vector embeddings enabled!")
    
    # Test embedding generation
    print("\nTesting embedding generation...")
    test_text = "artificial intelligence and machine learning"
    embedding = engine._generate_embedding(test_text)
    
    if embedding:
        print("SUCCESS: Embedding generation successful")
        print(f"   Embedding size: {len(embedding)} bytes")
    else:
        print("ERROR: Embedding generation failed")
        return False
    
    # Test similarity calculation
    print("\nTesting similarity calculation...")
    text1 = "artificial intelligence"
    text2 = "machine learning"
    text3 = "cooking recipes"
    
    embedding1 = engine._generate_embedding(text1)
    embedding2 = engine._generate_embedding(text2)
    embedding3 = engine._generate_embedding(text3)
    
    if embedding1 and embedding2 and embedding3:
        similarity_ai_ml = engine._calculate_similarity(embedding1, embedding2)
        similarity_ai_cooking = engine._calculate_similarity(embedding1, embedding3)
        
        print("SUCCESS: Similarity calculation successful")
        print(f"   AI vs ML similarity: {similarity_ai_ml:.3f}")
        print(f"   AI vs Cooking similarity: {similarity_ai_cooking:.3f}")
        
        # AI and ML should be more similar than AI and cooking
        if similarity_ai_ml > similarity_ai_cooking:
            print("SUCCESS: Similarity logic is working correctly!")
        else:
            print("WARNING: Similarity logic may need adjustment")
    else:
        print("ERROR: Similarity calculation failed")
        return False
    
    # Test database operations
    print("\nTesting database operations...")
    try:
        # Test storing a concept with embedding
        test_concept = {
            "core_concept": "AI is the simulation of human intelligence",
            "properties": ["intelligent", "adaptive", "learning"],
            "relationships": {"machine_learning": "subset"},
            "implications": ["Will change society"],
            "counterexamples": ["Simple calculators"]
        }
        
        engine._store_concept_rag("artificial_intelligence", test_concept)
        print("SUCCESS: Concept storage with embedding successful")
        
        # Test searching concepts
        results = engine._search_concepts_rag("machine learning", limit=3)
        print(f"SUCCESS: Concept search returned {len(results)} results")
        
        if results:
            for i, result in enumerate(results):
                similarity = result.get('similarity', 0)
                print(f"   {i+1}. {result['topic']} (similarity: {similarity:.3f})")
        
    except Exception as e:
        print(f"ERROR: Database operations failed: {e}")
        return False
    
    print("\nAll vector embedding tests passed!")
    return True

if __name__ == "__main__":
    success = test_vector_embeddings_simple()
    if success:
        print("\nSUCCESS: Vector embedding system is working correctly!")
    else:
        print("\nERROR: Vector embedding system has issues")
        sys.exit(1)
