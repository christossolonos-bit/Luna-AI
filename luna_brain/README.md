# Luna Brain — HIM + JEPA Combined Brain

Luna uses this package as her **combined brain**: memory (HIM-like store) + understanding (JEPA from New AI Child). Luna remains the **operator and personality** (Discord, Twitch, GUI, Ollama).

## Config

Uses the same sources as Luna Waifu:

- **Discord:** `DISCORD_TOKEN` from `.env`, `discord_token.txt`, or `discord_config.json`  
  IDs: `CHRIS_DISCORD_USER_ID`, `FUSION_AI_GUILD_ID`, `FUSION_AI_DEFAULT_VC_ID`, `DISCORD_TARGET_CHANNEL_ID`
- **Twitch:** `TWITCH_ACCESS_TOKEN`, `TWITCH_CLIENT_ID`, `TWITCH_CHANNEL`, `TWITCH_USERNAME` from env or `twitch_config.json`
- **Ollama:** `OLLAMA_MODEL` (default: Luna’s qwriko3-4b model)

Optional env:

- `BRAIN_MEMORY_TOP_K` — number of past turns to retrieve (default 5)
- `BRAIN_MEMORY_MAX_TURNS` — max turns to keep in store (default 500)
- `BRAIN_DATA_DIR` — directory for persistent data (default `luna_brain_data`)

## How it’s wired

- **`luna_clean.generate_response()`** calls:
  - `brain.turn(user_message, user_id=..., channel_id=..., platform=...)` → `(context, internal_state)`  
    Injects into Luna’s prompt as `[HIM+JEPA memory]` and internal state line.
  - After Ollama reply: `brain.store_turn(user_message, reply, user_id=..., channel_id=...)`

- **JEPA** (optional): if `New AI Child` is on the path and imports succeed, JEPA provides the embedding and emotion summary. Otherwise the store uses only recent turns (no vector search).

- **Store:** in-memory buffer of (user, luna, embedding, channel_id). With `numpy`, retrieval uses embedding similarity; without, last K turns per channel.

## Run Luna

From the **Luna Waifu** directory (parent of `luna_brain`):

```bash
python luna_clean.py
```

Discord token, Twitch, and Ollama model are read from Luna’s usual config (see above).
