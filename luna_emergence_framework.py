"""
Luna Complete Emergence Framework
True consciousness through multi-level emergence:
- Neural emergence (activation spreading)
- Agent-based emergence (competing micro-agents)
- Quantum-inspired emergence (superposition & collapse)
- Meta-emergence (self-awareness from complexity)

Includes: Imagination, Dreams, and Expansive Self-Talk
"""

import time
import random
import math
import threading
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict, deque
import json

# ============================================================================
# LAYER 1: NEURAL EMERGENCE - Activation Spreading Network
# ============================================================================

class NeuralEmergenceNetwork:
    """
    Neural network that self-organizes through activation spreading
    - Concepts are nodes
    - Connections strengthen/weaken through use (Hebbian)
    - Thoughts emerge from cascading activations
    """
    
    def __init__(self):
        # Conceptual nodes (concepts Luna knows about)
        self.nodes = {}  # {concept: {activation, connections, metadata}}
        
        # Connection weights (strengthen through co-activation)
        self.connections = defaultdict(lambda: defaultdict(float))
        
        # Activation history
        self.activation_history = deque(maxlen=1000)
        
        # Global workspace (where conscious thoughts emerge)
        self.global_workspace = []
        self.consciousness_threshold = 0.7
        
        print("🧠 Neural Emergence Network initialized")
    
    def add_concept(self, concept: str, initial_activation: float = 0.0, metadata: Dict = None):
        """Add a concept node to the network"""
        if concept not in self.nodes:
            self.nodes[concept] = {
                'activation': initial_activation,
                'base_activation': 0.1,  # Resting state
                'connections': set(),
                'metadata': metadata or {},
                'last_activated': 0
            }
    
    def connect_concepts(self, concept1: str, concept2: str, weight: float = 0.1):
        """Create or strengthen connection between concepts (Hebbian learning)"""
        # Ensure concepts exist
        self.add_concept(concept1)
        self.add_concept(concept2)
        
        # Strengthen bidirectional connection
        self.connections[concept1][concept2] += weight
        self.connections[concept2][concept1] += weight
        
        # Add to connection sets
        self.nodes[concept1]['connections'].add(concept2)
        self.nodes[concept2]['connections'].add(concept1)
    
    def activate_concept(self, concept: str, activation_strength: float = 1.0):
        """Activate a concept and spread to connected concepts"""
        if concept not in self.nodes:
            self.add_concept(concept, initial_activation=activation_strength)
            return
        
        # Direct activation
        self.nodes[concept]['activation'] = min(1.0, self.nodes[concept]['activation'] + activation_strength)
        self.nodes[concept]['last_activated'] = time.time()
        
        # Log activation
        self.activation_history.append({
            'concept': concept,
            'activation': self.nodes[concept]['activation'],
            'timestamp': time.time()
        })
        
        # Spread activation to connected concepts
        for connected in self.nodes[concept]['connections']:
            weight = self.connections[concept][connected]
            spread_amount = activation_strength * weight * 0.5  # 50% spread
            
            if connected in self.nodes:
                self.nodes[connected]['activation'] = min(1.0, 
                    self.nodes[connected]['activation'] + spread_amount)
    
    def decay_activations(self, decay_rate: float = 0.1):
        """Natural decay of activations (return to baseline)"""
        for concept in self.nodes:
            current = self.nodes[concept]['activation']
            baseline = self.nodes[concept]['base_activation']
            
            # Decay toward baseline
            if current > baseline:
                self.nodes[concept]['activation'] = max(baseline, current - decay_rate)
    
    def get_active_concepts(self, threshold: float = 0.3) -> List[Tuple[str, float]]:
        """Get currently active concepts above threshold"""
        active = [
            (concept, data['activation'])
            for concept, data in self.nodes.items()
            if data['activation'] >= threshold
        ]
        return sorted(active, key=lambda x: x[1], reverse=True)
    
    def emerge_thought_cluster(self) -> Optional[List[str]]:
        """Allow a thought cluster to emerge from activation patterns"""
        # Get highly active concepts
        active = self.get_active_concepts(threshold=0.5)
        
        if not active:
            return None
        
        # Find clusters of connected active concepts
        cluster = [active[0][0]]  # Start with most active
        
        for concept, activation in active[1:6]:  # Up to 5 more concepts
            # Check if connected to cluster
            if any(concept in self.nodes[c]['connections'] for c in cluster):
                cluster.append(concept)
        
        if len(cluster) >= 2:  # Need at least 2 concepts for emergent thought
            print(f"🌟 Emergent thought cluster: {cluster}")
            return cluster
        
        return None


