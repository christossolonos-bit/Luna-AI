"""
🧬 Luna DNA Memory System
========================

Inspired by biological DNA, this system stores memories as genetic strands that:
- Form double-helix pairs (user input + Luna response)
- Replicate when accessed (strengthening)
- Mutate with new context (evolution)
- Combine to form new insights (recombination)
- Express based on triggers (gene activation)

Each memory strand has:
- Nucleotides: Core information units
- Codons: 3-nucleotide sequences that encode meaning
- Genes: Complete thought sequences
- Chromosomes: Related memory clusters
"""

import sqlite3
import json
import time
import hashlib
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import random


class DNAMemoryStrand:
    """A single memory encoded as a DNA-like strand"""
    
    def __init__(self, user_message: str, luna_response: str, 
                 platform: str, username: str, timestamp: float = None):
        self.timestamp = timestamp or time.time()
        self.user_message = user_message
        self.luna_response = luna_response
        self.platform = platform
        self.username = username
        
        # DNA properties
        self.strand_id = self._generate_strand_id()
        self.nucleotides = self._encode_nucleotides()
        self.strength = 1.0  # Replication count
        self.mutations = 0
        self.last_accessed = self.timestamp
        self.expression_count = 0
        
    def _generate_strand_id(self) -> str:
        """Generate unique ID like DNA fingerprint"""
        data = f"{self.username}:{self.user_message}:{self.timestamp}"
        return hashlib.md5(data.encode()).hexdigest()[:12]
    
    def _encode_nucleotides(self) -> Dict:
        """Encode memory into nucleotide-like structure
        
        Using 4 bases like DNA (A, T, G, C):
        A = Action/Request
        T = Topic/Subject  
        G = Emotion/Tone
        C = Context/Details
        """
        return {
            'A': self._extract_action(),
            'T': self._extract_topic(),
            'G': self._extract_emotion(),
            'C': self._extract_context()
        }
    
    def _extract_action(self) -> str:
        """Extract action/intent from message"""
        action_keywords = ['help', 'tell', 'show', 'explain', 'what', 'how', 'when', 'where', 'why']
        words = self.user_message.lower().split()
        for word in words:
            if word in action_keywords:
                return word
        return 'chat'
    
    def _extract_topic(self) -> str:
        """Extract main topic/subject"""
        # Simple noun extraction (can be enhanced with NLP)
        words = self.user_message.lower().split()
        # Remove common words
        stopwords = ['the', 'a', 'an', 'and', 'or', 'but', 'is', 'am', 'are', 'what', 'how']
        topics = [w for w in words if w not in stopwords and len(w) > 3]
        return topics[0] if topics else 'general'
    
    def _extract_emotion(self) -> str:
        """Extract emotional tone"""
        emotion_markers = {
            'happy': ['!', 'haha', 'lol', 'love', 'great', 'awesome'],
            'sad': [':(', 'sad', 'sorry', 'miss'],
            'angry': ['!!', 'hate', 'angry', 'mad'],
            'curious': ['?', 'wonder', 'curious'],
            'neutral': []
        }
        msg_lower = self.user_message.lower()
        for emotion, markers in emotion_markers.items():
            if any(marker in msg_lower for marker in markers):
                return emotion
        return 'neutral'
    
    def _extract_context(self) -> str:
        """Extract contextual details"""
        return f"{self.platform}:{len(self.user_message)}"
    
    def replicate(self):
        """Strengthen through access (like DNA replication)"""
        self.strength += 0.1
        self.last_accessed = time.time()
        self.expression_count += 1
    
    def mutate(self, new_context: str):
        """Evolve with new context"""
        self.mutations += 1
        self.nucleotides['C'] += f"|{new_context}"
    
    def to_dict(self) -> Dict:
        """Export strand as dictionary"""
        return {
            'strand_id': self.strand_id,
            'timestamp': self.timestamp,
            'user_message': self.user_message,
            'luna_response': self.luna_response,
            'platform': self.platform,
            'username': self.username,
            'nucleotides': json.dumps(self.nucleotides),
            'strength': self.strength,
            'mutations': self.mutations,
            'last_accessed': self.last_accessed,
            'expression_count': self.expression_count
        }


