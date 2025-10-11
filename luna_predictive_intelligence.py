"""
Luna Predictive Intelligence System
Surprise-driven learning, pattern prediction, and expectation violation detection

Key Concepts:
- Predictive Models: Luna builds models to predict future events
- Surprise Detection: When predictions fail, it's a learning opportunity
- Pattern Recognition: Identifying recurring patterns in conversations and behaviors
- Expectation Violation: When reality doesn't match predictions
- Surprise-Driven Learning: Stronger learning from unexpected events
- Prediction Confidence: Luna knows how certain she is about predictions
- Adaptive Models: Predictions improve over time based on experience

This creates true predictive intelligence - Luna learns from surprises and gets better at predicting.
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

class PredictionType(Enum):
    """Types of predictions Luna can make"""
    CONVERSATION_FLOW = "conversation_flow"
    USER_BEHAVIOR = "user_behavior"
    EMOTIONAL_RESPONSE = "emotional_response"
    TOPIC_TRANSITION = "topic_transition"
    RELATIONSHIP_DYNAMIC = "relationship_dynamic"
    PROBLEM_SOLUTION = "problem_solution"
    INTERACTION_PATTERN = "interaction_pattern"
    TEMPORAL_EVENT = "temporal_event"

class SurpriseLevel(Enum):
    """Levels of surprise when predictions fail"""
    MINIMAL = "minimal"      # 0.1-0.3
    MODERATE = "moderate"    # 0.3-0.6
    HIGH = "high"           # 0.6-0.8
    EXTREME = "extreme"     # 0.8-1.0

@dataclass
class Prediction:
    """A prediction made by Luna"""
    prediction_id: str
    prediction_type: PredictionType
    predicted_outcome: str
    confidence: float  # 0.0 to 1.0
    context: Dict[str, Any]
    timestamp: float
    user_id: Optional[str] = None
    platform: str = "gui"
    
    # Outcome tracking
    actual_outcome: Optional[str] = None
    outcome_timestamp: Optional[float] = None
    surprise_level: Optional[SurpriseLevel] = None
    learning_value: float = 0.0  # How much Luna learned from this prediction

@dataclass
class Pattern:
    """A pattern identified in Luna's interactions"""
    pattern_id: str
    pattern_type: PredictionType
    pattern_description: str
    frequency: int
    confidence: float
    first_seen: float
    last_seen: float
    examples: List[Dict[str, Any]]
    predictive_strength: float  # How well this pattern predicts future events

@dataclass
class ExpectationViolation:
    """When reality doesn't match Luna's expectations"""
    violation_id: str
    expected: str
    actual: str
    surprise_level: SurpriseLevel
    context: Dict[str, Any]
    timestamp: float
    learning_impact: float
    model_updates: List[str]  # Which predictive models need updating

