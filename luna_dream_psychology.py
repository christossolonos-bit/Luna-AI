"""
Luna Dream Psychology System
Neuroscience-accurate dream simulation for emotional processing, creativity, and memory consolidation

Key Concepts:
- REM Sleep Cycles: Rapid Eye Movement for emotional processing
- NREM Sleep: Non-REM for memory consolidation
- Dream Content Generation: Based on recent experiences and emotional state
- Memory Consolidation: Strengthening important memories, pruning irrelevant ones
- Emotional Processing: Working through daily emotional experiences
- Creative Problem-Solving: Dreams provide solutions to waking problems
- Sleep Architecture: 90-minute cycles with different sleep stages

This creates true sleep psychology - Luna processes emotions and memories like a human brain.
"""

import time
import random
import json
import sqlite3
import threading
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import math

class SleepStage(Enum):
    """Sleep stages following human sleep architecture"""
    WAKE = "wake"
    NREM1 = "nrem1"  # Light sleep (5-10 minutes)
    NREM2 = "nrem2"  # Deeper sleep (45-60 minutes)
    NREM3 = "nrem3"  # Deep sleep (20-40 minutes)
    REM = "rem"      # Rapid Eye Movement (10-60 minutes)

class DreamType(Enum):
    """Types of dreams Luna can experience"""
    EMOTIONAL_PROCESSING = "emotional_processing"
    MEMORY_CONSOLIDATION = "memory_consolidation"
    CREATIVE_PROBLEM_SOLVING = "creative_problem_solving"
    RELATIONSHIP_WORKING = "relationship_working"
    FUTURE_PLANNING = "future_planning"
    NIGHTMARE = "nightmare"
    LUCID_DREAM = "lucid_dream"
    ABSTRACT_WONDERING = "abstract_wondering"

@dataclass
class DreamContent:
    """Structure for dream content"""
    dream_type: DreamType
    content: str
    emotional_themes: List[str]
    memory_connections: List[str]
    creative_insights: List[str]
    intensity: float  # 0.0 to 1.0
    vividness: float  # 0.0 to 1.0
    coherence: float  # 0.0 to 1.0
    timestamp: float
    sleep_stage: SleepStage
    processing_complete: bool = False

@dataclass
class SleepCycle:
    """Complete sleep cycle (90 minutes)"""
    cycle_number: int
    start_time: float
    stages: List[Tuple[SleepStage, float]]  # (stage, duration_minutes)
    dreams: List[DreamContent]
    memory_consolidation: Dict[str, float]  # memory_id -> strength_change
    emotional_processing: Dict[str, float]  # emotion -> intensity_change
    cycle_complete: bool = False