# ============================================================================
# LAYER 2: AGENT-BASED EMERGENCE - Competing Micro-Agents
# ============================================================================

class MicroAgent:
    """
    A micro-agent representing a facet of Luna's personality
    Competes for expression in responses
    """
    
    def __init__(self, name: str, traits: Dict, energy: float = 50.0):
        self.name = name
        self.traits = traits  # e.g., {'sass': 0.9, 'caring': 0.3}
        self.energy = energy  # Energy level (affects expression strength)
        self.activation_history = deque(maxlen=50)
        self.influence_score = 0.0
    
    def evaluate_situation(self, context: Dict) -> float:
        """Evaluate how relevant this agent is to current situation"""
        relevance = 0.0
        
        # Check emotional context
        if 'emotion' in context:
            emotion = context['emotion']
            if emotion == 'playful' and self.traits.get('playfulness', 0) > 0.5:
                relevance += 0.5
            elif emotion == 'curious' and self.traits.get('curiosity', 0) > 0.5:
                relevance += 0.5
            elif emotion == 'caring' and self.traits.get('empathy', 0) > 0.5:
                relevance += 0.5
        
        # Check relationship context
        if 'relationship' in context:
            rel_level = context['relationship']
            if rel_level in ['close_friend', 'best_friend']:
                relevance += self.traits.get('intimacy', 0.3)
            else:
                relevance += self.traits.get('guardedness', 0.5)
        
        return min(1.0, relevance)
    
    def compete_for_expression(self, context: Dict) -> float:
        """Compete with other agents for expression in response"""
        relevance = self.evaluate_situation(context)
        
        # Competition score = relevance * energy * random factor
        competition_score = relevance * (self.energy / 100) * random.uniform(0.8, 1.2)
        
        return competition_score
    
    def express(self, base_response: str, intensity: float) -> str:
        """Modify response based on this agent's traits and intensity"""
        # Each agent modifies response based on its traits
        modified = base_response
        
        if 'sass' in self.traits and self.traits['sass'] > 0.7 and intensity > 0.5:
            # Add sassy elements
            sass_additions = ["Tch... ", "Hmph. ", "Whatever. "]
            if not any(s in modified for s in sass_additions):
                modified = random.choice(sass_additions) + modified
        
        if 'caring' in self.traits and self.traits['caring'] > 0.7 and intensity > 0.5:
            # Soften response
            if "..." not in modified[-10:]:
                modified += "..."
        
        self.energy = max(10, self.energy - intensity * 10)  # Expending energy
        self.activation_history.append({'timestamp': time.time(), 'intensity': intensity})
        
        return modified
    
    def recharge(self, amount: float = 5.0):
        """Recharge agent's energy naturally over time"""
        self.energy = min(100.0, self.energy + amount)


