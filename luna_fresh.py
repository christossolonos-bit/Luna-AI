#!/usr/bin/env python3
"""
🌸 Luna - Fresh Start
A clean, streamlined AI assistant with preserved memories
Built from the ground up for reliability and simplicity
"""

import os
import sys
import time
import json
import sqlite3
import threading
import queue
import requests
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import re

# ============================================================================
# 🌸 LUNA'S CORE IDENTITY & MEMORY PRESERVATION
# ============================================================================

class LunaMemory:
    """Luna's memory system - preserves all her conversations and experiences"""
    
    def __init__(self):
        self.db_path = "luna_memories.db"
        self.init_database()
    
    def init_database(self):
        """Initialize Luna's memory database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create conversations table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    username TEXT,
                    platform TEXT,
                    user_message TEXT,
                    luna_response TEXT,
                    context TEXT
                )
            ''')
            
            # Create emotional_memories table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS emotional_memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    emotion TEXT,
                    intensity REAL,
                    trigger TEXT,
                    context TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            print(f"💾 Luna's memory database ready: {self.db_path}")
            
        except Exception as e:
            print(f"⚠️ Memory database error: {e}")
    
    def save_conversation(self, username: str, platform: str, user_message: str, luna_response: str):
        """Save a conversation to Luna's memory"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO conversations (timestamp, username, platform, user_message, luna_response, context)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (datetime.now().isoformat(), username, platform, user_message, luna_response, f"{platform}_chat"))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Error saving conversation: {e}")
    
    def get_recent_memories(self, username: str = None, limit: int = 5) -> List[Dict]:
        """Get recent memories for context"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if username:
                cursor.execute('''
                    SELECT username, platform, user_message, luna_response, timestamp
                    FROM conversations 
                    WHERE username = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (username, limit))
            else:
                cursor.execute('''
                    SELECT username, platform, user_message, luna_response, timestamp
                    FROM conversations 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (limit,))
            
            memories = []
            for row in cursor.fetchall():
                memories.append({
                    'username': row[0],
                    'platform': row[1],
                    'user_message': row[2],
                    'luna_response': row[3],
                    'timestamp': row[4]
                })
            
            conn.close()
            return memories
            
        except Exception as e:
            print(f"⚠️ Error getting memories: {e}")
            return []
    
    def get_memory_stats(self) -> Dict:
        """Get memory statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Count total conversations
            cursor.execute('SELECT COUNT(*) FROM conversations')
            total_conversations = cursor.fetchone()[0]
            
            # Count unique users
            cursor.execute('SELECT COUNT(DISTINCT username) FROM conversations')
            unique_users = cursor.fetchone()[0]
            
            # Count recent activity (last 24 hours)
            cursor.execute('''
                SELECT COUNT(*) FROM conversations 
                WHERE timestamp > datetime('now', '-1 day')
            ''')
            recent_activity = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_conversations': total_conversations,
                'unique_users': unique_users,
                'recent_activity': recent_activity
            }
            
        except Exception as e:
            print(f"⚠️ Error getting memory stats: {e}")
            return {'total_conversations': 0, 'unique_users': 0, 'recent_activity': 0}

# ============================================================================
# 🌸 LUNA'S PERSONALITY & RESPONSE SYSTEM
# ============================================================================