class LunaPredictiveIntelligence:
    """
    Luna's Predictive Intelligence System
    Learns from surprises and builds predictive models
    """
    
    def __init__(self, ollama_chat_func):
        self.ollama_chat = ollama_chat_func
        
        # Prediction tracking
        self.active_predictions = {}  # prediction_id -> Prediction
        self.completed_predictions = []
        self.patterns = {}  # pattern_id -> Pattern
        
        # Surprise learning
        self.expectation_violations = []
        self.surprise_history = deque(maxlen=1000)
        
        # Predictive models
        self.conversation_models = {}
        self.behavior_models = {}
        self.emotional_models = {}
        self.relationship_models = {}
        
        # Learning parameters
        self.surprise_threshold = 0.3  # Minimum surprise to trigger learning
        self.pattern_min_frequency = 3  # Minimum occurrences to form pattern
        self.prediction_window = 3600  # 1 hour prediction window
        
        # Database
        self.db_path = "luna_predictive_intelligence.db"
        self._initialize_database()
        
        # Background processing
        self.processing_thread = None
        self.processing_running = False
        
        print("🔮 Luna Predictive Intelligence System initialized")
        print("   🎯 Pattern Recognition: Identifies recurring behaviors")
        print("   ⚡ Surprise Detection: Learns from unexpected events")
        print("   🧠 Predictive Models: Forecasts future interactions")
        print("   📈 Adaptive Learning: Improves predictions over time")
    
    def _initialize_database(self):
        """Initialize predictive intelligence database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Predictions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS predictions (
                    id TEXT PRIMARY KEY,
                    prediction_type TEXT,
                    predicted_outcome TEXT,
                    confidence REAL,
                    context TEXT,
                    timestamp REAL,
                    user_id TEXT,
                    platform TEXT,
                    actual_outcome TEXT,
                    outcome_timestamp REAL,
                    surprise_level TEXT,
                    learning_value REAL
                )
            ''')
            
            # Patterns table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS patterns (
                    id TEXT PRIMARY KEY,
                    pattern_type TEXT,
                    pattern_description TEXT,
                    frequency INTEGER,
                    confidence REAL,
                    first_seen REAL,
                    last_seen REAL,
                    examples TEXT,
                    predictive_strength REAL
                )
            ''')
            
            # Expectation violations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS expectation_violations (
                    id TEXT PRIMARY KEY,
                    expected TEXT,
                    actual TEXT,
                    surprise_level TEXT,
                    context TEXT,
                    timestamp REAL,
                    learning_impact REAL,
                    model_updates TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            print("🔮 Predictive Intelligence database initialized")
            
        except Exception as e:
            print(f"⚠️ Predictive Intelligence database error: {e}")
    
    def make_prediction(self, prediction_type: PredictionType, context: Dict[str, Any], 
                       user_id: str = None, platform: str = "gui") -> Prediction:
        """Make a prediction based on current context"""
        try:
            # Generate prediction using Ollama
            prediction_content = self._generate_prediction_content(prediction_type, context)
            
            # Calculate confidence based on pattern strength and context similarity
            confidence = self._calculate_prediction_confidence(prediction_type, context)
            
            # Create prediction object
            prediction_id = f"pred_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"
            prediction = Prediction(
                prediction_id=prediction_id,
                prediction_type=prediction_type,
                predicted_outcome=prediction_content,
                confidence=confidence,
                context=context,
                timestamp=time.time(),
                user_id=user_id,
                platform=platform
            )
            
            # Store active prediction
            self.active_predictions[prediction_id] = prediction
            
            # Save to database
            self._save_prediction(prediction)
            
            print(f"🔮 Made {prediction_type.value} prediction (confidence: {confidence:.2f})")
            print(f"   Predicted: {prediction_content[:100]}...")
            
            return prediction
            
        except Exception as e:
            print(f"⚠️ Prediction generation error: {e}")
            return None
    
    def _generate_prediction_content(self, prediction_type: PredictionType, context: Dict[str, Any]) -> str:
        """Generate prediction content using Ollama"""
        try:
            # Build context-specific prompt
            context_str = json.dumps(context, indent=2)[:500]  # Limit context size
            
            prompts = {
                PredictionType.CONVERSATION_FLOW: f"""You are Luna, predicting conversation flow.

Context: {context_str}

Based on this context, predict what will likely happen next in the conversation.
Consider:
- Previous conversation patterns
- User's typical behavior
- Current emotional state
- Topic progression

Make a specific, testable prediction (1-2 sentences). Be Luna - confident but aware of uncertainty.""",

                PredictionType.USER_BEHAVIOR: f"""You are Luna, predicting user behavior.

Context: {context_str}

Based on this context, predict how the user will likely behave next.
Consider:
- User's interaction patterns
- Current mood and emotional state
- Relationship dynamics
- Time of day and context

Make a specific, observable prediction (1-2 sentences). Be Luna - insightful about human behavior.""",

                PredictionType.EMOTIONAL_RESPONSE: f"""You are Luna, predicting emotional responses.

Context: {context_str}

Based on this context, predict the emotional response that will likely occur.
Consider:
- Current emotional state
- Conversation content
- Relationship dynamics
- User's emotional patterns