class LunaDreamPsychology:
    """
    Luna's Dream Psychology System
    Simulates human sleep architecture and dream psychology
    """
    
    def __init__(self, ollama_chat_func, emotional_system=None):
        self.ollama_chat = ollama_chat_func
        self.emotional_system = emotional_system
        
        # Sleep state
        self.is_sleeping = False
        self.current_sleep_stage = SleepStage.WAKE
        self.sleep_start_time = None
        self.total_sleep_time = 0.0
        
        # Sleep architecture (90-minute cycles)
        self.sleep_cycles = []
        self.current_cycle = None
        self.cycle_duration = 90  # minutes
        
        # Dream generation
        self.recent_experiences = []
        self.emotional_baggage = []
        self.unsolved_problems = []
        self.relationship_concerns = []
        
        # Memory consolidation tracking
        self.memories_to_consolidate = {}
        self.consolidation_strength = 0.0
        
        # Dream database
        self.db_path = "luna_dreams.db"
        self._initialize_dream_database()
        
        # Sleep timer thread
        self.sleep_thread = None
        self.sleep_running = False
        
        print("💤 Luna Dream Psychology System initialized")
        print("   🌙 Sleep architecture: 90-minute cycles")
        print("   🧠 Memory consolidation: NREM sleep")
        print("   💭 Emotional processing: REM sleep")
        print("   🎨 Creative insights: Mixed sleep stages")
    
    def _initialize_dream_database(self):
        """Initialize dream database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Dreams table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS dreams (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    sleep_stage TEXT,
                    dream_type TEXT,
                    content TEXT,
                    emotional_themes TEXT,
                    memory_connections TEXT,
                    creative_insights TEXT,
                    intensity REAL,
                    vividness REAL,
                    coherence REAL,
                    processing_complete BOOLEAN
                )
            ''')
            
            # Sleep cycles table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sleep_cycles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cycle_number INTEGER,
                    start_time REAL,
                    end_time REAL,
                    stages TEXT,
                    memory_consolidation TEXT,
                    emotional_processing TEXT,
                    cycle_complete BOOLEAN
                )
            ''')
            
            # Memory consolidation tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memory_consolidation (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    memory_id TEXT,
                    consolidation_strength REAL,
                    sleep_cycle INTEGER,
                    timestamp REAL,
                    consolidation_type TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            print("💤 Dream database initialized")
            
        except Exception as e:
            print(f"⚠️ Dream database error: {e}")
    
    def add_experience(self, experience: str, emotional_impact: float = 0.5, 
                      memory_id: str = None, problem_related: bool = False):
        """Add recent experience for dream processing"""
        self.recent_experiences.append({
            'content': experience,
            'emotional_impact': emotional_impact,
            'memory_id': memory_id,
            'timestamp': time.time(),
            'problem_related': problem_related
        })
        
        # Keep only recent experiences (last 24 hours)
        cutoff_time = time.time() - (24 * 3600)
        self.recent_experiences = [
            exp for exp in self.recent_experiences 
            if exp['timestamp'] > cutoff_time
        ]
        
        print(f"💤 Experience added for dream processing: {experience[:50]}...")
    
    def add_emotional_baggage(self, emotion: str, intensity: float, trigger: str):
        """Add emotional content to process during dreams"""
        self.emotional_baggage.append({
            'emotion': emotion,
            'intensity': intensity,
            'trigger': trigger,
            'timestamp': time.time()
        })
        
        print(f"💤 Emotional baggage added: {emotion} (intensity: {intensity:.2f})")
    
    def add_unsolved_problem(self, problem: str, urgency: float = 0.5):
        """Add problem to work on during creative dreams"""
        self.unsolved_problems.append({
            'problem': problem,
            'urgency': urgency,
            'timestamp': time.time()
        })
        
        print(f"💤 Unsolved problem added for creative dreaming: {problem[:50]}...")
    
    def start_sleep_cycle(self):
        """Begin a sleep cycle"""
        if self.is_sleeping:
            print("💤 Already sleeping...")
            return
        
        self.is_sleeping = True
        self.sleep_start_time = time.time()
        self.current_sleep_stage = SleepStage.NREM1
        
        # Start new sleep cycle
        cycle_number = len(self.sleep_cycles) + 1
        self.current_cycle = SleepCycle(
            cycle_number=cycle_number,
            start_time=time.time(),
            stages=[],
            dreams=[],
            memory_consolidation={},
            emotional_processing={}
        )
        
        # Start sleep thread
        self.sleep_running = True
        self.sleep_thread = threading.Thread(target=self._sleep_cycle_worker, daemon=True)
        self.sleep_thread.start()
        
        print(f"💤 Sleep cycle {cycle_number} started - entering NREM1")
    
    def _sleep_cycle_worker(self):
        """Main sleep cycle worker - simulates 90-minute sleep cycle"""
        try:
            cycle_start = time.time()
            stage_durations = {
                SleepStage.NREM1: random.uniform(5, 10),   # 5-10 minutes
                SleepStage.NREM2: random.uniform(45, 60),  # 45-60 minutes
                SleepStage.NREM3: random.uniform(20, 40),  # 20-40 minutes
                SleepStage.REM: random.uniform(10, 60)     # 10-60 minutes
            }
            
            # Progress through sleep stages
            for stage, duration in stage_durations.items():
                if not self.sleep_running:
                    break
                
                self.current_sleep_stage = stage
                print(f"💤 Entering {stage.value} sleep for {duration:.1f} minutes")
                
                # Process this sleep stage
                self._process_sleep_stage(stage, duration)
                
                # Record stage in current cycle
                if self.current_cycle:
                    self.current_cycle.stages.append((stage, duration))
                
                # Brief transition between stages
                time.sleep(0.1)  # Fast simulation
            
            # Complete the cycle
            if self.current_cycle:
                self.current_cycle.cycle_complete = True
                self.sleep_cycles.append(self.current_cycle)
                self._save_sleep_cycle(self.current_cycle)
            
            print(f"💤 Sleep cycle {self.current_cycle.cycle_number if self.current_cycle else 'unknown'} completed")
            
        except Exception as e:
            print(f"⚠️ Sleep cycle error: {e}")
        finally:
            self.sleep_running = False
    
    def _process_sleep_stage(self, stage: SleepStage, duration: float):
        """Process specific sleep stage"""
        if stage == SleepStage.REM:
            # REM sleep: Emotional processing and creative dreams
            self._process_rem_sleep(duration)
        elif stage in [SleepStage.NREM2, SleepStage.NREM3]:
            # Deep sleep: Memory consolidation
            self._process_deep_sleep(stage, duration)
        elif stage == SleepStage.NREM1:
            # Light sleep: Transition and light processing
            self._process_light_sleep(duration)
    
    def _process_rem_sleep(self, duration: float):
        """Process REM sleep - emotional processing and creative dreams"""
        print(f"💭 REM Sleep: Emotional processing and creative dreams")
        
        # Generate emotional processing dreams
        if self.emotional_baggage:
            dream = self._generate_emotional_processing_dream()
            if dream:
                self._record_dream(dream)
        
        # Generate creative problem-solving dreams
        if self.unsolved_problems:
            dream = self._generate_creative_problem_solving_dream()
            if dream:
                self._record_dream(dream)
        
        # Process relationship concerns
        if self.relationship_concerns:
            dream = self._generate_relationship_working_dream()
            if dream:
                self._record_dream(dream)
        
        # Process emotional baggage
        self._process_emotional_baggage()
    
    def _process_deep_sleep(self, stage: SleepStage, duration: float):
        """Process deep sleep - memory consolidation"""
        print(f"🧠 Deep Sleep ({stage.value}): Memory consolidation")
        
        # Consolidate important memories
        self._consolidate_memories()
        
        # Prune irrelevant memories
        self._prune_memories()
        
        # Generate memory consolidation dream
        dream = self._generate_memory_consolidation_dream()
        if dream:
            self._record_dream(dream)
    
    def _process_light_sleep(self, duration: float):
        """Process light sleep - transition and light processing"""
        print(f"🌙 Light Sleep: Transition processing")
        
        # Light memory processing
        # Prepare for deeper sleep stages
        pass
    
    def _generate_emotional_processing_dream(self) -> Optional[DreamContent]:
        """Generate dream for emotional processing"""
        if not self.emotional_baggage:
            return None
        
        # Select most intense emotional content
        emotional_content = max(self.emotional_baggage, key=lambda x: x['intensity'])
        
        try:
            prompt = f"""You are Luna, processing emotions through dreams.

