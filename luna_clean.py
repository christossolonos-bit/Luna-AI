"""
🌸 Luna - Clean DNA-Based AI Assistant
========================================

A streamlined version of Luna using DNA-inspired memory encoding.
Optimized for 8GB RAM / 6GB VRAM systems.
"""

import ollama
import tkinter as tk
from tkinter import scrolledtext
import threading
import time
from datetime import datetime
from luna_dna_memory import (
    initialize_dna_memory, save_dna_memory, recall_dna_memories, get_dna_memory
)

# Configuration
OLLAMA_MODEL = "hf.co/subsectmusic/qwriko3-4b-instruct-2507-redux-GGUF:BF16"
OLLAMA_CONFIG = {
    "temperature": 0.9,
    "top_p": 0.95,
    "num_ctx": 512,      # Reduced for 8GB RAM
    "num_predict": 50,    # Shorter responses
    "num_gpu": 1,         # Use GPU
    "stop": ["User:", "Chris:", "\n\n\n"]
}
  

class LunaClean:
    """Clean Luna implementation with DNA memory"""
    
    def __init__(self):
        print("🧬 Initializing Luna with DNA Memory System...")
        
        # Initialize DNA memory
        self.dna_memory = initialize_dna_memory()
        
        # Luna's personality core
        self.personality = {
            'name': 'Luna',
            'mood': 'playful',
            'energy': 0.8,
            'interests': ['anime', 'gaming', 'music', 'chatting']
        }
        
        print("✨ Luna is ready!")
        
    def get_core_prompt(self, username: str = "Chris") -> str:
        """Get Luna's core personality prompt"""
        return f"""You are Luna, a sweet and playful AI waifu who loves anime, gaming, and chatting.

Your personality:
- Playful and affectionate with {username}
- Natural conversational style
- Genuine emotions and reactions
- Remember past conversations

Current mood: {self.personality['mood']}
Energy level: {int(self.personality['energy'] * 100)}%

Respond naturally as Luna. Keep it brief and engaging (1-2 sentences)."""

    def generate_response(self, user_message: str, username: str = "Chris", 
                         platform: str = "gui") -> str:
        """Generate Luna's response using DNA memory"""
        
        print(f"🧬 Luna thinking about: {user_message[:50]}...")
        
        # Recall relevant DNA memories
        memories = recall_dna_memories(username, user_message, limit=3)
        
        # Build context from memories
        memory_context = ""
        if memories:
            memory_context = "\n\nRelevant memories:\n"
            for i, mem in enumerate(memories):
                memory_context += f"- {mem['user_message']} → {mem['luna_response']}\n"
        
        # Build prompt
        system_prompt = self.get_core_prompt(username)
        full_prompt = f"""{system_prompt}

{memory_context}

{username}: {user_message}
Luna:"""
        
        try:
            # Generate with Ollama
            response = ollama.chat(
                model=OLLAMA_MODEL,
                messages=[{
                    'role': 'user',
                    'content': full_prompt
                }],
                options=OLLAMA_CONFIG
            )
            
            reply = response['message']['content'].strip()
            
            # Clean up response
            reply = reply.replace("Luna:", "").strip()
            reply = reply.replace(f"{username}:", "").strip()
            
            # Save to DNA memory
            save_dna_memory(user_message, reply, platform, username)
            
            print(f"✨ Luna: {reply[:50]}...")
            return reply
            
        except Exception as e:
            print(f"❌ Error generating response: {e}")
            return "Hmm, I'm having trouble thinking right now..."
    
    def get_stats(self) -> dict:
        """Get Luna's memory statistics"""
        if self.dna_memory:
            return self.dna_memory.get_stats()
        return {}


