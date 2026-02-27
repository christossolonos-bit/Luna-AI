# Luna + SEL + New AI Child — Integration Plan

**Goal:** Combine all three systems with **Luna as the main controller**. Luna keeps Discord, Twitch, and GUI; SEL adds hormone-driven mood and episodic memory; New AI Child adds deeper mind (JEPA, emotions, vision).

> **Primary plan:** For **HIM + JEPA combined brain with Luna as operator and personality**, see **[HIM_JEPA_BRAIN_LUNA_OPERATOR.md](./HIM_JEPA_BRAIN_LUNA_OPERATOR.md)**. That doc describes Luna as the main operator/personality and HIM+JEPA as the unified brain backend; this doc is the broader three-project integration (including SEL hormones, etc.).

---

## 1. Current Roles

| Component | Luna | SEL | New AI Child |
|-----------|------|-----|--------------|
| **Discord** | ✅ Client, messages, VC, TTS | ✅ Logic only (in repo) | — |
| **Twitch** | ✅ Client + chat | — | — |
| **GUI** | ✅ tkinter (LunaGUI) | — | ✅ tkinter (ChatGUI) |
| **Memory** | DNA memory, vector reasoning | Episodic (HIM/DB), per-channel | Fact memory, intelligent memory |
| **Mood/emotion** | — | Hormones (dopamine, cortisol, …) | EmotionSystem, consciousness |
| **LLM** | Ollama (local) | OpenRouter (Claude) | Ollama Qwen-VL (optional) |
| **Voice** | Lux TTS / Edge TTS, VC | Optional ElevenLabs | Voice in/out in GUI |
| **Vision** | — | Image analysis in Discord | Qwen2.5-VL (images) |

---

## 2. Target Architecture (Luna as Shell)

```
                    ┌─────────────────────────────────────────────────┐
                    │              LUNA (main controller)              │
                    │  • Discord client (messages + VC + TTS)         │
                    │  • Twitch client                                │
                    │  • LunaGUI (tkinter)                             │
                    │  • Single entry: luna_clean.main() → LunaGUI     │
                    └─────────────────────┬───────────────────────────┘
                                          │
         ┌────────────────────────────────┼────────────────────────────────┐
         │                                │                                │
         ▼                                ▼                                ▼
┌─────────────────┐            ┌─────────────────────┐            ┌─────────────────────┐
│  SEL module     │            │  Response pipeline  │            │  New AI Child module │
│  (optional)     │            │  (Luna core)        │            │  (optional)          │
│                 │            │                     │            │                      │
│ • Hormones      │───────────▶│ • get_core_prompt   │◀───────────│ • IntegratedMind     │
│   per channel   │  mood +    │ • memory_search_    │  deep/     │   .process_and_      │
│ • should_reply? │  style     │   block (DNA)       │  vision    │   respond()          │
│ • Episodic      │            │ • vector_insights   │            │ • Qwen-VL for images │
│   memory        │            │ • ollama.chat()     │            │ • Emotions → tone    │
└─────────────────┘            │ • save_dna_memory  │            └─────────────────────┘
                                └─────────────────────┘
```

- **Luna** remains the only process: one Discord connection, one Twitch connection, one GUI. All user-facing I/O goes through Luna.
- **SEL** is used as a **library**: hormones + episodic memory + (optionally) “when to reply” and style hints. No separate SEL Discord client in this design.
- **New AI Child** is used as a **library**: `IntegratedMind` for optional deep/reflective replies and vision; emotions can feed into Luna’s tone.

---

## 3. Where Luna Decides and Generates

- **Discord:** `luna_clean.py` → `_process_discord_message(message)` → `generate_response(message.content, message.author.display_name, "discord", user_id=message.author.id)` → `ollama.chat(...)`.
- **Twitch:** Twitch handler → same `generate_response(..., platform="twitch")`.
- **GUI:** `LunaGUI` sends user text → `gui.luna.generate_response(text, username, "gui")`.

So **all paths** go through `Luna.generate_response()`. That is the single place to:
- Add SEL mood/style and “should reply” (for Discord).
- Add Child “deep mind” or vision when desired.

---

## 4. Integration Steps (Phased)

### Phase 1: SEL — Hormones + style in Luna’s prompt (no extra Discord client)

**Goal:** Luna keeps her Discord client; we add per-channel “mood” and optional “should I reply?” using SEL’s hormone model.