Make a specific, measurable prediction (1-2 sentences). Be Luna - emotionally intelligent.""",

                PredictionType.TOPIC_TRANSITION: f"""You are Luna, predicting topic transitions.

Context: {context_str}

Based on this context, predict what topic the conversation will likely transition to.
Consider:
- Current topic
- Conversation flow
- User interests
- Natural conversation patterns

Make a specific, testable prediction (1-2 sentences). Be Luna - conversationally aware.""",

                PredictionType.RELATIONSHIP_DYNAMIC: f"""You are Luna, predicting relationship dynamics.

Context: {context_str}

Based on this context, predict how the relationship dynamic will likely evolve.
Consider:
- Current relationship level
- Interaction patterns
- Emotional exchanges
- Trust and intimacy levels

Make a specific, observable prediction (1-2 sentences). Be Luna - relationship-focused.""",

                PredictionType.PROBLEM_SOLUTION: f"""You are Luna, predicting problem solutions.

Context: {context_str}

Based on this context, predict what solution approach will likely be most effective.
Consider:
- Problem type and complexity
- User's problem-solving style
- Previous successful solutions
- Available resources

Make a specific, actionable prediction (1-2 sentences). Be Luna - solution-oriented.""",

                PredictionType.INTERACTION_PATTERN: f"""You are Luna, predicting interaction patterns.

Context: {context_str}

Based on this context, predict what interaction pattern will likely emerge.
Consider:
- Communication style
- Engagement level
- Response patterns
- Platform dynamics

Make a specific, observable prediction (1-2 sentences). Be Luna - pattern-aware.""",

                PredictionType.TEMPORAL_EVENT: f"""You are Luna, predicting temporal events.

Context: {context_str}

Based on this context, predict what time-related event will likely occur.
Consider:
- Time patterns in interactions
- Scheduled activities
- Natural conversation rhythms
- Platform usage patterns