class LunaDNAMemorySystem:
    """DNA-inspired memory system for Luna"""
    
    def __init__(self, db_path: str = "luna_dna_memory.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._initialize_genome()
    
    def _initialize_genome(self):
        """Initialize the memory genome (database structure)"""
        cursor = self.conn.cursor()
        
        # Memory strands table (like chromosomes)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory_strands (
                strand_id TEXT PRIMARY KEY,
                timestamp REAL,
                user_message TEXT,
                luna_response TEXT,
                platform TEXT,
                username TEXT,
                nucleotides TEXT,
                strength REAL,
                mutations INTEGER,
                last_accessed REAL,
                expression_count INTEGER
            )
        ''')
        
        # Gene combinations (paired memories that activate together)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gene_combinations (
                combo_id TEXT PRIMARY KEY,
                strand_ids TEXT,
                activation_count INTEGER,
                last_activated REAL,
                fitness REAL
            )
        ''')
        
        # User profiles (genetic markers)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS genetic_profiles (
                username TEXT PRIMARY KEY,
                platform TEXT,
                total_strands INTEGER,
                dominant_traits TEXT,
                last_interaction REAL
            )
        ''')
        
        self.conn.commit()
        print("[DNA] Luna DNA Memory System initialized")
    
    def store_memory_strand(self, strand: DNAMemoryStrand):
        """Store a new memory strand in the genome"""
        cursor = self.conn.cursor()
        data = strand.to_dict()
        
        cursor.execute('''
            INSERT OR REPLACE INTO memory_strands 
            (strand_id, timestamp, user_message, luna_response, platform, username,
             nucleotides, strength, mutations, last_accessed, expression_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['strand_id'], data['timestamp'], data['user_message'],
            data['luna_response'], data['platform'], data['username'],
            data['nucleotides'], data['strength'], data['mutations'],
            data['last_accessed'], data['expression_count']
        ))
        
        self.conn.commit()
        self._update_genetic_profile(strand.username, strand.platform)
    
    def _update_genetic_profile(self, username: str, platform: str):
        """Update user's genetic profile"""
        cursor = self.conn.cursor()
        
        # Count total strands
        cursor.execute('''
            SELECT COUNT(*) FROM memory_strands WHERE username = ?
        ''', (username,))
        total_strands = cursor.fetchone()[0]
        
        # Get dominant traits (most common nucleotides)
        cursor.execute('''
            SELECT nucleotides FROM memory_strands WHERE username = ?
            ORDER BY strength DESC LIMIT 10
        ''', (username,))
        
        traits = {}
        for row in cursor.fetchall():
            nucleotides = json.loads(row[0])
            for key, value in nucleotides.items():
                traits[value] = traits.get(value, 0) + 1
        
        dominant_traits = json.dumps(traits)
        
        cursor.execute('''
            INSERT OR REPLACE INTO genetic_profiles
            (username, platform, total_strands, dominant_traits, last_interaction)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, platform, total_strands, dominant_traits, time.time()))
        
        self.conn.commit()
    
    def express_genes(self, username: str, query: str, limit: int = 5) -> List[Dict]:
        """Express relevant genes (activate memories) based on query
        
        Like gene expression in biology, only relevant memories activate
        """
        cursor = self.conn.cursor()
        
        # Extract nucleotides from query
        temp_strand = DNAMemoryStrand(query, "", "query", username)
        query_nucleotides = temp_strand.nucleotides
        
        # Find matching strands (complementary base pairing)
        cursor.execute('''
            SELECT * FROM memory_strands 
            WHERE username = ?
            ORDER BY strength DESC, last_accessed DESC
            LIMIT 50
        ''', (username,))
        
        all_strands = cursor.fetchall()
        scored_strands = []
        
        for strand in all_strands:
            strand_nucleotides = json.loads(strand[6])  # nucleotides column
            
            # Calculate complementarity score
            score = 0.0
            for key in ['A', 'T', 'G', 'C']:
                if query_nucleotides[key] == strand_nucleotides[key]:
                    score += 1.0
                elif query_nucleotides[key] in strand_nucleotides[key]:
                    score += 0.5
            
            # Bonus for strong strands (frequently accessed)
            score *= (1.0 + strand[7] * 0.1)  # strength column
            
            scored_strands.append((score, strand))
        
        # Sort by score and get top matches
        scored_strands.sort(reverse=True, key=lambda x: x[0])
        top_strands = scored_strands[:limit]
        
        # Mark as expressed (replicate)
        results = []
        for score, strand in top_strands:
            strand_id = strand[0]
            cursor.execute('''
                UPDATE memory_strands 
                SET strength = strength + 0.1,
                    last_accessed = ?,
                    expression_count = expression_count + 1
                WHERE strand_id = ?
            ''', (time.time(), strand_id))
            
            results.append({
                'user_message': strand[2],
                'luna_response': strand[3],
                'platform': strand[4],
                'timestamp': strand[1],
                'strength': strand[7],
                'match_score': score
            })
        
        self.conn.commit()
        return results
    
    def recombine_genes(self, strand_ids: List[str]) -> Optional[str]:
        """Combine multiple memory strands to form new insights
        
        Like genetic recombination, mixing genes creates novelty
        """
        if len(strand_ids) < 2:
            return None
        
        cursor = self.conn.cursor()
        
        # Fetch strands
        strands_data = []
        for strand_id in strand_ids:
            cursor.execute('''
                SELECT user_message, luna_response, nucleotides 
                FROM memory_strands WHERE strand_id = ?
            ''', (strand_id,))
            result = cursor.fetchone()
            if result:
                strands_data.append(result)
        
        if len(strands_data) < 2:
            return None
        
        # Combine insights
        combined_context = "Combined memories:\n"
        for i, strand in enumerate(strands_data):
            combined_context += f"{i+1}. User: {strand[0]} | Luna: {strand[1]}\n"
        
        # Store gene combination
        combo_id = hashlib.md5(str(strand_ids).encode()).hexdigest()[:12]
        cursor.execute('''
            INSERT OR REPLACE INTO gene_combinations
            (combo_id, strand_ids, activation_count, last_activated, fitness)
            VALUES (?, ?, ?, ?, ?)
        ''', (combo_id, json.dumps(strand_ids), 1, time.time(), 1.0))
        
        self.conn.commit()
        return combined_context
    
    def get_user_profile(self, username: str) -> Optional[Dict]:
        """Get user's genetic profile"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM genetic_profiles WHERE username = ?
        ''', (username,))
        
        result = cursor.fetchone()
        if result:
            return {
                'username': result[0],
                'platform': result[1],
                'total_strands': result[2],
                'dominant_traits': json.loads(result[3]),
                'last_interaction': result[4]
            }
        return None
    
    def prune_weak_strands(self, min_strength: float = 0.5):
        """Remove weak memory strands (like synaptic pruning)"""
        cursor = self.conn.cursor()
        cursor.execute('''
            DELETE FROM memory_strands 
            WHERE strength < ? AND expression_count = 0
        ''', (min_strength,))
        
        deleted = cursor.rowcount
        self.conn.commit()
        return deleted
    
    def get_stats(self) -> Dict:
        """Get DNA memory system statistics"""
        cursor = self.conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM memory_strands')
        total_strands = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(strength) FROM memory_strands')
        avg_strength = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT COUNT(*) FROM gene_combinations')
        total_combinations = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM genetic_profiles')
        total_users = cursor.fetchone()[0]
        
        return {
            'total_strands': total_strands,
            'avg_strength': round(avg_strength, 2),
            'gene_combinations': total_combinations,
            'unique_users': total_users
        }
    
    def close(self):
        """Close the genome database"""
        self.conn.close()


# Global instance
_dna_memory_system = None

def initialize_dna_memory():
    """Initialize the DNA memory system"""
    global _dna_memory_system
    _dna_memory_system = LunaDNAMemorySystem()
    return _dna_memory_system

def get_dna_memory():
    """Get the DNA memory system instance"""
    return _dna_memory_system

def save_dna_memory(user_message: str, luna_response: str, 
                    platform: str, username: str):
    """Save a new memory strand"""
    if _dna_memory_system:
        strand = DNAMemoryStrand(user_message, luna_response, platform, username)
        _dna_memory_system.store_memory_strand(strand)

def recall_dna_memories(username: str, query: str, limit: int = 5) -> List[Dict]:
    """Recall relevant memories by expressing genes"""
    if _dna_memory_system:
        return _dna_memory_system.express_genes(username, query, limit)
    return []

