# 🌙 Kokoro TTS Setup Guide for Luna

## Overview
Kokoro TTS provides high-quality, natural voice synthesis for Luna's speech system. This guide will help you set up Kokoro TTS as Luna's voice engine.

## Installation Options

### Option 1: Kokoro Voice API (Recommended)
A production-grade TTS server with multiple voices and advanced features.

#### 1. Clone the Repository
```bash
git clone https://github.com/nodeblackbox/Kokoro-Voice-Api.git
cd Kokoro-Voice-Api
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Start the Server
```bash
python kokoro_api.py
```

The server will start on `http://localhost:5000` by default.

#### 4. Test the API
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello, I am Luna!", "voice": "af_heart"}' \
  http://localhost:5000/v1/audio/speech
```

### Option 2: Kokoro Web
A browser-based AI voice generator with web interface.

#### 1. Clone the Repository
```bash
git clone https://github.com/eduardolat/kokoro-web.git
cd kokoro-web
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Run the Application
```bash
python app.py
```

Access the web interface at `http://localhost:5000`.

### Option 3: Kokoro TTS CLI Tool
A command-line tool for batch processing.

#### 1. Install via pip
```bash
pip install kokoro-tts
```

#### 2. Test Installation
```bash
kokoro-tts --help
```

## Configuration

### 1. Enable Kokoro TTS in Luna
Edit `kokoro_tts_config.json`:
```json
{
  "enabled": true,
  "api_url": "http://localhost:5000",
  "voice": "af_heart"
}
```

### 2. Available Voices
- `af_heart` - Female English (US) - Default
- `am_adam` - Male English (US)
- `af_sarah` - Female English (UK)
- `am_james` - Male English (UK)
- `af_emma` - Female English (AU)
- `am_liam` - Male English (AU)
- `af_sophie` - Female French
- `am_pierre` - Male French
- `af_yuki` - Female Japanese
- `am_hiroshi` - Male Japanese
- `af_mina` - Female Korean
- `am_jin` - Male Korean
- `af_mei` - Female Chinese
- `am_wei` - Male Chinese

### 3. Voice Profiles
Luna comes with pre-configured voice profiles for different moods:
- **soft** - Gentle, calm voice
- **cheeky** - Playful, cheerful voice
- **sultry** - Seductive, lower pitch
- **excited** - Energetic, higher pitch
- **tsundere_cold** - Cold, dismissive
- **tsundere_arrogant** - Superior, bratty
- **tsundere_sassy** - Quick-witted, sassy
- **tsundere_denial** - Flustered, emotional
- **tsundere_caring** - Gentle, hidden caring

## Integration with Luna

### 1. Automatic Integration
Once enabled, Luna will automatically use Kokoro TTS for all speech output.

### 2. Manual Control
You can control Kokoro TTS through Luna's command system:
- `/kokoro status` - Check status
- `/kokoro test` - Test connection
- `/kokoro voices` - List available voices
- `/kokoro voice <voice_name>` - Change voice
- `/kokoro speak <text>` - Test speech

### 3. Mood-Based Voice Selection
Luna automatically selects appropriate voice profiles based on her mood:
- Happy/cheerful → `cheeky` or `excited`
- Seductive/flirty → `sultry`
- Tsundere moods → appropriate tsundere profile
- Default → `soft`

## Advanced Features

### Voice Blending
Kokoro supports blending multiple voices:
```bash
kokoro-tts input.txt output.wav --voice "af_heart:60,am_adam:40"
```

### Custom Voice Profiles
You can create custom voice profiles by editing `kokoro_tts_config.json`:
```json
{
  "voice_profiles": {
    "custom_mood": {
      "voice": "af_heart",
      "speed": 1.1,
      "pitch": 1.05,
      "volume": 0.9,
      "style": "custom"
    }
  }
}
```

### Rate Limiting
Kokoro TTS includes built-in rate limiting:
- Minimum 500ms between requests
- Daily limit of 1000 requests
- Automatic fallback to Edge TTS if limits exceeded

## Troubleshooting

### Common Issues

1. **Server Not Running**
   - Check if Kokoro server is started
   - Verify port 5000 is available
   - Check firewall settings

2. **Voice Not Available**
   - Verify voice name is correct
   - Check if voice is supported by your Kokoro installation
   - Try default voice `af_heart`

3. **Audio Playback Issues**
   - Ensure `playsound` library is installed
   - Check audio device settings
   - Verify temporary files are being created

4. **Performance Issues**
   - Reduce request frequency
   - Use voice caching
   - Consider using local Kokoro installation

### Debug Mode
Enable debug logging by setting environment variable:
```bash
export LUNA_DEBUG=1
```

## Performance Optimization

### 1. Voice Caching
Luna automatically caches generated audio to improve performance.

### 2. Async Processing
Kokoro TTS uses async processing to prevent blocking.

### 3. Fallback System
If Kokoro TTS fails, Luna automatically falls back to Edge TTS.

## Support

For issues with Kokoro TTS integration:
1. Check Luna's console output for error messages
2. Verify Kokoro server is running and accessible
3. Test with simple text first
4. Check network connectivity

For Kokoro TTS specific issues:
- [Kokoro Voice API GitHub](https://github.com/nodeblackbox/Kokoro-Voice-Api)
- [Kokoro Web GitHub](https://github.com/eduardolat/kokoro-web)
- [Kokoro TTS CLI GitHub](https://github.com/nazdridoy/kokoro-tts)