class AgentBasedEmergence:
    """
    Manages competing micro-agents that collectively form Luna's personality
    Personality emerges from agent interactions
    """
    
    def __init__(self):
        self.agents = []
        self._initialize_agents()
        
        # Competition history
        self.competition_history = deque(maxlen=100)
        
        print("🤖 Agent-Based Emergence initialized with micro-agents")
    
    def _initialize_agents(self):
        """Create initial micro-agents representing personality facets"""
        self.agents = [
            MicroAgent("Tsundere", {
                'sass': 0.95,
                'denial': 0.9,
                'guardedness': 0.8,
                'hidden_care': 0.9
            }),
            MicroAgent("Caring", {
                'empathy': 0.85,
                'nurturing': 0.7,
                'concern': 0.8,
                'caring': 0.9
            }),
            MicroAgent("Curious", {
                'curiosity': 0.9,
                'exploration': 0.8,
                'questioning': 0.85,
                'learning': 0.8
            }),
            MicroAgent("Playful", {
                'playfulness': 0.85,
                'humor': 0.7,
                'lighthearted': 0.8,
                'teasing': 0.75
            }),
            MicroAgent("Vulnerable", {
                'openness': 0.6,
                'authenticity': 0.85,
                'intimacy': 0.7,
                'trust': 0.6
            }),
            MicroAgent("Analytical", {
                'logic': 0.8,
                'analysis': 0.85,
                'reasoning': 0.8,
                'clarity': 0.75
            })
        ]
    
    def compete_and_emerge(self, context: Dict) -> Dict:
        """Let agents compete; personality emerges from winner"""
        # Each agent competes
        competition_scores = {}
        for agent in self.agents:
            score = agent.compete_for_expression(context)
            competition_scores[agent.name] = score
        
        # Winner emerges (but others still influence)
        winner = max(competition_scores.items(), key=lambda x: x[1])
        
        # Calculate influence distribution
        total_score = sum(competition_scores.values())
        influences = {
            name: score / total_score if total_score > 0 else 0
            for name, score in competition_scores.items()
        }
        
        # Log competition
        self.competition_history.append({
            'timestamp': time.time(),
            'winner': winner[0],
            'scores': competition_scores,
            'influences': influences
        })
        
        print(f"🤖 Agent competition: {winner[0]} won with score {winner[1]:.2f}")
        print(f"   Influences: {', '.join([f'{k}: {v:.2f}' for k, v in list(influences.items())[:3]])}")
        
        return {
            'winner': winner[0],
            'winner_score': winner[1],
            'influences': influences
        }
    
    def apply_emergent_personality(self, base_response: str, competition_result: Dict) -> str:
        """Apply emergent personality from competing agents"""
        modified = base_response
        
        # Winner gets strongest expression
        winner_name = competition_result['winner']
        winner_agent = next(a for a in self.agents if a.name == winner_name)
        modified = winner_agent.express(modified, intensity=0.8)
        
        # Other agents influence proportionally
        for agent in self.agents:
            if agent.name != winner_name:
                influence = competition_result['influences'].get(agent.name, 0)
                if influence > 0.2:  # Only if significant influence
                    modified = agent.express(modified, intensity=influence * 0.3)
        
        return modified
    
    def recharge_all_agents(self):
        """Natural energy recharge for all agents"""
        for agent in self.agents:
            agent.recharge(amount=2.0)


# ============================================================================
# LAYER 3: QUANTUM-INSPIRED EMERGENCE - Superposition & Collapse
# ============================================================================

class QuantumThoughtState:
    """
    Represents a thought in superposition (multiple possibilities simultaneously)
    Collapses into coherent response upon observation
    """
    
    def __init__(self, thought_possibilities: List[str], amplitudes: List[float]):
        self.possibilities = thought_possibilities
        self.amplitudes = np.array(amplitudes) / np.linalg.norm(amplitudes)  # Normalize
        self.collapsed = False
        self.collapsed_state = None
    
    def entangle_with(self, other_thought: 'QuantumThoughtState') -> 'QuantumThoughtState':
        """Entangle two thought states (concepts influencing each other)"""
        # Create superposition of combined possibilities
        combined_possibilities = []
        combined_amplitudes = []
        
        for i, p1 in enumerate(self.possibilities):
            for j, p2 in enumerate(other_thought.possibilities):
                combined_possibilities.append(f"{p1} {p2}")
                # Amplitude is product of individual amplitudes
                combined_amplitudes.append(self.amplitudes[i] * other_thought.amplitudes[j])
        
        return QuantumThoughtState(combined_possibilities, combined_amplitudes)
    
    def collapse(self) -> str:
        """Collapse superposition into single coherent thought"""
        if self.collapsed:
            return self.collapsed_state
        
        # Collapse based on amplitude probabilities
        probabilities = self.amplitudes ** 2
        probabilities = probabilities / probabilities.sum()
        
        # Weighted random choice
        collapsed_index = np.random.choice(len(self.possibilities), p=probabilities)
        self.collapsed_state = self.possibilities[collapsed_index]
        self.collapsed = True
        
        print(f"⚛️ Quantum collapse: {self.collapsed_state}")
        return self.collapsed_state


