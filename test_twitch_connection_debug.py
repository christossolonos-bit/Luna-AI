#!/usr/bin/env python3
"""
Test Twitch connection with debug output
"""
import time
from twitch_api_chat import initialize_twitch_api_chat, start_twitch_api_chat

def test_callback(username, message, channel):
    """Test callback function"""
    print(f"✅ CALLBACK TRIGGERED: [{channel}] {username}: {message}")
    return None  # Don't send a response for testing

# Twitch configuration
TWITCH_CONFIG = {
    "token": "m2iw2ccv12vufrpfpt25bi25n97zc7",
    "client_id": "gp762nuuoqcoxypju8c569th9wz7q5",
    "nick": "solosluna",
    "channels": ["solonaras"]
}

print("🎮 Testing Twitch connection...")
print(f"📋 Config: {TWITCH_CONFIG}")

# Initialize
if initialize_twitch_api_chat(
    token=TWITCH_CONFIG["token"],
    client_id=TWITCH_CONFIG["client_id"],
    nick=TWITCH_CONFIG["nick"],
    channels=TWITCH_CONFIG["channels"],
    callback=test_callback
):
    print("✅ Twitch API chat initialized")
    
    # Start
    if start_twitch_api_chat():
        print("✅ Twitch API chat started")
        print("🎮 Listening for messages... (Press Ctrl+C to stop)")
        print("💬 Try sending a message in the solonaras Twitch channel!")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Stopping...")
    else:
        print("❌ Failed to start Twitch API chat")
else:
    print("❌ Failed to initialize Twitch API chat")