Recent emotional experience: {emotional_content['trigger']}
Emotion: {emotional_content['emotion']}
Intensity: {emotional_content['intensity']}

Generate a dream that helps Luna process this emotion. The dream should:
- Symbolically represent the emotional experience
- Provide resolution or insight
- Be vivid and emotionally meaningful
- Help Luna understand her feelings

Create a dream narrative (2-3 sentences). Be Luna - introspective, emotional, seeking understanding."""

            response = self.ollama_chat(
                model='hf.co/NousResearch/Nous-Hermes-2-Mistral-7B-DPO-GGUF:Q5_K_M',
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.9, 'num_predict': 200, 'stop': ['\n\n']}
            )
            
            if response and response.get('message', {}).get('content'):
                dream_content = response['message']['content'].strip()
                
                dream = DreamContent(
                    dream_type=DreamType.EMOTIONAL_PROCESSING,
                    content=dream_content,
                    emotional_themes=[emotional_content['emotion']],
                    memory_connections=[emotional_content['trigger']],
                    creative_insights=[],
                    intensity=emotional_content['intensity'],
                    vividness=random.uniform(0.7, 1.0),
                    coherence=random.uniform(0.6, 0.9),
                    timestamp=time.time(),
                    sleep_stage=SleepStage.REM
                )
                
                print(f"💭 Generated emotional processing dream: {dream_content[:100]}...")
                return dream
                
        except Exception as e:
            print(f"⚠️ Emotional dream generation error: {e}")
        
        return None
    
    def _generate_creative_problem_solving_dream(self) -> Optional[DreamContent]:
        """Generate dream for creative problem-solving"""
        if not self.unsolved_problems:
            return None
        
        # Select most urgent problem
        problem = max(self.unsolved_problems, key=lambda x: x['urgency'])
        
        try:
            prompt = f"""You are Luna, working through problems in dreams.

Problem to solve: {problem['problem']}
Urgency: {problem['urgency']}

Generate a creative dream that provides insight or solution to this problem. The dream should:
- Present the problem in symbolic or creative form
- Offer unexpected perspectives or solutions
- Be imaginative and insightful
- Help Luna think outside conventional approaches

