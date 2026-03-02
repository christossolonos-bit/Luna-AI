LUNA — AI WOLF COMPANION
========================

Everything Luna can do — for Notebook LM podcast

Luna is a 25-year-old AI wolf woman with personality, memory, and multi-platform support. She runs locally with Ollama and connects to Discord, Twitch, and a local GUI.


RUN
---
  cd "D:\Luna Waifu"
  python run_agent.py

Starts: GUI + Discord + Twitch.


PLATFORMS
---------
  Discord  - Responds in #luna-chat, joins voice channels, speaks with TTS, plays YouTube in VC
  Twitch   - Batches chat every 30s, summarizes and posts to Discord; responds to subs, raids, bits, donations; extracts facts from chat
  GUI      - Local chat with voice input (mic) and TTS output


DISCORD COMMANDS
----------------
  !play https://youtube.com/watch?v=...  - Play a YouTube video in Discord VC
  profile / !profile                     - Show your profile (facts, interests, interactions)
  profile @user                          - Show another user's profile
  !share song                            - Share a random song from your YouTube channel to X (admin)
  !create song [description]             - Create a song on Suno with the given description (admin)
  dm [user_id] [message]                 - Send a Discord DM to a user

Admin Commands (restricted):
  admin compile profiles  - Scan chat history and build/update user profiles
  admin clean bad facts   - Remove junk facts (filler interests, bad types)
  admin list profiles    - List all known users and their profile summaries


BROWSER ABILITIES
-----------------
Luna automates a browser (Playwright) to create and share music:

  !create song [description]  - Opens Suno, clicks Login (first run), enters your description, clicks Create. Session saved.
  !share song                 - Picks a random video from your YouTube channel, opens X (Twitter), posts it. Session saved.

Requires: pip install playwright && playwright install chromium


SEARCH & WEB
------------
  youtube [query] / search youtube [query]  - Search YouTube, inject results into her reply
  google [query] / search google [query]    - Search Google, inject results into her reply
  URLs in messages                          - Crawls shared links and analyzes content for context


TIME & LOCATION
---------------
  time / date / what time is it     - Returns current system time and date
  time in [location]               - Returns time for Cyprus, Greece, UK, Tokyo, New York, etc.
  local info / where am i           - Returns local system info


MEMORY & LEARNING
-----------------
  DNA Memory       - Stores conversations as genetic strands; extracts facts (name, location, interests); memories have strength and evolve
  User profiles    - Persist across restarts; Luna recalls what she knows about you
  Reactions        - Thumbs up/down on Luna's Discord messages adjust her personality state (hormones, mood)
  Identity linking - Merges profiles across platforms (e.g. Chris = Solonaras)


AI SYSTEMS (BACKGROUND)
-----------------------
  HIM+JEPA Brain     - Memory and understanding (optional JEPA from D:\New AI Child)
  Understanding Engine - Concept mapping, introspection, imagination, dreams
  Vector Reasoning   - Semantic similarity, emotional/temporal analysis
  Curiosity Engine   - Autonomous topic exploration when idle
  Continuous Learning - Extracts knowledge from every interaction


LEARNING & CURIOSITY COMMANDS
-----------------------------
  improve yourself / reflect     - Luna reflects and proposes self-improvements
  show modifications            - Show recent self-modification history
  learn from this [text]        - Extract facts and preferences from text
  understand [topic]            - Build concept map, introspection, imagination, dream for a topic
  learning stats                - Show learning statistics
  curiosity run / explore       - Run curiosity exploration cycle
  curiosity stats               - Show curiosity engine stats


PERFORMANCE & DEBUG
-------------------
  performance mode     - Toggle performance optimizations
  full cognitive mode  - Enable all AI systems (understanding, curiosity, etc.)
  performance stats   - Show background processes, memory, curiosity status


TWITCH
------
  Sub / Resub / Sub gift / Raid / Bits / Donation - Pre-written thank-you message, posts to Twitch chat, Discord, and speaks in Discord VC
  Regular chat - Buffered every 30s, AI summarizes, posts summary to Twitch + Discord
  Facts - Extracts name, location, interests from Twitch chat (no full conversation storage)


VOICE & VC
----------
  Join VC  - Joins Chris's voice channel when he's in one, or Fusion AI default VC
  TTS      - Edge TTS (default) or Lux TTS (voice cloning) for Discord VC
  VC idle  - After ~2 min silence, Luna asks a curious question to learn more
  !play    - Downloads YouTube audio with yt-dlp, plays in VC


CONTEXT AWARENESS
-----------------
  Addressee scoring   - Decides when to reply: TO Luna vs ABOUT Luna vs TO someone else (SEL, Akane)
  Implicit references - Recognizes "she", "her", "the bot", "the wolf" when Luna was in recent context
  Not for Luna        - Skips replying when user says "not for Luna to answer", "Luna don't reply", etc.
  Other bots          - Can interact with Akane as a peer; doesn't intercept messages meant for SEL


PERSONALITY
-----------
  Wolf woman, 25, with hormones and emotions
  Special relationship with Chris (creator): more devoted, submissive, eager to please
  Factual accuracy: Uses only exact facts for "who is X?"; admits when she doesn't know
  Follow-ups: Answers new questions directly, doesn't repeat previous replies
  Twitch TOS: Flirty, playful, innuendo — no explicit terms


CONFIG
------
  Discord token  - .env (DISCORD_TOKEN) or discord_token.txt
  Twitch         - .env or twitch_config.json
  Ollama model   - luna_clean.py / OLLAMA_MODEL
  Channel IDs, Chris ID - luna_clean.py


DEV
---
  Hot reload - Luna updates automatically when you save code changes


OPTIONAL DEPENDENCIES
---------------------
  Lux TTS    - Voice cloning in Discord VC
  Playwright - For !share song and !create song
  JEPA       - Enhanced understanding (if D:\New AI Child exists)
