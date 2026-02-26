# Discord Voice Channel (Lux TTS) Setup

Luna joins a voice channel and speaks her responses using Lux TTS (Arabella voice) or Edge TTS (fallback).

**Behavior:** If Chris is in a VC on any server, Luna joins that. If not, she joins the Fusion AI default VC.

**Twitch→Discord VC:** When someone chats on Twitch, Luna replies in Twitch text *and* joins your Discord VC to speak the reply with Arabella voice. She finds you by `CHRIS_DISCORD_USER_ID`—set it below.

## 1. Set Chris's Discord User ID

In `luna_clean.py`:
```python
CHRIS_DISCORD_USER_ID = 1234567890123456789  # Your Discord user ID
```

Or: `CHRIS_DISCORD_USER_ID=1234567890123456789`

To get it: Enable Developer Mode (Discord Settings → Advanced), right-click your profile → Copy User ID.

## 2. Set Fusion AI Fallback (when Chris isn't in VC)

```python
FUSION_AI_GUILD_ID = 9876543210987654321  # Fusion AI server ID
FUSION_AI_DEFAULT_VC_ID = 1111111111111111111  # VC to join (e.g. "Chris' voice")
```

Or use env vars: `FUSION_AI_GUILD_ID`, `FUSION_AI_DEFAULT_VC_ID`

## 2. Install Voice Support

```bash
pip install "discord.py[voice]"
```

FFmpeg must be installed on your system for audio playback.

## 3. Lux TTS (Optional - Voice Cloning)

For Luna's custom voice (Arabella-style), install Lux TTS:

```bash
pip install LuxTTS-mlx
pip install "LuxTTS-mlx[phonemize]"  # For English
```

Place your voice sample at `LuxTTS/prompts/arabella.mp3` (or .wav) - at least 3 seconds of clear speech.

Configure in `luna_clean.py` via `LUX_TTS_CONFIG`:
- `prompt_audio`: Path to your voice sample
- `prompt_text`: Transcription of that sample
- `device`: `cuda`, `cpu`, `mps`, or `mlx`

## 4. Fallback

If Lux TTS is not installed or fails, Luna uses Edge TTS (Ava voice) for Discord VC.
