# Luna Waifu — Luna + HIM + JEPA

One agent: **Luna** (personality + LLM) + **HIM** (memory) + **JEPA** (understanding). Run everything from this folder; all tokens and config live here.

## Run the agent

From this folder:

```bash
cd "D:\Luna Waifu"
python run_agent.py
```

Or:

```bash
python luna_clean.py
```

Starts: GUI + Discord + Twitch. Luna uses the HIM+JEPA brain (`luna_brain`) for memory and understanding.

## Config (this folder)

- **Discord:** `DISCORD_TOKEN` in `.env`, or `discord_token.txt`, or `discord_config.json`
- **Twitch:** `twitch_config.json` or env: `TWITCH_ACCESS_TOKEN`, `TWITCH_CLIENT_ID`, `TWITCH_CHANNEL`, `TWITCH_USERNAME`
- **Ollama:** model and options in `luna_clean.py` / env

Channel IDs and other Luna settings are in `luna_clean.py`.

## Optional

- **JEPA:** If `D:\New AI Child` exists and is on the path, `luna_brain` uses it for understanding.
- **Grumpychat:** The `d:\grumpychat` folder has a music bot (`bot.py`) and optional launchers; the main agent runs from here.
