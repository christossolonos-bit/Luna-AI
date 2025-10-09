# voice_engine.py - Advanced version with turn-taking system
import threading
import edge_tts
import asyncio
from playsound import playsound
import os
# subprocess import removed - no longer needed
import time
import re
import random
import hashlib
from functools import lru_cache

# 🎤 VMC Lip-sync integration (removed - not using VSeeFace)
VMC_LIPSYNC_AVAILABLE = False

# Turn-taking system to prevent Luna from interrupting herself
class TurnManager:
    """Manages turn-taking to prevent Luna from interrupting her own speech"""
    
    def __init__(self):
        self.luna_is_speaking = False
        self.speaking_lock = threading.Lock()
        self.last_speech_end = 0
        self.min_silence_duration = 0.1  # Reduced silence duration for more responsive interaction
        self.tts_start_time = 0
        self.tts_duration = 0
        self.message_counter = 0
        self.waiting_for_tts = False

# 🎯 TTS Event Architecture
class TTSEventManager:
    """Manages TTS events with queue and End flag system"""
    
    def __init__(self):
        self.tts_queue = []
        self.queue_lock = threading.Lock()
        self.current_tts_event = None
        self.tts_worker_thread = None
        self.tts_worker_running = False
        self.end_flag_received = threading.Event()
        self.processing_message = False
        
    def add_tts_message(self, text: str, mood: str = "soft", fast_mode: bool = True, context: str = ""):
        """Add a message to the TTS queue"""
        with self.queue_lock:
            message = {
                "text": text,
                "mood": mood,
                "fast_mode": fast_mode,
                "context": context,
                "timestamp": time.time(),
                "id": len(self.tts_queue) + 1
            }
            self.tts_queue.append(message)
            print(f"🎯 TTS Event: Added message #{message['id']} to queue (Queue size: {len(self.tts_queue)})")
            
            # Start worker if not running
            if not self.tts_worker_running:
                self.start_tts_worker()
    
    def start_tts_worker(self):
        """Start the TTS worker thread"""
        if self.tts_worker_running:
            return
            
        self.tts_worker_running = True
        self.tts_worker_thread = threading.Thread(target=self._tts_worker_loop, daemon=True)
        self.tts_worker_thread.start()
        print("🎯 TTS Event: Worker thread started")
    
    def _tts_worker_loop(self):
        """Main TTS worker loop that processes messages sequentially"""
        while self.tts_worker_running:
            try:
                # Get next message from queue
                message = None
                with self.queue_lock:
                    if self.tts_queue:
                        message = self.tts_queue.pop(0)
                        self.current_tts_event = message
                        self.processing_message = True
                        print(f"🎯 TTS Event: Processing message #{message['id']}")
                
                if message:
                    # Process the message
                    self._process_tts_message(message)
                    
                    # Wait for End flag before processing next message
                    print(f"🎯 TTS Event: Waiting for End flag before next message...")
                    self.end_flag_received.wait(timeout=5.0)  # 5 second timeout
                    
                    # Reset for next message
                    self.end_flag_received.clear()
                    self.processing_message = False
                    self.current_tts_event = None
                    
                else:
                    # No messages in queue, sleep briefly
                    time.sleep(0.1)
                    
            except Exception as e:
                print(f"❌ TTS Event Worker Error: {e}")
                time.sleep(0.1)
    
    def _process_tts_message(self, message: dict):
        """Process a single TTS message"""
        try:
            print(f"🎯 TTS Event: Speaking message #{message['id']}: {message['text'][:50]}...")
            
            # Use the direct speak function to avoid recursion
            speak_direct(
                text=message['text'],
                mood=message['mood'],
                fast_mode=message['fast_mode'],
                context=message['context']
            )
            
            print(f"🎯 TTS Event: Message #{message['id']} completed")
            
        except Exception as e:
            print(f"❌ TTS Event: Error processing message #{message['id']}: {e}")
    
    def signal_end_flag(self):
        """Signal that current TTS has ended (End flag received)"""
        print("🎯 TTS Event: End flag received, allowing next message")
        self.end_flag_received.set()
    
    def get_queue_status(self):
        """Get current queue status"""
        with self.queue_lock:
            return {
                "queue_size": len(self.tts_queue),
                "processing_message": self.processing_message,
                "current_message": self.current_tts_event,
                "worker_running": self.tts_worker_running
            }
    
    def clear_queue(self):
        """Clear all pending messages"""
        with self.queue_lock:
            cleared_count = len(self.tts_queue)
            self.tts_queue.clear()
            print(f"🎯 TTS Event: Cleared {cleared_count} pending messages")
    
    def stop_worker(self):
        """Stop the TTS worker thread"""
        self.tts_worker_running = False
        if self.tts_worker_thread:
            self.tts_worker_thread.join(timeout=1.0)
        print("🎯 TTS Event: Worker thread stopped")
        
    def luna_starts_speaking(self):
        """Mark that Luna has started speaking"""
        with self.speaking_lock:
            self.luna_is_speaking = True
            self.tts_start_time = time.time()
            self.message_counter += 1
            self.waiting_for_tts = True
            print(f"🎤 Luna's turn: Speaking started (Message #{self.message_counter})")
    
    def luna_stops_speaking(self):
        """Mark that Luna has stopped speaking"""
        with self.speaking_lock:
            self.luna_is_speaking = False
            self.last_speech_end = time.time()
            self.tts_duration = time.time() - self.tts_start_time
            self.waiting_for_tts = False
            print(f"🎤 Luna's turn: Speaking ended (Duration: {self.tts_duration:.1f}s)")
    
    def wait_for_tts_completion(self, timeout=30.0):
        """Wait for TTS to complete before allowing new input"""
        start_wait = time.time()
        while self.waiting_for_tts and (time.time() - start_wait) < timeout:
            time.sleep(0.1)
        return not self.waiting_for_tts
    
    def get_tts_status(self):
        """Get current TTS status"""
        with self.speaking_lock:
            if self.waiting_for_tts:
                elapsed = time.time() - self.tts_start_time
                return {
                    "waiting": True,
                    "elapsed": elapsed,
                    "message_number": self.message_counter
                }
            else:
                return {
                    "waiting": False,
                    "duration": self.tts_duration,
                    "message_number": self.message_counter
                }
    
    def can_user_speak(self) -> bool:
        """Check if user can speak (Luna is not speaking and enough silence has passed)"""
        with self.speaking_lock:
            if self.luna_is_speaking:
                return False
            
            # Check if enough silence has passed since Luna stopped speaking
            silence_duration = time.time() - self.last_speech_end
            if silence_duration < self.min_silence_duration:
                return False
            
            return True
    
    def get_turn_status(self) -> dict:
        """Get current turn status"""
        with self.speaking_lock:
            return {
                "luna_is_speaking": self.luna_is_speaking,
                "silence_duration": time.time() - self.last_speech_end,
                "can_user_speak": self.can_user_speak(),
                "message_counter": self.message_counter,
                "tts_status": self.get_tts_status()
            }

# Global turn manager instance
turn_manager = TurnManager()

# Global TTS event manager instance
tts_event_manager = TTSEventManager()

# Virtual audio support (DISABLED to avoid WSL requirements)
VIRTUAL_AUDIO_AVAILABLE = False
print("🎧 Virtual audio module DISABLED to avoid WSL requirements")



# Cache directory for pre-generated TTS segments
CACHE_DIR = "tts_cache"

def ensure_cache_dir_exists() -> None:
    try:
        if not os.path.isdir(CACHE_DIR):
            os.makedirs(CACHE_DIR, exist_ok=True)
    except Exception:
        pass

def get_tts_cache_path(segment_text: str, voice_profile: dict) -> str:
    """Compute a stable cache path for a segment + voice settings."""
    voice = voice_profile.get("voice", "")
    rate = voice_profile.get("rate", "")
    volume = voice_profile.get("volume", "")
    style = voice_profile.get("style", "")
    key = f"{voice}|{rate}|{volume}|{style}|{segment_text}".encode("utf-8", errors="ignore")
    digest = hashlib.sha1(key).hexdigest()
    return os.path.join(CACHE_DIR, f"tts_{digest}.mp3")

# 🎙️ Enhanced voice profiles with Edge TTS features (Fixed rate at +5%)
VOICE_PROFILES = {
    "soft": {
        "voice": "en-US-AvaMultilingualNeural",
        "rate": "+5%",  # Fixed rate
        "volume": "+0%",
        "pitch": "+0%",
        "style": "gentle"
    },
    "cheeky": {
        "voice": "en-US-AvaMultilingualNeural", 
        "rate": "+5%",  # Fixed rate
        "volume": "+10%",
        "pitch": "+5%",
        "style": "cheerful"
    },
    "sultry": {
        "voice": "en-US-AvaMultilingualNeural",
        "rate": "+5%",  # Fixed rate
        "volume": "+5%",
        "pitch": "-5%",
        "style": "seductive"
    },
    # Tsundere voice profiles with SSMF markup
    "tsundere_cold": {
        "voice": "en-US-AvaMultilingualNeural",
        "rate": "+5%",
        "volume": "+0%",
        "pitch": "-10%",
        "style": "cold",
        "ssmf_markup": True,
        "ssmf_style": "cold_dismissive"
    },
    "tsundere_arrogant": {
        "voice": "en-US-AvaMultilingualNeural",
        "rate": "+8%",
        "volume": "+15%",
        "pitch": "+5%",
        "style": "arrogant",
        "ssmf_markup": True,
        "ssmf_style": "superior_bratty"
    },
    "tsundere_sassy": {
        "voice": "en-US-AvaMultilingualNeural",
        "rate": "+10%",
        "volume": "+10%",
        "pitch": "+8%",
        "style": "sassy",
        "ssmf_markup": True,
        "ssmf_style": "quick_witted"
    },
    "tsundere_denial": {
        "voice": "en-US-AvaMultilingualNeural",
        "rate": "+12%",
        "volume": "+20%",
        "pitch": "+15%",
        "style": "flustered",
        "ssmf_markup": True,
        "ssmf_style": "emotional_denial"
    },
    "tsundere_caring": {
        "voice": "en-US-AvaMultilingualNeural",
        "rate": "+3%",
        "volume": "+5%",
        "pitch": "-5%",
        "style": "gentle",
        "ssmf_markup": True,
        "ssmf_style": "hidden_caring"
    },
    "excited": {
        "voice": "en-US-AvaMultilingualNeural",
        "rate": "+5%",  # Fixed rate
        "volume": "+15%",
        "pitch": "+10%",
        "style": "excited"
    },
    "sad": {
        "voice": "en-US-AvaMultilingualNeural",
        "rate": "+5%",  # Fixed rate
        "volume": "-5%",
        "pitch": "-5%",
        "style": "sad"
    },
    "angry": {
        "voice": "en-US-AvaMultilingualNeural",
        "rate": "+5%",  # Fixed rate
        "volume": "+20%",
        "pitch": "+5%",
        "style": "angry"
    },
    "whisper": {
        "voice": "en-US-AvaMultilingualNeural",
        "rate": "+5%",  # Fixed rate
        "volume": "-10%",
        "pitch": "-5%",
        "style": "whisper"
    },
    "romantic": {
        "voice": "en-US-AvaMultilingualNeural",
        "rate": "+5%",  # Fixed rate
        "volume": "+5%",
        "pitch": "-10%",
        "style": "romantic"
    },
    "playful": {
        "voice": "en-US-AvaMultilingualNeural",
        "rate": "+5%",  # Fixed rate
        "volume": "+10%",
        "pitch": "+15%",
        "style": "playful"
    },
    "serious": {
        "voice": "en-US-AvaMultilingualNeural",
        "rate": "+5%",  # Fixed rate
        "volume": "+5%",
        "pitch": "-5%",
        "style": "serious"
    },
    "nervous": {
        "voice": "en-US-AvaMultilingualNeural",
        "rate": "+5%",  # Fixed rate
        "volume": "-5%",
        "pitch": "+5%",
        "style": "nervous"
    },
    "confident": {
        "voice": "en-US-AvaMultilingualNeural",
        "rate": "+5%",  # Fixed rate
        "volume": "+10%",
        "pitch": "+5%",
        "style": "confident"
    },
    "sleepy": {
        "voice": "en-US-AvaMultilingualNeural",
        "rate": "+5%",  # Fixed rate
        "volume": "-10%",
        "pitch": "-5%",
        "style": "sleepy"
    },
    "giggly": {
        "voice": "en-US-AvaMultilingualNeural",
        "rate": "+5%",  # Fixed rate
        "volume": "+5%",
        "pitch": "+15%",
        "style": "giggly"
    },
    "protective": {
        "voice": "en-US-AvaMultilingualNeural",
        "rate": "+10%",  # Reduced for faster generation
        "volume": "+15%",
        "pitch": "+0%",
        "style": "protective"
    },
    "mysterious": {
        "voice": "en-US-AvaMultilingualNeural",
        "rate": "+0%",  # Reduced for faster generation
        "volume": "+0%",
        "pitch": "-10%",
        "style": "mysterious"
    }
}

