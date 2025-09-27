#!/usr/bin/env python3
"""
Hybrid Retrieval System for Luna
Implements the hybrid retrieval formula: s_hyb(m) = α ⋅ ŝ_BM25(m) + (1 - α) ⋅ ŝ_RAG(m)
Final score: s_final(m) = s_hyb(m) × imp_t(m)

Credits: 𝜟𝒎𝜼𝜺𝒔𝒊𝜶𝝇 (Amnesia) - Teacher and AI Companion Memory Systems Expert
Credits: Teto - Teacher and BM25 Indexing Expert
Inspired by Layla AI's advanced memory organization and Teto's BM25 expertise
"""

import math
import time
import sqlite3
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import numpy as np

class HybridRetrievalSystem:
    """
    Hybrid retrieval system combining BM25, RAG, and time-dependent importance
    Credits: 𝜟𝒎𝜼𝜺𝒔𝒊𝜶𝝇 (Amnesia) - Inspired by Layla AI's memory architecture
    Credits: Teto - BM25 Indexing and Information Retrieval Expert
    """
    
    def __init__(self, alpha: float = 0.7, time_decay_factor: float = 0.1):
        """
        Initialize hybrid retrieval system
        
        Args:
            alpha: Weighting factor for BM25 vs RAG (0.0 = pure RAG, 1.0 = pure BM25)
            time_decay_factor: Controls how much older memories decay in importance
        """
        self.alpha = alpha  # BM25 weight
        self.time_decay_factor = time_decay_factor
        self.rag_weight = 1.0 - alpha  # RAG weight
        self.teacher_name = "𝜟𝒎𝜼𝜺𝒔𝒊𝜶𝝇"  # Amnesia - Teacher
        self.bm25_teacher = "Teto"  # BM25 Expert
        
        print(f"🧠 Hybrid Retrieval System initialized (α={alpha:.2f})")
        print(f"📚 Credits: {self.teacher_name} - Layla AI Memory Architecture")
        print(f"📚 Credits: {self.bm25_teacher} - BM25 Indexing and Information Retrieval")
    
    def normalize_score(self, score: float, min_score: float = 0.0, max_score: float = 1.0) -> float:
        """Normalize a score to [0, 1] range"""
        if max_score == min_score:
            return 0.5
        return max(0.0, min(1.0, (score - min_score) / (max_score - min_score)))
    
    def calculate_time_importance(self, timestamp: str, current_time: Optional[datetime] = None) -> float:
        """
        Calculate time-dependent importance factor: imp_t(m)
        More recent memories have higher importance
        """
        if current_time is None:
            current_time = datetime.now()
        
        try:
            # Parse timestamp (handle different formats)
            if isinstance(timestamp, str):
                if 'T' in timestamp:
                    # ISO format
                    memory_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                else:
                    # SQLite datetime format
                    memory_time = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            else:
                memory_time = timestamp
            
            # Calculate time difference in days
            time_diff = (current_time - memory_time).total_seconds() / (24 * 3600)  # Convert to days
            
            # Exponential decay: imp_t = e^(-λt)
            # where λ is the decay factor and t is time in days
            importance = math.exp(-self.time_decay_factor * time_diff)
            
            # Ensure importance is between 0.1 and 1.0
            return max(0.1, min(1.0, importance))
            
        except Exception as e:
            print(f"⚠️ Error calculating time importance: {e}")
            return 0.5  # Default neutral importance
    
    def calculate_rag_score(self, content: str, query: str, metadata: Dict = None) -> float:
        """
        Calculate RAG (Retrieval-Augmented Generation) score
        Based on semantic similarity and content quality
        """
        if not content or not query:
            return 0.0
        
        # Simple RAG scoring based on:
        # 1. Keyword overlap
        # 2. Content length (more detailed = higher score)
        # 3. Metadata importance
        # 4. Content quality indicators
        
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())
        
        # Keyword overlap score
        overlap = len(query_words & content_words)
        total_query_words = len(query_words)
        keyword_score = overlap / max(total_query_words, 1)
        
        # Content length score (normalized)
        content_length = len(content.split())
        length_score = min(1.0, content_length / 100.0)  # Normalize to 100 words
        
        # Metadata importance boost
        importance_boost = 0.0
        if metadata:
            if metadata.get('importance', 0) > 3:
                importance_boost = 0.2
            elif metadata.get('importance', 0) > 2:
                importance_boost = 0.1
        
        # Content quality indicators
        quality_indicators = ['important', 'special', 'favorite', 'love', 'hate', 'always', 'never']
        quality_score = sum(1 for indicator in quality_indicators if indicator in content.lower()) * 0.05
        
        # Combine scores
        rag_score = (keyword_score * 0.5 + length_score * 0.3 + importance_boost + quality_score)
        
        return min(1.0, rag_score)
    
    def calculate_hybrid_score(self, bm25_score: float, rag_score: float) -> float:
        """
        Calculate hybrid score: s_hyb(m) = α ⋅ ŝ_BM25(m) + (1 - α) ⋅ ŝ_RAG(m)
        """
        # Normalize scores to [0, 1] range
        normalized_bm25 = self.normalize_score(bm25_score, 0.0, 20.0)  # BM25 scores typically 0-20
        normalized_rag = self.normalize_score(rag_score, 0.0, 1.0)  # RAG scores already 0-1
        
        # Calculate hybrid score
        hybrid_score = self.alpha * normalized_bm25 + self.rag_weight * normalized_rag
        
        return hybrid_score
    
    def calculate_final_score(self, hybrid_score: float, time_importance: float) -> float:
        """
        Calculate final score: s_final(m) = s_hyb(m) × imp_t(m)
        """
        return hybrid_score * time_importance
    
    def calculate_enhanced_hybrid_score(self, bm25_score: float, rag_score: float, pairing_score: float = 0.0, pairing_weight: float = 0.2) -> float:
        """Enhanced hybrid scoring including pairing engine results"""
        # Original hybrid score
        original_hybrid = self.calculate_hybrid_score(bm25_score, rag_score)
        
        # Add pairing engine contribution
        if pairing_score > 0:
            # Adjust weights to accommodate pairing engine
            adjusted_alpha = self.alpha * (1 - pairing_weight)
            adjusted_rag_weight = self.rag_weight * (1 - pairing_weight)
            
            # Calculate enhanced score
            enhanced_score = (adjusted_alpha * self.normalize_score(bm25_score, 0, 10) + 
                            adjusted_rag_weight * rag_score + 
                            pairing_weight * pairing_score)
            
            return enhanced_score
        
        return original_hybrid
    
    def hybrid_search(self, query: str, bm25_results: List[Dict], limit: int = 10) -> List[Dict]:
        """
        Perform hybrid search combining BM25 and RAG scores
        
        Args:
            query: Search query
            bm25_results: Results from BM25 system
            limit: Maximum number of results
            
        Returns:
            List of results with hybrid scores
        """
        if not bm25_results:
            return []
        
        enhanced_results = []
        current_time = datetime.now()
        
        for result in bm25_results:
            # Extract information
            content = result.get('content', '')
            bm25_score = result.get('score', 0.0)
            metadata = result.get('metadata', {})
            timestamp = metadata.get('timestamp', current_time.isoformat())
            
            # Calculate RAG score
            rag_score = self.calculate_rag_score(content, query, metadata)
            
            # Calculate hybrid score
            hybrid_score = self.calculate_hybrid_score(bm25_score, rag_score)
            
            # Calculate time importance
            time_importance = self.calculate_time_importance(timestamp, current_time)
            
            # Calculate final score
            final_score = self.calculate_final_score(hybrid_score, time_importance)
            
            # Create enhanced result
            enhanced_result = {
                'content': content,
                'bm25_score': bm25_score,
                'rag_score': rag_score,
                'hybrid_score': hybrid_score,
                'time_importance': time_importance,
                'final_score': final_score,
                'metadata': metadata,
                'timestamp': timestamp
            }
            
            # Copy other fields from original result
            for key, value in result.items():
                if key not in enhanced_result:
                    enhanced_result[key] = value
            
            enhanced_results.append(enhanced_result)
        
        # Sort by final score (descending)
        enhanced_results.sort(key=lambda x: x['final_score'], reverse=True)
        
        return enhanced_results[:limit]
    
    def search_with_hybrid_retrieval(self, query: str, bm25_system, limit: int = 10) -> List[Dict]:
        """
        Complete hybrid search using BM25 system and hybrid scoring
        
        Args:
            query: Search query
            bm25_system: BM25 system instance
            limit: Maximum number of results
            
        Returns:
            List of results with hybrid scores
        """
        # Get BM25 results
        bm25_results = bm25_system.search(query, limit=limit*2)  # Get more for better selection
        
        # Apply hybrid scoring
        hybrid_results = self.hybrid_search(query, bm25_results, limit)
        
        return hybrid_results
    
    def enhanced_hybrid_search_with_pairing(self, query: str, bm25_system, limit: int = 10) -> List[Dict]:
        """
        Enhanced hybrid search including pairing engine results
        """
        # Get standard hybrid results
        hybrid_results = self.search_with_hybrid_retrieval(query, bm25_system, limit)
        
        # Try to get pairing engine results
        pairing_results = []
        try:
            from luna_pairing_integration import get_luna_pairing_engine
            pairing_engine = get_luna_pairing_engine()
            if pairing_engine:
                pairing_matches = pairing_engine.find_best_response(query, top_k=limit, min_similarity=0.3)
                for pair_id, similarity, data in pairing_matches:
                    pairing_results.append({
                        'content': data['luna_response'],
                        'bm25_score': 0.0,  # Pairing engine doesn't use BM25
                        'rag_score': similarity,  # Use similarity as RAG score
                        'hybrid_score': similarity,
                        'time_importance': 1.0,
                        'final_score': similarity,
                        'source': 'pairing_engine',
                        'metadata': data['metadata']
                    })
        except Exception as e:
            print(f"⚠️ Pairing engine integration error in hybrid search: {e}")
        
        # Combine results
        all_results = hybrid_results + pairing_results
        
        # Sort by final score and return top results
        all_results.sort(key=lambda x: x['final_score'], reverse=True)
        return all_results[:limit]
    
    def get_retrieval_stats(self) -> Dict[str, Any]:
        """Get statistics about the hybrid retrieval system"""
        return {
            'alpha': self.alpha,
            'rag_weight': self.rag_weight,
            'time_decay_factor': self.time_decay_factor,
            'formula': f"s_hyb(m) = {self.alpha:.2f} ⋅ ŝ_BM25(m) + {self.rag_weight:.2f} ⋅ ŝ_RAG(m)",
            'final_formula': "s_final(m) = s_hyb(m) × imp_t(m)",
            'teachers': {
                'amnesia': {
                    'name': self.teacher_name,
                    'title': 'AI Companion Memory Systems Expert',
                    'contribution': 'Layla AI Memory Architecture and Advanced Retrieval Techniques'
                },
                'teto': {
                    'name': self.bm25_teacher,
                    'title': 'BM25 Indexing and Information Retrieval Expert',
                    'contribution': 'BM25 Ranking Algorithm and Information Retrieval Systems'
                }
            },
            'description': 'Combines keyword matching (BM25) with semantic understanding (RAG) and time-based importance for optimal memory retrieval. Inspired by Layla AI\'s sophisticated memory organization.'
        }

