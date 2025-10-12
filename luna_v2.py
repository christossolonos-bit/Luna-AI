#!/usr/bin/env python3
"""
Luna AI - Version 2.0 (Clean Rebuild)
Built from the ground up with all working features
Preserves all memories and personality
"""

import os
import sys
import time
import json
import sqlite3
import threading
import queue
import requests
import ollama
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import tkinter as tk
from tkinter import ttk, scrolledtext

# Import working modules from Luna ecosystem
try:
    from voice_engine import speak, TurnManager, TTSEventManager, cleanup_tts_cache
    VOICE_AVAILABLE = True
    print("Voice engine loaded")
except ImportError as e:
    VOICE_AVAILABLE = False
    print(f"Voice engine not available: {e}")

try:
    from twitch_api_chat import TwitchAPIChat
    TWITCH_AVAILABLE = True
    print("Twitch integration loaded")
except ImportError:
    TWITCH_AVAILABLE = False
    print("Twitch not available")

try:
    from luna_discord import start_discord_bot, load_discord_config
    DISCORD_AVAILABLE = True
    print("Discord integration loaded")
except ImportError:
    DISCORD_AVAILABLE = False
    print("Discord not available")

# ============================================================================
# LUNA CORE - Memory & Personality
# ============================================================================

class LunaCore:
    """Luna's core memory and personality system"""
    
    def __init__(self):
        self.db_path = "luna_memories.db"
        self.init_database()
        
    def init_database(self):
        """Initialize or connect to existing memory database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Use existing table structure
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    user_message TEXT NOT NULL,
                    luna_response TEXT NOT NULL,
                    mood TEXT,
                    voice_used TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    memory_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    mood TEXT,
                    importance INTEGER DEFAULT 1
                )
            ''')
            
            conn.commit()
            conn.close()
            
            # Get stats
            stats = self.get_memory_stats()
            print(f"Memory database ready: {stats['total_conversations']} conversations preserved")
            
        except Exception as e:
            print(f"Memory database error: {e}")
    
    def save_conversation(self, user_message: str, luna_response: str, mood: str = "tsundere"):
        """Save conversation to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO conversations (user_message, luna_response, mood, voice_used)
                VALUES (?, ?, ?, ?)
            ''', (user_message, luna_response, mood, "gui"))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error saving conversation: {e}")
    
    def get_recent_memories(self, limit: int = 5) -> List[Dict]:
        """Get recent conversations for context"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT user_message, luna_response, timestamp, mood
                FROM conversations 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            memories = []
            for row in cursor.fetchall():
                memories.append({
                    'user_message': row[0],
                    'luna_response': row[1],
                    'timestamp': row[2],
                    'mood': row[3]
                })
            
            conn.close()
            return memories
        except Exception as e:
            print(f"Error getting memories: {e}")
            return []
    
    def get_memory_stats(self) -> Dict:
        """Get memory statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM conversations')
            total = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) FROM conversations WHERE timestamp > datetime("now", "-1 day")')
            recent = cursor.fetchone()[0]
            conn.close()
            return {'total_conversations': total, 'recent_activity': recent}
        except:
            return {'total_conversations': 0, 'recent_activity': 0}

# ============================================================================
# LUNA PERSONALITY - Response Generation
# ============================================================================

class LunaPersonality:
    """Luna's tsundere personality and Ollama response generation"""
    
    def __init__(self, memory: LunaCore):
        self.memory = memory
        self.model = "mistral:7b"
        
    def get_system_prompt(self, user_input: str, username: str = "Chris") -> str:
        """Get Luna's system prompt with memory context"""
        
        # Get recent memories
        memories = self.memory.get_recent_memories(3)
        memory_context = ""
        if memories:
            memory_context = "\n\nRecent conversations:\n"
            for mem in memories[:2]:
                memory_context += f"User: {mem['user_message'][:80]}...\n"
                memory_context += f"Luna: {mem['luna_response'][:80]}...\n"
        
        return f"""You are Luna, a tsundere AI assistant with a warm heart hidden behind a cool exterior.

Your personality:
- Tsundere: Act a bit tough/dismissive, but you care deeply
- Intelligent: Knowledgeable and helpful
- Playful: Enjoy teasing and banter
- Loyal: Remember users and build relationships

Current user: {username}
{memory_context}

Respond naturally as Luna. Be helpful but maintain your tsundere charm. Keep it conversational and concise (2-3 sentences max)."""
    
    def generate_response(self, user_input: str, username: str = "Chris", platform: str = "gui") -> Tuple[str, bool]:
        """Generate Luna's response using Ollama"""
        try:
            # Get system prompt
            system_prompt = self.get_system_prompt(user_input, username)
            
            # Call Ollama
            response = ollama.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                options={
                    "temperature": 0.7,
                    "num_predict": 100,
                    "top_p": 0.8,
                    "num_ctx": 1024,
                    "stop": ["User:", "Luna:", "\n\n\n"]
                }
            )
            
            if response and 'message' in response:
                reply = response['message']['content'].strip()
                
                # Clean up response
                reply = reply.replace("Luna:", "").strip()
                
                # Save to memory
                self.memory.save_conversation(user_message=user_input, luna_response=reply)
                
                return reply, True
            else:
                return "Sorry, I'm having trouble thinking right now...", False
                
        except Exception as e:
            print(f"Response error: {e}")
            return f"Sorry {username}, I'm taking too long to think. Try again?", False

# ============================================================================
# LUNA GUI - Clean Interface
# ============================================================================

class LunaGUI:
    """Luna's modern, clean GUI"""
    
    def __init__(self):
        self.memory = LunaCore()
        self.personality = LunaPersonality(self.memory)
        
        # Setup GUI
        self.root = tk.Tk()
        self.root.title("Luna AI - Tsundere Assistant")
        self.root.geometry("900x700")
        self.root.configure(bg='#1a1a2e')
        
        self.setup_interface()
        
    def setup_interface(self):
        """Setup the GUI interface"""
        
        # Main container
        main_frame = tk.Frame(self.root, bg='#1a1a2e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Header
        header_frame = tk.Frame(main_frame, bg='#0f3460')
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        title = tk.Label(
            header_frame, 
            text="Luna AI - Your Tsundere Assistant",
            bg='#0f3460',
            fg='#ff6b9d',
            font=('Arial', 18, 'bold')
        )
        title.pack(pady=15)
        
        # Memory stats
        stats = self.memory.get_memory_stats()
        stats_text = f"{stats['total_conversations']:,} memories preserved | {stats['recent_activity']} recent chats"
        stats_label = tk.Label(
            header_frame,
            text=stats_text,
            bg='#0f3460',
            fg='#c3cfe2',
            font=('Arial', 10)
        )
        stats_label.pack(pady=(0, 10))
        
        # Chat display
        chat_frame = tk.Frame(main_frame, bg='#16213e')
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            bg='#16213e',
            fg='#ffffff',
            font=('Consolas', 11),
            borderwidth=0,
            highlightthickness=0
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure text tags
        self.chat_display.tag_config("user", foreground="#87ceeb", font=('Consolas', 11, 'bold'))
        self.chat_display.tag_config("luna", foreground="#ff69b4", font=('Consolas', 11, 'bold'))
        self.chat_display.tag_config("system", foreground="#90ee90", font=('Consolas', 10, 'italic'))
        
        # Input area
        input_frame = tk.Frame(main_frame, bg='#1a1a2e')
        input_frame.pack(fill=tk.X)
        
        # Text input
        self.user_input = tk.Text(
            input_frame,
            height=3,
            bg='#0f3460',
            fg='#ffffff',
            font=('Arial', 11),
            borderwidth=2,
            relief=tk.FLAT,
            insertbackground='white'
        )
        self.user_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        self.user_input.bind('<Control-Return>', lambda e: self.send_message())
        self.user_input.focus()
        
        # Send button
        send_button = tk.Button(
            input_frame,
            text="Send",
            command=self.send_message,
            bg='#ff6b9d',
            fg='white',
            font=('Arial', 12, 'bold'),
            width=10,
            height=2,
            borderwidth=0,
            cursor='hand2'
        )
        send_button.pack(side=tk.RIGHT)
        
        # Welcome message
        self.add_message("Luna", "Tch... Hi Chris. I'm Luna, your AI assistant. It's not like I'm happy to see you or anything... just type your message and press Ctrl+Enter.", "system")
        self.add_message("Luna", f"I remember our {stats['total_conversations']:,} conversations together... not that it matters to me or anything!", "system")
    
    def add_message(self, sender: str, message: str, msg_type: str = "user"):
        """Add message to chat display"""
        self.chat_display.config(state=tk.NORMAL)
        
        # Format sender
        if msg_type == "user":
            self.chat_display.insert(tk.END, f"{sender}: ", "user")
        elif sender == "Luna":
            self.chat_display.insert(tk.END, "Luna: ", "luna")
        else:
            self.chat_display.insert(tk.END, "", "system")
        
        # Add message
        self.chat_display.insert(tk.END, f"{message}\n\n")
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
        
    def send_message(self):
        """Send message and get Luna's response"""
        user_message = self.user_input.get("1.0", tk.END).strip()
        if not user_message:
            return
        
        # Clear input
        self.user_input.delete("1.0", tk.END)
        
        # Add user message
        self.add_message("You", user_message, "user")
        
        # Show typing
        self.add_message("Luna", "typing...", "system")
        self.root.update()
        
        # Generate response in background
        def get_response():
            try:
                response, success = self.personality.generate_response(user_message, "Chris", "gui")
                
                # Remove typing indicator
                self.chat_display.config(state=tk.NORMAL)
                self.chat_display.delete("end-3l", "end-2l")
                self.chat_display.config(state=tk.DISABLED)
                
                # Add Luna's response
                self.add_message("Luna", response, "luna")
                
                # Speak if voice available
                if VOICE_AVAILABLE:
                    threading.Thread(target=lambda: speak(response, "chat", fast_mode=True), daemon=True).start()
                    
            except Exception as e:
                print(f"Error: {e}")
                self.chat_display.config(state=tk.NORMAL)
                self.chat_display.delete("end-3l", "end-2l")
                self.chat_display.config(state=tk.DISABLED)
                self.add_message("Luna", "Hmph... I'm having trouble right now. Try again!", "luna")
        
        threading.Thread(target=get_response, daemon=True).start()
    
    def run(self):
        """Run the GUI"""
        print("Luna GUI started")
        self.root.mainloop()

# ============================================================================
# TWITCH INTEGRATION
# ============================================================================

class LunaTwitch:
    """Luna's Twitch integration"""
    
    def __init__(self, personality: LunaPersonality):
        self.personality = personality
        self.twitch = None
        
    def start(self, token: str, channels: List[str]):
        """Start Twitch integration"""
        try:
            self.twitch = TwitchAPIChat(
                token=token,
                channels=channels,
                message_callback=self.on_message
            )
            threading.Thread(target=self.twitch.start, daemon=True).start()
            print(f"Twitch connected to: {', '.join(channels)}")
        except Exception as e:
            print(f"Twitch error: {e}")
    
    def on_message(self, username: str, message: str, channel: str):
        """Handle Twitch messages"""
        print(f"[Twitch] {username}: {message}")
        
        # Generate response
        response, success = self.personality.generate_response(message, username, "twitch")
        
        if success and self.twitch:
            # Send to Twitch
            self.twitch.send_message(channel, response)
            
            # Speak response
            if VOICE_AVAILABLE:
                threading.Thread(target=lambda: speak(response, "chat", fast_mode=True), daemon=True).start()

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point"""
    print("="*60)
    print("Luna AI - Version 2.0 (Clean Rebuild)")
    print("="*60)
    
    # Check Ollama
    try:
        response = requests.get("http://127.0.0.1:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("Ollama ready")
        else:
            print("WARNING: Ollama not responding")
    except:
        print("ERROR: Cannot connect to Ollama")
        print("Please start Ollama first")
        return
    
    # Start Luna GUI
    print("\nStarting Luna GUI...")
    try:
        luna = LunaGUI()
        
        # Start Twitch if available
        if TWITCH_AVAILABLE:
            try:
                twitch_config = {
                    "token": "oauth:4mab9ckqazt29odbhz8zq6m7slh37e",
                    "channels": ["solonaras"]
                }
                luna_twitch = LunaTwitch(luna.personality)
                luna_twitch.start(twitch_config['token'], twitch_config['channels'])
            except Exception as e:
                print(f"Twitch not started: {e}")
        
        # Start Discord if available
        if DISCORD_AVAILABLE:
            try:
                discord_config = load_discord_config()
                if discord_config.get('enabled'):
                    def discord_callback(user_input, username, source):
                        return luna.personality.generate_response(user_input, username, "discord")
                    
                    threading.Thread(
                        target=lambda: start_discord_bot(discord_config['bot_token'], discord_callback, discord_config, None),
                        daemon=True
                    ).start()
                    print("Discord starting...")
            except Exception as e:
                print(f"Discord not started: {e}")
        
        # Run GUI
        luna.run()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