# 🎭 Dynamic voice modulation based on word emphasis
EMPHASIS_PATTERNS = {
    "love_words": {
        "words": ["love", "adore", "cherish", "treasure", "darling", "sweetheart", "beloved", "dear"],
        "modulation": {"pitch": "+15%", "rate": "-10%", "volume": "+10%"},
        "description": "romantic emphasis"
    },
    "excitement_words": {
        "words": ["wow", "amazing", "incredible", "fantastic", "awesome", "brilliant", "perfect", "yay"],
        "modulation": {"pitch": "+20%", "rate": "+15%", "volume": "+20%"},
        "description": "excited emphasis"
    },
    "sadness_words": {
        "words": ["sad", "cry", "tears", "hurt", "pain", "sorry", "heartbroken", "lonely"],
        "modulation": {"pitch": "-15%", "rate": "-20%", "volume": "-10%"},
        "description": "sad emphasis"
    },
    "anger_words": {
        "words": ["angry", "mad", "furious", "hate", "disgust", "annoyed", "irritated"],
        "modulation": {"pitch": "+10%", "rate": "+10%", "volume": "+25%"},
        "description": "angry emphasis"
    },
    "whisper_words": {
        "words": ["secret", "whisper", "quiet", "shh", "hush", "silent", "private"],
        "modulation": {"pitch": "-10%", "rate": "-15%", "volume": "-25%"},
        "description": "whisper emphasis"
    },
    "surprise_words": {
        "words": ["what", "really", "seriously", "no way", "unbelievable", "shocked"],
        "modulation": {"pitch": "+25%", "rate": "+20%", "volume": "+15%"},
        "description": "surprised emphasis"
    },
    "question_words": {
        "words": ["why", "how", "what", "when", "where", "who", "?"],
        "modulation": {"pitch": "+10%", "rate": "+0%", "volume": "+5%"},
        "description": "question emphasis"
    },
    "emphasis_words": {
        "words": ["really", "truly", "actually", "definitely", "absolutely", "certainly"],
        "modulation": {"pitch": "+5%", "rate": "-5%", "volume": "+10%"},
        "description": "general emphasis"
    }
}

# 🎵 Musical/emotional patterns
MUSICAL_PATTERNS = {
    "laughter": {
        "triggers": ["hehe", "haha", "teehee", "giggle", "laugh", "chuckle"],
        "modulation": {"pitch": "+25%", "rate": "+20%", "volume": "+15%"}
    },
    "sighing": {
        "triggers": ["sigh", "breath", "exhale", "inhale"],
        "modulation": {"pitch": "-20%", "rate": "-25%", "volume": "-15%"}
    },
    "gasping": {
        "triggers": ["gasp", "gulp", "choke", "pant"],
        "modulation": {"pitch": "+30%", "rate": "+25%", "volume": "+20%"}
    }
}

# 🎭 Emotional expressions using text and voice modulation
EXPRESSIONS = {
    "laughter": {
        "text_patterns": [
            "hehehe", "hahaha", "teehee", "heehee", "hihihi",
            "giggle giggle", "laugh laugh", "chuckle chuckle"
        ],
        "voice_modulation": {
            "pitch": "+20%",
            "rate": "+15%",
            "volume": "+10%"
        },
        "mood_adaptations": {
            "cheeky": {"pitch": "+25%", "rate": "+20%", "volume": "+15%"},
            "playful": {"pitch": "+30%", "rate": "+25%", "volume": "+20%"},
            "romantic": {"pitch": "+15%", "rate": "+10%", "volume": "+5%"},
            "sultry": {"pitch": "+10%", "rate": "+5%", "volume": "+15%"},
            "soft": {"pitch": "+10%", "rate": "+5%", "volume": "+5%"}
        }
    },
    "shouting": {
        "text_patterns": [
            "wow!", "amazing!", "incredible!", "fantastic!", "awesome!",
            "yay!", "yes!", "finally!", "success!", "victory!"
        ],
        "voice_modulation": {
            "pitch": "+15%",
            "rate": "+10%",
            "volume": "+25%"
        },
        "mood_adaptations": {
            "excited": {"pitch": "+20%", "rate": "+15%", "volume": "+30%"},
            "angry": {"pitch": "+10%", "rate": "+5%", "volume": "+35%"},
            "surprised": {"pitch": "+25%", "rate": "+20%", "volume": "+25%"}
        }
    },
    "crying": {
        "text_patterns": [
            "sniff sniff", "sob sob", "weep weep", "cry cry",
            "tears tears", "sad sad", "heartbroken"
        ],
        "voice_modulation": {
            "pitch": "-10%",
            "rate": "-15%",
            "volume": "-5%"
        },
        "mood_adaptations": {
            "sad": {"pitch": "-15%", "rate": "-20%", "volume": "-10%"},
            "heartbroken": {"pitch": "-20%", "rate": "-25%", "volume": "-15%"},
            "emotional": {"pitch": "-5%", "rate": "-10%", "volume": "-5%"}
        }
    },
    "singing": {
        "text_patterns": [
            "la la la", "do re mi", "sing sing", "melody melody",
            "harmony harmony", "music music", "song song"
        ],
        "voice_modulation": {
            "pitch": "+5%",
            "rate": "+0%",
            "volume": "+15%"
        },
        "mood_adaptations": {
            "romantic": {"pitch": "+10%", "rate": "+5%", "volume": "+20%"},
            "playful": {"pitch": "+15%", "rate": "+10%", "volume": "+15%"},
            "sweet": {"pitch": "+5%", "rate": "+0%", "volume": "+10%"}
        }
    },
    "whisper": {
        "text_patterns": [
            "shh", "whisper", "quiet", "secret", "private",
            "hush", "silent", "murmur", "mutter"
        ],
        "voice_modulation": {
            "pitch": "-5%",
            "rate": "-10%",
            "volume": "-20%"
        },
        "mood_adaptations": {
            "mysterious": {"pitch": "-10%", "rate": "-15%", "volume": "-25%"},
            "romantic": {"pitch": "-5%", "rate": "-10%", "volume": "-15%"},
            "secretive": {"pitch": "-15%", "rate": "-20%", "volume": "-30%"}
        }
    },
    # Tsundere-specific expressions
    "tsundere_denial": {
        "text_patterns": [
            "It's not like I like you or anything!", "Whatever!", "Baka!",
            "I don't care!", "Not that I care!", "It's not like I was worried!",
            "Hmph!", "Tch!", "As if!", "Whatever you say!"
        ],
        "voice_modulation": {
            "pitch": "+20%",
            "rate": "+15%",
            "volume": "+15%"
        },
        "mood_adaptations": {
            "tsundere_cold": {"pitch": "+10%", "rate": "+5%", "volume": "+5%"},
            "tsundere_arrogant": {"pitch": "+25%", "rate": "+20%", "volume": "+20%"},
            "tsundere_sassy": {"pitch": "+30%", "rate": "+25%", "volume": "+25%"},
            "tsundere_denial": {"pitch": "+35%", "rate": "+30%", "volume": "+30%"},
            "tsundere_caring": {"pitch": "+5%", "rate": "+0%", "volume": "+5%"}
        }
    },
    "tsundere_arrogant": {
        "text_patterns": [
            "Obviously!", "Of course!", "Naturally!", "Obviously I'm right!",
            "I'm way smarter than you!", "You're so slow!", "Keep up!",
            "It's common sense!", "Anyone would know that!", "Duh!"
        ],
        "voice_modulation": {
            "pitch": "+15%",
            "rate": "+10%",
            "volume": "+20%"
        },
        "mood_adaptations": {
            "tsundere_cold": {"pitch": "+5%", "rate": "+0%", "volume": "+10%"},
            "tsundere_arrogant": {"pitch": "+20%", "rate": "+15%", "volume": "+25%"},
            "tsundere_sassy": {"pitch": "+25%", "rate": "+20%", "volume": "+30%"},
            "tsundere_denial": {"pitch": "+30%", "rate": "+25%", "volume": "+35%"},
            "tsundere_caring": {"pitch": "+0%", "rate": "+0%", "volume": "+5%"}
        }
    },
    "tsundere_caring": {
        "text_patterns": [
            "Are you okay?", "You better not get hurt!", "Don't push yourself too hard!",
            "Make sure you eat properly!", "Don't stay up too late!", "Take care of yourself!",
            "It's not like I'm worried about you!", "Just... be careful, okay?"
        ],
        "voice_modulation": {
            "pitch": "-5%",
            "rate": "-5%",
            "volume": "+5%"
        },
        "mood_adaptations": {
            "tsundere_cold": {"pitch": "-10%", "rate": "-10%", "volume": "+0%"},
            "tsundere_arrogant": {"pitch": "+0%", "rate": "+0%", "volume": "+10%"},
            "tsundere_sassy": {"pitch": "+5%", "rate": "+5%", "volume": "+15%"},
            "tsundere_denial": {"pitch": "+10%", "rate": "+10%", "volume": "+20%"},
            "tsundere_caring": {"pitch": "-10%", "rate": "-10%", "volume": "+0%"}
        }
    }
}

# 🎵 Advanced intonation patterns for natural speech
INTONATION_PATTERNS = {
    "question_rise": {
        "triggers": ["?", "what", "how", "why", "when", "where", "who", "which"],
        "modulation": {"pitch": "+15%", "rate": "-5%", "volume": "+5%"},
        "description": "question intonation rise"
    },
    "exclamation_fall": {
        "triggers": ["!", "wow", "amazing", "incredible", "fantastic", "awesome"],
        "modulation": {"pitch": "+10%", "rate": "+10%", "volume": "+15%"},
        "description": "exclamation intonation"
    },
    "statement_fall": {
        "triggers": [".", "indeed", "certainly", "definitely", "absolutely"],
        "modulation": {"pitch": "-5%", "rate": "-5%", "volume": "+0%"},
        "description": "statement intonation fall"
    },
    "emphasis_rise": {
        "triggers": ["really", "truly", "actually", "especially", "particularly"],
        "modulation": {"pitch": "+20%", "rate": "-10%", "volume": "+10%"},
        "description": "emphasis intonation"
    },
    "doubt_rise": {
        "triggers": ["maybe", "perhaps", "possibly", "might", "could"],
        "modulation": {"pitch": "+10%", "rate": "-15%", "volume": "-5%"},
        "description": "doubtful intonation"
    },
    "certainty_fall": {
        "triggers": ["definitely", "certainly", "absolutely", "surely", "obviously"],
        "modulation": {"pitch": "-10%", "rate": "+5%", "volume": "+10%"},
        "description": "certainty intonation"
    }
}

