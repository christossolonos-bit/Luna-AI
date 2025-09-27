#!/usr/bin/env python3
"""
BM25 Memory System for Luna
Advanced retrieval system using BM25 ranking for better context retrieval

Credits: Teto - Teacher and BM25 Indexing Expert
Inspired by Teto's expertise in information retrieval and ranking algorithms
"""

import sqlite3
import math
import re
import json
from collections import defaultdict, Counter
from typing import List, Dict, Tuple, Optional
import time

class BM25MemorySystem:
    """
    BM25-based memory retrieval system for Luna
    Credits: Teto - Teacher and BM25 Indexing Expert
    """
    
    def __init__(self, db_path: str = "luna_memories.db", k1: float = 1.2, b: float = 0.75):
        """
        Initialize BM25 memory system
        
        Args:
            db_path: Path to SQLite database
            k1: Term frequency saturation parameter (1.2-2.0)
            b: Length normalization parameter (0.0-1.0)
        """
        self.db_path = db_path
        self.k1 = k1
        self.b = b
        self.teacher_name = "Teto"  # BM25 Indexing Expert
        
        # BM25 data structures
        self.documents = {}  # doc_id -> document content
        self.document_lengths = {}  # doc_id -> document length
        self.term_frequencies = defaultdict(dict)  # term -> {doc_id: frequency}
        self.document_frequencies = defaultdict(int)  # term -> number of docs containing term
        self.total_documents = 0
        self.average_document_length = 0
        
        # Index status
        self.is_indexed = False
        self.last_index_update = 0
        
        print("🧠 BM25 Memory System initialized")
        print(f"📚 Credits: {self.teacher_name} - BM25 Indexing and Information Retrieval Expert")
    
    def _preprocess_text(self, text: str) -> List[str]:
        """Preprocess text for indexing"""
        if not text:
            return []
        
        # Convert to lowercase and extract words
        text = text.lower()
        # Remove special characters but keep alphanumeric and spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        # Split into words and remove empty strings
        words = [word.strip() for word in text.split() if word.strip()]
        
        # Simple stemming (remove common suffixes)
        stemmed_words = []
        for word in words:
            if len(word) > 3:
                # Remove common suffixes
                if word.endswith(('ing', 'ed', 'er', 'ly', 'tion', 'sion')):
                    word = word[:-3] if word.endswith(('ing', 'ed', 'er', 'ly')) else word[:-4]
            stemmed_words.append(word)
        
        return stemmed_words
    
    def _build_index(self):
        """Build BM25 index from database"""
        print("🔍 Building BM25 index from memory database...")
        start_time = time.time()
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all memories and conversations
            cursor.execute("""
                SELECT id, content, memory_type, importance, timestamp 
                FROM memories 
                WHERE content IS NOT NULL AND content != ''
            """)
            memories = cursor.fetchall()
            
            cursor.execute("""
                SELECT id, user_message, luna_response, mood, timestamp
                FROM conversations 
                WHERE (user_message IS NOT NULL AND user_message != '') 
                OR (luna_response IS NOT NULL AND luna_response != '')
            """)
            conversations = cursor.fetchall()
            
            conn.close()
            
            # Clear existing index
            self.documents.clear()
            self.document_lengths.clear()
            self.term_frequencies.clear()
            self.document_frequencies.clear()
            
            doc_id = 0
            
            # Index memories
            for memory_id, content, memory_type, importance, timestamp in memories:
                if content:
                    # Create document content with metadata
                    doc_content = f"{content} [type: {memory_type}] [importance: {importance}]"
                    self.documents[doc_id] = doc_content
                    
                    # Preprocess and count terms
                    terms = self._preprocess_text(doc_content)
                    self.document_lengths[doc_id] = len(terms)
                    
                    # Count term frequencies
                    term_counts = Counter(terms)
                    for term, count in term_counts.items():
                        self.term_frequencies[term][doc_id] = count
                        self.document_frequencies[term] += 1
                    
                    doc_id += 1
            
            # Index conversations
            for conv_id, user_message, luna_response, mood, timestamp in conversations:
                # Combine user message and Luna response
                combined_content = ""
                if user_message:
                    combined_content += f"User: {user_message} "
                if luna_response:
                    combined_content += f"Luna: {luna_response} "
                
                if combined_content:
                    combined_content += f"[mood: {mood}] [conversation]"
                    self.documents[doc_id] = combined_content
                    
                    # Preprocess and count terms
                    terms = self._preprocess_text(combined_content)
                    self.document_lengths[doc_id] = len(terms)
                    
                    # Count term frequencies
                    term_counts = Counter(terms)
                    for term, count in term_counts.items():
                        self.term_frequencies[term][doc_id] = count
                        self.document_frequencies[term] += 1
                    
                    doc_id += 1
            
            # Calculate statistics
            self.total_documents = len(self.documents)
            if self.total_documents > 0:
                self.average_document_length = sum(self.document_lengths.values()) / self.total_documents
            else:
                self.average_document_length = 0
            
            self.is_indexed = True
            self.last_index_update = time.time()
            
            build_time = time.time() - start_time
            print(f"✅ BM25 index built successfully!")
            print(f"   📊 Indexed {self.total_documents} documents")
            print(f"   📊 Average document length: {self.average_document_length:.1f} terms")
            print(f"   📊 Unique terms: {len(self.term_frequencies)}")
            print(f"   ⏱️ Build time: {build_time:.2f} seconds")
            
        except Exception as e:
            print(f"❌ Error building BM25 index: {e}")
            self.is_indexed = False
    
    def _calculate_idf(self, term: str) -> float:
        """Calculate Inverse Document Frequency for a term"""
        if term not in self.document_frequencies or self.document_frequencies[term] == 0:
            return 0.0
        
        # IDF = log((N - df + 0.5) / (df + 0.5))
        # where N = total documents, df = document frequency
        N = self.total_documents
        df = self.document_frequencies[term]
        
        idf = math.log((N - df + 0.5) / (df + 0.5))
        return idf
    
    def _calculate_bm25_score(self, query_terms: List[str], doc_id: int) -> float:
        """Calculate BM25 score for a document given query terms"""
        if doc_id not in self.documents:
            return 0.0
        
        score = 0.0
        doc_length = self.document_lengths[doc_id]
        
        for term in query_terms:
            if term in self.term_frequencies and doc_id in self.term_frequencies[term]:
                # Term frequency in document
                tf = self.term_frequencies[term][doc_id]
                
                # Inverse document frequency
                idf = self._calculate_idf(term)
                
                # BM25 formula
                # score += idf * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * (doc_length / avg_doc_length)))
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * (doc_length / self.average_document_length))
                
                score += idf * (numerator / denominator)
        
        return score
    
    def search(self, query: str, limit: int = 10, min_score: float = 0.1) -> List[Dict]:
        """
        Search for relevant documents using BM25 ranking
        
        Args:
            query: Search query
            limit: Maximum number of results
            min_score: Minimum BM25 score threshold
            
        Returns:
            List of relevant documents with scores
        """
        if not self.is_indexed:
            print("⚠️ BM25 index not built, building now...")
            self._build_index()
        
        if self.total_documents == 0:
            print("⚠️ No documents in index")
            return []
        
        # Preprocess query
        query_terms = self._preprocess_text(query)
        if not query_terms:
            print("⚠️ No valid terms in query")
            return []
        
        print(f"🔍 BM25 search: '{query}' -> terms: {query_terms}")
        
        # Calculate BM25 scores for all documents
        doc_scores = []
        for doc_id in self.documents:
            score = self._calculate_bm25_score(query_terms, doc_id)
            if score >= min_score:
                doc_scores.append((doc_id, score))
        
        # Sort by score (descending)
        doc_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return top results
        results = []
        for doc_id, score in doc_scores[:limit]:
            results.append({
                'doc_id': doc_id,
                'content': self.documents[doc_id],
                'score': score,
                'length': self.document_lengths[doc_id]
            })
        
        print(f"📊 BM25 search returned {len(results)} results")
        return results
    
    def get_relevant_memories(self, query: str, limit: int = 5) -> List[str]:
        """Get relevant memories using BM25 ranking"""
        results = self.search(query, limit=limit)
        return [result['content'] for result in results]
    
    def get_relevant_conversations(self, query: str, limit: int = 5) -> List[str]:
        """Get relevant conversations using BM25 ranking"""
        results = self.search(query, limit=limit)
        # Filter for conversation-type results
        conversations = []
        for result in results:
            if '[conversation]' in result['content']:
                conversations.append(result['content'])
        return conversations[:limit]
    
    def update_index(self):
        """Update the BM25 index (rebuild if needed)"""
        print("🔄 Updating BM25 index...")
        self._build_index()
    
    def get_index_stats(self) -> Dict:
        """Get statistics about the BM25 index"""
        return {
            'is_indexed': self.is_indexed,
            'total_documents': self.total_documents,
            'average_document_length': self.average_document_length,
            'unique_terms': len(self.term_frequencies),
            'last_update': self.last_index_update,
            'parameters': {
                'k1': self.k1,
                'b': self.b
            }
        }
    
    def test_search(self, test_queries: List[str]):
        """Test the BM25 system with sample queries"""
        print("🧪 Testing BM25 search system...")
        print("=" * 50)
        
        for query in test_queries:
            print(f"\n🔍 Query: '{query}'")
            results = self.search(query, limit=3)
            
            if results:
                for i, result in enumerate(results, 1):
                    print(f"  {i}. Score: {result['score']:.3f}")
                    print(f"     Content: {result['content'][:100]}...")
            else:
                print("  No results found")
        
        print("\n" + "=" * 50)

