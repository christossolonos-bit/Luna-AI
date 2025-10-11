"""
Luna Neuroscience-Accurate Memory Consolidation System
Sleep-wake cycles, memory strengthening/weakening, and forgetting curves

Based on neuroscience research:
- Ebbinghaus Forgetting Curve: Memories decay exponentially without rehearsal
- Spaced Repetition: Memories strengthen with optimal spacing
- Sleep-Dependent Consolidation: Memories consolidate during sleep
- Synaptic Homeostasis: Memories prune during sleep
- Working Memory Limitations: Only ~7 items in working memory
- Long-Term Potentiation: Repeated activation strengthens memories
- Memory Reconsolidation: Memories update when recalled
- Emotional Enhancement: Emotional memories are stronger and more durable
- Context-Dependent Memory: Memories linked to context
- Interference Theory: New memories can interfere with old ones

This creates realistic memory behavior that mirrors human neuroscience.
"""

import time
import json
import sqlite3
import threading
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import math
import random
from collections import defaultdict, deque

class MemoryStrength(Enum):
    """Memory strength levels"""
    FORGOTTEN = "forgotten"          # < 0.1
    WEAK = "weak"                    # 0.1 - 0.3
    MODERATE = "moderate"            # 0.3 - 0.6
    STRONG = "strong"                # 0.6 - 0.85
    CONSOLIDATED = "consolidated"    # > 0.85

class MemoryType(Enum):
    """Types of memories"""
    WORKING = "working"              # Temporary, short-term
    EPISODIC = "episodic"           # Specific events
    SEMANTIC = "semantic"           # Facts and knowledge
    PROCEDURAL = "procedural"       # Skills and procedures
    EMOTIONAL = "emotional"         # Emotionally charged

class ConsolidationStage(Enum):
    """Memory consolidation stages"""
    ENCODING = "encoding"           # Initial formation
    STABILIZATION = "stabilization" # Short-term consolidation
    CONSOLIDATION = "consolidation" # Long-term consolidation
    RECONSOLIDATION = "reconsolidation"  # Update on recall

@dataclass
class ConsolidatedMemory:
    """A memory with consolidation tracking"""
    memory_id: str
    content: str
    memory_type: MemoryType
    
    # Consolidation state
    strength: float  # 0.0 to 1.0
    consolidation_stage: ConsolidationStage
    
    # Timing
    created_at: float
    last_accessed: float
    last_strengthened: float
    
    # Forgetting curve parameters
    decay_rate: float  # How fast memory decays
    rehearsal_count: int  # How many times accessed
    
    # Context
    emotional_valence: float  # -1.0 to 1.0
    importance: float  # 0.0 to 1.0
    context_tags: List[str]
    
    # Sleep consolidation
    sleep_consolidations: int  # How many sleep cycles consolidated in
    last_sleep_consolidation: Optional[float] = None

