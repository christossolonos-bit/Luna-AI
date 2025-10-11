# luna_advanced_nlp.py
"""
🧠 Luna Advanced NLP Processing System
Advanced natural language processing capabilities including NER, dependency parsing,
semantic analysis, intent classification, and topic modeling.
"""

import spacy
import nltk
from transformers import pipeline, AutoTokenizer, AutoModel
import re
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import json
import sqlite3
from collections import defaultdict, Counter
import threading
import time

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger')
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag import pos_tag
from nltk.stem import WordNetLemmatizer

@dataclass
class Entity:
    """Named Entity"""
    text: str
    label: str
    start: int
    end: int
    confidence: float = 0.0

@dataclass
class Intent:
    """User Intent Classification"""
    intent: str
    confidence: float
    entities: List[Entity] = None
    sentiment: str = "neutral"
    topics: List[str] = None

@dataclass
class DependencyRelation:
    """Dependency parsing relation"""
    head: str
    dep: str
    relation: str
    head_pos: str
    dep_pos: str

@dataclass
class SemanticAnalysis:
    """Semantic analysis results"""
    entities: List[Entity]
    dependencies: List[DependencyRelation]
    intent: Intent
    topics: List[str]
    sentiment: str
    complexity_score: float
    coherence_score: float

class LunaAdvancedNLP:
    """Advanced NLP Processing System for Luna"""
    
    def __init__(self):
        """Initialize the Advanced NLP system"""
        self.nlp = None
        self.sentiment_analyzer = None
        self.intent_classifier = None
        self.topic_modeler = None
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Initialize database
        self.init_database()
        
        # Load models
        self.load_models()
        
        print("🧠 Luna Advanced NLP System initialized!")
        print("   📝 Named Entity Recognition (NER)")
        print("   🔗 Dependency Parsing")
        print("   🎯 Intent Classification")
        print("   📊 Sentiment Analysis")
        print("   🏷️ Topic Modeling")
        print("   🧠 Semantic Analysis")
    
    def load_models(self):
        """Load NLP models"""
        try:
            # Load spaCy model
            print("📥 Loading spaCy English model...")
            self.nlp = spacy.load("en_core_web_sm")
            print("✅ spaCy model loaded")
            
            # Load sentiment analyzer
            print("📥 Loading sentiment analyzer...")
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                return_all_scores=True
            )
            print("✅ Sentiment analyzer loaded")
            
            # Load intent classifier (using a general model)
            print("📥 Loading intent classifier...")
            self.intent_classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli"
            )
            print("✅ Intent classifier loaded")
            
        except Exception as e:
            print(f"⚠️ Error loading NLP models: {e}")
            # Fallback to basic functionality
            self.nlp = None
            self.sentiment_analyzer = None
            self.intent_classifier = None
    
    def init_database(self):
        """Initialize NLP analysis database"""
        try:
            conn = sqlite3.connect('luna_nlp_analysis.db')
            cursor = conn.cursor()
            
            # Create entities table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS entities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    label TEXT NOT NULL,
                    confidence REAL,
                    context TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create intents table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS intents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    intent TEXT NOT NULL,
                    confidence REAL,
                    entities TEXT,
                    sentiment TEXT,
                    topics TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create topics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS topics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    topics TEXT NOT NULL,
                    weights TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            print("✅ NLP analysis database initialized")
            
        except Exception as e:
            print(f"⚠️ Error initializing NLP database: {e}")
    
    def extract_entities(self, text: str) -> List[Entity]:
        """Extract named entities from text"""
        entities = []
        
        if not self.nlp:
            return entities
        
        try:
            doc = self.nlp(text)
            
            for ent in doc.ents:
                entity = Entity(
                    text=ent.text,
                    label=ent.label_,
                    start=ent.start_char,
                    end=ent.end_char,
                    confidence=0.9  # spaCy doesn't provide confidence scores
                )
                entities.append(entity)
            
            # Store entities in database
            self.store_entities(text, entities)
            
        except Exception as e:
            print(f"⚠️ Error extracting entities: {e}")
        
        return entities
    
    def parse_dependencies(self, text: str) -> List[DependencyRelation]:
        """Parse dependency relations"""
        dependencies = []
        
        if not self.nlp:
            return dependencies
        
        try:
            doc = self.nlp(text)
            
            for token in doc:
                if not token.is_space and not token.is_punct:
                    dep_rel = DependencyRelation(
                        head=token.head.text,
                        dep=token.text,
                        relation=token.dep_,
                        head_pos=token.head.pos_,
                        dep_pos=token.pos_
                    )
                    dependencies.append(dep_rel)
            
        except Exception as e:
            print(f"⚠️ Error parsing dependencies: {e}")
        
        return dependencies
    
    def analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of text"""
        if not self.sentiment_analyzer:
            return "neutral"
        
        try:
            # Truncate text if too long
            if len(text) > 512:
                text = text[:512]
            
            results = self.sentiment_analyzer(text)
            
            # Get the highest scoring sentiment
            best_result = max(results, key=lambda x: x['score'])
            sentiment = best_result['label'].lower()
            
            # Map to our sentiment categories
            sentiment_map = {
                'positive': 'positive',
                'negative': 'negative',
                'neutral': 'neutral',
                'lab_0': 'negative',
                'lab_1': 'neutral',
                'lab_2': 'positive'
            }
            
            return sentiment_map.get(sentiment, 'neutral')
            
        except Exception as e:
            print(f"⚠️ Error analyzing sentiment: {e}")
            return "neutral"
    
    def classify_intent(self, text: str) -> Intent:
        """Classify user intent"""
        if not self.intent_classifier:
            return Intent(intent="unknown", confidence=0.0)
        
        try:
            # Common intents for Luna
            intent_labels = [
                "question",
                "greeting",
                "complaint",
                "compliment",
                "request",
                "command",
                "conversation",
                "emotional_support",
                "information_seeking",
                "social_interaction",
                "creative_request",
                "technical_help"
            ]
            
            # Truncate text if too long
            if len(text) > 512:
                text = text[:512]
            
            result = self.intent_classifier(text, intent_labels)
            
            intent = result['labels'][0]
            confidence = result['scores'][0]
            
            # Extract entities and sentiment
            entities = self.extract_entities(text)
            sentiment = self.analyze_sentiment(text)
            topics = self.extract_topics(text)
            
            intent_obj = Intent(
                intent=intent,
                confidence=confidence,
                entities=entities,
                sentiment=sentiment,
                topics=topics
            )
            
            # Store intent analysis
            self.store_intent(text, intent_obj)
            
            return intent_obj
            
        except Exception as e:
            print(f"⚠️ Error classifying intent: {e}")
            return Intent(intent="unknown", confidence=0.0)
    
    def extract_topics(self, text: str) -> List[str]:
        """Extract topics from text using simple keyword extraction"""
        topics = []
        
        try:
            # Tokenize and clean text
            tokens = word_tokenize(text.lower())
            tokens = [token for token in tokens if token.isalpha() and token not in self.stop_words]
            
            # POS tagging
            pos_tags = pos_tag(tokens)
            
            # Extract nouns and adjectives as potential topics
            important_words = []
            for word, pos in pos_tags:
                if pos in ['NN', 'NNS', 'NNP', 'NNPS', 'JJ', 'JJR', 'JJS']:
                    important_words.append(self.lemmatizer.lemmatize(word))
            
            # Count frequency and get top topics
            word_counts = Counter(important_words)
            topics = [word for word, count in word_counts.most_common(5) if count > 0]
            
            # Store topics
            self.store_topics(text, topics)
            
        except Exception as e:
            print(f"⚠️ Error extracting topics: {e}")
        
        return topics
    
    def analyze_semantics(self, text: str) -> SemanticAnalysis:
        """Perform comprehensive semantic analysis"""
        try:
            # Extract all components
            entities = self.extract_entities(text)
            dependencies = self.parse_dependencies(text)
            intent = self.classify_intent(text)
            topics = self.extract_topics(text)
            sentiment = self.analyze_sentiment(text)
            
            # Calculate complexity score
            complexity_score = self.calculate_complexity(text, dependencies)
            
            # Calculate coherence score
            coherence_score = self.calculate_coherence(text, entities, topics)
            
            analysis = SemanticAnalysis(
                entities=entities,
                dependencies=dependencies,
                intent=intent,
                topics=topics,
                sentiment=sentiment,
                complexity_score=complexity_score,
                coherence_score=coherence_score
            )
            
            return analysis
            
        except Exception as e:
            print(f"⚠️ Error in semantic analysis: {e}")
            return SemanticAnalysis(
                entities=[],
                dependencies=[],
                intent=Intent(intent="unknown", confidence=0.0),
                topics=[],
                sentiment="neutral",
                complexity_score=0.0,
                coherence_score=0.0
            )
    
    def calculate_complexity(self, text: str, dependencies: List[DependencyRelation]) -> float:
        """Calculate text complexity score"""
        try:
            # Factors: sentence length, dependency depth, vocabulary diversity
            sentences = sent_tokenize(text)
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
            
            # Dependency complexity (average dependency depth)
            dep_complexity = len(dependencies) / len(text.split()) if text.split() else 0
            
            # Vocabulary diversity (unique words / total words)
            words = word_tokenize(text.lower())
            unique_words = set(words)
            vocab_diversity = len(unique_words) / len(words) if words else 0
            
            # Combine factors (normalized to 0-1)
            complexity = min(1.0, (avg_sentence_length / 20 + dep_complexity + vocab_diversity) / 3)
            
            return complexity
            
        except Exception as e:
            print(f"⚠️ Error calculating complexity: {e}")
            return 0.0
    
    def calculate_coherence(self, text: str, entities: List[Entity], topics: List[str]) -> float:
        """Calculate text coherence score"""
        try:
            # Factors: entity consistency, topic coherence, sentence flow
            entity_coherence = min(1.0, len(set(e.label for e in entities)) / max(1, len(entities)))
            topic_coherence = min(1.0, len(topics) / 5)  # More topics = more coherent
            
            # Simple sentence flow (based on transitions)
            transitions = ['however', 'therefore', 'moreover', 'furthermore', 'consequently', 'meanwhile']
            transition_count = sum(1 for trans in transitions if trans in text.lower())
            flow_score = min(1.0, transition_count / 3)
            
            coherence = (entity_coherence + topic_coherence + flow_score) / 3
            return coherence
            
        except Exception as e:
            print(f"⚠️ Error calculating coherence: {e}")
            return 0.0
    
    def store_entities(self, text: str, entities: List[Entity]):
        """Store entities in database"""
        try:
            conn = sqlite3.connect('luna_nlp_analysis.db')
            cursor = conn.cursor()
            
            for entity in entities:
                cursor.execute('''
                    INSERT INTO entities (text, label, confidence, context)
                    VALUES (?, ?, ?, ?)
                ''', (entity.text, entity.label, entity.confidence, text[:100]))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Error storing entities: {e}")
    
    def store_intent(self, text: str, intent: Intent):
        """Store intent analysis in database"""
        try:
            conn = sqlite3.connect('luna_nlp_analysis.db')
            cursor = conn.cursor()
            
            entities_str = json.dumps([e.__dict__ for e in intent.entities]) if intent.entities else "[]"
            topics_str = json.dumps(intent.topics) if intent.topics else "[]"
            
            cursor.execute('''
                INSERT INTO intents (text, intent, confidence, entities, sentiment, topics)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (text[:500], intent.intent, intent.confidence, entities_str, intent.sentiment, topics_str))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Error storing intent: {e}")
    
    def store_topics(self, text: str, topics: List[str]):
        """Store topics in database"""
        try:
            conn = sqlite3.connect('luna_nlp_analysis.db')
            cursor = conn.cursor()
            
            topics_str = json.dumps(topics)
            weights_str = json.dumps([1.0] * len(topics))  # Simple equal weights
            
            cursor.execute('''
                INSERT INTO topics (text, topics, weights)
                VALUES (?, ?, ?)
            ''', (text[:500], topics_str, weights_str))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Error storing topics: {e}")
    
    def get_analysis_stats(self) -> Dict[str, Any]:
        """Get NLP analysis statistics"""
        try:
            conn = sqlite3.connect('luna_nlp_analysis.db')
            cursor = conn.cursor()
            
            # Entity stats
            cursor.execute('SELECT COUNT(*) FROM entities')
            entity_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT label, COUNT(*) FROM entities GROUP BY label')
            entity_types = dict(cursor.fetchall())
            
            # Intent stats
            cursor.execute('SELECT COUNT(*) FROM intents')
            intent_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT intent, COUNT(*) FROM intents GROUP BY intent')
            intent_types = dict(cursor.fetchall())
            
            # Topic stats
            cursor.execute('SELECT COUNT(*) FROM topics')
            topic_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_analyses': intent_count,
                'entity_count': entity_count,
                'entity_types': entity_types,
                'intent_types': intent_types,
                'topic_analyses': topic_count
            }
            
        except Exception as e:
            print(f"⚠️ Error getting analysis stats: {e}")
            return {}

# Global instance
advanced_nlp_system = None

def initialize_advanced_nlp():
    """Initialize the Advanced NLP system"""
    global advanced_nlp_system
    try:
        advanced_nlp_system = LunaAdvancedNLP()
        return advanced_nlp_system
    except Exception as e:
        print(f"⚠️ Failed to initialize Advanced NLP: {e}")
        return None

def get_advanced_nlp():
    """Get the Advanced NLP system instance"""
    return advanced_nlp_system

def analyze_text_advanced(text: str) -> SemanticAnalysis:
    """Analyze text with advanced NLP"""
    if not advanced_nlp_system:
        return SemanticAnalysis(
            entities=[],
            dependencies=[],
            intent=Intent(intent="unknown", confidence=0.0),
            topics=[],
            sentiment="neutral",
            complexity_score=0.0,
            coherence_score=0.0
        )
    
    return advanced_nlp_system.analyze_semantics(text)

def extract_entities_advanced(text: str) -> List[Entity]:
    """Extract entities with advanced NLP"""
    if not advanced_nlp_system:
        return []
    
    return advanced_nlp_system.extract_entities(text)

def classify_intent_advanced(text: str) -> Intent:
    """Classify intent with advanced NLP"""
    if not advanced_nlp_system:
        return Intent(intent="unknown", confidence=0.0)
    
    return advanced_nlp_system.classify_intent(text)

def get_nlp_stats():
    """Get NLP analysis statistics"""
    if not advanced_nlp_system:
        return {}
    
    return advanced_nlp_system.get_analysis_stats()
