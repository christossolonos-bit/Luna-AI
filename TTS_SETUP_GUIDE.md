# 🎤 Luna TTS Setup Guide - Ava Multilingual Voice

## Quick Start

Luna now speaks with **Ava's multilingual voice** using ElevenLabs TTS! She can speak in multiple languages naturally.

---

## 🎯 Features

- ✅ **Ava Multilingual Voice**: Natural, expressive speech
- ✅ **Multiple Languages**: Supports 28+ languages
- ✅ **Voice Toggle**: Turn TTS on/off with button
- ✅ **Real-time Speech**: Luna speaks her responses
- ✅ **Voice + Text**: Both voice input and output

---

## 📦 Installation

### 1. Install Dependencies
```bash
pip install -r requirements_voice.txt
```

### 2. Get ElevenLabs API Key
1. Go to [ElevenLabs.io](https://elevenlabs.io)
2. Sign up for a free account
3. Go to Profile → API Keys
4. Copy your API key

### 3. Configure API Key
Edit `luna_clean.py` and add your API key:

```python
# TTS Configuration
TTS_CONFIG = {
    "voice": "ava_multilingual",
    "model": "eleven_multilingual_v2",
    "api_key": "your_api_key_here",  # Add your key here
    "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.8,
        "style": 0.2,
        "use_speaker_boost": True
    }
}
```

---

## 🎮 How to Use

### TTS Controls:
- **TTS Button**: Toggle speech on/off
- **🔇 TTS OFF**: Luna only texts
- **🔊 TTS ON**: Luna speaks her responses

### Voice Chat Flow:
1. **Hold SPACEBAR** → Speak to Luna
2. **Release SPACEBAR** → Luna processes your speech
3. **Luna responds** → Text + Speech (if TTS enabled)

---

## 🌍 Supported Languages

Ava's multilingual voice supports:

| Language | Code | Example |
|----------|------|---------|
| **English** | en | "Hello, how are you?" |
| **Spanish** | es | "Hola, ¿cómo estás?" |
| **French** | fr | "Bonjour, comment allez-vous?" |
| **German** | de | "Hallo, wie geht es dir?" |
| **Italian** | it | "Ciao, come stai?" |
| **Portuguese** | pt | "Olá, como você está?" |
| **Dutch** | nl | "Hallo, hoe gaat het?" |
| **Polish** | pl | "Cześć, jak się masz?" |
| **Russian** | ru | "Привет, как дела?" |
| **Chinese** | zh | "你好，你好吗？" |
| **Japanese** | ja | "こんにちは、元気ですか？" |
| **Korean** | ko | "안녕하세요, 어떻게 지내세요?" |

**And 16+ more languages!**

---

## ⚙️ Voice Settings

### Customize Ava's Voice:
```python
"voice_settings": {
    "stability": 0.5,        # 0.0-1.0 (voice consistency)
    "similarity_boost": 0.8, # 0.0-1.0 (voice similarity)
    "style": 0.2,           # 0.0-1.0 (style exaggeration)
    "use_speaker_boost": True # Boost speaker similarity
}
```

### Voice Characteristics:
- **Stability**: Lower = more expressive, Higher = more consistent
- **Similarity Boost**: Higher = more like original voice
- **Style**: Higher = more dramatic, Lower = more natural
- **Speaker Boost**: Enhances voice clarity

---

## 🔧 Troubleshooting

### "TTS not available - No ElevenLabs API key"
1. Check you added your API key to `TTS_CONFIG`
2. Verify the key is correct
3. Make sure you have ElevenLabs credits

### "Speech generation error"
1. Check internet connection
2. Verify API key is valid
3. Check ElevenLabs service status
4. Ensure you have remaining credits

### "Audio playback not available"
1. Install pygame: `pip install pygame`
2. Check your speakers/headphones
3. Test with other audio applications

### "No sound playing"
1. Check volume levels
2. Verify audio output device
3. Test with other applications
4. Check Windows audio settings

---

## 💰 ElevenLabs Pricing

### Free Tier:
- ✅ 10,000 characters/month
- ✅ 3 custom voices
- ✅ Standard voices

### Creator Plan ($5/month):
- ✅ 30,000 characters/month
- ✅ 10 custom voices
- ✅ Professional voices

### Pro Plan ($22/month):
- ✅ 100,000 characters/month
- ✅ 30 custom voices
- ✅ All voices + cloning

---

## 🎯 Tips for Best Results

### Text Preparation:
- ✅ Use punctuation for natural pauses
- ✅ Avoid emojis in TTS (they're filtered out)
- ✅ Keep responses under 500 characters for speed

### Voice Quality:
- ✅ Use good speakers/headphones
- ✅ Reduce background noise
- ✅ Adjust system volume appropriately

### Performance:
- ✅ TTS adds 2-5 seconds to response time
- ✅ Turn off TTS for faster text-only chat
- ✅ Internet required for speech generation

---

## 🔄 Complete Voice Chat Flow

```
1. User holds SPACEBAR
   ↓
2. Microphone records speech
   ↓
3. Google Speech Recognition transcribes
   ↓
4. Luna generates response (DNA memory)
   ↓
5. Response displayed as text
   ↓
6. ElevenLabs generates Ava's speech
   ↓
7. Luna speaks the response
   ↓
8. Conversation saved to DNA memory
```

---

## 🧬 Voice + DNA Memory

Every voice conversation creates DNA strands:

```
🎤 Voice: "I love anime"
🧬 DNA Memory: Encoded with voice context
💬 Luna: "Me too! What's your favorite?" (spoken by Ava)
🔄 Future: Luna remembers your anime preferences!
```

---

## 🚀 Advanced Features

### Custom Voice Settings:
```python
# More expressive Luna
"voice_settings": {
    "stability": 0.3,        # More variable
    "similarity_boost": 0.9, # Very similar to Ava
    "style": 0.4,           # More dramatic
    "use_speaker_boost": True
}

# More consistent Luna
"voice_settings": {
    "stability": 0.8,        # More consistent
    "similarity_boost": 0.7, # Good similarity
    "style": 0.1,           # Natural
    "use_speaker_boost": True
}
```

### Multiple Languages:
Luna automatically detects language and responds appropriately:
- Speak English → Luna responds in English
- Speak Spanish → Luna responds in Spanish
- Mix languages → Luna adapts naturally

---

## 📞 Support

### ElevenLabs Issues:
1. Check [ElevenLabs Status](https://status.elevenlabs.io)
2. Verify API key in dashboard
3. Check credit balance
4. Contact ElevenLabs support

### Luna TTS Issues:
1. Check internet connection
2. Verify API key configuration
3. Test with simple text first
4. Check console for error messages

---

## 🎉 What's Next?

### Planned Features:
- 🎵 **Voice Cloning**: Custom Luna voice
- 🎛️ **Voice Commands**: Special voice shortcuts
- 🌍 **Auto Language Detection**: Seamless language switching
- 📱 **Mobile TTS**: Voice on mobile devices
- 🎭 **Emotional TTS**: Voice changes with mood

---

**Ready to hear Luna speak? Set up your API key and toggle TTS on!** 🎤🌸

**Luna + Ava = Perfect Voice Companion!** 💕
