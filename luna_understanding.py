"""
Luna's Deep Understanding System
Goes beyond pattern matching to build conceptual understanding
"""

import os
import json
from datetime import datetime

try:
    import ollama
except ImportError:
    print("⚠️ ollama not installed - understanding system will use requests")
    import requests
    ollama = None

class UnderstandingEngine:
    """Builds genuine understanding through concept mapping and reasoning"""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.concept_graph_file = "luna_concept_graph.json"
        self.reasoning_chains_file = "luna_reasoning_chains.json"
        
        self._ensure_files_exist()
    
    def _ensure_files_exist(self):
        """Create understanding files"""
        
        if not os.path.exists(self.concept_graph_file):
            with open(self.concept_graph_file, 'w') as f:
                json.dump({
                    "concepts": {},
                    "relationships": []
                }, f, indent=2)
        
        if not os.path.exists(self.reasoning_chains_file):
            with open(self.reasoning_chains_file, 'w') as f:
                json.dump({"chains": []}, f, indent=2)
    
    def build_concept_map(self, topic: str) -> dict:
        """Build a conceptual understanding of a topic"""
        
        prompt = f"""Analyze this topic deeply and build a concept map:

Topic: {topic}

For genuine understanding, identify:
1. Core concept - What IS it fundamentally?
2. Properties - What are its essential characteristics?
3. Relationships - How does it relate to other concepts?
4. Implications - What follows from this concept?
5. Counterexamples - What is NOT this concept?

Format as JSON:
{{
    "core_concept": "explanation",
    "properties": ["prop1", "prop2"],
    "relationships": {{"related_concept": "relationship_type"}},
    "implications": ["implication1"],
    "counterexamples": ["not_this"]
}}

Deep analysis:"""

        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}],
                options={"temperature": 0.4, "num_predict": 300}
            )
            
            response_text = response['message']['content'].strip()
            
            # Extract JSON
            if "{" in response_text:
                json_start = response_text.index("{")
                json_end = response_text.rindex("}") + 1
                concept_map = json.loads(response_text[json_start:json_end])
                
                # Store in concept graph
                self._add_to_concept_graph(topic, concept_map)
                
                return concept_map
            else:
                return {}
                
        except Exception as e:
            print(f"❌ Concept mapping failed: {e}")
            return {}
    
    def _add_to_concept_graph(self, topic: str, concept_map: dict):
        """Add concept to the graph"""
        
        try:
            with open(self.concept_graph_file, 'r') as f:
                graph = json.load(f)
            
            # Add concept
            graph["concepts"][topic] = {
                "added": datetime.now().isoformat(),
                "understanding": concept_map
            }
            
            # Add relationships
            if "relationships" in concept_map:
                for related, rel_type in concept_map["relationships"].items():
                    graph["relationships"].append({
                        "from": topic,
                        "to": related,
                        "type": rel_type
                    })
            
            with open(self.concept_graph_file, 'w') as f:
                json.dump(graph, f, indent=2)
            
            print(f"✅ Added {topic} to concept graph")
            
        except Exception as e:
            print(f"❌ Failed to add to graph: {e}")
    
    def reason_about(self, question: str) -> dict:
        """Multi-step reasoning instead of pattern matching"""
        
        prompt = f"""Think step-by-step to answer this question.

Question: {question}

Use chain-of-thought reasoning:
1. What do I know that's relevant?
2. What can I infer from what I know?
3. What assumptions am I making?
4. What conclusion follows logically?
5. What uncertainty remains?

Format as JSON:
{{
    "known_facts": ["fact1"],
    "inferences": ["inference1"],
    "assumptions": ["assumption1"],
    "conclusion": "answer",
    "uncertainty": "what I'm not sure about",
    "confidence": 0.8
}}

Reasoning:"""

        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}],
                options={"temperature": 0.3, "num_predict": 300}
            )
            
            response_text = response['message']['content'].strip()
            
            # Extract JSON
            if "{" in response_text:
                json_start = response_text.index("{")
                json_end = response_text.rindex("}") + 1
                reasoning = json.loads(response_text[json_start:json_end])
                
                # Store reasoning chain
                self._save_reasoning_chain(question, reasoning)
                
                return reasoning
            else:
                return {"conclusion": response_text, "confidence": 0.5}
                
        except Exception as e:
            print(f"❌ Reasoning failed: {e}")
            return {"error": str(e)}
    
    def _save_reasoning_chain(self, question: str, reasoning: dict):
        """Save reasoning chain for learning"""
        
        try:
            with open(self.reasoning_chains_file, 'r') as f:
                chains = json.load(f)
            
            chains["chains"].append({
                "timestamp": datetime.now().isoformat(),
                "question": question,
                "reasoning": reasoning
            })
            
            # Keep only last 100 chains
            chains["chains"] = chains["chains"][-100:]
            
            with open(self.reasoning_chains_file, 'w') as f:
                json.dump(chains, f, indent=2)
                
        except Exception as e:
            print(f"❌ Failed to save reasoning: {e}")
    
    def understand_context(self, message: str, conversation_history: list) -> dict:
        """Deep contextual understanding"""
        
        history_text = "\n".join([f"{msg['user']}: {msg['text']}" for msg in conversation_history[-5:]])
        
        prompt = f"""Analyze this conversation for deep understanding.

Recent conversation:
{history_text}

Current message: {message}

Understand:
1. Explicit meaning - What are they literally saying?
2. Implicit meaning - What are they implying?
3. Emotional state - How do they feel?
4. Intent - What do they want?
5. Context shifts - Has the topic changed?

Format as JSON:
{{
    "explicit": "literal meaning",
    "implicit": "what's implied",
    "emotion": "emotional state",
    "intent": "what they want",
    "context_shift": true/false
}}

Understanding:"""

        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}],
                options={"temperature": 0.4}
            )
            
            response_text = response['message']['content'].strip()
            
            if "{" in response_text:
                json_start = response_text.index("{")
                json_end = response_text.rindex("}") + 1
                return json.loads(response_text[json_start:json_end])
            else:
                return {"explicit": message, "understanding": "partial"}
                
        except Exception as e:
            print(f"❌ Context understanding failed: {e}")
            return {}
    
    def get_understanding_stats(self) -> dict:
        """Get stats about Luna's understanding"""
        
        try:
            with open(self.concept_graph_file, 'r') as f:
                graph = json.load(f)
            
            with open(self.reasoning_chains_file, 'r') as f:
                chains = json.load(f)
            
            return {
                "concepts_understood": len(graph.get("concepts", {})),
                "relationships_mapped": len(graph.get("relationships", [])),
                "reasoning_chains": len(chains.get("chains", []))
            }
            
        except Exception as e:
            return {"error": str(e)}


# Add import at top
import os

if __name__ == "__main__":
    engine = UnderstandingEngine("hf.co/subsectmusic/qwriko3-4b-instruct-2507-redux-GGUF:Q4_K_M")
    
    # Test concept mapping
    concept = engine.build_concept_map("love")
    print(f"Concept: {concept}")
    
    # Test reasoning
    reasoning = engine.reason_about("If all cats are animals, and Luna likes animals, does Luna like cats?")
    print(f"Reasoning: {reasoning}")

