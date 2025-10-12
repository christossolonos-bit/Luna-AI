"""
Luna Hybrid Model System
Intelligently routes between Mistral 7B (fast) and Qwriko3-4b (deep)
"""

import ollama
import json
import time
from typing import Dict, Tuple

class LunaHybridModels:
    """
    Intelligent model routing for optimal responses
    
    Models:
    - Mistral 7B: Fast, concise, general chat
    - Qwriko3-4b: Deep, empathetic, complex reasoning
    """
    
    def __init__(self):
        self.models = {
            'fast': 'mistral:7b',
            'deep': 'hf.co/subsectmusic/qwriko3-4b-instruct-2507-redux-GGUF:Q4_K_M'
        }
        
        self.routing_rules = {
            'gui': 'fast',      # GUI needs speed
            'twitch': 'fast',   # Twitch needs instant
            'discord': 'deep'   # Discord can handle deeper responses
        }
        
        print("🔀 Hybrid Model System initialized")
        print(f"   Fast: {self.models['fast']}")
        print(f"   Deep: {self.models['deep']}")
    
    def should_use_deep_model(self, user_input: str, username: str, platform: str) -> bool:
        """Determine if we should use the deep model"""
        
        # Platform-based routing
        if platform == 'discord':
            return True  # Discord always uses deep model
        
        # Complexity-based routing
        word_count = len(user_input.split())
        has_question = '?' in user_input
        
        # Use deep model for:
        if word_count > 20:  # Long messages need depth
            return True
        if has_question and word_count > 10:  # Complex questions
            return True
        
        # Emotional keywords suggest need for empathy
        emotional_keywords = ['feel', 'sad', 'angry', 'hurt', 'love', 'hate', 
                            'depressed', 'anxious', 'worried', 'scared', 'afraid']
        if any(kw in user_input.lower() for kw in emotional_keywords):
            return True
        
        # Default to fast model
        return False
    
    def generate_with_classification(self, user_input: str, username: str, 
                                    platform: str, system_prompt: str) -> Tuple[str, Dict]:
        """
        Generate response with Qwriko3-4b's classification system
        Returns: (response, metadata)
        """
        try:
            # Step 1: Classify the message
            classify_prompt = f"""Analyze this message and classify it:
Message: "{user_input}"

Respond with ONLY a JSON object:
{{
    "importance": 0-100,
    "memory_type": "conversation|emotional|preference|question",
    "keywords": ["key", "words"],
    "needs_deep_response": true/false,
    "emotional_intensity": 0.0-1.0
}}"""
            
            classification_response = ollama.chat(
                model=self.models['deep'],
                messages=[{"role": "user", "content": classify_prompt}],
                options={"temperature": 0.3, "num_predict": 100}
            )
            
            # Parse classification
            classification_text = classification_response['message']['content'].strip()
            # Extract JSON from response
            import re
            json_match = re.search(r'\{[^}]+\}', classification_text)
            if json_match:
                classification = json.loads(json_match.group())
            else:
                classification = {'importance': 50, 'needs_deep_response': False}
            
            print(f"📊 Classification: importance={classification.get('importance', 50)}, "
                  f"emotional={classification.get('emotional_intensity', 0.5)}")
            
            # Step 2: Generate response with full context
            response = ollama.chat(
                model=self.models['deep'],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                options={
                    "temperature": 0.7,
                    "num_predict": 300 if classification.get('needs_deep_response') else 150,
                    "top_p": 0.9
                }
            )
            
            reply = response['message']['content'].strip()
            
            return reply, classification
            
        except Exception as e:
            print(f"⚠️ Deep model error: {e}")
            return "", {}
    
    def generate_response(self, user_input: str, username: str, platform: str,
                         system_prompt: str) -> Tuple[str, bool, Dict]:
        """
        Generate response using optimal model
        Returns: (response, success, metadata)
        """
        
        # Determine which model to use
        use_deep = self.should_use_deep_model(user_input, username, platform)
        
        metadata = {
            'model_used': 'deep' if use_deep else 'fast',
            'platform': platform,
            'username': username
        }
        
        if use_deep:
            print(f"🧠 Using DEEP model (Qwriko3-4b) for {username}@{platform}")
            reply, classification = self.generate_with_classification(
                user_input, username, platform, system_prompt
            )
            metadata.update(classification)
            return reply, bool(reply), metadata
        else:
            print(f"⚡ Using FAST model (Mistral 7B) for {username}@{platform}")
            try:
                response = ollama.chat(
                    model=self.models['fast'],
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_input}
                    ],
                    options={
                        "temperature": 0.7,
                        "num_predict": 100,
                        "top_p": 0.8
                    }
                )
                
                reply = response['message']['content'].strip()
                return reply, True, metadata
                
            except Exception as e:
                print(f"⚠️ Fast model error: {e}")
                return "", False, metadata

# Global instance
hybrid_models = LunaHybridModels()

def get_hybrid_models():
    """Get the global hybrid models instance"""
    return hybrid_models

