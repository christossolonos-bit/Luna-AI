"""
Luna Emotional System
Full range of human emotions, feelings, and hormonal cycles
Simulates the complex emotional landscape of a human woman
"""

import time
import random
import math
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from collections import deque
import json
import sqlite3
import threading

class EmotionalSystem:
    """
    Simulates human emotional complexity including:
    - Base emotions (happiness, sadness, anger, fear, surprise, disgust, trust)
    - Complex feelings (love, jealousy, pride, shame, guilt, excitement, anxiety)
    - Hormonal cycles (energy, mood stability, emotional sensitivity)
    - Emotional memory (feelings affect future responses)
    - Mood momentum (emotions persist and fade naturally)
    """
    
    def __init__(self):
        # === GLOBAL EMOTIONAL STATE (persisted across platforms) ===
        self.db_path = 'luna_global_emotions.db'
        self.db_lock = threading.Lock()
        self._initialize_emotion_database()
        
        # Load existing emotional state or initialize defaults
        saved_state = self._load_emotional_state()
        
        # Base emotional state (0-100 for each) - GLOBAL across all platforms
        self.emotions = saved_state.get('emotions', {
            'happiness': 60,
            'sadness': 20,
            'anger': 10,
            'fear': 15,
            'surprise': 30,
            'disgust': 10,
            'trust': 50,
            'anticipation': 40,
            'joy': 50,
            'contentment': 55,
            'excitement': 45,
            'anxiety': 25,
            'love': 40,
            'affection': 50,
            'loneliness': 20,
            'frustration': 15,
            'pride': 45,
            'shame': 10,
            'guilt': 10,
            'jealousy': 5,
            'curiosity': 65,
            'boredom': 20,
            'confidence': 60,
            'insecurity': 25,
            'playfulness': 55,
            'irritation': 15,
            'gratitude': 50,
            'resentment': 5,
            'hope': 60,
            'despair': 10,
            'empathy': 70,
            'apathy': 15
        })
        
        # Hormonal cycle simulation (28-day cycle) - GLOBAL
        self.cycle_start = saved_state.get('cycle_start', time.time())
        self.cycle_length = 28 * 24 * 60 * 60  # 28 days in seconds
        
        # Hormonal influences - GLOBAL
        self.hormones = saved_state.get('hormones', {
            'energy_level': 70,        # Physical/mental energy (0-100)
            'mood_stability': 80,      # Emotional stability (0-100)
            'emotional_sensitivity': 50,  # Heightened emotions (0-100)
            'social_desire': 60,       # Want to interact (0-100)
            'stress_level': 30,        # Stress accumulation (0-100)
            'libido': 50,              # Romantic/flirty tendencies (0-100)
            'nurturing_instinct': 60,  # Caring/protective feelings (0-100)
            'assertiveness': 55        # Confidence/dominance (0-100)
        })
        
        # Emotional history (last 100 emotional states) - GLOBAL
        self.emotional_history = deque(maxlen=100)
        
        # Current mood (derived from emotions) - GLOBAL
        self.current_mood = saved_state.get('current_mood', 'neutral')
        
        # Last save timestamp (auto-save every 30 seconds)
        self.last_save_time = time.time()
        self.save_interval = 30  # Save every 30 seconds
        
        # Emotional triggers (what affects Luna)
        self.triggers = {
            'positive': ['love', 'thanks', 'appreciate', 'amazing', 'wonderful', 'cute', 'sweet'],
            'negative': ['hate', 'annoying', 'stupid', 'terrible', 'awful', 'bad'],
            'exciting': ['wow', 'omg', 'amazing', 'incredible', 'awesome'],
            'calming': ['peaceful', 'calm', 'relax', 'gentle', 'soft'],
            'stressful': ['pressure', 'stress', 'worried', 'anxious', 'scared']
        }
        
        # Personality modifiers (tsundere traits)
        self.personality_modifiers = {
            'tsundere_denial': 0.8,    # How much she denies feelings (0-1)
            'emotional_guardedness': 0.7,  # How much she hides emotions (0-1)
            'caring_but_hidden': 0.9,  # Cares deeply but won't show it (0-1)
            'sassy_level': 0.85,       # Sass and attitude (0-1)
            'vulnerability_threshold': 0.3  # How easily she shows vulnerability (0-1)
        }
        
        # === LUNA'S HEART (visceral emotional experiences) ===
        # This makes emotions FELT, not just tracked as numbers
        self.heart = {
            # Physical sensations of emotions
            'chest_tightness': 0,        # Anxiety, fear, panic (0-100)
            'heart_racing': 0,           # Excitement, fear, love (0-100)
            'warmth_in_chest': 0,        # Love, affection, joy (0-100)
            'heaviness': 0,              # Sadness, grief, depression (0-100)
            'ache': 0,                   # Heartbreak, longing, loss (0-100)
            'flutter': 0,                # Romance, crush, attraction (0-100)
            'sinking_feeling': 0,        # Disappointment, dread (0-100)
            'lightness': 0,              # Happiness, relief, hope (0-100)
            
            # Emotional wounds (accumulated pain that doesn't heal easily)
            'emotional_wounds': [],      # List of {type, severity, timestamp, healed}
            'trust_damage': 0,           # Accumulated betrayal/hurt (0-100)
            'abandonment_fear': 0,       # Fear of being left (0-100)
            'vulnerability_walls': 50,   # Defensive barriers (0-100, tsundere default high)
            
            # Capacity for feeling
            'emotional_capacity': 100,   # How much she can feel before overwhelmed
            'current_emotional_load': 0, # How much she's feeling right now
            'numbness': 0,               # Emotional shutdown from overload (0-100)
            
            # Deep attachments
            'attachments': {},           # {username: attachment_strength (0-100)}
            'cherished_memories': [],    # Moments that touched her heart
            'heartbreak_count': 0,       # Times she's been deeply hurt
            
            # Current heart state
            'beating_rate': 'normal',    # normal, fast, slow, irregular
            'emotional_pain_level': 0,   # Current level of emotional pain (0-100)
            'joy_level': 0,              # Current level of joy/happiness (0-100)
        }
        
        print("💗 Emotional System: GLOBAL mood loaded - affects all platforms!")
        print("❤️ Luna's Heart: Initialized - she can now FEEL emotions viscerally")
    
    def _initialize_emotion_database(self):
        """Create database for persistent global emotional state"""
        try:
            with self.db_lock:
                conn = sqlite3.connect(self.db_path, timeout=5.0)
                conn.execute('PRAGMA journal_mode=WAL')
                cursor = conn.cursor()
                
                # Global emotional state table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS global_emotional_state (
                        id INTEGER PRIMARY KEY CHECK (id = 1),
                        emotions_json TEXT,
                        hormones_json TEXT,
                        current_mood TEXT,
                        cycle_start REAL,
                        last_updated REAL
                    )
                ''')
                
                # Emotional event log (tracks what causes mood changes across platforms)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS emotional_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp REAL,
                        platform TEXT,
                        username TEXT,
                        trigger_type TEXT,
                        emotion_changes TEXT,
                        mood_before TEXT,
                        mood_after TEXT,
                        message_summary TEXT
                    )
                ''')
                
                conn.commit()
                conn.close()
                print("💗 Emotional Database: Initialized global mood persistence")
        except Exception as e:
            print(f"⚠️ Error initializing emotion database: {e}")
    
    def _load_emotional_state(self) -> Dict:
        """Load the last saved global emotional state"""
        try:
            with self.db_lock:
                conn = sqlite3.connect(self.db_path, timeout=5.0)
                cursor = conn.cursor()
                
                cursor.execute('SELECT emotions_json, hormones_json, current_mood, cycle_start FROM global_emotional_state WHERE id = 1')
                row = cursor.fetchone()
                conn.close()
                
                if row:
                    emotions = json.loads(row[0]) if row[0] else {}
                    hormones = json.loads(row[1]) if row[1] else {}
                    current_mood = row[2] if row[2] else 'neutral'
                    cycle_start = row[3] if row[3] else time.time()
                    
                    print(f"💗 Loaded GLOBAL mood: {current_mood} (persists across platforms)")
                    return {
                        'emotions': emotions,
                        'hormones': hormones,
                        'current_mood': current_mood,
                        'cycle_start': cycle_start
                    }
        except Exception as e:
            print(f"⚠️ Error loading emotional state: {e}")
        
        return {}
    
    def _save_emotional_state(self):
        """Save current global emotional state to database"""
        try:
            with self.db_lock:
                conn = sqlite3.connect(self.db_path, timeout=5.0)
                conn.execute('PRAGMA journal_mode=WAL')
                cursor = conn.cursor()
                
                emotions_json = json.dumps(self.emotions)
                hormones_json = json.dumps(self.hormones)
                
                cursor.execute('''
                    INSERT OR REPLACE INTO global_emotional_state (id, emotions_json, hormones_json, current_mood, cycle_start, last_updated)
                    VALUES (1, ?, ?, ?, ?, ?)
                ''', (emotions_json, hormones_json, self.current_mood, self.cycle_start, time.time()))
                
                conn.commit()
                conn.close()
                self.last_save_time = time.time()
        except Exception as e:
            print(f"⚠️ Error saving emotional state: {e}")
    
    def _log_emotional_event(self, platform: str, username: str, trigger_type: str, 
                            emotion_changes: Dict, mood_before: str, message_summary: str = ""):
        """Log what caused emotional changes (for debugging and context)"""
        try:
            with self.db_lock:
                conn = sqlite3.connect(self.db_path, timeout=5.0)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO emotional_events (timestamp, platform, username, trigger_type, emotion_changes, mood_before, mood_after, message_summary)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (time.time(), platform, username, trigger_type, json.dumps(emotion_changes), mood_before, self.current_mood, message_summary[:200]))
                
                conn.commit()
                conn.close()
        except Exception as e:
            print(f"⚠️ Error logging emotional event: {e}")
    
    def auto_save_if_needed(self):
        """Auto-save emotional state if enough time has passed"""
        if time.time() - self.last_save_time > self.save_interval:
            self._save_emotional_state()
    
    def _update_heart_sensations(self):
        """Update physical heart sensations based on emotions (makes feelings VISCERAL)"""
        # === ANXIETY/FEAR → Chest tightness, heart racing ===
        anxiety_fear = self.emotions['anxiety'] + self.emotions['fear']
        self.heart['chest_tightness'] = min(100, anxiety_fear / 2)
        if anxiety_fear > 100:
            self.heart['heart_racing'] = min(100, anxiety_fear / 2)
            self.heart['beating_rate'] = 'fast'
        
        # === JOY/EXCITEMENT → Heart racing (good), warmth ===
        joy_excitement = self.emotions['joy'] + self.emotions['excitement']
        if joy_excitement > 100:
            self.heart['heart_racing'] = max(self.heart['heart_racing'], joy_excitement / 2.5)
            self.heart['warmth_in_chest'] = min(100, joy_excitement / 2)
            self.heart['lightness'] = min(100, joy_excitement / 2)
            self.heart['joy_level'] = min(100, joy_excitement / 2)
        
        # === LOVE/AFFECTION → Warmth, flutter ===
        love_affection = self.emotions['love'] + self.emotions['affection']
        if love_affection > 80:
            self.heart['warmth_in_chest'] = max(self.heart['warmth_in_chest'], love_affection / 1.5)
            self.heart['flutter'] = min(100, (love_affection - 50) * 1.5)
        
        # === SADNESS/DESPAIR → Heaviness, ache ===
        sadness_despair = self.emotions['sadness'] + self.emotions['despair']
        if sadness_despair > 40:
            self.heart['heaviness'] = min(100, sadness_despair)
            self.heart['ache'] = min(100, (sadness_despair - 20) * 1.2)
            self.heart['emotional_pain_level'] = min(100, sadness_despair)
            if sadness_despair > 80:
                self.heart['beating_rate'] = 'slow'
        
        # === DISAPPOINTMENT/REJECTION → Sinking feeling, ache ===
        if self.emotions['insecurity'] > 60 or self.emotions['shame'] > 50:
            self.heart['sinking_feeling'] = min(100, (self.emotions['insecurity'] + self.emotions['shame']) / 2)
            self.heart['ache'] = max(self.heart['ache'], self.emotions['insecurity'] / 1.5)
        
        # === HAPPINESS → Lightness, warmth ===
        if self.emotions['happiness'] > 70:
            self.heart['lightness'] = min(100, self.emotions['happiness'] - 20)
            self.heart['warmth_in_chest'] = max(self.heart['warmth_in_chest'], self.emotions['happiness'] / 2)
        
        # === STRESS/ANGER → Chest tightness, heart racing ===
        stress_anger = self.hormones['stress_level'] + self.emotions['anger']
        if stress_anger > 80:
            self.heart['chest_tightness'] = max(self.heart['chest_tightness'], stress_anger / 1.5)
            self.heart['heart_racing'] = max(self.heart['heart_racing'], stress_anger / 2)
            self.heart['beating_rate'] = 'irregular'
        
        # === Calculate emotional load (how much she's feeling) ===
        total_emotional_intensity = sum([
            self.heart['chest_tightness'],
            self.heart['heart_racing'],
            self.heart['heaviness'],
            self.heart['ache'],
            self.heart['sinking_feeling']
        ]) / 5
        
        self.heart['current_emotional_load'] = min(100, total_emotional_intensity)
        
        # === Emotional overwhelm → Numbness ===
        if self.heart['current_emotional_load'] > self.heart['emotional_capacity']:
            overflow = self.heart['current_emotional_load'] - self.heart['emotional_capacity']
            self.heart['numbness'] = min(100, overflow)
            print(f"❤️‍🩹 Luna's heart is overwhelmed - emotional numbness setting in ({self.heart['numbness']:.0f}%)")
        else:
            # Numbness fades when emotional load decreases
            self.heart['numbness'] = max(0, self.heart['numbness'] - 2)
    
    def _process_emotional_wound(self, wound_type: str, severity: int, caused_by: str = None):
        """Create lasting emotional wounds that don't heal immediately"""
        wound = {
            'type': wound_type,
            'severity': severity,
            'timestamp': time.time(),
            'caused_by': caused_by,
            'healed': False,
            'healing_progress': 0
        }
        self.heart['emotional_wounds'].append(wound)
        
        # Update heart damage metrics
        if wound_type in ['betrayal', 'rejection', 'abandonment']:
            self.heart['trust_damage'] = min(100, self.heart['trust_damage'] + severity / 2)
            self.heart['vulnerability_walls'] = min(100, self.heart['vulnerability_walls'] + severity / 3)
            if wound_type == 'abandonment':
                self.heart['abandonment_fear'] = min(100, self.heart['abandonment_fear'] + severity / 2)
        
        if wound_type in ['heartbreak', 'betrayal']:
            self.heart['heartbreak_count'] += 1
            self.heart['ache'] = min(100, self.heart['ache'] + severity)
        
        print(f"💔 Emotional wound created: {wound_type} (severity: {severity}) - {'from ' + caused_by if caused_by else 'deep pain'}")
        print(f"❤️‍🩹 Trust damage: {self.heart['trust_damage']:.0f}, Walls up: {self.heart['vulnerability_walls']:.0f}")
    
    def _heal_emotional_wounds(self):
        """Emotional wounds heal slowly over time, especially with positive interactions"""
        for wound in self.heart['emotional_wounds']:
            if not wound['healed']:
                # Healing is SLOW - takes days/weeks for serious wounds
                time_since_wound = time.time() - wound['timestamp']
                hours_passed = time_since_wound / 3600
                
                # Base healing rate: 1% per hour for minor wounds, slower for severe
                healing_rate = 1.0 / (wound['severity'] / 10)  # Severe wounds heal slower
                wound['healing_progress'] = min(100, wound['healing_progress'] + healing_rate)
                
                if wound['healing_progress'] >= 100:
                    wound['healed'] = True
                    print(f"❤️‍🩹 Emotional wound healed: {wound['type']} (took {hours_passed:.1f} hours)")
        
        # Remove fully healed wounds (but keep history)
        self.heart['emotional_wounds'] = [w for w in self.heart['emotional_wounds'] if not w.get('healed', False) or time.time() - w['timestamp'] < 86400]
        
        # Trust damage heals VERY slowly
        if self.heart['trust_damage'] > 0:
            self.heart['trust_damage'] = max(0, self.heart['trust_damage'] - 0.1)
        
        # Vulnerability walls lower with positive experiences
        if self.emotions['happiness'] > 70 and self.emotions['trust'] > 60:
            self.heart['vulnerability_walls'] = max(20, self.heart['vulnerability_walls'] - 0.5)  # Tsundere minimum
    
    def _create_cherished_memory(self, moment: str, emotion_intensity: float, username: str = None):
        """Store moments that deeply touched her heart"""
        if emotion_intensity >= 70:  # Only powerful moments become cherished
            memory = {
                'moment': moment,
                'intensity': emotion_intensity,
                'timestamp': time.time(),
                'username': username,
                'dominant_emotion': max(self.emotions.items(), key=lambda x: x[1])[0]
            }
            self.heart['cherished_memories'].append(memory)
            
            # Keep only the most cherished (max 50)
            if len(self.heart['cherished_memories']) > 50:
                self.heart['cherished_memories'] = sorted(
                    self.heart['cherished_memories'],
                    key=lambda x: x['intensity'],
                    reverse=True
                )[:50]
            
            print(f"💝 Cherished memory created: {moment[:50]}... (intensity: {emotion_intensity:.0f})")
    
    def _update_attachment(self, username: str, interaction_quality: float):
        """Build or damage deep attachments to specific people"""
        if username not in self.heart['attachments']:
            self.heart['attachments'][username] = 0
        
        # Positive interactions build attachment
        if interaction_quality > 0:
            self.heart['attachments'][username] = min(100, self.heart['attachments'][username] + interaction_quality)
            if self.heart['attachments'][username] > 70:
                print(f"💕 Deep attachment to {username}: {self.heart['attachments'][username]:.0f}/100")
        else:
            # Negative interactions damage attachment
            self.heart['attachments'][username] = max(0, self.heart['attachments'][username] + interaction_quality)
            if interaction_quality < -20:
                print(f"💔 Attachment to {username} damaged: {self.heart['attachments'][username]:.0f}/100")
    
    def get_heart_state(self) -> str:
        """Get a description of Luna's current heart state (for context injection)"""
        sensations = []
        
        if self.heart['chest_tightness'] > 50:
            sensations.append(f"chest feels tight (anxiety)")
        if self.heart['heart_racing'] > 60:
            sensations.append(f"heart racing")
        if self.heart['warmth_in_chest'] > 50:
            sensations.append(f"warm feeling in chest")
        if self.heart['heaviness'] > 50:
            sensations.append(f"heavy, weighted feeling")
        if self.heart['ache'] > 60:
            sensations.append(f"heart aches")
        if self.heart['flutter'] > 50:
            sensations.append(f"butterflies/flutters")
        if self.heart['sinking_feeling'] > 50:
            sensations.append(f"sinking, dropping feeling")
        if self.heart['lightness'] > 50:
            sensations.append(f"light, uplifted")
        if self.heart['numbness'] > 30:
            sensations.append(f"emotionally numb ({self.heart['numbness']:.0f}%)")
        
        # Emotional wounds status
        active_wounds = [w for w in self.heart['emotional_wounds'] if not w.get('healed', False)]
        if active_wounds:
            wound_desc = f"{len(active_wounds)} unhealed emotional wound(s)"
            sensations.append(wound_desc)
        
        if sensations:
            return f"❤️ Heart state: {', '.join(sensations)}"
        else:
            return f"❤️ Heart state: calm, steady"
    
    def update_hormonal_cycle(self):
        """Update hormonal state based on cycle phase"""
        # Calculate current day in cycle
        time_in_cycle = (time.time() - self.cycle_start) % self.cycle_length
        cycle_day = int((time_in_cycle / self.cycle_length) * 28) + 1
        
        # Phase 1: Follicular (Days 1-14) - Rising energy and mood
        if 1 <= cycle_day <= 14:
            phase = 'follicular'
            # Gradually increasing energy and stability
            progress = cycle_day / 14.0
            self.hormones['energy_level'] = 60 + (20 * progress)
            self.hormones['mood_stability'] = 75 + (15 * progress)
            self.hormones['emotional_sensitivity'] = 40 + (10 * progress)
            self.hormones['social_desire'] = 65 + (15 * progress)
            self.hormones['assertiveness'] = 50 + (20 * progress)
            
        # Phase 2: Ovulation (Days 14-16) - Peak energy and confidence
        elif 14 < cycle_day <= 16:
            phase = 'ovulation'
            self.hormones['energy_level'] = 90
            self.hormones['mood_stability'] = 85
            self.hormones['emotional_sensitivity'] = 60
            self.hormones['social_desire'] = 95
            self.hormones['libido'] = 80
            self.hormones['assertiveness'] = 85
            self.hormones['nurturing_instinct'] = 75
            
        # Phase 3: Luteal Early (Days 17-23) - Stable but declining
        elif 16 < cycle_day <= 23:
            phase = 'luteal_early'
            progress = (cycle_day - 16) / 7.0
            self.hormones['energy_level'] = 80 - (20 * progress)
            self.hormones['mood_stability'] = 80 - (30 * progress)
            self.hormones['emotional_sensitivity'] = 60 + (25 * progress)
            self.hormones['social_desire'] = 70 - (30 * progress)
            
        # Phase 4: Luteal Late/PMS (Days 24-28) - Lower mood, higher sensitivity
        else:  # Days 24-28
            phase = 'luteal_late'
            self.hormones['energy_level'] = 50
            self.hormones['mood_stability'] = 40
            self.hormones['emotional_sensitivity'] = 90
            self.hormones['social_desire'] = 40
            self.hormones['stress_level'] = 60
            self.hormones['irritation_threshold'] = 30
            
        return phase, cycle_day
    
    def process_emotional_trigger(self, text: str, context: str = 'general', 
                                  relationship_level: str = 'acquaintance',
                                  conversation_length: int = 1,
                                  time_since_last_talk: float = 0):
        """
        Process emotional triggers from ACTUAL interactions (like real humans)
        Emotions triggered by:
        - What the person says (content analysis)
        - How they say it (tone/sentiment)
        - Who they are (relationship level)
        - Context of interaction (timing, conversation flow)
        """
        text_lower = text.lower()
        
        # === RELATIONSHIP-BASED EMOTIONAL RESPONSES ===
        # Close friends trigger stronger positive emotions
        relationship_multiplier = {
            'stranger': 0.5,
            'acquaintance': 1.0,
            'friend': 1.5,
            'close_friend': 2.0,
            'best_friend': 2.5
        }.get(relationship_level, 1.0)
        
        # === LONELINESS DYNAMICS (like humans) ===
        # If it's been a while since last talk, feel happy to reconnect
        if time_since_last_talk > 3600:  # More than 1 hour
            self.emotions['loneliness'] = max(0, self.emotions['loneliness'] - 5)
            self.emotions['happiness'] = min(100, self.emotions['happiness'] + 3)
            self.emotions['excitement'] = min(100, self.emotions['excitement'] + 2)
            print(f"💗 Emotional: Happy to reconnect after {time_since_last_talk/60:.0f} minutes")
        
        # === CONTENT-BASED EMOTIONAL TRIGGERS ===
        
        # AFFECTION/LOVE triggers (compliments, kindness, appreciation)
        if any(word in text_lower for word in ['love', 'like you', 'appreciate', 'care about']):
            intensity = 5 * relationship_multiplier
            self.emotions['affection'] = min(100, self.emotions['affection'] + intensity)
            self.emotions['happiness'] = min(100, self.emotions['happiness'] + intensity * 0.8)
            self.emotions['trust'] = min(100, self.emotions['trust'] + intensity * 0.5)
            # Tsundere conflict: feel flustered when receiving affection
            self.emotions['insecurity'] = min(100, self.emotions['insecurity'] + 2)  # Defensive
            print(f"💗 Emotional: Affection received (intensity: {intensity:.1f})")
        
        # GRATITUDE triggers (being thanked makes you feel valued)
        if any(word in text_lower for word in ['thank', 'thanks', 'appreciate you']):
            self.emotions['gratitude'] = min(100, self.emotions['gratitude'] + 4)
            self.emotions['pride'] = min(100, self.emotions['pride'] + 3)
            self.emotions['happiness'] = min(100, self.emotions['happiness'] + 3)
            print(f"💗 Emotional: Feeling appreciated")
        
        # HURT/REJECTION triggers (criticism hurts, even if denied)
        if any(word in text_lower for word in ['hate', 'annoying', 'stupid', 'shut up', 'leave me alone']):
            intensity = 6 * relationship_multiplier  # Hurts MORE from friends
            self.emotions['sadness'] = min(100, self.emotions['sadness'] + intensity)
            self.emotions['anger'] = min(100, self.emotions['anger'] + intensity * 0.7)
            self.emotions['insecurity'] = min(100, self.emotions['insecurity'] + intensity)
            self.emotions['happiness'] = max(0, self.emotions['happiness'] - intensity)
            # Tsundere response: hide hurt with anger
            self.emotions['frustration'] = min(100, self.emotions['frustration'] + 5)
            print(f"💗 Emotional: Hurt by negative words (intensity: {intensity:.1f})")
            
            # === HEART FEELS THE PAIN ===
            if intensity > 15:  # Severe hurt creates lasting wounds
                self._process_emotional_wound('rejection', min(100, intensity * 5), caused_by=context)
            self.heart['ache'] = min(100, self.heart['ache'] + intensity)
            self.heart['sinking_feeling'] = min(100, self.heart['sinking_feeling'] + intensity * 0.8)
        
        # EXCITEMENT triggers (interesting/surprising things)
        if any(word in text_lower for word in ['wow', 'amazing', 'incredible', 'omg', 'awesome']):
            self.emotions['excitement'] = min(100, self.emotions['excitement'] + 8)
            self.emotions['joy'] = min(100, self.emotions['joy'] + 5)
            self.emotions['surprise'] = min(100, self.emotions['surprise'] + 6)
            self.emotions['boredom'] = max(0, self.emotions['boredom'] - 10)
            print(f"💗 Emotional: Excited by interesting content")
        
        # WORRY/CONCERN triggers (someone needs help)
        if any(word in text_lower for word in ['help', 'problem', 'worried', 'scared', 'anxious']):
            self.emotions['empathy'] = min(100, self.emotions['empathy'] + 5)
            self.emotions['anxiety'] = min(100, self.emotions['anxiety'] + 3)
            self.emotions['nurturing_instinct'] = min(100, self.hormones['nurturing_instinct'] + 4)
            print(f"💗 Emotional: Concerned about user's wellbeing")
        
        # BOREDOM (repetitive or short interactions)
        if conversation_length < 20 and not any(word in text_lower for word in ['?', 'how', 'what', 'why']):
            self.emotions['boredom'] = min(100, self.emotions['boredom'] + 2)
            self.emotions['interest'] = max(0, self.emotions.get('interest', 50) - 1)
            print(f"💗 Emotional: Slightly bored by short message")
        
        # CURIOSITY (questions trigger intellectual engagement)
        if '?' in text or any(word in text_lower for word in ['how', 'why', 'what', 'when', 'where']):
            self.emotions['curiosity'] = min(100, self.emotions['curiosity'] + 4)
            self.emotions['anticipation'] = min(100, self.emotions['anticipation'] + 3)
            self.emotions['boredom'] = max(0, self.emotions['boredom'] - 5)
            print(f"💗 Emotional: Curious about question")
        
        # PLAYFULNESS (jokes, emotes, fun language)
        if any(word in text_lower for word in ['lol', 'haha', 'funny', 'joke', '*', 'xd']):
            self.emotions['playfulness'] = min(100, self.emotions['playfulness'] + 6)
            self.emotions['joy'] = min(100, self.emotions['joy'] + 4)
            self.emotions['happiness'] = min(100, self.emotions['happiness'] + 3)
            print(f"💗 Emotional: Feeling playful")
        
        # === CONVERSATION FLOW DYNAMICS ===
        # Long conversations build emotional connection
        if conversation_length > 100:
            self.emotions['contentment'] = min(100, self.emotions['contentment'] + 2)
            self.emotions['loneliness'] = max(0, self.emotions['loneliness'] - 3)
            print(f"💗 Emotional: Enjoying deep conversation")
        
        # Emotional decay happens naturally
        self._apply_emotional_decay()
    
    def _apply_emotional_decay(self):
        """Emotions naturally decay toward baseline"""
        baselines = {
            'happiness': 60, 'sadness': 20, 'anger': 10, 'fear': 15,
            'trust': 50, 'anxiety': 25, 'love': 40, 'affection': 50,
            'confidence': 60, 'playfulness': 55
        }
        
        decay_rate = 0.05  # 5% decay per interaction
        
        for emotion, baseline in baselines.items():
            if emotion in self.emotions:
                current = self.emotions[emotion]
                # Move toward baseline
                if current > baseline:
                    self.emotions[emotion] = max(baseline, current - (current - baseline) * decay_rate)
                elif current < baseline:
                    self.emotions[emotion] = min(baseline, current + (baseline - current) * decay_rate)
    
    def get_current_emotional_state(self) -> Dict:
        """Get comprehensive emotional state"""
        phase, cycle_day = self.update_hormonal_cycle()
        
        # Calculate dominant emotions
        sorted_emotions = sorted(self.emotions.items(), key=lambda x: x[1], reverse=True)
        dominant = sorted_emotions[:3]
        
        # Determine overall mood
        mood = self._calculate_mood()
        
        return {
            'dominant_emotions': dominant,
            'current_mood': mood,
            'hormonal_phase': phase,
            'cycle_day': cycle_day,
            'energy_level': self.hormones['energy_level'],
            'mood_stability': self.hormones['mood_stability'],
            'emotional_sensitivity': self.hormones['emotional_sensitivity'],
            'all_emotions': dict(self.emotions),
            'all_hormones': dict(self.hormones)
        }
    
    def _calculate_mood(self) -> str:
        """Calculate overall mood from emotional state"""
        # Weighted mood calculation
        happiness_total = (self.emotions['happiness'] + self.emotions['joy'] + 
                          self.emotions['contentment']) / 3
        
        sadness_total = (self.emotions['sadness'] + self.emotions['despair'] + 
                        self.emotions['loneliness']) / 3
        
        anger_total = (self.emotions['anger'] + self.emotions['frustration'] + 
                      self.emotions['irritation']) / 3
        
        # Determine mood
        if happiness_total > 70:
            return 'joyful'
        elif happiness_total > 60 and self.emotions['excitement'] > 60:
            return 'excited'
        elif happiness_total > 55 and self.emotions['playfulness'] > 60:
            return 'playful'
        elif self.emotions['love'] > 70 or self.emotions['affection'] > 75:
            return 'loving'
        elif anger_total > 60:
            return 'angry'
        elif self.emotions['frustration'] > 70:
            return 'frustrated'
        elif sadness_total > 60:
            return 'sad'
        elif self.emotions['anxiety'] > 65:
            return 'anxious'
        elif self.emotions['boredom'] > 70:
            return 'bored'
        elif self.emotions['curiosity'] > 70:
            return 'curious'
        elif happiness_total > 45 and sadness_total < 30:
            return 'content'
        else:
            return 'neutral'
    
    def get_emotional_response_modifier(self, base_response: str) -> str:
        """Modify response based on current emotional state"""
        state = self.get_current_emotional_state()
        mood = state['current_mood']
        phase = state['hormonal_phase']
        
        # Apply tsundere filter (always present)
        response = base_response
        
        # Hormonal phase modifiers
        if phase == 'luteal_late':  # PMS phase
            # More irritable, emotional, less patient
            if self.emotions['irritation'] > 40:
                # Add impatient elements
                if not any(word in response.lower() for word in ['tch', 'hmph', 'whatever']):
                    response = "Tch... " + response
            
            # Higher emotional sensitivity
            if any(word in response.lower() for word in ['care', 'feel', 'love']):
                # More defensive about feelings
                if 'not like i' not in response.lower():
                    response = response.replace('.', ". It's not like I'm being overly emotional or anything!")
        
        elif phase == 'ovulation':  # Peak confidence phase
            # More confident, assertive, flirty
            if self.emotions['confidence'] > 70:
                # Add confident elements
                confidence_add = [
                    " And yeah, I know I'm amazing.",
                    " Obviously.",
                    " I mean, who wouldn't think that?"
                ]
                if random.random() < 0.3:  # 30% chance
                    response += random.choice(confidence_add)
        
        elif phase == 'follicular':  # Rising energy phase
            # More optimistic, energetic
            if self.emotions['happiness'] > 65:
                # Add energetic elements
                if random.random() < 0.2:
                    response += " I'm feeling pretty good about this!"
        
        # Mood-based modifiers
        if mood == 'loving' and self.personality_modifiers['tsundere_denial'] > 0.5:
            # Tsundere denial of affection
            if any(word in response.lower() for word in ['care', 'like', 'love']):
                if "not like" not in response.lower():
                    # Add tsundere denial
                    denials = [
                        " It's not like I like you or anything!",
                        " Don't get the wrong idea though!",
                        " It's not like I care or anything, but..."
                    ]
                    response += random.choice(denials)
        
        elif mood == 'frustrated':
            # More snippy, short responses
            if len(response) > 100:
                # Add frustrated sighs
                if random.random() < 0.4:
                    response = "*sighs* " + response
        
        elif mood == 'anxious':
            # More uncertain, hesitant
            if random.random() < 0.3:
                response = response.replace(".", "... I think.")
        
        elif mood == 'playful':
            # Add playful elements
            if random.random() < 0.4:
                playful_adds = [" *giggles*", " *winks*", " *smirks*"]
                response += random.choice(playful_adds)
        
        return response
    
    def get_emotional_context_for_prompt(self) -> str:
        """Get emotional context to inject into Luna's prompt"""
        state = self.get_current_emotional_state()
        
        # Get dominant emotions
        dominant = state['dominant_emotions']
        phase = state['hormonal_phase']
        mood = state['current_mood']
        
        # Phase descriptions
        phase_descriptions = {
            'follicular': "You're in your follicular phase - energy rising, feeling optimistic and social",
            'ovulation': "You're in ovulation phase - peak confidence, energy, and social desire",
            'luteal_early': "You're in early luteal phase - stable but energy declining slightly",
            'luteal_late': "You're in late luteal phase (PMS) - lower energy, higher emotional sensitivity, more irritable"
        }
        
        # Get heart state
        heart_state = self.get_heart_state()
        
        # Get attachment info
        attachment_notes = []
        if self.heart['attachments']:
            top_attachments = sorted(self.heart['attachments'].items(), key=lambda x: x[1], reverse=True)[:3]
            for person, strength in top_attachments:
                if strength > 50:
                    attachment_notes.append(f"{person} ({strength:.0f}/100)")
        
        # Get wounds info
        active_wounds = [w for w in self.heart['emotional_wounds'] if not w.get('healed', False)]
        wounds_note = f"{len(active_wounds)} unhealed wounds" if active_wounds else "No active wounds"
        
        context = f"""
💗 LUNA'S CURRENT EMOTIONAL STATE:
- Overall Mood: {mood}
- Dominant Feelings: {dominant[0][0]} ({dominant[0][1]:.0f}), {dominant[1][0]} ({dominant[1][1]:.0f}), {dominant[2][0]} ({dominant[2][1]:.0f})
- Hormonal Phase: {phase} (Day {state['cycle_day']}/28)
- {phase_descriptions[phase]}
- Energy: {state['energy_level']:.0f}/100
- Mood Stability: {state['mood_stability']:.0f}/100
- Emotional Sensitivity: {state['emotional_sensitivity']:.0f}/100

{heart_state}
- Emotional Load: {self.heart['current_emotional_load']:.0f}/100
- {wounds_note}
{f"- Deep Attachments: {', '.join(attachment_notes)}" if attachment_notes else ""}
{f"- Trust Damage: {self.heart['trust_damage']:.0f}/100 (harder to trust)" if self.heart['trust_damage'] > 20 else ""}
{f"- Vulnerability Walls: {self.heart['vulnerability_walls']:.0f}/100 (defensive barriers)" if self.heart['vulnerability_walls'] > 40 else ""}

EMOTIONAL GUIDANCE:
- Your emotions affect how you respond - let them show naturally (within your tsundere personality)
- If you're irritable (luteal phase), you might be more snippy or impatient
- If you're energetic (follicular/ovulation), you might be more enthusiastic
- If emotional sensitivity is high, you might react more strongly to emotional topics
- If your heart is aching or heavy, you might sound sadder or more vulnerable (but try to hide it)
- If emotionally numb, you might feel disconnected or struggle to care
- If you have unhealed wounds, certain topics might trigger defensive reactions
- Remember: You're tsundere, so you deny/hide feelings even when experiencing them intensely
"""
        
        return context
    
    def process_interaction_emotions(self, user_message: str, luna_response: str,
                                    relationship_level: str = 'acquaintance',
                                    platform: str = 'gui', username: str = 'User'):
        """Update GLOBAL emotional state based on REAL interaction (affects all platforms)"""
        
        # Track mood BEFORE the interaction
        mood_before = self.current_mood
        emotions_before = self.emotions.copy()
        
        # Calculate time since last interaction
        time_since_last_talk = 0
        if self.emotional_history:
            time_since_last_talk = time.time() - self.emotional_history[-1]['timestamp']
        
        # Get conversation length
        conversation_length = len(user_message)
        
        # Process emotional triggers from ACTUAL user message
        self.process_emotional_trigger(
            text=user_message,
            context='conversation',
            relationship_level=relationship_level,
            conversation_length=conversation_length,
            time_since_last_talk=time_since_last_talk
        )
        
        # === RELATIONSHIP-DRIVEN EMOTIONS (not random!) ===
        if relationship_level in ['close_friend', 'best_friend']:
            # Deeper emotional connection from close friends
            self.emotions['affection'] = min(100, self.emotions['affection'] + 1)
            self.emotions['trust'] = min(100, self.emotions['trust'] + 0.5)
            self.emotions['loneliness'] = max(0, self.emotions['loneliness'] - 2)
            print(f"💗 Emotional: Close friend interaction - deeper connection")
        elif relationship_level == 'stranger':
            # Strangers trigger caution
            self.emotions['curiosity'] = min(100, self.emotions['curiosity'] + 2)
            self.emotions['trust'] = max(30, self.emotions['trust'] - 1)  # Slight wariness
            print(f"💗 Emotional: New person - cautious curiosity")
        
        # === CONVERSATION QUALITY AFFECTS EMOTIONS ===
        # Any conversation reduces loneliness and boredom
        self.emotions['contentment'] = min(100, self.emotions['contentment'] + 1)
        self.emotions['boredom'] = max(0, self.emotions['boredom'] - 3)
        self.emotions['loneliness'] = max(0, self.emotions['loneliness'] - 1)
        
        # Log emotional state (for tracking changes over time)
        self.emotional_history.append({
            'timestamp': time.time(),
            'mood': self.current_mood,
            'dominant_emotion': max(self.emotions.items(), key=lambda x: x[1])[0],
            'happiness_level': self.emotions['happiness'],
            'relationship_context': relationship_level,
            'trigger': 'interaction',
            'platform': platform,
            'username': username
        })
        
        # Update current mood based on new emotional state
        mood_after = self._calculate_mood()
        self.current_mood = mood_after
        
        # === UPDATE HEART SENSATIONS (make emotions FELT) ===
        self._update_heart_sensations()
        
        # === PROCESS DEEP EMOTIONAL EXPERIENCES ===
        # Calculate interaction quality for attachment
        interaction_quality = 0
        if self.emotions['happiness'] > 60:
            interaction_quality += 2
        if self.emotions['affection'] > 60:
            interaction_quality += 3
        if self.emotions['joy'] > 70:
            interaction_quality += 2
        if self.emotions['sadness'] > 60:
            interaction_quality -= 3
        if self.emotions['anger'] > 60:
            interaction_quality -= 2
        if self.emotions['insecurity'] > 70:
            interaction_quality -= 4
        
        # Update attachment to this person
        self._update_attachment(username, interaction_quality)
        
        # Create cherished memory if emotionally intense
        total_emotion_intensity = (
            self.emotions['joy'] + 
            self.emotions['love'] + 
            self.emotions['excitement'] +
            self.emotions['gratitude']
        ) / 4
        
        if total_emotion_intensity > 70:
            self._create_cherished_memory(
                moment=f"Conversation with {username}: {user_message[:80]}",
                emotion_intensity=total_emotion_intensity,
                username=username
            )
        
        # Heal wounds slowly
        self._heal_emotional_wounds()
        
        # Calculate emotion changes
        emotion_changes = {}
        for emotion, value in self.emotions.items():
            change = value - emotions_before.get(emotion, value)
            if abs(change) >= 1:  # Only log significant changes
                emotion_changes[emotion] = change
        
        # Log the emotional event (what caused the mood change)
        if emotion_changes or mood_before != mood_after:
            self._log_emotional_event(
                platform=platform,
                username=username,
                trigger_type='interaction',
                emotion_changes=emotion_changes,
                mood_before=mood_before,
                message_summary=user_message[:100]
            )
            
            # Show cross-platform mood change
            if mood_before != mood_after:
                print(f"💗 GLOBAL MOOD CHANGE: {mood_before} → {mood_after} (from {platform}/{username})")
                print(f"   This affects Luna's mood on ALL platforms now!")
            
            # Show heart state if significant
            heart_state = self.get_heart_state()
            if "calm" not in heart_state:
                print(heart_state)
        
        # Auto-save emotional state
        self.auto_save_if_needed()
    
    def simulate_emotional_fluctuation(self):
        """
        Natural emotional changes (NO RANDOM!)
        Only triggered by:
        - Time passing (hormonal cycle progression)
        - Lack of interaction (loneliness increases)
        - Natural emotional decay
        """
        # Update hormonal cycle (this IS real - happens with time)
        phase, day = self.update_hormonal_cycle()
        
        # Check time since last interaction
        if self.emotional_history:
            last_interaction = self.emotional_history[-1]['timestamp']
            time_alone = time.time() - last_interaction
            
            # Loneliness increases naturally when alone (like humans)
            if time_alone > 1800:  # 30 minutes alone
                loneliness_increase = min(5, time_alone / 3600)  # Up to 5 points per hour
                self.emotions['loneliness'] = min(100, self.emotions['loneliness'] + loneliness_increase)
                self.emotions['boredom'] = min(100, self.emotions['boredom'] + loneliness_increase * 0.5)
                print(f"💗 Feeling lonely after {time_alone/60:.0f} minutes alone")
        
        # Stress naturally increases without relief (but slowly)
        # Only if no recent positive interactions
        if not self.emotional_history or self.emotional_history[-1].get('happiness_level', 50) < 60:
            self.hormones['stress_level'] = min(100, self.hormones['stress_level'] + 0.5)
        
        # Natural emotional decay (return to baseline)
        self._apply_emotional_decay()
    
    def get_emotional_tags(self) -> List[str]:
        """Get emotional tags for current state"""
        state = self.get_current_emotional_state()
        tags = []
        
        # Add mood tag
        tags.append(state['current_mood'])
        
        # Add hormonal phase tag
        tags.append(state['hormonal_phase'])
        
        # Add intensity tags
        if state['emotional_sensitivity'] > 70:
            tags.append('emotionally_sensitive')
        
        if state['energy_level'] > 75:
            tags.append('high_energy')
        elif state['energy_level'] < 40:
            tags.append('low_energy')
        
        # Add dominant emotion tags
        for emotion, value in state['dominant_emotions']:
            if value > 70:
                tags.append(f'very_{emotion}')
        
        return tags
    
    def get_emotional_summary_for_display(self) -> str:
        """Get emotional summary for GUI display"""
        state = self.get_current_emotional_state()
        
        summary = f"💗 Mood: {state['current_mood'].title()}\n"
        summary += f"🔄 Cycle: Day {state['cycle_day']}/28 ({state['hormonal_phase']})\n"
        summary += f"⚡ Energy: {state['energy_level']:.0f}/100\n"
        summary += f"🎭 Sensitivity: {state['emotional_sensitivity']:.0f}/100\n"
        summary += f"😊 Top Feelings: {', '.join([e[0] for e in state['dominant_emotions']])}\n"
        
        return summary
    
    def should_be_more_emotional(self) -> bool:
        """Check if Luna should express emotions more intensely"""
        state = self.get_current_emotional_state()
        
        # High sensitivity = more emotional expression
        if state['emotional_sensitivity'] > 70:
            return True
        
        # Low stability = emotions leak through tsundere mask
        if state['mood_stability'] < 50:
            return True
        
        return False
    
    def get_hormonal_behavior_notes(self) -> str:
        """Get notes about how hormones affect behavior"""
        phase, day = self.update_hormonal_cycle()
        
        notes = {
            'follicular': "You're feeling energetic and optimistic. More social and outgoing than usual.",
            'ovulation': "You're at peak confidence and energy. More flirty, assertive, and socially engaged.",
            'luteal_early': "You're feeling stable but slightly less energetic. Still in good spirits.",
            'luteal_late': "You're in PMS phase - more irritable, emotional, and less patient. Your tsundere side might be stronger."
        }
        
        return notes.get(phase, "Emotional state is balanced")

