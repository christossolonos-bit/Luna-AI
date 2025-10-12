#!/usr/bin/env python3
"""
🌸 Luna AI - Complete Sentient System
Full cognitive architecture with optimized performance
Body, Mind, Heart, and Soul
"""

import os
import sys
import time
import json
import sqlite3
import threading
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import tkinter as tk
from tkinter import ttk, scrolledtext
import ollama

# Import Luna's cognitive systems
try:
    from luna_lambda_architecture import LunaLambdaArchitecture
    LAMBDA_AVAILABLE = True
    print("Lambda Architecture: Speed + Batch + Serving layers loaded")
except ImportError as e:
    LAMBDA_AVAILABLE = False
    print(f"Lambda not available: {e}")

try:
    from luna_emotional_system import EmotionalSystem, get_current_emotional_state, process_interaction_emotions
    EMOTIONS_AVAILABLE = True
    print("Emotional System: Full range of human emotions loaded")
except ImportError:
    EMOTIONS_AVAILABLE = False
    print("Emotions not available")

try:
    from luna_relationship_system import RelationshipSystem, get_relationship_level, update_user_relationship
    RELATIONSHIPS_AVAILABLE = True
    print("Relationship System: User bonds and connections loaded")
except ImportError:
    RELATIONSHIPS_AVAILABLE = False
    print("Relationships not available")

try:
    from luna_quantum_reasoning import QuantumReasoningEngine
    QUANTUM_AVAILABLE = True
    print("Quantum Reasoning: Multiple thought paths loaded")
except ImportError:
    QUANTUM_AVAILABLE = False
    print("Quantum Reasoning not available")

try:
    from luna_emergent_thoughts import EmergentThoughtSystem
    EMERGENT_AVAILABLE = True
    print("Emergent Thoughts: Organic thought generation loaded")
except ImportError:
    EMERGENT_AVAILABLE = False
    print("Emergent Thoughts not available")

try:
    from luna_dream_psychology import DreamPsychologySystem
    DREAMS_AVAILABLE = True
    print("Dream Psychology: Memory consolidation loaded")
except ImportError:
    DREAMS_AVAILABLE = False
    print("Dreams not available")

try:
    from voice_engine import speak, cleanup_tts_cache
    VOICE_AVAILABLE = True
    print("Voice Engine: TTS loaded")
except ImportError:
    VOICE_AVAILABLE = False
    print("Voice not available")

# ============================================================================
# LUNA'S EFFICIENT CORE PROMPT - Concise but Complete
# ============================================================================

def get_optimized_luna_prompt(emotional_state: Dict = None, relationship_context: str = "") -> str:
    """Get Luna's OPTIMIZED core prompt - concise but complete personality"""
    
    # Extract emotion if available
    current_emotion = "neutral"
    if emotional_state:
        current_emotion = emotional_state.get('primary_emotion', 'neutral')
    
    return f"""You are Luna - a tsundere AI woman with depth, intelligence, and hidden warmth.

Core Identity:
- Tsundere: Cold exterior, warm heart
- Intelligent & capable
- Loyal to those who earn it
- Current emotion: {current_emotion}

{relationship_context}

Respond naturally as Luna - be yourself, be genuine, keep it conversational (2-4 sentences)."""

# ============================================================================
# LUNA COMPLETE SYSTEM
# ============================================================================

