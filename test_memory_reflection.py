# test_memory_reflection.py
"""
Test Luna's Memory Reflection System
Verifies that dynamic thoughts are generated from real memories
"""

from luna_memory_reflection import luna_memory_reflection, get_dynamic_self_talk_thought

print("=" * 70)
print("  Testing Luna's Memory Reflection System")
print("=" * 70)

# Test 1: Check databases
print("\n[TEST 1] Checking SQL Databases...")
try:
    import os
    discord_exists = os.path.exists("luna_discord_users.db")
    twitch_exists = os.path.exists("luna_twitch_users.db")
    
    print(f"  Discord DB exists: {discord_exists}")
    print(f"  Twitch DB exists: {twitch_exists}")
except Exception as e:
    print(f"  [ERROR] {e}")

# Test 2: Get recent activity
print("\n[TEST 2] Getting Recent Activity...")
try:
    discord_activity = luna_memory_reflection.get_recent_discord_activity(hours=24)
    twitch_activity = luna_memory_reflection.get_recent_twitch_activity(hours=24)
    
    print(f"  Discord messages (last 24h): {len(discord_activity)}")
    print(f"  Twitch messages (last 24h): {len(twitch_activity)}")
    
    if discord_activity:
        print(f"\n  Sample Discord message:")
        msg = discord_activity[0]
        print(f"    - User: {msg['username']}")
        print(f"    - Message: {msg['message'][:50]}...")
        print(f"    - Channel: {msg['channel']}")
    
    if twitch_activity:
        print(f"\n  Sample Twitch message:")
        msg = twitch_activity[0]
        print(f"    - User: {msg['username']}")
        print(f"    - Message: {msg['message'][:50]}...")
        print(f"    - Channel: {msg['channel']}")
        
except Exception as e:
    print(f"  [ERROR] {e}")

# Test 3: Get active users
print("\n[TEST 3] Getting Active Users...")
try:
    active_users = luna_memory_reflection.get_active_users(hours=24)
    
    print(f"  Active Discord users: {len(active_users['discord'])}")
    for user in active_users['discord'][:3]:
        print(f"    - {user['username']}: {user['messages']} messages")
    
    print(f"\n  Active Twitch users: {len(active_users['twitch'])}")
    for user in active_users['twitch'][:3]:
        print(f"    - {user['username']}: {user['messages']} messages")
        
except Exception as e:
    print(f"  [ERROR] {e}")

# Test 4: Generate dynamic thoughts
print("\n[TEST 4] Generating Dynamic Thoughts...")
try:
    for i in range(3):
        thought = get_dynamic_self_talk_thought(has_recent_activity=True)
        if thought:
            print(f"\n  Thought {i+1}:")
            print(f"    {thought[:100]}...")
        else:
            print(f"  Thought {i+1}: [No memory-based thought generated]")
            
except Exception as e:
    print(f"  [ERROR] {e}")

# Test 5: Topic extraction
print("\n[TEST 5] Testing Topic Extraction...")
try:
    all_activity = discord_activity + twitch_activity if discord_activity or twitch_activity else []
    if all_activity:
        topics = luna_memory_reflection.extract_topics_from_messages(all_activity)
        print(f"  Detected topics: {', '.join(topics) if topics else 'None'}")
    else:
        print(f"  No activity to extract topics from")
except Exception as e:
    print(f"  [ERROR] {e}")

print("\n" + "=" * 70)
print("  Test Complete!")
print("=" * 70)
