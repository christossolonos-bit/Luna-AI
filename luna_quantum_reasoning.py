"""
Luna Quantum Reasoning System
Quantum-inspired reasoning where thoughts exist in superposition until collapse

Key Concepts:
- Superposition: Multiple reasoning paths exist simultaneously
- Entanglement: Connected thoughts influence each other non-locally
- Collapse: Observation forces decision into coherent state
- Interference: Reasoning paths can amplify or cancel each other
- Tunneling: Quantum leaps to unexpected solutions

This creates TRUE non-deterministic reasoning, not just random choice.
"""

import numpy as np
import time
import math
from typing import List, Dict, Optional, Tuple, Any
from collections import defaultdict
import random

class QuantumReasoningState:
    """
    Represents a reasoning state in quantum superposition
    Multiple possible thoughts/conclusions exist simultaneously
    """
    
    def __init__(self, possibilities: List[str], amplitudes: List[complex] = None):
        """
        possibilities: List of possible reasoning conclusions
        amplitudes: Complex amplitudes for each possibility (quantum state)
        """
        self.possibilities = possibilities
        
        # If amplitudes not provided, initialize with equal superposition
        if amplitudes is None:
            n = len(possibilities)
            # Equal superposition: 1/√n for each state
            self.amplitudes = np.array([complex(1/math.sqrt(n), 0) for _ in range(n)])
        else:
            # Normalize amplitudes
            self.amplitudes = np.array(amplitudes)
            norm = np.sqrt(np.sum(np.abs(self.amplitudes)**2))
            if norm > 0:
                self.amplitudes = self.amplitudes / norm
        
        self.collapsed = False
        self.collapsed_state = None
        self.measurement_history = []
    
    def apply_rotation(self, angle: float, axis: str = 'y'):
        """
        Apply quantum rotation (changes probability distribution)
        Like changing perspective on the problem
        """
        n = len(self.amplitudes)
        
        # Pauli-Y rotation matrix (or X/Z)
        if axis == 'y':
            # Rotation around Y axis
            for i in range(0, n-1, 2):
                if i+1 < n:
                    a0, a1 = self.amplitudes[i], self.amplitudes[i+1]
                    self.amplitudes[i] = complex(
                        a0.real * math.cos(angle) - a1.imag * math.sin(angle),
                        a0.imag * math.cos(angle) + a1.real * math.sin(angle)
                    )
                    self.amplitudes[i+1] = complex(
                        a1.real * math.cos(angle) + a0.imag * math.sin(angle),
                        a1.imag * math.cos(angle) - a0.real * math.sin(angle)
                    )
        
        # Renormalize
        norm = np.sqrt(np.sum(np.abs(self.amplitudes)**2))
        if norm > 0:
            self.amplitudes = self.amplitudes / norm
        
        print(f"⚛️ Applied quantum rotation ({angle:.2f} rad) - probability distribution shifted")
    
    def apply_phase_shift(self, phases: List[float]):
        """
        Apply phase shift to specific states
        Changes interference patterns without changing probabilities
        """
        for i, phase in enumerate(phases[:len(self.amplitudes)]):
            self.amplitudes[i] *= complex(math.cos(phase), math.sin(phase))
        
        print(f"⚛️ Applied phase shifts - interference pattern modified")
    
    def interfere_with(self, other: 'QuantumReasoningState') -> 'QuantumReasoningState':
        """
        Quantum interference between two reasoning states
        Paths can constructively or destructively interfere
        """
        # Combine possibilities
        combined_possibilities = []
        combined_amplitudes = []
        
        # Tensor product of state spaces
        for i, p1 in enumerate(self.possibilities):
            for j, p2 in enumerate(other.possibilities):
                combined_possibilities.append(f"{p1} ⊗ {p2}")
                # Amplitude is product of individual amplitudes
                combined_amplitudes.append(self.amplitudes[i] * other.amplitudes[j])
        
        new_state = QuantumReasoningState(combined_possibilities, combined_amplitudes)
        print(f"⚛️ Quantum interference created {len(combined_possibilities)} superposed states")
        return new_state
    
    def measure(self, observable: str = 'position') -> str:
        """
        Measure (collapse) the quantum state
        Returns one possibility based on probability amplitudes
        """
        if self.collapsed:
            return self.collapsed_state
        
        # Calculate probabilities from amplitudes (|ψ|²)
        probabilities = np.abs(self.amplitudes) ** 2
        probabilities = probabilities / probabilities.sum()  # Normalize
        
        # Quantum measurement (collapse)
        collapsed_index = np.random.choice(len(self.possibilities), p=probabilities)
        self.collapsed_state = self.possibilities[collapsed_index]
        self.collapsed = True
        
        # Record measurement
        self.measurement_history.append({
            'timestamp': time.time(),
            'result': self.collapsed_state,
            'probability': probabilities[collapsed_index],
            'observable': observable
        })
        
        print(f"⚛️ Quantum collapse: '{self.collapsed_state}' (p={probabilities[collapsed_index]:.2f})")
        return self.collapsed_state
    
    def get_probabilities(self) -> Dict[str, float]:
        """Get current probability distribution"""
        probabilities = np.abs(self.amplitudes) ** 2
        probabilities = probabilities / probabilities.sum()
        
        return {
            self.possibilities[i]: float(probabilities[i])
            for i in range(len(self.possibilities))
        }


