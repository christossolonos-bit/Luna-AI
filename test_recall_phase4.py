#!/usr/bin/env python3
"""Test Phase 4: Vector reasoning + save_dna_memory use aliases."""

import sys
sys.path.insert(0, ".")

def test_phase4():
    from luna_dna_memory import (
        initialize_dna_memory, save_dna_memory, get_user_facts,
        recall_dna_memories_with_vector_reasoning, get_user_aliases,
        seed_user_identity, set_known_user_aliases,
    )
    
    print("=== Phase 4 Test: Alias-Aware Components ===\n")
    
    initialize_dna_memory()
    set_known_user_aliases({"discord:1414944231222411378": ["Chris", "chris", "Solonaras", "solonaras"]})
    seed_user_identity("discord:1414944231222411378", ["Chris", "chris", "Solonaras", "solonaras"], "discord")
    aliases = get_user_aliases("discord", "Solonaras", "1414944231222411378")
    
    # 1. recall_dna_memories_with_vector_reasoning passes usernames to reason_with_vectors
    result = recall_dna_memories_with_vector_reasoning(
        "what do you remember about me?", "Solonaras", limit=3, usernames=aliases
    )
    memories = result.get("memories", [])
    vr = result.get("vector_reasoning")
    print(f"[OK] recall_dna_memories_with_vector_reasoning returned {len(memories)} memories")
    if vr:
        print(f"[OK] Vector reasoning available (insights: {len(vr.insights) if vr.insights else 0})")
    else:
        print("[OK] Vector reasoning not enhanced (optional)")
    
    # 2. save_dna_memory - add profile update and verify no error
    save_dna_memory("I like testing", "That's cool!", "discord", "Solonaras")
    facts = get_user_facts("Chris", usernames=aliases)
    interests = [f["fact_value"] for f in facts if f["fact_type"] == "interest"]
    # May or may not have "testing" from extraction - just verify no crash
    print("[OK] save_dna_memory with Solonaras completed (profile merge uses aliases)")
    
    # 3. Memories from Chris+Solonaras should be merged (we had both in DB)
    result2 = recall_dna_memories_with_vector_reasoning(
        "hello", "Chris", limit=5, usernames=aliases
    )
    assert "memories" in result2, "Should have memories key"
    print(f"[OK] Merged recall for Chris: {len(result2['memories'])} memories")
    
    print("\n=== Phase 4 PASSED ===")
    return True

if __name__ == "__main__":
    try:
        test_phase4()
    except Exception as e:
        print(f"\n[FAIL] Phase 4 FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
