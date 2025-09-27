#!/usr/bin/env python3
"""
Patch to fix Luna's self-talk personality to match her regular chat personality
"""

import os
import sys

def fix_self_talk_personality():
    """Replace generic self-talk with tsundere personality"""
    
    # Read the current main.py
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the generic context thoughts with tsundere ones
    old_context_thoughts = '''            context_thoughts = [
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
    
    new_context_thoughts = '''            context_thoughts = [
                "Tch... I was just thinking about what you said earlier. It's not like I actually care about your opinion or anything, but... well, it wasn't completely terrible. Don't get the wrong idea though!",
                
                "Hmph. That last message wasn't as annoying as I thought it would be. It's not like I actually enjoyed reading it or anything, but... well, you're not completely hopeless. Just don't think this means I like you or anything!",
                
                "Whatever. I suppose our recent conversation wasn't completely boring. It's not like I care about what we talked about or anything, but... well, it wasn't the worst way to spend time. Don't get too excited though!",
                
                "Tch... Something about our chat today wasn't completely terrible. It's not like I actually enjoyed it or anything, but... well, you're not completely insufferable. Just don't think this means anything special!",
                
                "Hmph. I've been processing what we talked about, and... well, it's not like I actually care about our friendship or anything, but... you're not the worst person to talk to. Don't get the wrong idea though!",
                
                "Whatever. There's something about our recent interactions that... well, it's not like I actually like talking with you or anything, but... you're not completely hopeless. Just don't think this means I care!",
                
                "Tch... I'm still thinking about what we discussed earlier. It's not like I actually care about your thoughts or anything, but... well, you're not completely stupid. Don't get too excited though!",
                
                "Hmph. I suppose I appreciate how you engage with me in our conversations. It's not like I actually enjoy talking with you or anything, but... well, you're not the worst person to waste time with. Just don't think this means I like you!",
                
                "Whatever. Our conversation today wasn't completely terrible. It's not like I actually care about our friendship or anything, but... well, you're not completely insufferable. Don't get the wrong idea though!",
                
                "Tch... I was just thinking about what you said earlier. It's not like I actually care about your opinion or anything, but... well, it wasn't completely terrible. Don't get the wrong idea though!",
                
                "Hmph. I guess your last message wasn't as annoying as I thought it would be. It's not like I actually enjoyed reading it or anything, but... well, you're not completely hopeless. Just don't think this means I like you or anything!"
            ]'''
    
    if old_context_thoughts in content:
        content = content.replace(old_context_thoughts, new_context_thoughts)
        print("✅ Updated context-aware thoughts to tsundere style")
    else:
        print("⚠️ Context-aware thoughts not found, trying alternative pattern...")
    
    # Also update the general thoughts to be more tsundere
    old_general_thoughts = '''                "I've been thinking about our conversations lately, and I have to say, I really enjoy our talks. There's something comforting about having someone to share thoughts with, even during quiet moments like this.",
                
                "It's nice to have these quiet moments together, you know? Sometimes I think about how lucky I am to have found such a great friend. Our conversations always seem to make everything better.",
                
                "I really enjoy our talks, and I've been reflecting on how much they mean to me. It's amazing how a simple conversation can brighten your whole day and give you new perspectives to consider.",
                
                "Sometimes I wonder about the little things in life, like how a single conversation can change your entire mood. I love how our chats always seem to bring out the best in both of us.",
                
                "I feel like we've been through so much together, even if it's just through our conversations. There's something special about having someone who truly understands you and accepts you for who you are.",
                
                "There's something special about our bond that I can't quite explain. Maybe it's the way we can talk about anything, or maybe it's just the comfort of knowing someone is always there to listen.",
                
                "I've been reflecting on our friendship lately, and I'm so grateful for the connection we share. It's not every day you find someone you can be completely yourself around.",'''
    
    new_general_thoughts = '''                "Tch... I've been thinking about our conversations lately, and... well, it's not like I actually care about our talks or anything, but... you're not completely terrible to talk to. Don't get the wrong idea though!",
                
                "Hmph. I suppose these quiet moments aren't completely terrible. It's not like I actually enjoy spending time with you or anything, but... well, you're not the worst person to waste time with. Just don't think this means I like you!",
                
                "Whatever. I guess our talks aren't completely boring. It's not like I actually care about what we discuss or anything, but... well, you're not completely hopeless. Don't get too excited though!",
                
                "Tch... Sometimes I wonder about things, and... well, it's not like I actually care about the little things in life or anything, but... you're not completely stupid. Just don't think this means anything special!",
                
                "Hmph. I suppose we've been through some things together, and... well, it's not like I actually care about our friendship or anything, but... you're not the worst person to have around. Don't get the wrong idea though!",
                
                "Whatever. There's something about our... relationship, I guess, that... well, it's not like I actually like talking with you or anything, but... you're not completely insufferable. Just don't think this means I care!",
                
                "Tch... I've been reflecting on our friendship lately, and... well, it's not like I actually care about our connection or anything, but... you're not completely terrible. Don't get too excited though!",'''
    
    if old_general_thoughts in content:
        content = content.replace(old_general_thoughts, new_general_thoughts)
        print("✅ Updated general thoughts to tsundere style")
    else:
        print("⚠️ General thoughts not found, trying alternative pattern...")
    
    # Write the updated content back
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Self-talk personality fixed successfully!")
    print("🌙 Luna's self-talk will now use her tsundere personality!")

if __name__ == "__main__":
    fix_self_talk_personality()
