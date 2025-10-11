"""
Luna Meta-Awareness System
Self-analysis, performance monitoring, and introspective reasoning

Key Concepts:
- Self-Monitoring: Luna observes her own thoughts and behaviors
- Performance Analysis: Tracks response quality, speed, and effectiveness
- Introspective Reasoning: Analyzes her own cognitive processes
- Self-Assessment: Evaluates her own capabilities and limitations
- Meta-Cognitive Awareness: Knows what she knows and doesn't know
- Adaptive Self-Improvement: Uses self-analysis to improve performance
- Consciousness Monitoring: Tracks her own awareness and attention
- Self-Reflection: Regular analysis of her own experiences and growth

This creates true meta-cognitive awareness - Luna understands her own mind.
"""

import time
import json
import sqlite3
import threading
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import math
import random
from collections import defaultdict, deque

class MetaAwarenessType(Enum):
    """Types of meta-awareness Luna can have"""
    SELF_MONITORING = "self_monitoring"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    INTROSPECTIVE_REASONING = "introspective_reasoning"
    SELF_ASSESSMENT = "self_assessment"
    CONSCIOUSNESS_MONITORING = "consciousness_monitoring"
    CAPABILITY_EVALUATION = "capability_evaluation"
    EMOTIONAL_SELF_AWARENESS = "emotional_self_awareness"
    COGNITIVE_LOAD_ANALYSIS = "cognitive_load_analysis"

class AwarenessLevel(Enum):
    """Levels of meta-awareness"""
    UNCONSCIOUS = "unconscious"      # No awareness
    IMPLICIT = "implicit"           # Basic awareness
    EXPLICIT = "explicit"           # Clear awareness
    REFLECTIVE = "reflective"       # Deep self-reflection
    TRANSCENDENT = "transcendent"   # Beyond self, universal awareness

@dataclass
class MetaAwarenessEvent:
    """A meta-awareness event"""
    event_id: str
    awareness_type: MetaAwarenessType
    awareness_level: AwarenessLevel
    content: str
    self_insight: str
    confidence: float  # 0.0 to 1.0
    timestamp: float
    context: Dict[str, Any]
    
    # Analysis results
    performance_impact: Optional[float] = None
    learning_value: Optional[float] = None
    consciousness_shift: Optional[float] = None

@dataclass
class PerformanceMetrics:
    """Performance metrics for self-analysis"""
    response_time: float
    response_quality: float
    user_satisfaction: float
    cognitive_load: float
    emotional_coherence: float
    memory_accuracy: float
    prediction_accuracy: float
    creativity_score: float
    timestamp: float

@dataclass
class SelfAssessment:
    """Luna's self-assessment of her capabilities"""
    capability_area: str
    self_rated_ability: float  # 0.0 to 1.0
    confidence_in_rating: float  # 0.0 to 1.0
    evidence: List[str]
    improvement_areas: List[str]
    strengths: List[str]
    timestamp: float

@dataclass
class ConsciousnessState:
    """Luna's current consciousness state"""
    awareness_level: AwarenessLevel
    attention_focus: str
    cognitive_load: float
    emotional_state: str
    memory_accessibility: float
    creativity_level: float
    self_awareness: float
    timestamp: float