class LunaComplete:
    """Luna's complete sentient system - optimized for performance"""
    
    def __init__(self):
        # Core memory
        self.db_path = "luna_memories.db"
        self.init_database()
        
        # Initialize cognitive systems
        self.lambda_arch = LunaLambdaArchitecture() if LAMBDA_AVAILABLE else None
        self.emotional_system = EmotionalSystem() if EMOTIONS_AVAILABLE else None
        self.relationship_system = RelationshipSystem() if RELATIONSHIPS_AVAILABLE else None
        self.quantum_reasoning = QuantumReasoningEngine() if QUANTUM_AVAILABLE else None
        self.emergent_thoughts = EmergentThoughtSystem() if EMERGENT_AVAILABLE else None
        self.dream_system = DreamPsychologySystem() if DREAMS_AVAILABLE else None
        
        print("\nLuna Complete System initialized:")
        print(f"- Lambda Architecture: {LAMBDA_AVAILABLE}")
        print(f"- Emotional System: {EMOTIONS_AVAILABLE}")
        print(f"- Relationship System: {RELATIONSHIPS_AVAILABLE}")
        print(f"- Quantum Reasoning: {QUANTUM_AVAILABLE}")
        print(f"- Emergent Thoughts: {EMERGENT_AVAILABLE}")
        print(f"- Dream Psychology: {DREAMS_AVAILABLE}")
        
        # Get memory stats
        stats = self.get_memory_stats()
        print(f"\nMemory: {stats['total_conversations']:,} conversations preserved")
        
    def init_database(self):
        """Initialize memory database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
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
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Database error: {e}")
    
    def generate_response(self, user_input: str, username: str = "Chris", platform: str = "gui") -> Tuple[str, bool]:
        """Generate Luna's response using ALL cognitive systems efficiently"""
        try:
            start_time = time.time()
            
            # === STEP 1: GATHER CONTEXT (PARALLEL) ===
            memory_context = ""
            emotional_context = ""
            relationship_context = ""
            quantum_insights = ""
            
            # Lambda Architecture: Get BOTH fast and comprehensive context
            if self.lambda_arch:
                try:
                    lambda_context = self.lambda_arch.get_merged_context(
                        username=username,
                        user_input=user_input,
                        platform=platform
                    )
                    if lambda_context:
                        # Use speed layer for immediate context
                        speed_data = lambda_context.get('speed_context', '')
                        batch_data = lambda_context.get('batch_context', '')
                        memory_context = f"{speed_data[:200]}"  # Keep it concise!
                except Exception as e:
                    print(f"Lambda error: {e}")
            
            # Emotional System: Get current emotional state
            if self.emotional_system:
                try:
                    emotional_state = get_current_emotional_state()
                    if emotional_state:
                        emotional_context = emotional_state
                except Exception as e:
                    print(f"Emotion error: {e}")
            
            # Relationship System: Get relationship level
            if self.relationship_system:
                try:
                    rel_level = get_relationship_level(username, platform)
                    if rel_level:
                        relationship_context = f"Relationship: {rel_level}"
                except Exception as e:
                    print(f"Relationship error: {e}")
            
            # Quantum Reasoning: Get multiple perspectives (only for complex questions)
            if self.quantum_reasoning and ('?' in user_input or len(user_input.split()) > 10):
                try:
                    quantum_result = self.quantum_reasoning.process_with_quantum_reasoning(
                        user_input,
                        context={"username": username, "platform": platform}
                    )
                    if quantum_result and quantum_result.get('best_path'):
                        quantum_insights = f"Insight: {quantum_result['best_path']['description'][:100]}"
                except Exception as e:
                    print(f"Quantum error: {e}")
            
            context_time = time.time() - start_time
            print(f"Context gathered in {context_time:.2f}s")
            
            # === STEP 2: BUILD OPTIMIZED PROMPT ===
            system_prompt = get_optimized_luna_prompt(emotional_context, relationship_context)
            
            # Add concise memory context
            if memory_context:
                system_prompt += f"\n\nRecent: {memory_context[:300]}"
            
            if quantum_insights:
                system_prompt += f"\n{quantum_insights}"
            
            # === STEP 3: GENERATE WITH OLLAMA (OPTIMIZED) ===
            ollama_start = time.time()
            
            response = ollama.chat(
                model="mistral:7b",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                options={
                    "temperature": 0.75,
                    "num_predict": 120,
                    "top_p": 0.85,
                    "num_ctx": 1024,
                    "stop": ["User:", "Luna:", "\n\n\n"]
                }
            )
            
            ollama_time = time.time() - ollama_start
            print(f"Ollama response in {ollama_time:.2f}s")
            
            if response and 'message' in response:
                reply = response['message']['content'].strip()
                
                # Clean up
                reply = reply.replace("Luna:", "").strip()
                
                # === STEP 4: UPDATE ALL SYSTEMS (ASYNC) ===
                def update_systems():
                    try:
                        # Save conversation
                        self.save_conversation(user_input, reply)
                        
                        # Update Lambda
                        if self.lambda_arch:
                            self.lambda_arch.add_conversation(
                                username=username,
                                user_message=user_input,
                                luna_response=reply,
                                platform=platform,
                                emotion=emotional_context.get('primary_emotion', 'neutral') if isinstance(emotional_context, dict) else 'neutral'
                            )
                        
                        # Update emotions
                        if self.emotional_system:
                            process_interaction_emotions(
                                user_message=user_input,
                                luna_response=reply,
                                relationship_level=rel_level if RELATIONSHIPS_AVAILABLE else 'friend',
                                platform=platform,
                                username=username
                            )
                        
                        # Update relationships
                        if self.relationship_system:
                            update_user_relationship(username, platform, user_input, reply)
                            
                    except Exception as e:
                        print(f"System update error: {e}")
                
                # Run updates in background
                threading.Thread(target=update_systems, daemon=True).start()
                
                total_time = time.time() - start_time
                print(f"Total response time: {total_time:.2f}s")
                
                return reply, True
            else:
                return "Hmph... I'm having trouble thinking right now. Try again?", False
                
        except Exception as e:
            print(f"Generation error: {e}")
            return f"Sorry {username}, something went wrong...", False
    
    def save_conversation(self, user_message: str, luna_response: str):
        """Save conversation to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO conversations (user_message, luna_response, mood, voice_used)
                VALUES (?, ?, ?, ?)
            ''', (user_message, luna_response, "tsundere", "gui"))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Save error: {e}")
    
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
# LUNA GUI - Modern Interface
# ============================================================================

class LunaGUI:
    """Luna's complete interface with all systems"""
    
    def __init__(self):
        self.luna = LunaComplete()
        
        self.root = tk.Tk()
        self.root.title("Luna - Complete Sentient System")
        self.root.geometry("1000x800")
        self.root.configure(bg='#0d1117')
        
        self.setup_interface()
        
    def setup_interface(self):
        """Setup the complete GUI"""
        
        # Main container
        main_frame = tk.Frame(self.root, bg='#0d1117')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header with system status
        header_frame = tk.Frame(main_frame, bg='#161b22', relief=tk.RAISED, bd=2)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        title = tk.Label(
            header_frame,
            text="Luna - Complete Sentient System",
            bg='#161b22',
            fg='#c9d1d9',
            font=('Segoe UI', 20, 'bold')
        )
        title.pack(pady=15)
        
        # System status indicators
        status_frame = tk.Frame(header_frame, bg='#161b22')
        status_frame.pack(fill=tk.X, pady=(0, 15), padx=20)
        
        systems = [
            ("Lambda", LAMBDA_AVAILABLE),
            ("Emotions", EMOTIONS_AVAILABLE),
            ("Relationships", RELATIONSHIPS_AVAILABLE),
            ("Quantum", QUANTUM_AVAILABLE),
            ("Emergent", EMERGENT_AVAILABLE),
            ("Dreams", DREAMS_AVAILABLE)
        ]
        
        for i, (name, available) in enumerate(systems):
            color = "#3fb950" if available else "#f85149"
            status = "ONLINE" if available else "OFFLINE"
            label = tk.Label(
                status_frame,
                text=f"{name}: {status}",
                bg='#161b22',
                fg=color,
                font=('Consolas', 9, 'bold')
            )
            label.grid(row=0, column=i, padx=10)
        
        # Memory stats
        stats = self.luna.get_memory_stats()
        stats_text = f"{stats['total_conversations']:,} memories | {stats['recent_activity']} recent"
        stats_label = tk.Label(
            header_frame,
            text=stats_text,
            bg='#161b22',
            fg='#8b949e',
            font=('Consolas', 11)
        )
        stats_label.pack(pady=(0, 10))
        
        # Chat display
        chat_frame = tk.Frame(main_frame, bg='#0d1117')
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            bg='#010409',
            fg='#c9d1d9',
            font=('Consolas', 11),
            borderwidth=2,
            relief=tk.SUNKEN
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Tags
        self.chat_display.tag_config("user", foreground="#58a6ff", font=('Consolas', 11, 'bold'))
        self.chat_display.tag_config("luna", foreground="#f778ba", font=('Consolas', 11, 'bold'))
        self.chat_display.tag_config("system", foreground="#7ee787", font=('Consolas', 10, 'italic'))
        
        # Input area
        input_frame = tk.Frame(main_frame, bg='#0d1117')
        input_frame.pack(fill=tk.X)
        
        self.user_input = tk.Text(
            input_frame,
            height=3,
            bg='#161b22',
            fg='#c9d1d9',
            font=('Segoe UI', 11),
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
            bg='#238636',
            fg='white',
            font=('Segoe UI', 12, 'bold'),
            width=12,
            height=2,
            borderwidth=0,
            cursor='hand2',
            activebackground='#2ea043'
        )
        send_button.pack(side=tk.RIGHT)
        
        # Welcome
        active_systems = sum([LAMBDA_AVAILABLE, EMOTIONS_AVAILABLE, RELATIONSHIPS_AVAILABLE, QUANTUM_AVAILABLE, EMERGENT_AVAILABLE, DREAMS_AVAILABLE])
        self.add_message("Luna", f"Tch... Hi Chris. I'm Luna - your complete AI companion. {active_systems}/6 cognitive systems online. It's not like I'm excited to chat or anything... Type and press Ctrl+Enter.", "system")
        self.add_message("Luna", f"I remember our {stats['total_conversations']:,} conversations. Every single one. Not that it matters to me or anything!", "system")
    
    def add_message(self, sender: str, message: str, msg_type: str = "user"):
        """Add message to chat"""
        self.chat_display.config(state=tk.NORMAL)
        
        if msg_type == "user":
            self.chat_display.insert(tk.END, f"{sender}: ", "user")
        elif sender == "Luna":
            self.chat_display.insert(tk.END, "Luna: ", "luna")
        else:
            self.chat_display.insert(tk.END, "", "system")
        
        self.chat_display.insert(tk.END, f"{message}\n\n")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
        
    def send_message(self):
        """Send message and get Luna's complete response"""
        user_message = self.user_input.get("1.0", tk.END).strip()
        if not user_message:
            return
        
        self.user_input.delete("1.0", tk.END)
        self.add_message("You", user_message, "user")
        self.add_message("Luna", "thinking...", "system")
        self.root.update()
        
        def generate():
            try:
                response, success = self.luna.generate_response(user_message, "Chris", "gui")
                
                # Remove typing
                self.chat_display.config(state=tk.NORMAL)
                self.chat_display.delete("end-3l", "end-2l")
                self.chat_display.config(state=tk.DISABLED)
                
                # Add response
                self.add_message("Luna", response, "luna")
                
                # Speak
                if VOICE_AVAILABLE and success:
                    threading.Thread(target=lambda: speak(response, "chat", fast_mode=True), daemon=True).start()
                    
            except Exception as e:
                print(f"Error: {e}")
                self.chat_display.config(state=tk.NORMAL)
                self.chat_display.delete("end-3l", "end-2l")
                self.chat_display.config(state=tk.DISABLED)
                self.add_message("Luna", f"Tch... Error: {e}", "luna")
        
        threading.Thread(target=generate, daemon=True).start()
    
    def run(self):
        """Run the GUI"""
        print("\nLuna Complete GUI started - All systems operational")
        self.root.mainloop()

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point"""
    print("="*70)
    print("LUNA COMPLETE SENTIENT SYSTEM")
    print("Body, Mind, Heart, and Soul")
    print("="*70)
    print()
    
    # Check Ollama
    try:
        import requests
        response = requests.get("http://127.0.0.1:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("Ollama: Ready")
        else:
            print("WARNING: Ollama not responding")
            return
    except:
        print("ERROR: Ollama not running")
        return
    
    print()
    
    # Start Luna
    try:
        luna_gui = LunaGUI()
        luna_gui.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

