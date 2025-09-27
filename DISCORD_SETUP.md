# 🤖 Luna Discord Bot Setup Guide

## 📋 Prerequisites

1. **Discord Bot Account**: You already have a Discord bot account
2. **Python Dependencies**: Install required packages
3. **Bot Token**: Your Discord bot token

## 🚀 Quick Setup

### 1. Install Dependencies

```bash
pip install discord.py
```

### 2. Configure Your Bot

1. **Get Your Bot Token**:
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Select your bot application
   - Go to "Bot" section
   - Copy the token

2. **Set Bot Permissions**:
   - In Discord Developer Portal, go to "OAuth2" > "URL Generator"
   - Select "bot" scope
   - Select these permissions:
     - Send Messages
     - Read Message History
     - Use Slash Commands
     - Embed Links
     - Read Messages/View Channels
     - Add Reactions

3. **Configure Luna**:
   - Edit `discord_config.json`
   - Add your bot token:
   ```json
   {
     "bot_token": "YOUR_BOT_TOKEN_HERE",
     "enabled": true
   }
   ```

### 3. Invite Bot to Server

1. Use the generated OAuth2 URL from Discord Developer Portal
2. Select your server
3. Authorize the bot

## 🎮 Features

### 💬 Chat Integration
- **Mentions**: Luna responds when mentioned
- **Replies**: Responds to direct replies
- **Luna Name**: Always responds when "Luna" is mentioned anywhere
- **Keywords**: Responds to certain keywords (configurable)
- **Rate Limiting**: Prevents spam responses

### 🔧 Commands
- `!ping` - Check if Luna is responsive
- `!status` - View Luna's current status
- `!help` - Show available commands
- `!vision` - Toggle desktop vision mode
- `!joinvoice` - Join your voice channel
- `!leave` - Leave voice channel

### 🎤 Voice Features
- **Voice Channel Support**: Luna can join voice channels and speak her responses
- **TTS Integration**: Uses Luna's TTS system for natural voice responses
- **Auto-Voice**: Automatically plays TTS when responding in voice channels
- **Voice Commands**: Easy join/leave voice channel commands

### 📊 Statistics
- Messages processed
- Responses sent
- Active channels
- Uptime tracking

## ⚙️ Configuration Options

### `discord_config.json` Settings

```json
{
  "bot_token": "YOUR_BOT_TOKEN",
  "enabled": true,
  "response_cooldown": 2.0,
  "auto_respond": true,
  "respond_to_mentions": true,
  "respond_to_replies": true,
  "respond_to_keywords": true,
  "keyword_response_chance": 0.3,
  "respond_to_luna_mention": true,
  "max_response_length": 2000,
  "activity_type": "watching",
  "activity_text": "your desktop 👀"
}
```

### Configuration Explained

- **`bot_token`**: Your Discord bot token
- **`enabled`**: Enable/disable Discord integration
- **`response_cooldown`**: Seconds between responses per channel
- **`auto_respond`**: Enable automatic responses
- **`respond_to_mentions`**: Respond when mentioned
- **`respond_to_replies`**: Respond to direct replies
- **`respond_to_keywords`**: Respond to keyword triggers
- **`keyword_response_chance`**: Probability of responding to keywords (0.0-1.0)
- **`respond_to_luna_mention`**: Always respond when "Luna" is mentioned
- **`max_response_length`**: Maximum Discord message length
- **`activity_type`**: Bot activity type (playing, watching, listening)
- **`activity_text`**: Bot activity text

## 🔧 Integration with Main App

### Starting Discord Bot

```python
from luna_discord import start_discord_bot, stop_discord_bot

# Start bot with Luna AI callback
await start_discord_bot(token, luna_ai_callback)

# Stop bot
await stop_discord_bot()
```

### Luna AI Callback

The Discord bot calls your Luna AI function with this format:
```
[Discord] Username in #channel: message content
```

Your Luna AI should respond naturally to this format.

## 🛠️ Troubleshooting

### Common Issues

1. **Bot Not Responding**:
   - Check if bot token is correct
   - Verify bot has proper permissions
   - Check if `enabled` is set to `true`

2. **Permission Errors**:
   - Ensure bot has "Send Messages" permission
   - Check channel-specific permissions
   - Verify bot role hierarchy

3. **Rate Limiting**:
   - Adjust `response_cooldown` in config
   - Check Discord API rate limits
   - Monitor bot logs for errors

### Debug Mode

Enable debug logging:
```json
{
  "log_level": "DEBUG"
}
```

## 📱 Usage Examples

### Basic Chat
```
User: @Luna hello!
Luna: Hello! How can I help you today?
```

### Commands
```
User: !status
Luna: [Shows status embed with statistics]
```

### Vision Integration
```
User: !vision
Luna: 🖥️ Desktop vision toggled on/off
```

## 🔒 Security Notes

- **Never share your bot token**
- **Use environment variables for production**
- **Set up proper channel restrictions**
- **Monitor bot activity regularly**

## 📈 Advanced Features

### Custom Commands
Add custom commands by modifying `luna_discord.py`:

```python
@self.bot.command(name='custom')
async def custom_command(ctx):
    await ctx.send("Custom response!")
```

### Channel Restrictions
```json
{
  "allowed_channels": [123456789, 987654321],
  "blocked_channels": [111111111]
}
```

### User Restrictions
```json
{
  "allowed_users": [123456789, 987654321],
  "blocked_users": [111111111]
}
```

## 🎯 Next Steps

1. **Test the bot** in a private channel
2. **Configure permissions** for your server
3. **Customize responses** in Luna's personality
4. **Monitor performance** and adjust settings
5. **Add custom commands** as needed

## 📞 Support

If you encounter issues:
1. Check the logs in your terminal
2. Verify Discord bot permissions
3. Test with a simple message first
4. Check network connectivity

---

**Happy chatting with Luna! 🤖✨**
