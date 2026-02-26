#!/usr/bin/env python3
"""Test Phase 3: Bad facts removed from DB, merge still works."""

import sys
sys.path.insert(0, ".")

def test_phase3():
    from luna_dna_memory import initialize_dna_memory, get_user_facts, get_user_aliases
    
    print("=== Phase 3 Test: Bad Facts Cleaned ===\n")
    
    initialize_dna_memory()
    aliases = get_user_aliases("discord", "Chris", "1414944231222411378")
    facts = get_user_facts("Chris", usernames=aliases)
    
    names = [f["fact_value"] for f in facts if f["fact_type"] == "name"]
    locations = [f["fact_value"] for f in facts if f["fact_type"] == "location"]
    
    # No "from Cyprus" or "from X" as name
    bad_names = [n for n in names if n.lower().startswith("from ") or n.lower().startswith("in ")]
    assert not bad_names, f"Bad names still present: {bad_names}"
    print("[OK] No bad 'from X' / 'in X' name facts in DB")
    
    # Chris name and Cyprus location still present
    assert "Chris" in names, f"Expected name=Chris, got: {names}"
    assert "Cyprus" in locations, f"Expected location=Cyprus, got: {locations}"
    print("[OK] Chris name and Cyprus location preserved")
    
    print("\n=== Phase 3 PASSED ===")
    return True

if __name__ == "__main__":
    try:
        test_phase3()
    except Exception as e:
        print(f"\n[FAIL] Phase 3 FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