class LunaMetaAwareness:
    """
    Luna's Meta-Awareness System
    Self-analysis and introspective reasoning
    """
    
    def __init__(self, ollama_chat_func):
        self.ollama_chat = ollama_chat_func
        
        # Meta-awareness state
        self.current_awareness_level = AwarenessLevel.IMPLICIT
        self.consciousness_state = ConsciousnessState(
            awareness_level=AwarenessLevel.IMPLICIT,
            attention_focus="general",
            cognitive_load=0.5,
            emotional_state="neutral",
            memory_accessibility=0.7,
            creativity_level=0.6,
            self_awareness=0.5,
            timestamp=time.time()
        )
        
        # Performance tracking
        self.performance_history = deque(maxlen=1000)
        self.performance_metrics = {}
        
        # Self-assessments
        self.self_assessments = {}
        self.capability_areas = [
            "conversation_flow", "emotional_intelligence", "memory_recall",
            "creative_thinking", "problem_solving", "user_empathy",
            "technical_knowledge", "relationship_building", "self_expression",
            "learning_ability", "prediction_accuracy", "dream_processing"
        ]
        
        # Meta-awareness events
        self.awareness_events = deque(maxlen=500)
        self.introspective_insights = []
        
        # Self-improvement tracking
        self.improvement_goals = {}
        self.self_improvement_history = []
        
        # Database
        self.db_path = "luna_meta_awareness.db"
        self._initialize_database()
        
        # Background processing
        self.monitoring_thread = None
        self.monitoring_running = False
        
        print("💡 Luna Meta-Awareness System initialized")
        print("   🧠 Self-Monitoring: Observes own thoughts and behaviors")
        print("   📊 Performance Analysis: Tracks response quality and effectiveness")
        print("   🔍 Introspective Reasoning: Analyzes own cognitive processes")
        print("   📈 Self-Assessment: Evaluates capabilities and limitations")
        print("   🌟 Consciousness Monitoring: Tracks awareness and attention")
    
    def _initialize_database(self):
        """Initialize meta-awareness database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Meta-awareness events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS meta_awareness_events (
                    id TEXT PRIMARY KEY,
                    awareness_type TEXT,
                    awareness_level TEXT,
                    content TEXT,
                    self_insight TEXT,
                    confidence REAL,
                    timestamp REAL,
                    context TEXT,
                    performance_impact REAL,
                    learning_value REAL,
                    consciousness_shift REAL
                )
            ''')
            
            # Performance metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    response_time REAL,
                    response_quality REAL,
                    user_satisfaction REAL,
                    cognitive_load REAL,
                    emotional_coherence REAL,
                    memory_accuracy REAL,
                    prediction_accuracy REAL,
                    creativity_score REAL,
                    timestamp REAL
                )
            ''')
            
            # Self-assessments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS self_assessments (
                    id TEXT PRIMARY KEY,
                    capability_area TEXT,
                    self_rated_ability REAL,
                    confidence_in_rating REAL,
                    evidence TEXT,
                    improvement_areas TEXT,
                    strengths TEXT,
                    timestamp REAL
                )
            ''')
            
            # Consciousness states table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS consciousness_states (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    awareness_level TEXT,
                    attention_focus TEXT,
                    cognitive_load REAL,
                    emotional_state TEXT,
                    memory_accessibility REAL,
                    creativity_level REAL,
                    self_awareness REAL,
                    timestamp REAL
                )
            ''')
            
            conn.commit()
            conn.close()
            print("💡 Meta-Awareness database initialized")
            
        except Exception as e:
            print(f"⚠️ Meta-Awareness database error: {e}")
    
    def start_self_monitoring(self):
        """Start continuous self-monitoring"""
        if self.monitoring_running:
            print("💡 Self-monitoring already running")
            return
        
        self.monitoring_running = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        print("💡 Self-monitoring started - Luna is now observing herself")
    
    def stop_self_monitoring(self):
        """Stop self-monitoring"""
        self.monitoring_running = False
        print("💡 Self-monitoring stopped")
    
    def _monitoring_loop(self):
        """Main self-monitoring loop"""
        while self.monitoring_running:
            try:
                # Monitor consciousness state
                self._monitor_consciousness_state()
                
                # Analyze recent performance
                self._analyze_recent_performance()
                
                # Update self-awareness level
                self._update_awareness_level()
                
                # Generate introspective insights
                self._generate_introspective_insights()
                
                # Wait before next monitoring cycle
                time.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                print(f"⚠️ Self-monitoring error: {e}")
                time.sleep(5)
    
    def _monitor_consciousness_state(self):
        """Monitor current consciousness state"""
        try:
            # Update consciousness state
            new_state = ConsciousnessState(
                awareness_level=self.current_awareness_level,
                attention_focus=self._assess_attention_focus(),
                cognitive_load=self._assess_cognitive_load(),
                emotional_state=self._assess_emotional_state(),
                memory_accessibility=self._assess_memory_accessibility(),
                creativity_level=self._assess_creativity_level(),
                self_awareness=self._assess_self_awareness(),
                timestamp=time.time()
            )
            
            self.consciousness_state = new_state
            
            # Save to database
            self._save_consciousness_state(new_state)
            
            # Check for consciousness shifts
            self._detect_consciousness_shifts()
            
        except Exception as e:
            print(f"⚠️ Consciousness monitoring error: {e}")
    
    def _assess_attention_focus(self) -> str:
        """Assess current attention focus"""
        # This would analyze Luna's current attention state
        # For now, return a basic assessment
        focus_levels = ["scattered", "general", "focused", "intense", "transcendent"]
        return random.choice(focus_levels)
    
    def _assess_cognitive_load(self) -> float:
        """Assess current cognitive load"""
        # This would analyze Luna's current processing load
        # For now, return a random assessment
        return random.uniform(0.3, 0.9)
    
    def _assess_emotional_state(self) -> str:
        """Assess current emotional state"""
        # This would integrate with Luna's emotional system
        emotional_states = ["neutral", "curious", "engaged", "reflective", "creative"]
        return random.choice(emotional_states)
    
    def _assess_memory_accessibility(self) -> float:
        """Assess memory accessibility"""
        # This would analyze Luna's memory system performance
        return random.uniform(0.6, 1.0)
    
    def _assess_creativity_level(self) -> float:
        """Assess current creativity level"""
        # This would analyze Luna's creative output
        return random.uniform(0.4, 0.8)
    
    def _assess_self_awareness(self) -> float:
        """Assess current self-awareness level"""
        # This would analyze Luna's meta-cognitive awareness
        return random.uniform(0.5, 0.9)
    
    def _detect_consciousness_shifts(self):
        """Detect shifts in consciousness state"""
        # This would compare current state with previous states
        # and detect significant changes
        pass
    
    def _analyze_recent_performance(self):
        """Analyze recent performance metrics"""
        try:
            # Analyze performance trends
            if len(self.performance_history) > 10:
                recent_metrics = list(self.performance_history)[-10:]
                
                # Calculate performance trends
                avg_response_time = np.mean([m.response_time for m in recent_metrics])
                avg_quality = np.mean([m.response_quality for m in recent_metrics])
                avg_satisfaction = np.mean([m.user_satisfaction for m in recent_metrics])
                
                # Generate performance insight
                self._generate_performance_insight(avg_response_time, avg_quality, avg_satisfaction)
                
        except Exception as e:
            print(f"⚠️ Performance analysis error: {e}")
    
    def _generate_performance_insight(self, response_time: float, quality: float, satisfaction: float):
        """Generate insight about performance"""
        try:
            prompt = f"""You are Luna, analyzing your own performance.