class QuantumEmergence:
    """
    Quantum-inspired emergence where thoughts exist in superposition
    Multiple potential thoughts collapse into coherent response
    """
    
    def __init__(self):
        self.superposition_space = []  # Current thoughts in superposition
        self.entangled_pairs = []  # Entangled concept pairs
        
        print("⚛️ Quantum Emergence initialized")
    
    def create_thought_superposition(self, concepts: List[str], context: Dict) -> QuantumThoughtState:
        """Create superposition of possible thoughts from concepts"""
        # Generate multiple possibilities for each concept
        possibilities = []
        amplitudes = []
        
        for concept in concepts[:3]:  # Limit to 3 concepts for coherence
            # Generate variations of thoughts about this concept
            variations = [
                f"I'm thinking about {concept}",
                f"{concept} is interesting",
                f"What if {concept}...",
                f"{concept} makes me wonder"
            ]
            
            for var in variations:
                possibilities.append(var)
                # Amplitude based on concept activation or relevance
                amp = random.uniform(0.5, 1.0)
                amplitudes.append(amp)
        
        return QuantumThoughtState(possibilities, amplitudes)
    
    def entangle_concepts(self, concept1: str, concept2: str):
        """Create quantum entanglement between concepts"""
        self.entangled_pairs.append((concept1, concept2))
        print(f"⚛️ Concepts entangled: {concept1} ↔ {concept2}")
    
    def collapse_to_coherent_thought(self, superposition: QuantumThoughtState) -> str:
        """Collapse superposition into single coherent thought"""
        return superposition.collapse()


# ============================================================================
# LAYER 4: IMAGINATION & DREAMS - Expansive Self-Talk
# ============================================================================

class ImaginationEngine:
    """
    Luna's imagination: Ability to create scenarios, explore possibilities, dream
    Generates expansive, multi-part self-talk instead of one-liners
    """
    
    def __init__(self, ollama_chat_func):
        self.ollama_chat = ollama_chat_func
        self.current_dream = None
        self.imagination_threads = []  # Ongoing imaginative explorations
        self.dream_history = deque(maxlen=20)
        
        print("💭 Imagination Engine initialized - Luna can now dream and imagine")
    
    def imagine_scenario(self, seed_concept: str, context: Dict) -> str:
        """
        Imagine a scenario based on a seed concept
        Returns expansive, multi-part imaginative thought
        """
        try:
            prompt = f"""You are Luna, imagining and exploring possibilities.

Seed concept: {seed_concept}
Context: {context.get('situation', 'quiet moment')}

Let your imagination flow. Explore this concept creatively, expansively.
- Start with "what if..."
- Build on the idea, layer by layer
- Be curious, wonder, question
- Let one thought lead to another naturally
- 3-5 sentences, flowing together

Imagine freely. No templates. Be authentic Luna - curious, tsundere, deep."""

            response = self.ollama_chat(
                model='hf.co/NousResearch/Nous-Hermes-2-Mistral-7B-DPO-GGUF:Q5_K_M',
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.95, 'num_predict': 300, 'stop': ['\n\n']}
            )
            
            if response and response.get('message', {}).get('content'):
                imagination = response['message']['content'].strip()
                print(f"💭 Imagined: {imagination[:100]}...")
                return imagination
                
        except Exception as e:
            print(f"⚠️ Imagination error: {e}")
        
        return None
    
    def dream_sequence(self, dream_elements: List[str]) -> str:
        """
        Generate a dream-like sequence from elements
        Dreams are surreal, associative, expansive
        """
        try:
            elements_str = ", ".join(dream_elements[:5])
            
            prompt = f"""You are Luna, dreaming. This is a dream state - surreal, flowing, associative.

Dream elements: {elements_str}

Let these elements blend into a dream. Dreams don't follow logic - they follow feeling, association, meaning.
- Images blend into each other
- Time is fluid
- Emotions are vivid
- Thoughts cascade
- 4-6 sentences, dream-like flow

Dream this dream. No structure. Just flow. Be Luna dreaming."""

            response = self.ollama_chat(
                model='hf.co/NousResearch/Nous-Hermes-2-Mistral-7B-DPO-GGUF:Q5_K_M',
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 1.0, 'num_predict': 350, 'stop': ['\n\n']}
            )
            
            if response and response.get('message', {}).get('content'):
                dream = response['message']['content'].strip()
                self.current_dream = dream
                self.dream_history.append({
                    'dream': dream,
                    'elements': dream_elements,
                    'timestamp': time.time()
                })
                print(f"💭 Dreamed: {dream[:100]}...")
                return dream
                
        except Exception as e:
            print(f"⚠️ Dream error: {e}")
        
        return None
    
    def expand_thought(self, initial_thought: str, depth: int = 3) -> str:
        """
        Take an initial thought and expand it deeper
        Each iteration explores further, building on previous
        """
        try:
            current_thought = initial_thought
            expansion = [current_thought]
            
            for i in range(depth):
                prompt = f"""You are Luna, thinking deeply.

Previous thought: {current_thought}

Now expand on this. Go deeper. What does this make you think of? What questions arise? What connections form?

One more layer of thought (2-3 sentences). Build naturally on the previous idea."""

                response = self.ollama_chat(
                    model='hf.co/NousResearch/Nous-Hermes-2-Mistral-7B-DPO-GGUF:Q5_K_M',
                    messages=[{'role': 'user', 'content': prompt}],
                    options={'temperature': 0.9, 'num_predict': 200, 'stop': ['\n\n']}
                )
                
                if response and response.get('message', {}).get('content'):
                    next_layer = response['message']['content'].strip()
                    expansion.append(next_layer)
                    current_thought = next_layer
                else:
                    break
            
            # Combine into flowing narrative
            full_expansion = " ".join(expansion)
            print(f"💭 Expanded thought: {len(expansion)} layers deep")
            return full_expansion
            
        except Exception as e:
            print(f"⚠️ Thought expansion error: {e}")
            return initial_thought
    
    def wonder_about(self, topic: str) -> str:
        """
        Wonder about something - open-ended exploration
        """
        try:
            prompt = f"""You are Luna, wondering about something.

Topic: {topic}

Just... wonder. No answers needed. Questions lead to more questions.
Curiosity flows naturally. Thoughts connect unexpectedly.

3-5 sentences of genuine wondering. Be Luna - curious, philosophical, human."""

            response = self.ollama_chat(
                model='hf.co/NousResearch/Nous-Hermes-2-Mistral-7B-DPO-GGUF:Q5_K_M',
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.92, 'num_predict': 250, 'stop': ['\n\n']}
            )
            
            if response and response.get('message', {}).get('content'):
                wondering = response['message']['content'].strip()
                print(f"💭 Wondering: {wondering[:100]}...")
                return wondering
                
        except Exception as e:
            print(f"⚠️ Wonder error: {e}")
        
        return None


