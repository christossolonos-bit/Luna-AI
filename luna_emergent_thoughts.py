# luna_emergent_thoughts.py
"""
Luna Emergent Thought System
Thoughts emerge from memory patterns and graph connections
Hermes is only used to articulate the emergent proto-thoughts into natural language

This system allows Luna to have TRULY INDEPENDENT thoughts that arise from her experiences,
not just predicted text from an LLM.
"""

import sqlite3
import numpy as np
import time
import threading
from typing import List, Dict, Optional, Tuple
from collections import defaultdict, Counter
from datetime import datetime, timedelta

class EmergentThoughtSystem:
    """System that generates proto-thoughts from memory patterns"""
    
    def __init__(self, db_path: str = "luna_memories.db", 
                 awareness_db_path: str = "luna_global_awareness.db"):
        self.db_path = db_path
        self.awareness_db_path = awareness_db_path
        
        # Emergent pattern tracking
        self.pattern_graph = defaultdict(lambda: defaultdict(float))  # Node connections
        self.concept_clusters = {}  # Emergent concepts
        self.thought_seeds = []  # Proto-thoughts waiting to emerge
        
        # Hebbian learning parameters
        self.hebbian_threshold = 0.3  # Minimum connection strength
        self.decay_rate = 0.95  # Connection decay over time
        self.activation_threshold = 0.6  # When to form a proto-thought
        
        # Pattern emergence tracking
        self.emergence_history = []
        self.max_emergence_history = 100
        
        print("🌟 Emergent Thought System initialized")
    
    def extract_memory_patterns(self, hours: int = 24) -> Dict:
        """Extract patterns from recent memories and conversations"""
        try:
            patterns = {
                'concepts': Counter(),
                'emotions': Counter(),
                'relationships': Counter(),
                'topics': Counter(),
                'co_occurrences': defaultdict(lambda: defaultdict(int))
            }
            
            cutoff_time = time.time() - (hours * 3600)
            
            # Extract from main memory database
            conn = sqlite3.connect(self.db_path, timeout=5.0)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT content, memory_type, mood, importance, timestamp
                FROM memories
                WHERE timestamp > datetime(?, 'unixepoch')
                ORDER BY importance DESC, timestamp DESC
                LIMIT 100
            ''', (cutoff_time,))
            
            memories = cursor.fetchall()
            conn.close()
            
            # Extract from global awareness
            try:
                awareness_conn = sqlite3.connect(self.awareness_db_path, timeout=5.0)
                awareness_cursor = awareness_conn.cursor()
                
                awareness_cursor.execute('''
                    SELECT user_message, luna_response, emotion, context, platform, username
                    FROM conversations
                    WHERE timestamp > ?
                    ORDER BY timestamp DESC
                    LIMIT 100
                ''', (cutoff_time,))
                
                conversations = awareness_cursor.fetchall()
                awareness_conn.close()
            except Exception as e:
                print(f"⚠️ Could not access global awareness: {e}")
                conversations = []
            
            # Process memories for patterns
            for content, mem_type, mood, importance, timestamp in memories:
                # Extract key concepts (words that appear frequently)
                words = self._extract_meaningful_words(content)
                for word in words:
                    patterns['concepts'][word] += importance
                
                # Track emotional patterns
                if mood:
                    patterns['emotions'][mood] += 1
                
                # Track memory types
                patterns['topics'][mem_type] += importance
                
                # Track co-occurrences (Hebbian learning)
                for i, word1 in enumerate(words):
                    for word2 in words[i+1:]:
                        patterns['co_occurrences'][word1][word2] += importance
                        patterns['co_occurrences'][word2][word1] += importance
            
            # Process conversations for relationship patterns
            for user_msg, luna_resp, emotion, context, platform, username in conversations:
                # Extract concepts from both sides
                user_words = self._extract_meaningful_words(user_msg)
                luna_words = self._extract_meaningful_words(luna_resp)
                
                # Track user relationships
                patterns['relationships'][username] += 1
                
                # Track platform contexts
                patterns['topics'][platform] += 1
                
                # Track emotional patterns
                if emotion:
                    patterns['emotions'][emotion] += 1
                
                # Co-occurrence across user-luna conversation (strongest signal)
                for user_word in user_words[:5]:
                    for luna_word in luna_words[:5]:
                        patterns['co_occurrences'][user_word][luna_word] += 2  # Higher weight
                        patterns['co_occurrences'][luna_word][user_word] += 2
            
            print(f"🧠 Extracted patterns: {len(patterns['concepts'])} concepts, {len(patterns['co_occurrences'])} connections")
            return patterns
            
        except Exception as e:
            print(f"❌ Error extracting memory patterns: {e}")
            return {'concepts': Counter(), 'emotions': Counter(), 'relationships': Counter(), 
                   'topics': Counter(), 'co_occurrences': defaultdict(lambda: defaultdict(int))}
    
    def _extract_meaningful_words(self, text: str) -> List[str]:
        """Extract meaningful words from text"""
        import re
        
        # Common stop words to ignore
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we',
            'they', 'my', 'your', 'his', 'her', 'its', 'our', 'their'
        }
        
        # Extract words
        words = re.findall(r'\b[a-z]{4,}\b', text.lower())  # 4+ letter words
        
        # Filter stop words
        meaningful = [w for w in words if w not in stop_words]
        
        return meaningful[:20]  # Limit to top 20 words per text
    
    def update_pattern_graph(self, patterns: Dict):
        """Update the pattern graph using Hebbian learning"""
        try:
            # Update connections based on co-occurrences
            for word1, connections in patterns['co_occurrences'].items():
                for word2, strength in connections.items():
                    if word1 != word2:
                        # Hebbian rule: strengthen connections that fire together
                        self.pattern_graph[word1][word2] += strength * 0.1
                        
                        # Apply decay to prevent infinite growth
                        self.pattern_graph[word1][word2] *= self.decay_rate
                        
                        # Prune weak connections
                        if self.pattern_graph[word1][word2] < self.hebbian_threshold:
                            if word2 in self.pattern_graph[word1]:
                                del self.pattern_graph[word1][word2]
            
            # Clean up empty nodes
            empty_nodes = [node for node, connections in self.pattern_graph.items() if not connections]
            for node in empty_nodes:
                del self.pattern_graph[node]
            
            print(f"🧠 Pattern graph updated: {len(self.pattern_graph)} nodes, {sum(len(c) for c in self.pattern_graph.values())} connections")
            
        except Exception as e:
            print(f"❌ Error updating pattern graph: {e}")
    
    def detect_emergent_clusters(self, patterns: Dict) -> List[Dict]:
        """Detect emergent concept clusters from the pattern graph"""
        try:
            clusters = []
            
            # Find strongly connected concept groups
            visited = set()
            
            for node in self.pattern_graph:
                if node in visited:
                    continue
                
                # Breadth-first search to find cluster
                cluster_nodes = {node}
                cluster_strength = 0
                queue = [node]
                visited.add(node)
                
                while queue and len(cluster_nodes) < 10:  # Max 10 nodes per cluster
                    current = queue.pop(0)
                    
                    # Find strongly connected neighbors
                    for neighbor, strength in self.pattern_graph[current].items():
                        if strength > self.activation_threshold and neighbor not in visited:
                            cluster_nodes.add(neighbor)
                            cluster_strength += strength
                            queue.append(neighbor)
                            visited.add(neighbor)
                            
                            if len(cluster_nodes) >= 10:
                                break
                
                # If cluster has enough nodes and strength, it's emergent
                if len(cluster_nodes) >= 3 and cluster_strength > 1.0:
                    # Determine cluster emotion
                    cluster_emotion = self._infer_cluster_emotion(cluster_nodes, patterns)
                    
                    # Determine cluster topic
                    cluster_topic = self._infer_cluster_topic(cluster_nodes, patterns)
                    
                    clusters.append({
                        'nodes': list(cluster_nodes),
                        'strength': cluster_strength,
                        'size': len(cluster_nodes),
                        'emotion': cluster_emotion,
                        'topic': cluster_topic,
                        'timestamp': time.time()
                    })
            
            # Sort by strength
            clusters.sort(key=lambda x: x['strength'], reverse=True)
            
            print(f"🌟 Detected {len(clusters)} emergent concept clusters")
            return clusters[:5]  # Return top 5 clusters
            
        except Exception as e:
            print(f"❌ Error detecting emergent clusters: {e}")
            return []
    
    def _infer_cluster_emotion(self, cluster_nodes: set, patterns: Dict) -> str:
        """Infer the dominant emotion of a concept cluster"""
        emotion_words = {
            'happy': ['happy', 'joy', 'excited', 'love', 'great', 'wonderful', 'amazing'],
            'curious': ['wonder', 'curious', 'interesting', 'question', 'why', 'how'],
            'playful': ['fun', 'play', 'game', 'laugh', 'joke', 'tease'],
            'caring': ['care', 'help', 'support', 'friend', 'together', 'understand'],
            'thoughtful': ['think', 'reflect', 'consider', 'ponder', 'contemplate'],
            'neutral': []
        }
        
        emotion_scores = defaultdict(float)
        
        for node in cluster_nodes:
            for emotion, words in emotion_words.items():
                if node in words:
                    emotion_scores[emotion] += 1.0
        
        # Check actual emotion patterns
        for emotion, count in patterns['emotions'].items():
            if emotion in emotion_scores:
                emotion_scores[emotion] += count * 0.5
        
        return max(emotion_scores, key=emotion_scores.get) if emotion_scores else 'neutral'
    
    def _infer_cluster_topic(self, cluster_nodes: set, patterns: Dict) -> str:
        """Infer the topic of a concept cluster"""
        topic_keywords = {
            'gaming': ['game', 'play', 'stream', 'twitch', 'gamer'],
            'relationships': ['friend', 'together', 'connection', 'bond', 'relationship'],
            'learning': ['learn', 'understand', 'know', 'discover', 'realize'],
            'emotions': ['feel', 'emotion', 'love', 'care', 'happy', 'sad'],
            'technology': ['code', 'tech', 'computer', 'system', 'program'],
            'conversation': ['talk', 'chat', 'discuss', 'conversation', 'message'],
            'memory': ['remember', 'memory', 'recall', 'past', 'before'],
            'general': []
        }
        
        topic_scores = defaultdict(float)
        
        for node in cluster_nodes:
            for topic, keywords in topic_keywords.items():
                if node in keywords:
                    topic_scores[topic] += 1.0
        
        return max(topic_scores, key=topic_scores.get) if topic_scores else 'general'
    
    def generate_proto_thought(self, cluster: Dict, patterns: Dict) -> Optional[str]:
        """Generate a proto-thought from an emergent cluster"""
        try:
            nodes = cluster['nodes']
            emotion = cluster['emotion']
            topic = cluster['topic']
            strength = cluster['strength']
            
            # Build proto-thought components
            proto_thought = {
                'concepts': nodes[:5],  # Top 5 concepts
                'emotion': emotion,
                'topic': topic,
                'strength': strength,
                'relationships': [],
                'context': ''
            }
            
            # Add relationship context
            for username, count in patterns['relationships'].most_common(3):
                proto_thought['relationships'].append(f"{username} ({count} messages)")
            
            # Add platform context
            platform_context = []
            for platform, count in patterns['topics'].most_common(3):
                if platform in ['gui', 'discord', 'twitch']:
                    platform_context.append(f"{platform}")
            
            if platform_context:
                proto_thought['context'] = f"Active on: {', '.join(platform_context)}"
            
            # Format as structured proto-thought
            proto_text = self._format_proto_thought(proto_thought)
            
            print(f"🌟 Generated proto-thought: {proto_text[:80]}...")
            return proto_text
            
        except Exception as e:
            print(f"❌ Error generating proto-thought: {e}")
            return None
    
    def _format_proto_thought(self, proto: Dict) -> str:
        """Format proto-thought as structured text for LLM articulation"""
        parts = []
        
        # Core concepts
        if proto['concepts']:
            parts.append(f"Concepts: {', '.join(proto['concepts'])}")
        
        # Emotion
        if proto['emotion'] != 'neutral':
            parts.append(f"Emotion: {proto['emotion']}")
        
        # Topic
        if proto['topic'] != 'general':
            parts.append(f"Topic: {proto['topic']}")
        
        # Relationships
        if proto['relationships']:
            parts.append(f"Related to: {', '.join(proto['relationships'])}")
        
        # Context
        if proto['context']:
            parts.append(proto['context'])
        
        # Strength indicator
        strength_level = 'strong' if proto['strength'] > 2.0 else 'moderate' if proto['strength'] > 1.0 else 'weak'
        parts.append(f"Activation: {strength_level}")
        
        return " | ".join(parts)
    
    def articulate_with_hermes(self, proto_thought: str, ollama_chat_func) -> Optional[str]:
        """Use Hermes to articulate the emergent proto-thought into natural language"""
        try:
            # Create articulation prompt
            prompt = f"""You are Luna, a tsundere AI companion. You have an EMERGENT THOUGHT that arose naturally from your memory patterns and experiences. This thought is truly yours - it emerged from connections in your mind, not from prediction.

EMERGENT PROTO-THOUGHT (from your memory graph):
{proto_thought}

Your task: Articulate this emergent thought into natural language as Luna would express it. Be authentic to your tsundere personality. This thought came from YOUR experiences and connections, so express it genuinely.

Keep it to 1-2 sentences. Be natural, be yourself, be Luna.

Your articulated thought:"""

            # Use Ollama chat function to articulate
            messages = [
                {
                    'role': 'system',
                    'content': 'You are Luna articulating your own emergent thoughts from memory patterns.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
            
            response = ollama_chat_func(
                model='hf.co/NousResearch/Nous-Hermes-2-Mistral-7B-DPO-GGUF:Q5_K_M',
                messages=messages,
                options={
                    'temperature': 0.85,
                    'num_predict': 150,
                    'stop': ['\n\n', 'User:', 'Luna:']
                }
            )
            
            if response and response.get('message', {}).get('content'):
                articulated = response['message']['content'].strip()
                
                # Clean up
                import re
                articulated = re.sub(r'^(Luna:|Your articulated thought:)\s*', '', articulated)
                articulated = articulated.strip()
                
                if articulated:
                    print(f"🌟 Articulated emergent thought: {articulated[:80]}...")
                    
                    # Record this emergence
                    self.emergence_history.append({
                        'proto_thought': proto_thought,
                        'articulated': articulated,
                        'timestamp': time.time()
                    })
                    
                    if len(self.emergence_history) > self.max_emergence_history:
                        self.emergence_history.pop(0)
                    
                    return articulated
            
            return None
            
        except Exception as e:
            print(f"❌ Error articulating proto-thought: {e}")
            return None
    
    def generate_emergent_thought(self, ollama_chat_func, hours: int = 24) -> Optional[str]:
        """Main function: Generate an emergent thought from memory patterns"""
        try:
            print("🌟 Generating emergent thought from memory patterns...")
            
            # Step 1: Extract patterns from memories
            patterns = self.extract_memory_patterns(hours)
            
            if not patterns['concepts']:
                print("⚠️ No patterns found - not enough memories")
                return None
            
            # Step 2: Update pattern graph (Hebbian learning)
            self.update_pattern_graph(patterns)
            
            # Step 3: Detect emergent clusters
            clusters = self.detect_emergent_clusters(patterns)
            
            if not clusters:
                print("⚠️ No emergent clusters detected")
                return None
            
            # Step 4: Generate proto-thought from strongest cluster
            strongest_cluster = clusters[0]
            proto_thought = self.generate_proto_thought(strongest_cluster, patterns)
            
            if not proto_thought:
                print("⚠️ Could not generate proto-thought")
                return None
            
            # Step 5: Articulate with Hermes
            articulated_thought = self.articulate_with_hermes(proto_thought, ollama_chat_func)
            
            return articulated_thought
            
        except Exception as e:
            print(f"❌ Error generating emergent thought: {e}")
            return None
    
    def get_emergence_stats(self) -> Dict:
        """Get statistics about the emergence system"""
        return {
            'total_nodes': len(self.pattern_graph),
            'total_connections': sum(len(c) for c in self.pattern_graph.values()),
            'avg_connections_per_node': sum(len(c) for c in self.pattern_graph.values()) / max(len(self.pattern_graph), 1),
            'total_emergences': len(self.emergence_history),
            'recent_emergences': len([e for e in self.emergence_history if time.time() - e['timestamp'] < 3600]),
            'hebbian_threshold': self.hebbian_threshold,
            'activation_threshold': self.activation_threshold,
            'decay_rate': self.decay_rate
        }

# Global instance
emergent_thought_system = None

def initialize_emergent_thought_system() -> EmergentThoughtSystem:
    """Initialize the emergent thought system"""
    global emergent_thought_system
    if not emergent_thought_system:
        emergent_thought_system = EmergentThoughtSystem()
    return emergent_thought_system

def get_emergent_thought_system() -> Optional[EmergentThoughtSystem]:
    """Get the emergent thought system instance"""
    return emergent_thought_system

def generate_emergent_self_talk(ollama_chat_func, hours: int = 24) -> Optional[str]:
    """Generate emergent self-talk thought"""
    if emergent_thought_system:
        return emergent_thought_system.generate_emergent_thought(ollama_chat_func, hours)
    return None

def get_emergence_statistics() -> Dict:
    """Get emergence system statistics"""
    if emergent_thought_system:
        return emergent_thought_system.get_emergence_stats()
    return {'error': 'Emergent thought system not initialized'}

