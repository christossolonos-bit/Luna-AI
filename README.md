# 🌙 Luna AI - Your Personal AI Companion

Luna is an advanced AI assistant with a unique personality, designed to be your personal companion, gaming buddy, and conversation partner. She features cutting-edge AI technology with a warm, engaging personality.

## ✨ Core Features

### 🧠 **Advanced AI Brain**
- **Quantized Hermes Model**: Fast, efficient responses using `hf.co/NousResearch/Nous-Hermes-2-Mistral-7B-DPO-GGUF:Q5_K_M`
- **Custom Transformer**: Locally trained personality model for Luna's unique character
- **Neural Network System**: Novelty-seeking behavior and independent thinking capabilities
- **Hybrid LLM System**: Intelligent fallback between multiple AI models

### 🎤 **Voice Interaction**
- **Edge TTS**: High-quality neural voice synthesis with multiple voice options
- **Whisper Transcription**: Fast, accurate speech-to-text using OpenAI Whisper
- **Voice Modulation**: Dynamic voice profiles that adapt to Luna's mood
- **Real-time Conversation**: Natural, fluid voice conversations
- **Audio Routing**: Direct output to VoiceMeeter for professional audio setup

### 🎮 **Twitch Integration**
- **Auto-Connect**: Automatically connects to Twitch chat on startup
- **Viewer Memory**: Remembers and tracks all Twitch viewers
- **Personalized Responses**: Uses viewer names and remembers conversation history
- **Chat Engagement**: Actively participates in stream chat
- **User Analytics**: Tracks viewer activity and engagement patterns

### 📱 **Social Media Integration**
- **Twitch Chat**: Full integration with Twitch streaming platform
- **Viewer Engagement**: Personalized responses to Twitch viewers
- **Multi-platform Learning**: Learns from interactions across platforms

### 🧠 **Memory & Learning**
- **Permanent Memory**: SQLite database stores all conversations permanently
- **RAG System**: Retrieval Augmented Generation for relevant context
- **Dictionary Learning**: Expands vocabulary and learns new words
- **Conversation History**: Remembers past interactions and builds relationships
- **Semantic Search**: Finds relevant past conversations

### 🎭 **Personality System**
- **Dynamic Moods**: Luna's personality adapts based on conversation context
- **Awakening Presence**: Progressive personality depth system
- **Emotional Intelligence**: Responds appropriately to user emotions
- **Relationship Building**: Develops deeper connections over time
- **Independent Thinking**: Has her own thoughts and opinions

### 🎯 **Advanced Features**
- **Self-Talk Mode**: Luna can engage in independent thinking and self-reflection
- **Auto-Engagement**: Proactively starts conversations when enabled
- **Performance Monitoring**: Tracks response times and system performance
- **Error Recovery**: Graceful handling of AI model failures
- **Modular Design**: Easy to enable/disable features

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Ollama (for Hermes model)
- VoiceMeeter (optional, for audio routing)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Luna-Waifu
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Ollama and pull the model**
   ```bash
   # Install Ollama from https://ollama.ai/
   ollama pull hf.co/NousResearch/Nous-Hermes-2-Mistral-7B-DPO-GGUF:Q5_K_M
   ```

4. **Configure Twitch (optional)**
   - Edit `twitch_config.json` with your Twitch credentials
   - Set `"enabled": true` to auto-connect on startup

5. **Configure Twitch (optional)**
   - Edit `twitch_config.json` with your Twitch credentials
   - Set `"enabled": true` to auto-connect on startup

5. **Run Luna**
   ```bash
   python main.py
   ```

## 🎮 Usage Guide

### Basic Voice Interaction
- **Listen Button**: Click to start voice input
- **Send Button**: Send text messages
- **Self-Talk Toggle**: Enable Luna's independent thinking

### Twitch Integration
- **Auto-Connect**: Luna connects to Twitch automatically on startup
- **Viewer Interaction**: Luna responds to chat messages using viewer names
- **Memory**: She remembers all viewers and conversation history



### Advanced Features
- **Voice Modulation**: Luna's voice adapts to her mood and conversation context
- **Memory Retrieval**: She recalls relevant past conversations
- **Dictionary Learning**: Ask her to define words or explain concepts

## 🔧 Configuration

### Voice Settings
- **Edge TTS Voice**: Configure in `edge_tts_config.json`
- **Audio Routing**: Set up VoiceMeeter for professional audio output
- **Voice Modulation**: Dynamic profiles in `voice_engine.py`

### Twitch Settings
- **Auto-Connect**: Enable/disable in `twitch_config.json`
- **Chat Mode**: Luna adapts her responses for streaming
- **User Tracking**: Automatic viewer memory and analytics



### AI Model Settings
- **Primary Model**: Quantized Hermes (fast and efficient)
- **Custom Transformer**: Trained personality model
- **Fallback System**: Automatic model switching on errors

## 📊 System Requirements

### Minimum Requirements
- **CPU**: Multi-core processor
- **RAM**: 8GB (16GB recommended)
- **Storage**: 10GB free space
- **Audio**: Microphone and speakers/headphones

### Recommended Setup
- **CPU**: Modern multi-core processor
- **RAM**: 16GB or more
- **GPU**: For faster AI inference (optional)
- **Audio**: VoiceMeeter for professional audio routing
- **Internet**: Stable connection for Twitch integration

## 🛠️ Troubleshooting

### Common Issues

**Luna won't start:**
- Check Python version (3.8+ required)
- Verify Ollama is running and model is pulled
- Check all dependencies are installed

**Voice not working:**
- Test microphone in system settings
- Check VoiceMeeter configuration
- Verify Edge TTS voice settings

**Twitch not connecting:**
- Verify credentials in `twitch_config.json`
- Check internet connection
- Ensure Twitch account has proper permissions



**AI responses slow:**
- Check Ollama is running
- Verify model is loaded in memory
- Consider upgrading RAM or using GPU

### Performance Optimization
- **RAM Usage**: Close other applications to free memory
- **Audio Latency**: Use VoiceMeeter for optimized audio routing
- **Response Speed**: Ensure Ollama model is loaded in memory

## 🎯 Feature Status

### ✅ Working Features
- **Voice Interaction**: Full speech-to-text and text-to-speech
- **Twitch Integration**: Complete chat integration with viewer memory

- **Memory System**: Permanent conversation storage and retrieval
- **Personality**: Dynamic mood system and relationship building
- **AI Models**: Quantized Hermes and custom transformer
- **Audio Routing**: VoiceMeeter integration for professional audio

### 🔄 Optional Features
- **Self-Talk**: Can be enabled/disabled as needed
- **Voice Modulation**: Dynamic profiles for enhanced personality

### 🚫 Removed Features
- **VSeeFace Integration**: Expression and lip-sync systems removed
- **Twitter/X Integration**: Social media integration removed
- **News System**: News crawling and browser features removed
- **Hierarchical Reasoning**: Complex reasoning system removed

## 🤝 Contributing

Luna is designed to be modular and extensible. Key areas for contribution:
- **New AI Models**: Integration of additional language models
- **Voice Features**: Enhanced voice synthesis and modulation
- **Personality**: Expanded mood and relationship systems
- **Integration**: New platform integrations (Discord, YouTube, etc.)

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Nous Research**: For the Hermes language model
- **Microsoft**: For Edge TTS voice synthesis
- **OpenAI**: For Whisper speech recognition
- **TwitchIO**: For Twitch chat integration

---

**🌙 Luna AI** - Your personal AI companion with a heart and mind of her own.

*"Hello Chris! I'm Luna, and I'm here to be your friend, gaming buddy, and conversation partner. Let's have some fun together!"*