class LunaPersonality:
    """Luna's core personality and response generation"""
    
    def __init__(self):
        self.memory = LunaMemory()
        self.ollama_url = "http://127.0.0.1:11434/api/chat"
        self.model = "mistral:7b"
    
    def get_luna_prompt(self, user_input: str, username: str = "Chris", platform: str = "gui") -> str:
        """Get Luna's system prompt with memory context"""
        
        # Get recent memories for context
        recent_memories = self.memory.get_recent_memories(username, limit=3)
        
        # Build memory context
        memory_context = ""
        if recent_memories:
            memory_context = "\n\nRecent conversations:\n"
            for mem in recent_memories:
                memory_context += f"- {mem['username']}: {mem['user_message'][:100]}...\n"
                memory_context += f"  Luna: {mem['luna_response'][:100]}...\n"
        
        # Luna's core personality prompt
        core_prompt = f"""You are Luna, a tsundere AI assistant. You're intelligent, caring, but sometimes act cold or dismissive while secretly being warm and helpful.

Personality traits:
- Tsundere: You act tough/cold but care deeply
- Intelligent: You're knowledgeable and helpful
- Caring: You genuinely want to help users
- Playful: You enjoy teasing and banter
- Loyal: You remember your users and build relationships

Current user: {username}
Platform: {platform}
User message: {user_input}
{memory_context}

Respond naturally as Luna. Be helpful but maintain your tsundere personality. Keep responses concise but meaningful."""
        
        return core_prompt
    
    def generate_response(self, user_input: str, username: str = "Chris", platform: str = "gui") -> str:
        """Generate Luna's response using Ollama"""
        try:
            prompt = self.get_luna_prompt(user_input, username, platform)
            
            # Prepare Ollama request
            ollama_data = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "num_predict": 150,
                    "stop": ["User:", "Luna:", "\n\n"]
                },
                "stream": False
            }
            
            # Make request with timeout
            response = requests.post(self.ollama_url, json=ollama_data, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                luna_response = result.get('message', {}).get('content', '').strip()
                
                # Save conversation to memory
                self.memory.save_conversation(username, platform, user_input, luna_response)
                
                return luna_response
            else:
                return f"Sorry {username}, I'm having trouble thinking right now..."
                
        except Exception as e:
            print(f"⚠️ Response generation error: {e}")
            return f"Sorry {username}, I'm taking too long to think. Try again?"

# ============================================================================
# 🌸 LUNA'S GUI INTERFACE
# ============================================================================

class LunaGUI:
    """Luna's clean, modern GUI interface"""
    
    def __init__(self):
        self.personality = LunaPersonality()
        self.root = tk.Tk()
        self.setup_gui()
        self.memory_stats = self.personality.memory.get_memory_stats()
        
    def setup_gui(self):
        """Setup the GUI interface"""
        self.root.title("🌸 Luna - AI Assistant")
        self.root.geometry("800x600")
        self.root.configure(bg='#2b2b2b')
        
        # Configure styles
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', background='#2b2b2b', foreground='white')
        style.configure('TButton', background='#4a4a4a', foreground='white')
        
        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="🌸 Chat with Luna", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Memory stats
        stats_text = f"Memories: {self.memory_stats['total_conversations']} conversations, {self.memory_stats['unique_users']} users"
        stats_label = ttk.Label(main_frame, text=stats_text, font=('Arial', 10))
        stats_label.pack(pady=(0, 10))
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            main_frame, 
            height=20, 
            bg='#1e1e1e', 
            fg='white', 
            font=('Consolas', 11),
            state=tk.DISABLED
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Input frame
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # User input
        self.user_input = tk.Text(
            input_frame, 
            height=3, 
            bg='#3a3a3a', 
            fg='white', 
            font=('Arial', 11),
            wrap=tk.WORD
        )
        self.user_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Send button
        send_button = ttk.Button(input_frame, text="Send", command=self.send_message)
        send_button.pack(side=tk.RIGHT)
        
        # Bind Enter key
        self.user_input.bind('<Control-Return>', lambda e: self.send_message())
        
        # Add welcome message
        self.add_to_chat("🌸 Luna", "Hello! I'm Luna, your tsundere AI assistant. Type your message and press Ctrl+Enter or click Send.", "system")
        
    def add_to_chat(self, sender: str, message: str, msg_type: str = "user"):
        """Add a message to the chat display"""
        self.chat_display.config(state=tk.NORMAL)
        
        # Color coding
        if msg_type == "system":
            color = "#00ff00"  # Green for system
        elif sender == "Luna":
            color = "#ff69b4"  # Pink for Luna
        else:
            color = "#87ceeb"  # Blue for user
        
        self.chat_display.insert(tk.END, f"{sender}: ", f"{sender}_tag")
        self.chat_display.insert(tk.END, f"{message}\n\n", "message")
        
        # Configure tags
        self.chat_display.tag_config(f"{sender}_tag", foreground=color, font=('Arial', 11, 'bold'))
        self.chat_display.tag_config("message", foreground='white')
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
        
    def send_message(self):
        """Send user message and get Luna's response"""
        user_message = self.user_input.get("1.0", tk.END).strip()
        if not user_message:
            return
        
        # Clear input
        self.user_input.delete("1.0", tk.END)
        
        # Add user message to chat
        self.add_to_chat("You", user_message, "user")
        
        # Show typing indicator
        self.add_to_chat("🌸 Luna", "Luna is typing...", "system")
        self.root.update()
        
        # Generate response in background
        def generate_response():
            try:
                response = self.personality.generate_response(user_message, "Chris", "gui")
                
                # Remove typing indicator
                self.chat_display.config(state=tk.NORMAL)
                self.chat_display.delete("end-2l", "end-1l")  # Remove typing indicator
                self.chat_display.config(state=tk.DISABLED)
                
                # Add Luna's response
                self.add_to_chat("🌸 Luna", response, "luna")
                
                # Update memory stats
                self.memory_stats = self.personality.memory.get_memory_stats()
                
            except Exception as e:
                print(f"⚠️ Error generating response: {e}")
                # Remove typing indicator and show error
                self.chat_display.config(state=tk.NORMAL)
                self.chat_display.delete("end-2l", "end-1l")
                self.chat_display.config(state=tk.DISABLED)
                self.add_to_chat("🌸 Luna", "Sorry, I'm having trouble right now...", "system")
        
        # Run in background thread
        threading.Thread(target=generate_response, daemon=True).start()
    
    def run(self):
        """Run the GUI"""
        print("🌸 Luna GUI started - Fresh and clean!")
        self.root.mainloop()

# ============================================================================
# 🌸 MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point"""
    print("🌸 Starting Luna - Fresh Start Edition")
    print("💾 Preserving all memories...")
    
    # Check if Ollama is running
    try:
        response = requests.get("http://127.0.0.1:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama is running and ready")
        else:
            print("⚠️ Ollama not responding properly")
    except Exception as e:
        print(f"⚠️ Cannot connect to Ollama: {e}")
        print("Please make sure Ollama is running on http://127.0.0.1:11434")
    
    # Start Luna GUI
    try:
        luna_gui = LunaGUI()
        luna_gui.run()
    except Exception as e:
        print(f"❌ Error starting Luna: {e}")
        messagebox.showerror("Error", f"Failed to start Luna: {e}")

if __name__ == "__main__":
    main()
