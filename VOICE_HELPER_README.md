# 🎤 Discord Voice Helper

A JavaScript-based Discord voice connection helper that works around Discord.py's voice handshake timeout issues. This provides a more reliable voice connection system for Luna AI.

## 🚀 Features

- **Reliable Voice Connections**: Uses Discord.js which handles voice connections more reliably
- **Python Integration**: Seamless integration with your existing Python Discord bot
- **Keepalive System**: Maintains voice connections with automatic reconnection
- **Audio Playback**: Play audio files in voice channels
- **Cross-Platform**: Works on Windows, macOS, and Linux

## 📋 Requirements

- Node.js 16.0.0 or higher
- npm (comes with Node.js)
- Discord bot token
- Python 3.8+ (for integration)

## 🛠️ Installation

1. **Run the setup script:**
   ```bash
   python setup_voice_helper.py
   ```

2. **Edit the .env file:**
   ```bash
   # Edit .env file and add your Discord bot token
   DISCORD_BOT_TOKEN=your_actual_bot_token_here
   ```

3. **Test the installation:**
   ```bash
   # On Unix/Linux
   ./start_voice_helper.sh status
   
   # On Windows
   start_voice_helper.bat status
   ```

## 🔧 Usage

### Command Line Interface

```bash
# Connect to voice channel
node discord_voice_helper.js connect <guildId> <channelId>

# Disconnect from voice channel
node discord_voice_helper.js disconnect

# Play audio file
node discord_voice_helper.js play <audioPath>

# Check connection status
node discord_voice_helper.js status

# Reconnect to voice channel
node discord_voice_helper.js reconnect
```

### Python Integration

```python
from discord_voice_bridge import start_voice_bridge, connect_to_voice_channel, play_audio_in_voice

# Start the voice bridge
await start_voice_bridge("your_bot_token")

# Connect to voice channel
await connect_to_voice_channel("guild_id", "channel_id")

# Play audio
await play_audio_in_voice("path/to/audio.mp3")
```

## 🎯 How It Works

1. **JavaScript Helper**: The Node.js script handles Discord voice connections using Discord.js
2. **Python Bridge**: The Python script communicates with the JavaScript helper via subprocess
3. **Reliable Connections**: Discord.js handles voice connections more reliably than Discord.py
4. **Keepalive System**: Maintains connections with automatic reconnection on failure

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with:

```env
DISCORD_BOT_TOKEN=your_discord_bot_token
NODE_PATH=node
```

### Voice Helper Settings

The voice helper automatically:
- Connects to voice channels
- Maintains connections with keepalive
- Handles reconnection on failure
- Plays audio files

## 🔧 Troubleshooting

### Common Issues

1. **Node.js not found:**
   - Install Node.js from https://nodejs.org/
   - Make sure it's in your PATH

2. **Dependencies not installed:**
   - Run `npm install` in the project directory
   - Check that package.json exists

3. **Bot token not set:**
   - Edit .env file and add your Discord bot token
   - Make sure the token is valid

4. **Voice connection fails:**
   - Check bot permissions (Connect, Speak)
   - Verify guild and channel IDs
   - Check internet connection

### Debug Mode

Enable debug logging by setting environment variable:

```bash
export DEBUG=discord:*
node discord_voice_helper.js
```

## 📊 Monitoring

### Connection Status

The helper provides real-time status updates:

```json
{
  "is_connected": true,
  "guild_id": "123456789",
  "channel_id": "987654321",
  "connection_status": "Ready",
  "keep_alive_active": true
}
```

### Logs

The helper logs all activities:
- Connection attempts
- Audio playback
- Keepalive checks
- Error messages

## 🔒 Security

- Bot token is stored in .env file (not committed to git)
- Voice helper runs as a separate process
- No sensitive data is logged

## 🚀 Performance

- **Low Latency**: Direct Discord.js connection
- **Reliable**: Handles Discord's voice connection quirks
- **Efficient**: Minimal resource usage
- **Stable**: Automatic reconnection on failure

## 📝 API Reference

### Python Functions

```python
# Start the voice bridge
await start_voice_bridge(bot_token: str, node_path: str = "node") -> bool

# Stop the voice bridge
await stop_voice_bridge()

# Connect to voice channel
await connect_to_voice_channel(guild_id: str, channel_id: str) -> bool

# Disconnect from voice channel
await disconnect_from_voice_channel() -> bool

# Play audio in voice channel
await play_audio_in_voice(audio_path: str) -> bool

# Get connection status
get_voice_connection_status() -> Dict[str, Any]
```

### JavaScript Commands

```bash
# Connect to voice channel
connect <guildId> <channelId>

# Disconnect from voice channel
disconnect

# Play audio file
play <audioPath>

# Check connection status
status

# Reconnect to voice channel
reconnect
```

## 🤝 Integration with Luna

To integrate with your existing Luna Discord bot:

1. **Start the voice bridge in your main application:**
   ```python
   from discord_voice_bridge import start_voice_bridge
   
   # Start the bridge
   await start_voice_bridge(discord_bot_token)
   ```

2. **Use voice functions in your Discord bot:**
   ```python
   from discord_voice_bridge import connect_to_voice_channel, play_audio_in_voice
   
   # Connect to voice when user joins
   await connect_to_voice_channel(guild_id, channel_id)
   
   # Play TTS audio
   await play_audio_in_voice("tts_output.mp3")
   ```

## 📞 Support

For issues and questions:
1. Check this README
2. Review the troubleshooting section
3. Check console logs for error messages
4. Open an issue in the main project repository

## 📝 License

This helper is part of the Luna AI project. See main project license for details.

## 🔄 Updates

To update the voice helper:

1. Pull the latest changes
2. Run `npm install` to update dependencies
3. Restart the voice helper

## 🎯 Future Improvements

- WebSocket communication between Python and JavaScript
- Multiple voice channel support
- Audio streaming capabilities
- Better error handling and recovery
- Performance monitoring and metrics