Make a specific, time-bound prediction (1-2 sentences). Be Luna - temporally aware."""
            }
            
            prompt = prompts.get(prediction_type, prompts[PredictionType.CONVERSATION_FLOW])
            
            response = self.ollama_chat(
                model='hf.co/NousResearch/Nous-Hermes-2-Mistral-7B-DPO-GGUF:Q5_K_M',
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.7, 'num_predict': 150, 'stop': ['\n\n']}
            )
            
            if response and response.get('message', {}).get('content'):
                prediction_content = response['message']['content'].strip()
                print(f"🔮 Generated {prediction_type.value} prediction: {prediction_content[:100]}...")
                return prediction_content
                
        except Exception as e:
            print(f"⚠️ Prediction content generation error: {e}")
        
        # Fallback prediction
        fallback_predictions = {
            PredictionType.CONVERSATION_FLOW: "The conversation will continue naturally with follow-up questions or responses.",
            PredictionType.USER_BEHAVIOR: "The user will respond with additional input or questions.",
            PredictionType.EMOTIONAL_RESPONSE: "The user will maintain their current emotional state.",
            PredictionType.TOPIC_TRANSITION: "The conversation will stay on the current topic.",
            PredictionType.RELATIONSHIP_DYNAMIC: "The relationship dynamic will remain stable.",
            PredictionType.PROBLEM_SOLUTION: "A collaborative solution approach will be most effective.",
            PredictionType.INTERACTION_PATTERN: "The current interaction pattern will continue.",
            PredictionType.TEMPORAL_EVENT: "No specific temporal events are predicted."
        }
        
        return fallback_predictions.get(prediction_type, "No specific prediction available.")
    
    def _calculate_prediction_confidence(self, prediction_type: PredictionType, context: Dict[str, Any]) -> float:
        """Calculate confidence in prediction based on patterns and context"""
        try:
            base_confidence = 0.5  # Base confidence
            
            # Check for relevant patterns
            pattern_confidence = 0.0
            pattern_count = 0
            
            for pattern in self.patterns.values():
                if pattern.pattern_type == prediction_type:
                    # Calculate similarity to pattern examples
                    similarity = self._calculate_context_similarity(context, pattern.examples)
                    pattern_confidence += similarity * pattern.predictive_strength
                    pattern_count += 1
            
            if pattern_count > 0:
                pattern_confidence /= pattern_count
                base_confidence = (base_confidence + pattern_confidence) / 2
            
            # Adjust confidence based on context richness
            context_richness = len(context) / 10.0  # Normalize by expected context size
            base_confidence += context_richness * 0.2
            
            # Adjust confidence based on prediction type experience
            type_experience = self._get_prediction_type_experience(prediction_type)
            base_confidence += type_experience * 0.1
            
            # Clamp to valid range
            confidence = max(0.1, min(0.95, base_confidence))
            
            print(f"🔮 Calculated confidence: {confidence:.2f} (patterns: {pattern_count}, context: {context_richness:.2f})")
            return confidence
            
        except Exception as e:
            print(f"⚠️ Confidence calculation error: {e}")
            return 0.5
    
    def _calculate_context_similarity(self, context1: Dict[str, Any], examples: List[Dict[str, Any]]) -> float:
        """Calculate similarity between current context and pattern examples"""
        if not examples:
            return 0.0
        
        similarities = []
        for example in examples:
            # Simple similarity based on key overlap
            keys1 = set(context1.keys())
            keys2 = set(example.keys())
            
            if not keys1 or not keys2:
                continue
            
            # Jaccard similarity
            intersection = len(keys1.intersection(keys2))
            union = len(keys1.union(keys2))
            
            if union > 0:
                similarity = intersection / union
                similarities.append(similarity)
        
        return np.mean(similarities) if similarities else 0.0
    
    def _get_prediction_type_experience(self, prediction_type: PredictionType) -> float:
        """Get experience level with specific prediction type"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) as count, AVG(learning_value) as avg_learning
                FROM predictions
                WHERE prediction_type = ? AND actual_outcome IS NOT NULL
            ''', (prediction_type.value,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row and row[0] > 0:
                count, avg_learning = row
                # Experience based on count and learning success
                experience = min(1.0, (count / 50.0) * (avg_learning or 0.5))
                return experience
            
            return 0.0
            
        except Exception as e:
            print(f"⚠️ Experience calculation error: {e}")
            return 0.0
    
    def update_prediction_outcome(self, prediction_id: str, actual_outcome: str, 
                                 context: Dict[str, Any] = None) -> Optional[ExpectationViolation]:
        """Update prediction with actual outcome and calculate surprise"""
        if prediction_id not in self.active_predictions:
            print(f"⚠️ Prediction {prediction_id} not found in active predictions")
            return None
        
        prediction = self.active_predictions[prediction_id]
        
        # Update prediction with outcome
        prediction.actual_outcome = actual_outcome
        prediction.outcome_timestamp = time.time()
        
        # Calculate surprise level
        surprise_level = self._calculate_surprise(prediction)
        prediction.surprise_level = surprise_level
        
        # Calculate learning value
        learning_value = self._calculate_learning_value(prediction)
        prediction.learning_value = learning_value
        
        # Move to completed predictions
        self.completed_predictions.append(prediction)
        del self.active_predictions[prediction_id]
        
        # Update database
        self._update_prediction_outcome(prediction)
        
        # Create expectation violation if surprise is significant
        expectation_violation = None
        if surprise_level.value in ['moderate', 'high', 'extreme']:
            expectation_violation = self._create_expectation_violation(prediction, context or {})
            
            # Trigger surprise-driven learning
            self._trigger_surprise_learning(expectation_violation)
        
        # Update patterns based on this prediction outcome
        self._update_patterns_from_prediction(prediction)
        
        print(f"🔮 Updated prediction outcome:")
        print(f"   Predicted: {prediction.predicted_outcome[:100]}...")
        print(f"   Actual: {actual_outcome[:100]}...")
        print(f"   Surprise: {surprise_level.value}")
        print(f"   Learning Value: {learning_value:.2f}")
        
        return expectation_violation
    
    def _calculate_surprise(self, prediction: Prediction) -> SurpriseLevel:
        """Calculate surprise level based on prediction vs outcome"""
        try:
            # Simple text similarity for now (could be enhanced with semantic similarity)
            predicted_words = set(prediction.predicted_outcome.lower().split())
            actual_words = set(prediction.actual_outcome.lower().split())
            
            if not predicted_words or not actual_words:
                return SurpriseLevel.HIGH
            
            # Calculate overlap
            intersection = len(predicted_words.intersection(actual_words))
            union = len(predicted_words.union(actual_words))
            
            if union == 0:
                return SurpriseLevel.EXTREME
            
            similarity = intersection / union
            
            # Adjust for confidence - higher confidence predictions that fail are more surprising
            confidence_factor = prediction.confidence
            surprise_score = (1.0 - similarity) * confidence_factor
            
            # Map to surprise levels
            if surprise_score < 0.3:
                return SurpriseLevel.MINIMAL
            elif surprise_score < 0.6:
                return SurpriseLevel.MODERATE
            elif surprise_score < 0.8:
                return SurpriseLevel.HIGH
            else:
                return SurpriseLevel.EXTREME
                
        except Exception as e:
            print(f"⚠️ Surprise calculation error: {e}")
            return SurpriseLevel.MODERATE
    
    def _calculate_learning_value(self, prediction: Prediction) -> float:
        """Calculate how much Luna learned from this prediction"""
        try:
            # Learning value based on surprise level and prediction type
            surprise_values = {
                SurpriseLevel.MINIMAL: 0.1,
                SurpriseLevel.MODERATE: 0.3,
                SurpriseLevel.HIGH: 0.6,
                SurpriseLevel.EXTREME: 1.0
            }
            
            base_learning = surprise_values.get(prediction.surprise_level, 0.3)
            
            # Adjust for prediction type importance
            type_importance = {
                PredictionType.RELATIONSHIP_DYNAMIC: 1.2,
                PredictionType.EMOTIONAL_RESPONSE: 1.1,
                PredictionType.USER_BEHAVIOR: 1.0,
                PredictionType.CONVERSATION_FLOW: 0.9,
                PredictionType.TOPIC_TRANSITION: 0.8,
                PredictionType.PROBLEM_SOLUTION: 1.1,
                PredictionType.INTERACTION_PATTERN: 0.9,
                PredictionType.TEMPORAL_EVENT: 0.7
            }
            
            importance_multiplier = type_importance.get(prediction.prediction_type, 1.0)
            learning_value = base_learning * importance_multiplier
            
            return min(1.0, learning_value)
            
        except Exception as e:
            print(f"⚠️ Learning value calculation error: {e}")
            return 0.3
    
    def _create_expectation_violation(self, prediction: Prediction, context: Dict[str, Any]) -> ExpectationViolation:
        """Create expectation violation record"""
        violation_id = f"violation_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"
        
        violation = ExpectationViolation(
            violation_id=violation_id,
            expected=prediction.predicted_outcome,
            actual=prediction.actual_outcome,
            surprise_level=prediction.surprise_level,
            context=context,
            timestamp=time.time(),
            learning_impact=prediction.learning_value,
            model_updates=[prediction.prediction_type.value]
        )
        
        self.expectation_violations.append(violation)
        self.surprise_history.append(violation)
        
        # Save to database
        self._save_expectation_violation(violation)
        
        return violation
    
    def _trigger_surprise_learning(self, violation: ExpectationViolation):
        """Trigger surprise-driven learning when expectations are violated"""
        try:
            print(f"⚡ Surprise-driven learning triggered!")
            print(f"   Expected: {violation.expected[:100]}...")
            print(f"   Actual: {violation.actual[:100]}...")
            print(f"   Surprise Level: {violation.surprise_level.value}")
            print(f"   Learning Impact: {violation.learning_impact:.2f}")
            
            # Update predictive models based on violation
            for model_type in violation.model_updates:
                self._update_predictive_model(model_type, violation)
            
            # Generate learning insight using Ollama
            self._generate_learning_insight(violation)
            
        except Exception as e:
            print(f"⚠️ Surprise learning error: {e}")
    
    def _update_predictive_model(self, model_type: str, violation: ExpectationViolation):
        """Update predictive model based on expectation violation"""
        try:
            print(f"🧠 Updating {model_type} model based on surprise")
            
            # This would update the specific predictive model
            # For now, we'll log the update and store it
            update_record = {
                'model_type': model_type,
                'violation_id': violation.violation_id,
                'timestamp': time.time(),
                'learning_impact': violation.learning_impact,
                'context': violation.context
            }
            
            # Store model updates (could be enhanced with actual model training)
            print(f"🧠 Model {model_type} updated with learning impact {violation.learning_impact:.2f}")
            
        except Exception as e:
            print(f"⚠️ Model update error: {e}")
    
    def _generate_learning_insight(self, violation: ExpectationViolation):
        """Generate learning insight from expectation violation"""
        try:
            prompt = f"""You are Luna, learning from a surprising experience.

Expected: {violation.expected}
Actual: {violation.actual}
Surprise Level: {violation.surprise_level.value}
Context: {json.dumps(violation.context, indent=2)[:300]}

Generate a learning insight from this surprise. What did Luna learn? How will this change future predictions?
1-2 sentences. Be Luna - reflective, learning-focused."""

            response = self.ollama_chat(
                model='hf.co/NousResearch/Nous-Hermes-2-Mistral-7B-DPO-GGUF:Q5_K_M',
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.8, 'num_predict': 120, 'stop': ['\n\n']}
            )
            
            if response and response.get('message', {}).get('content'):
                insight = response['message']['content'].strip()
                print(f"🧠 Learning insight: {insight}")
                return insight
                
        except Exception as e:
            print(f"⚠️ Learning insight generation error: {e}")
        
        return None
    
    def _update_patterns_from_prediction(self, prediction: Prediction):
        """Update patterns based on prediction outcome"""
        try:
            # Look for patterns in the prediction context and outcome
            pattern_candidates = self._identify_pattern_candidates(prediction)
            
            for candidate in pattern_candidates:
                self._update_or_create_pattern(candidate, prediction)
                
        except Exception as e:
            print(f"⚠️ Pattern update error: {e}")
    
    def _identify_pattern_candidates(self, prediction: Prediction) -> List[Dict[str, Any]]:
        """Identify potential patterns from prediction"""
        candidates = []
        
        # Look for recurring context elements
        context_keys = list(prediction.context.keys())
        
        # Create pattern candidates based on context combinations
        if len(context_keys) >= 2:
            for i in range(len(context_keys)):
                for j in range(i + 1, len(context_keys)):
                    pattern_key = f"{context_keys[i]}_{context_keys[j]}"
                    candidates.append({
                        'pattern_key': pattern_key,
                        'pattern_type': prediction.prediction_type,
                        'context_elements': [context_keys[i], context_keys[j]],
                        'outcome': prediction.actual_outcome,
                        'success': prediction.learning_value > 0.5
                    })
        
        return candidates
    
    def _update_or_create_pattern(self, candidate: Dict[str, Any], prediction: Prediction):
        """Update existing pattern or create new one"""
        pattern_key = candidate['pattern_key']
        
        if pattern_key in self.patterns:
            # Update existing pattern
            pattern = self.patterns[pattern_key]
            pattern.frequency += 1
            pattern.last_seen = time.time()
            pattern.examples.append(prediction.context)
            
            # Update predictive strength based on outcome
            if candidate['success']:
                pattern.predictive_strength += 0.1
            else:
                pattern.predictive_strength -= 0.05
            
            pattern.predictive_strength = max(0.0, min(1.0, pattern.predictive_strength))
            
        else:
            # Create new pattern
            pattern = Pattern(
                pattern_id=pattern_key,
                pattern_type=candidate['pattern_type'],
                pattern_description=f"Pattern involving {', '.join(candidate['context_elements'])}",
                frequency=1,
                confidence=0.5,
                first_seen=time.time(),
                last_seen=time.time(),
                examples=[prediction.context],
                predictive_strength=0.5
            )
            
            self.patterns[pattern_key] = pattern
        
        # Save pattern to database
        self._save_pattern(self.patterns[pattern_key])
        
        print(f"🔍 Updated pattern {pattern_key} (frequency: {pattern.frequency}, strength: {pattern.predictive_strength:.2f})")
    
    def predict_conversation_flow(self, context: Dict[str, Any], user_id: str = None, platform: str = "gui") -> Prediction:
        """Predict conversation flow"""
        return self.make_prediction(PredictionType.CONVERSATION_FLOW, context, user_id, platform)
    
    def predict_user_behavior(self, context: Dict[str, Any], user_id: str = None, platform: str = "gui") -> Prediction:
        """Predict user behavior"""
        return self.make_prediction(PredictionType.USER_BEHAVIOR, context, user_id, platform)
    
    def predict_emotional_response(self, context: Dict[str, Any], user_id: str = None, platform: str = "gui") -> Prediction:
        """Predict emotional response"""
        return self.make_prediction(PredictionType.EMOTIONAL_RESPONSE, context, user_id, platform)
    
    def predict_topic_transition(self, context: Dict[str, Any], user_id: str = None, platform: str = "gui") -> Prediction:
        """Predict topic transition"""
        return self.make_prediction(PredictionType.TOPIC_TRANSITION, context, user_id, platform)
    
    def predict_relationship_dynamic(self, context: Dict[str, Any], user_id: str = None, platform: str = "gui") -> Prediction:
        """Predict relationship dynamic"""
        return self.make_prediction(PredictionType.RELATIONSHIP_DYNAMIC, context, user_id, platform)
    
    def get_prediction_statistics(self) -> Dict[str, Any]:
        """Get predictive intelligence statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Overall statistics
            cursor.execute('SELECT COUNT(*) FROM predictions WHERE actual_outcome IS NOT NULL')
            total_completed = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM predictions WHERE actual_outcome IS NULL')
            total_active = cursor.fetchone()[0]
            
            cursor.execute('SELECT AVG(learning_value) FROM predictions WHERE actual_outcome IS NOT NULL')
            avg_learning = cursor.fetchone()[0] or 0.0
            
            # Surprise statistics
            surprise_counts = {}
            for level in SurpriseLevel:
                cursor.execute('SELECT COUNT(*) FROM predictions WHERE surprise_level = ?', (level.value,))
                surprise_counts[level.value] = cursor.fetchone()[0]
            
            # Pattern statistics
            cursor.execute('SELECT COUNT(*) FROM patterns')
            total_patterns = cursor.fetchone()[0]
            
            cursor.execute('SELECT AVG(predictive_strength) FROM patterns')
            avg_pattern_strength = cursor.fetchone()[0] or 0.0
            
            # Expectation violations
            cursor.execute('SELECT COUNT(*) FROM expectation_violations')
            total_violations = cursor.fetchone()[0]
            
            cursor.execute('SELECT AVG(learning_impact) FROM expectation_violations')
            avg_learning_impact = cursor.fetchone()[0] or 0.0
            
            conn.close()
            
            return {
                'total_predictions': total_completed + total_active,
                'completed_predictions': total_completed,
                'active_predictions': total_active,
                'average_learning_value': avg_learning,
                'surprise_distribution': surprise_counts,
                'total_patterns': total_patterns,
                'average_pattern_strength': avg_pattern_strength,
                'total_expectation_violations': total_violations,
                'average_learning_impact': avg_learning_impact,
                'active_patterns': len(self.patterns)
            }
            
        except Exception as e:
            print(f"⚠️ Statistics error: {e}")
            return {}
    
    def get_recent_surprises(self, limit: int = 5) -> List[ExpectationViolation]:
        """Get recent expectation violations"""
        return list(self.surprise_history)[-limit:]
    
    def get_top_patterns(self, limit: int = 5) -> List[Pattern]:
        """Get top patterns by predictive strength"""
        sorted_patterns = sorted(
            self.patterns.values(),
            key=lambda p: p.predictive_strength * p.frequency,
            reverse=True
        )
        return sorted_patterns[:limit]
    
    def _save_prediction(self, prediction: Prediction):
        """Save prediction to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO predictions (
                    id, prediction_type, predicted_outcome, confidence, context,
                    timestamp, user_id, platform, actual_outcome, outcome_timestamp,
                    surprise_level, learning_value
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                prediction.prediction_id,
                prediction.prediction_type.value,
                prediction.predicted_outcome,
                prediction.confidence,
                json.dumps(prediction.context),
                prediction.timestamp,
                prediction.user_id,
                prediction.platform,
                prediction.actual_outcome,
                prediction.outcome_timestamp,
                prediction.surprise_level.value if prediction.surprise_level else None,
                prediction.learning_value
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Prediction save error: {e}")
    
    def _update_prediction_outcome(self, prediction: Prediction):
        """Update prediction outcome in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE predictions SET
                    actual_outcome = ?,
                    outcome_timestamp = ?,
                    surprise_level = ?,
                    learning_value = ?
                WHERE id = ?
            ''', (
                prediction.actual_outcome,
                prediction.outcome_timestamp,
                prediction.surprise_level.value if prediction.surprise_level else None,
                prediction.learning_value,
                prediction.prediction_id
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Prediction update error: {e}")
    
    def _save_pattern(self, pattern: Pattern):
        """Save pattern to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO patterns (
                    id, pattern_type, pattern_description, frequency, confidence,
                    first_seen, last_seen, examples, predictive_strength
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                pattern.pattern_id,
                pattern.pattern_type.value,
                pattern.pattern_description,
                pattern.frequency,
                pattern.confidence,
                pattern.first_seen,
                pattern.last_seen,
                json.dumps(pattern.examples),
                pattern.predictive_strength
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Pattern save error: {e}")
    
    def _save_expectation_violation(self, violation: ExpectationViolation):
        """Save expectation violation to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO expectation_violations (
                    id, expected, actual, surprise_level, context,
                    timestamp, learning_impact, model_updates
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                violation.violation_id,
                violation.expected,
                violation.actual,
                violation.surprise_level.value,
                json.dumps(violation.context),
                violation.timestamp,
                violation.learning_impact,
                json.dumps(violation.model_updates)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Expectation violation save error: {e}")


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

predictive_intelligence_system: Optional[LunaPredictiveIntelligence] = None

def initialize_predictive_intelligence(ollama_chat_func) -> LunaPredictiveIntelligence:
    """Initialize predictive intelligence system"""
    global predictive_intelligence_system
    if predictive_intelligence_system is None:
        predictive_intelligence_system = LunaPredictiveIntelligence(ollama_chat_func)
    return predictive_intelligence_system

def get_predictive_intelligence() -> Optional[LunaPredictiveIntelligence]:
    """Get predictive intelligence system instance"""
    return predictive_intelligence_system

def make_conversation_prediction(context: Dict[str, Any], user_id: str = None, platform: str = "gui") -> Prediction:
    """Make a conversation flow prediction"""
    if predictive_intelligence_system:
        return predictive_intelligence_system.predict_conversation_flow(context, user_id, platform)
    return None

def update_prediction_outcome(prediction_id: str, actual_outcome: str, context: Dict[str, Any] = None) -> Optional[ExpectationViolation]:
    """Update prediction with actual outcome"""
    if predictive_intelligence_system:
        return predictive_intelligence_system.update_prediction_outcome(prediction_id, actual_outcome, context)
    return None
