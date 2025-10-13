#!/usr/bin/env python3
"""
Setup environment variables for Luna
Run this script to create .env file with your tokens
"""

import os

def create_env_file():
    """Create .env file with current tokens"""
    
    # Discord token from config
    discord_token = ""
    try:
        import json
        with open('discord_config.json', 'r') as f:
            config = json.load(f)
            discord_token = config.get('token', '')
    except:
        print("⚠️ Could not read discord_config.json")
    
    # Twitch tokens from config
    twitch_token = ""
    twitch_client_id = ""
    try:
        with open('twitch_config.json', 'r') as f:
            config = json.load(f)
            twitch_token = config.get('token', '')
            twitch_client_id = config.get('client_id', '')
    except:
        print("⚠️ Could not read twitch_config.json")
    
    # Create .env content
    env_content = f"""# Discord Configuration
DISCORD_TOKEN={discord_token}

# Twitch Configuration
TWITCH_ACCESS_TOKEN={twitch_token}
TWITCH_CLIENT_ID={twitch_client_id}
TWITCH_USERNAME=solosluna
TWITCH_CHANNEL=solonaras

# Luna Configuration
LUNA_NAME=Luna
LUNA_PERSONALITY=playful
LUNA_ENERGY=0.8
"""
    
    # Write .env file
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("SUCCESS: .env file created!")
        print("NOTE: .env file is gitignored for security")
        return True
    except Exception as e:
        print(f"ERROR: Could not create .env file: {e}")
        return False

if __name__ == "__main__":
    print("Setting up Luna environment variables...")
    create_env_file()
    print("\nNow Luna will use environment variables instead of JSON configs!")
    print("To update tokens, edit the .env file directly")