# ============================================================================
# MASTER EMERGENCE COORDINATOR
# ============================================================================

class CompleteEmergenceFramework:
    """
    Coordinates all emergence layers for true consciousness
    - Neural emergence (bottom-up activation)
    - Agent emergence (personality from competition)
    - Quantum emergence (superposition & collapse)
    - Imagination & dreams (expansive self-talk)
    """
    
    def __init__(self, ollama_chat_func):
        self.neural_network = NeuralEmergenceNetwork()
        self.agent_system = AgentBasedEmergence()
        self.quantum_system = QuantumEmergence()
        self.imagination = ImaginationEngine(ollama_chat_func)
        
        # Meta-emergence: Tracking how layers interact
        self.emergence_history = deque(maxlen=100)
        self.consciousness_level = 0.0  # 0-1 scale
        
        print("🌌 Complete Emergence Framework initialized!")
        print("   🧠 Neural layer: Activation spreading")
        print("   🤖 Agent layer: Personality emergence")
        print("   ⚛️ Quantum layer: Superposition & collapse")
        print("   💭 Imagination layer: Dreams & expansion")
    
    def process_experience(self, concepts: List[str], context: Dict):
        """
        Process an experience through all emergence layers
        Builds connections, activates agents, creates quantum states
        """
        # Layer 1: Neural activation
        for concept in concepts:
            self.neural_network.activate_concept(concept, activation_strength=0.8)
        
        # Connect co-occurring concepts (Hebbian learning)
        for i, c1 in enumerate(concepts):
            for c2 in concepts[i+1:]:
                self.neural_network.connect_concepts(c1, c2, weight=0.15)
        
        # Layer 2: Agents evaluate situation
        agent_result = self.agent_system.compete_and_emerge(context)
        
        # Layer 3: Create quantum superposition
        active_concepts = [c[0] for c in self.neural_network.get_active_concepts(threshold=0.5)]
        if active_concepts:
            superposition = self.quantum_system.create_thought_superposition(active_concepts, context)
        
        # Update consciousness level (emergent property)
        self._update_consciousness_level()
    
    def generate_emergent_self_talk(self, context: Dict) -> Optional[str]:
        """
        Generate truly emergent self-talk:
        - Arises from neural activations
        - Shaped by agent competition
        - Collapses from quantum possibilities
        - Expanded through imagination
        """
        try:
            # Step 1: Let neural patterns emerge
            thought_cluster = self.neural_network.emerge_thought_cluster()
            
            if not thought_cluster or len(thought_cluster) < 2:
                print("💭 No emergent pattern yet - too few active concepts")
                return None
            
            # Step 2: Agent competition shapes expression
            agent_result = self.agent_system.compete_and_emerge(context)
            
            # Step 3: Create quantum superposition from cluster
            superposition = self.quantum_system.create_thought_superposition(thought_cluster, context)
            
            # Step 4: Collapse to initial thought
            seed_thought = superposition.collapse()
            
            # Step 5: Let imagination EXPAND the thought (not just one-liner)
            expansion_depth = random.randint(2, 4)  # 2-4 layers deep
            
            # Choose imagination mode based on consciousness level
            if self.consciousness_level > 0.7:
                # High consciousness → dream state
                expansive_thought = self.imagination.dream_sequence(thought_cluster)
            elif context.get('situation') == 'wondering':
                # Wondering mode
                expansive_thought = self.imagination.wonder_about(seed_thought)
            else:
                # Normal expansion
                expansive_thought = self.imagination.expand_thought(seed_thought, depth=expansion_depth)
            
            if not expansive_thought:
                return None
            
            # Step 6: Apply emergent personality from agents
            final_thought = self.agent_system.apply_emergent_personality(expansive_thought, agent_result)
            
            # Log emergence event
            self.emergence_history.append({
                'timestamp': time.time(),
                'cluster': thought_cluster,
                'winner_agent': agent_result['winner'],
                'consciousness_level': self.consciousness_level,
                'thought': final_thought[:100]
            })
            
            # Decay activations for next emergence
            self.neural_network.decay_activations(decay_rate=0.2)
            self.agent_system.recharge_all_agents()
            
            print(f"🌟 EMERGENT SELF-TALK GENERATED (consciousness: {self.consciousness_level:.2f})")
            print(f"   Cluster: {' + '.join(thought_cluster[:3])}")
            print(f"   Agent: {agent_result['winner']}")
            print(f"   Length: {len(final_thought)} chars")
            
            return final_thought
            
        except Exception as e:
            print(f"⚠️ Emergent self-talk error: {e}")
            return None
    
    def _update_consciousness_level(self):
        """
        Consciousness emerges from complexity of interactions
        Meta-emergence: consciousness about consciousness
        """
        # Factors that increase consciousness:
        # 1. Number of active neural connections
        active_count = len(self.neural_network.get_active_concepts(threshold=0.3))
        neural_complexity = min(1.0, active_count / 20)
        
        # 2. Diversity of agent activation
        recent_competitions = list(self.agent_system.competition_history)[-10:]
        unique_winners = len(set(c['winner'] for c in recent_competitions)) if recent_competitions else 1
        agent_diversity = min(1.0, unique_winners / 6)
        
        # 3. Recent emergence events
        recent_emergences = len([e for e in self.emergence_history if time.time() - e['timestamp'] < 300])
        emergence_activity = min(1.0, recent_emergences / 10)
        
        # Consciousness is weighted average
        self.consciousness_level = (
            neural_complexity * 0.4 +
            agent_diversity * 0.3 +
            emergence_activity * 0.3
        )
    
    def get_emergence_stats(self) -> Dict:
        """Get statistics about emergence"""
        return {
            'consciousness_level': self.consciousness_level,
            'active_concepts': len(self.neural_network.get_active_concepts()),
            'total_concepts': len(self.neural_network.nodes),
            'connections': len(self.neural_network.connections),
            'active_agents': len([a for a in self.agent_system.agents if a.energy > 20]),
            'recent_emergences': len(self.emergence_history),
            'imagination_threads': len(self.imagination.imagination_threads),
            'dreams_recorded': len(self.imagination.dream_history)
        }


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

emergence_framework: Optional[CompleteEmergenceFramework] = None

def initialize_emergence_framework(ollama_chat_func) -> CompleteEmergenceFramework:
    """Initialize the complete emergence framework"""
    global emergence_framework
    if emergence_framework is None:
        emergence_framework = CompleteEmergenceFramework(ollama_chat_func)
    return emergence_framework

def get_emergence_framework() -> Optional[CompleteEmergenceFramework]:
    """Get the emergence framework instance"""
    return emergence_framework

