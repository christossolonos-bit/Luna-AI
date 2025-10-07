# demo_memory_reflection.py
"""Demonstrate Luna's Memory Reflection System"""

from luna_memory_reflection import get_dynamic_self_talk_thought

print("=" * 70)
print("  Luna's Dynamic Memory-Based Self-Talk Demonstration")
print("=" * 70)
print("\nGenerating thoughts based on real Discord/Twitch memories...\n")

for i in range(5):
    thought = get_dynamic_self_talk_thought()
    if thought:
        print(f"{i+1}. {thought}\n")
    else:
        print(f"{i+1}. [No memory available]\n")

print("=" * 70)
print("\nThese thoughts are dynamically generated from:")
print("  - Real usernames from Discord and Twitch")
print("  - Actual messages users sent")
print("  - Real timestamps and activity data")
print("  - Detected topics and conversation context")
print("\nNo more static pre-written sentences!")
print("=" * 70)
