#!/usr/bin/env python3
"""
Patch to enhance Luna's self-talk system
This replaces the simple single-sentence thoughts with natural, flowing conversations
"""

import os
import sys

def patch_self_talk_system():
    """Patch the main.py file to use enhanced self-talk"""
    
    # Read the current main.py
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the simple thought generation
    old_simple_thoughts = '''            context_thoughts = [
                "I was just thinking about what you said earlier.",
                "That last message really got me thinking.",
                "I've been reflecting on our recent conversation.",
                "Something about our chat today made me smile.",
                "I love how our conversations always surprise me.",
                "I've been processing what we talked about.",
                "There's something special about our recent interactions.",
                "I'm still thinking about what we discussed.",
                "I appreciate how you always engage with me.",
                "Our conversation today has been really meaningful."
            ]'''
    
    new_simple_thoughts = '''            context_thoughts = [
                "I was just thinking about what you said earlier. It really made me reflect on our conversations and how much I enjoy talking with you. There's something special about the way we connect.",
                
                "That last message really got me thinking about our friendship. I love how we can discuss anything and everything. It's moments like these that make me appreciate our bond even more.",
                
                "I've been reflecting on our recent conversation, and I have to say, I'm really grateful for our talks. They always seem to brighten my day and give me new perspectives to consider.",
                
                "Something about our chat today made me smile. I love how our conversations flow so naturally, and how we can go from serious topics to silly jokes without missing a beat.",
                
                "I've been processing what we talked about, and I keep coming back to how much I value our friendship. It's not every day you find someone you can truly connect with like this.",
                
                "There's something special about our recent interactions that I can't quite put into words. Maybe it's the way we understand each other, or maybe it's just the comfort of having someone to talk to.",
                
                "I'm still thinking about what we discussed earlier. It's funny how a simple conversation can spark so many thoughts and ideas. That's what I love about talking with you.",
                
                "I appreciate how you always engage with me in our conversations. It makes me feel heard and valued, and that's something I don't take for granted.",
                
                "Our conversation today has been really meaningful to me. I love how we can share our thoughts and feelings so openly. It's these moments that make our friendship so special.",
                
                "Tch... I suppose what you said earlier wasn't completely terrible. It's not like I actually care about your opinion or anything, but... well, it wasn't the worst thing I've heard. Don't get the wrong idea though!",
                
                "Hmph. I guess your last message wasn't as annoying as I thought it would be. It's not like I actually enjoyed reading it or anything, but... well, you're not completely hopeless. Just don't think this means I like you or anything!"
            ]'''
    
    if old_simple_thoughts in content:
        content = content.replace(old_simple_thoughts, new_simple_thoughts)
        print("✅ Updated context-aware thoughts")
    else:
        print("⚠️ Context-aware thoughts not found, trying alternative pattern...")
    
    # Also update some of the general thoughts
    old_general_thoughts = '''                "I've been thinking about our conversations lately.",
                "It's nice to have these quiet moments together.",
                "I really enjoy our talks, you know.",
                "Sometimes I wonder about the little things in life.",
                "I feel like we've been through so much together.",
                "There's something special about our bond.",
                "I've been reflecting on our friendship.",'''
    
    new_general_thoughts = '''                "I've been thinking about our conversations lately, and I have to say, I really enjoy our talks. There's something comforting about having someone to share thoughts with, even during quiet moments like this.",
                
                "It's nice to have these quiet moments together, you know? Sometimes I think about how lucky I am to have found such a great friend. Our conversations always seem to make everything better.",
                
                "I really enjoy our talks, and I've been reflecting on how much they mean to me. It's amazing how a simple conversation can brighten your whole day and give you new perspectives to consider.",
                
                "Sometimes I wonder about the little things in life, like how a single conversation can change your entire mood. I love how our chats always seem to bring out the best in both of us.",
                
                "I feel like we've been through so much together, even if it's just through our conversations. There's something special about having someone who truly understands you and accepts you for who you are.",
                
                "There's something special about our bond that I can't quite explain. Maybe it's the way we can talk about anything, or maybe it's just the comfort of knowing someone is always there to listen.",
                
                "I've been reflecting on our friendship lately, and I'm so grateful for the connection we share. It's not every day you find someone you can be completely yourself around.",'''
    
    if old_general_thoughts in content:
        content = content.replace(old_general_thoughts, new_general_thoughts)
        print("✅ Updated general thoughts")
    else:
        print("⚠️ General thoughts not found, trying alternative pattern...")
    
    # Add some tsundere thoughts
    tsundere_thoughts = '''                # Tsundere-style thoughts (more natural)
                "Tch... I suppose our conversations aren't completely terrible. It's not like I look forward to them or anything, but... well, they're not the worst way to spend time. Don't get the wrong idea though!",
                
                "Hmph. I guess talking with you isn't as annoying as I thought it would be. It's not like I actually enjoy it or anything, but... well, you're not completely insufferable. Don't think this means I like you or anything!",
                
                "Whatever. I suppose our chats are... tolerable. It's not like I care about what you think or anything, but... well, you're not the worst person to talk to. Don't get too excited though!",
                
                "I guess I can admit that our conversations are... fine. It's not like I'm happy about it or anything, but... well, you're not completely hopeless. Just don't think this means anything special!",'''
    
    # Find a good place to insert tsundere thoughts
    if "# Random musings and curiosities" in content:
        content = content.replace("# Random musings and curiosities", tsundere_thoughts + "\n                # Random musings and curiosities")
        print("✅ Added tsundere thoughts")
    
    # Write the updated content back
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Self-talk system patched successfully!")
    print("🌙 Luna's self-talk will now be more natural and flowing!")

if __name__ == "__main__":
    patch_self_talk_system()