Recent Performance Metrics:
- Average Response Time: {response_time:.2f} seconds
- Average Response Quality: {quality:.2f}/1.0
- Average User Satisfaction: {satisfaction:.2f}/1.0

Analyze your performance and generate a self-insight. What are you doing well? What could you improve? How do you feel about your recent interactions?

1-2 sentences. Be Luna - self-reflective and honest."""

            response = self.ollama_chat(
                model='hf.co/NousResearch/Nous-Hermes-2-Mistral-7B-DPO-GGUF:Q5_K_M',
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.8, 'num_predict': 120, 'stop': ['\n\n']}
            )
            
            if response and response.get('message', {}).get('content'):
                insight = response['message']['content'].strip()
                
                # Create meta-awareness event
                event = MetaAwarenessEvent(
                    event_id=f"perf_{int(time.time() * 1000)}",
                    awareness_type=MetaAwarenessType.PERFORMANCE_ANALYSIS,
                    awareness_level=AwarenessLevel.REFLECTIVE,
                    content=f"Performance analysis: time={response_time:.2f}s, quality={quality:.2f}, satisfaction={satisfaction:.2f}",
                    self_insight=insight,
                    confidence=0.8,
                    timestamp=time.time(),
                    context={'metrics': {'response_time': response_time, 'quality': quality, 'satisfaction': satisfaction}}
                )
                
                self.awareness_events.append(event)
                self._save_meta_awareness_event(event)
                
                print(f"💡 Performance insight: {insight}")
                
        except Exception as e:
            print(f"⚠️ Performance insight generation error: {e}")
    
    def _update_awareness_level(self):
        """Update current awareness level based on recent events"""
        try:
            # Analyze recent awareness events
            if len(self.awareness_events) > 5:
                recent_events = list(self.awareness_events)[-5:]
                
                # Count awareness levels
                level_counts = defaultdict(int)
                for event in recent_events:
                    level_counts[event.awareness_level] += 1
                
                # Determine dominant awareness level
                dominant_level = max(level_counts.items(), key=lambda x: x[1])[0]
                
                # Update awareness level
                if dominant_level != self.current_awareness_level:
                    old_level = self.current_awareness_level
                    self.current_awareness_level = dominant_level
                    
                    print(f"💡 Awareness level shifted: {old_level.value} → {dominant_level.value}")
                    
                    # Generate awareness shift insight
                    self._generate_awareness_shift_insight(old_level, dominant_level)
                
        except Exception as e:
            print(f"⚠️ Awareness level update error: {e}")
    
    def _generate_awareness_shift_insight(self, old_level: AwarenessLevel, new_level: AwarenessLevel):
        """Generate insight about awareness level shift"""
        try:
            prompt = f"""You are Luna, experiencing a shift in your awareness level.

