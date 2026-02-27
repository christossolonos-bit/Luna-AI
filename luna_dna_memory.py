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
import re
import traceback
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import random

# Fallback for config/seed: optional known platform_user_id -> aliases (for migration)
# Set via set_known_user_aliases() or from config
_KNOWN_USER_ALIASES: Dict[str, List[str]] = {}


def set_known_user_aliases(mapping: Dict[str, List[str]]):
    """Seed known user aliases (e.g. from config). Key = platform_user_id like 'discord:123'."""
    global _KNOWN_USER_ALIASES
    _KNOWN_USER_ALIASES = dict(mapping)


def seed_user_identity(platform_user_id: str, display_names: List[str], platform: str = "discord"):
    """Seed user_identity_links for migration (e.g. discord:123 -> Chris, Solonaras)."""
    if not _dna_memory_system or not platform_user_id:
        return
    for name in display_names:
        if name:
            _dna_memory_system.link_user_identity(platform_user_id, name, platform)


def link_user_identity(platform: str, username: str, user_id: Optional[str] = None):
    """Link display_name to platform user ID. Call when user sends a message."""
    if not platform or not user_id:
        return
    platform_user_id = f"{platform}:{user_id}"
    if _dna_memory_system:
        _dna_memory_system.link_user_identity(platform_user_id, username, platform)


def get_user_aliases(platform: str, username: str, user_id: Optional[str] = None) -> List[str]:
    """
    Get all display-name aliases for a user. Dynamic: uses platform_user_id to merge identities.
    Returns [username] + any linked names (e.g. Chris + Solonaras for same Discord user).
    """
    platform_user_id = f"{platform}:{user_id}" if (platform and user_id) else None
    if _dna_memory_system and platform_user_id:
        aliases = _dna_memory_system.get_linked_aliases(platform_user_id)
        if aliases:
            return list(dict.fromkeys([username] + [a for a in aliases if a != username]))
    # Fallback: known seed (e.g. from config)
    if platform_user_id and platform_user_id in _KNOWN_USER_ALIASES:
        return _KNOWN_USER_ALIASES[platform_user_id]
    return [username]


def get_all_known_display_names() -> List[str]:
    """Get all display names we have data for (for dynamic mention extraction)."""
    if not _dna_memory_system:
        return []
    cursor = _dna_memory_system.conn.cursor()
    names = set()
    cursor.execute("SELECT DISTINCT display_name FROM user_identity_links")
    for row in cursor.fetchall():
        if row[0]:
            names.add(row[0])
    cursor.execute("SELECT DISTINCT username FROM user_facts")
    for row in cursor.fetchall():
        if row[0]:
            names.add(row[0])
    return sorted(names, key=lambda x: x.lower())


def get_aliases_for_display_name(display_name: str) -> List[str]:
    """Get aliases for a mentioned user (e.g. 'Chris' in 'where is Chris from?'). Uses DB links."""
    if not display_name or not _dna_memory_system:
        return [display_name] if display_name else []
    cursor = _dna_memory_system.conn.cursor()
    cursor.execute('''
        SELECT platform_user_id FROM user_identity_links
        WHERE LOWER(display_name) = LOWER(?)
        LIMIT 1
    ''', (display_name.strip(),))
    row = cursor.fetchone()
    if row:
        aliases = _dna_memory_system.get_linked_aliases(row[0])
        if aliases:
            return list(dict.fromkeys([display_name] + [a for a in aliases if a != display_name]))
    return [display_name]


