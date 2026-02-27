"""
Luna Brain config — Discord, Twitch, Ollama and other settings.
Uses same sources as Luna Waifu: .env, discord_token.txt, discord_config.json, twitch_config.json.
"""
from __future__ import annotations

import os
import json
from pathlib import Path

# Load .env if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# --- Discord (from Luna Waifu) ---
def _discord_token() -> str | None:
    token = None
    if Path("discord_token.txt").exists():
        token = Path("discord_token.txt").read_text(encoding="utf-8").strip()
    if not token:
        token = os.getenv("DISCORD_TOKEN")
    if not token and Path("discord_config.json").exists():
        with open("discord_config.json", "r", encoding="utf-8") as f:
            token = json.load(f).get("token")
    return token if (token and len(token) > 50 and "." in token) else None

DISCORD_TOKEN = _discord_token()

# Channel and user IDs (from Luna Waifu)
DISCORD_TARGET_CHANNEL_ID = int(os.getenv("DISCORD_TARGET_CHANNEL_ID", "1387526539293233308"))
DISCORD_TARGET_CHANNEL_ID_2 = int(os.getenv("DISCORD_TARGET_CHANNEL_ID_2", "1427975568439251045"))
CHRIS_DISCORD_USER_ID = int(os.getenv("CHRIS_DISCORD_USER_ID", "1414944231222411378")) or None
FUSION_AI_GUILD_ID = int(os.getenv("FUSION_AI_GUILD_ID", "1387520068367159368")) or None
FUSION_AI_DEFAULT_VC_ID = int(os.getenv("FUSION_AI_DEFAULT_VC_ID", "1387526220882771999")) or None

# --- Twitch (from Luna Waifu) ---
TWITCH_ACCESS_TOKEN = os.getenv("TWITCH_ACCESS_TOKEN")
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_USERNAME = os.getenv("TWITCH_USERNAME", "solosluna")
TWITCH_CHANNEL = os.getenv("TWITCH_CHANNEL", "solonaras")

if not TWITCH_ACCESS_TOKEN and Path("twitch_config.json").exists():
    try:
        with open("twitch_config.json", "r", encoding="utf-8") as f:
            cfg = json.load(f)
            TWITCH_ACCESS_TOKEN = cfg.get("token") or TWITCH_ACCESS_TOKEN
            TWITCH_CLIENT_ID = cfg.get("client_id") or TWITCH_CLIENT_ID
            TWITCH_USERNAME = cfg.get("username", TWITCH_USERNAME)
            TWITCH_CHANNEL = cfg.get("channel", TWITCH_CHANNEL)
    except Exception:
        pass

# --- Ollama (from Luna Waifu) ---
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "hf.co/subsectmusic/qwriko3-4b-instruct-2507-redux-GGUF:Q4_K_M")

OLLAMA_CONFIG = {
    "temperature": 0.95,
    "top_p": 0.98,
    "num_ctx": 4096,
    "num_gpu": 1,
    "stop": ["User:", "Chris:", "\n\n\n"],
    "repeat_penalty": 1.1,
    "presence_penalty": 0.0,
    "frequency_penalty": 0.0,
}

# --- Brain ---
# Max number of past turns to retrieve for context
BRAIN_MEMORY_TOP_K = int(os.getenv("BRAIN_MEMORY_TOP_K", "5"))
# Max total turns to keep in store (HIM-like buffer)
BRAIN_MEMORY_MAX_TURNS = int(os.getenv("BRAIN_MEMORY_MAX_TURNS", "500"))
# Data directory for persistent store (optional)
BRAIN_DATA_DIR = Path(os.getenv("BRAIN_DATA_DIR", "luna_brain_data"))
BRAIN_DATA_DIR.mkdir(parents=True, exist_ok=True)
