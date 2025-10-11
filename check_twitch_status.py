# check_twitch_status.py
"""
Quick script to check Twitch integration status for Luna
"""

import sys

print("🎮 Luna Twitch Integration Status Check")
print("=" * 50)

# Check twitch_api_chat.py
try:
    from twitch_api_chat import TwitchAPIChat, twitch_api_manager
    print("✅ twitch_api_chat.py imported successfully")
except ImportError as e:
    print(f"❌ Could not import twitch_api_chat.py: {e}")
    sys.exit(1)

# Check required packages
packages = {
    'requests': None,
    'websocket': None,
}

for package_name in packages:
    try:
        __import__(package_name)
        print(f"✅ {package_name} installed")
    except ImportError:
        print(f"❌ {package_name} not installed")
        print(f"   Install with: pip install {package_name if package_name != 'websocket' else 'websocket-client'}")

# Check configuration
print("\n📋 Checking Twitch Configuration...")
try:
    from main import TWITCH_CONFIG, TWITCH_AVAILABLE
    
    print(f"✅ TWITCH_AVAILABLE: {TWITCH_AVAILABLE}")
    print(f"✅ Twitch enabled: {TWITCH_CONFIG.get('enabled', False)}")
    print(f"✅ Bot nickname: {TWITCH_CONFIG.get('nick', 'N/A')}")
    print(f"✅ Channels: {TWITCH_CONFIG.get('channels', [])}")
    
    # Don't print sensitive tokens
    token_exists = bool(TWITCH_CONFIG.get('token'))
    client_id_exists = bool(TWITCH_CONFIG.get('client_id'))
    
    print(f"✅ OAuth token configured: {token_exists}")
    print(f"✅ Client ID configured: {client_id_exists}")
    
except Exception as e:
    print(f"❌ Error checking configuration: {e}")

print("\n" + "=" * 50)
print("🎮 Status check complete!")
print("\nTo start Luna with Twitch:")
print("1. Ensure TWITCH_CONFIG['enabled'] = True in main.py")
print("2. Run: python main.py")
print("3. Luna will auto-connect to Twitch chat on startup")
print("\nTwitch bot will:")
print("- Connect to channels: solonaras")
print("- Respond as: solosluna")
print("- Use ALL Luna features (emotions, memory, relationships, etc.)")
print("- TTS enabled for Twitch responses")

