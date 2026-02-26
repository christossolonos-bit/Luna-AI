#!/usr/bin/env python3
"""Test Phase 2: Fact extraction - 'I'm from X' should NOT be stored as name."""

import sys
sys.path.insert(0, ".")

def test_phase2():
    from luna_dna_memory import _extract_facts_from_message
    
    print("=== Phase 2 Test: Name vs Location Extraction ===\n")
    
    # 1. "I'm from Cyprus" -> location=Cyprus, NOT name=from Cyprus
    facts = _extract_facts_from_message("I'm from Cyprus")
    names = [f[1] for f in facts if f[0] == "name"]
    locations = [f[1] for f in facts if f[0] == "location"]
    
    assert "from Cyprus" not in names, f"BAD: 'from Cyprus' extracted as name: {facts}"
    assert "Cyprus" in locations, f"Expected location=Cyprus, got: {facts}"
    print("[OK] 'I'm from Cyprus' -> location=Cyprus, no name=from Cyprus")
    
    # 2. "I'm from Alabama" -> location only
    facts = _extract_facts_from_message("I'm from Alabama")
    names = [f[1] for f in facts if f[0] == "name"]
    assert "from Alabama" not in names, f"BAD: 'from Alabama' as name: {facts}"
    print("[OK] 'I'm from Alabama' -> location only")
    
    # 3. "I'm Chris" -> name=Chris
    facts = _extract_facts_from_message("I'm Chris")
    names = [f[1] for f in facts if f[0] == "name"]
    assert "Chris" in names, f"Expected name=Chris, got: {facts}"
    print("[OK] 'I'm Chris' -> name=Chris")
    
    # 4. "I live in New York" -> location only (no name)
    facts = _extract_facts_from_message("I live in New York")
    names = [f[1] for f in facts if f[0] == "name"]
    locations = [f[1] for f in facts if f[0] == "location"]
    assert "in New York" not in names, f"BAD: 'in New York' as name: {facts}"
    assert "New York" in locations, f"Expected location, got: {facts}"
    print("[OK] 'I live in New York' -> location=New York")
    
    # 5. "I'm in Tokyo" -> location only
    facts = _extract_facts_from_message("I'm in Tokyo")
    names = [f[1] for f in facts if f[0] == "name"]
    assert "in Tokyo" not in names, f"BAD: 'in Tokyo' as name: {facts}"
    print("[OK] 'I'm in Tokyo' -> location only")
    
    # 6. "my name is Chris" still works
    facts = _extract_facts_from_message("my name is Chris")
    names = [f[1] for f in facts if f[0] == "name"]
    assert "Chris" in names, f"Expected name=Chris, got: {facts}"
    print("[OK] 'my name is Chris' -> name=Chris")
    
    print("\n=== Phase 2 PASSED ===")
    return True

if __name__ == "__main__":
    try:
        test_phase2()
    except Exception as e:
        print(f"\n[FAIL] Phase 2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