# Global BM25 system instance
bm25_system = None

def initialize_bm25_system(db_path: str = "luna_memories.db") -> BM25MemorySystem:
    """Initialize the global BM25 system"""
    global bm25_system
    bm25_system = BM25MemorySystem(db_path)
    return bm25_system

def get_bm25_system() -> Optional[BM25MemorySystem]:
    """Get the global BM25 system instance"""
    return bm25_system

def bm25_search_memories(query: str, limit: int = 5) -> List[str]:
    """Search memories using BM25 ranking"""
    if bm25_system is None:
        initialize_bm25_system()
    
    return bm25_system.get_relevant_memories(query, limit)

def bm25_search_conversations(query: str, limit: int = 5) -> List[str]:
    """Search conversations using BM25 ranking"""
    if bm25_system is None:
        initialize_bm25_system()
    
    return bm25_system.get_relevant_conversations(query, limit)

def bm25_research_memory_database(query: str, limit: int = 10) -> str:
    """Enhanced research function using BM25 ranking"""
    if bm25_system is None:
        initialize_bm25_system()
    
    results = bm25_system.search(query, limit=limit)
    
    if not results:
        return "No relevant memories found for this query."
    
    # Format results
    formatted_results = []
    for i, result in enumerate(results, 1):
        score = result['score']
        content = result['content']
        
        # Truncate long content
        if len(content) > 200:
            content = content[:200] + "..."
        
        formatted_results.append(f"{i}. [Score: {score:.3f}] {content}")
    
    return f"Found {len(results)} relevant memories:\n" + "\n".join(formatted_results)