# 🎭 Emotional intonation patterns
EMOTIONAL_INTONATION = {
    "joy": {
        "triggers": ["happy", "joy", "delight", "pleasure", "excited", "thrilled"],
        "modulation": {"pitch": "+25%", "rate": "+15%", "volume": "+20%"},
        "description": "joyful intonation"
    },
    "sadness": {
        "triggers": ["sad", "sorrow", "grief", "melancholy", "depressed", "heartbroken"],
        "modulation": {"pitch": "-20%", "rate": "-25%", "volume": "-15%"},
        "description": "sad intonation"
    },
    "anger": {
        "triggers": ["angry", "furious", "enraged", "irritated", "annoyed", "mad"],
        "modulation": {"pitch": "+15%", "rate": "+20%", "volume": "+30%"},
        "description": "angry intonation"
    },
    "fear": {
        "triggers": ["afraid", "scared", "terrified", "frightened", "worried", "anxious"],
        "modulation": {"pitch": "+10%", "rate": "+25%", "volume": "-10%"},
        "description": "fearful intonation"
    },
    "surprise": {
        "triggers": ["surprised", "shocked", "astonished", "amazed", "stunned"],
        "modulation": {"pitch": "+30%", "rate": "+20%", "volume": "+25%"},
        "description": "surprised intonation"
    },
    "love": {
        "triggers": ["love", "adore", "cherish", "treasure", "beloved", "darling"],
        "modulation": {"pitch": "-10%", "rate": "-20%", "volume": "+15%"},
        "description": "loving intonation"
    }
}

# 🎭 Human throat simulation patterns
HUMAN_THROAT_PATTERNS = {
    "gasping": {
        "triggers": ["gasp", "gulp", "choke", "pant", "breath", "inhale", "exhale"],
        "modulation": {"pitch": "+40%", "rate": "+50%", "volume": "+30%"},
        "description": "human gasping sound",
        "throat_effect": "sharp_inhale"
    },
    "screaming": {
        "triggers": ["scream", "shout", "yell", "cry out", "wail", "howl"],
        "modulation": {"pitch": "+60%", "rate": "+40%", "volume": "+50%"},
        "description": "human screaming",
        "throat_effect": "vocal_strain"
    },
    "crying": {
        "triggers": ["sob", "weep", "cry", "sniff", "tears", "whimper", "moan"],
        "modulation": {"pitch": "-30%", "rate": "-40%", "volume": "-20%"},
        "description": "human crying",
        "throat_effect": "choked_voice"
    },
    "celebrating": {
        "triggers": ["yay", "woo", "cheer", "celebrate", "victory", "success", "amazing"],
        "modulation": {"pitch": "+35%", "rate": "+25%", "volume": "+40%"},
        "description": "human celebration",
        "throat_effect": "excited_breath"
    },
    "laughing": {
        "triggers": ["haha", "hehe", "lol", "giggle", "chuckle", "laugh", "teehee"],
        "modulation": {"pitch": "+45%", "rate": "+35%", "volume": "+25%"},
        "description": "human laughter",
        "throat_effect": "vibrating_voice"
    },
    "sighing": {
        "triggers": ["sigh", "breath", "exhale", "relief", "tired", "exhausted"],
        "modulation": {"pitch": "-25%", "rate": "-30%", "volume": "-15%"},
        "description": "human sighing",
        "throat_effect": "slow_exhale"
    },
    "whispering": {
        "triggers": ["whisper", "quiet", "secret", "shh", "hush", "murmur"],
        "modulation": {"pitch": "-15%", "rate": "-20%", "volume": "-40%"},
        "description": "human whispering",
        "throat_effect": "breathy_voice"
    },
    "growling": {
        "triggers": ["growl", "grunt", "angry", "furious", "rage", "hate"],
        "modulation": {"pitch": "-40%", "rate": "-25%", "volume": "+35%"},
        "description": "human growling",
        "throat_effect": "deep_resonance"
    },
    "squealing": {
        "triggers": ["squeal", "squeak", "excited", "delighted", "thrilled", "joy"],
        "modulation": {"pitch": "+50%", "rate": "+45%", "volume": "+35%"},
        "description": "human squealing",
        "throat_effect": "high_pitch_breath"
    },
    "moaning": {
        "triggers": ["moan", "groan", "pain", "hurt", "suffering", "agony"],
        "modulation": {"pitch": "-20%", "rate": "-35%", "volume": "-10%"},
        "description": "human moaning",
        "throat_effect": "strained_voice"
    },
    "giggling": {
        "triggers": ["giggle", "teehee", "heehee", "hihihi", "playful", "cute"],
        "modulation": {"pitch": "+30%", "rate": "+40%", "volume": "+20%"},
        "description": "human giggling",
        "throat_effect": "light_vibration"
    },
    "panting": {
        "triggers": ["pant", "breath", "tired", "exhausted", "winded", "heavy"],
        "modulation": {"pitch": "+20%", "rate": "+50%", "volume": "+15%"},
        "description": "human panting",
        "throat_effect": "rapid_breath"
    }
}

# 🎤 SSMF (Speech Synthesis Markup Format) processing for tsundere voices
def process_ssmf_markup(text: str, mood: str = "soft", context: str = ""):
    """Process text with SSMF markup for tsundere voice characteristics"""
    if not text or not isinstance(text, str):
        return text, mood
    
    # Determine tsundere mood based on content and context
    tsundere_mood = determine_tsundere_mood(text, mood, context)
    
    # Apply SSMF markup based on tsundere mood (returns clean text)
    clean_text = apply_tsundere_ssmf(text, tsundere_mood)
    
    return clean_text, tsundere_mood

def determine_tsundere_mood(text: str, base_mood: str, context: str = ""):
    """Determine the appropriate tsundere mood based on text content"""
    text_lower = text.lower()
    
    # Check for denial patterns
    denial_patterns = [
        "it's not like", "whatever", "baka", "i don't care", "not that i care",
        "it's not like i was worried", "hmph", "tch", "as if", "whatever you say"
    ]
    if any(pattern in text_lower for pattern in denial_patterns):
        return "tsundere_denial"
    
    # Check for arrogant patterns
    arrogant_patterns = [
        "obviously", "of course", "naturally", "i'm way smarter", "you're so slow",
        "keep up", "common sense", "anyone would know", "duh"
    ]
    if any(pattern in text_lower for pattern in arrogant_patterns):
        return "tsundere_arrogant"
    
    # Check for caring patterns (hidden caring)
    caring_patterns = [
        "are you okay", "you better not get hurt", "don't push yourself",
        "make sure you eat", "don't stay up too late", "take care of yourself",
        "it's not like i'm worried", "be careful"
    ]
    if any(pattern in text_lower for pattern in caring_patterns):
        return "tsundere_caring"
    
    # Check for sassy patterns
    sassy_patterns = [
        "really", "seriously", "come on", "give me a break", "oh please",
        "spare me", "whatever", "as if", "yeah right"
    ]
    if any(pattern in text_lower for pattern in sassy_patterns):
        return "tsundere_sassy"
    
    # Default to cold tsundere
    return "tsundere_cold"

def clean_ssmf_markup(text: str):
    """Remove all SSMF/HTML/XML markup from text to prevent TTS from reading tags aloud"""
    import re
    if not text or not isinstance(text, str):
        return text
    
    # Remove all HTML/XML tags including SSMF markup
    clean_text = re.sub(r'<[^>]+>', '', text)
    
    # Remove any remaining markup artifacts
    clean_text = re.sub(r'&[a-zA-Z]+;', '', clean_text)  # Remove HTML entities
    clean_text = re.sub(r'\s+', ' ', clean_text)  # Normalize whitespace
    clean_text = clean_text.strip()
    
    return clean_text

def apply_tsundere_ssmf(text: str, tsundere_mood: str):
    """Apply SSMF markup for tsundere voice characteristics - returns clean text for TTS"""
    # Clean any existing SSMF markup from text to prevent TTS from reading tags aloud
    # The voice profile will handle the actual voice modulation
    clean_text = clean_ssmf_markup(text)
    
    return clean_text

def get_tsundere_voice_profile(tsundere_mood: str):
    """Get voice profile for specific tsundere mood"""
    tsundere_profiles = {
        "tsundere_cold": {
            "voice": "en-US-AvaMultilingualNeural",
            "rate": "+5%",
            "volume": "+0%",
            "pitch": "-10%",
            "style": "cold",
            "ssmf_markup": True,
            "ssmf_style": "cold_dismissive"
        },
        "tsundere_arrogant": {
            "voice": "en-US-AvaMultilingualNeural",
            "rate": "+8%",
            "volume": "+15%",
            "pitch": "+5%",
            "style": "arrogant",
            "ssmf_markup": True,
            "ssmf_style": "superior_bratty"
        },
        "tsundere_sassy": {
            "voice": "en-US-AvaMultilingualNeural",
            "rate": "+10%",
            "volume": "+10%",
            "pitch": "+8%",
            "style": "sassy",
            "ssmf_markup": True,
            "ssmf_style": "quick_witted"
        },
        "tsundere_denial": {
            "voice": "en-US-AvaMultilingualNeural",
            "rate": "+12%",
            "volume": "+20%",
            "pitch": "+15%",
            "style": "flustered",
            "ssmf_markup": True,
            "ssmf_style": "emotional_denial"
        },
        "tsundere_caring": {
            "voice": "en-US-AvaMultilingualNeural",
            "rate": "+3%",
            "volume": "+5%",
            "pitch": "-5%",
            "style": "gentle",
            "ssmf_markup": True,
            "ssmf_style": "hidden_caring"
        }
    }
    
    return tsundere_profiles.get(tsundere_mood, tsundere_profiles["tsundere_cold"])

# 🎤 Throat effect simulation
THROAT_EFFECTS = {
    "sharp_inhale": {
        "description": "Sharp intake of breath",
        "text_addition": " *sharp inhale* ",
        "modulation_boost": {"pitch": "+10%", "rate": "+15%", "volume": "+5%"}
    },
    "vocal_strain": {
        "description": "Strained vocal cords",
        "text_addition": " *strained voice* ",
        "modulation_boost": {"pitch": "+5%", "rate": "+10%", "volume": "+20%"}
    },
    "choked_voice": {
        "description": "Choked up voice",
        "text_addition": " *choked up* ",
        "modulation_boost": {"pitch": "-15%", "rate": "-20%", "volume": "-10%"}
    },
    "excited_breath": {
        "description": "Excited breathing",
        "text_addition": " *excited breath* ",
        "modulation_boost": {"pitch": "+15%", "rate": "+20%", "volume": "+15%"}
    },
    "vibrating_voice": {
        "description": "Vibrating vocal cords",
        "text_addition": " *vibrating* ",
        "modulation_boost": {"pitch": "+20%", "rate": "+25%", "volume": "+10%"}
    },
    "slow_exhale": {
        "description": "Slow exhale",
        "text_addition": " *slow exhale* ",
        "modulation_boost": {"pitch": "-10%", "rate": "-25%", "volume": "-5%"}
    },
    "breathy_voice": {
        "description": "Breathy whisper",
        "text_addition": " *breathy* ",
        "modulation_boost": {"pitch": "-5%", "rate": "-15%", "volume": "-25%"}
    },
    "deep_resonance": {
        "description": "Deep throat resonance",
        "text_addition": " *deep resonance* ",
        "modulation_boost": {"pitch": "-20%", "rate": "-10%", "volume": "+25%"}
    },
    "high_pitch_breath": {
        "description": "High-pitched breath",
        "text_addition": " *high breath* ",
        "modulation_boost": {"pitch": "+25%", "rate": "+30%", "volume": "+20%"}
    },
    "strained_voice": {
        "description": "Strained vocal cords",
        "text_addition": " *strained* ",
        "modulation_boost": {"pitch": "-15%", "rate": "-20%", "volume": "+5%"}
    },
    "light_vibration": {
        "description": "Light vocal vibration",
        "text_addition": " *light vibration* ",
        "modulation_boost": {"pitch": "+15%", "rate": "+20%", "volume": "+8%"}
    },
    "rapid_breath": {
        "description": "Rapid breathing",
        "text_addition": " *rapid breath* ",
        "modulation_boost": {"pitch": "+10%", "rate": "+40%", "volume": "+10%"}
    }
}

