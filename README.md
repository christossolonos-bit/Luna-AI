# Luna — AI Wolf Companion

Luna is an AI companion with personality, memory, and multi-platform support. She runs locally with Ollama and connects to Discord and Twitch.

## Run

```bash
cd "D:\Luna Waifu"
python run_agent.py
```

Starts: GUI + Discord + Twitch.

---

## Platforms

| Platform | What Luna does |
|----------|----------------|
| **Discord** | Responds in `#luna-chat`, joins voice channels, plays YouTube in VC |
| **Twitch** | Batches chat every 30s → summarizes and posts to Discord; responds to subs, raids, bits, donations |
| **GUI** | Local chat with voice input (mic) and TTS output |

---

## Discord Commands

| Command | Description |
|---------|-------------|
| `!play https://youtube.com/watch?v=...` | Play a YouTube video in Discord VC |
| `profile` / `!profile` | Show your profile (facts, interests, interactions) |
| `profile @user` | Show another user's profile |
| `!share song` | Share a random song from your YouTube channel to X *(admin)* |
| `!create song [description]` | Create a song on Suno with the given description *(admin)* |

### Admin Commands *(restricted to `ADMIN_USER_IDS`)*

| Command | Description |
|---------|-------------|
| `admin compile profiles` | Scan chat history and build/update user profiles |
| `admin clean bad facts` | Remove junk facts (filler interests, bad types) |
| `admin list profiles` | List all known users and their profile summaries |

---

## Browser Abilities

Luna can automate a browser (via Playwright) to create and share music:

| Command | What it does |
|---------|---------------|
| **`!create song [description]`** | Opens Suno, enters your description, and clicks Create. First run: click Login to sign in; session is saved. |
| **`!share song`** | Picks a random video from your YouTube channel, opens X (Twitter), and posts it. First run: log in to X; session is saved. |

**Requires:** `pip install playwright && playwright install chromium`

---

## Search (in chat)

- **`youtube [query]`** or **`search youtube [query]`** — Search YouTube, Luna uses results in her reply
- **`google [query]`** or **`search google [query]`** — Search Google, Luna uses results in her reply

---

## Memory & Profiles

- **DNA Memory** — Stores conversations, extracts facts (name, location, interests)
- **User profiles** — Persist across restarts; Luna recalls what she knows about you
- **Reactions** — 👍 / 👎 on Luna's messages adjust her personality state

---

## Config

| Item | Location |
|------|----------|
| Discord token | `.env` (`DISCORD_TOKEN`) or `discord_token.txt` |
| Twitch | `.env` or `twitch_config.json`: `TWITCH_ACCESS_TOKEN`, `TWITCH_CLIENT_ID`, `TWITCH_CHANNEL`, `TWITCH_USERNAME` |
| Ollama model | `luna_clean.py` / `OLLAMA_MODEL` in env |
| Channel IDs | `luna_clean.py` |

---

## Optional

- **Lux TTS** — `pip install LuxTTS-mlx` for voice cloning in Discord VC (otherwise Edge TTS)
- **Playwright** — `pip install playwright && playwright install chromium` for `!share song` and `!create song`
- **JEPA** — If `D:\New AI Child` exists, Luna Brain uses it for understanding
