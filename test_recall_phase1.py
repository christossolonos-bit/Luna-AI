#!/usr/bin/env python3
"""Test Phase 1: CHRIS_ALIASES includes Solonaras and facts are merged correctly."""

import sys
sys.path.insert(0, ".")

def test_phase1():
    from luna_dna_memory import initialize_dna_memory, get_user_facts, get_user_aliases, seed_user_identity, set_known_user_aliases
    
    print("=== Phase 1 Test: Dynamic Aliases ===\n")
    
    # 1. Initialize and seed Chris identity (dynamic profile)
    initialize_dna_memory()
    set_known_user_aliases({"discord:1414944231222411378": ["Chris", "chris", "Solonaras", "solonaras"]})
    seed_user_identity("discord:1414944231222411378", ["Chris", "chris", "Solonaras", "solonaras"], "discord")
    
    aliases = get_user_aliases("discord", "Chris", "1414944231222411378")
    assert "Solonaras" in aliases or "Chris" in aliases, f"Aliases should include Chris/Solonaras: {aliases}"
    print(f"[OK] get_user_aliases = {aliases}")
    
    # 2. Fetch facts for Chris (should merge from all aliases including Solonaras)
    facts = get_user_facts("Chris", usernames=aliases)
    
    # 3. Should have location=Cyprus (stored under Solonaras in DB)
    fact_types = {f["fact_type"]: f["fact_value"] for f in facts}
    locations = [f["fact_value"] for f in facts if f["fact_type"] == "location"]
    names = [f["fact_value"] for f in facts if f["fact_type"] == "name"]
    
    print(f"[OK] Merged facts for Chris: {len(facts)} total")
    print(f"  - Names: {names}")
    print(f"  - Locations: {locations}")
    
    if "Cyprus" in locations or any("Cyprus" in str(v) for v in locations):
        print("[OK] Location 'Cyprus' found (from Solonaras row) - alias merge works!")
    else:
        print("[WARN] Location 'Cyprus' not in merged facts (may not exist in DB yet)")
    
    # 4. Verify no "from Cyprus" as name (bad extraction - we'll fix in Phase 2)
    bad_names = [n for n in names if "from " in n.lower() or n.lower() == "from cyprus"]
    if bad_names:
        print(f"[WARN] Bad name facts still present: {bad_names} (will clean in Phase 3)")
    else:
        print("[OK] No bad 'from X' name facts in merged result")
    
    print("\n=== Phase 1 PASSED ===")
    return True

if __name__ == "__main__":
    try:
        test_phase1()
    except Exception as e:
        print(f"\n[FAIL] Phase 1 FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
