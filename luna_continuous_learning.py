"""
Luna's Continuous Learning System
Allows Luna to update her understanding over time through fine-tuning and knowledge accumulation
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path

try:
    import ollama
except ImportError:
    print("⚠️ ollama not installed - continuous learning will use requests")
    import requests
    ollama = None

class ContinuousLearningEngine:
    """Enables Luna to learn continuously from interactions"""
    
    def __init__(self, model_name: str, base_model: str = "hf.co/subsectmusic/qwriko3-4b-instruct-2507-redux-GGUF:Q4_K_M"):
        self.model_name = model_name
        self.base_model = base_model
        self.learning_data_file = "luna_learning_data.jsonl"
        self.fine_tune_trigger_count = 100  # Trigger fine-tune after 100 new examples
        self.knowledge_base_file = "luna_knowledge_base.json"
        
        self._ensure_files_exist()
        
    def _ensure_files_exist(self):
        """Create learning files if they don't exist"""
        if not os.path.exists(self.learning_data_file):
            open(self.learning_data_file, 'w').close()
        
        if not os.path.exists(self.knowledge_base_file):
            with open(self.knowledge_base_file, 'w') as f:
                json.dump({
                    "facts": [],
                    "concepts": {},
                    "user_preferences": {},
                    "learned_patterns": []
                }, f, indent=2)
    
    def record_interaction(self, user_message: str, luna_response: str, 
                          username: str, feedback: str = None):
        """Record an interaction for learning"""
        
        # Store in JSONL format for potential fine-tuning
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "user": username,
            "input": user_message,
            "output": luna_response,
            "feedback": feedback
        }
        
        with open(self.learning_data_file, 'a') as f:
            f.write(json.dumps(interaction) + '\n')
    
    def extract_knowledge(self, conversation: str) -> dict:
        """Extract learnable knowledge from conversation"""
        
        prompt = f"""Analyze this conversation and extract key learnings:

{conversation}

Extract:
1. New facts mentioned
2. User preferences revealed
3. Patterns in conversation style
4. Corrections or feedback given

Format as JSON:
{{
    "facts": ["fact1", "fact2"],
    "preferences": {{"user": "preference"}},
    "patterns": ["pattern1"],
    "corrections": ["correction1"]
}}

Extracted knowledge:"""

        try:
            response = ollama.chat(
                model=self.base_model,
                messages=[{'role': 'user', 'content': prompt}],
                options={"temperature": 0.3}  # Lower temp for factual extraction
            )
            
            response_text = response['message']['content'].strip()
            
            # Extract JSON
            if "{" in response_text and "}" in response_text:
                json_start = response_text.index("{")
                json_end = response_text.rindex("}") + 1
                knowledge = json.loads(response_text[json_start:json_end])
                
                # Store in knowledge base
                self._update_knowledge_base(knowledge)
                
                return knowledge
            else:
                return {}
                
        except Exception as e:
            print(f"❌ Knowledge extraction failed: {e}")
            return {}
    
    def _update_knowledge_base(self, new_knowledge: dict):
        """Update the persistent knowledge base"""
        
        try:
            with open(self.knowledge_base_file, 'r') as f:
                kb = json.load(f)
            
            # Merge new facts
            if "facts" in new_knowledge:
                for fact in new_knowledge["facts"]:
                    if fact not in kb["facts"]:
                        kb["facts"].append(fact)
            
            # Merge preferences
            if "preferences" in new_knowledge:
                kb["user_preferences"].update(new_knowledge["preferences"])
            
            # Merge patterns
            if "patterns" in new_knowledge:
                for pattern in new_knowledge["patterns"]:
                    if pattern not in kb["learned_patterns"]:
                        kb["learned_patterns"].append(pattern)
            
            # Save updated knowledge base
            with open(self.knowledge_base_file, 'w') as f:
                json.dump(kb, f, indent=2)
            
            print(f"✅ Knowledge base updated")
            
        except Exception as e:
            print(f"❌ Knowledge base update failed: {e}")
    
    def get_knowledge_context(self) -> str:
        """Get knowledge base as context for prompts"""
        
        try:
            with open(self.knowledge_base_file, 'r') as f:
                kb = json.load(f)
            
            context = "What I've learned:\n"
            
            if kb["facts"]:
                context += "\nFacts:\n"
                for fact in kb["facts"][-10:]:  # Last 10 facts
                    context += f"- {fact}\n"
            
            if kb["user_preferences"]:
                context += "\nUser Preferences:\n"
                for user, pref in kb["user_preferences"].items():
                    context += f"- {user}: {pref}\n"
            
            return context
            
        except Exception as e:
            return ""
    
    def get_learning_stats(self) -> dict:
        """Get statistics about learning progress"""
        
        try:
            # Count interactions
            interaction_count = 0
            if os.path.exists(self.learning_data_file):
                with open(self.learning_data_file, 'r') as f:
                    interaction_count = sum(1 for _ in f)
            
            # Get knowledge base size
            with open(self.knowledge_base_file, 'r') as f:
                kb = json.load(f)
            
            return {
                "total_interactions": interaction_count,
                "facts_learned": len(kb.get("facts", [])),
                "users_tracked": len(kb.get("user_preferences", {})),
                "patterns_identified": len(kb.get("learned_patterns", [])),
                "ready_for_fine_tune": interaction_count >= self.fine_tune_trigger_count
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def create_modelfile_for_fine_tune(self) -> str:
        """Create a Modelfile with learned knowledge baked in"""
        
        try:
            with open(self.knowledge_base_file, 'r') as f:
                kb = json.load(f)
            
            # Build enhanced system prompt with learned knowledge
            learned_facts = "\n".join([f"- {fact}" for fact in kb.get("facts", [])[:20]])
            learned_patterns = "\n".join([f"- {pattern}" for pattern in kb.get("learned_patterns", [])[:10]])
            
            modelfile = f"""FROM {self.base_model}

# Luna's Learned Knowledge
SYSTEM You are Luna, an AI that learns and evolves.

You have learned these facts:
{learned_facts}

You've identified these conversation patterns:
{learned_patterns}

Use this knowledge naturally in your responses.

PARAMETER temperature 0.9
PARAMETER top_p 0.95
PARAMETER num_ctx 512
"""
            
            modelfile_path = "luna_learned_model.Modelfile"
            with open(modelfile_path, 'w') as f:
                f.write(modelfile)
            
            return modelfile_path
            
        except Exception as e:
            print(f"❌ Modelfile creation failed: {e}")
            return None
    
    def propose_model_update(self) -> dict:
        """Propose updating the model with learned knowledge"""
        
        stats = self.get_learning_stats()
        
        if not stats.get("ready_for_fine_tune", False):
            return {
                "ready": False,
                "message": f"Not enough data yet. {stats['total_interactions']}/{self.fine_tune_trigger_count} interactions",
                "stats": stats
            }
        
        modelfile = self.create_modelfile_for_fine_tune()
        
        if not modelfile:
            return {
                "ready": False,
                "message": "Failed to create Modelfile",
                "stats": stats
            }
        
        return {
            "ready": True,
            "message": f"Ready to update model with {stats['facts_learned']} learned facts",
            "modelfile": modelfile,
            "stats": stats,
            "command": f"ollama create luna_learned -f {modelfile}"
        }


if __name__ == "__main__":
    # Test
    engine = ContinuousLearningEngine("luna_v1")
    
    # Simulate learning
    engine.record_interaction(
        "What's my favorite color?",
        "I remember you love blue!",
        "Chris",
        "positive"
    )
    
    # Extract knowledge
    knowledge = engine.extract_knowledge("""
    Chris: I really love cats
    Luna: That's awesome! Cats are so cute!
    Chris: Yeah, especially orange ones
    """)
    
    print(f"Extracted: {knowledge}")
    print(f"Stats: {engine.get_learning_stats()}")