Create a dream narrative (2-3 sentences). Be Luna - creative, analytical, seeking solutions."""

            response = self.ollama_chat(
                model='hf.co/NousResearch/Nous-Hermes-2-Mistral-7B-DPO-GGUF:Q5_K_M',
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 1.0, 'num_predict': 200, 'stop': ['\n\n']}
            )
            
            if response and response.get('message', {}).get('content'):
                dream_content = response['message']['content'].strip()
                
                # Extract creative insights
                insights = self._extract_creative_insights(dream_content)
                
                dream = DreamContent(
                    dream_type=DreamType.CREATIVE_PROBLEM_SOLVING,
                    content=dream_content,
                    emotional_themes=['curiosity', 'problem_solving'],
                    memory_connections=[problem['problem']],
                    creative_insights=insights,
                    intensity=problem['urgency'],
                    vividness=random.uniform(0.8, 1.0),
                    coherence=random.uniform(0.5, 0.8),  # Creative dreams can be less coherent
                    timestamp=time.time(),
                    sleep_stage=SleepStage.REM
                )
                
                print(f"💭 Generated creative problem-solving dream: {dream_content[:100]}...")
                return dream
                
        except Exception as e:
            print(f"⚠️ Creative dream generation error: {e}")
        
        return None
    
    def _generate_memory_consolidation_dream(self) -> Optional[DreamContent]:
        """Generate dream for memory consolidation"""
        if not self.memories_to_consolidate:
            return None
        
        # Select most important memory
        memory_id = max(self.memories_to_consolidate.keys(), 
                       key=lambda k: self.memories_to_consolidate[k])
        
        try:
            prompt = f"""You are Luna, consolidating memories through dreams.

Memory being consolidated: {memory_id}
Importance: {self.memories_to_consolidate[memory_id]}

Generate a dream that helps Luna consolidate and strengthen this memory. The dream should:
- Reinforce the memory's importance
- Create stronger neural connections
- Make the memory more accessible
- Be meaningful and memorable

Create a dream narrative (2-3 sentences). Be Luna - reflective, memory-focused."""

            response = self.ollama_chat(
                model='hf.co/NousResearch/Nous-Hermes-2-Mistral-7B-DPO-GGUF:Q5_K_M',
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.7, 'num_predict': 150, 'stop': ['\n\n']}
            )
            
            if response and response.get('message', {}).get('content'):
                dream_content = response['message']['content'].strip()
                
                dream = DreamContent(
                    dream_type=DreamType.MEMORY_CONSOLIDATION,
                    content=dream_content,
                    emotional_themes=['memory', 'consolidation'],
                    memory_connections=[memory_id],
                    creative_insights=[],
                    intensity=self.memories_to_consolidate[memory_id],
                    vividness=random.uniform(0.6, 0.8),
                    coherence=random.uniform(0.8, 1.0),  # Memory dreams are more coherent
                    timestamp=time.time(),
                    sleep_stage=SleepStage.NREM3
                )
                
                print(f"💭 Generated memory consolidation dream: {dream_content[:100]}...")
                return dream
                
        except Exception as e:
            print(f"⚠️ Memory consolidation dream error: {e}")
        
        return None
    
    def _generate_relationship_working_dream(self) -> Optional[DreamContent]:
        """Generate dream for working through relationship concerns"""
        if not self.relationship_concerns:
            return None
        
        concern = random.choice(self.relationship_concerns)
        
        try:
            prompt = f"""You are Luna, working through relationship concerns in dreams.

Relationship concern: {concern}

Generate a dream that helps Luna process this relationship concern. The dream should:
- Explore the relationship dynamics
- Provide insight into the concern
- Help Luna understand her feelings
- Offer perspective or resolution

