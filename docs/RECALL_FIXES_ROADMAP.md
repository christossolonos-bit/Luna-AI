# Recall Inconsistency Fixes — Roadmap

## Overview

Five fixes to resolve Luna's recall inconsistencies (user mixing, wrong facts, missing memories). Ordered by dependency and impact.

---

## Phase 1: Foundation (Quick Wins)

### Fix 1.1 — Add `"Solonaras"` to alias lists

**What:** Extend Chris aliases from `["Chris", "chris", "solonaras"]` to `["Chris", "chris", "Solonaras", "solonaras"]`.

**Files:**
- `luna_clean.py` — `memory_usernames`, `profile_usernames`, VC curious gaps, `_get_global_context`
- `luna_memory_search.py` — `KNOWN_USER_ALIASES["chris"]`, `KNOWN_USER_ALIASES["solonaras"]`
- Any other hardcoded `["Chris", "chris", "solonaras"]` lists

**Effort:** ~15 min  
**Risk:** Low  
**Blocks:** Nothing

---

### Fix 1.2 — Centralize alias definition

**What:** Define a single constant (e.g. `CHRIS_ALIASES`) and reuse it everywhere instead of duplicating lists.

**Files:**
- New: `luna_config.py` or add to `luna_dna_memory.py`
- Update all call sites to import and use the constant

**Effort:** ~20 min  
**Risk:** Low  
**Blocks:** Nothing (can be done with 1.1)

---

## Phase 2: Stop Bad Data at Source

### Fix 2.1 — Fix fact extraction (name vs location)

**What:** Prevent `"I'm from X"` from being stored as `name="from X"`.

**Approach options:**
- **A:** Run location extraction first; skip name extraction if the match would be `"from X"` or `"in X"`.
- **B:** Add negative lookahead to name regex: exclude matches starting with `from ` or `in `.
- **C:** Add a post-filter: drop any `name` fact that looks like a location phrase (e.g. starts with "from", "in", contains a known country/city).

**Files:** `luna_dna_memory.py` — `_extract_facts_from_message`

**Effort:** ~30 min  
**Risk:** Low (add tests for "I'm from Cyprus", "I'm Chris", "my name is X")  
**Blocks:** Nothing

---

## Phase 3: Data Cleanup

### Fix 3.1 — Remove/correct bad facts in DB

**What:** One-time cleanup of existing bad rows.

**Examples:**
- Delete `Solonaras|name|from Cyprus`
- Optionally merge duplicate facts (e.g. consolidate Chris/Solonaras rows)

**Approach:**
- SQL script or small Python migration
- Run once, then rely on Fix 2.1 to prevent new bad data

**Files:** New script `scripts/clean_bad_facts.py` or similar

**Effort:** ~20 min  
**Risk:** Low (backup DB first)  
**Blocks:** Fix 2.1 (so you know what “bad” means)  
**When:** After Fix 2.1

---

## Phase 4: Alias-Aware Components

### Fix 4.1 — Vector reasoning uses aliases

**What:** Make `reason_with_vectors` merge memories across all aliases.

**Changes:**
1. Add `usernames: List[str] = None` to `reason_with_vectors`.
2. In `_retrieve_semantic_memories`, loop over `usernames or [username]`, call `express_genes` per alias, merge and deduplicate.
3. Update `recall_dna_memories_with_vector_reasoning` to pass `memory_usernames` into `reason_with_vectors`.

**Files:**
- `luna_vector_reasoning.py` — `reason_with_vectors`, `_retrieve_semantic_memories`
- `luna_dna_memory.py` — `recall_dna_memories_with_vector_reasoning`

**Effort:** ~45 min  
**Risk:** Medium (vector reasoning path is complex)  
**Blocks:** Fix 1.1 (aliases must be correct)

---

### Fix 4.2 — save_dna_memory profile merge uses aliases

**What:** When updating profile in `save_dna_memory`, merge from all aliases before applying updates.

**Changes:**
1. Add alias resolution in `save_dna_memory` (e.g. if `username` in Chris aliases, use `CHRIS_ALIASES`).
2. Call `get_user_profile(username, usernames=aliases)` instead of `get_user_profile(username)`.
3. When saving, decide whether to write to all alias rows or a canonical one (recommend: write to primary alias, e.g. `"Chris"`).

**Files:** `luna_dna_memory.py` — `save_dna_memory`

**Effort:** ~30 min  
**Risk:** Low  
**Blocks:** Fix 1.1 / 1.2 (alias list)

---

## Phase 5: Optional Enhancements

### Fix 5.1 — Fact deduplication / conflict resolution

**What:** When merging facts from multiple aliases, prefer higher-confidence or canonical values (e.g. prefer `name=Chris` over `name=from Cyprus`).

**Approach:**
- In `get_user_facts` merge logic: for `fact_type="name"`, drop values that look like location phrases.
- Or: add a `fact_confidence` or `source` field for future use.

**Effort:** ~30 min  
**Risk:** Low  
**Blocks:** Fix 2.1, 3.1

---

### Fix 5.2 — Extend alias system for other users

**What:** Support configurable aliases (e.g. Travis + twitch_username) so future users don’t hit the same issues.

**Approach:**
- Add `USER_ALIASES` config: `{"chris": [...], "travis": [...]}`.
- Resolve aliases from config instead of hardcoding.

**Effort:** ~1 hr  
**Risk:** Low  
**Blocks:** Fix 1.2

---

## Roadmap Summary

| Phase | Fix | Effort | Dependencies |
|-------|-----|--------|--------------|
| **1** | 1.1 Add Solonaras to aliases | 15 min | — |
| **1** | 1.2 Centralize alias constant | 20 min | — |
| **2** | 2.1 Fix name/location extraction | 30 min | — |
| **3** | 3.1 Clean bad facts in DB | 20 min | 2.1 |
| **4** | 4.1 Vector reasoning aliases | 45 min | 1.1 |
| **4** | 4.2 save_dna_memory profile merge | 30 min | 1.1 |
| **5** | 5.1 Fact conflict resolution | 30 min | 2.1, 3.1 |
| **5** | 5.2 Configurable aliases | 1 hr | 1.2 |

**Total (Phases 1–4):** ~2.5–3 hrs  
**With Phase 5:** ~4 hrs

---

## Suggested Order

1. **1.1 + 1.2** — Alias fixes (foundation)
2. **2.1** — Stop new bad facts
3. **3.1** — Clean existing bad facts
4. **4.1 + 4.2** — Alias-aware recall and profile merge
5. **5.1, 5.2** — Optional improvements

---

## Validation Checklist

After each phase:

- [ ] Run Luna, ask “what is my name?” as Chris/Solonaras → expects “Chris”
- [ ] Ask “where is Chris from?” as Travis → expects “Cyprus”
- [ ] Ask “where are you from?” as Chris → expects “Cyprus”
- [ ] Check `user_facts` for no new `name=from X` rows
- [ ] Verify vector reasoning returns memories from all aliases (if enabled)