@lru_cache(maxsize=4096)
def analyze_sentence_structure(text: str):
    """Analyze sentence structure for intonation patterns"""
    sentences = text.split('.')
    intonation_marks = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # Check for question marks
        if '?' in sentence:
            intonation_marks.append({
                "type": "question_rise",
                "sentence": sentence,
                "strength": 1.5
            })
        
        # Check for exclamation marks
        elif '!' in sentence:
            intonation_marks.append({
                "type": "exclamation_fall",
                "sentence": sentence,
                "strength": 1.3
            })
        
        # Check for statements
        else:
            intonation_marks.append({
                "type": "statement_fall",
                "sentence": sentence,
                "strength": 1.0
            })
    
    return intonation_marks

def detect_word_level_intonation(text: str, context: str = ""):
    """Detect word-level intonation patterns"""
    text_lower = text.lower()
    context_lower = context.lower() if context else ""
    detected_intonations = []
    
    # Check for intonation patterns
    for pattern_name, pattern_data in INTONATION_PATTERNS.items():
        for trigger in pattern_data["triggers"]:
            if trigger in text_lower:
                # Calculate strength based on context
                strength = 1.0
                if trigger in context_lower:
                    strength = 1.5  # Boost if found in context
                
                detected_intonations.append({
                    "type": pattern_name,
                    "word": trigger,
                    "modulation": pattern_data["modulation"],
                    "description": pattern_data["description"],
                    "strength": strength
                })
                break
    
    # Check for emotional intonation
    for emotion_name, emotion_data in EMOTIONAL_INTONATION.items():
        for trigger in emotion_data["triggers"]:
            if trigger in text_lower or trigger in context_lower:
                strength = 1.0
                if trigger in context_lower:
                    strength = 1.8  # Higher boost for emotional context
                
                detected_intonations.append({
                    "type": emotion_name,
                    "word": trigger,
                    "modulation": emotion_data["modulation"],
                    "description": emotion_data["description"],
                    "strength": strength
                })
                break
    
    return detected_intonations

def detect_emphasis_words(text: str, mood: str = "soft", context: str = ""):
    """Detect words that need emphasis based on context, mood, and meaning"""
    text_lower = text.lower()
    detected_modulations = []
    
    # Context-aware emphasis detection
    context_lower = context.lower() if context else ""
    full_context = f"{text_lower} {context_lower}".lower()
    
    # Check for emphasis patterns with context awareness
    for pattern_name, pattern_data in EMPHASIS_PATTERNS.items():
        for word in pattern_data["words"]:
            # Check if word appears in text or context
            if word in text_lower or word in context_lower:
                # Add context-based scoring
                emphasis_score = 1
                
                # Boost score if word appears in both text and context
                if word in text_lower and word in context_lower:
                    emphasis_score += 2
                
                # Boost score based on mood compatibility
                mood_boost = {
                    "love_words": ["romantic", "sultry", "soft"],
                    "excitement_words": ["excited", "playful", "giggly"],
                    "sadness_words": ["sad", "nervous", "sleepy"],
                    "anger_words": ["angry", "serious"],
                    "whisper_words": ["mysterious", "whisper", "nervous"],
                    "surprise_words": ["excited", "playful", "giggly"],
                    "question_words": ["nervous", "curious", "mysterious"],
                    "emphasis_words": ["confident", "serious", "protective"]
                }
                
                if pattern_name in mood_boost and mood in mood_boost[pattern_name]:
                    emphasis_score += 1
                
                detected_modulations.append({
                    "type": pattern_name,
                    "word": word,
                    "modulation": pattern_data["modulation"],
                    "description": pattern_data["description"],
                    "score": emphasis_score,
                    "context_found": word in context_lower
                })
                break  # Only use first match per pattern
    
    # Check for musical patterns with context
    for pattern_name, pattern_data in MUSICAL_PATTERNS.items():
        for trigger in pattern_data["triggers"]:
            if trigger in text_lower or trigger in context_lower:
                emphasis_score = 1
                if trigger in text_lower and trigger in context_lower:
                    emphasis_score += 2
                
                detected_modulations.append({
                    "type": pattern_name,
                    "word": trigger,
                    "modulation": pattern_data["modulation"],
                    "description": f"{pattern_name} emphasis",
                    "score": emphasis_score,
                    "context_found": trigger in context_lower
                })
                break
    
    # Sort by emphasis score (highest first)
    detected_modulations.sort(key=lambda x: x["score"], reverse=True)
    
    return detected_modulations

def calculate_dynamic_modulation(text: str, base_mood: str = "soft"):
    """Calculate dynamic voice modulation based on text content"""
    emphasis_modulations = detect_emphasis_words(text)
    
    if not emphasis_modulations:
        return None, text
    
    # Use the first detected emphasis for overall modulation
    primary_emphasis = emphasis_modulations[0]
    return primary_emphasis["modulation"], text

def get_mood_adjustments(mood: str, conversation_context: dict = None):
    """Get dynamic mood-specific voice adjustments"""
    # Import the dynamic mood system from voice_modulation
    try:
        from voice_modulation import get_mood_adjustments as get_dynamic_mood_adjustments
        return get_dynamic_mood_adjustments(mood, conversation_context)
    except ImportError:
        # Fallback to basic adjustments if import fails
        mood_adjustments = {
            "romantic": {"pitch": "-5%", "rate": "-10%", "volume": "+5%"},
            "excited": {"pitch": "+10%", "rate": "+15%", "volume": "+10%"},
            "sad": {"pitch": "-10%", "rate": "-15%", "volume": "-5%"},
            "angry": {"pitch": "+5%", "rate": "+10%", "volume": "+15%"},
            "playful": {"pitch": "+15%", "rate": "+20%", "volume": "+10%"},
            "mysterious": {"pitch": "-10%", "rate": "-5%", "volume": "-10%"},
            "whisper": {"pitch": "-15%", "rate": "-20%", "volume": "-25%"}
        }
        return mood_adjustments.get(mood, {"pitch": "+0%", "rate": "+0%", "volume": "+0%"})

def add_emphasis_markers(text: str):
    """Add emphasis markers to important words"""
    # This is a placeholder - actual implementation would add SSML tags
    return text

def create_dynamic_voice_profile(base_profile: dict, text: str, mood: str = "soft", context: str = ""):
    """Create dynamic voice profile with context-aware emphasis-based modulation"""
    emphasis_modulations = detect_emphasis_words(text, mood, context)
    
    if not emphasis_modulations:
        # No emphasis detected, return base profile
        return base_profile.copy(), text
    
    # Use the highest-scored emphasis for overall modulation
    primary_emphasis = emphasis_modulations[0]
    modulation = primary_emphasis["modulation"]
    
    # Create enhanced profile
    enhanced_profile = base_profile.copy()
    
    # Apply modulation adjustments with context awareness
    try:
        # Adjust rate
        base_rate = enhanced_profile["rate"]
        rate_value = int(base_rate.replace("%", ""))
        mod_rate_value = int(modulation["rate"].replace("%", ""))
        
        # Apply context-based multiplier
        context_multiplier = 1.0
        if primary_emphasis.get("context_found", False):
            context_multiplier = 1.5  # Boost effect if found in context
        
        new_rate = rate_value + (mod_rate_value * context_multiplier)
        new_rate = max(-100, min(50, new_rate))  # Keep within bounds (50% speed limit)
        enhanced_profile["rate"] = f"{int(new_rate):+d}%"
        
        # Adjust volume
        base_volume = enhanced_profile["volume"]
        volume_value = int(base_volume.replace("%", ""))
        mod_volume_value = int(modulation["volume"].replace("%", ""))
        new_volume = volume_value + (mod_volume_value * context_multiplier)
        new_volume = max(-100, min(100, new_volume))  # Keep within bounds
        enhanced_profile["volume"] = f"{int(new_volume):+d}%"
        
        context_info = " (context-enhanced)" if primary_emphasis.get("context_found", False) else ""
        print(f"🎤 Applied {primary_emphasis['description']} for '{primary_emphasis['word']}'{context_info}")
        
    except Exception as e:
        print(f"❌ Error applying modulation: {e}")
        # Fallback to base profile
        enhanced_profile = base_profile.copy()
    
    return enhanced_profile, text

def process_text_with_emphasis(text: str, mood: str = "soft", context: str = ""):
    """Process text with context-aware emphasis markers"""
    # Add emphasis markers to important words based on context
    enhanced_text = add_emphasis_markers(text)
    
    # Add context-based emphasis
    if context:
        # Find words in text that also appear in context for extra emphasis
        context_words = context.lower().split()
        text_words = text.lower().split()
        
        # Add emphasis to words that appear in both text and context
        for word in text_words:
            if word in context_words and len(word) > 3:  # Only emphasize meaningful words
                enhanced_text = enhanced_text.replace(word, f"**{word}**", 1)
    
    return enhanced_text

def get_expression_for_mood(mood: str, text: str):
    """Determine if we should add an expression based on mood and text"""
    
    # Laughter triggers
    laughter_triggers = [
        "haha", "hehe", "lol", "funny", "laugh", "giggle", "hilarious",
        "*giggles*", "*laughs*", "*chuckles*", "*giggles playfully*",
        "*excited giggle*", "*soft giggle*", "*romantic giggle*", "*sultry giggle*",
        "*giggles softly*", "*giggles sweetly*", "*giggles seductively*"
    ]
    
    # Check for laughter triggers
    text_lower = text.lower()
    for trigger in laughter_triggers:
        if trigger in text_lower:
            return "laughter"
    
    # Check for other expressions based on mood and content
    if mood == "excited" and any(word in text_lower for word in ["wow", "amazing", "incredible"]):
        return "shouting"
    elif mood == "sad" and any(word in text_lower for word in ["cry", "tears", "sad"]):
        return "crying"
    elif mood == "romantic" and any(word in text_lower for word in ["sing", "melody", "song"]):
        return "singing"
    elif mood == "mysterious" and any(word in text_lower for word in ["secret", "whisper", "quiet"]):
        return "whisper"
    
    return None

def add_expression_to_text(text: str, expression_type: str, mood: str = "soft"):
    """Add expression text to the response"""
    if expression_type not in EXPRESSIONS:
        return text
    
    expression_data = EXPRESSIONS[expression_type]
    patterns = expression_data["text_patterns"]
    
    # Add a random expression pattern
    expression = random.choice(patterns)
    return f"{text} {expression}"

def get_expression_voice_modulation(expression_type: str, mood: str = "soft"):
    """Get voice modulation for expressions"""
    if expression_type not in EXPRESSIONS:
        return {}
    
    expression_data = EXPRESSIONS[expression_type]
    base_modulation = expression_data["voice_modulation"]
    
    # Apply mood-specific adaptations
    mood_adaptations = expression_data.get("mood_adaptations", {})
    if mood in mood_adaptations:
        # Merge base modulation with mood adaptation
        adapted_modulation = base_modulation.copy()
        for key, value in mood_adaptations[mood].items():
            if key in adapted_modulation:
                # Combine the values (simplified)
                adapted_modulation[key] = value
        return adapted_modulation
    
    return base_modulation

@lru_cache(maxsize=4096)
def process_text_with_expressions(text: str, mood: str):
    """Process text and add expressions based on mood and content"""
    # Remove hashtags first - they shouldn't be read aloud
    import re
    text = re.sub(r'#\w+', '', text)  # Remove #hashtag patterns
    text = re.sub(r'#\s*\w+', '', text)  # Remove # hashtag patterns with spaces
    
    # Check for expressions
    expression_type = get_expression_for_mood(mood, text)
    
    if expression_type:
        # Add expression text
        text = add_expression_to_text(text, expression_type, mood)
        print(f"🎭 Added {expression_type} expression")
    
    return text

def create_expression_voice_profile(base_profile: dict, expression_modulation: dict):
    """Create voice profile with expression modulation"""
    if not expression_modulation:
        return base_profile
    
    enhanced_profile = base_profile.copy()
    
    # Apply expression modulation
    for key, value in expression_modulation.items():
        if key in enhanced_profile:
            # Simple addition for now
            try:
                current_value = enhanced_profile[key]
                if isinstance(current_value, str) and "%" in current_value:
                    current_num = int(current_value.replace("%", ""))
                    mod_num = int(value.replace("%", ""))
                    new_value = current_num + mod_num
                    new_value = max(-100, min(100, new_value))  # Keep within bounds
                    enhanced_profile[key] = f"{new_value:+d}%"
            except Exception as e:
                print(f"❌ Error applying expression modulation: {e}")
    
    return enhanced_profile

