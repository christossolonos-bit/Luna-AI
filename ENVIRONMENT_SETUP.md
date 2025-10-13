# 🔧 Environment Setup Guide

## Create .env File

Create a `.env` file in the Luna Waifu directory with your tokens:

```bash
# Twitch Configuration
TWITCH_ACCESS_TOKEN=i4uj12hcmjn649mpnty4oslg16q4vs
TWITCH_REFRESH_TOKEN=feqvsqlfk5elj7bz5igsdfiq22khui0tscdifx68z7tzlsvbu8
TWITCH_CLIENT_ID=gp762nuuoqcoxypju8c569th9wz7q5
TWITCH_USERNAME=solosluna
TWITCH_CHANNEL=solonaras

# Discord Configuration  
DISCORD_TOKEN=your_discord_bot_token_here

# Luna Configuration
LUNA_NAME=Luna
LUNA_PERSONALITY=playful
LUNA_ENERGY=0.8
```

## Security Note

The `.env` file is automatically ignored by git, so your tokens won't be uploaded to GitHub.

## Current Status

✅ **Twitch tokens configured** - Luna can connect to solonaras channel
⚠️ **Discord token needs update** - Current token is invalid

## Next Steps

1. **For Twitch**: Tokens are ready! Click the Twitch button in Luna's GUI
2. **For Discord**: Get a fresh Discord bot token and update DISCORD_TOKEN in .env

## How Luna Loads Tokens

1. **First**: Checks environment variables (.env file)
2. **Fallback**: Uses config files (discord_config.json, twitch_config.json)

This gives you flexibility to use either method!