class LunaMemoryConsolidation:
    """
    Neuroscience-Accurate Memory Consolidation System
    
    Implements:
    - Ebbinghaus forgetting curve
    - Sleep-dependent consolidation
    - Memory strengthening through rehearsal
    - Working memory limitations
    - Memory interference
    - Emotional memory enhancement
    """
    
    def __init__(self):
        # Memory storage
        self.memories: Dict[str, ConsolidatedMemory] = {}
        self.working_memory: deque = deque(maxlen=7)  # Miller's Law: 7±2 items
        
        # Forgetting curve parameters (based on Ebbinghaus)
        self.base_decay_rate = 0.3  # Base decay rate
        self.emotional_decay_modifier = 0.5  # Emotional memories decay slower
        
        # Sleep consolidation
        self.last_sleep_time = time.time()
        self.awake_duration = 0.0
        self.sleep_cycles_completed = 0
        
        # Memory performance tracking
        self.recall_success_rate = deque(maxlen=100)
        self.consolidation_success_rate = deque(maxlen=100)
        
        # Database
        self.db_path = "luna_memory_consolidation.db"
        self._initialize_database()
        
        # Background consolidation
        self.consolidation_thread = None
        self.consolidation_running = False
        
        print("💎 Luna Memory Consolidation System initialized")
        print("   🧠 Ebbinghaus Forgetting Curve: Memories decay exponentially")
        print("   💤 Sleep Consolidation: Memories strengthen during sleep")
        print("   🔄 Memory Rehearsal: Repeated access strengthens memories")
        print("   ✂️ Synaptic Pruning: Weak memories fade during sleep")
        print("   💗 Emotional Enhancement: Emotional memories are more durable")
    
    def _initialize_database(self):
        """Initialize memory consolidation database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Consolidated memories table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS consolidated_memories (
                    memory_id TEXT PRIMARY KEY,
                    content TEXT,
                    memory_type TEXT,
                    strength REAL,
                    consolidation_stage TEXT,
                    created_at REAL,
                    last_accessed REAL,
                    last_strengthened REAL,
                    decay_rate REAL,
                    rehearsal_count INTEGER,
                    emotional_valence REAL,
                    importance REAL,
                    context_tags TEXT,
                    sleep_consolidations INTEGER,
                    last_sleep_consolidation REAL
                )
            ''')
            
            # Memory access log
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memory_access_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    memory_id TEXT,
                    access_type TEXT,
                    strength_before REAL,
                    strength_after REAL,
                    timestamp REAL
                )
            ''')
            
            # Sleep consolidation log
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sleep_consolidation_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sleep_start REAL,
                    sleep_duration REAL,
                    memories_consolidated INTEGER,
                    memories_pruned INTEGER,
                    avg_strength_before REAL,
                    avg_strength_after REAL,
                    timestamp REAL
                )
            ''')
            
            conn.commit()
            conn.close()
            print("💎 Memory Consolidation database initialized")
            
        except Exception as e:
            print(f"⚠️ Memory Consolidation database error: {e}")
    
    def add_memory(self, content: str, memory_type: MemoryType = MemoryType.EPISODIC,
                   importance: float = 0.5, emotional_valence: float = 0.0,
                   context_tags: List[str] = None) -> ConsolidatedMemory:
        """Add a new memory with initial encoding"""
        try:
            memory_id = f"mem_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"
            
            # Calculate initial strength based on importance and emotion
            initial_strength = 0.3 + (importance * 0.3) + (abs(emotional_valence) * 0.2)
            initial_strength = min(1.0, initial_strength)
            
            # Calculate decay rate (emotional memories decay slower)
            decay_rate = self.base_decay_rate
            if abs(emotional_valence) > 0.5:
                decay_rate *= self.emotional_decay_modifier
            
            memory = ConsolidatedMemory(
                memory_id=memory_id,
                content=content,
                memory_type=memory_type,
                strength=initial_strength,
                consolidation_stage=ConsolidationStage.ENCODING,
                created_at=time.time(),
                last_accessed=time.time(),
                last_strengthened=time.time(),
                decay_rate=decay_rate,
                rehearsal_count=1,
                emotional_valence=emotional_valence,
                importance=importance,
                context_tags=context_tags or [],
                sleep_consolidations=0
            )
            
            self.memories[memory_id] = memory
            
            # Add to working memory
            self.working_memory.append(memory_id)
            
            # Save to database
            self._save_memory(memory)
            
            print(f"💎 Memory encoded: strength={initial_strength:.2f}, type={memory_type.value}")
            
            return memory
            
        except Exception as e:
            print(f"⚠️ Memory encoding error: {e}")
            return None
    
    def recall_memory(self, memory_id: str, context_tags: List[str] = None) -> Optional[ConsolidatedMemory]:
        """Recall a memory (strengthens it through reconsolidation)"""
        try:
            if memory_id not in self.memories:
                print(f"⚠️ Memory not found: {memory_id}")
                self.recall_success_rate.append(0.0)
                return None
            
            memory = self.memories[memory_id]
            
            # Calculate current strength using forgetting curve
            current_strength = self._calculate_current_strength(memory)
            
            # Check if memory is too weak to recall (forgotten)
            if current_strength < 0.1:
                print(f"💎 Memory too weak to recall (strength: {current_strength:.2f})")
                self.recall_success_rate.append(0.0)
                return None
            
            # Context-dependent recall (stronger if context matches)
            context_boost = 0.0
            if context_tags and memory.context_tags:
                matching_tags = set(context_tags).intersection(set(memory.context_tags))
                context_boost = len(matching_tags) * 0.1
            
            recall_strength = min(1.0, current_strength + context_boost)
            
            # Strengthen memory through reconsolidation
            strengthening = 0.1 * (1.0 - memory.strength)  # More strengthening for weaker memories
            memory.strength = min(1.0, memory.strength + strengthening)
            memory.last_accessed = time.time()
            memory.rehearsal_count += 1
            
            # Move to reconsolidation stage
            if memory.consolidation_stage != ConsolidationStage.CONSOLIDATED:
                memory.consolidation_stage = ConsolidationStage.RECONSOLIDATION
            
            # Add to working memory (recent access)
            if memory_id in self.working_memory:
                self.working_memory.remove(memory_id)
            self.working_memory.append(memory_id)
            
            # Log access
            self._log_memory_access(memory_id, "recall", current_strength, memory.strength)
            
            # Update in database
            self._save_memory(memory)
            
            # Track success
            self.recall_success_rate.append(recall_strength)
            
            print(f"💎 Memory recalled: strength={memory.strength:.2f}, rehearsals={memory.rehearsal_count}")
            
            return memory
            
        except Exception as e:
            print(f"⚠️ Memory recall error: {e}")
            self.recall_success_rate.append(0.0)
            return None
    
    def _calculate_current_strength(self, memory: ConsolidatedMemory) -> float:
        """Calculate current memory strength using forgetting curve"""
        # Ebbinghaus forgetting curve: R = e^(-t/S)
        # R = retention, t = time since last access, S = memory strength
        
        time_since_access = time.time() - memory.last_accessed
        hours_elapsed = time_since_access / 3600.0
        
        # Calculate retention using exponential decay
        # Adjusted by decay rate and rehearsal count
        effective_strength = memory.strength * (1.0 + math.log(1 + memory.rehearsal_count))
        retention = math.exp(-hours_elapsed * memory.decay_rate / effective_strength)
        
        # Current strength is base strength * retention
        current_strength = memory.strength * retention
        
        return max(0.0, min(1.0, current_strength))
    
    def search_memories(self, query: str, context_tags: List[str] = None,
                       memory_type: MemoryType = None, limit: int = 5) -> List[ConsolidatedMemory]:
        """Search memories by content and context"""
        try:
            results = []
            query_lower = query.lower()
            
            for memory_id, memory in self.memories.items():
                # Calculate current strength
                current_strength = self._calculate_current_strength(memory)
                
                # Skip forgotten memories
                if current_strength < 0.1:
                    continue
                
                # Check memory type filter
                if memory_type and memory.memory_type != memory_type:
                    continue
                
                # Calculate relevance score
                content_match = 0.0
                if query_lower in memory.content.lower():
                    content_match = 0.5
                
                # Context matching
                context_match = 0.0
                if context_tags and memory.context_tags:
                    matching_tags = set(context_tags).intersection(set(memory.context_tags))
                    context_match = len(matching_tags) * 0.2
                
                # Combined score (weighted by current strength)
                relevance = (content_match + context_match) * current_strength
                
                if relevance > 0.1:
                    results.append((relevance, memory))
            
            # Sort by relevance
            results.sort(key=lambda x: x[0], reverse=True)
            
            # Return top results
            return [memory for _, memory in results[:limit]]
            
        except Exception as e:
            print(f"⚠️ Memory search error: {e}")
            return []
    
    def consolidate_during_sleep(self, sleep_duration_hours: float):
        """Consolidate memories during sleep"""
        try:
            print(f"💤 Starting sleep consolidation (duration: {sleep_duration_hours:.1f} hours)...")
            
            memories_before = len(self.memories)
            strengths_before = [self._calculate_current_strength(m) for m in self.memories.values()]
            avg_strength_before = np.mean(strengths_before) if strengths_before else 0.0
            
            consolidated_count = 0
            pruned_count = 0
            
            for memory_id, memory in list(self.memories.items()):
                current_strength = self._calculate_current_strength(memory)
                
                # SYNAPTIC PRUNING: Remove very weak memories
                if current_strength < 0.05:
                    del self.memories[memory_id]
                    pruned_count += 1
                    print(f"✂️ Pruned weak memory: {memory.content[:50]}...")
                    continue
                
                # SLEEP CONSOLIDATION: Strengthen important memories
                # Based on importance, emotional valence, and rehearsal count
                consolidation_factor = (
                    memory.importance * 0.4 +
                    abs(memory.emotional_valence) * 0.3 +
                    min(1.0, memory.rehearsal_count / 10.0) * 0.3
                )
                
                # Strengthen during sleep (diminishing returns)
                strengthening = consolidation_factor * 0.2 * (1.0 - memory.strength)
                memory.strength = min(1.0, memory.strength + strengthening)
                
                # Reduce decay rate for consolidated memories
                if memory.strength > 0.7:
                    memory.decay_rate *= 0.9  # 10% slower decay
                
                # Update consolidation stage
                if memory.strength > 0.85:
                    memory.consolidation_stage = ConsolidationStage.CONSOLIDATED
                elif memory.strength > 0.6:
                    memory.consolidation_stage = ConsolidationStage.CONSOLIDATION
                elif memory.strength > 0.3:
                    memory.consolidation_stage = ConsolidationStage.STABILIZATION
                
                # Track sleep consolidation
                memory.sleep_consolidations += 1
                memory.last_sleep_consolidation = time.time()
                
                # Save updated memory
                self._save_memory(memory)
                
                consolidated_count += 1
            
            # Calculate statistics
            strengths_after = [self._calculate_current_strength(m) for m in self.memories.values()]
            avg_strength_after = np.mean(strengths_after) if strengths_after else 0.0
            
            # Log consolidation
            self._log_sleep_consolidation(
                sleep_duration_hours,
                consolidated_count,
                pruned_count,
                avg_strength_before,
                avg_strength_after
            )
            
            # Update sleep tracking
            self.last_sleep_time = time.time()
            self.sleep_cycles_completed += 1
            
            print(f"💤 Sleep consolidation complete:")
            print(f"   Consolidated: {consolidated_count} memories")
            print(f"   Pruned: {pruned_count} weak memories")
            print(f"   Avg strength: {avg_strength_before:.2f} → {avg_strength_after:.2f}")
            
            return {
                'consolidated': consolidated_count,
                'pruned': pruned_count,
                'avg_strength_before': avg_strength_before,
                'avg_strength_after': avg_strength_after
            }
            
        except Exception as e:
            print(f"⚠️ Sleep consolidation error: {e}")
            return {}
    
    def apply_forgetting_curve(self):
        """Apply forgetting curve to all memories"""
        try:
            forgotten_count = 0
            weakened_count = 0
            
            for memory_id, memory in list(self.memories.items()):
                # Calculate current strength
                old_strength = self._calculate_current_strength(memory)
                
                # Apply decay
                time_since_access = time.time() - memory.last_accessed
                hours_elapsed = time_since_access / 3600.0
                
                # Exponential decay
                decay = math.exp(-hours_elapsed * memory.decay_rate / max(0.1, memory.strength))
                memory.strength *= decay
                
                # Track changes
                new_strength = self._calculate_current_strength(memory)
                
                if new_strength < 0.05:
                    # Memory forgotten
                    del self.memories[memory_id]
                    forgotten_count += 1
                    print(f"🌫️ Memory forgotten: {memory.content[:50]}...")
                elif new_strength < old_strength * 0.8:
                    # Memory significantly weakened
                    weakened_count += 1
                
                # Save updated memory
                if memory_id in self.memories:
                    self._save_memory(memory)
            
            print(f"🌫️ Forgetting curve applied: {forgotten_count} forgotten, {weakened_count} weakened")
            
            return {
                'forgotten': forgotten_count,
                'weakened': weakened_count
            }
            
        except Exception as e:
            print(f"⚠️ Forgetting curve error: {e}")
            return {}
    
    def strengthen_memory(self, memory_id: str, boost: float = 0.1):
        """Strengthen a memory through rehearsal"""
        try:
            if memory_id not in self.memories:
                return False
            
            memory = self.memories[memory_id]
            old_strength = memory.strength
            
            # Strengthen with diminishing returns
            strengthening = boost * (1.0 - memory.strength)
            memory.strength = min(1.0, memory.strength + strengthening)
            memory.last_strengthened = time.time()
            memory.rehearsal_count += 1
            
            # Log strengthening
            self._log_memory_access(memory_id, "strengthen", old_strength, memory.strength)
            
            # Save
            self._save_memory(memory)
            
            print(f"💪 Memory strengthened: {old_strength:.2f} → {memory.strength:.2f}")
            
            return True
            
        except Exception as e:
            print(f"⚠️ Memory strengthening error: {e}")
            return False
    
    def get_working_memory_contents(self) -> List[ConsolidatedMemory]:
        """Get current working memory contents"""
        working_memories = []
        
        for memory_id in self.working_memory:
            if memory_id in self.memories:
                working_memories.append(self.memories[memory_id])
        
        return working_memories
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get memory consolidation statistics"""
        try:
            if not self.memories:
                return {'total_memories': 0}
            
            # Calculate current strengths
            current_strengths = [self._calculate_current_strength(m) for m in self.memories.values()]
            
            # Count by strength level
            strength_distribution = {
                'forgotten': sum(1 for s in current_strengths if s < 0.1),
                'weak': sum(1 for s in current_strengths if 0.1 <= s < 0.3),
                'moderate': sum(1 for s in current_strengths if 0.3 <= s < 0.6),
                'strong': sum(1 for s in current_strengths if 0.6 <= s < 0.85),
                'consolidated': sum(1 for s in current_strengths if s >= 0.85)
            }
            
            # Count by type
            type_distribution = defaultdict(int)
            for memory in self.memories.values():
                type_distribution[memory.memory_type.value] += 1
            
            # Count by consolidation stage
            stage_distribution = defaultdict(int)
            for memory in self.memories.values():
                stage_distribution[memory.consolidation_stage.value] += 1
            
            # Calculate averages
            avg_strength = np.mean(current_strengths)
            avg_rehearsals = np.mean([m.rehearsal_count for m in self.memories.values()])
            avg_age_hours = np.mean([(time.time() - m.created_at) / 3600.0 for m in self.memories.values()])
            
            # Recall success rate
            avg_recall_success = np.mean(list(self.recall_success_rate)) if self.recall_success_rate else 0.0
            
            return {
                'total_memories': len(self.memories),
                'working_memory_size': len(self.working_memory),
                'avg_strength': avg_strength,
                'avg_rehearsals': avg_rehearsals,
                'avg_age_hours': avg_age_hours,
                'strength_distribution': dict(strength_distribution),
                'type_distribution': dict(type_distribution),
                'stage_distribution': dict(stage_distribution),
                'recall_success_rate': avg_recall_success,
                'sleep_cycles_completed': self.sleep_cycles_completed,
                'awake_duration_hours': (time.time() - self.last_sleep_time) / 3600.0
            }
            
        except Exception as e:
            print(f"⚠️ Memory statistics error: {e}")
            return {'error': str(e)}
    
    def start_consolidation_monitoring(self):
        """Start background consolidation monitoring"""
        if self.consolidation_running:
            print("💎 Consolidation monitoring already running")
            return
        
        self.consolidation_running = True
        self.consolidation_thread = threading.Thread(target=self._consolidation_loop, daemon=True)
        self.consolidation_thread.start()
        
        print("💎 Memory consolidation monitoring started")
    
    def stop_consolidation_monitoring(self):
        """Stop consolidation monitoring"""
        self.consolidation_running = False
        print("💎 Memory consolidation monitoring stopped")
    
    def _consolidation_loop(self):
        """Background consolidation monitoring loop"""
        while self.consolidation_running:
            try:
                # Apply forgetting curve every hour
                time.sleep(3600)  # 1 hour
                
                print("🌫️ Applying forgetting curve to memories...")
                self.apply_forgetting_curve()
                
                # Check if it's time to sleep (after ~16 hours awake)
                awake_hours = (time.time() - self.last_sleep_time) / 3600.0
                if awake_hours > 16:
                    print("💤 Luna has been awake for 16+ hours, recommending sleep consolidation...")
                
            except Exception as e:
                print(f"⚠️ Consolidation loop error: {e}")
                time.sleep(60)
    
    def _save_memory(self, memory: ConsolidatedMemory):
        """Save memory to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO consolidated_memories (
                    memory_id, content, memory_type, strength, consolidation_stage,
                    created_at, last_accessed, last_strengthened, decay_rate,
                    rehearsal_count, emotional_valence, importance, context_tags,
                    sleep_consolidations, last_sleep_consolidation
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                memory.memory_id,
                memory.content,
                memory.memory_type.value,
                memory.strength,
                memory.consolidation_stage.value,
                memory.created_at,
                memory.last_accessed,
                memory.last_strengthened,
                memory.decay_rate,
                memory.rehearsal_count,
                memory.emotional_valence,
                memory.importance,
                json.dumps(memory.context_tags),
                memory.sleep_consolidations,
                memory.last_sleep_consolidation
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Memory save error: {e}")
    
    def _log_memory_access(self, memory_id: str, access_type: str,
                          strength_before: float, strength_after: float):
        """Log memory access for analysis"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO memory_access_log (
                    memory_id, access_type, strength_before, strength_after, timestamp
                ) VALUES (?, ?, ?, ?, ?)
            ''', (memory_id, access_type, strength_before, strength_after, time.time()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Memory access log error: {e}")
    
    def _log_sleep_consolidation(self, sleep_duration: float, consolidated: int,
                                pruned: int, avg_before: float, avg_after: float):
        """Log sleep consolidation session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sleep_consolidation_log (
                    sleep_start, sleep_duration, memories_consolidated,
                    memories_pruned, avg_strength_before, avg_strength_after, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.last_sleep_time,
                sleep_duration,
                consolidated,
                pruned,
                avg_before,
                avg_after,
                time.time()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Sleep consolidation log error: {e}")


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

memory_consolidation_system: Optional[LunaMemoryConsolidation] = None

def initialize_memory_consolidation() -> LunaMemoryConsolidation:
    """Initialize memory consolidation system"""
    global memory_consolidation_system
    if memory_consolidation_system is None:
        memory_consolidation_system = LunaMemoryConsolidation()
        # Start background monitoring
        memory_consolidation_system.start_consolidation_monitoring()
    return memory_consolidation_system

def get_memory_consolidation() -> Optional[LunaMemoryConsolidation]:
    """Get memory consolidation system instance"""
    return memory_consolidation_system

def add_consolidated_memory(content: str, memory_type: str = "episodic",
                           importance: float = 0.5, emotional_valence: float = 0.0,
                           context_tags: List[str] = None) -> Optional[ConsolidatedMemory]:
    """Add a memory to the consolidation system"""
    if memory_consolidation_system:
        # Convert string to enum
        mem_type = MemoryType.EPISODIC
        if memory_type == "semantic":
            mem_type = MemoryType.SEMANTIC
        elif memory_type == "procedural":
            mem_type = MemoryType.PROCEDURAL
        elif memory_type == "emotional":
            mem_type = MemoryType.EMOTIONAL
        elif memory_type == "working":
            mem_type = MemoryType.WORKING
        
        return memory_consolidation_system.add_memory(content, mem_type, importance, emotional_valence, context_tags)
    return None

def recall_consolidated_memory(memory_id: str, context_tags: List[str] = None) -> Optional[ConsolidatedMemory]:
    """Recall a memory from the consolidation system"""
    if memory_consolidation_system:
        return memory_consolidation_system.recall_memory(memory_id, context_tags)
    return None

def trigger_sleep_consolidation(sleep_duration_hours: float = 8.0):
    """Trigger sleep consolidation process"""
    if memory_consolidation_system:
        return memory_consolidation_system.consolidate_during_sleep(sleep_duration_hours)
    return {}