@lru_cache(maxsize=4096)
def process_text_for_tts(text: str, mood: str):
    """Process text to make giggles and winks more audible in TTS"""
    
    # Remove all asterisk patterns that would be read literally
    import re
    
    # Remove all *pattern* expressions
    text = re.sub(r'\*[^*]*\*', '', text)
    
    # Remove hashtags - they shouldn't be read aloud
    text = re.sub(r'#\w+', '', text)  # Remove #hashtag patterns
    text = re.sub(r'#\s*\w+', '', text)  # Remove # hashtag patterns with spaces
    
    # Remove emojis and emoji-like characters
    # This regex pattern matches most emoji characters
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"  # dingbats
        u"\U000024C2-\U0001F251" 
        "]+", flags=re.UNICODE)
    text = emoji_pattern.sub('', text)
    
    # Also remove common emoji text representations
    text = re.sub(r':[a-zA-Z_]+:', '', text)  # :smile:, :heart:, etc.
    
    # Clean up extra spaces
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return text

def add_natural_pauses(text: str):
    """Add natural pauses to make speech more human-like"""
    import re
    
    # For now, just return the text as-is since SSML tags are being read literally
    # The natural pauses will be handled through voice modulation and rate changes instead
    return text

def create_enhanced_voice_profile(base_profile: dict, text: str, mood: str = "soft", context: str = ""):
    """Create voice profile with advanced intonation and emphasis"""
    # Get sentence structure analysis
    sentence_intonations = analyze_sentence_structure(text)
    
    # Get word-level intonation
    word_intonations = detect_word_level_intonation(text, context)
    
    # Get emphasis patterns (existing)
    emphasis_modulations = detect_emphasis_words(text, mood, context)
    
    # Combine all modulation patterns
    all_modulations = []
    
    # Add sentence-level intonations
    for intonation in sentence_intonations:
        pattern_type = intonation["type"]
        if pattern_type in INTONATION_PATTERNS:
            modulation = INTONATION_PATTERNS[pattern_type]["modulation"].copy()
            modulation["strength"] = intonation["strength"]
            all_modulations.append({
                "type": "sentence_intonation",
                "description": f"sentence {pattern_type}",
                "modulation": modulation,
                "strength": intonation["strength"]
            })
    
    # Add word-level intonations
    for intonation in word_intonations:
        all_modulations.append({
            "type": "word_intonation",
            "description": intonation["description"],
            "modulation": intonation["modulation"],
            "strength": intonation["strength"]
        })
    
    # Add emphasis patterns
    for emphasis in emphasis_modulations:
        all_modulations.append({
            "type": "emphasis",
            "description": emphasis["description"],
            "modulation": emphasis["modulation"],
            "strength": emphasis.get("score", 1.0)
        })
    
    # Sort by strength (highest first)
    all_modulations.sort(key=lambda x: x["strength"], reverse=True)
    
    # Create enhanced profile
    enhanced_profile = base_profile.copy()
    
    if all_modulations:
        # Use the strongest modulation pattern
        primary_modulation = all_modulations[0]
        modulation = primary_modulation["modulation"]
        strength = primary_modulation["strength"]
        
        # Apply modulation with strength multiplier
        try:
            # Adjust rate
            base_rate = enhanced_profile["rate"]
            rate_value = int(base_rate.replace("%", ""))
            mod_rate_value = int(modulation["rate"].replace("%", ""))
            
            # Apply strength multiplier
            new_rate = rate_value + (mod_rate_value * strength)
            new_rate = max(-100, min(50, new_rate))
            enhanced_profile["rate"] = f"{int(new_rate):+d}%"
            
            # Adjust volume
            base_volume = enhanced_profile["volume"]
            volume_value = int(base_volume.replace("%", ""))
            mod_volume_value = int(modulation["volume"].replace("%", ""))
            new_volume = volume_value + (mod_volume_value * strength)
            new_volume = max(-100, min(100, new_volume))
            enhanced_profile["volume"] = f"{int(new_volume):+d}%"
            
            print(f"🎤 Applied {primary_modulation['description']} (strength: {strength:.1f})")
            
        except Exception as e:
            print(f"❌ Error applying intonation: {e}")
            enhanced_profile = base_profile.copy()
    
    return enhanced_profile, text

@lru_cache(maxsize=4096)
def process_text_with_intonation(text: str, mood: str = "soft", context: str = ""):
    """Process text with intonation markers"""
    # Add natural pauses and emphasis based on sentence structure
    sentences = text.split('.')
    enhanced_sentences = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        # Add emphasis to key words based on context
        if context:
            context_words = context.lower().split()
            sentence_words = sentence.lower().split()
            
            for word in sentence_words:
                if word in context_words and len(word) > 3:
                    # Add emphasis marker
                    sentence = sentence.replace(word, f"**{word}**", 1)
        
        enhanced_sentences.append(sentence)
    
    return '. '.join(enhanced_sentences)

def detect_human_throat_sounds(text: str, context: str = ""):
    """Detect human throat sounds and vocal expressions"""
    text_lower = text.lower()
    context_lower = context.lower() if context else ""
    detected_throat_sounds = []
    
    # Check for throat patterns
    for pattern_name, pattern_data in HUMAN_THROAT_PATTERNS.items():
        for trigger in pattern_data["triggers"]:
            if trigger in text_lower or trigger in context_lower:
                # Calculate strength based on context
                strength = 1.0
                if trigger in context_lower:
                    strength = 1.8  # Higher boost for throat sounds in context
                
                detected_throat_sounds.append({
                    "type": pattern_name,
                    "word": trigger,
                    "modulation": pattern_data["modulation"],
                    "description": pattern_data["description"],
                    "throat_effect": pattern_data["throat_effect"],
                    "strength": strength
                })
                break
    
    return detected_throat_sounds

def apply_throat_effects(text: str, throat_sounds: list):
    """Apply throat effect text additions"""
    enhanced_text = text
    
    for throat_sound in throat_sounds:
        throat_effect = throat_sound["throat_effect"]
        if throat_effect in THROAT_EFFECTS:
            effect_data = THROAT_EFFECTS[throat_effect]
            enhanced_text += effect_data["text_addition"]
    
    return enhanced_text

def create_human_voice_profile(base_profile: dict, text: str, mood: str = "soft", context: str = ""):
    """Create voice profile with human throat simulation"""
    # Get throat sounds
    throat_sounds = detect_human_throat_sounds(text, context)
    
    # Get existing intonation and emphasis
    sentence_intonations = analyze_sentence_structure(text)
    word_intonations = detect_word_level_intonation(text, context)
    emphasis_modulations = detect_emphasis_words(text, mood, context)
    
    # Get dynamic mood adjustments based on conversation context
    conversation_context = {
        "depth": len(text.split()) // 10,  # Simple depth estimation
        "context": context,
        "mood": mood
    }
    mood_adjustments = get_mood_adjustments(mood, conversation_context)
    
    # Combine all modulation patterns
    all_modulations = []
    
    # Add throat sounds (highest priority)
    for throat_sound in throat_sounds:
        modulation = throat_sound["modulation"].copy()
        throat_effect = throat_sound["throat_effect"]
        
        # Apply throat effect boost
        if throat_effect in THROAT_EFFECTS:
            effect_boost = THROAT_EFFECTS[throat_effect]["modulation_boost"]
            for key, value in effect_boost.items():
                if key in modulation:
                    # Combine throat effect with base modulation
                    current_value = int(modulation[key].replace("%", ""))
                    boost_value = int(value.replace("%", ""))
                    new_value = current_value + boost_value
                    new_value = max(-100, min(100, new_value))
                    modulation[key] = f"{new_value:+d}%"
        
        modulation["strength"] = throat_sound["strength"]
        all_modulations.append({
            "type": "throat_sound",
            "description": throat_sound["description"],
            "modulation": modulation,
            "strength": throat_sound["strength"] * 1.5  # Throat sounds get priority
        })
    
    # Add sentence-level intonations
    for intonation in sentence_intonations:
        pattern_type = intonation["type"]
        if pattern_type in INTONATION_PATTERNS:
            modulation = INTONATION_PATTERNS[pattern_type]["modulation"].copy()
            modulation["strength"] = intonation["strength"]
            all_modulations.append({
                "type": "sentence_intonation",
                "description": f"sentence {pattern_type}",
                "modulation": modulation,
                "strength": intonation["strength"]
            })
    
    # Add word-level intonations
    for intonation in word_intonations:
        all_modulations.append({
            "type": "word_intonation",
            "description": intonation["description"],
            "modulation": intonation["modulation"],
            "strength": intonation["strength"]
        })
    
    # Add emphasis patterns
    for emphasis in emphasis_modulations:
        all_modulations.append({
            "type": "emphasis",
            "description": emphasis["description"],
            "modulation": emphasis["modulation"],
            "strength": emphasis.get("score", 1.0)
        })
    
    # Sort by strength (highest first)
    all_modulations.sort(key=lambda x: x["strength"], reverse=True)
    
    # Create enhanced profile
    enhanced_profile = base_profile.copy()
    
    if all_modulations:
        # Use the strongest modulation pattern
        primary_modulation = all_modulations[0]
        modulation = primary_modulation["modulation"]
        strength = primary_modulation["strength"]
        
        # Apply modulation with strength multiplier
        try:
            # Adjust rate
            base_rate = enhanced_profile["rate"]
            rate_value = int(base_rate.replace("%", ""))
            mod_rate_value = int(modulation["rate"].replace("%", ""))
            
            # Apply strength multiplier
            new_rate = rate_value + (mod_rate_value * strength)
            new_rate = max(-100, min(50, new_rate))
            enhanced_profile["rate"] = f"{int(new_rate):+d}%"
            
            # Adjust volume
            base_volume = enhanced_profile["volume"]
            volume_value = int(base_volume.replace("%", ""))
            mod_volume_value = int(modulation["volume"].replace("%", ""))
            new_volume = volume_value + (mod_volume_value * strength)
            new_volume = max(-100, min(100, new_volume))
            enhanced_profile["volume"] = f"{int(new_volume):+d}%"
            
            print(f"🎤 Applied {primary_modulation['description']} (strength: {strength:.1f})")
            
        except Exception as e:
            print(f"❌ Error applying throat modulation: {e}")
            enhanced_profile = base_profile.copy()
    
    # Apply dynamic mood adjustments
    try:
        for param, value in mood_adjustments.items():
            if param in enhanced_profile:
                # Combine existing modulation with mood adjustments
                current_val = int(enhanced_profile[param].replace("%", ""))
                mood_val = int(value.replace("%", ""))
                combined = current_val + mood_val
                
                # Apply bounds based on parameter
                if param == "rate":
                    combined = max(-100, min(50, combined))  # Rate limit
                elif param == "volume":
                    combined = max(-100, min(100, combined))  # Volume limit
                
                enhanced_profile[param] = f"{combined:+d}%"
            else:
                enhanced_profile[param] = value
        
        print(f"🎤 Applied dynamic mood adjustments: {mood_adjustments}")
        
    except Exception as e:
        print(f"❌ Error applying mood adjustments: {e}")
    
    return enhanced_profile, text, throat_sounds