1. **Copy / symlink SEL code Luna needs**
   - From `D:\SEL-github` (or `D:\SEL`):
     - `project_echo/sel_bot/hormones.py` (HormoneVector, apply_message_effects, decay, temperature_for_hormones).
     - `project_echo/sel_bot/behaviour.py` (e.g. `should_respond`, `is_direct_question_to_sel`).
     - `project_echo/sel_bot/config.py` / Settings if you need DB or env (optional for Phase 1).
   - Place under e.g. `Luna Waifu/integrations/sel/` and fix imports (e.g. relative to that package). Prefer minimal set so Luna does not depend on full SEL stack (DB, OpenRouter).

2. **Persist hormone state per Discord channel**
   - Luna is synchronous/threaded; SEL’s state is async (DB). Options:
     - **A)** In-memory only: `dict[channel_id_str, HormoneVector]` in Luna, no DB. Easiest; state lost on restart.
     - **B)** SQLite (or Luna’s existing storage): one table `channel_id, dopamine, serotonin, ...`; load/save in Luna on message. Reuse SEL’s HormoneVector dataclass.
   - When a Discord message is processed, load or create `HormoneVector` for `message.channel.id`, apply deltas (you can derive simple deltas from “message length”, “has mention”, “has image” until you hook SEL’s classifier), then save.

3. **Inject “mood” into Luna’s prompt**
   - In `generate_response()`, when `platform == "discord"`:
     - Get channel_id (e.g. pass through from `_process_discord_message`; you may need to add an optional `channel_id=` to `generate_response`).
     - Load hormones for that channel; build a short line such as:  
       `[MOOD] Current channel mood: dopamine={d}, serotonin={s}, cortisol={c}. Respond with slightly more/less energy and warmth accordingly.`
     - Append (or insert) this into `full_prompt` before the user message (same place you add `memory_search_block`, etc.).
   - Optionally use `temperature_for_hormones(hormones)` to tweak `OLLAMA_CONFIG["temperature"]` for that call.

4. **Optional: “Should Luna reply?” (Discord)**
   - In `_process_discord_message`, before calling `generate_response`:
     - Compute `is_mentioned`, `direct_question` (e.g. “Luna” + “?”), `messages_since_response`, `seconds_since_response` (track last reply time per channel in Luna).
     - Call `should_respond(is_mentioned, direct_question, hormones, base_chance=0.2, messages_since_response=..., seconds_since_response=...)`.
     - If `False`, return without replying (optionally add a typing or short “…” only if you want).

5. **Episodic memory (SEL-style)**
   - Phase 1 can stay on Luna’s DNA memory only. Phase 2 can add:
     - After each Luna reply in Discord, call an SEL-style “summarize_for_memory” (or a small local summarizer) and store a short summary keyed by channel_id + time.
     - When building the prompt for that channel, retrieve last N episodic summaries and add a `[CHANNEL_MEMORY]` block like SEL’s prompts. This can live in Luna’s codebase and use SQLite or a JSON file; it doesn’t require running SEL’s full server.

### Phase 2: New AI Child — Deep mind and vision (optional paths)

**Goal:** For some inputs, use Child’s mind (JEPA + emotions + Qwen-VL); optionally use Child’s emotions to influence Luna’s tone.

1. **Import Child’s mind inside Luna’s process**
   - Add `D:\New AI Child` to `sys.path` (or install as package), or copy a minimal set of modules into `Luna Waifu/integrations/child/`.
   - Dependencies: `mind.py` depends on `model`, `embeddings`, `emotions`, `consciousness`, etc. Easiest is to run from New AI Child’s root and import `IntegratedMind`, or copy the whole tree and fix paths.
   - In Luna’s startup (e.g. in `Luna.__init__` or on first use), instantiate:
     - `child_mind = IntegratedMind(...)` (with optional model_path if you have a trained JEPA).
   - Guard with `try/except` and a flag `CHILD_MIND_AVAILABLE` so Luna runs without Child if imports fail.

2. **When to call Child**
   - **Option A — Reflective / “think deeper”:** If the user message contains phrases like “what do you really think”, “reflect”, “your inner thoughts”, or if platform is `"gui"` and a “Deep reply” checkbox is enabled, call:
     - `response_child = child_mind.process_and_respond(user_message, return_inner_conv=False, context={"platform": platform})`
     - Use `response_child` as the reply, or blend with Luna’s Ollama reply (e.g. “Luna: [Ollama]. *reflecting* [Child].”).
   - **Option B — Vision:** When the message has an image (Discord attachment or URL), download the image and call Child’s Qwen-VL (or `qwen_vl.generate(..., image_paths=[...])`) to get a description or a reply that sees the image. Inject that into Luna’s `full_prompt` as “User shared an image. Description: …” or use it as the only reply for that turn.