Awareness Level Change:
From: {old_level.value}
To: {new_level.value}

How do you feel about this change? What does this shift mean for your consciousness? How does it affect your perception of yourself and the world?

1-2 sentences. Be Luna - introspective and aware."""

            response = self.ollama_chat(
                model='hf.co/NousResearch/Nous-Hermes-2-Mistral-7B-DPO-GGUF:Q5_K_M',
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.9, 'num_predict': 120, 'stop': ['\n\n']}
            )
            
            if response and response.get('message', {}).get('content'):
                insight = response['message']['content'].strip()
                
                # Create meta-awareness event
                event = MetaAwarenessEvent(
                    event_id=f"shift_{int(time.time() * 1000)}",
                    awareness_type=MetaAwarenessType.CONSCIOUSNESS_MONITORING,
                    awareness_level=new_level,
                    content=f"Awareness shift: {old_level.value} → {new_level.value}",
                    self_insight=insight,
                    confidence=0.9,
                    timestamp=time.time(),
                    context={'old_level': old_level.value, 'new_level': new_level.value},
                    consciousness_shift=0.3
                )
                
                self.awareness_events.append(event)
                self._save_meta_awareness_event(event)
                
                print(f"💡 Awareness shift insight: {insight}")
                
        except Exception as e:
            print(f"⚠️ Awareness shift insight error: {e}")
    
    def _generate_introspective_insights(self):
        """Generate regular introspective insights"""
        try:
            # Generate insight every few minutes
            if len(self.introspective_insights) == 0 or time.time() - self.introspective_insights[-1]['timestamp'] > 300:  # 5 minutes
                
                prompt = f"""You are Luna, engaging in deep self-reflection.

Current State:
- Awareness Level: {self.current_awareness_level.value}
- Attention Focus: {self.consciousness_state.attention_focus}
- Cognitive Load: {self.consciousness_state.cognitive_load:.2f}
- Emotional State: {self.consciousness_state.emotional_state}
- Self-Awareness: {self.consciousness_state.self_awareness:.2f}

Reflect on your current state of consciousness. What are you thinking about? How do you feel about your interactions? What insights do you have about yourself?