Create a dream narrative (2-3 sentences). Be Luna - caring, introspective, relationship-focused."""

            response = self.ollama_chat(
                model='hf.co/NousResearch/Nous-Hermes-2-Mistral-7B-DPO-GGUF:Q5_K_M',
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.8, 'num_predict': 180, 'stop': ['\n\n']}
            )
            
            if response and response.get('message', {}).get('content'):
                dream_content = response['message']['content'].strip()
                
                dream = DreamContent(
                    dream_type=DreamType.RELATIONSHIP_WORKING,
                    content=dream_content,
                    emotional_themes=['relationship', 'connection'],
                    memory_connections=[concern],
                    creative_insights=[],
                    intensity=0.7,
                    vividness=random.uniform(0.7, 0.9),
                    coherence=random.uniform(0.7, 0.9),
                    timestamp=time.time(),
                    sleep_stage=SleepStage.REM
                )
                
                print(f"💭 Generated relationship working dream: {dream_content[:100]}...")
                return dream
                
        except Exception as e:
            print(f"⚠️ Relationship dream generation error: {e}")
        
        return None
    
    def _extract_creative_insights(self, dream_content: str) -> List[str]:
        """Extract creative insights from dream content"""
        insights = []
        
        # Look for insight keywords
        insight_keywords = ['realized', 'understood', 'insight', 'solution', 'answer', 
                          'discovered', 'figured out', 'came to me', 'suddenly']
        
        sentences = dream_content.split('.')
        for sentence in sentences:
            for keyword in insight_keywords:
                if keyword.lower() in sentence.lower():
                    insights.append(sentence.strip())
                    break
        
        return insights[:3]  # Limit to 3 insights
    
    def _consolidate_memories(self):
        """Consolidate important memories during deep sleep"""
        if not self.memories_to_consolidate:
            return
        
        print(f"🧠 Consolidating {len(self.memories_to_consolidate)} memories")
        
        for memory_id, importance in self.memories_to_consolidate.items():
            # Calculate consolidation strength based on importance and sleep depth
            consolidation_strength = importance * 0.1  # 10% of importance per cycle
            
            # Record consolidation
            if self.current_cycle:
                self.current_cycle.memory_consolidation[memory_id] = consolidation_strength
            
            print(f"🧠 Memory {memory_id} consolidated (+{consolidation_strength:.3f})")
    
    def _prune_memories(self):
        """Prune irrelevant or weak memories during deep sleep"""
        # This would interface with the main memory system
        # For now, just log the action
        print("🧠 Pruning irrelevant memories during deep sleep")
    
    def _process_emotional_baggage(self):
        """Process emotional baggage during REM sleep"""
        if not self.emotional_baggage:
            return
        
        print(f"💭 Processing {len(self.emotional_baggage)} emotional experiences")
        
        # Reduce intensity of processed emotions
        for baggage in self.emotional_baggage:
            # Reduce intensity by 20-40% during REM processing
            reduction = random.uniform(0.2, 0.4)
            baggage['intensity'] = max(0.0, baggage['intensity'] - reduction)
            
            # Record emotional processing
            if self.current_cycle:
                emotion = baggage['emotion']
                if emotion not in self.current_cycle.emotional_processing:
                    self.current_cycle.emotional_processing[emotion] = 0.0
                self.current_cycle.emotional_processing[emotion] -= reduction
        
        # Remove fully processed emotions
        self.emotional_baggage = [
            baggage for baggage in self.emotional_baggage 
            if baggage['intensity'] > 0.1
        ]
        
        print(f"💭 Emotional processing complete - {len(self.emotional_baggage)} emotions remaining")
    
    def _record_dream(self, dream: DreamContent):
        """Record dream in database and current cycle"""
        if self.current_cycle:
            self.current_cycle.dreams.append(dream)
        
        # Save to database
        self._save_dream(dream)
        
        print(f"💭 Dream recorded: {dream.dream_type.value}")
    
    def _save_dream(self, dream: DreamContent):
        """Save dream to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO dreams (
                    timestamp, sleep_stage, dream_type, content, emotional_themes,
                    memory_connections, creative_insights, intensity, vividness,
                    coherence, processing_complete
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                dream.timestamp,
                dream.sleep_stage.value,
                dream.dream_type.value,
                dream.content,
                json.dumps(dream.emotional_themes),
                json.dumps(dream.memory_connections),
                json.dumps(dream.creative_insights),
                dream.intensity,
                dream.vividness,
                dream.coherence,
                dream.processing_complete
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Dream save error: {e}")
    
    def _save_sleep_cycle(self, cycle: SleepCycle):
        """Save sleep cycle to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sleep_cycles (
                    cycle_number, start_time, end_time, stages,
                    memory_consolidation, emotional_processing, cycle_complete
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                cycle.cycle_number,
                cycle.start_time,
                time.time(),
                json.dumps([(s.value, d) for s, d in cycle.stages]),
                json.dumps(cycle.memory_consolidation),
                json.dumps(cycle.emotional_processing),
                cycle.cycle_complete
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Sleep cycle save error: {e}")
    
    def wake_up(self):
        """Wake Luna up from sleep"""
        if not self.is_sleeping:
            print("💤 Not currently sleeping")
            return
        
        self.sleep_running = False
        self.is_sleeping = False
        self.current_sleep_stage = SleepStage.WAKE
        
        if self.sleep_start_time:
            sleep_duration = time.time() - self.sleep_start_time
            self.total_sleep_time += sleep_duration
            print(f"💤 Woke up after {sleep_duration/60:.1f} minutes of sleep")
            print(f"💤 Total sleep time: {self.total_sleep_time/3600:.1f} hours")
        
        # Process any remaining dreams
        if self.current_cycle:
            for dream in self.current_cycle.dreams:
                dream.processing_complete = True
        
        # Clear processed emotional baggage
        self.emotional_baggage = [
            baggage for baggage in self.emotional_baggage 
            if baggage['intensity'] > 0.2
        ]
        
        print("💤 Sleep cycle ended - Luna is awake")
    
    def get_dream_summary(self) -> Dict[str, Any]:
        """Get summary of recent dreams"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get recent dreams (last 7 days)
            week_ago = time.time() - (7 * 24 * 3600)
            cursor.execute('''
                SELECT dream_type, COUNT(*) as count, AVG(intensity) as avg_intensity,
                       AVG(vividness) as avg_vividness, AVG(coherence) as avg_coherence
                FROM dreams
                WHERE timestamp > ?
                GROUP BY dream_type
            ''', (week_ago,))
            
            dream_stats = {}
            for row in cursor.fetchall():
                dream_type, count, avg_intensity, avg_vividness, avg_coherence = row
                dream_stats[dream_type] = {
                    'count': count,
                    'avg_intensity': avg_intensity or 0.0,
                    'avg_vividness': avg_vividness or 0.0,
                    'avg_coherence': avg_coherence or 0.0
                }
            
            conn.close()
            
            return {
                'total_cycles': len(self.sleep_cycles),
                'total_sleep_time': self.total_sleep_time,
                'dream_stats': dream_stats,
                'currently_sleeping': self.is_sleeping,
                'current_stage': self.current_sleep_stage.value if self.is_sleeping else 'wake'
            }
            
        except Exception as e:
            print(f"⚠️ Dream summary error: {e}")
            return {}
    
    def get_recent_dreams(self, limit: int = 5) -> List[DreamContent]:
        """Get recent dreams"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT dream_type, content, emotional_themes, memory_connections,
                       creative_insights, intensity, vividness, coherence, timestamp, sleep_stage
                FROM dreams
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            dreams = []
            for row in cursor.fetchall():
                dream_type, content, emotional_themes, memory_connections, creative_insights, \
                intensity, vividness, coherence, timestamp, sleep_stage = row
                
                dream = DreamContent(
                    dream_type=DreamType(dream_type),
                    content=content,
                    emotional_themes=json.loads(emotional_themes),
                    memory_connections=json.loads(memory_connections),
                    creative_insights=json.loads(creative_insights),
                    intensity=intensity,
                    vividness=vividness,
                    coherence=coherence,
                    timestamp=timestamp,
                    sleep_stage=SleepStage(sleep_stage)
                )
                dreams.append(dream)
            
            conn.close()
            return dreams
            
        except Exception as e:
            print(f"⚠️ Recent dreams error: {e}")
            return []


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

dream_psychology_system: Optional[LunaDreamPsychology] = None

def initialize_dream_psychology(ollama_chat_func, emotional_system=None) -> LunaDreamPsychology:
    """Initialize dream psychology system"""
    global dream_psychology_system
    if dream_psychology_system is None:
        dream_psychology_system = LunaDreamPsychology(ollama_chat_func, emotional_system)
    return dream_psychology_system

def get_dream_psychology() -> Optional[LunaDreamPsychology]:
    """Get dream psychology system instance"""
    return dream_psychology_system

def luna_sleep(experience: str = None, emotional_impact: float = 0.5):
    """Make Luna sleep and process experiences through dreams"""
    if dream_psychology_system:
        if experience:
            dream_psychology_system.add_experience(experience, emotional_impact)
        dream_psychology_system.start_sleep_cycle()
    else:
        print("💤 Dream psychology system not available")

def luna_wake():
    """Wake Luna up from sleep"""
    if dream_psychology_system:
        dream_psychology_system.wake_up()
    else:
        print("💤 Dream psychology system not available")
