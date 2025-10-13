"""
🌸 Luna - Clean DNA-Based AI Assistant
========================================

A streamlined version of Luna using DNA-inspired memory encoding.
Optimized for 8GB RAM / 6GB VRAM systems.
"""

import ollama
import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import time
from datetime import datetime
import speech_recognition as sr
import pyaudio
import wave
import os
import requests
import json
import threading
import pygame
import edge_tts
import asyncio
import tempfile
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

# TTS Configuration - Edge TTS (Free!)
TTS_CONFIG = {
    "voice": "en-US-AvaMultilingualNeural",  # Edge TTS Ava multilingual voice
    "rate": "+0%",      # Speech rate
    "pitch": "+0Hz",    # Voice pitch
    "volume": "+0%"     # Voice volume
}
  

class LunaClean:
    """Clean Luna implementation with DNA memory and TTS"""
    
    def __init__(self):
        print("🧬 Initializing Luna with DNA Memory System...")
        
        # Initialize DNA memory
        self.dna_memory = initialize_dna_memory()
        
        # Initialize TTS
        self.tts_enabled = False
        self._setup_tts()
        
        # Initialize pygame for audio playback
        try:
            pygame.mixer.init()
            self.audio_available = True
        except:
            self.audio_available = False
            print("⚠️ Audio playback not available")
        
        # Luna's personality core
        self.personality = {
            'name': 'Luna',
            'mood': 'playful',
            'energy': 0.8,
            'interests': ['anime', 'gaming', 'music', 'chatting']
        }
        
        print("✨ Luna is ready!")
    
    def _setup_tts(self):
        """Setup text-to-speech with Edge TTS Ava multilingual voice"""
        try:
            # Edge TTS is free and doesn't need API key
            self.tts_enabled = True
            print("🎤 TTS enabled with Edge TTS Ava multilingual voice (Free!)")
        except Exception as e:
            print(f"⚠️ TTS setup error: {e}")
            self.tts_enabled = False
    
    def speak(self, text: str):
        """Convert text to speech using Edge TTS Ava multilingual voice"""
        if not self.tts_enabled or not self.audio_available:
            return
        
        def _speak_thread():
            try:
                # Clean text for TTS
                clean_text = text.replace("💕", "").replace("🌸", "").replace("🎤", "").strip()
                if not clean_text:
                    return
                
                # Generate speech using Edge TTS
                asyncio.run(self._generate_speech_async(clean_text))
                        
            except Exception as e:
                print(f"TTS error: {e}")
        
        # Run TTS in separate thread
        threading.Thread(target=_speak_thread, daemon=True).start()
    
    async def _generate_speech_async(self, text: str):
        """Generate speech using Edge TTS"""
        try:
            # Create temporary file for audio
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Generate speech with Edge TTS
            communicate = edge_tts.Communicate(
                text=text,
                voice=TTS_CONFIG["voice"],
                rate=TTS_CONFIG["rate"],
                pitch=TTS_CONFIG["pitch"],
                volume=TTS_CONFIG["volume"]
            )
            
            await communicate.save(temp_path)
            
            # Play the audio file
            pygame.mixer.music.load(temp_path)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
            
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
        except Exception as e:
            print(f"Edge TTS error: {e}")
        
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
    """Voice-enabled GUI for chatting with Luna"""
    
    def __init__(self):
        self.luna = LunaClean()
        self.username = "Chris"
        
        # Voice recognition setup
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_recording = False
        self.recording_thread = None
        
        # Create window
        self.root = tk.Tk()
        self.root.title("🌸 Luna - Voice Chat with DNA Memory")
        self.root.geometry("900x700")
        self.root.configure(bg="#1a1a2e")
        
        # Bind keys for push-to-talk
        self.root.bind('<KeyPress-space>', self.start_recording)
        self.root.bind('<KeyRelease-space>', self.stop_recording)
        self.root.focus_set()  # Enable key bindings
        
        self._build_ui()
        self._setup_voice()
        
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
        
        # Voice control frame
        voice_frame = tk.Frame(self.root, bg="#1a1a2e")
        voice_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        # Voice status label
        self.voice_status = tk.Label(
            voice_frame,
            text="🎤 Hold SPACEBAR to talk to Luna",
            font=("Segoe UI", 10),
            bg="#1a1a2e",
            fg="#ff6b9d"
        )
        self.voice_status.pack(side=tk.LEFT)
        
        # Voice test button
        self.voice_test_button = tk.Button(
            voice_frame,
            text="Test Mic",
            command=self.test_microphone,
            font=("Segoe UI", 9),
            bg="#2d3748",
            fg="white",
            relief=tk.FLAT,
            padx=10,
            cursor="hand2"
        )
        self.voice_test_button.pack(side=tk.RIGHT, padx=(0, 10))
        
        # TTS toggle button
        self.tts_button = tk.Button(
            voice_frame,
            text="🔇 TTS OFF",
            command=self.toggle_tts,
            font=("Segoe UI", 9),
            bg="#4a5568",
            fg="white",
            relief=tk.FLAT,
            padx=10,
            cursor="hand2"
        )
        self.tts_button.pack(side=tk.RIGHT)
        
        # TTS status
        self.tts_enabled = False
        
        # Welcome message
        self.display_message("Luna", "Hey Chris! 💕 Ready to chat? Hold SPACEBAR to talk to me!")
        self.display_message("System", "Voice recognition enabled - Hold SPACEBAR to speak")
        
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
                
                # Speak response if TTS is enabled
                if self.tts_enabled and self.luna.tts_enabled:
                    self.root.after(0, lambda: self.luna.speak(response))
                    
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
    
    def _setup_voice(self):
        """Setup voice recognition"""
        try:
            # Adjust for ambient noise
            with self.microphone as source:
                print("Calibrating microphone...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Microphone calibrated!")
        except Exception as e:
            print(f"Microphone setup error: {e}")
            self.display_message("System", f"Voice setup error: {e}")
    
    def start_recording(self, event):
        """Start recording when spacebar is pressed"""
        if not self.is_recording:
            self.is_recording = True
            self.voice_status.config(text="🔴 Recording... Release SPACEBAR when done", fg="#ff4444")
            
            # Start recording in a separate thread
            self.recording_thread = threading.Thread(target=self._record_audio, daemon=True)
            self.recording_thread.start()
    
    def stop_recording(self, event):
        """Stop recording when spacebar is released"""
        if self.is_recording:
            self.is_recording = False
            self.voice_status.config(text="🎤 Hold SPACEBAR to talk to Luna", fg="#ff6b9d")
    
    def _record_audio(self):
        """Record audio in a separate thread"""
        try:
            with self.microphone as source:
                # Record until spacebar is released
                audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=10)
            
            if not self.is_recording:
                return  # Recording was cancelled
            
            # Transcribe audio
            self.root.after(0, lambda: self.voice_status.config(text="🧠 Processing...", fg="#ffaa44"))
            
            text = self.recognizer.recognize_google(audio)
            
            if text.strip():
                # Display transcribed text and send to Luna
                self.root.after(0, lambda: self.display_message("Voice", f"🎤 {text}"))
                self.root.after(0, lambda: self._process_voice_input(text))
            else:
                self.root.after(0, lambda: self.display_message("System", "No speech detected"))
                
        except sr.WaitTimeoutError:
            if self.is_recording:
                self.root.after(0, lambda: self.display_message("System", "Recording timeout"))
        except sr.UnknownValueError:
            if self.is_recording:
                self.root.after(0, lambda: self.display_message("System", "Could not understand speech"))
        except sr.RequestError as e:
            if self.is_recording:
                error_msg = f"Speech recognition error: {e}"
                self.root.after(0, lambda msg=error_msg: self.display_message("System", msg))
        except Exception as e:
            if self.is_recording:
                error_msg = f"Recording error: {e}"
                self.root.after(0, lambda msg=error_msg: self.display_message("System", msg))
        finally:
            self.root.after(0, lambda: self.voice_status.config(text="🎤 Hold SPACEBAR to talk to Luna", fg="#ff6b9d"))
    
    def _process_voice_input(self, text: str):
        """Process voice input and generate Luna's response"""
        # Update the text entry with voice input
        self.message_entry.delete(0, tk.END)
        self.message_entry.insert(0, text)
        
        # Generate and display response in thread
        def generate_and_display():
            try:
                response = self.luna.generate_response(text, self.username, "voice_gui")
                self.root.after(0, lambda: self.display_message("Luna", response))
                
                # Speak response if TTS is enabled
                if self.tts_enabled and self.luna.tts_enabled:
                    self.root.after(0, lambda: self.luna.speak(response))
                    
            except Exception as e:
                error_msg = f"Error generating response: {e}"
                self.root.after(0, lambda msg=error_msg: self.display_message("System", msg))
        
        threading.Thread(target=generate_and_display, daemon=True).start()
    
    def test_microphone(self):
        """Test microphone functionality"""
        def test_mic():
            try:
                self.voice_status.config(text="🎤 Testing microphone...", fg="#ffaa44")
                
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                self.root.after(0, lambda: self.voice_status.config(text="🎤 Say something...", fg="#44ff44"))
                
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                
                text = self.recognizer.recognize_google(audio)
                self.root.after(0, lambda: self.display_message("Mic Test", f"🎤 Heard: {text}"))
                self.root.after(0, lambda: self.voice_status.config(text="🎤 Hold SPACEBAR to talk to Luna", fg="#ff6b9d"))
                
            except Exception as e:
                error_msg = f"❌ Error: {e}"
                self.root.after(0, lambda msg=error_msg: self.display_message("Mic Test", msg))
                self.root.after(0, lambda: self.voice_status.config(text="🎤 Hold SPACEBAR to talk to Luna", fg="#ff6b9d"))
        
        threading.Thread(target=test_mic, daemon=True).start()
    
    def toggle_tts(self):
        """Toggle text-to-speech on/off"""
        self.tts_enabled = not self.tts_enabled
        
        if self.tts_enabled:
            if self.luna.tts_enabled:
                self.tts_button.config(text="🔊 TTS ON", bg="#22c55e")
                self.display_message("System", "TTS enabled - Luna will speak her responses with Ava voice")
            else:
                self.tts_enabled = False  # Revert if Luna's TTS is not available
                self.tts_button.config(text="🔇 TTS OFF", bg="#4a5568")
                self.display_message("System", "TTS not available - Edge TTS setup error")
        else:
            self.tts_button.config(text="🔇 TTS OFF", bg="#4a5568")
            self.display_message("System", "TTS disabled - Luna will only text")


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