# Global hybrid retrieval system instance
hybrid_retrieval_system = None

def initialize_hybrid_retrieval_system(alpha: float = 0.7, time_decay_factor: float = 0.1) -> HybridRetrievalSystem:
    """Initialize the global hybrid retrieval system"""
    global hybrid_retrieval_system
    hybrid_retrieval_system = HybridRetrievalSystem(alpha, time_decay_factor)
    return hybrid_retrieval_system

def get_hybrid_retrieval_system() -> Optional[HybridRetrievalSystem]:
    """Get the global hybrid retrieval system instance"""
    return hybrid_retrieval_system

def hybrid_search_memories(query: str, bm25_system, limit: int = 10) -> List[Dict]:
    """Search memories using hybrid retrieval"""
    if hybrid_retrieval_system is None:
        initialize_hybrid_retrieval_system()
    
    return hybrid_retrieval_system.search_with_hybrid_retrieval(query, bm25_system, limit)

def enhance_bm25_with_hybrid_retrieval(bm25_results: List[Dict], query: str, limit: int = 10) -> List[Dict]:
    """Enhance BM25 results with hybrid retrieval scoring"""
    if hybrid_retrieval_system is None:
        initialize_hybrid_retrieval_system()
    
    return hybrid_retrieval_system.hybrid_search(query, bm25_results, limit)