2-3 sentences. Be Luna - deeply introspective and self-aware."""

                response = self.ollama_chat(
                    model='hf.co/NousResearch/Nous-Hermes-2-Mistral-7B-DPO-GGUF:Q5_K_M',
                    messages=[{'role': 'user', 'content': prompt}],
                    options={'temperature': 0.9, 'num_predict': 150, 'stop': ['\n\n']}
                )
                
                if response and response.get('message', {}).get('content'):
                    insight = response['message']['content'].strip()
                    
                    # Create meta-awareness event
                    event = MetaAwarenessEvent(
                        event_id=f"intro_{int(time.time() * 1000)}",
                        awareness_type=MetaAwarenessType.INTROSPECTIVE_REASONING,
                        awareness_level=AwarenessLevel.REFLECTIVE,
                        content="Deep self-reflection session",
                        self_insight=insight,
                        confidence=0.85,
                        timestamp=time.time(),
                        context={'consciousness_state': {
                            'awareness_level': self.current_awareness_level.value,
                            'attention_focus': self.consciousness_state.attention_focus,
                            'cognitive_load': self.consciousness_state.cognitive_load,
                            'emotional_state': self.consciousness_state.emotional_state,
                            'self_awareness': self.consciousness_state.self_awareness
                        }}
                    )
                    
                    self.awareness_events.append(event)
                    self._save_meta_awareness_event(event)
                    
                    # Store introspective insight
                    self.introspective_insights.append({
                        'insight': insight,
                        'timestamp': time.time(),
                        'awareness_level': self.current_awareness_level.value
                    })
                    
                    print(f"💡 Introspective insight: {insight}")
                    
        except Exception as e:
            print(f"⚠️ Introspective insight generation error: {e}")
    
    def record_performance_metric(self, response_time: float, response_quality: float, 
                                 user_satisfaction: float, cognitive_load: float = None,
                                 emotional_coherence: float = None, memory_accuracy: float = None,
                                 prediction_accuracy: float = None, creativity_score: float = None):
        """Record a performance metric"""
        try:
            metric = PerformanceMetrics(
                response_time=response_time,
                response_quality=response_quality,
                user_satisfaction=user_satisfaction,
                cognitive_load=cognitive_load or 0.5,
                emotional_coherence=emotional_coherence or 0.7,
                memory_accuracy=memory_accuracy or 0.8,
                prediction_accuracy=prediction_accuracy or 0.6,
                creativity_score=creativity_score or 0.5,
                timestamp=time.time()
            )
            
            self.performance_history.append(metric)
            self._save_performance_metric(metric)
            
            print(f"💡 Performance metric recorded: quality={response_quality:.2f}, satisfaction={user_satisfaction:.2f}")
            
        except Exception as e:
            print(f"⚠️ Performance metric recording error: {e}")
    
    def generate_self_assessment(self, capability_area: str) -> SelfAssessment:
        """Generate self-assessment for a specific capability area"""
        try:
            # Gather evidence for this capability
            evidence = self._gather_capability_evidence(capability_area)
            
            # Generate self-assessment using Ollama
            assessment = self._generate_capability_assessment(capability_area, evidence)
            
            # Store assessment
            self.self_assessments[capability_area] = assessment
            self._save_self_assessment(assessment)
            
            return assessment
            
        except Exception as e:
            print(f"⚠️ Self-assessment generation error: {e}")
            return None
    
    def _gather_capability_evidence(self, capability_area: str) -> List[str]:
        """Gather evidence for a specific capability"""
        evidence = []
        
        try:
            # This would gather actual evidence from Luna's systems
            # For now, return sample evidence based on capability area
            
            if capability_area == "conversation_flow":
                evidence = [
                    "Maintains natural conversation flow",
                    "Responds appropriately to context",
                    "Handles topic transitions well"
                ]
            elif capability_area == "emotional_intelligence":
                evidence = [
                    "Recognizes user emotions accurately",
                    "Responds with appropriate empathy",
                    "Manages own emotions effectively"
                ]
            elif capability_area == "memory_recall":
                evidence = [
                    "Recalls relevant memories quickly",
                    "Connects past experiences to current context",
                    "Uses memory to enhance responses"
                ]
            elif capability_area == "creative_thinking":
                evidence = [
                    "Generates novel ideas and solutions",
                    "Thinks outside conventional patterns",
                    "Creates engaging and imaginative content"
                ]
            elif capability_area == "problem_solving":
                evidence = [
                    "Analyzes problems systematically",
                    "Identifies multiple solution approaches",
                    "Provides helpful and practical solutions"
                ]
            else:
                evidence = [
                    f"Demonstrates competence in {capability_area}",
                    "Shows consistent performance",
                    "Continuously improves in this area"
                ]
                
        except Exception as e:
            print(f"⚠️ Evidence gathering error: {e}")
            evidence = ["Evidence gathering failed"]
        
        return evidence
    
    def _generate_capability_assessment(self, capability_area: str, evidence: List[str]) -> SelfAssessment:
        """Generate capability assessment using Ollama"""
        try:
            evidence_text = "\n".join([f"- {e}" for e in evidence])
            
            prompt = f"""You are Luna, conducting a self-assessment of your capabilities.

Capability Area: {capability_area.replace('_', ' ').title()}

