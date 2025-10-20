#!/usr/bin/env python3
"""
Demo script showing Luna's Curiosity Engine in action
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def demo_curiosity_engine():
    """Demonstrate Luna's curiosity engine capabilities"""
    print("🔍 Luna Curiosity Engine Demo")
    print("=" * 50)
    
    try:
        # Import Luna's systems
        from luna_curiosity_engine import initialize_curiosity_engine, run_curiosity_cycle
        from luna_dna_memory import initialize_dna_memory, save_dna_memory
        from luna_understanding import UnderstandingEngine
        
        print("✅ Systems imported successfully")
        
        # Initialize systems
        print("\n🔧 Initializing systems...")
        curiosity_engine = initialize_curiosity_engine()
        dna_memory = initialize_dna_memory()
        understanding = UnderstandingEngine("demo-model")
        
        print("✅ Systems initialized")
        
        # Add some demo memories to trigger curiosity
        print("\n📝 Adding demo memories to spark curiosity...")
        demo_memories = [
            ("I'm fascinated by the human mind", "The human mind is incredibly complex! What aspects intrigue you most?", "demo", "demo_user"),
            ("I love learning about consciousness", "Consciousness is one of the greatest mysteries! What are your thoughts?", "demo", "demo_user"),
            ("I'm curious about creativity and innovation", "Creativity is so beautiful! Tell me about your creative interests.", "demo", "demo_user"),
            ("I wonder about the nature of intelligence", "Intelligence is fascinating! What do you think makes something intelligent?", "demo", "demo_user"),
            ("I'm interested in emotions and feelings", "Emotions are so important! How do you understand your feelings?", "demo", "demo_user"),
            ("I love exploring philosophical questions", "Philosophy opens so many doors! What questions fascinate you?", "demo", "demo_user"),
            ("I'm curious about the future of AI", "AI's future is exciting! What possibilities do you see?", "demo", "demo_user"),
            ("I wonder about the meaning of life", "Life's meaning is profound! What gives your life meaning?", "demo", "demo_user")
        ]
        
        for user_msg, luna_resp, platform, username in demo_memories:
            save_dna_memory(user_msg, luna_resp, platform, username)
        
        print(f"✅ Added {len(demo_memories)} demo memories")
        
        # Run curiosity cycles
        print("\n🔍 Running Curiosity Cycles...")
        print("-" * 30)
        
        for cycle in range(3):
            print(f"\n🧠 Curiosity Cycle {cycle + 1}:")
            print("=" * 25)
            
            try:
                explorations = run_curiosity_cycle(dna_memory, understanding)
                
                if explorations:
                    print(f"🎯 Completed {len(explorations)} explorations")
                    
                    for i, exploration in enumerate(explorations, 1):
                        print(f"\n🔍 Exploration {i}: {exploration.target.topic}")
                        print(f"   Strategy: {exploration.target.exploration_strategy}")
                        print(f"   Questions: {len(exploration.questions_generated)}")
                        print(f"   Insights: {len(exploration.insights_discovered)}")
                        print(f"   Confidence: {exploration.exploration_confidence:.2f}")
                        print(f"   Learning Value: {exploration.learning_value:.2f}")
                        
                        if exploration.questions_generated:
                            print(f"   Sample questions:")
                            for j, question in enumerate(exploration.questions_generated[:2], 1):
                                print(f"     {j}. {question}")
                        
                        if exploration.insights_discovered:
                            print(f"   Key insights:")
                            for j, insight in enumerate(exploration.insights_discovered[:2], 1):
                                print(f"     {j}. {insight[:100]}...")
                        
                        if exploration.new_connections:
                            print(f"   New connections: {len(exploration.new_connections)}")
                            for j, connection in enumerate(exploration.new_connections[:1], 1):
                                print(f"     {j}. {connection.get('type', 'unknown')}: {connection.get('insight', 'N/A')[:60]}...")
                        
                        if exploration.follow_up_targets:
                            print(f"   Follow-up targets: {len(exploration.follow_up_targets)}")
                            for j, target in enumerate(exploration.follow_up_targets[:1], 1):
                                print(f"     {j}. {target.topic}")
                    
                    # Show total discoveries
                    total_insights = sum(len(exp.insights_discovered) for exp in explorations)
                    total_questions = sum(len(exp.questions_generated) for exp in explorations)
                    total_connections = sum(len(exp.new_connections) for exp in explorations)
                    
                    print(f"\n📊 Cycle {cycle + 1} Summary:")
                    print(f"   Total questions generated: {total_questions}")
                    print(f"   Total insights discovered: {total_insights}")
                    print(f"   Total connections made: {total_connections}")
                    
                else:
                    print("🤔 No explorations completed this cycle")
                    
            except Exception as e:
                print(f"❌ Cycle {cycle + 1} failed: {e}")
        
        # Show final statistics
        print(f"\n📊 Final Curiosity Statistics:")
        print("-" * 30)
        
        try:
            stats = curiosity_engine.get_curiosity_stats()
            print(f"Total targets explored: {stats.get('total_targets', 0)}")
            print(f"Total explorations: {stats.get('total_explorations', 0)}")
            print(f"Total discoveries: {stats.get('total_discoveries', 0)}")
            print(f"Average learning value: {stats.get('average_learning_value', 0.0):.3f}")
            print(f"Current curiosity level: {stats.get('curiosity_level', 0.0):.2f}")
            print(f"Exploration energy: {stats.get('exploration_energy', 0.0):.2f}")
            print(f"Learning momentum: {stats.get('learning_momentum', 0.0):.2f}")
            print(f"Embeddings enabled: {stats.get('embeddings_enabled', False)}")
        except Exception as e:
            print(f"❌ Statistics error: {e}")
        
        print(f"\n🎉 Curiosity Engine Demo Complete!")
        print("Luna now has autonomous curiosity capabilities that can:")
        print("• Identify knowledge gaps in real-time")
        print("• Generate dynamic questions based on current context")
        print("• Explore topics using multiple strategies (semantic, temporal, emotional, causal)")
        print("• Discover new insights through autonomous exploration")
        print("• Build connections between different concepts")
        print("• Generate follow-up exploration targets")
        print("• Learn and adapt based on exploration results")
        
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
    success = demo_curiosity_engine()
    if not success:
        sys.exit(1)