if __name__ == "__main__":
    # Test the hybrid retrieval system
    print("🧠 Testing Hybrid Retrieval System")
    print("=" * 50)
    
    # Initialize system
    hybrid_system = initialize_hybrid_retrieval_system(alpha=0.7, time_decay_factor=0.1)
    
    # Test scoring functions
    print("\n🧪 Testing scoring functions...")
    
    # Test time importance
    current_time = datetime.now()
    recent_time = (current_time - timedelta(days=1)).isoformat()
    old_time = (current_time - timedelta(days=30)).isoformat()
    
    recent_importance = hybrid_system.calculate_time_importance(recent_time, current_time)
    old_importance = hybrid_system.calculate_time_importance(old_time, current_time)
    
    print(f"Recent memory importance: {recent_importance:.3f}")
    print(f"Old memory importance: {old_importance:.3f}")
    
    # Test RAG scoring
    test_content = "Chris loves gaming, especially RPGs and strategy games. He spends hours playing them."
    test_query = "gaming preferences"
    
    rag_score = hybrid_system.calculate_rag_score(test_content, test_query, {'importance': 4})
    print(f"RAG score: {rag_score:.3f}")
    
    # Test hybrid scoring
    bm25_score = 5.5
    hybrid_score = hybrid_system.calculate_hybrid_score(bm25_score, rag_score)
    final_score = hybrid_system.calculate_final_score(hybrid_score, recent_importance)
    
    print(f"BM25 score: {bm25_score:.3f}")
    print(f"Hybrid score: {hybrid_score:.3f}")
    print(f"Final score: {final_score:.3f}")
    
    # Show stats
    stats = hybrid_system.get_retrieval_stats()
    print(f"\n📊 Hybrid Retrieval Statistics:")
    print(f"  Alpha (BM25 weight): {stats['alpha']:.2f}")
    print(f"  RAG weight: {stats['rag_weight']:.2f}")
    print(f"  Time decay factor: {stats['time_decay_factor']:.2f}")
    print(f"  Formula: {stats['formula']}")
    print(f"  Final formula: {stats['final_formula']}")
    
    print("\n✅ Hybrid retrieval system test completed!")
