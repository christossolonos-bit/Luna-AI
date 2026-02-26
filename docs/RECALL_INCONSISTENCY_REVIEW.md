# Luna Recall Inconsistency Review

Based on analysis of the message flow, DNA memory, and actual database contents.

---

## 1. Username alias gaps (Chris vs Solonaras)

**Observed in DB:**
```
user_facts:     Chris, Solonaras, solonaras, chris, Travis
memory_strands: Chris, Solonaras, solonaras, Travis, ...
```

**Current aliases:** `["Chris", "chris", "solonaras"]`

**Issue:** `"Solonaras"` (capital S) is **not** in the alias list. SQLite `=` is case-sensitive, so:
- `username = 'solonaras'` does **not** match rows with `username = 'Solonaras'`
- Facts and memories stored as `Solonaras` are never merged when recalling for Chris

**Impact:** Luna can miss Chris’s facts (e.g. location=Cyprus) when they were stored under `Solonaras`.

---

## 2. Bad fact extraction: "I'm from X" → name="from X"

**Observed in DB:**
```
Solonaras|name|from Cyprus
```

**Cause:** In `_extract_facts_from_message`, the name regex runs and matches:
- Pattern: `(?:i am|i\'?m)\s+([a-zA-Z][a-zA-Z0-9_\s\-]{1,20})`
- Input: "I'm from Cyprus"
- Match: "I'm" + "from Cyprus" → stored as `name="from Cyprus"`

The location pattern `(?:i\'?m from|...)\s+([...])` would capture "Cyprus" correctly, but the name pattern fires first and incorrectly treats "from Cyprus" as a name.

**Impact:** Luna may recall "from Cyprus" as Chris’s name instead of "Chris".

---

## 3. Vector reasoning ignores username aliases

**Code:** `reason_with_vectors(query, username, dna_memory_system)` receives a single `username`.

**Flow:**
- `recall_dna_memories_with_vector_reasoning` passes `username` (e.g. `"Solonaras"`)
- `reason_with_vectors` → `_retrieve_semantic_memories` → `express_genes(username, query)`
- `express_genes` queries `WHERE username = ?` with that one value

**Issue:** No alias merging. Only memories for the exact `username` are used:
- `username="Solonaras"` → only Solonaras rows
- `username="Chris"` → only Chris rows
- No merge of Chris + chris + solonaras + Solonaras

**Impact:** Vector reasoning can miss relevant memories when the user appears under different usernames.

---

## 4. save_dna_memory profile merge uses single username

**Code (luna_dna_memory.py ~733):**
```python
prof = _dna_memory_system.get_user_profile(username) or {}
```

**Issue:** `get_user_profile(username)` is called without `usernames`. When `username="Solonaras"`:
- Only the `Solonaras` profile row is loaded
- Chris’s existing interests/preferences are not merged
- Updates are written only to the `Solonaras` row

**Impact:** Profile data can stay split across Chris/Solonaras instead of being unified.

---

## 5. Conflicting facts across aliases

**Observed in DB:**
```
Chris|name|Chris
Solonaras|name|from Cyprus   ← wrong
solonaras|name|Chris
chris|name|Chris
```

When merging with `usernames=["Chris", "chris", "solonaras"]` (and no `"Solonaras"`):
- We get `name=Chris` and `name=from Cyprus`
- Both are injected into the prompt
- The model may pick the wrong one or mix them

---

## 6. Recall flow summary

| Component | Uses aliases? | Notes |
|-----------|----------------|-------|
| `recall_dna_memories` | ✅ Yes | Iterates over `usernames`, merges |
| `get_user_facts` | ✅ Yes | Queries each alias |
| `get_user_profile` | ✅ Yes | When `usernames` passed |
| `get_user_profile_analysis` | ✅ Yes | When `usernames` passed |
| `express_genes` | ❌ Per-call only | One username per call; `recall_dna_memories` loops to compensate |
| `reason_with_vectors` | ❌ No | Single `username`, no alias support |
| `save_dna_memory` → `get_user_profile` | ❌ No | Single `username` |
| Alias list | ⚠️ Incomplete | Missing `"Solonaras"` |

---

## Recommended fixes

1. **Add `"Solonaras"` to all alias lists**  
   Use: `["Chris", "chris", "Solonaras", "solonaras"]` everywhere.

2. **Fix name extraction**  
   Exclude location phrases from the name pattern, e.g.:
   - Do not treat `"from X"` / `"in X"` as names
   - Or run location extraction before name extraction and skip name extraction when location matched

3. **Pass `usernames` into `reason_with_vectors`**  
   - Extend signature to accept `usernames`
   - In `_retrieve_semantic_memories`, call `express_genes` for each alias and merge results (similar to `recall_dna_memories`)

4. **Pass `usernames` in `save_dna_memory`**  
   - When updating profile, call `get_user_profile(username, usernames=aliases)` so all alias rows are merged before applying updates.

5. **Clean bad facts**  
   - Remove or correct `Solonaras|name|from Cyprus` and similar rows (e.g. via a one-off migration or admin script).
