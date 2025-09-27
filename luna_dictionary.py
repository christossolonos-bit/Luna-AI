#!/usr/bin/env python3
# luna_dictionary.py
# Dictionary Module for Luna AI - Word Definitions, Synonyms, and Language Assistance

import requests
import json
import re
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
import sqlite3
import os

@dataclass
class WordDefinition:
    """Data class for word definitions"""
    word: str
    part_of_speech: str
    definition: str
    example: Optional[str] = None
    synonyms: List[str] = None
    antonyms: List[str] = None
    etymology: Optional[str] = None
    pronunciation: Optional[str] = None
    frequency: Optional[str] = None

@dataclass
class DictionaryResult:
    """Data class for dictionary search results"""
    word: str
    definitions: List[WordDefinition]
    total_definitions: int
    pronunciation: Optional[str] = None
    etymology: Optional[str] = None
    related_words: List[str] = None
    search_time: float = 0.0

class LunaDictionary:
    """Comprehensive dictionary system for Luna AI"""
    
    def __init__(self):
        self.api_keys = {
            "free_dictionary": None,  # Free Dictionary API (no key needed)
            "words_api": None,        # WordsAPI (requires key)
            "merriam_webster": None   # Merriam-Webster API (requires key)
        }
        
        # Cache for dictionary lookups
        self.cache = {}
        self.cache_duration = 3600  # 1 hour cache
        
        # Database for storing lookup history and favorites
        self.db_path = "luna_dictionary.db"
        self.init_database()
        
        # Common word patterns for detection
        self.word_patterns = {
            "definition_request": [
                r"what (does|is) (\w+) mean",
                r"define (\w+)",
                r"definition of (\w+)",
                r"what is the meaning of (\w+)",
                r"tell me about (\w+)",
                r"explain (\w+)",
                r"(\w+) meaning"
            ],
            "synonym_request": [
                r"synonym(s)? (for|of) (\w+)",
                r"similar words (for|to) (\w+)",
                r"other words for (\w+)",
                r"(\w+) synonym"
            ],
            "antonym_request": [
                r"antonym(s)? (for|of) (\w+)",
                r"opposite(s)? (of|for) (\w+)",
                r"(\w+) antonym"
            ],
            "spelling_request": [
                r"how do you spell (\w+)",
                r"spelling of (\w+)",
                r"correct spelling for (\w+)"
            ],
            "pronunciation_request": [
                r"how do you pronounce (\w+)",
                r"pronunciation of (\w+)",
                r"(\w+) pronunciation"
            ]
        }
        
        # Language learning features
        self.language_features = {
            "word_of_the_day": None,
            "vocabulary_builder": [],
            "difficulty_levels": ["beginner", "intermediate", "advanced"],
            "learning_categories": ["common_words", "academic", "business", "slang", "technical"]
        }
    
    def init_database(self):
        """Initialize dictionary database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create lookup history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS lookup_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word TEXT NOT NULL,
                    lookup_type TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    user_id TEXT DEFAULT 'default'
                )
            ''')
            
            # Create favorites table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS favorites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word TEXT NOT NULL,
                    definition TEXT,
                    notes TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    user_id TEXT DEFAULT 'default'
                )
            ''')
            
            # Create vocabulary table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vocabulary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word TEXT NOT NULL,
                    definition TEXT,
                    difficulty TEXT,
                    category TEXT,
                    mastered BOOLEAN DEFAULT FALSE,
                    review_count INTEGER DEFAULT 0,
                    last_review DATETIME,
                    user_id TEXT DEFAULT 'default'
                )
            ''')
            
            conn.commit()
            conn.close()
            print("✅ Dictionary database initialized")
            
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
    
    def detect_dictionary_request(self, text: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Detect if text contains a dictionary request"""
        text_lower = text.lower()
        
        # Check for definition requests
        for pattern in self.word_patterns["definition_request"]:
            match = re.search(pattern, text_lower)
            if match:
                word = match.group(2) if len(match.groups()) > 1 else match.group(1)
                return word, "definition", None
        
        # Check for synonym requests
        for pattern in self.word_patterns["synonym_request"]:
            match = re.search(pattern, text_lower)
            if match:
                word = match.group(2) if len(match.groups()) > 1 else match.group(1)
                return word, "synonyms", None
        
        # Check for antonym requests
        for pattern in self.word_patterns["antonym_request"]:
            match = re.search(pattern, text_lower)
            if match:
                word = match.group(2) if len(match.groups()) > 1 else match.group(1)
                return word, "antonyms", None
        
        # Check for spelling requests
        for pattern in self.word_patterns["spelling_request"]:
            match = re.search(pattern, text_lower)
            if match:
                word = match.group(1)
                return word, "spelling", None
        
        # Check for pronunciation requests
        for pattern in self.word_patterns["pronunciation_request"]:
            match = re.search(pattern, text_lower)
            if match:
                word = match.group(1)
                return word, "pronunciation", None
        
        # Check for general word lookups (single word or "what is X")
        words = text_lower.split()
        if len(words) == 1 and len(words[0]) > 2:
            return words[0], "definition", None
        
        # Check for "what is X" patterns
        if text_lower.startswith("what is ") and len(words) == 3:
            return words[2], "definition", None
        
        return None, None, None
    
    async def lookup_word(self, word: str, lookup_type: str = "definition") -> Optional[DictionaryResult]:
        """Look up a word in the dictionary"""
        start_time = time.time()
        
        # Clean the word
        word = word.strip().lower()
        
        # Check cache first
        cache_key = f"{word}_{lookup_type}"
        if cache_key in self.cache:
            cache_time, result = self.cache[cache_key]
            if time.time() - cache_time < self.cache_duration:
                return result
        
        try:
            # Try Free Dictionary API first (no key required)
            result = await self._lookup_free_dictionary(word, lookup_type)
            
            if result and result.definitions:
                # Cache the result
                self.cache[cache_key] = (time.time(), result)
                
                # Log lookup in database
                self._log_lookup(word, lookup_type)
                
                result.search_time = time.time() - start_time
                return result
            
            # Fallback to other APIs if available
            if self.api_keys["words_api"]:
                result = await self._lookup_words_api(word, lookup_type)
                if result:
                    self.cache[cache_key] = (time.time(), result)
                    self._log_lookup(word, lookup_type)
                    result.search_time = time.time() - start_time
                    return result
            
            return None
            
        except Exception as e:
            print(f"❌ Dictionary lookup error for '{word}': {e}")
            return None
    
    async def _lookup_free_dictionary(self, word: str, lookup_type: str) -> Optional[DictionaryResult]:
        """Look up word using Free Dictionary API"""
        try:
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                definitions = []
                pronunciation = None
                etymology = None
                related_words = []
                
                for entry in data:
                    # Extract pronunciation
                    if "phonetics" in entry and entry["phonetics"]:
                        for phonetic in entry["phonetics"]:
                            if "text" in phonetic:
                                pronunciation = phonetic["text"]
                                break
                    
                    # Extract etymology
                    if "etymologies" in entry and entry["etymologies"]:
                        etymology = entry["etymologies"][0]
                    
                    # Extract meanings
                    if "meanings" in entry:
                        for meaning in entry["meanings"]:
                            part_of_speech = meaning.get("partOfSpeech", "unknown")
                            
                            for definition in meaning.get("definitions", []):
                                word_def = WordDefinition(
                                    word=word,
                                    part_of_speech=part_of_speech,
                                    definition=definition.get("definition", ""),
                                    example=definition.get("example"),
                                    synonyms=definition.get("synonyms", []),
                                    antonyms=definition.get("antonyms", [])
                                )
                                definitions.append(word_def)
                    
                    # Extract related words
                    if "meanings" in entry:
                        for meaning in entry["meanings"]:
                            related_words.extend(meaning.get("synonyms", []))
                            related_words.extend(meaning.get("antonyms", []))
                
                if definitions:
                    return DictionaryResult(
                        word=word,
                        definitions=definitions,
                        total_definitions=len(definitions),
                        pronunciation=pronunciation,
                        etymology=etymology,
                        related_words=list(set(related_words))
                    )
            
            return None
            
        except Exception as e:
            print(f"❌ Free Dictionary API error: {e}")
            return None
    
    async def _lookup_words_api(self, word: str, lookup_type: str) -> Optional[DictionaryResult]:
        """Look up word using WordsAPI (requires API key)"""
        if not self.api_keys["words_api"]:
            return None
        
        try:
            url = f"https://wordsapiv1.p.rapidapi.com/words/{word}"
            headers = {
                "X-RapidAPI-Key": self.api_keys["words_api"],
                "X-RapidAPI-Host": "wordsapiv1.p.rapidapi.com"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                definitions = []
                pronunciation = data.get("pronunciation", {}).get("all")
                
                # Extract definitions
                if "results" in data:
                    for result in data["results"]:
                        word_def = WordDefinition(
                            word=word,
                            part_of_speech=result.get("partOfSpeech", "unknown"),
                            definition=result.get("definition", ""),
                            example=result.get("examples", [None])[0] if result.get("examples") else None,
                            synonyms=result.get("synonyms", []),
                            antonyms=result.get("antonyms", [])
                        )
                        definitions.append(word_def)
                
                if definitions:
                    return DictionaryResult(
                        word=word,
                        definitions=definitions,
                        total_definitions=len(definitions),
                        pronunciation=pronunciation
                    )
            
            return None
            
        except Exception as e:
            print(f"❌ WordsAPI error: {e}")
            return None
    
    def format_definition_response(self, result: DictionaryResult, lookup_type: str = "definition") -> str:
        """Format dictionary result into a natural response"""
        if not result or not result.definitions:
            return f"I couldn't find a definition for '{result.word}' in my dictionary."
        
        response_parts = []
        
        # Header
        if lookup_type == "definition":
            response_parts.append(f"📖 **{result.word.title()}**")
        elif lookup_type == "synonyms":
            response_parts.append(f"🔄 **Synonyms for '{result.word}':**")
        elif lookup_type == "antonyms":
            response_parts.append(f"⚖️ **Antonyms for '{result.word}':**")
        
        # Pronunciation
        if result.pronunciation:
            response_parts.append(f"🔊 Pronunciation: {result.pronunciation}")
        
        # Definitions
        if lookup_type == "definition":
            for i, definition in enumerate(result.definitions[:3], 1):  # Limit to 3 definitions
                response_parts.append(f"\n**{i}. {definition.part_of_speech.title()}:**")
                response_parts.append(f"   {definition.definition}")
                
                if definition.example:
                    response_parts.append(f"   *Example: {definition.example}*")
                
                if definition.synonyms and lookup_type == "definition":
                    synonyms_text = ", ".join(definition.synonyms[:5])  # Limit to 5 synonyms
                    if synonyms_text:
                        response_parts.append(f"   *Synonyms: {synonyms_text}*")
        
        # Synonyms/Antonyms specific response
        elif lookup_type in ["synonyms", "antonyms"]:
            all_words = []
            for definition in result.definitions:
                if lookup_type == "synonyms" and definition.synonyms:
                    all_words.extend(definition.synonyms)
                elif lookup_type == "antonyms" and definition.antonyms:
                    all_words.extend(definition.antonyms)
            
            if all_words:
                unique_words = list(set(all_words))[:10]  # Limit to 10 unique words
                response_parts.append(f"   {', '.join(unique_words)}")
            else:
                response_parts.append(f"   I couldn't find any {lookup_type} for '{result.word}'.")
        
        # Etymology
        if result.etymology and lookup_type == "definition":
            response_parts.append(f"\n📚 **Etymology:** {result.etymology}")
        
        # Related words
        if result.related_words and lookup_type == "definition":
            related_text = ", ".join(result.related_words[:8])  # Limit to 8 related words
            if related_text:
                response_parts.append(f"\n🔗 **Related words:** {related_text}")
        
        return "\n".join(response_parts)
    
    def add_to_favorites(self, word: str, definition: str = "", notes: str = "", user_id: str = "default"):
        """Add a word to favorites"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO favorites (word, definition, notes, user_id)
                VALUES (?, ?, ?, ?)
            ''', (word, definition, notes, user_id))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Error adding to favorites: {e}")
            return False
    
    def get_favorites(self, user_id: str = "default") -> List[Dict]:
        """Get user's favorite words"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT word, definition, notes, timestamp
                FROM favorites
                WHERE user_id = ?
                ORDER BY timestamp DESC
            ''', (user_id,))
            
            favorites = []
            for row in cursor.fetchall():
                favorites.append({
                    "word": row[0],
                    "definition": row[1],
                    "notes": row[2],
                    "timestamp": row[3]
                })
            
            conn.close()
            return favorites
            
        except Exception as e:
            print(f"❌ Error getting favorites: {e}")
            return []
    
    def add_to_vocabulary(self, word: str, definition: str = "", difficulty: str = "intermediate", 
                         category: str = "common_words", user_id: str = "default"):
        """Add a word to vocabulary builder"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO vocabulary (word, definition, difficulty, category, user_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (word, definition, difficulty, category, user_id))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Error adding to vocabulary: {e}")
            return False
    
    def get_vocabulary_words(self, difficulty: str = None, category: str = None, 
                           user_id: str = "default") -> List[Dict]:
        """Get vocabulary words with optional filtering"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = '''
                SELECT word, definition, difficulty, category, mastered, review_count, last_review
                FROM vocabulary
                WHERE user_id = ?
            '''
            params = [user_id]
            
            if difficulty:
                query += " AND difficulty = ?"
                params.append(difficulty)
            
            if category:
                query += " AND category = ?"
                params.append(category)
            
            query += " ORDER BY last_review ASC NULLS FIRST"
            
            cursor.execute(query, params)
            
            words = []
            for row in cursor.fetchall():
                words.append({
                    "word": row[0],
                    "definition": row[1],
                    "difficulty": row[2],
                    "category": row[3],
                    "mastered": bool(row[4]),
                    "review_count": row[5],
                    "last_review": row[6]
                })
            
            conn.close()
            return words
            
        except Exception as e:
            print(f"❌ Error getting vocabulary: {e}")
            return []
    
    def mark_word_mastered(self, word: str, user_id: str = "default") -> bool:
        """Mark a vocabulary word as mastered"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE vocabulary
                SET mastered = TRUE, last_review = CURRENT_TIMESTAMP
                WHERE word = ? AND user_id = ?
            ''', (word, user_id))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Error marking word mastered: {e}")
            return False
    
    def get_word_of_the_day(self) -> Optional[Dict]:
        """Get a word of the day for learning"""
        # This would typically connect to a word-of-the-day API
        # For now, return a hardcoded example
        return {
            "word": "serendipity",
            "definition": "The occurrence and development of events by chance in a happy or beneficial way",
            "part_of_speech": "noun",
            "example": "Finding that perfect coffee shop was pure serendipity!",
            "etymology": "From the Persian fairy tale 'The Three Princes of Serendip'"
        }
    
    def get_learning_suggestions(self, user_id: str = "default") -> List[Dict]:
        """Get personalized learning suggestions"""
        try:
            # Get words that need review
            vocabulary = self.get_vocabulary_words(user_id=user_id)
            
            suggestions = []
            
            # Words that haven't been reviewed recently
            unreviewed = [w for w in vocabulary if not w["last_review"]]
            if unreviewed:
                suggestions.append({
                    "type": "review_needed",
                    "title": "Words to Review",
                    "words": unreviewed[:5],
                    "description": "These words need your attention!"
                })
            
            # Words by difficulty
            for difficulty in self.language_features["difficulty_levels"]:
                diff_words = [w for w in vocabulary if w["difficulty"] == difficulty and not w["mastered"]]
                if diff_words:
                    suggestions.append({
                        "type": "difficulty_level",
                        "title": f"{difficulty.title()} Level Words",
                        "words": diff_words[:3],
                        "description": f"Practice your {difficulty} vocabulary"
                    })
            
            return suggestions
            
        except Exception as e:
            print(f"❌ Error getting learning suggestions: {e}")
            return []
    
    def _log_lookup(self, word: str, lookup_type: str, user_id: str = "default"):
        """Log a dictionary lookup in the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO lookup_history (word, lookup_type, user_id)
                VALUES (?, ?, ?)
            ''', (word, lookup_type, user_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Error logging lookup: {e}")
    
    def get_lookup_stats(self, user_id: str = "default") -> Dict:
        """Get dictionary usage statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total lookups
            cursor.execute('''
                SELECT COUNT(*) FROM lookup_history WHERE user_id = ?
            ''', (user_id,))
            total_lookups = cursor.fetchone()[0]
            
            # Most looked up words
            cursor.execute('''
                SELECT word, COUNT(*) as count
                FROM lookup_history
                WHERE user_id = ?
                GROUP BY word
                ORDER BY count DESC
                LIMIT 5
            ''', (user_id,))
            top_words = [{"word": row[0], "count": row[1]} for row in cursor.fetchall()]
            
            # Vocabulary progress
            cursor.execute('''
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN mastered THEN 1 ELSE 0 END) as mastered
                FROM vocabulary
                WHERE user_id = ?
            ''', (user_id,))
            vocab_stats = cursor.fetchone()
            
            conn.close()
            
            return {
                "total_lookups": total_lookups,
                "top_words": top_words,
                "vocabulary_total": vocab_stats[0] or 0,
                "vocabulary_mastered": vocab_stats[1] or 0
            }
            
        except Exception as e:
            print(f"❌ Error getting lookup stats: {e}")
            return {}

# Global instance
luna_dictionary = LunaDictionary()

# Convenience functions for easy integration
async def lookup_word_definition(word: str) -> Optional[str]:
    """Quick function to get word definition"""
    result = await luna_dictionary.lookup_word(word, "definition")
    if result:
        return luna_dictionary.format_definition_response(result, "definition")
    return None

async def get_word_synonyms(word: str) -> Optional[str]:
    """Quick function to get word synonyms"""
    result = await luna_dictionary.lookup_word(word, "synonyms")
    if result:
        return luna_dictionary.format_definition_response(result, "synonyms")
    return None

async def get_word_antonyms(word: str) -> Optional[str]:
    """Quick function to get word antonyms"""
    result = await luna_dictionary.lookup_word(word, "antonyms")
    if result:
        return luna_dictionary.format_definition_response(result, "antonyms")
    return None

def detect_dictionary_request(text: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Quick function to detect dictionary requests"""
    return luna_dictionary.detect_dictionary_request(text)

# Export main functions
__all__ = [
    'LunaDictionary',
    'luna_dictionary',
    'lookup_word_definition',
    'get_word_synonyms', 
    'get_word_antonyms',
    'detect_dictionary_request'
]