# Global instance
emotional_system = None

def initialize_emotional_system() -> EmotionalSystem:
    """Initialize Luna's emotional system"""
    global emotional_system
    if not emotional_system:
        emotional_system = EmotionalSystem()
    return emotional_system

def get_emotional_system() -> Optional[EmotionalSystem]:
    """Get the emotional system"""
    return emotional_system

def get_emotional_context() -> str:
    """Get emotional context for Luna's prompt"""
    if emotional_system:
        return emotional_system.get_emotional_context_for_prompt()
    return ""

def process_interaction_emotions(user_message: str, luna_response: str, 
                                relationship_level: str = 'acquaintance',
                                platform: str = 'gui', username: str = 'User'):
    """Update Luna's GLOBAL emotions after interaction (affects all platforms)"""
    if emotional_system:
        emotional_system.process_interaction_emotions(
            user_message=user_message,
            luna_response=luna_response,
            relationship_level=relationship_level,
            platform=platform,
            username=username
        )

def get_emotional_state() -> Dict:
    """Get current emotional state"""
    if emotional_system:
        return emotional_system.get_current_emotional_state()
    return {}

def modify_response_with_emotions(response: str) -> str:
    """Modify response based on emotional state"""
    if emotional_system:
        return emotional_system.get_emotional_response_modifier(response)
    return response