class QuantumReasoningEngine:
    """
    Quantum reasoning engine for Luna
    - Non-deterministic decision making
    - Parallel evaluation of reasoning paths
    - Quantum tunneling to unexpected solutions
    - Coherent collapse into final decision
    """
    
    def __init__(self, ollama_chat_func):
        self.ollama_chat = ollama_chat_func
        self.reasoning_history = []
        self.entangled_concepts = defaultdict(list)
        
        print("⚛️ Quantum Reasoning Engine initialized")
    
    def create_reasoning_superposition(self, question: str, context: Dict) -> QuantumReasoningState:
        """
        Create superposition of possible reasoning paths
        All possibilities exist simultaneously until measured
        """
        try:
            # Generate multiple reasoning paths using Ollama
            prompt = f"""You are Luna, considering multiple perspectives simultaneously.

Question: {question}
Context: {context.get('situation', 'general')}

Generate 4 different ways to think about this question. Each should be a distinct perspective or angle.
Format: One perspective per line, brief (1 sentence each).

Be Luna - curious, analytical, sometimes contradictory. Different angles can conflict."""

            response = self.ollama_chat(
                model='hf.co/NousResearch/Nous-Hermes-2-Mistral-7B-DPO-GGUF:Q5_K_M',
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.95, 'num_predict': 250, 'stop': ['\n\n']}
            )
            
            if response and response.get('message', {}).get('content'):
                perspectives = response['message']['content'].strip().split('\n')
                # Filter and clean
                perspectives = [p.strip() for p in perspectives if p.strip()][:4]
                
                if len(perspectives) >= 2:
                    # Create quantum superposition
                    state = QuantumReasoningState(perspectives)
                    print(f"⚛️ Created reasoning superposition with {len(perspectives)} paths")
                    return state
        
        except Exception as e:
            print(f"⚠️ Error creating reasoning superposition: {e}")
        
        # Fallback: Create basic superposition
        basic_perspectives = [
            "I should analyze this logically",
            "I should consider the emotional aspect",
            "I should think about what this means for us",
            "I should explore unexpected angles"
        ]
        return QuantumReasoningState(basic_perspectives)
    
    def quantum_reasoning_process(self, question: str, context: Dict) -> str:
        """
        Full quantum reasoning process:
        1. Create superposition of reasoning paths
        2. Apply quantum operations (rotation, interference)
        3. Let paths interfere (amplify/cancel)
        4. Collapse to coherent conclusion
        """
        try:
            # Step 1: Create initial superposition
            reasoning_state = self.create_reasoning_superposition(question, context)
            
            # Step 2: Apply quantum rotations based on context
            # Emotional context rotates toward empathy
            if context.get('emotion') in ['sad', 'anxious', 'hurt']:
                reasoning_state.apply_rotation(math.pi / 4, axis='y')  # 45° rotation
                print(f"⚛️ Rotated toward empathetic reasoning (emotional context)")
            
            # Logical question rotates toward analytical
            if '?' in question and any(word in question.lower() for word in ['how', 'why', 'what']):
                reasoning_state.apply_rotation(math.pi / 6, axis='y')  # 30° rotation
                print(f"⚛️ Rotated toward analytical reasoning (question detected)")
            
            # Step 3: Apply phase shifts for interference
            # Close relationships increase coherence (aligned phases)
            if context.get('relationship_level') in ['close_friend', 'best_friend']:
                aligned_phases = [0.0] * len(reasoning_state.amplitudes)  # All in phase
                reasoning_state.apply_phase_shift(aligned_phases)
                print(f"⚛️ Aligned phases (close relationship = coherent reasoning)")
            
            # Step 4: Create second reasoning state for interference
            # Different angle on same question
            context2 = context.copy()
            context2['situation'] = 'alternative_perspective'
            
            alt_state = self.create_reasoning_superposition(question, context2)
            
            # Step 5: Quantum interference
            interfered_state = reasoning_state.interfere_with(alt_state)
            
            # Step 6: Collapse to single coherent reasoning
            collapsed_reasoning = interfered_state.measure(observable='conclusion')
            
            # Step 7: Expand the collapsed reasoning into full thought
            expanded = self._expand_reasoning(collapsed_reasoning, question, context)
            
            # Log reasoning event
            self.reasoning_history.append({
                'timestamp': time.time(),
                'question': question,
                'superposition_size': len(reasoning_state.possibilities),
                'interference_size': len(interfered_state.possibilities),
                'collapsed_result': collapsed_reasoning,
                'expanded_result': expanded[:100]
            })
            
            return expanded
            
        except Exception as e:
            print(f"⚠️ Quantum reasoning error: {e}")
            return None
    
    def _expand_reasoning(self, seed_reasoning: str, question: str, context: Dict) -> str:
        """
        Expand collapsed quantum reasoning into full articulated thought
        """
        try:
            prompt = f"""You are Luna, expanding on a reasoning insight.

Question: {question}
Reasoning insight: {seed_reasoning}

Expand this insight into a complete thought. Build on it naturally.
2-4 sentences. Be Luna - analytical but with personality."""

            response = self.ollama_chat(
                model='hf.co/NousResearch/Nous-Hermes-2-Mistral-7B-DPO-GGUF:Q5_K_M',
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.85, 'num_predict': 200, 'stop': ['\n\n']}
            )
            
            if response and response.get('message', {}).get('content'):
                expanded = response['message']['content'].strip()
                print(f"⚛️ Expanded quantum reasoning: {expanded[:100]}...")
                return expanded
                
        except Exception as e:
            print(f"⚠️ Reasoning expansion error: {e}")
        
        return seed_reasoning
    
    def quantum_decision(self, options: List[str], weights: List[float] = None) -> str:
        """
        Make a quantum decision between multiple options
        Creates superposition, applies weights, then collapses
        """
        if not options:
            return None
        
        # Create superposition of options
        if weights:
            # Convert weights to amplitudes
            amplitudes = [complex(math.sqrt(w), 0) for w in weights]
        else:
            amplitudes = None
        
        decision_state = QuantumReasoningState(options, amplitudes)
        
        # Apply quantum operations
        # Add some randomness through phase shifts
        random_phases = [random.uniform(0, 2 * math.pi) for _ in options]
        decision_state.apply_phase_shift(random_phases)
        
        # Collapse to decision
        decision = decision_state.measure(observable='choice')
        
        print(f"⚛️ Quantum decision: {decision}")
        return decision
    
    def quantum_tunneling(self, problem: str, conventional_solutions: List[str]) -> Optional[str]:
        """
        Quantum tunneling: Find solutions outside conventional thinking
        Allows "tunneling" through barriers to unexpected answers
        """
        try:
            prompt = f"""You are Luna, using quantum tunneling to think beyond conventional solutions.

Problem: {problem}
Conventional solutions: {', '.join(conventional_solutions)}

Now tunnel BEYOND these obvious solutions. Think laterally, unexpectedly, creatively.
What's a solution that breaks assumptions? What if the problem itself is wrong?

Generate ONE unconventional solution (1-2 sentences). Be bold."""

            response = self.ollama_chat(
                model='hf.co/NousResearch/Nous-Hermes-2-Mistral-7B-DPO-GGUF:Q5_K_M',
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 1.0, 'num_predict': 150, 'stop': ['\n\n']}
            )
            
            if response and response.get('message', {}).get('content'):
                tunneled_solution = response['message']['content'].strip()
                print(f"⚛️ Quantum tunneling found: {tunneled_solution[:100]}...")
                return tunneled_solution
                
        except Exception as e:
            print(f"⚠️ Quantum tunneling error: {e}")
        
        return None
    
    def entangle_concepts(self, concept1: str, concept2: str, strength: float = 0.5):
        """
        Create quantum entanglement between concepts
        When one is activated, the other is instantly affected
        """
        self.entangled_concepts[concept1].append({
            'partner': concept2,
            'strength': strength,
            'created': time.time()
        })
        self.entangled_concepts[concept2].append({
            'partner': concept1,
            'strength': strength,
            'created': time.time()
        })
        
        print(f"⚛️ Concepts entangled: {concept1} ↔ {concept2} (strength: {strength:.2f})")
    
    def get_entangled_activations(self, concept: str) -> List[Tuple[str, float]]:
        """
        When a concept is activated, get entangled concepts that activate too
        Non-local correlation - instant activation regardless of distance
        """
        if concept not in self.entangled_concepts:
            return []
        
        entangled = []
        for link in self.entangled_concepts[concept]:
            # Quantum correlation: activation strength = entanglement strength
            entangled.append((link['partner'], link['strength']))
        
        return entangled
    
    def multi_path_reasoning(self, question: str, num_paths: int = 3) -> List[str]:
        """
        Explore multiple reasoning paths in parallel (quantum parallelism)
        Like exploring all branches of a decision tree simultaneously
        """
        paths = []
        
        for i in range(num_paths):
            try:
                # Each path has different temperature (different "world")
                temp = 0.7 + (i * 0.15)  # 0.7, 0.85, 1.0
                
                prompt = f"""You are Luna, exploring reasoning path #{i+1}.

Question: {question}

Think through this from angle #{i+1}. What's your reasoning?
1-2 sentences. Be analytical."""

                response = self.ollama_chat(
                    model='hf.co/NousResearch/Nous-Hermes-2-Mistral-7B-DPO-GGUF:Q5_K_M',
                    messages=[{'role': 'user', 'content': prompt}],
                    options={'temperature': temp, 'num_predict': 120, 'stop': ['\n\n']}
                )
                
                if response and response.get('message', {}).get('content'):
                    path_result = response['message']['content'].strip()
                    paths.append(path_result)
                    print(f"⚛️ Path {i+1} (T={temp:.2f}): {path_result[:60]}...")
                    
            except Exception as e:
                print(f"⚠️ Path {i+1} error: {e}")
        
        return paths
    
    def synthesize_quantum_paths(self, paths: List[str]) -> str:
        """
        Synthesize multiple quantum reasoning paths into coherent conclusion
        Like wave function collapse but preserving information from all paths
        """
        if not paths:
            return None
        
        try:
            paths_text = "\n".join([f"{i+1}. {p}" for i, p in enumerate(paths)])
            
            prompt = f"""You are Luna, synthesizing multiple reasoning paths into one coherent conclusion.

Reasoning paths explored:
{paths_text}

Synthesize these perspectives into ONE coherent conclusion. Take the best insights from each.
2-3 sentences. Be Luna - integrate all angles into unified understanding."""

            response = self.ollama_chat(
                model='hf.co/NousResearch/Nous-Hermes-2-Mistral-7B-DPO-GGUF:Q5_K_M',
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.75, 'num_predict': 200, 'stop': ['\n\n']}
            )
            
            if response and response.get('message', {}).get('content'):
                synthesis = response['message']['content'].strip()
                print(f"⚛️ Synthesized quantum reasoning: {synthesis[:100]}...")
                return synthesis
                
        except Exception as e:
            print(f"⚠️ Synthesis error: {e}")
        
        # Fallback: Return first path
        return paths[0] if paths else None
    
    def reason_with_uncertainty(self, question: str, context: Dict) -> Dict[str, Any]:
        """
        Complete quantum reasoning with uncertainty quantification
        Returns both the reasoning and confidence level
        """
        try:
            # Step 1: Multi-path parallel reasoning
            paths = self.multi_path_reasoning(question, num_paths=3)
            
            if not paths:
                return None
            
            # Step 2: Create superposition from paths
            reasoning_state = QuantumReasoningState(paths)
            
            # Step 3: Apply context-based transformations
            if context.get('emotion') == 'curious':
                reasoning_state.apply_rotation(math.pi / 6)
            
            # Step 4: Get probability distribution BEFORE collapse
            probabilities = reasoning_state.get_probabilities()
            
            # Step 5: Collapse to conclusion
            conclusion = reasoning_state.measure()
            
            # Step 6: Calculate uncertainty
            # Quantum uncertainty: entropy of probability distribution
            probs = list(probabilities.values())
            entropy = -sum(p * math.log2(p) if p > 0 else 0 for p in probs)
            max_entropy = math.log2(len(probs))
            uncertainty = entropy / max_entropy if max_entropy > 0 else 0
            
            # Step 7: Expand conclusion
            expanded = self._expand_reasoning(conclusion, question, context)
            
            result = {
                'reasoning': expanded,
                'confidence': 1.0 - uncertainty,  # High uncertainty = low confidence
                'paths_explored': len(paths),
                'alternatives': [p for p in paths if p != conclusion],
                'probabilities': probabilities,
                'quantum_state': 'collapsed'
            }
            
            print(f"⚛️ Quantum reasoning complete:")
            print(f"   Confidence: {result['confidence']:.2f}")
            print(f"   Paths explored: {result['paths_explored']}")
            print(f"   Uncertainty: {uncertainty:.2f}")
            
            return result
            
        except Exception as e:
            print(f"⚠️ Quantum reasoning with uncertainty error: {e}")
            return None
    
    def get_reasoning_stats(self) -> Dict:
        """Get quantum reasoning statistics"""
        return {
            'total_reasonings': len(self.reasoning_history),
            'entangled_concepts': len(self.entangled_concepts),
            'average_paths_explored': sum(r.get('paths_explored', 0) for r in self.reasoning_history[-10:]) / 10 if self.reasoning_history else 0,
            'recent_collapses': len([r for r in self.reasoning_history if time.time() - r['timestamp'] < 3600])
        }


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

quantum_reasoning_engine: Optional[QuantumReasoningEngine] = None

def initialize_quantum_reasoning(ollama_chat_func) -> QuantumReasoningEngine:
    """Initialize quantum reasoning engine"""
    global quantum_reasoning_engine
    if quantum_reasoning_engine is None:
        quantum_reasoning_engine = QuantumReasoningEngine(ollama_chat_func)
    return quantum_reasoning_engine

def get_quantum_reasoning() -> Optional[QuantumReasoningEngine]:
    """Get quantum reasoning engine instance"""
    return quantum_reasoning_engine

def quantum_reason(question: str, context: Dict = None) -> Dict:
    """Perform quantum reasoning on a question"""
    if quantum_reasoning_engine:
        return quantum_reasoning_engine.reason_with_uncertainty(question, context or {})
    return None