def bm25_with_pairing_engine_search(query: str, limit: int = 5) -> List[Dict]:
    """Enhanced search combining BM25 with pairing engine"""
    if bm25_system is None:
        initialize_bm25_system()
    
    # Get BM25 results
    bm25_results = bm25_system.search(query, limit=limit)
    
    # Try to get pairing engine results if available
    pairing_results = []
    try:
        from luna_pairing_integration import get_luna_pairing_engine
        pairing_engine = get_luna_pairing_engine()
        if pairing_engine:
            pairing_matches = pairing_engine.find_best_response(query, top_k=limit, min_similarity=0.3)
            for pair_id, similarity, data in pairing_matches:
                pairing_results.append({
                    'content': data['luna_response'],
                    'score': similarity,
                    'source': 'pairing_engine',
                    'metadata': data['metadata']
                })
    except Exception as e:
        print(f"⚠️ Pairing engine integration error: {e}")
    
    # Combine and rank results
    all_results = []
    
    # Add BM25 results
    for result in bm25_results:
        all_results.append({
            'content': result['content'],
            'score': result['score'],
            'source': 'bm25',
            'metadata': result.get('metadata', {})
        })
    
    # Add pairing engine results
    all_results.extend(pairing_results)
    
    # Sort by score and return top results
    all_results.sort(key=lambda x: x['score'], reverse=True)
    return all_results[:limit]

if __name__ == "__main__":
    # Test the BM25 system
    print("🚀 Testing BM25 Memory System")
    print("=" * 50)
    
    # Initialize system
    system = initialize_bm25_system()
    
    # Test queries
    test_queries = [
        "gaming",
        "streaming setup",
        "community chat",
        "technical problems",
        "happy memories",
        "discord voice",
        "whisper transcription"
    ]
    
    # Run tests
    system.test_search(test_queries)
    
    # Show stats
    stats = system.get_index_stats()
    print(f"\n📊 Index Statistics:")
    print(f"   Total documents: {stats['total_documents']}")
    print(f"   Unique terms: {stats['unique_terms']}")
    print(f"   Average doc length: {stats['average_document_length']:.1f}")
    print(f"   Parameters: k1={stats['parameters']['k1']}, b={stats['parameters']['b']}")