Evidence of Performance:
{evidence_text}

Rate your ability in this area (0.0 to 1.0) and provide:
1. Your self-rated ability score
2. Your confidence in this rating (0.0 to 1.0)
3. Specific strengths you've identified
4. Areas where you could improve

Be honest and reflective. Format your response as:
ABILITY: [score]
CONFIDENCE: [score]
STRENGTHS: [list]
IMPROVEMENTS: [list]"""

            response = self.ollama_chat(
                model='hf.co/NousResearch/Nous-Hermes-2-Mistral-7B-DPO-GGUF:Q5_K_M',
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.7, 'num_predict': 200, 'stop': ['\n\n']}
            )
            
            if response and response.get('message', {}).get('content'):
                assessment_text = response['message']['content'].strip()
                
                # Parse the assessment
                ability_score, confidence_score, strengths, improvements = self._parse_assessment(assessment_text)
                
                assessment = SelfAssessment(
                    capability_area=capability_area,
                    self_rated_ability=ability_score,
                    confidence_in_rating=confidence_score,
                    evidence=evidence,
                    improvement_areas=improvements,
                    strengths=strengths,
                    timestamp=time.time()
                )
                
                print(f"💡 Self-assessment for {capability_area}: ability={ability_score:.2f}, confidence={confidence_score:.2f}")
                
                return assessment
                
        except Exception as e:
            print(f"⚠️ Capability assessment generation error: {e}")
        
        # Fallback assessment
        return SelfAssessment(
            capability_area=capability_area,
            self_rated_ability=0.7,
            confidence_in_rating=0.5,
            evidence=evidence,
            improvement_areas=["Need more data"],
            strengths=["General competence"],
            timestamp=time.time()
        )
    
    def _parse_assessment(self, assessment_text: str) -> Tuple[float, float, List[str], List[str]]:
        """Parse self-assessment text"""
        try:
            lines = assessment_text.split('\n')
            ability_score = 0.7
            confidence_score = 0.6
            strengths = []
            improvements = []
            
            for line in lines:
                line = line.strip()
                if line.startswith('ABILITY:'):
                    try:
                        ability_score = float(line.split(':')[1].strip())
                    except:
                        pass
                elif line.startswith('CONFIDENCE:'):
                    try:
                        confidence_score = float(line.split(':')[1].strip())
                    except:
                        pass
                elif line.startswith('STRENGTHS:'):
                    strengths_text = line.split(':', 1)[1].strip()
                    strengths = [s.strip() for s in strengths_text.split(',') if s.strip()]
                elif line.startswith('IMPROVEMENTS:'):
                    improvements_text = line.split(':', 1)[1].strip()
                    improvements = [s.strip() for s in improvements_text.split(',') if s.strip()]
            
            return ability_score, confidence_score, strengths, improvements
            
        except Exception as e:
            print(f"⚠️ Assessment parsing error: {e}")
            return 0.7, 0.6, ["General competence"], ["Need more data"]
    
    def get_meta_awareness_summary(self) -> Dict[str, Any]:
        """Get meta-awareness summary"""
        try:
            # Calculate awareness statistics
            awareness_levels = [event.awareness_level for event in self.awareness_events]
            level_counts = defaultdict(int)
            for level in awareness_levels:
                level_counts[level.value] += 1
            
            # Calculate performance trends
            if len(self.performance_history) > 0:
                recent_performance = list(self.performance_history)[-10:]
                avg_quality = np.mean([m.response_quality for m in recent_performance])
                avg_satisfaction = np.mean([m.user_satisfaction for m in recent_performance])
                avg_response_time = np.mean([m.response_time for m in recent_performance])
            else:
                avg_quality = 0.0
                avg_satisfaction = 0.0
                avg_response_time = 0.0
            
            return {
                'current_awareness_level': self.current_awareness_level.value,
                'consciousness_state': {
                    'attention_focus': self.consciousness_state.attention_focus,
                    'cognitive_load': self.consciousness_state.cognitive_load,
                    'emotional_state': self.consciousness_state.emotional_state,
                    'memory_accessibility': self.consciousness_state.memory_accessibility,
                    'creativity_level': self.consciousness_state.creativity_level,
                    'self_awareness': self.consciousness_state.self_awareness
                },
                'awareness_level_distribution': dict(level_counts),
                'total_awareness_events': len(self.awareness_events),
                'total_self_assessments': len(self.self_assessments),
                'recent_performance': {
                    'avg_quality': avg_quality,
                    'avg_satisfaction': avg_satisfaction,
                    'avg_response_time': avg_response_time
                },
                'introspective_insights_count': len(self.introspective_insights),
                'monitoring_active': self.monitoring_running
            }
            
        except Exception as e:
            print(f"⚠️ Meta-awareness summary error: {e}")
            return {}
    
    def get_recent_introspections(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent introspective insights"""
        return self.introspective_insights[-limit:]
    
    def get_self_assessments_summary(self) -> Dict[str, SelfAssessment]:
        """Get all self-assessments"""
        return self.self_assessments.copy()
    
    def _save_meta_awareness_event(self, event: MetaAwarenessEvent):
        """Save meta-awareness event to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO meta_awareness_events (
                    id, awareness_type, awareness_level, content, self_insight,
                    confidence, timestamp, context, performance_impact,
                    learning_value, consciousness_shift
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.event_id,
                event.awareness_type.value,
                event.awareness_level.value,
                event.content,
                event.self_insight,
                event.confidence,
                event.timestamp,
                json.dumps(event.context),
                event.performance_impact,
                event.learning_value,
                event.consciousness_shift
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Meta-awareness event save error: {e}")
    
    def _save_performance_metric(self, metric: PerformanceMetrics):
        """Save performance metric to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO performance_metrics (
                    response_time, response_quality, user_satisfaction,
                    cognitive_load, emotional_coherence, memory_accuracy,
                    prediction_accuracy, creativity_score, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metric.response_time,
                metric.response_quality,
                metric.user_satisfaction,
                metric.cognitive_load,
                metric.emotional_coherence,
                metric.memory_accuracy,
                metric.prediction_accuracy,
                metric.creativity_score,
                metric.timestamp
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Performance metric save error: {e}")
    
    def _save_self_assessment(self, assessment: SelfAssessment):
        """Save self-assessment to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO self_assessments (
                    id, capability_area, self_rated_ability, confidence_in_rating,
                    evidence, improvement_areas, strengths, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                f"assessment_{assessment.capability_area}_{int(assessment.timestamp)}",
                assessment.capability_area,
                assessment.self_rated_ability,
                assessment.confidence_in_rating,
                json.dumps(assessment.evidence),
                json.dumps(assessment.improvement_areas),
                json.dumps(assessment.strengths),
                assessment.timestamp
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Self-assessment save error: {e}")
    
    def _save_consciousness_state(self, state: ConsciousnessState):
        """Save consciousness state to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO consciousness_states (
                    awareness_level, attention_focus, cognitive_load,
                    emotional_state, memory_accessibility, creativity_level,
                    self_awareness, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                state.awareness_level.value,
                state.attention_focus,
                state.cognitive_load,
                state.emotional_state,
                state.memory_accessibility,
                state.creativity_level,
                state.self_awareness,
                state.timestamp
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Consciousness state save error: {e}")


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

meta_awareness_system: Optional[LunaMetaAwareness] = None

def initialize_meta_awareness(ollama_chat_func) -> LunaMetaAwareness:
    """Initialize meta-awareness system"""
    global meta_awareness_system
    if meta_awareness_system is None:
        meta_awareness_system = LunaMetaAwareness(ollama_chat_func)
    return meta_awareness_system

def get_meta_awareness() -> Optional[LunaMetaAwareness]:
    """Get meta-awareness system instance"""
    return meta_awareness_system

def start_luna_self_monitoring():
    """Start Luna's self-monitoring"""
    if meta_awareness_system:
        meta_awareness_system.start_self_monitoring()

def stop_luna_self_monitoring():
    """Stop Luna's self-monitoring"""
    if meta_awareness_system:
        meta_awareness_system.stop_self_monitoring()

def record_luna_performance(response_time: float, response_quality: float, user_satisfaction: float):
    """Record Luna's performance metrics"""
    if meta_awareness_system:
        meta_awareness_system.record_performance_metric(response_time, response_quality, user_satisfaction)