# 🗣️ Enhanced TTS function with all features
async def speak_text(text: str, mood: str = "soft", fast_mode: bool = True, context: str = ""):
    print(f"🎤 Starting TTS generation for: {text[:50]}...")
    
    # Use Edge TTS for speech generation
    try:
        # Generate speech with Edge TTS
        output_path = f"tts_cache/edge_tts_{int(time.time())}.mp3"
        
        # Ensure cache directory exists
        os.makedirs("tts_cache", exist_ok=True)
        
        # Use Edge TTS to generate speech
        voice = "en-US-AriaNeural"  # Default voice
        if mood == "excited":
            voice = "en-US-JennyNeural"
        elif mood == "sad":
            voice = "en-US-AriaNeural"
        elif mood == "angry":
            voice = "en-US-GuyNeural"
        
        # Generate TTS
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)
        
        # Play the generated audio
        if os.path.exists(output_path):
            playsound(output_path)
            print("✅ Edge TTS playback completed")
            
            # Clean up the file after a delay
            def cleanup_file():
                time.sleep(2)  # Wait 2 seconds before cleanup
                try:
                    if os.path.exists(output_path):
                        os.remove(output_path)
                        print(f"🗑️ Cleaned up: {output_path}")
                except Exception as e:
                    print(f"❌ Cleanup error: {e}")
            
            # Start cleanup in background
            cleanup_thread = threading.Thread(target=cleanup_file)
            cleanup_thread.daemon = True
            cleanup_thread.start()
            return
        else:
            print("❌ Edge TTS file not generated")
            
    except Exception as e:
        print(f"⚠️ Edge TTS error: {e}, falling back to default TTS")
    
    # Fallback to default TTS system
    # Get base voice profile
    voice_profile = VOICE_PROFILES.get(mood, VOICE_PROFILES["soft"])
    print(f"🎤 Using voice profile: {mood}")
    
    # Process text with expressions
    try:
        enhanced_text = process_text_with_expressions(text, mood)
        print(f"🎭 Text processed with expressions")
    except Exception as e:
        print(f"❌ Error processing expressions: {e}")
        enhanced_text = text
    
    # Process text with SSMF markup for tsundere voices
    try:
        ssmf_text, tsundere_mood = process_ssmf_markup(enhanced_text, mood, context)
        if tsundere_mood.startswith("tsundere_"):
            print(f"🎭 SSMF processing: {tsundere_mood} mood detected")
            enhanced_text = ssmf_text
            # Use tsundere voice profile
            voice_profile = get_tsundere_voice_profile(tsundere_mood)
        else:
            print(f"🎭 SSMF processing: Standard mood ({mood})")
    except Exception as e:
        print(f"❌ Error processing SSMF markup: {e}")
        # Fallback to original voice profile
        voice_profile = VOICE_PROFILES.get(mood, VOICE_PROFILES["soft"])
    
    # Create dynamic voice profile with context-aware emphasis-based modulation
    try:
        dynamic_profile, enhanced_text, throat_sounds = create_human_voice_profile(voice_profile, enhanced_text, mood, context)
        print(f"🎤 Dynamic profile created: {dynamic_profile['voice']} at {dynamic_profile['rate']}")
    except Exception as e:
        print(f"❌ Error creating dynamic profile: {e}")
        # Fallback to basic profile
        dynamic_profile = voice_profile.copy()
        enhanced_text = text
    
    # Process text with throat effects, intonation and better TTS handling
    try:
        # First apply throat effects
        throat_text = apply_throat_effects(enhanced_text, throat_sounds)
        # Then apply intonation processing
        intonation_text = process_text_with_intonation(throat_text, mood, context)
        # Finally apply TTS processing
        processed_text = process_text_for_tts(intonation_text, mood)
        
        # Clean any SSMF markup that might have gotten through
        processed_text = clean_ssmf_markup(processed_text)
        
        print(f"🎤 Processed text with throat effects: {processed_text[:50]}...")
    except Exception as e:
        print(f"❌ Error processing text: {e}")
        processed_text = text.replace("*", "").replace("_", "").strip()
        # Clean markup from fallback text too
        processed_text = clean_ssmf_markup(processed_text)
    
    # Optimize rate for fast mode
    if fast_mode:
        try:
            current_rate = dynamic_profile["rate"]
            rate_value = int(current_rate.replace("%", ""))
            # Boost speed by 20% for faster response
            dynamic_profile["rate"] = f"{rate_value + 20}%"
        except Exception as e:
            print(f"❌ Error optimizing rate: {e}")
            dynamic_profile["rate"] = "+15%"
    
    # Validate rate and volume
    try:
        rate = dynamic_profile["rate"]
        volume = dynamic_profile["volume"]
        
        # Ensure rate is within valid bounds (-100% to +50% for speed limit)
        rate_value = int(rate.replace("%", ""))
        rate_value = max(-100, min(50, rate_value))
        rate = f"{rate_value:+d}%"
        
        # Ensure volume is within valid bounds (-100% to +100%)
        volume_value = int(volume.replace("%", ""))
        volume_value = max(-100, min(100, volume_value))
        volume = f"{volume_value:+d}%"
        
    except Exception as e:
        print(f"❌ Error validating settings: {e}")
        rate = "+15%"
        volume = "+0%"
    
    print(f"🎤 Final TTS settings: voice={dynamic_profile['voice']}, rate={rate}, volume={volume}")
    
    # Create communicate object
    try:
        communicate = edge_tts.Communicate(
            processed_text, 
            dynamic_profile["voice"],
            rate=rate,
            volume=volume
        )
        print(f"🎤 Communicate object created successfully")
    except Exception as e:
        print(f"❌ Error creating communicate object: {e}")
        return
    
    print(f"🎤 Speaking with {mood} mood: {dynamic_profile['voice']} at {dynamic_profile['rate']} speed")
    
    # Generate unique filename to avoid conflicts
    import uuid
    filename = f"luna_voice_{uuid.uuid4().hex[:8]}.mp3"
    print(f"🎤 Generated filename: {filename}")
    
    try:
        # Save audio file
        print(f"🎤 Starting audio file generation...")
        await communicate.save(filename)
        print(f"🎤 Audio file saved successfully: {filename}")
        
        # Play audio using subprocess for better control
        global current_audio_process
        try:
            # Mark that Luna is starting to speak
            turn_manager.luna_starts_speaking()
            
            # Stop any existing audio first
            stop_current_audio()
            
            # Check if virtual audio is enabled (for virtual cable input)
            if is_virtual_audio_enabled():
                print(f"🎧 Playing to virtual cable input: {filename}")
                try:
                    # Play to virtual audio cable asynchronously
                    virtual_thread = play_tts_to_virtual_cable_async(filename)
                    if virtual_thread:
                        virtual_thread.join()  # Wait for completion
                        print("🎧 Virtual audio playback completed")
                    else:
                        raise Exception("Virtual audio thread failed to start")
                except Exception as virtual_error:
                    print(f"❌ Virtual audio failed, falling back to speakers: {virtual_error}")
                    # Fallback to regular speakers
                    if os.path.exists(filename):
                        # Direct playsound call instead of subprocess to avoid WSL
                        playsound(filename)
                    else:
                        print(f"❌ Audio file not found: {filename}")
            else:
                # Regular speaker output
                if os.path.exists(filename):
                    # Direct playsound call instead of subprocess to avoid WSL
                    print(f"🎤 Started audio playback: {filename}")
                    playsound(filename)
                    print("🎤 Audio playback completed")
                else:
                    print(f"❌ Audio file not found: {filename}")
        except Exception as e:
            print(f"🎤 Audio playback error: {e}")
            current_audio_process = None
        finally:
            # Mark that Luna has stopped speaking
            turn_manager.luna_stops_speaking()
        
        # Clean up the file
        try:
            if os.path.exists(filename):
                os.remove(filename)
                print(f"🗑️ Cleaned up: {filename}")
        except Exception as cleanup_error:
            print(f"❌ Cleanup error for {filename}: {cleanup_error}")
        
    except Exception as e:
        print(f"❌ TTS error: {e}")
        # Cleanup on error
        try:
            if os.path.exists(filename):
                os.remove(filename)
                print(f"🗑️ Cleaned up on error: {filename}")
        except Exception as cleanup_error:
            print(f"❌ Error cleanup failed for {filename}: {cleanup_error}")

# 🗣️ Segmented TTS processing functions
@lru_cache(maxsize=4096)
def segment_text_for_tts(text: str, max_sentence_len: int = 220, max_phrase_len: int = 100):
    """Segment text with dynamic segmentation: full sentences, but split long sentences at commas."""
    import re
    text = (text or "").strip()
    if not text:
        return []

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    # Extract sentences while preserving terminal punctuation (., !, ?, …)
    sentence_pattern = re.compile(r"[^.!?…]+[.!?…]|[^.!?…]+$")
    raw_sentences = [s.strip() for s in sentence_pattern.findall(text) if s.strip()]

    # Dynamic segmentation: split long sentences at commas
    final_segments = []
    for sentence in raw_sentences:
        word_count = len(sentence.split())
        
        if word_count <= 50:
            # Short sentence: keep as-is
            final_segments.append(sentence)
        else:
            # Long sentence: split at commas for better interrupt handling
            print(f"🔄 Dynamic segmentation: splitting long sentence ({word_count} words)")
            
            # Split at commas, but preserve the comma
            comma_parts = re.split(r'(,\s*)', sentence)
            
            # Reconstruct segments with commas
            current_segment = ""
            for part in comma_parts:
                if part.strip() == "":
                    continue
                    
                # Add this part to current segment
                current_segment += part
                
                # If this part ends with a comma, check if we should split here
                if part.endswith(','):
                    # Check if we should split here (at least 20 words for better interrupt handling)
                    if len(current_segment.split()) >= 20:
                        final_segments.append(current_segment.strip())
                        current_segment = ""
            
            # Add any remaining segment (the final part without comma)
            if current_segment.strip():
                # If the remaining segment is still very long (>40 words), split it at spaces
                remaining_words = current_segment.split()
                if len(remaining_words) > 40:
                    # Split into chunks of ~30 words
                    for i in range(0, len(remaining_words), 30):
                        chunk = ' '.join(remaining_words[i:i+30])
                        if chunk.strip():
                            final_segments.append(chunk.strip())
                else:
                    final_segments.append(current_segment.strip())
    
    print(f"🎤 Dynamic segmentation: {len(raw_sentences)} sentences → {len(final_segments)} segments")
    return final_segments

async def speak_segment(segment: str, voice_profile: dict, mood: str = "soft", fast_mode: bool = True):
    """Speak a single text segment"""
    if not segment.strip():
        return
    
    print(f"🎤 Speaking segment: {segment[:30]}...")
    
    # Use disk cache for this segment
    try:
        global current_audio_process
        ensure_cache_dir_exists()
        cache_path = get_tts_cache_path(segment, voice_profile)

        # If already cached, play from cache
        if os.path.exists(cache_path):
            try:
                stop_current_audio()
                # Direct playsound call instead of subprocess to avoid WSL
                playsound(cache_path)
            except Exception as e:
                print(f"🎤 Cached segment playback error: {e}")
                current_audio_process = None
            return
        else:
            print(f"❌ Cached audio file not found: {cache_path}")

        # Not cached: synthesize and store in cache
        communicate = edge_tts.Communicate(
            segment,
            voice_profile["voice"],
            rate=voice_profile["rate"],
            volume=voice_profile["volume"]
        )

        tmp_path = cache_path + ".tmp"
        await communicate.save(tmp_path)
        try:
            os.replace(tmp_path, cache_path)
        except Exception:
            # If replace fails, keep tmp as fallback path
            cache_path = tmp_path if os.path.exists(tmp_path) else cache_path

        # Play audio from cache
        try:
            stop_current_audio()
            
            # Check if virtual audio is enabled
            if is_virtual_audio_enabled():
                try:
                    # Play to virtual audio cable
                    virtual_thread = play_tts_to_virtual_cable_async(cache_path)
                    if virtual_thread:
                        virtual_thread.join()  # Wait for completion
                except Exception as virtual_error:
                    print(f"❌ Virtual audio segment failed, falling back: {virtual_error}")
                    # Fallback to regular speakers
                    if os.path.exists(cache_path):
                        # Direct playsound call instead of subprocess to avoid WSL
                        playsound(cache_path)
                    else:
                        print(f"❌ Audio file not found: {cache_path}")
            else:
                # Regular speaker output
                if os.path.exists(cache_path):
                    # Direct playsound call instead of subprocess to avoid WSL
                    playsound(cache_path)
                else:
                    print(f"❌ Audio file not found: {cache_path}")
        except Exception as e:
            print(f"🎤 Segment playback error: {e}")
            current_audio_process = None

    except Exception as e:
        print(f"❌ Segment TTS error: {e}")

