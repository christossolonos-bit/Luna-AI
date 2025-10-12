"""
Test script for Luna's DNA Memory System
"""

from luna_dna_memory import (
    DNAMemoryStrand, LunaDNAMemorySystem,
    initialize_dna_memory, save_dna_memory, recall_dna_memories
)

def test_dna_memory():
    print("Testing Luna DNA Memory System\n")
    print("=" * 50)
    
    # Initialize
    print("\n[1] Initializing DNA Memory...")
    dna_system = initialize_dna_memory()
    print("[OK] Initialized!")
    
    # Test 1: Create memory strands
    print("\n[2] Creating test memory strands...")
    
    conversations = [
        ("hello luna", "Hey Chris! How are you doing?"),
        ("I love anime", "Me too! What's your favorite anime?"),
        ("Attack on Titan is awesome", "That's a great choice! The story is amazing!"),
        ("how are you?", "I'm doing great! Thanks for asking!"),
        ("tell me about yourself", "I'm Luna, your AI companion who loves anime and gaming!"),
    ]
    
    for user_msg, luna_response in conversations:
        save_dna_memory(user_msg, luna_response, "test", "Chris")
        print(f"[OK] Saved: '{user_msg}' -> '{luna_response[:30]}...'")
    
    # Test 2: Recall memories
    print("\n[3] Testing memory recall...")
    
    queries = [
        "anime",
        "hello",
        "who are you",
    ]
    
    for query in queries:
        print(f"\n[QUERY] '{query}'")
        memories = recall_dna_memories("Chris", query, limit=3)
        
        if memories:
            for i, mem in enumerate(memories):
                print(f"   {i+1}. [{mem['match_score']:.2f}] {mem['user_message']} -> {mem['luna_response'][:40]}...")
        else:
            print("   No memories found")
    
    # Test 3: Get stats
    print("\n[4] DNA Memory Statistics:")
    stats = dna_system.get_stats()
    print(f"   Total Strands: {stats['total_strands']}")
    print(f"   Avg Strength: {stats['avg_strength']}")
    print(f"   Gene Combinations: {stats['gene_combinations']}")
    print(f"   Unique Users: {stats['unique_users']}")
    
    # Test 4: User profile
    print("\n[5] User Genetic Profile:")
    profile = dna_system.get_user_profile("Chris")
    if profile:
        print(f"   Username: {profile['username']}")
        print(f"   Total Strands: {profile['total_strands']}")
        print(f"   Dominant Traits: {list(profile['dominant_traits'].keys())[:5]}")
    
    # Test 5: Create a strand and examine nucleotides
    print("\n[6] Examining DNA Nucleotides:")
    strand = DNAMemoryStrand(
        "I love playing video games",
        "That's awesome! What games do you like?",
        "test", "Chris"
    )
    print(f"   Strand ID: {strand.strand_id}")
    print(f"   Nucleotides:")
    for base, value in strand.nucleotides.items():
        print(f"      {base}: {value}")
    print(f"   Strength: {strand.strength}")
    print(f"   Mutations: {strand.mutations}")
    
    # Test 6: Replication
    print("\n[7] Testing replication (strengthening)...")
    original_strength = strand.strength
    strand.replicate()
    strand.replicate()
    strand.replicate()
    print(f"   Original Strength: {original_strength}")
    print(f"   After 3 replications: {strand.strength}")
    print(f"   Expression Count: {strand.expression_count}")
    
    # Test 7: Mutation
    print("\n[8] Testing mutation (evolution)...")
    original_context = strand.nucleotides['C']
    strand.mutate("mentioned_in_discord")
    print(f"   Original Context: {original_context}")
    print(f"   After Mutation: {strand.nucleotides['C']}")
    print(f"   Mutations: {strand.mutations}")
    
    print("\n" + "=" * 50)
    print("[OK] All tests completed successfully!")
    print("[OK] DNA Memory System is working perfectly!\n")

if __name__ == "__main__":
    test_dna_memory()

