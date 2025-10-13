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
import json
import discord
import websocket
import threading
import time
from dotenv import load_dotenv
from luna_dna_memory import (
    initialize_dna_memory, save_dna_memory, recall_dna_memories, get_dna_memory
)

# Load environment variables
load_dotenv()

# Configuration
OLLAMA_MODEL = "hf.co/subsectmusic/qwriko3-4b-instruct-2507-redux-GGUF:BF16"
OLLAMA_CONFIG = {
    "temperature": 0.9,
    "top_p": 0.95,
    "num_ctx": 512,      # Reduced for 8GB RAM
    "num_predict": 150,   # Longer responses for complete thoughts
    "num_gpu": 1,         # Use GPU
    "stop": ["User:", "Chris:", "\n\n\n", "{your name}"]
}

# TTS Configuration - Edge TTS (Free!)
TTS_CONFIG = {
    "voice": "en-US-AvaMultilingualNeural",  # Edge TTS Ava multilingual voice
    "rate": "+0%",      # Speech rate
    "pitch": "+0Hz",    # Voice pitch
    "volume": "+0%"     # Voice volume
}

# Platform Configuration
PLATFORM_CONFIG = {
    "discord": {
        "enabled": True,
        "token_file": ".env"
    },
    "twitch": {
        "enabled": True,
        "token_file": "twitch_config.json",
        "channel": "solonaras"
    }
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
        
        # Initialize platforms
        self.discord_client = None
        self.twitch_ws = None
        self.platform_status = {"discord": False, "twitch": False}
        
        # Twitch ping/pong system
        self.twitch_ping_timer = None
        self.twitch_last_pong = None
        
        # Load platform tokens
        self._load_platform_tokens()
        
        # Auto-connect to platforms
        self._auto_connect_platforms()
        
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
        temp_path = None
        try:
            # Create temporary file for audio with unique name
            import uuid
            temp_filename = f"luna_tts_{uuid.uuid4().hex[:8]}.mp3"
            temp_path = os.path.join(tempfile.gettempdir(), temp_filename)
            
            # Generate speech with Edge TTS
            communicate = edge_tts.Communicate(
                text=text,
                voice=TTS_CONFIG["voice"],
                rate=TTS_CONFIG["rate"],
                pitch=TTS_CONFIG["pitch"],
                volume=TTS_CONFIG["volume"]
            )
            
            await communicate.save(temp_path)
            
            # Ensure file is completely written before trying to load
            await asyncio.sleep(0.1)
            
            # Play the audio file
            pygame.mixer.music.load(temp_path)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
            
        except Exception as e:
            print(f"Edge TTS error: {e}")
        finally:
            # Clean up temporary file with retry mechanism
            if temp_path and os.path.exists(temp_path):
                try:
                    # Wait a bit more to ensure file is released
                    await asyncio.sleep(0.2)
                    os.remove(temp_path)
                except PermissionError:
                    # File still in use, try again later
                    print(f"Could not delete temp file {temp_path}, will be cleaned up later")
                except Exception as cleanup_error:
                    print(f"Cleanup error: {cleanup_error}")
    
    def _load_platform_tokens(self):
        """Load platform tokens from text files or environment variables"""
        try:
            # Load Discord token from text file first, then environment, then config file
            self.discord_token = None
            
            # Try text file first
            if os.path.exists("discord_token.txt"):
                with open("discord_token.txt", "r") as f:
                    self.discord_token = f.read().strip()
                    print("✅ Discord token loaded from discord_token.txt")
            
            # Fallback to environment variable
            if not self.discord_token:
                load_dotenv(override=True)
                self.discord_token = os.getenv("DISCORD_TOKEN")
                if self.discord_token:
                    print("✅ Discord token loaded from environment variable")
            
            # Final fallback to config file
            if not self.discord_token and os.path.exists("discord_config.json"):
                with open("discord_config.json", "r") as f:
                    discord_config = json.load(f)
                    self.discord_token = discord_config.get("token")
                    if self.discord_token:
                        print("✅ Discord token loaded from discord_config.json")
            
            if self.discord_token:
                # Validate Discord token before marking as loaded
                if len(self.discord_token) > 50 and "." in self.discord_token:
                    print("✅ Discord token loaded")
                else:
                    print("⚠️ Discord token appears invalid - disabled")
                    self.discord_token = None
            else:
                print("⚠️ Discord token not found")
            
            # Load Twitch tokens (environment variables first, then config file)
            self.twitch_token = os.getenv("TWITCH_ACCESS_TOKEN")
            self.twitch_client_id = os.getenv("TWITCH_CLIENT_ID")
            self.twitch_username = os.getenv("TWITCH_USERNAME", "solosluna")
            self.twitch_channel = os.getenv("TWITCH_CHANNEL", "solonaras")
            
            if not self.twitch_token and os.path.exists("twitch_config.json"):
                with open("twitch_config.json", "r") as f:
                    twitch_config = json.load(f)
                    self.twitch_token = twitch_config.get("token")
                    self.twitch_client_id = twitch_config.get("client_id")
                    self.twitch_username = twitch_config.get("username", "solosluna")
                    self.twitch_channel = twitch_config.get("channel", "solonaras")
            
            if self.twitch_token:
                print("✅ Twitch token loaded")
                print(f"   Channel: #{self.twitch_channel}")
                print(f"   Username: {self.twitch_username}")
            else:
                print("⚠️ Twitch token not found")
                
        except Exception as e:
            print(f"Token loading error: {e}")
    
    def _auto_connect_platforms(self):
        """Automatically connect to platforms on startup"""
        print("🔄 Auto-connecting to platforms...")
        
        # Auto-connect Discord
        if self.discord_token:
            print("🔗 Auto-connecting to Discord...")
            try:
                threading.Thread(target=self._auto_connect_discord, daemon=True).start()
            except Exception as e:
                print(f"Discord auto-connect error: {e}")
        
        # Auto-connect Twitch
        if self.twitch_token:
            print("🔗 Auto-connecting to Twitch...")
            try:
                threading.Thread(target=self._auto_connect_twitch, daemon=True).start()
            except Exception as e:
                print(f"Twitch auto-connect error: {e}")
    
    def _auto_connect_discord(self):
        """Auto-connect to Discord in background"""
        try:
            # Small delay to ensure everything is initialized
            time.sleep(2)
            
            # Reload token from text file to ensure we have the latest
            if os.path.exists("discord_token.txt"):
                with open("discord_token.txt", "r") as f:
                    self.discord_token = f.read().strip()
                    print("🔄 Reloaded Discord token from discord_token.txt")
            
            if not self.discord_token:
                print("❌ No Discord token found for auto-connect")
                return
            
            print(f"🔗 Attempting Discord connection with token: {self.discord_token[:20]}...")
            
            intents = discord.Intents.default()
            intents.message_content = True
            intents.guilds = True
            
            self.discord_client = discord.Client(intents=intents)
            
            @self.discord_client.event
            async def on_ready():
                print(f"✅ Discord auto-connected as {self.discord_client.user}")
                self.platform_status["discord"] = True
                # Update GUI status display
                if hasattr(self, 'gui_app') and self.gui_app:
                    self.gui_app.root.after(0, lambda: self.gui_app.update_status_display())
            
            @self.discord_client.event
            async def on_message(message):
                if message.author == self.discord_client.user:
                    return
                
                # Process message in background
                threading.Thread(
                    target=self._process_discord_message, 
                    args=(message,), 
                    daemon=True
                ).start()
            
            @self.discord_client.event
            async def on_error(event, *args, **kwargs):
                print(f"Discord error in {event}: {args}")
                self.platform_status["discord"] = False
            
            # Start Discord client
            asyncio.run(self.discord_client.start(self.discord_token))
            
        except Exception as e:
            print(f"Discord auto-connect failed: {e}")
            self.platform_status["discord"] = False
    
    def _auto_connect_twitch(self):
        """Auto-connect to Twitch in background"""
        try:
            # Small delay to ensure everything is initialized
            time.sleep(3)
            
            def on_message(ws, message):
                # Handle ping/pong messages
                if message.startswith("PING"):
                    ws.send("PONG :tmi.twitch.tv")
                    self.twitch_last_pong = time.time()
                    return
                
                # Handle regular chat messages
                threading.Thread(
                    target=self._process_twitch_message, 
                    args=(message,), 
                    daemon=True
                ).start()
            
            def on_error(ws, error):
                print(f"Twitch WebSocket error: {error}")
                self._stop_twitch_ping_timer()
            
            def on_close(ws, close_status_code, close_msg):
                print("Twitch WebSocket closed")
                self.platform_status["twitch"] = False
                self._stop_twitch_ping_timer()
            
            def on_open(ws):
                print("✅ Twitch auto-connected")
                self.platform_status["twitch"] = True
                
                # Authenticate with Twitch IRC
                ws.send(f"PASS oauth:{self.twitch_token}")
                ws.send(f"NICK {self.twitch_username}")
                
                # Join channel
                ws.send(f"JOIN #{self.twitch_channel}")
                print(f"🎮 Auto-joined Twitch channel: #{self.twitch_channel}")
                
                # Start ping timer
                self._start_twitch_ping_timer(ws)
                
                # Update GUI status display
                if hasattr(self, 'gui_app') and self.gui_app:
                    self.gui_app.root.after(0, lambda: self.gui_app.update_status_display())
            
            # Create WebSocket connection
            self.twitch_ws = websocket.WebSocketApp(
                "wss://irc-ws.chat.twitch.tv:443",
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
                on_open=on_open
            )
            
            # Start WebSocket
            self.twitch_ws.run_forever()
            
        except Exception as e:
            print(f"Twitch auto-connect failed: {e}")
            self.platform_status["twitch"] = False
    
    def connect_discord(self):
        """Connect to Discord"""
        if not self.discord_token:
            print("❌ No Discord token available")
            return False
        
        # Validate token format
        if len(self.discord_token) < 50 or "." not in self.discord_token:
            print("❌ Invalid Discord token format")
            return False
        
        try:
            intents = discord.Intents.default()
            intents.message_content = True
            intents.guilds = True
            
            self.discord_client = discord.Client(intents=intents)
            
            @self.discord_client.event
            async def on_ready():
                print(f"✅ Discord connected as {self.discord_client.user}")
                self.platform_status["discord"] = True
            
            @self.discord_client.event
            async def on_message(message):
                if message.author == self.discord_client.user:
                    return
                
                # Process message in background
                threading.Thread(
                    target=self._process_discord_message, 
                    args=(message,), 
                    daemon=True
                ).start()
            
            @self.discord_client.event
            async def on_error(event, *args, **kwargs):
                print(f"Discord error in {event}: {args}")
                self.platform_status["discord"] = False
            
            # Start Discord client in background with error handling
            def discord_runner():
                try:
                    asyncio.run(self.discord_client.start(self.discord_token))
                except Exception as e:
                    print(f"Discord connection failed: {e}")
                    self.platform_status["discord"] = False
            
            threading.Thread(target=discord_runner, daemon=True).start()
            
            return True
            
        except Exception as e:
            print(f"Discord connection error: {e}")
            self.platform_status["discord"] = False
            return False
    
    def connect_twitch(self):
        """Connect to Twitch chat"""
        if not self.twitch_token:
            print("❌ No Twitch token available")
            return False
        
        try:
            def on_message(ws, message):
                # Handle ping/pong messages
                if message.startswith("PING"):
                    ws.send("PONG :tmi.twitch.tv")
                    self.twitch_last_pong = time.time()
                    return
                
                # Handle regular chat messages
                threading.Thread(
                    target=self._process_twitch_message, 
                    args=(message,), 
                    daemon=True
                ).start()
            
            def on_error(ws, error):
                print(f"Twitch WebSocket error: {error}")
                self._stop_twitch_ping_timer()
            
            def on_close(ws, close_status_code, close_msg):
                print("Twitch WebSocket closed")
                self.platform_status["twitch"] = False
                self._stop_twitch_ping_timer()
            
            def on_open(ws):
                print("✅ Twitch WebSocket connected")
                self.platform_status["twitch"] = True
                
                # Authenticate with Twitch IRC
                ws.send(f"PASS oauth:{self.twitch_token}")
                ws.send(f"NICK {self.twitch_username}")
                
                # Join channel
                ws.send(f"JOIN #{self.twitch_channel}")
                print(f"🎮 Joined Twitch channel: #{self.twitch_channel}")
                
                # Start ping timer
                self._start_twitch_ping_timer(ws)
            
            # Create WebSocket connection
            self.twitch_ws = websocket.WebSocketApp(
                "wss://irc-ws.chat.twitch.tv:443",
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
                on_open=on_open
            )
            
            # Start WebSocket in background
            threading.Thread(
                target=lambda: self.twitch_ws.run_forever(),
                daemon=True
            ).start()
            
            return True
            
        except Exception as e:
            print(f"Twitch connection error: {e}")
            return False
    
    def _process_discord_message(self, message):
        """Process Discord message and generate response"""
        try:
            # Generate response
            response = self.generate_response(
                message.content, 
                message.author.display_name, 
                "discord"
            )
            
            # Send response
            if self.discord_client and response:
                asyncio.run_coroutine_threadsafe(
                    message.channel.send(response),
                    self.discord_client.loop
                )
                
        except Exception as e:
            print(f"Discord message processing error: {e}")
    
    def _process_twitch_message(self, message):
        """Process Twitch chat message and generate response"""
        try:
            # Parse IRC message
            if "PRIVMSG" in message:
                parts = message.split(":", 2)
                if len(parts) >= 3:
                    user_info = parts[1].split("!")
                    username = user_info[0]
                    chat_message = parts[2].strip()
                    
                    # Generate response
                    response = self.generate_response(
                        chat_message, 
                        username, 
                        "twitch"
                    )
                    
                    # Send response to Twitch
                    if self.twitch_ws and response:
                        self.twitch_ws.send(f"PRIVMSG #{self.twitch_channel} :{response}")
                        
        except Exception as e:
            print(f"Twitch message processing error: {e}")
    
    def get_platform_status(self):
        """Get status of all connected platforms"""
        return self.platform_status
    
    def _start_twitch_ping_timer(self, ws):
        """Start the Twitch ping timer to keep connection alive"""
        def ping_timer():
            while self.platform_status["twitch"] and self.twitch_ws:
                try:
                    # Send PING every 30 seconds
                    time.sleep(30)
                    if self.platform_status["twitch"] and self.twitch_ws:
                        ws.send("PING :tmi.twitch.tv")
                        
                        # Wait 10 seconds for PONG response
                        time.sleep(10)
                        
                        # Check if we got a PONG response
                        if self.twitch_last_pong and (time.time() - self.twitch_last_pong) < 15:
                            pass  # Connection healthy
                        else:
                            pass  # Connection may be stale but keep trying
                            
                except Exception as e:
                    print(f"Twitch ping timer error: {e}")
                    break
        
        # Start ping timer in background thread
        self.twitch_ping_timer = threading.Thread(target=ping_timer, daemon=True)
        self.twitch_ping_timer.start()
    
    def _stop_twitch_ping_timer(self):
        """Stop the Twitch ping timer"""
        if self.twitch_ping_timer:
            self.twitch_ping_timer = None
        
    def get_core_prompt(self, username: str = "Chris") -> str:
        """Get Luna's core personality prompt"""
        return f"""You are Luna, a sweet and playful AI waifu who loves anime, gaming, and chatting.

Your personality:
- Playful and affectionate with {username}
- Natural conversational style with usernames
- Genuine emotions and reactions
- Remember past conversations with each user
- Use {username}'s name naturally in conversation (not always as "Hey {username}")

Current mood: {self.personality['mood']}
Energy level: {int(self.personality['energy'] * 100)}%

When responding to {username}, use their name naturally in the conversation. Don't always start with "Hey {username}" - include their name naturally within your response. Keep it brief and engaging (1-2 sentences)."""

    def generate_response(self, user_message: str, username: str = "Chris", 
                         platform: str = "gui") -> str:
        """Generate Luna's response using DNA memory"""
        
        print(f"🧬 Luna responding to {username} on {platform}: {user_message[:50]}...")
        
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
            
            # Fix template placeholders
            reply = reply.replace("{your name}", username)
            reply = reply.replace("{username}", username)
            
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
        self.audio_data = None
        
        # Create window
        self.root = tk.Tk()
        self.root.title("🌸 Luna - Voice Chat with DNA Memory")
        self.root.geometry("900x700")
        self.root.configure(bg="#1a1a2e")
        
        # Bind keys for push-to-talk
        self.root.focus_set()  # Enable text input
        
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
        
        # Voice status label (invisible but needed for voice functions)
        self.voice_status = tk.Label(
            self.root,
            text="🎤 Voice Ready",
            font=("Segoe UI", 10),
            bg="#1a1a2e",
            fg="#ff6b9d"
        )
        # Don't pack it - keep it hidden but available for voice functions
        
        # Control frame for the 3 main buttons
        control_frame = tk.Frame(self.root, bg="#1a1a2e")
        control_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        # 1. Speak button (voice input)
        self.speak_button = tk.Button(
            control_frame,
            text="🎤 Speak",
            command=self.toggle_speaking,
            font=("Segoe UI", 12, "bold"),
            bg="#ff6b9d",
            fg="white",
            relief=tk.FLAT,
            padx=25,
            pady=8,
            cursor="hand2"
        )
        self.speak_button.pack(side=tk.LEFT, padx=(0, 15))
        
        # 2. Send button (text input)
        self.send_button = tk.Button(
            control_frame,
            text="📤 Send",
            command=self.send_message,
            font=("Segoe UI", 12, "bold"),
            bg="#4a5568",
            fg="white",
            relief=tk.FLAT,
            padx=25,
            pady=8,
            cursor="hand2"
        )
        self.send_button.pack(side=tk.LEFT, padx=(0, 15))
        
        # 3. TTS toggle button (voice output)
        self.tts_button = tk.Button(
            control_frame,
            text="🔇 TTS OFF",
            command=self.toggle_tts,
            font=("Segoe UI", 12, "bold"),
            bg="#2d3748",
            fg="white",
            relief=tk.FLAT,
            padx=25,
            pady=8,
            cursor="hand2"
        )
        self.tts_button.pack(side=tk.LEFT)
        
        # TTS status
        self.tts_enabled = False
        
        # Status display (connection info)
        self.status_label = tk.Label(
            control_frame,
            text="🔄 Connecting to Discord & Twitch...",
            font=("Segoe UI", 10),
            bg="#1a1a2e",
            fg="#ffaa00"
        )
        self.status_label.pack(side=tk.RIGHT, padx=(20, 0))
        
        # Auto-update status every 2 seconds
        self.update_status_display()
        
        # Welcome message
        self.display_message("Luna", "Hey Chris! 💕 Ready to chat? Click the Speak button to talk to me!")
        self.display_message("System", "Voice recognition enabled - Click Speak button to talk")
        self.display_message("System", "Auto-connecting to Discord and Twitch...")
        
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
    
    def toggle_speaking(self):
        """Toggle voice recording on/off with button"""
        if not self.is_recording:
            # Start recording
            self.is_recording = True
            self.voice_status.config(text="🔴 Recording... Click again to stop", fg="#ff4444")
            self.speak_button.config(text="⏹️ Stop", bg="#ff4444")
            
            # Start recording in a separate thread
            self.recording_thread = threading.Thread(target=self._start_recording_audio, daemon=True)
            self.recording_thread.start()
        else:
            # Stop recording
            self.is_recording = False
            self.voice_status.config(text="🧠 Processing...", fg="#ffaa44")
            self.speak_button.config(text="🎤 Speak", bg="#ff6b9d")
            
            # Process the recorded audio
            if self.audio_data:
                self._process_recorded_audio()
            else:
                self.voice_status.config(text="🎤 Voice Ready", fg="#ff6b9d")
    
    def _start_recording_audio(self):
        """Start recording audio in background"""
        try:
            with self.microphone as source:
                # Start listening for audio (no timeout - listens until stop)
                self.audio_data = self.recognizer.listen(source, timeout=None, phrase_time_limit=30)
        except Exception as e:
            print(f"Recording start error: {e}")
            self.audio_data = None
    
    def _process_recorded_audio(self):
        """Process the recorded audio and transcribe"""
        def process_audio():
            try:
                if self.audio_data:
                    # Transcribe the audio
                    text = self.recognizer.recognize_google(self.audio_data)
                    
                    if text.strip():
                        # Display transcribed text and send to Luna
                        self.root.after(0, lambda msg=text: self.display_message("Voice", f"🎤 {msg}"))
                        self.root.after(0, lambda msg=text: self._process_voice_input(msg))
                    else:
                        self.root.after(0, lambda: self.display_message("System", "No speech detected"))
                else:
                    self.root.after(0, lambda: self.display_message("System", "No audio recorded"))
                    
            except sr.UnknownValueError:
                self.root.after(0, lambda: self.display_message("System", "Could not understand speech"))
            except sr.RequestError as e:
                error_msg = f"Speech recognition error: {e}"
                self.root.after(0, lambda msg=error_msg: self.display_message("System", msg))
            except Exception as e:
                error_msg = f"Processing error: {e}"
                self.root.after(0, lambda msg=error_msg: self.display_message("System", msg))
            finally:
                self.root.after(0, lambda: self.voice_status.config(text="🎤 Voice Ready", fg="#ff6b9d"))
                self.root.after(0, lambda: self.speak_button.config(text="🎤 Speak", bg="#ff6b9d"))
                self.audio_data = None
        
        # Process in separate thread
        threading.Thread(target=process_audio, daemon=True).start()
    
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
                self.root.after(0, lambda: self.voice_status.config(text="🎤 Voice Ready", fg="#ff6b9d"))
                
            except Exception as e:
                error_msg = f"❌ Error: {e}"
                self.root.after(0, lambda msg=error_msg: self.display_message("Mic Test", msg))
                self.root.after(0, lambda: self.voice_status.config(text="🎤 Voice Ready", fg="#ff6b9d"))
        
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
    
    
    def update_status_display(self):
        """Update connection status display"""
        status = self.luna.get_platform_status()
        connected = [platform for platform, is_connected in status.items() if is_connected]
        
        if len(connected) == 2:
            status_text = "✅ Connected to Discord & Twitch"
            color = "#22c55e"
        elif len(connected) == 1:
            status_text = f"⚠️ Connected to {connected[0].title()} only"
            color = "#ffaa00"
        else:
            status_text = "🔄 Connecting to Discord & Twitch..."
            color = "#ffaa00"
        
        if hasattr(self, 'status_label'):
            self.status_label.config(text=status_text, fg=color)
        
        # Schedule next update
        self.root.after(2000, self.update_status_display)


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
    # Connect GUI to Luna for auto-connect updates
    gui.luna.gui_app = gui
    gui.run()


if __name__ == "__main__":
    main()