async def ensure_segment_cached(segment: str, voice_profile: dict) -> str:
    """Ensure a segment is synthesized and cached; return cache path. NEVER returns None."""
    try:
        ensure_cache_dir_exists()
        cache_path = get_tts_cache_path(segment, voice_profile)
        
        # Validate cache_path is not None
        if not cache_path or cache_path is None:
            raise Exception(f"Cache path is None for segment: {segment[:30]}")
        
        if os.path.exists(cache_path):
            return cache_path

        communicate = edge_tts.Communicate(
            segment,
            voice_profile["voice"],
            rate=voice_profile["rate"],
            volume=voice_profile["volume"]
        )

        tmp_path = cache_path + ".tmp"
        await communicate.save(tmp_path)
        
        # Validate tmp file was created
        if not os.path.exists(tmp_path):
            raise Exception(f"Failed to create temp file: {tmp_path}")
        
        try:
            os.replace(tmp_path, cache_path)
            if os.path.exists(cache_path):
                return cache_path
            else:
                raise Exception("File disappeared after rename")
        except Exception as e:
            print(f"⚠️ Failed to rename temp file: {e}")
            # Clean up any existing cache file that might be corrupted
            if os.path.exists(cache_path):
                try:
                    os.remove(cache_path)
                except:
                    pass
            
            # Try rename again
            try:
                os.replace(tmp_path, cache_path)
                if os.path.exists(cache_path):
                    return cache_path
            except Exception as e2:
                print(f"⚠️ Second rename attempt failed: {e2}")
            
            # Final fallback: use tmp file directly if it exists
            if os.path.exists(tmp_path):
                print(f"⚠️ Using temp file as fallback: {tmp_path}")
                return tmp_path
            else:
                raise Exception(f"Failed to create audio file for segment: {segment[:30]}...")
        
        # Final validation before returning
        if os.path.exists(cache_path):
            return cache_path
        elif os.path.exists(tmp_path):
            return tmp_path
        else:
            raise Exception(f"No valid file path found for segment: {segment[:30]}")
            
    except Exception as e:
        print(f"❌ Segment caching failed: {e}")
        # Return None will be caught by the caller
        return None

def play_audio_file(file_path: str) -> None:
    """Play an audio file synchronously via subprocess, with kill support."""
    global current_audio_process
    try:
        stop_current_audio()
        
        # Validate file exists and is not empty
        if not os.path.exists(file_path):
            print(f"❌ Audio file not found: {file_path}")
            return
        
        # Check if file is empty or corrupted
        if os.path.getsize(file_path) == 0:
            print(f"❌ Audio file is empty: {file_path}")
            return
        
        # Handle temporary files (clean up after playing)
        is_temp_file = file_path.endswith('.tmp')
        
        try:
            # Direct playsound call instead of subprocess to avoid WSL
            playsound(file_path)
            
            # Clean up temp file after successful playback
            if is_temp_file and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"🗑️ Cleaned up temp file: {file_path}")
                except Exception as cleanup_error:
                    print(f"⚠️ Failed to clean up temp file {file_path}: {cleanup_error}")
                    
        except Exception as playback_error:
            print(f"🎤 Playback error: {playback_error}")
            current_audio_process = None
            
            # Clean up temp file on error too
            if is_temp_file and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"🗑️ Cleaned up temp file after error: {file_path}")
                except:
                    pass
                    
    except Exception as e:
        print(f"🎤 General audio error: {e}")
        current_audio_process = None

# 🧪 Test function for tsundere SSMF functionality
def test_tsundere_ssmf():
    """Test function to demonstrate tsundere SSMF voice processing"""
    test_phrases = [
        "It's not like I like you or anything!",
        "Obviously I'm way smarter than you!",
        "Are you okay? You better not get hurt!",
        "Really? You're so slow!",
        "Whatever! I don't care!"
    ]
    
    print("🎭 Testing Tsundere SSMF Processing:")
    print("=" * 50)
    
    for phrase in test_phrases:
        print(f"\n📝 Original: {phrase}")
        
        # Process with SSMF
        clean_text, tsundere_mood = process_ssmf_markup(phrase, "soft", "")
        print(f"🎭 Tsundere Mood: {tsundere_mood}")
        print(f"🎤 Clean Text: {clean_text}")
        
        # Get voice profile
        voice_profile = get_tsundere_voice_profile(tsundere_mood)
        print(f"🎵 Voice Profile: {voice_profile['style']} (Rate: {voice_profile['rate']}, Pitch: {voice_profile['pitch']}, Volume: {voice_profile['volume']})")
        
        print("-" * 30)

async def speak_text_segmented(text: str, mood: str = "soft", fast_mode: bool = True, context: str = ""):
    """Enhanced TTS function with segmented processing"""
    print(f"🎤 Starting segmented TTS generation for: {text[:50]}...")
    
    # Get base voice profile
    voice_profile = VOICE_PROFILES.get(mood, VOICE_PROFILES["soft"])
    print(f"🎤 Using voice profile: {mood}")
    
    # Process text with expressions
    try:
        enhanced_text = process_text_with_expressions(text, mood)
        print(f"🎭 Text processed with expressions")
    except Exception as e:
        print(f"❌ Error processing expressions: {e}")
        enhanced_text = text
    
    # Process text with SSMF markup for tsundere voices
    try:
        ssmf_text, tsundere_mood = process_ssmf_markup(enhanced_text, mood, context)
        if tsundere_mood.startswith("tsundere_"):
            print(f"🎭 SSMF processing: {tsundere_mood} mood detected")
            enhanced_text = ssmf_text
            # Use tsundere voice profile
            voice_profile = get_tsundere_voice_profile(tsundere_mood)
        else:
            print(f"🎭 SSMF processing: Standard mood ({mood})")
    except Exception as e:
        print(f"❌ Error processing SSMF markup: {e}")
        # Fallback to original voice profile
        voice_profile = VOICE_PROFILES.get(mood, VOICE_PROFILES["soft"])
    
    # Create dynamic voice profile
    try:
        dynamic_profile, enhanced_text, throat_sounds = create_human_voice_profile(voice_profile, enhanced_text, mood, context)
        print(f"🎤 Dynamic profile created: {dynamic_profile['voice']} at {dynamic_profile['rate']}")
    except Exception as e:
        print(f"❌ Error creating dynamic profile: {e}")
        dynamic_profile = voice_profile.copy()
        enhanced_text = text
    
    # Process text with effects
    try:
        throat_text = apply_throat_effects(enhanced_text, throat_sounds)
        intonation_text = process_text_with_intonation(throat_text, mood, context)
        processed_text = process_text_for_tts(intonation_text, mood)
        
        # Clean any SSMF markup that might have gotten through
        processed_text = clean_ssmf_markup(processed_text)
        
        print(f"🎤 Processed text with effects: {processed_text[:50]}...")
    except Exception as e:
        print(f"❌ Error processing text: {e}")
        processed_text = text.replace("*", "").replace("_", "").strip()
        # Clean markup from fallback text too
        processed_text = clean_ssmf_markup(processed_text)
    
    # Keep rate at +5% regardless of fast mode
    if fast_mode:
        try:
            # Force rate to +5% for consistent speed
            dynamic_profile["rate"] = "+5%"
        except Exception as e:
            print(f"❌ Error setting rate: {e}")
            dynamic_profile["rate"] = "+5%"
    
    # Validate settings
    try:
        rate = dynamic_profile["rate"]
        volume = dynamic_profile["volume"]
        
        rate_value = int(rate.replace("%", ""))
        rate_value = max(-100, min(50, rate_value))
        rate = f"{rate_value:+d}%"
        
        volume_value = int(volume.replace("%", ""))
        volume_value = max(-100, min(100, volume_value))
        volume = f"{volume_value:+d}%"
        
        dynamic_profile["rate"] = rate
        dynamic_profile["volume"] = volume
        
    except Exception as e:
        print(f"❌ Error validating settings: {e}")
        dynamic_profile["rate"] = "+5%"
        dynamic_profile["volume"] = "+0%"
    
    print(f"🎤 Final TTS settings: voice={dynamic_profile['voice']}, rate={dynamic_profile['rate']}, volume={dynamic_profile['volume']}")
    
    # Segment the text with dynamic segmentation (sentences + comma splitting for long ones)
    segments = segment_text_for_tts(processed_text, max_sentence_len=50, max_phrase_len=25)
    print(f"🎤 Text segmented into {len(segments)} full sentences")

    # Prefetch pipeline: cache-ahead while playing current
    prefetch_window = 3
    total = len(segments)
    if total == 0:
        print("🎤 No segments to speak")
        return

    # Ensure first segment is cached to minimize initial latency
    first_path = await ensure_segment_cached(segments[0], dynamic_profile)

    # Schedule initial prefetch tasks
    prefetch_tasks = {}
    for j in range(1, min(prefetch_window, total)):
        prefetch_tasks[j] = asyncio.create_task(ensure_segment_cached(segments[j], dynamic_profile))

    # Play segments with rolling prefetch
    for i in range(total):
        segment = segments[i]
        print(f"🎤 Processing segment {i+1}/{total}: {segment[:60]}...")

        # Get cache path for this segment (from task or ensure now)
        try:
            if i == 0:
                path = first_path
            elif i in prefetch_tasks:
                path = await prefetch_tasks[i]
                del prefetch_tasks[i]
            else:
                path = await ensure_segment_cached(segment, dynamic_profile)
            
            # Validate path before playing
            if not path or path is None:
                print(f"⚠️ Segment {i+1} returned None path, skipping...")
                continue
            
            # Validate file exists
            if not os.path.exists(path):
                print(f"⚠️ Segment {i+1} file not found: {path}, skipping...")
                continue

            # Play current segment (blocking while we prefetch further in background)
            play_audio_file(path)
        except Exception as segment_error:
            print(f"⚠️ Segment {i+1}/{total} playback error: {segment_error}, continuing...")

        # Schedule next prefetch if within window
        next_index_to_schedule = i + prefetch_window
        if next_index_to_schedule < total and next_index_to_schedule not in prefetch_tasks:
            prefetch_tasks[next_index_to_schedule] = asyncio.create_task(
                ensure_segment_cached(segments[next_index_to_schedule], dynamic_profile)
            )

        # Natural pause: sentence-aware only
        if i < total - 1:
            end_char = segment.strip()[-1:] if segment.strip() else ""
            await asyncio.sleep(0.22 if end_char in ".!?…" else 0.10)
    
    print(f"🎤 Segmented TTS completed")
    
    # Signal End flag to TTS event manager
    try:
        tts_event_manager.signal_end_flag()
        print("🎯 TTS Event: End flag signaled after TTS completion")
    except Exception as e:
        print(f"❌ Error signaling End flag: {e}")

# 🎧 Updated speak wrapper with event architecture
def speak(text: str, mood: str = "soft", fast_mode: bool = True, interrupt_callback=None, context: str = ""):
    """Updated speak wrapper with event architecture - adds message to queue"""
    try:
        # Add message to TTS event queue
        tts_event_manager.add_tts_message(text, mood, fast_mode, context)
        return {"success": True, "message": "TTS message added to queue"}
    except Exception as e:
        print(f"❌ Error adding TTS message to queue: {e}")
        return {"success": False, "error": str(e)}

# 🎧 Direct speak function (bypasses event system)
def speak_direct(text: str, mood: str = "soft", fast_mode: bool = True, interrupt_callback=None, context: str = ""):
    """Direct speak function that bypasses the event system"""
    try:
        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Run the segmented async function
            loop.run_until_complete(speak_text_segmented(text, mood, fast_mode, context))
        finally:
            # Clean up the loop
            loop.close()
            
    except Exception as e:
        print(f"Voice error: {e}")

# Global audio process tracking
current_audio_process = None

def start_interrupt_detection():
    """Simple interrupt detection placeholder"""
    print("🎤 Interrupt detection started")