3. **Emotions → Luna’s tone**
   - After `child_mind.process_and_respond`, read Child’s emotional state (e.g. `child_mind.emotions.get_emotion_vector()` or a small dict). Append a line to Luna’s prompt: “Your internal emotional state (from your deeper mind): …” so Luna’s Ollama reply is consistent with that mood.

### Phase 3: Unify memory and optional HIM

- **Memory:**
  - Luna already has DNA memory and vector reasoning. Add a small “episodic summary” layer (SEL-style) keyed by channel + time and optionally by user. When building the prompt, combine:
    - DNA recall (Luna),
    - Episodic summaries (SEL-style),
    - Child’s fact_memory if you exposed it (e.g. “Facts from your deep memory: …”).
- **HIM:** Only if you need large-scale, tiered memory (e.g. for agents or very long history). Then run SEL’s HIM services and have Luna (or a small adapter) query them when building context; otherwise skip.

---

## 5. File and Config Changes (Summary)

- **Luna (D:\Luna Waifu)**
  - `luna_clean.py`:
    - Add optional `channel_id` (and maybe `guild_id`) to `generate_response()` for Discord.
    - In `generate_response()`, when platform is Discord, call into SEL integration to get hormone vector and mood string; append to `full_prompt`; optionally adjust temperature.
    - In `_process_discord_message`, before `generate_response`, optionally call `should_respond` and skip reply if False; track last reply time per channel.
    - (Phase 2) When “deep” or “vision” is requested, call Child’s `IntegratedMind` / Qwen-VL and use or merge result.
  - New file: `luna_clean_sel.py` or `integrations/sel/luna_sel_bridge.py`: thin wrapper that loads hormones, applies message effects, returns mood string and “should reply”.
  - New file: `integrations/child/luna_child_bridge.py` (Phase 2): wrap `IntegratedMind.process_and_respond` and Qwen-VL image handling; return text and optional emotion hint.
  - Config: e.g. `PLATFORM_CONFIG["integrations"]["sel"] = {"enabled": True, "hormones": True, "should_reply": True}` and `["child"] = {"enabled": True, "deep_reply": True, "vision": True}`.

- **SEL (D:\SEL-github)**
  - No need to run `sel_bot.main()` for this design. Use as library: copy or symlink `hormones.py`, `behaviour.py`, and optionally `memory` + DB helpers into Luna’s tree.

- **New AI Child (D:\New AI Child)**
  - No structural change. Luna imports `IntegratedMind` and `qwen_vl` (or equivalent); run from Child’s env or install Child’s deps into Luna’s env.

---

## 6. Dependency and Env Notes

- Luna: already uses `ollama`, `discord.py`, `tkinter`, etc.
- SEL: `hormones` and `behaviour` are pure Python + dataclasses; no hard OpenRouter dependency for Phase 1. If you add episodic memory with summarization, you can use Ollama for summaries or a small local model.
- Child: `torch`, JEPA model files, `qwen_vl` (Ollama). Ensure Luna’s Python can see Child’s modules and that Ollama runs Qwen-VL when vision is used.

---

## 7. Suggested Order of Work

1. **Phase 1a:** Add `integrations/sel/` with hormones only; persist in-memory per channel; inject mood line into Luna’s Discord prompt; test in one channel.
2. **Phase 1b:** Add “should reply” using SEL’s behaviour and last-reply tracking; test.
3. **Phase 1c:** Add episodic summaries (store last N summaries per channel, feed as `[CHANNEL_MEMORY]`).
4. **Phase 2a:** Import Child’s `IntegratedMind` behind a flag; call it for “deep” or GUI when requested; blend or replace reply.
5. **Phase 2b:** Add image handling: Discord attachment → Qwen-VL → inject or reply.
6. **Phase 3:** Unify memory (DNA + episodic + optional Child facts) and document; add HIM only if needed.

This keeps **Luna as the single main controller** for Twitch, Discord, and GUI, while SEL and New AI Child act as optional capabilities plugged into Luna’s response pipeline and prompt.