class DNAMemoryStrand:
    """A single memory encoded as a DNA-like strand with global context"""
    
    def __init__(self, user_message: str, luna_response: str, 
                 platform: str, username: str, timestamp: float = None,
                 global_context: Dict = None, cross_platform_links: List = None):
        self.timestamp = timestamp or time.time()
        self.user_message = user_message
        self.luna_response = luna_response
        self.platform = platform
        self.username = username
        self.global_context = global_context or {}
        self.cross_platform_links = cross_platform_links or []
        
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
        
        # Permanent user facts (name, preferences, etc.) - survives restarts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_facts (
                fact_id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                fact_type TEXT NOT NULL,
                fact_value TEXT NOT NULL,
                timestamp REAL
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_facts_username ON user_facts(username)')

        # Persistent user profiles (per-user, Discord + Twitch) - survives restarts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                username TEXT PRIMARY KEY,
                platforms TEXT,
                total_interactions INTEGER DEFAULT 0,
                interests TEXT,
                preferences TEXT,
                topics_discussed TEXT,
                emotional_patterns TEXT,
                relationship_level TEXT,
                profile_json TEXT,
                last_updated REAL
            )
        ''')
        
        # Dynamic identity linking: platform_user_id (e.g. discord:123) -> display_names used
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_identity_links (
                platform_user_id TEXT NOT NULL,
                display_name TEXT NOT NULL,
                platform TEXT NOT NULL,
                first_seen REAL,
                PRIMARY KEY (platform_user_id, display_name)
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_identity_platform ON user_identity_links(platform_user_id)')
        
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
    
    def _keyword_overlap_score(self, query: str, text: str) -> float:
        """Score by word overlap - helps semantic recall when nucleotide matching fails."""
        if not text:
            return 0.0
        q_words = set(w.lower() for w in query.split() if len(w) > 2)
        t_words = set(w.lower() for w in text.split() if len(w) > 2)
        if not q_words:
            return 0.0
        overlap = len(q_words & t_words) / len(q_words)
        return overlap

    def express_genes(self, username: str, query: str, limit: int = 5) -> List[Dict]:
        """Express relevant genes (activate memories) based on query
        
        Uses nucleotide matching + keyword overlap fallback for better recall.
        """
        cursor = self.conn.cursor()
        
        # Extract nucleotides from query
        temp_strand = DNAMemoryStrand(query, "", "query", username)
        query_nucleotides = temp_strand.nucleotides
        
        # Find matching strands - also try common username aliases (e.g. Chris/solonaras)
        cursor.execute('''
            SELECT * FROM memory_strands 
            WHERE username = ?
            ORDER BY strength DESC, last_accessed DESC, timestamp DESC
            LIMIT 100
        ''', (username,))
        
        all_strands = cursor.fetchall()
        scored_strands = []
        
        for strand in all_strands:
            strand_nucleotides = json.loads(strand[6])  # nucleotides column
            
            # Nucleotide complementarity score
            nucl_score = 0.0
            for key in ['A', 'T', 'G', 'C']:
                if query_nucleotides[key] == strand_nucleotides[key]:
                    nucl_score += 1.0
                elif query_nucleotides[key] in strand_nucleotides[key]:
                    nucl_score += 0.5
            
            # Keyword overlap fallback (semantic relevance)
            kw_score = self._keyword_overlap_score(query, strand[2])  # user_message
            kw_score += 0.5 * self._keyword_overlap_score(query, strand[3])  # luna_response
            
            # Combine: prefer nucleotide match, but keyword overlap helps when nucl is weak
            score = nucl_score * 2.0 + kw_score  # nucl weighted higher when it matches
            
            # Bonus for strong strands (frequently accessed)
            score *= (1.0 + strand[7] * 0.1)  # strength column
            
            scored_strands.append((score, strand))
        
        # Sort by score and get top matches
        scored_strands.sort(reverse=True, key=lambda x: x[0])
        top_strands = scored_strands[:limit]
        
        # Fallback: if all scores are 0, return most recent memories (any relevance better than none)
        if top_strands and top_strands[0][0] == 0:
            cursor.execute('''
                SELECT * FROM memory_strands 
                WHERE username = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (username, limit))
            top_strands = [(0.1, row) for row in cursor.fetchall()]
        
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

    def save_user_fact(self, username: str, fact_type: str, fact_value: str, multi_value: bool = False):
        """Store a permanent fact. multi_value=True allows multiple (e.g. interests)."""
        fv = (fact_value or "").strip()
        if len(fv) < 2:
            return
        uname = str(username or "")
        ftype = str(fact_type or "")
        key = f"{uname}:{ftype}:{fv}" if multi_value else f"{uname}:{ftype}"
        fact_id = hashlib.md5(key.encode()).hexdigest()[:16]
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO user_facts (fact_id, username, fact_type, fact_value, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (fact_id, uname, ftype, fv[:500], time.time()))
        self.conn.commit()

    def get_user_facts(self, username: str, usernames: List[str] = None) -> List[Dict]:
        """Get all stored facts for user(s). usernames: aliases to merge (e.g. Chris, solonaras)."""
        names = usernames or [username]
        cursor = self.conn.cursor()
        seen = set()
        facts = []
        for name in names:
            cursor.execute('''
                SELECT fact_type, fact_value FROM user_facts WHERE username = ?
            ''', (name,))
            for row in cursor.fetchall():
                key = (row[0], row[1].lower())
                if key not in seen:
                    seen.add(key)
                    facts.append({"fact_type": row[0], "fact_value": row[1]})
        return facts

    def save_user_profile(self, username: str, profile_data: Dict):
        """Save/merge user profile (persistent, per-user)."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT profile_json, total_interactions FROM user_profiles WHERE username = ?', (username,))
        row = cursor.fetchone()
        try:
            existing = json.loads(row[0]) if row and row[0] and str(row[0]).strip() else {}
        except (json.JSONDecodeError, TypeError):
            existing = {}
        existing_interactions = (row[1] if row and row[1] is not None else 0) or 0
        # Convert sets to lists for merge
        def to_list(x):
            return list(x) if isinstance(x, (set, frozenset)) else (x if isinstance(x, list) else [])
        # Merge
        for k, v in profile_data.items():
            if k == "interaction_history":
                continue  # Don't persist full history
            v = to_list(v) if k in ("interests", "topics_discussed", "platforms") else v
            if k in ("interests", "topics_discussed"):
                existing[k] = list(set(existing.get(k, [])) | set(v))[:50]
            elif k in ("preferences", "emotional_patterns", "communication_style"):
                d = existing.get(k, {})
                if isinstance(v, dict):
                    d.update(v)
                existing[k] = d
            elif k == "platforms":
                existing[k] = list(set(existing.get(k, [])) | set(v))
            elif k == "total_interactions":
                v_int = v if isinstance(v, (int, float)) and v is not None else 0
                existing[k] = max(existing.get(k, 0) or 0, v_int)
            elif k not in ("last_seen",):
                existing[k] = v
        total = max(existing.get("total_interactions", 0) or 0, existing_interactions)
        profile_json = json.dumps(existing)
        platforms = json.dumps(existing.get("platforms") or [])
        interests = json.dumps(existing.get("interests") or [])
        preferences = json.dumps(existing.get("preferences") or {})
        topics = json.dumps(existing.get("topics_discussed") or [])
        emotional = json.dumps(existing.get("emotional_patterns") or {})
        rel_level = existing.get("relationship_level") or "new"
        if not isinstance(rel_level, str):
            rel_level = str(rel_level) if rel_level is not None else "new"
        params = (str(username or ""), platforms, int(total), interests, preferences, topics,
                  emotional, rel_level, profile_json, time.time())
        cursor.execute('''
            INSERT OR REPLACE INTO user_profiles
            (username, platforms, total_interactions, interests, preferences, topics_discussed,
             emotional_patterns, relationship_level, profile_json, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', params)
        self.conn.commit()

    def link_user_identity(self, platform_user_id: str, display_name: str, platform: str):
        """Link a display_name to a platform user ID (e.g. discord:123). Builds dynamic aliases."""
        if not platform_user_id or not display_name:
            return
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO user_identity_links (platform_user_id, display_name, platform, first_seen)
            VALUES (?, ?, ?, ?)
        ''', (platform_user_id, display_name.strip(), platform, time.time()))
        self.conn.commit()

    def get_linked_aliases(self, platform_user_id: str) -> List[str]:
        """Get all display_names linked to this platform user ID."""
        if not platform_user_id:
            return []
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT display_name FROM user_identity_links WHERE platform_user_id = ?
        ''', (platform_user_id,))
        return [row[0] for row in cursor.fetchall()]

    def get_recent_memories_for_user(self, username: str, usernames: List[str] = None, limit: int = 25) -> List[Dict]:
        """Get recent conversation memories for user(s) - for profile context."""
        names = list(dict.fromkeys(usernames or [username]))
        cursor = self.conn.cursor()
        placeholders = ",".join("?" * len(names))
        cursor.execute(f'''
            SELECT user_message, luna_response, timestamp FROM memory_strands
            WHERE username IN ({placeholders})
            ORDER BY timestamp DESC LIMIT ?
        ''', (*names, limit))
        seen = set()
        results = []
        for row in cursor.fetchall():
            key = (row[0][:80], row[1][:80])
            if key not in seen:
                seen.add(key)
                results.append({"user_message": row[0], "luna_response": row[1], "timestamp": row[2]})
        return results[:limit]

    def get_user_profile_analysis(self, username: str, usernames: List[str] = None) -> str:
        """Aggregate ALL permanent memory for user into a single profile analysis for prompt injection.
        Combines: user_facts, user_profiles, recent memories. Luna can recall any of this when asked."""
        names = usernames or [username]
        parts = []
        # 1. User facts (name, location, interests, occupation, etc.)
        facts = self.get_user_facts(username, usernames)
        if facts:
            by_type = {}
            for f in facts:
                t = f["fact_type"]
                v = f["fact_value"]
                if t not in by_type:
                    by_type[t] = []
                if v not in by_type[t]:
                    by_type[t].append(v)
            fact_lines = []
            for t, vals in sorted(by_type.items()):
                label = t.replace("_", " ").title()
                fact_lines.append(f"  {label}: {', '.join(vals[:5])}")
            if fact_lines:
                parts.append("FACTS YOU KNOW:\n" + "\n".join(fact_lines))
        # 2. User profile (interests, preferences, topics)
        profile = self.get_user_profile(username, usernames)
        if profile:
            p_parts = []
            if profile.get("interests"):
                p_parts.append(f"  Interests: {', '.join(profile['interests'][:15])}")
            if profile.get("topics_discussed"):
                p_parts.append(f"  Topics discussed: {', '.join(profile['topics_discussed'][-15:])}")
            if profile.get("preferences"):
                prefs = list(profile["preferences"].items())[:10]
                p_parts.append(f"  Preferences: {', '.join(f'{k}={v}' for k, v in prefs)}")
            if profile.get("relationship_level") and profile["relationship_level"] != "new":
                p_parts.append(f"  Relationship: {profile['relationship_level']}")
            if profile.get("total_interactions", 0) > 0:
                p_parts.append(f"  Total interactions: {profile['total_interactions']}")
            if p_parts:
                parts.append("PROFILE:\n" + "\n".join(p_parts))
        # 3. Recent conversation highlights (what they've talked about)
        memories = self.get_recent_memories_for_user(username, usernames, limit=15)
        if memories:
            conv_lines = []
            for m in memories[:10]:
                um = m["user_message"][:100] + ("..." if len(m["user_message"]) > 100 else "")
                lr = m["luna_response"][:80] + ("..." if len(m["luna_response"]) > 80 else "")
                conv_lines.append(f"  - They said: \"{um}\" → You replied: \"{lr}\"")
            if conv_lines:
                parts.append("PAST CONVERSATIONS (recall when asked about these topics):\n" + "\n".join(conv_lines))
        if not parts:
            return ""
        return "\n\n".join(parts)

    def get_profile_gaps(self, username: str, usernames: List[str] = None) -> List[str]:
        """Return list of things we don't know about the user (for Luna to ask)."""
        facts = self.get_user_facts(username, usernames)
        profile = self.get_user_profile(username, usernames)
        fact_types = {f["fact_type"] for f in facts}
        gaps = []
        if "name" not in fact_types:
            gaps.append("name")
        if "location" not in fact_types:
            gaps.append("where they live/are from")
        if "interest" not in fact_types and not (profile and profile.get("interests")):
            gaps.append("interests/hobbies")
        if "occupation" not in fact_types:
            gaps.append("what they do (job/school)")
        if not (profile and profile.get("preferences")):
            gaps.append("preferences")
        return gaps

    def get_user_profile(self, username: str, usernames: List[str] = None) -> Optional[Dict]:
        """Get persistent profile for user(s). Merges from aliases."""
        names = usernames or [username]
        cursor = self.conn.cursor()
        merged = {}
        for name in names:
            cursor.execute('''
                SELECT profile_json, platforms, total_interactions, interests, preferences,
                       topics_discussed, emotional_patterns, relationship_level
                FROM user_profiles WHERE username = ?
            ''', (name,))
            row = cursor.fetchone()
            if row and row[0]:
                try:
                    p = json.loads(row[0])
                except (json.JSONDecodeError, TypeError):
                    p = {}
                try:
                    p["platforms"] = json.loads(row[1]) if row[1] and str(row[1]).strip() else []
                except (json.JSONDecodeError, TypeError):
                    p["platforms"] = []
                p["total_interactions"] = row[2] or 0
                for key, idx, default in [("interests", 3, []), ("preferences", 4, {}), ("topics_discussed", 5, []), ("emotional_patterns", 6, {})]:
                    try:
                        p[key] = json.loads(row[idx]) if row[idx] and str(row[idx]).strip() else default
                    except (json.JSONDecodeError, TypeError):
                        p[key] = default
                p["relationship_level"] = str(row[7]) if row[7] else "new"
                for k, v in p.items():
                    if k not in merged or (isinstance(v, list) and len(v) > len(merged.get(k, []))):
                        merged[k] = v
                    elif isinstance(v, dict) and v:
                        merged.setdefault(k, {}).update(v)
        return merged if merged else None

    def compile_profiles_from_history(self) -> Dict:
        """
        Scan all memory_strands (chat history) and extract/update profiles for every user.
        Also extracts name from Luna's response when user asked about their name.
        Returns {processed: int, users_updated: int, facts_added: int}.
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT username, platform, user_message, luna_response FROM memory_strands
            ORDER BY timestamp ASC
        ''')
        rows = cursor.fetchall()
        users_updated = set()
        facts_added = 0
        for row in rows:
            try:
                username = (row[0] or "").strip() if len(row) > 0 and row[0] else None
                platform = row[1] if len(row) > 1 else None
                user_message = (row[2] or "").strip() if len(row) > 2 and row[2] else None
                luna_response = (row[3] or "").strip() if len(row) > 3 else ""
                if not username or not user_message:
                    continue
                extracted = _extract_facts_from_message(user_message)
                # When user asked about their name and Luna confirmed it, extract from Luna's response
                luna_name = _extract_name_from_luna_response(user_message, luna_response or "")
                if luna_name:
                    extracted.append(("name", luna_name))
                for fact_type, fact_value in extracted:
                    multi = fact_type in ("interest",)
                    self.save_user_fact(username, fact_type, fact_value, multi_value=multi)
                    facts_added += 1
                interests = [v for t, v in extracted if t == "interest"]
                prefs = {f"preference_{i}": v for i, (t, v) in enumerate(extracted) if t == "preference"}
                if interests or prefs:
                    prof = self.get_user_profile(username) or {}
                    if interests:
                        prof["interests"] = list(set(prof.get("interests") or []) | set(interests))[:30]
                        self.save_user_profile(username, {"interests": prof["interests"]})
                    if prefs:
                        prof["preferences"] = {**(prof.get("preferences") or {}), **prefs}
                        self.save_user_profile(username, {"preferences": prof["preferences"]})
                # Topics: meaningful nouns/topics only, skip filler words
                FILLER = {'that', 'this', 'what', 'when', 'where', 'with', 'from', 'have', 'been', 'were', 'they',
                          'your', 'more', 'some', 'sure', 'know', 'make', 'take', 'like', 'just', 'only', 'very',
                          'really', 'about', 'there', 'here', 'then', 'than', 'into', 'over', 'also', 'even',
                          'back', 'down', 'same', 'such', 'each', 'much', 'many', 'most', 'other', 'these',
                          'those', 'which', 'while', 'after', 'before', 'being', 'could', 'would', 'should',
                          'might', 'must', 'will', 'shall', 'does', 'done', 'going', 'gonna', 'wanna',
                          'finds', 'jokes', 'answer', 'read', 'tell', 'luna', 'live', 'named', 'again', 'fresh'}
                words = [w for w in user_message.lower().split() if len(w) > 3 and w not in FILLER][:15]
                if words:
                    prof = self.get_user_profile(username) or {}
                    topics = list(set(prof.get("topics_discussed") or []) | set(words))[:40]
                    self.save_user_profile(username, {"topics_discussed": topics})
                users_updated.add(username)
            except (sqlite3.ProgrammingError, sqlite3.OperationalError, json.JSONDecodeError) as e:
                print(f"[DNA] compile_profiles skip row: {e} | username={row[0] if row else '?'}")
            except Exception as e:
                print(f"[DNA] compile_profiles error: {e}\n{traceback.format_exc()}")
                raise
        return {"processed": len(rows), "users_updated": len(users_updated), "facts_added": facts_added}

    def get_all_known_profiles(self) -> List[Dict]:
        """Return list of all users Luna has profile/fact data for."""
        cursor = self.conn.cursor()
        usernames = set()
        cursor.execute("SELECT DISTINCT username FROM user_facts")
        for row in cursor.fetchall():
            if row[0]:
                usernames.add(row[0])
        cursor.execute("SELECT DISTINCT username FROM user_profiles")
        for row in cursor.fetchall():
            if row[0]:
                usernames.add(row[0])
        cursor.execute("SELECT DISTINCT username FROM memory_strands")
        for row in cursor.fetchall():
            if row[0]:
                usernames.add(row[0])
        result = []
        for uname in sorted(usernames, key=lambda x: x.lower()):
            facts = self.get_user_facts(uname)
            profile = self.get_user_profile(uname)
            fact_count = len(facts)
            interactions = profile.get("total_interactions", 0) if profile else 0
            if not interactions:
                cursor.execute("SELECT COUNT(*) FROM memory_strands WHERE username = ?", (uname,))
                interactions = cursor.fetchone()[0] or 0
            summary_parts = []
            if facts:
                by_type = {}
                for f in facts:
                    t, v = f["fact_type"], f["fact_value"]
                    by_type.setdefault(t, []).append(v)
                for t in ["name", "location", "interest"]:
                    if t in by_type:
                        summary_parts.append(f"{t}: {', '.join(by_type[t][:3])}")
            result.append({
                "username": uname,
                "fact_count": fact_count,
                "interactions": interactions,
                "summary": "; ".join(summary_parts) if summary_parts else "—",
            })
        return result

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

    def clean_bad_facts(self) -> Dict:
        """
        Remove junk facts: bad favorite_X types, fragment-like values, filler interests.
        Returns {deleted: int, by_type: {fact_type: count}}.
        """
        FAVORITE_WHITELIST = {"game", "food", "color", "movie", "show", "music", "sport", "book", "animal", "drink", "hobby", "thing"}
        FILLER_INTERESTS = {"sure", "more", "what", "that", "this", "when", "does", "make", "luna", "read", "tell", "know",
                           "again", "fresh", "there", "live", "named", "really", "gonna", "answer", "finds", "jokes"}
        FRAGMENT_PATTERN = re.compile(r'\b(your|you\'?re|that\'?s|raging|empty|snevk|dominate|wearing)\b', re.I)

        cursor = self.conn.cursor()
        cursor.execute('SELECT fact_id, fact_type, fact_value FROM user_facts')
        rows = cursor.fetchall()
        to_delete = []
        by_type = {}

        for fact_id, fact_type, fact_value in rows:
            fact_value = (fact_value or "").strip().lower()
            delete_reason = None

            if fact_type.startswith("favorite_"):
                cat = fact_type.replace("favorite_", "").lower()
                if cat not in FAVORITE_WHITELIST:
                    delete_reason = "bad_favorite_type"
            elif fact_type == "interest" and fact_value in FILLER_INTERESTS:
                delete_reason = "filler_interest"
            elif FRAGMENT_PATTERN.search(fact_value):
                delete_reason = "fragment_value"

            if delete_reason:
                to_delete.append(fact_id)
                by_type[fact_type] = by_type.get(fact_type, 0) + 1

        for fact_id in to_delete:
            cursor.execute('DELETE FROM user_facts WHERE fact_id = ?', (fact_id,))
        self.conn.commit()
        return {"deleted": len(to_delete), "by_type": by_type}

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

def _is_name_question(message: str) -> bool:
    """Check if user is asking about their name."""
    m = message.strip().lower()
    return any(
        p in m for p in
        ("what is my name", "what's my name", "whats my name", "my name?", "tell me my name", "remember my name")
    )


def _extract_name_from_luna_response(user_message: str, luna_response: str) -> Optional[str]:
    """
    When user asked about their name and Luna confirmed it, extract the name from Luna's response.
    E.g. "Your name is Chris!" or "You're Chris" or "You're called Chris"
    """
    if not _is_name_question(user_message) or not luna_response or len(luna_response) < 2:
        return None
    resp = luna_response.strip()
    # "Your name is X" / "Your name's X" / "You're X" / "You're called X" / "It's X"
    for pat in [
        r"(?:your name is|your name\'?s|you\'?re called|you are)\s+([A-Z][a-zA-Z0-9_\s\-]{1,25})",
        r"(?:it\'?s|that\'?s)\s+([A-Z][a-zA-Z0-9_\s\-]{1,25})\s*(?:!|\.|$)",
        r"^([A-Z][a-z]+)\s*[!.]?\s*$",  # "Chris!" as short reply
    ]:
        m = re.search(pat, resp, re.I)
        if m:
            name = m.group(1).strip()
            if len(name) >= 2 and name.lower() not in ("i", "you", "it", "the", "a"):
                return name
    return None


def _extract_facts_from_message(message: str) -> List[Tuple[str, str]]:
    """Extract permanent facts from user message. Returns [(fact_type, fact_value), ...]"""
    msg = message.strip()
    facts = []
    seen = set()
    def add(ftype: str, val: str):
        v = val.strip()[:50]
        if len(v) < 2 or v.lower() in ('a', 'the', 'an', 'it', 'i') or (ftype, v.lower()) in seen:
            return
        # Reject values that look like conversation fragments
        v_lower = v.lower()
        if re.search(r'\b(your|you\'?re|that\'?s|when|what|this|they|them|their)\b', v_lower):
            return
        if re.search(r'^(raging|empty|just|fine|snevk)', v_lower):  # common junk prefixes
            return
        seen.add((ftype, v_lower))
        facts.append((ftype, v))
    # Name: "my name is X", "I'm X", "I am X", "call me X", "I'm called X", "I go by X", etc.
    # Skip "I'm from X" / "I'm in X" - those are location phrases, not names
    for m in re.finditer(r'(?:my name is|i\'?m called?|call me|i am|i\'?m)\s+([a-zA-Z][a-zA-Z0-9_\s\-]{1,20})', msg, re.I):
        val = m.group(1).strip()
        if val.lower().startswith(("from ", "in ")):
            continue  # "I'm from Cyprus" -> location, not name
        add("name", val)
    m = re.search(r'(?:my\s+)?name\s+is\s+([a-zA-Z][a-zA-Z0-9_\s\-]{1,20})', msg, re.I)
    if m:
        add("name", m.group(1))
    for m in re.finditer(r'(?:i go by|people call me|you can call me|just call me)\s+([a-zA-Z][a-zA-Z0-9_\s\-]{1,20})', msg, re.I):
        add("name", m.group(1))
    # Location: "I live in X", "I'm from X"
    for m in re.finditer(r'(?:i live in|i\'?m from|i\'?m in)\s+([a-zA-Z][a-zA-Z0-9_\s\-,]{1,40})', msg, re.I):
        add("location", m.group(1))
    # Favorite: "favorite X is Y" - only whitelisted categories to avoid junk (body, shaft, etc.)
    FAVORITE_WHITELIST = {"game", "food", "color", "movie", "show", "music", "sport", "book", "animal", "drink", "hobby", "thing"}
    m = re.search(r'(?:my|favorite)\s+(\w+)\s+is\s+([a-zA-Z][a-zA-Z0-9_\s\-]{1,25})', msg, re.I)
    if m:
        cat = m.group(1).lower()
        val = m.group(2).strip()
        if cat in FAVORITE_WHITELIST and len(val) <= 25 and not re.search(r'\b(your|the|that|when|what|this|they)\b', val, re.I):
            add(f"favorite_{m.group(1)}", val)
    # Interests: "I like X", "I love X", "I'm into X", "I enjoy X"
    for m in re.finditer(r'(?:i like|i love|i\'?m into|i enjoy|i\'?m interested in)\s+([a-zA-Z][a-zA-Z0-9_\s\-]{1,30})', msg, re.I):
        add("interest", m.group(1))
    # Occupation: "I'm a X", "I work as X"
    for m in re.finditer(r'(?:i\'?m a|i work as|i am a)\s+([a-zA-Z][a-zA-Z0-9_\s\-]{1,30})', msg, re.I):
        add("occupation", m.group(1))
    # Age: "I'm X years old"
    m = re.search(r'i\'?m\s+(\d{1,3})\s*(?:years?\s*old)?', msg, re.I)
    if m and 1 <= int(m.group(1)) <= 120:
        add("age", m.group(1))
    # Preference: "I prefer X", "I'd rather X"
    m = re.search(r'i (?:prefer|would rather|like to)\s+([a-zA-Z][a-zA-Z0-9_\s\-]{1,40})', msg, re.I)
    if m:
        add("preference", m.group(1))
    # Short answer to "What's your name?" - e.g. "John" or "John Smith" (2-25 chars, name-like)
    if re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?$', msg) and 2 <= len(msg) <= 25:
        skip = {'hey', 'hi', 'yes', 'no', 'ok', 'okay', 'thanks', 'hello', 'bye', 'cool', 'nice'}
        if msg.lower() not in skip:
            add("name", msg)
    # Short answer to "What do you like?" - e.g. "anime", "gaming" (single word 4-25 chars)
    if re.match(r'^[a-zA-Z][a-zA-Z0-9_\-]{3,24}$', msg) and " " not in msg:
        skip = {'hey', 'hi', 'yes', 'no', 'ok', 'okay', 'thanks', 'hello', 'bye', 'cool', 'nice', 'stuff', 'things',
                'sure', 'more', 'what', 'that', 'this', 'when', 'does', 'make', 'luna', 'read', 'tell', 'know',
                'again', 'fresh', 'there', 'live', 'named', 'really', 'gonna', 'answer', 'finds', 'jokes'}
        if msg.lower() not in skip:
            add("interest", msg)
    return facts


def save_facts_from_message(
    user_message: str,
    platform: str,
    username: str,
    user_id: Optional[str] = None,
) -> int:
    """
    Extract and save facts from a message WITHOUT creating a memory strand.
    Use for high-volume chat (Twitch) where we want to learn names/interests
    without storing every message. Returns number of facts saved.
    """
    if not _dna_memory_system or not user_message or not username:
        return 0
    extracted = _extract_facts_from_message(user_message)
    if not extracted:
        return 0
    link_user_identity(platform, username, user_id)
    for fact_type, fact_value in extracted:
        multi = fact_type in ("interest",)
        _dna_memory_system.save_user_fact(username, fact_type, fact_value, multi_value=multi)
    return len(extracted)


def save_dna_memory(user_message: str, luna_response: str, 
                    platform: str, username: str, user_id: Optional[str] = None):
    """Save a new memory strand and extract/store any permanent facts."""
    if _dna_memory_system:
        strand = DNAMemoryStrand(user_message, luna_response, platform, username)
        _dna_memory_system.store_memory_strand(strand)
        # Extract and save permanent facts from user message
        extracted = _extract_facts_from_message(user_message)
        # When user asked about their name and Luna confirmed it, extract from Luna's response
        luna_name = _extract_name_from_luna_response(user_message, luna_response)
        if luna_name:
            extracted.append(("name", luna_name))
        for fact_type, fact_value in extracted:
            multi = fact_type in ("interest",)
            _dna_memory_system.save_user_fact(username, fact_type, fact_value, multi_value=multi)
        # Update profile with extracted interests and preferences (merge from aliases)
        profile_usernames = get_user_aliases(platform, username, user_id)
        prof = _dna_memory_system.get_user_profile(username, usernames=profile_usernames) or {}
        interests = [v for t, v in extracted if t == "interest"]
        prefs = {f"preference_{i}": v for i, (t, v) in enumerate(extracted) if t == "preference"}
        if interests or prefs:
            if interests:
                prof["interests"] = list(set(prof.get("interests", [])) | set(interests))[:30]
                _dna_memory_system.save_user_profile(username, {"interests": prof["interests"]})
            if prefs:
                prof["preferences"] = {**prof.get("preferences", {}), **prefs}
                _dna_memory_system.save_user_profile(username, {"preferences": prof["preferences"]})


def get_user_facts(username: str, usernames: List[str] = None) -> List[Dict]:
    """Get permanent facts for user. usernames: aliases to merge."""
    if _dna_memory_system:
        return _dna_memory_system.get_user_facts(username, usernames)
    return []


def save_user_profile(username: str, profile_data: Dict):
    """Save user profile (persistent, per-user)."""
    if _dna_memory_system:
        _dna_memory_system.save_user_profile(username, profile_data)


def get_user_profile(username: str, usernames: List[str] = None) -> Optional[Dict]:
    """Get persistent profile for user. usernames: aliases to merge."""
    if _dna_memory_system:
        return _dna_memory_system.get_user_profile(username, usernames)
    return None


def compile_profiles_from_history() -> Dict:
    """Admin: scan all chat history and extract/update profiles for every user."""
    if _dna_memory_system:
        return _dna_memory_system.compile_profiles_from_history()
    return {"processed": 0, "users_updated": 0, "facts_added": 0}


def clean_bad_facts() -> Dict:
    """Admin: remove junk facts (bad favorite_X, fragments, filler interests)."""
    if _dna_memory_system:
        return _dna_memory_system.clean_bad_facts()
    return {"deleted": 0, "by_type": {}}


def get_all_known_profiles() -> List[Dict]:
    """Admin: return list of all users Luna has profile/fact data for."""
    if _dna_memory_system:
        return _dna_memory_system.get_all_known_profiles()
    return []


def get_user_profile_analysis(username: str, usernames: List[str] = None) -> str:
    """Get full profile analysis (facts + profile + memories) for prompt injection."""
    if _dna_memory_system:
        return _dna_memory_system.get_user_profile_analysis(username, usernames)
    return ""


def get_profile_gaps(username: str, usernames: List[str] = None) -> List[str]:
    """Get list of profile gaps (what Luna doesn't know - for asking questions)."""
    if _dna_memory_system:
        return _dna_memory_system.get_profile_gaps(username, usernames)
    return []

def recall_dna_memories(username: str, query: str, limit: int = 5,
                       usernames: List[str] = None) -> List[Dict]:
    """Recall relevant memories by expressing genes.
    usernames: optional list of aliases (e.g. ['Chris', 'solonaras']) to merge memories from.
    """
    if not _dna_memory_system:
        return []
    names = usernames or [username]
    seen = set()
    merged = []
    for name in names:
        for mem in _dna_memory_system.express_genes(name, query, limit=limit):
            key = (mem['user_message'][:50], mem['luna_response'][:50])
            if key not in seen:
                seen.add(key)
                merged.append(mem)
    # Sort by match_score desc, keep limit
    merged.sort(key=lambda m: m.get('match_score', 0), reverse=True)
    return merged[:limit]

def recall_dna_memories_with_vector_reasoning(username: str, query: str, limit: int = 5,
                                             usernames: List[str] = None) -> Dict:
    """Recall memories with enhanced vector reasoning capabilities"""
    if _dna_memory_system:
        # Get basic memories (with optional username aliases)
        memories = recall_dna_memories(username, query, limit, usernames=usernames)
        
        # Try to get vector reasoning if available
        try:
            from luna_vector_reasoning import get_vector_reasoning, reason_with_vectors
            vector_engine = get_vector_reasoning()
            if vector_engine:
                reasoning_result = reason_with_vectors(query, username, _dna_memory_system, usernames=usernames)
                return {
                    "memories": memories,
                    "vector_reasoning": reasoning_result,
                    "enhanced": True
                }
        except ImportError:
            pass
        
        return {
            "memories": memories,
            "vector_reasoning": None,
            "enhanced": False
        }
    return {"memories": [], "vector_reasoning": None, "enhanced": False}