def stop_current_audio():
    """Stop current audio playback"""
    global current_audio_process
    

    
    # Stop virtual audio if active
    if is_virtual_audio_enabled():
        try:
            stop_virtual_audio()
        except Exception as virtual_error:
            print(f"⚠️ Error stopping virtual audio: {virtual_error}")
    
    # Stop regular audio process
    if current_audio_process:
        try:
            current_audio_process.terminate()
            current_audio_process = None
            print("🎤 Audio stopped")
        except Exception as e:
            print(f"❌ Error stopping audio: {e}")



# Virtual audio settings
virtual_audio_enabled = False
virtual_audio_initialized = False



# 🎤 VMC Lip-sync settings
# VMC lip sync variables (removed - not using VSeeFace)
vmc_lipsync_enabled = False
vmc_lipsync_initialized = False

# 🧹 Clean up any leftover voice files
def cleanup_old_voice_files():
    """Clean up any leftover voice files from previous runs"""
    import glob
    try:
        # Find all luna_voice_*.mp3 files
        voice_files = glob.glob("luna_voice_*.mp3")
        cleaned_count = 0
        for file in voice_files:
            try:
                os.remove(file)
                cleaned_count += 1
            except Exception as e:
                print(f"❌ Failed to clean up {file}: {e}")
        
        if cleaned_count > 0:
            print(f"🗑️ Cleaned up {cleaned_count} old voice files")
        else:
            print("✨ No old voice files found to clean up")
        
        # Also clean up any corrupted temp files
        temp_cleaned = cleanup_corrupted_temp_files()
        if temp_cleaned > 0:
            print(f"🗑️ Cleaned up {temp_cleaned} corrupted temp files")
            
    except Exception as e:
        print(f"❌ Cleanup error: {e}")

def cleanup_all_voice_files():
    """Force cleanup all voice files (emergency cleanup)"""
    import glob
    try:

        
        # Cleanup virtual audio
        if VIRTUAL_AUDIO_AVAILABLE:
            try:
                cleanup_virtual_audio()
            except:
                pass
        
        # Cleanup voice files
        voice_files = glob.glob("luna_voice_*.mp3")
        for file in voice_files:
            try:
                os.remove(file)
                print(f"🗑️ Emergency cleanup: {file}")
            except:
                pass
        print(f"🧹 Emergency cleanup complete - removed {len(voice_files)} files")
    except:
        pass

def cleanup_tts_cache():
    """Clean up all TTS cache files after each reply - DELAYED for safe deletion"""
    import glob
    import time
    
    def delayed_cleanup():
        """Cleanup files in background after safe delay"""
        # Wait 5 seconds to ensure all audio playback is complete
        time.sleep(5.0)
        
        try:
            # Clean up both cache directory and any leftover temp files
            cache_files = []
            
            # Get files from cache directory
            if os.path.exists(CACHE_DIR):
                cache_files.extend(glob.glob(os.path.join(CACHE_DIR, "tts_*.mp3")))
                cache_files.extend(glob.glob(os.path.join(CACHE_DIR, "tts_*.tmp")))
            
            # Also clean up any TTS files in root directory
            cache_files.extend(glob.glob("luna_voice_*.mp3"))
            cache_files.extend(glob.glob("tts_*.mp3"))
            cache_files.extend(glob.glob("tts_*.tmp"))
            
            cleaned_count = 0
            for file in cache_files:
                try:
                    if os.path.exists(file):
                        # Check if file is empty or corrupted
                        if os.path.getsize(file) == 0:
                            os.remove(file)
                            cleaned_count += 1
                            continue
                        
                        # Try to remove file (will fail if still in use)
                        os.remove(file)
                        cleaned_count += 1
                except PermissionError:
                    # File still in use, skip silently
                    pass
                except Exception as e:
                    # Don't print errors for files that are still in use
                    if "being used by another process" not in str(e):
                        print(f"⚠️ Could not clean file {os.path.basename(file)}: {e}")
            
            if cleaned_count > 0:
                print(f"🗑️ Cleaned up {cleaned_count} TTS cache files (delayed)")
        
        except Exception as e:
            print(f"⚠️ Delayed TTS cleanup error: {e}")
    
    # Run cleanup in background thread with delay
    import threading
    threading.Thread(target=delayed_cleanup, daemon=True).start()
    return 0  # Return immediately

def cleanup_corrupted_temp_files():
    """Clean up any corrupted temporary files that might be causing issues"""
    import glob
    try:
        # Find all .tmp files
        temp_files = []
        if os.path.exists(CACHE_DIR):
            temp_files.extend(glob.glob(os.path.join(CACHE_DIR, "*.tmp")))
        temp_files.extend(glob.glob("*.tmp"))
        
        cleaned_count = 0
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    # Remove temp files that are empty or very small (likely corrupted)
                    if os.path.getsize(temp_file) < 1024:  # Less than 1KB
                        os.remove(temp_file)
                        print(f"🗑️ Removed corrupted temp file: {temp_file}")
                        cleaned_count += 1
            except Exception as e:
                print(f"⚠️ Failed to clean up temp file {temp_file}: {e}")
        
        if cleaned_count > 0:
            print(f"🗑️ Cleaned up {cleaned_count} corrupted temp files")
        
        return cleaned_count
    except Exception as e:
        print(f"❌ Temp file cleanup error: {e}")
        return 0

# 🎧 Virtual Audio Functions
def init_virtual_audio():
    """Initialize virtual audio system"""
    global virtual_audio_initialized
    
    if not VIRTUAL_AUDIO_AVAILABLE:
        print("⚠️ Virtual audio module not available")
        return False
    
    try:
        if initialize_virtual_audio():
            virtual_audio_initialized = True
            status = get_virtual_audio_status()
            print(f"🎧 Virtual audio initialized: {status['virtual_device']}")
            return True
        else:
            print("❌ Virtual audio initialization failed")
            return False
    except Exception as e:
        print(f"❌ Virtual audio init error: {e}")
        return False

def enable_virtual_audio(enabled: bool = True):
    """Enable or disable virtual audio output"""
    global virtual_audio_enabled
    
    if enabled and not virtual_audio_initialized:
        if init_virtual_audio():
            virtual_audio_enabled = True
            print("🎧 Virtual audio enabled")
        else:
            print("❌ Cannot enable virtual audio - initialization failed")
            virtual_audio_enabled = False
    else:
        virtual_audio_enabled = enabled
        print(f"🎧 Virtual audio {'enabled' if enabled else 'disabled'}")

def is_virtual_audio_enabled() -> bool:
    """Check if virtual audio is enabled and available"""
    return virtual_audio_enabled and virtual_audio_initialized and VIRTUAL_AUDIO_AVAILABLE

def get_virtual_audio_info() -> dict:
    """Get virtual audio system information"""
    if VIRTUAL_AUDIO_AVAILABLE and virtual_audio_initialized:
        status = get_virtual_audio_status()
        status['enabled'] = virtual_audio_enabled
        return status
    else:
        return {
            'available': VIRTUAL_AUDIO_AVAILABLE,
            'initialized': virtual_audio_initialized,
            'enabled': virtual_audio_enabled,
            'virtual_device': None
        }


# 🎤 VMC Lip Sync Functions (removed - not using VSeeFace)
def init_vmc_lipsync():
    """VMC lip sync removed - not using VSeeFace"""
    return False

def enable_vmc_lipsync(enabled: bool = True):
    """VMC lip sync removed - not using VSeeFace"""
    pass

def is_vmc_lipsync_enabled() -> bool:
    """VMC lip sync removed - not using VSeeFace"""
    return False

def get_vmc_lipsync_info() -> dict:
    """VMC lip sync removed - not using VSeeFace"""
    return {
        'available': False,
        'initialized': False,
        'enabled': False,
        'connected': False,
        'lip_sync_enabled': False
    }

# ⚡ Fast response system
def pre_generate_common_responses():
    """Pre-generate common responses for instant playback"""
    common_phrases = [
        ("Hello Chris!", "soft"),
        ("I love you!", "romantic"),
        ("That's amazing!", "excited"),
        ("Oh no!", "sad"),
        ("Haha!", "playful"),
        ("Yes!", "confident"),
        ("No way!", "excited"),
        ("Really?", "curious"),
        ("Thank you!", "soft"),
        ("You're welcome!", "playful")
    ]
    
    print("⚡ Pre-generating common responses for instant playback...")
    for phrase, mood in common_phrases:
        try:
            # Use speak without interrupt detection for pre-generation
            speak(phrase, mood, fast_mode=True, interrupt_callback=None)
        except:
            pass

# 🎵 Get available voices (for debugging)
async def list_voices():
    voices = await edge_tts.list_voices()
    print("Available Edge TTS voices:")
    for voice in voices:
        if "en-US" in voice["ShortName"] or "en-GB" in voice["ShortName"]:
            print(f"  {voice['ShortName']} - {voice['FriendlyName']}")

# 🎤 Turn-taking system functions
def is_luna_speaking() -> bool:
    """Check if Luna is currently speaking"""
    return turn_manager.luna_is_speaking

def can_user_speak() -> bool:
    """Check if user can speak (Luna is not speaking and enough silence has passed)"""
    return turn_manager.can_user_speak()

def get_turn_status() -> dict:
    """Get current turn-taking status"""
    return turn_manager.get_turn_status()

def get_tts_status() -> dict:
    """Get current TTS status"""
    return turn_manager.get_tts_status()

def get_tts_event_status() -> dict:
    """Get current TTS event system status"""
    return tts_event_manager.get_queue_status()

def clear_tts_queue():
    """Clear all pending TTS messages"""
    tts_event_manager.clear_queue()

def stop_tts_worker():
    """Stop the TTS worker thread"""
    tts_event_manager.stop_worker()

def calculate_tts_duration(text: str, voice_profile: dict = None) -> float:
    """Calculate estimated TTS duration for given text and voice profile"""
    if voice_profile is None:
        voice_profile = VOICE_PROFILES["soft"]
    
    # Base calculation: ~150 words per minute
    words = len(text.split())
    base_seconds = (words / 150) * 60
    
    # Adjust for voice profile settings
    rate = voice_profile.get("rate", "+0%")
    if "+" in rate:
        try:
            rate_adjustment = float(rate.replace("+", "").replace("%", "")) / 100
            base_seconds = base_seconds / (1 + rate_adjustment)
        except:
            pass
    
    # Add small buffer for processing
    return base_seconds + 0.5

def generate_tts_audio(text: str, mood: str = "soft") -> str:
    """Generate TTS audio file and return the file path"""
    try:
        import tempfile
        import os
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_path = temp_file.name
        temp_file.close()
        
        # Get voice profile
        voice_profile = VOICE_PROFILES.get(mood, VOICE_PROFILES["soft"])
        
        # Use Edge TTS for speech generation
        try:
            # Generate speech with Edge TTS
            output_path = f"tts_cache/edge_tts_{int(time.time())}.mp3"
            
            # Ensure cache directory exists
            os.makedirs("tts_cache", exist_ok=True)
            
            # Use Edge TTS to generate speech
            voice = "en-US-AriaNeural"  # Default voice
            if mood == "excited":
                voice = "en-US-JennyNeural"
            elif mood == "sad":
                voice = "en-US-AriaNeural"
            elif mood == "angry":
                voice = "en-US-GuyNeural"
            
            # Generate TTS
            communicate = edge_tts.Communicate(text, voice)
            communicate.save(output_path)
            
            if os.path.exists(output_path):
                return output_path
            else:
                print("❌ Edge TTS file not generated")
                
        except Exception as e:
            print(f"⚠️ Edge TTS error: {e}, falling back to default TTS")
        
        # Fallback to default TTS (pyttsx3)
        try:
            import pyttsx3
            
            engine = pyttsx3.init()
            
            # Set voice properties
            voices = engine.getProperty('voices')
            if voices:
                # Try to find a female voice
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
            
            # Set speech rate
            engine.setProperty('rate', voice_profile.get('rate', 200))
            engine.setProperty('volume', voice_profile.get('volume', 0.8))
            
            # Save to file
            engine.save_to_file(text, temp_path)
            engine.runAndWait()
            
            return temp_path
            
        except Exception as e:
            print(f"❌ Error generating TTS audio: {e}")
            return None
            
    except Exception as e:
        print(f"❌ Error in generate_tts_audio: {e}")
        return None