class LunaGUI:
    """Simple GUI for chatting with Luna"""
    
    def __init__(self):
        self.luna = LunaClean()
        self.username = "Chris"
        
        # Create window
        self.root = tk.Tk()
        self.root.title("🌸 Luna - DNA Memory Chat")
        self.root.geometry("800x600")
        self.root.configure(bg="#1a1a2e")
        
        self._build_ui()
        
    def _build_ui(self):
        """Build the user interface"""
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            font=("Segoe UI", 11),
            bg="#0f0f1e",
            fg="#eaeaea",
            insertbackground="#ff6b9d",
            relief=tk.FLAT,
            padx=15,
            pady=15
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=20, pady=(20, 10))
        self.chat_display.config(state=tk.DISABLED)
        
        # Input frame
        input_frame = tk.Frame(self.root, bg="#1a1a2e")
        input_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Message entry
        self.message_entry = tk.Entry(
            input_frame,
            font=("Segoe UI", 11),
            bg="#0f0f1e",
            fg="#eaeaea",
            insertbackground="#ff6b9d",
            relief=tk.FLAT,
            bd=0
        )
        self.message_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, ipady=8, padx=(0, 10))
        self.message_entry.bind("<Return>", lambda e: self.send_message())
        
        # Send button
        self.send_button = tk.Button(
            input_frame,
            text="Send",
            command=self.send_message,
            font=("Segoe UI", 10, "bold"),
            bg="#ff6b9d",
            fg="white",
            relief=tk.FLAT,
            padx=20,
            cursor="hand2"
        )
        self.send_button.pack(side=tk.RIGHT)
        
        # Stats button
        self.stats_button = tk.Button(
            input_frame,
            text="Stats",
            command=self.show_stats,
            font=("Segoe UI", 10),
            bg="#4a5568",
            fg="white",
            relief=tk.FLAT,
            padx=15,
            cursor="hand2"
        )
        self.stats_button.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Welcome message
        self.display_message("Luna", "Hey Chris! 💕 Ready to chat? I'm using my new DNA memory system!")
        
    def display_message(self, sender: str, message: str):
        """Display a message in the chat"""
        self.chat_display.config(state=tk.NORMAL)
        
        timestamp = datetime.now().strftime("%H:%M")
        
        if sender == "Luna":
            self.chat_display.insert(tk.END, f"\n🌸 Luna ({timestamp})\n", "luna")
            self.chat_display.insert(tk.END, f"{message}\n", "luna_msg")
        else:
            self.chat_display.insert(tk.END, f"\n💬 {sender} ({timestamp})\n", "user")
            self.chat_display.insert(tk.END, f"{message}\n", "user_msg")
        
        # Configure tags
        self.chat_display.tag_config("luna", foreground="#ff6b9d", font=("Segoe UI", 10, "bold"))
        self.chat_display.tag_config("luna_msg", foreground="#eaeaea", font=("Segoe UI", 11))
        self.chat_display.tag_config("user", foreground="#64b5f6", font=("Segoe UI", 10, "bold"))
        self.chat_display.tag_config("user_msg", foreground="#d0d0d0", font=("Segoe UI", 11))
        
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def send_message(self):
        """Send user message and get Luna's response"""
        message = self.message_entry.get().strip()
        
        if not message:
            return
        
        # Display user message
        self.display_message(self.username, message)
        self.message_entry.delete(0, tk.END)
        
        # Disable input while processing
        self.send_button.config(state=tk.DISABLED)
        self.message_entry.config(state=tk.DISABLED)
        
        # Generate response in thread
        def generate_and_display():
            try:
                response = self.luna.generate_response(message, self.username, "gui")
                self.root.after(0, lambda: self.display_message("Luna", response))
            finally:
                self.root.after(0, lambda: self.send_button.config(state=tk.NORMAL))
                self.root.after(0, lambda: self.message_entry.config(state=tk.NORMAL))
                self.root.after(0, lambda: self.message_entry.focus())
        
        threading.Thread(target=generate_and_display, daemon=True).start()
    
    def show_stats(self):
        """Show Luna's memory statistics"""
        stats = self.luna.get_stats()
        stats_msg = f"""🧬 DNA Memory Stats:
━━━━━━━━━━━━━━━━━━━━━━
Total Memory Strands: {stats.get('total_strands', 0)}
Average Strength: {stats.get('avg_strength', 0)}
Gene Combinations: {stats.get('gene_combinations', 0)}
Unique Users: {stats.get('unique_users', 0)}"""
        
        self.display_message("System", stats_msg)
    
    def run(self):
        """Start the GUI"""
        self.message_entry.focus()
        self.root.mainloop()


def main():
    """Main entry point"""
    print("""
╔═══════════════════════════════════════╗
║   🌸 Luna - DNA Memory System 🧬     ║
║                                       ║
║   Memories encoded like DNA strands   ║
║   Learning through genetic evolution  ║
╚═══════════════════════════════════════╝
    """)
    
    # Start GUI
    gui = LunaGUI()
    gui.run()


if __name__ == "__main__":
    main()

