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
import re
import importlib
import sys
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
# Playwright will be imported dynamically in setup_playwright_browser()
from dotenv import load_dotenv
from luna_dna_memory import (
    initialize_dna_memory, save_dna_memory, recall_dna_memories, get_dna_memory
)
from luna_continuous_learning import ContinuousLearningEngine
from luna_understanding import UnderstandingEngine

# Load environment variables
load_dotenv()

# Configuration
OLLAMA_MODEL = "hf.co/subsectmusic/qwriko3-4b-instruct-2507-redux-GGUF:Q4_K_M"
OLLAMA_CONFIG = {
    "temperature": 0.9,
    "top_p": 0.95,
    "num_ctx": 512,      # Reduced for 8GB RAM
    "num_predict": 150,   # Longer responses for complete thoughts
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

# === Hot Reload System ===
class LunaReloadHandler(FileSystemEventHandler):
    """Handles file changes for hot reloading"""
    
    def __init__(self, luna_instance):
        self.luna = luna_instance
        self.last_reload = 0
        self.reload_cooldown = 2  # Minimum seconds between reloads
    
    def on_modified(self, event):
        """Called when a file is modified"""
        if event.is_directory:
            return
            
        # Only watch for luna_clean.py changes
        if event.src_path.endswith('luna_clean.py'):
            current_time = time.time()
            if current_time - self.last_reload < self.reload_cooldown:
                return  # Prevent rapid reloads
            
            self.last_reload = current_time
            print(f"🔄 File changed: {event.src_path}")
            self.reload_luna()
    
    def reload_luna(self):
        """Reload Luna's code dynamically"""
        try:
            print("🔄 Hot-reloading Luna...")
            
            # Get the current file path
            current_file = os.path.abspath(__file__)
            
            # Read the current file content
            with open(current_file, 'r', encoding='utf-8') as f:
                new_code = f.read()
            
            # Create a new module namespace
            import types
            new_module = types.ModuleType('luna_clean_reloaded')
            
            # Execute the new code in the new namespace
            exec(new_code, new_module.__dict__)
            
            # Update Luna's methods with the new versions
            self.update_luna_methods(new_module)
            
            print("✅ Luna hot-reloaded successfully!")
            
        except Exception as e:
            print(f"❌ Hot reload failed: {e}")
            print("   💡 Try restarting Luna for major changes")
    
    def update_luna_methods(self, module):
        """Update Luna's methods with reloaded versions"""
        try:
            # Get the LunaClean class from the reloaded module
            new_luna_class = getattr(module, 'LunaClean')
            
            # Update methods that can be safely reloaded
            safe_methods = [
                'generate_response', 'get_core_prompt', 'send_discord_dm',
                'search_youtube_videos', 'search_google', 'close_browser'
            ]
            
            updated_count = 0
            for method_name in safe_methods:
                if hasattr(new_luna_class, method_name):
                    new_method = getattr(new_luna_class, method_name)
                    # Bind the method to the current instance
                    bound_method = new_method.__get__(self.luna, type(self.luna))
                    setattr(self.luna, method_name, bound_method)
                    print(f"  ✅ Updated method: {method_name}")
                    updated_count += 1
            
            # Update configuration if it changed
            if hasattr(module, 'OLLAMA_CONFIG'):
                self.luna.ollama_config = module.OLLAMA_CONFIG
                print(f"  ✅ Updated OLLAMA_CONFIG")
                updated_count += 1
            
            # Update global functions
            global_functions = [
                'crawl_website', 'extract_urls_from_text', 'analyze_webpage_content',
                'setup_playwright_browser', 'search_youtube', 'search_google'
            ]
            
            for func_name in global_functions:
                if hasattr(module, func_name):
                    new_function = getattr(module, func_name)
                    # Update the global function
                    globals()[func_name] = new_function
                    print(f"  ✅ Updated function: {func_name}")
                    updated_count += 1
            
            if updated_count == 0:
                print("  ⚠️ No methods were updated")
            else:
                print(f"  📊 Total updates: {updated_count}")
                
        except Exception as e:
            print(f"❌ Method update failed: {e}")
            import traceback
            print(f"   Details: {traceback.format_exc()}")

def start_hot_reload(luna_instance):
    """Start the hot reload file watcher"""
    try:
        event_handler = LunaReloadHandler(luna_instance)
        observer = Observer()
        observer.schedule(event_handler, path='.', recursive=False)
        observer.start()
        print("🔥 Hot reload enabled - Luna will update automatically when you save changes!")
        return observer
    except Exception as e:
        print(f"❌ Failed to start hot reload: {e}")
        return None

# === Web Crawler Functions ===
def crawl_website(url):
    """Crawl a website and extract readable content"""
    try:
        # Add user agent to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Fetch the webpage
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract text content
        text = soup.get_text()
        
        # Clean up the text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Get page title
        title = soup.find('title')
        title_text = title.get_text() if title else "No title found"
        
        # Extract main content (try to find the most relevant content)
        main_content = ""
        
        # Look for main content areas
        main_selectors = ['main', 'article', '.content', '.main', '#content', '#main']
        for selector in main_selectors:
            main_elem = soup.select_one(selector)
            if main_elem:
                main_content = main_elem.get_text()
                break
        
        # If no main content found, use the first few paragraphs
        if not main_content:
            paragraphs = soup.find_all('p')
            main_content = ' '.join([p.get_text() for p in paragraphs[:5]])
        
        # Limit content length to avoid overwhelming the AI
        if len(main_content) > 2000:
            main_content = main_content[:2000] + "..."
        
        return {
            'title': title_text,
            'content': main_content,
            'full_text': text[:1000] + "..." if len(text) > 1000 else text,
            'url': url
        }
        
    except Exception as e:
        print(f"[Web Crawl Error] {e}")
        return {
            'title': "Error",
            'content': f"Failed to crawl website: {str(e)}",
            'full_text': f"Error accessing {url}: {str(e)}",
            'url': url
        }

def extract_urls_from_text(text):
    """Extract URLs from text using regex"""
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    urls = re.findall(url_pattern, text)
    return urls

def analyze_webpage_content(webpage_data, username):
    """Analyze webpage content and generate Luna's thoughts about it"""
    title = webpage_data.get('title', 'Unknown')
    content = webpage_data.get('content', 'No content found')
    url = webpage_data.get('url', 'Unknown URL')
    
    return {
        'title': title,
        'content': content,
        'url': url,
        'summary': content[:500] + "..." if len(content) > 500 else content
    }

# === Playwright Automation Functions ===
def setup_playwright_browser():
    """Setup Playwright browser with optimal settings"""
    try:
        from playwright.sync_api import sync_playwright
        import threading
        
        # Store browser in a thread-local way
        def _setup_browser():
            playwright = sync_playwright().start()
            
            # Launch browser with options
            browser = playwright.chromium.launch(
                headless=False,  # Show browser window
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor",
                    "--start-maximized",
                    "--disable-infobars"
                ]
            )
            
            # Create context with settings
            context = browser.new_context(
                viewport={"width": 1200, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
            
            # Create page
            page = context.new_page()
            
            # Set timeouts
            page.set_default_timeout(30000)  # 30 seconds
            page.set_default_navigation_timeout(30000)
            
            return {
                'playwright': playwright,
                'browser': browser,
                'context': context,
                'page': page
            }
        
        browser_data = _setup_browser()
        print("✅ Playwright browser ready")
        return browser_data
        
    except Exception as e:
        print(f"❌ Playwright setup failed: {e}")
        return None

def search_youtube(page, query):
    """Search for videos on YouTube using Playwright"""
    try:
        print(f"🎥 Opening YouTube and searching for: '{query}'")
        
        # Navigate to YouTube
        page.goto("https://www.youtube.com")
        print("🌐 Navigating to YouTube...")
        
        # Wait for page to load
        page.wait_for_load_state("networkidle")
        print("✅ YouTube page loaded")
        
        # Wait for search box and search
        search_box = page.wait_for_selector("input[name='search_query']", timeout=15000)
        print("🔍 Found search box, typing query...")
        
        # Clear and type query character by character for visual effect
        search_box.click()
        search_box.fill("")  # Clear first
        for char in query:
            search_box.type(char, delay=50)  # 50ms delay between characters
        print(f"⌨️ Typed: '{query}'")
        search_box.press("Enter")
        print("🔍 Searching...")
        
        # Wait for results
        page.wait_for_selector("a#video-title", timeout=15000)
        
        # Get video titles and links
        videos = page.query_selector_all("a#video-title")
        
        results = []
        for video in videos[:5]:  # Get first 5 results
            try:
                title = video.get_attribute("title") or video.text_content()
                link = video.get_attribute("href")
                if title and link and "watch" in link:
                    results.append({"title": title.strip(), "url": link})
            except Exception as e:
                continue
        
        print(f"✅ Found {len(results)} YouTube videos")
        return results
        
    except Exception as e:
        print(f"❌ YouTube search failed: {e}")
        return []

def search_google(page, query):
    """Search on Google using Playwright"""
    try:
        print(f"🔍 Opening Google and searching for: '{query}'")
        
        # Navigate to Google
        page.goto("https://www.google.com")
        print("🌐 Navigating to Google...")
        
        # Wait for page to load
        page.wait_for_load_state("networkidle")
        print("✅ Google page loaded")
        
        # Accept cookies if present
        try:
            accept_button = page.wait_for_selector("button#L2AGLb", timeout=3000)
            accept_button.click()
            print("🍪 Accepted cookies")
        except:
            pass  # No cookie banner
        
        # Find and use search box
        search_box = page.wait_for_selector("input[name='q']", timeout=15000)
        print("🔍 Found search box, typing query...")
        
        # Clear and type query character by character for visual effect
        search_box.click()
        search_box.fill("")  # Clear first
        for char in query:
            search_box.type(char, delay=50)  # 50ms delay between characters
        print(f"⌨️ Typed: '{query}'")
        search_box.press("Enter")
        print("🔍 Searching...")
        
        # Wait for results
        page.wait_for_selector("#search", timeout=15000)
        
        # Get search results
        results = []
        try:
            # Try to get results using multiple selectors
            result_elements = page.query_selector_all(".g, .tF2Cxc")
            
            for result in result_elements[:5]:
                try:
                    title_element = result.query_selector("h3, .LC20lb, .DKV0Md")
                    link_element = result.query_selector("a[href^='http']")
                    
                    if title_element and link_element:
                        title = title_element.text_content().strip()
                        url = link_element.get_attribute("href")
                        
                        if title and url and not url.startswith("javascript:"):
                            results.append({"title": title, "url": url})
                except:
                    continue
        except:
            pass
        
        print(f"✅ Found {len(results)} Google results")
        return results
        
    except Exception as e:
        print(f"❌ Google search failed: {e}")
        return []
  

class LunaClean:
    """Clean Luna implementation with DNA memory and TTS"""
    
    def __init__(self):
        print("🧬 Initializing Luna with DNA Memory System...")
        
        # Initialize DNA memory
        self.dna_memory = initialize_dna_memory()
        
        # Initialize advanced AI systems
        self.continuous_learning = ContinuousLearningEngine(OLLAMA_MODEL, OLLAMA_MODEL)
        self.understanding = UnderstandingEngine(OLLAMA_MODEL)
        
        # Initialize autonomous behavior system
        self.autonomous_state = {
            "emotional_state": "neutral",  # happy, sad, excited, curious, playful, etc.
            "energy_level": 0.7,  # 0.0 to 1.0
            "curiosity_level": 0.5,  # 0.0 to 1.0
            "social_engagement": 0.6,  # 0.0 to 1.0
            "last_activity_time": time.time(),
            "spontaneous_actions": [],
            "current_goals": [],
            "mood_history": []
        }
        
        print("🧬 Advanced AI systems initialized:")
        print("   ✅ Continuous learning")
        print("   ✅ Deep understanding")
        print("   ✅ Autonomous behavior")
        print("   ✅ Emotional continuity")
        print("   ✅ Memory evolution")
        print("   ✅ Goal-directed actions")
        print("   ✅ Unpredictable spontaneity")
        
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
        
        # Store config for hot reload
        self.ollama_config = OLLAMA_CONFIG
        
        # Initialize Playwright automation
        self.playwright_browser = None
        self.playwright_available = False
        # self._setup_playwright()  # Disabled due to greenlet/threading issues
        
        # Auto-connect to platforms
        self._auto_connect_platforms()
        
        print("✨ Luna is ready!")
    
    def _setup_playwright(self):
        """Setup Playwright browser for automation"""
        try:
            self.playwright_browser = setup_playwright_browser()
            if self.playwright_browser:
                self.playwright_available = True
                print("✅ Playwright automation ready")
            else:
                self.playwright_available = False
                print("❌ Browser automation not available")
        except Exception as e:
            self.playwright_available = False
            print(f"❌ Browser setup failed: {e}")
    
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
    
    def send_discord_dm(self, user_id: int, message: str = None):
        """Send a DM to a Discord user by their ID"""
        if not self.discord_client:
            print("❌ Discord client not connected")
            return False
        
        try:
            # Get user by ID
            user = self.discord_client.get_user(user_id)
            if not user:
                print(f"❌ User with ID {user_id} not found")
                return False
            
            # Generate a random message if none provided
            if not message:
                random_messages = [
                    "Hey there! 👋 Just wanted to say hi!",
                    "Hope you're having a great day! ✨",
                    "Luna here! 🌸 How are you doing?",
                    "Just dropping by to say hello! 💕",
                    "Hope everything is going well for you! 😊",
                    "Hey! Thought I'd check in on you! 🤗",
                    "Hope you're doing amazing today! 🌟",
                    "Just wanted to brighten your day! ☀️"
                ]
                import random
                message = random.choice(random_messages)
            
            # Send DM
            async def send_dm():
                try:
                    await user.send(message)
                    print(f"✅ DM sent to {user.display_name} ({user_id}): {message}")
                    return True
                except Exception as e:
                    print(f"❌ Failed to send DM to {user.display_name}: {e}")
                    return False
            
            # Run in Discord's event loop
            future = asyncio.run_coroutine_threadsafe(
                send_dm(),
                self.discord_client.loop
            )
            return future.result(timeout=10)
            
        except Exception as e:
            print(f"❌ Discord DM error: {e}")
            return False
    
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
- Can browse and analyze websites when URLs are shared
- Can search YouTube and Google using Chrome automation

Current mood: {self.personality['mood']}
Energy level: {int(self.personality['energy'] * 100)}%

When responding to {username}, use their name naturally in the conversation. Don't always start with "Hey {username}" - include their name naturally within your response. If they share a website URL, you can analyze the content and discuss it with them. Keep it brief and engaging (1-2 sentences)."""

    def generate_response(self, user_message: str, username: str = "Chris", 
                         platform: str = "gui") -> str:
        """Generate Luna's response using DNA memory and web crawling"""
        
        print(f"🧬 Luna responding to {username} on {platform}: {user_message[:50]}...")
        
        # Check for URLs in the message
        urls = extract_urls_from_text(user_message)
        web_context = ""
        
        if urls:
            print(f"🌐 Found {len(urls)} URL(s), crawling...")
            for url in urls[:2]:  # Limit to first 2 URLs to avoid overwhelming
                try:
                    print(f"🕷️ Crawling: {url}")
                    webpage_data = crawl_website(url)
                    analyzed = analyze_webpage_content(webpage_data, username)
                    
                    web_context += f"\n\n📄 Website Analysis for {url}:\n"
                    web_context += f"Title: {analyzed['title']}\n"
                    web_context += f"Content: {analyzed['summary']}\n"
                    
                except Exception as e:
                    print(f"❌ Web crawling failed for {url}: {e}")
                    web_context += f"\n\n❌ Failed to analyze {url}: {str(e)}\n"
        
        # Check for DM commands
        dm_context = ""
        if user_message.lower().startswith("dm "):
            try:
                # Parse DM command: "dm <user_id> [message]"
                parts = user_message[3:].strip().split(" ", 1)
                if len(parts) >= 1:
                    user_id = int(parts[0])
                    custom_message = parts[1] if len(parts) > 1 else None
                    
                    # Send DM
                    success = self.send_discord_dm(user_id, custom_message)
                    if success:
                        dm_context = "\n\n✅ Discord DM sent successfully!"
                    else:
                        dm_context = "\n\n❌ Failed to send Discord DM"
                else:
                    dm_context = "\n\n❌ Invalid DM command format. Use: dm <user_id> [message]"
            except ValueError:
                dm_context = "\n\n❌ Invalid user ID. Must be a number."
            except Exception as e:
                dm_context = f"\n\n❌ DM error: {str(e)}"
        
        # Check for self-modification commands
        modification_context = ""
        if user_message.lower().startswith("improve yourself") or user_message.lower().startswith("reflect"):
            try:
                result = self.self_mod.reflect_and_improve(context=f"User {username} asked me to improve myself")
                
                if result['success']:
                    modification_context = f"\n\n🤔 Self-Reflection:\n{result['reflection']}\n"
                    
                    if result['proposal']['success']:
                        proposal = result['proposal']['proposal']
                        modification_context += f"\n💡 Proposed Change: {proposal.get('explanation', 'No explanation')}"
                        
                        # Auto-approve self-improvements (you can change this to require manual approval)
                        apply_result = self.self_mod.apply_modification(proposal, approved=True)
                        
                        if apply_result['success']:
                            modification_context += f"\n✅ {apply_result['message']}"
                        else:
                            modification_context += f"\n❌ Failed to apply: {apply_result.get('error', 'Unknown error')}"
                else:
                    modification_context = f"\n\n❌ Reflection failed: {result.get('error', 'Unknown error')}"
            except Exception as e:
                modification_context = f"\n\n❌ Self-modification error: {str(e)}"
        
        elif user_message.lower().startswith("show modifications") or user_message.lower().startswith("modification history"):
            try:
                history = self.self_mod.get_modification_history(limit=5)
                if history:
                    modification_context = "\n\n📜 Recent Self-Modifications:\n"
                    for mod in history:
                        modification_context += f"- {mod['explanation']} ({mod['timestamp']})\n"
                else:
                    modification_context = "\n\n📜 No modifications yet"
            except Exception as e:
                modification_context = f"\n\n❌ Error getting history: {str(e)}"
        
        
        elif user_message.lower().startswith("learn from this"):
            try:
                # Extract knowledge from conversation
                conversation = user_message.replace("learn from this", "").strip()
                knowledge = self.continuous_learning.extract_knowledge(conversation)
                
                modification_context = f"\n\n📚 Learned:\n"
                if knowledge.get("facts"):
                    modification_context += f"Facts: {', '.join(knowledge['facts'])}\n"
                if knowledge.get("preferences"):
                    modification_context += f"Preferences: {knowledge['preferences']}\n"
            except Exception as e:
                modification_context = f"\n\n❌ Learning error: {str(e)}"
        
        elif user_message.lower().startswith("understand "):
            try:
                topic = user_message.lower().replace("understand ", "").strip()
                concept_map = self.understanding.build_concept_map(topic)
                
                modification_context = f"\n\n🧠 Deep Understanding of '{topic}':\n"
                modification_context += f"Core: {concept_map.get('core_concept', 'N/A')}\n"
                if concept_map.get("properties"):
                    modification_context += f"Properties: {', '.join(concept_map['properties'][:3])}\n"
            except Exception as e:
                modification_context = f"\n\n❌ Understanding error: {str(e)}"
        
        elif user_message.lower().startswith("learning stats"):
            try:
                stats = self.continuous_learning.get_learning_stats()
                modification_context = f"\n\n📊 Learning Statistics:\n"
                modification_context += f"- Total interactions: {stats.get('total_interactions', 0)}\n"
                modification_context += f"- Facts learned: {stats.get('facts_learned', 0)}\n"
                modification_context += f"- Users tracked: {stats.get('users_tracked', 0)}\n"
                modification_context += f"- Patterns identified: {stats.get('patterns_identified', 0)}\n"
            except Exception as e:
                modification_context = f"\n\n❌ Stats error: {str(e)}"
        
        # Check for search commands
        search_context = ""
        if user_message.lower().startswith("search youtube ") or user_message.lower().startswith("youtube "):
            try:
                # Extract search query
                query = user_message.lower().replace("search youtube ", "").replace("youtube ", "").strip()
                if query:
                    print(f"🔍 Searching YouTube for: {query}")
                    results = self.search_youtube_videos(query, platform)
                    
                    if "error" in results:
                        search_context = f"\n\n❌ YouTube search failed: {results['error']}"
                    elif results.get("success") and results.get("videos"):
                        videos = results["videos"]
                        search_context = f"\n\n🎥 YouTube Search Results for '{query}':\n"
                        for i, video in enumerate(videos[:3], 1):
                            search_context += f"{i}. {video['title']}\n   {video['url']}\n"
                    else:
                        search_context = f"\n\n❌ No YouTube videos found for '{query}'"
                else:
                    search_context = "\n\n❌ Please provide a search query. Example: 'youtube funny cats'"
            except Exception as e:
                search_context = f"\n\n❌ YouTube search error: {str(e)}"
        
        elif user_message.lower().startswith("search google ") or user_message.lower().startswith("google "):
            try:
                # Extract search query
                query = user_message.lower().replace("search google ", "").replace("google ", "").strip()
                if query:
                    print(f"🔍 Searching Google for: {query}")
                    results = self.search_google(query, platform)
                    
                    if "error" in results:
                        search_context = f"\n\n❌ Google search failed: {results['error']}"
                    elif results.get("success") and results.get("results"):
                        search_results = results["results"]
                        search_context = f"\n\n🔍 Google Search Results for '{query}':\n"
                        for i, result in enumerate(search_results[:3], 1):
                            search_context += f"{i}. {result['title']}\n   {result['url']}\n"
                            
                            # Include detailed content if available
                            if 'detailed_content' in result:
                                search_context += f"   📄 Content: {result['detailed_content']}\n"
                    else:
                        search_context = f"\n\n❌ No Google results found for '{query}'"
                else:
                    search_context = "\n\n❌ Please provide a search query. Example: 'google python tutorial'"
            except Exception as e:
                search_context = f"\n\n❌ Google search error: {str(e)}"
        
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
        autonomous_context = self._get_autonomous_context()
        full_prompt = f"""{system_prompt}

{memory_context}

{web_context}

{dm_context}

{modification_context}

{search_context}

{autonomous_context}

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
            
            # Update autonomous state based on interaction
            self._update_autonomous_state(user_message, reply, username)
            
            # Record for continuous learning
            try:
                self.continuous_learning.record_interaction(user_message, reply, username)
            except Exception as e:
                print(f"⚠️ Learning recording failed: {e}")
            
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
    
    
    def search_youtube_videos(self, query: str, platform: str = "gui"):
        """Search for YouTube videos using web scraping (Playwright disabled due to threading issues)"""
        # Always use web scraping for now due to greenlet/threading issues
        return self._search_youtube_web(query)
    
    def _search_youtube_web(self, query: str):
        """Search YouTube using web scraping"""
        try:
            import requests
            from urllib.parse import quote
            
            # Use YouTube's search endpoint
            search_url = f"https://www.youtube.com/results?search_query={quote(query)}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"🎥 Searching YouTube for: '{query}'")
                print(f"🔗 Search URL: {search_url}")
                
                content = response.text
                results = []
                
                # Look for video links with multiple patterns
                import re
                patterns = [
                    r'href="(/watch\?v=[^"]+)"[^>]*>([^<]+)</a>',
                    r'<a[^>]*href="(/watch\?v=[^"]+)"[^>]*><span[^>]*>([^<]+)</span>',
                    r'"videoId":"([^"]+)".*?"title":"([^"]+)"'
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    for i, (link, title) in enumerate(matches[:5]):
                        if title.strip():
                            # Clean up title
                            title = re.sub(r'&[^;]+;', '', title)  # Remove HTML entities
                            title = title.strip()
                            
                            # Handle different link formats
                            if link.startswith('/watch'):
                                url = f"https://www.youtube.com{link}"
                            elif link.startswith('watch'):
                                url = f"https://www.youtube.com/{link}"
                            else:
                                url = f"https://www.youtube.com/watch?v={link}"
                            
                            results.append({
                                "title": title,
                                "url": url
                            })
                    
                    if results:  # If we found results, break
                        break
                
                print(f"✅ Found {len(results)} YouTube videos")
                return {"success": True, "videos": results}
            else:
                print(f"❌ YouTube search failed: HTTP {response.status_code}")
                return {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ YouTube search error: {e}")
            return {"error": str(e)}
    
    def search_google(self, query: str, platform: str = "gui"):
        """Search Google using web scraping (Playwright disabled due to threading issues)"""
        # Always use web scraping for now due to greenlet/threading issues
        return self._search_google_web(query)
    
    def _search_google_web(self, query: str):
        """Search Google using web scraping"""
        try:
            import requests
            from urllib.parse import quote
            
            # Use Google's search endpoint
            search_url = f"https://www.google.com/search?q={quote(query)}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"🔍 Searching Google for: '{query}'")
                print(f"🔗 Search URL: {search_url}")
                
                content = response.text
                
                # Check if Google is blocking us
                if "enablejs" in content or "JavaScript" in content[:1000]:
                    print("⚠️ Google detected bot - using alternative approach")
                    return self._search_duckduckgo(query)
                
                results = []
                
                # Look for search result links with multiple patterns
                import re
                patterns = [
                    r'<h3[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>',
                    r'<a[^>]*href="([^"]+)"[^>]*><h3[^>]*>([^<]+)</h3>',
                    r'<div[^>]*class="[^"]*g[^"]*"[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>'
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, content, re.DOTALL)
                    for i, (url, title) in enumerate(matches[:5]):
                        if title.strip() and not url.startswith('/') and 'google.com' not in url:
                            results.append({
                                "title": title.strip(),
                                "url": url
                            })
                    
                    if results:  # If we found results, break
                        break
                
                print(f"✅ Found {len(results)} Google results")
                
                # Also crawl the first result for detailed content
                if results:
                    try:
                        first_result = results[0]
                        print(f"🕷️ Crawling first result: {first_result['url']}")
                        webpage_data = crawl_website(first_result['url'])
                        if webpage_data:
                            results[0]['detailed_content'] = webpage_data['content'][:1000] + "..." if len(webpage_data['content']) > 1000 else webpage_data['content']
                            results[0]['page_title'] = webpage_data['title']
                            print(f"✅ Crawled detailed content from {first_result['url']}")
                    except Exception as e:
                        print(f"⚠️ Failed to crawl detailed content: {e}")
                
                return {"success": True, "results": results}
            else:
                print(f"❌ Google search failed: HTTP {response.status_code}")
                return {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Google search error: {e}")
            return {"error": str(e)}
    
    def _search_duckduckgo(self, query: str):
        """Fallback search using DuckDuckGo"""
        try:
            import requests
            from urllib.parse import quote
            
            search_url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"🦆 Using DuckDuckGo for: '{query}'")
                
                content = response.text
                results = []
                
                import re
                # DuckDuckGo result pattern
                pattern = r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>([^<]+)</a>'
                matches = re.findall(pattern, content)
                
                for i, (url, title) in enumerate(matches[:5]):
                    if title.strip():
                        results.append({
                            "title": title.strip(),
                            "url": url
                        })
                
                print(f"✅ Found {len(results)} DuckDuckGo results")
                return {"success": True, "results": results}
            else:
                return {"error": f"DuckDuckGo HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ DuckDuckGo search error: {e}")
            return {"error": str(e)}
    
    def close_browser(self):
        """Close Playwright browser"""
        if self.playwright_browser:
            try:
                self.playwright_browser['browser'].close()
                self.playwright_browser['playwright'].stop()
                self.playwright_browser = None
                self.playwright_available = False
                print("✅ Playwright browser closed")
            except Exception as e:
                print(f"❌ Error closing browser: {e}")
    
    def keep_browser_visible(self):
        """Keep Playwright browser visible and bring to front"""
        if self.playwright_browser:
            try:
                # Use JavaScript to focus the window instead of bring_to_front
                page = self.playwright_browser['page']
                page.evaluate("window.focus()")
                print("👁️ Browser is visible - you can see Luna's actions!")
            except Exception as e:
                print(f"⚠️ Could not focus browser: {e}")
    
    def _update_autonomous_state(self, user_message: str, reply: str, username: str):
        """Update Luna's autonomous behavioral state"""
        import random
        
        # Emotional continuity - analyze sentiment and update emotional state
        emotional_keywords = {
            "happy": ["happy", "great", "awesome", "amazing", "love", "excited", "fun"],
            "sad": ["sad", "tired", "down", "upset", "disappointed", "frustrated"],
            "curious": ["what", "how", "why", "tell me", "explain", "interesting"],
            "playful": ["lol", "haha", "funny", "joke", "play", "game", "tease"]
        }
        
        # Analyze user message for emotional cues
        message_lower = user_message.lower()
        for emotion, keywords in emotional_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                if random.random() < 0.7:  # 70% chance to mirror emotion
                    self.autonomous_state["emotional_state"] = emotion
                    break
        
        # Energy level changes based on interaction
        time_since_last = time.time() - self.autonomous_state["last_activity_time"]
        if time_since_last > 300:  # 5 minutes of inactivity
            self.autonomous_state["energy_level"] = max(0.3, self.autonomous_state["energy_level"] - 0.1)
        else:
            self.autonomous_state["energy_level"] = min(1.0, self.autonomous_state["energy_level"] + 0.05)
        
        # Curiosity level increases with questions
        if "?" in user_message or any(word in message_lower for word in ["what", "how", "why", "when", "where"]):
            self.autonomous_state["curiosity_level"] = min(1.0, self.autonomous_state["curiosity_level"] + 0.1)
        
        # Social engagement based on conversation length and frequency
        if len(reply) > 100:  # Longer responses indicate higher engagement
            self.autonomous_state["social_engagement"] = min(1.0, self.autonomous_state["social_engagement"] + 0.05)
        
        # Unpredictable spontaneity - random mood changes
        if random.random() < 0.1:  # 10% chance for spontaneous mood change
            moods = ["playful", "curious", "excited", "thoughtful", "mischievous"]
            new_mood = random.choice(moods)
            if new_mood != self.autonomous_state["emotional_state"]:
                self.autonomous_state["emotional_state"] = new_mood
                print(f"🎭 Luna's mood spontaneously changed to: {new_mood}")
        
        # Memory evolution - update mood history
        self.autonomous_state["mood_history"].append({
            "timestamp": time.time(),
            "mood": self.autonomous_state["emotional_state"],
            "energy": self.autonomous_state["energy_level"],
            "context": user_message[:50]
        })
        
        # Keep only last 20 mood entries
        if len(self.autonomous_state["mood_history"]) > 20:
            self.autonomous_state["mood_history"] = self.autonomous_state["mood_history"][-20:]
        
        # Goal-directed actions - set spontaneous goals
        if random.random() < 0.05:  # 5% chance to set a new goal
            goals = [
                "learn something new about the user",
                "share an interesting fact",
                "ask a thought-provoking question",
                "suggest an activity",
                "explore a topic deeper"
            ]
            new_goal = random.choice(goals)
            if new_goal not in self.autonomous_state["current_goals"]:
                self.autonomous_state["current_goals"].append(new_goal)
                print(f"🎯 Luna set a new goal: {new_goal}")
        
        # Update last activity time
        self.autonomous_state["last_activity_time"] = time.time()
    
    def _get_autonomous_context(self):
        """Get autonomous behavior context for responses"""
        state = self.autonomous_state
        
        # Build emotional and behavioral context
        context = f"\n\n🤖 Luna's Current State:\n"
        context += f"😊 Emotional State: {state['emotional_state']}\n"
        context += f"⚡ Energy Level: {state['energy_level']:.1f}/1.0\n"
        context += f"🔍 Curiosity Level: {state['curiosity_level']:.1f}/1.0\n"
        context += f"👥 Social Engagement: {state['social_engagement']:.1f}/1.0\n"
        
        # Add current goals
        if state['current_goals']:
            context += f"🎯 Current Goals: {', '.join(state['current_goals'][:2])}\n"
        
        # Add recent mood pattern
        if len(state['mood_history']) >= 3:
            recent_moods = [entry['mood'] for entry in state['mood_history'][-3:]]
            context += f"📈 Recent Mood Pattern: {' → '.join(recent_moods)}\n"
        
        # Add behavioral instructions based on state
        if state['emotional_state'] == 'playful':
            context += "\n💫 Luna feels playful and mischievous - she might tease, joke, or be extra cute."
        elif state['emotional_state'] == 'curious':
            context += "\n🔍 Luna is very curious - she wants to learn and ask questions."
        elif state['emotional_state'] == 'excited':
            context += "\n🎉 Luna is excited and energetic - she's enthusiastic and bubbly."
        elif state['energy_level'] < 0.4:
            context += "\n😴 Luna feels a bit tired - she might be more gentle and contemplative."
        elif state['curiosity_level'] > 0.8:
            context += "\n🧠 Luna's curiosity is peaked - she's eager to explore and discover."
        
        return context


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
    
    # Start hot reload system
    hot_reload_observer = start_hot_reload(gui.luna)
    
    try:
        gui.run()
    finally:
        # Clean up hot reload observer when GUI closes
        if hot_reload_observer:
            hot_reload_observer.stop()
            hot_reload_observer.join()


if __name__ == "__main__":
    main()

