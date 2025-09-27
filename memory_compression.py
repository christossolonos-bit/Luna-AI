#!/usr/bin/env python3
# memory_compression.py
# Memory Compression System for Luna AI
# Compresses conversation and emotion memories while maintaining full access

import sqlite3
import gzip
import json
import os
import shutil
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import pickle
import zlib
from pathlib import Path

class MemoryCompressor:
    """Advanced memory compression system for Luna's conversations and emotions"""
    
    def __init__(self, compression_level: int = 9):
        self.compression_level = compression_level
        self.db_path = "luna_memories.db"
        self.compressed_dir = "compressed_memories"
        self.cache_dir = "memory_cache"
        self.lock = threading.Lock()
        
        # Create directories
        os.makedirs(self.compressed_dir, exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Compression statistics
        self.stats = {
            'total_compressed': 0,
            'total_original_size': 0,
            'compression_ratio': 0.0,
            'last_compression': None
        }
        
        print("🗜️ Memory compression system initialized")
    
    def compress_memories(self, force: bool = False) -> Dict[str, Any]:
        """Compress all memories into efficient archives"""
        with self.lock:
            try:
                print("🗜️ Starting memory compression...")
                
                # Check if compression is needed
                if not force and self._should_skip_compression():
                    print("🗜️ Compression not needed - data is recent")
                    return self.stats
                
                # Connect to database
                conn = sqlite3.connect(self.db_path, timeout=60.0)
                conn.execute('PRAGMA journal_mode=WAL')
                
                # Get all memories
                memories = self._extract_all_memories(conn)
                conversations = self._extract_all_conversations(conn)
                
                conn.close()
                
                # Compress memories by type
                compressed_data = {
                    'memories': self._compress_by_type(memories, 'memories'),
                    'conversations': self._compress_by_type(conversations, 'conversations'),
                    'metadata': self._create_metadata(memories, conversations)
                }
                
                # Save compressed archives
                self._save_compressed_archives(compressed_data)
                
                # Update statistics
                self._update_compression_stats(compressed_data)
                
                # Create access cache
                self._create_access_cache(compressed_data)
                
                print(f"✅ Memory compression complete! Saved {self.stats['total_compressed']} bytes")
                return self.stats
                
            except Exception as e:
                print(f"❌ Memory compression failed: {e}")
                return {'error': str(e)}
    
    def _extract_all_memories(self, conn: sqlite3.connect) -> List[Dict]:
        """Extract all memories from database"""
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, timestamp, memory_type, content, mood, importance
            FROM memories
            ORDER BY timestamp DESC
        ''')
        
        memories = []
        for row in cursor.fetchall():
            memories.append({
                'id': row[0],
                'timestamp': row[1],
                'memory_type': row[2],
                'content': row[3],
                'mood': row[4],
                'importance': row[5]
            })
        
        return memories
    
    def _extract_all_conversations(self, conn: sqlite3.connect) -> List[Dict]:
        """Extract all conversations from database"""
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, timestamp, user_message, luna_response, mood, voice_used
            FROM conversations
            ORDER BY timestamp DESC
        ''')
        
        conversations = []
        for row in cursor.fetchall():
            conversations.append({
                'id': row[0],
                'timestamp': row[1],
                'user_message': row[2],
                'luna_response': row[3],
                'mood': row[4],
                'voice_used': row[5]
            })
        
        return conversations
    
    def _compress_by_type(self, data: List[Dict], data_type: str) -> Dict[str, Any]:
        """Compress data by type with intelligent grouping"""
        if not data:
            return {'compressed': b'', 'groups': {}}
        
        # Group by time periods (monthly chunks)
        groups = self._group_by_time_period(data)
        
        compressed_groups = {}
        for period, group_data in groups.items():
            # Serialize to JSON
            json_data = json.dumps(group_data, ensure_ascii=False, separators=(',', ':'))
            
            # Compress with gzip
            compressed = gzip.compress(json_data.encode('utf-8'), compresslevel=self.compression_level)
            
            compressed_groups[period] = {
                'compressed': compressed,
                'original_size': len(json_data),
                'compressed_size': len(compressed),
                'count': len(group_data)
            }
        
        return {
            'groups': compressed_groups,
            'total_original': sum(g['original_size'] for g in compressed_groups.values()),
            'total_compressed': sum(g['compressed_size'] for g in compressed_groups.values()),
            'total_count': len(data)
        }
    
    def _group_by_time_period(self, data: List[Dict]) -> Dict[str, List[Dict]]:
        """Group data by monthly periods for efficient compression"""
        groups = {}
        
        for item in data:
            try:
                # Parse timestamp
                if isinstance(item['timestamp'], str):
                    dt = datetime.fromisoformat(item['timestamp'].replace('Z', '+00:00'))
                else:
                    dt = datetime.fromtimestamp(item['timestamp'])
                
                # Group by year-month
                period = dt.strftime('%Y-%m')
                
                if period not in groups:
                    groups[period] = []
                
                groups[period].append(item)
                
            except Exception as e:
                # Fallback to current month for invalid timestamps
                period = datetime.now().strftime('%Y-%m')
                if period not in groups:
                    groups[period] = []
                groups[period].append(item)
        
        return groups
    
    def _create_metadata(self, memories: List[Dict], conversations: List[Dict]) -> Dict:
        """Create metadata for quick access"""
        metadata = {
            'compression_info': {
                'compression_level': self.compression_level,
                'compressed_at': datetime.now().isoformat(),
                'algorithm': 'gzip'
            },
            'statistics': {
                'total_memories': len(memories),
                'total_conversations': len(conversations),
                'memory_types': {},
                'mood_distribution': {},
                'time_range': {}
            },
            'indexes': {
                'memory_types': {},
                'moods': {},
                'importance_levels': {},
                'time_periods': {}
            }
        }
        
        # Analyze memories
        for memory in memories:
            # Memory types
            mem_type = memory.get('memory_type', 'unknown')
            metadata['statistics']['memory_types'][mem_type] = metadata['statistics']['memory_types'].get(mem_type, 0) + 1
            
            # Moods
            mood = memory.get('mood', 'neutral')
            metadata['statistics']['mood_distribution'][mood] = metadata['statistics']['mood_distribution'].get(mood, 0) + 1
        
        return metadata
    
    def _save_compressed_archives(self, compressed_data: Dict):
        """Save compressed archives to disk"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save memories archive
        memories_path = os.path.join(self.compressed_dir, f'memories_{timestamp}.gz')
        with gzip.open(memories_path, 'wb', compresslevel=self.compression_level) as f:
            pickle.dump(compressed_data['memories'], f)
        
        # Save conversations archive
        conversations_path = os.path.join(self.compressed_dir, f'conversations_{timestamp}.gz')
        with gzip.open(conversations_path, 'wb', compresslevel=self.compression_level) as f:
            pickle.dump(compressed_data['conversations'], f)
        
        # Save metadata
        metadata_path = os.path.join(self.compressed_dir, f'metadata_{timestamp}.json')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(compressed_data['metadata'], f, indent=2, ensure_ascii=False)
        
        # Create latest symlinks
        self._create_latest_links(timestamp)
        
        print(f"💾 Saved compressed archives: {memories_path}, {conversations_path}")
    
    def _create_latest_links(self, timestamp: str):
        """Create latest file references for easy access (symlinks on Unix, copies on Windows)"""
        try:
            # Create latest file references for easy access
            latest_memories = os.path.join(self.compressed_dir, 'memories_latest.gz')
            latest_conversations = os.path.join(self.compressed_dir, 'conversations_latest.gz')
            latest_metadata = os.path.join(self.compressed_dir, 'metadata_latest.json')
            
            # Source files
            source_memories = os.path.join(self.compressed_dir, f'memories_{timestamp}.gz')
            source_conversations = os.path.join(self.compressed_dir, f'conversations_{timestamp}.gz')
            source_metadata = os.path.join(self.compressed_dir, f'metadata_{timestamp}.json')
            
            # Remove old files
            for file_path in [latest_memories, latest_conversations, latest_metadata]:
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            # Create references (symlinks on Unix, copies on Windows)
            if os.name == 'nt':  # Windows
                # Use file copies instead of symlinks on Windows
                shutil.copy2(source_memories, latest_memories)
                shutil.copy2(source_conversations, latest_conversations)
                shutil.copy2(source_metadata, latest_metadata)
                print("📁 Created latest file copies (Windows)")
            else:  # Unix-like systems
                # Use symlinks on Unix systems
                os.symlink(f'memories_{timestamp}.gz', latest_memories)
                os.symlink(f'conversations_{timestamp}.gz', latest_conversations)
                os.symlink(f'metadata_{timestamp}.json', latest_metadata)
                print("🔗 Created latest symlinks (Unix)")
            
        except Exception as e:
            print(f"⚠️ Could not create latest file references: {e}")
    
    def _create_access_cache(self, compressed_data: Dict):
        """Create fast access cache for frequently accessed data"""
        cache_data = {
            'recent_memories': self._extract_recent_data(compressed_data['memories'], days=7),
            'recent_conversations': self._extract_recent_data(compressed_data['conversations'], days=7),
            'important_memories': self._extract_important_memories(compressed_data['memories']),
            'mood_index': self._create_mood_index(compressed_data)
        }
        
        cache_path = os.path.join(self.cache_dir, 'access_cache.pkl')
        with open(cache_path, 'wb') as f:
            pickle.dump(cache_data, f)
        
        print(f"⚡ Created access cache: {cache_path}")
    
    def _extract_recent_data(self, compressed_data: Dict, days: int) -> List[Dict]:
        """Extract recent data for fast access"""
        recent_data = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for period, group_info in compressed_data['groups'].items():
            try:
                period_date = datetime.strptime(period, '%Y-%m')
                if period_date >= cutoff_date:
                    # Decompress this group
                    decompressed = gzip.decompress(group_info['compressed'])
                    group_data = json.loads(decompressed.decode('utf-8'))
                    
                    # Filter for recent items
                    for item in group_data:
                        try:
                            item_date = datetime.fromisoformat(item['timestamp'].replace('Z', '+00:00'))
                            if item_date >= cutoff_date:
                                recent_data.append(item)
                        except:
                            recent_data.append(item)  # Include if date parsing fails
            except:
                continue
        
        return recent_data
    
    def _extract_important_memories(self, compressed_data: Dict) -> List[Dict]:
        """Extract high-importance memories for fast access"""
        important_memories = []
        
        for period, group_info in compressed_data['groups'].items():
            try:
                # Decompress this group
                decompressed = gzip.decompress(group_info['compressed'])
                group_data = json.loads(decompressed.decode('utf-8'))
                
                # Filter for important memories
                for item in group_data:
                    if item.get('importance', 1) >= 3:  # High importance threshold
                        important_memories.append(item)
            except:
                continue
        
        return important_memories
    
    def _create_mood_index(self, compressed_data: Dict) -> Dict[str, List[str]]:
        """Create mood-based index for quick retrieval"""
        mood_index = {}
        
        for period, group_info in compressed_data['memories']['groups'].items():
            try:
                # Decompress this group
                decompressed = gzip.decompress(group_info['compressed'])
                group_data = json.loads(decompressed.decode('utf-8'))
                
                # Index by mood
                for item in group_data:
                    mood = item.get('mood', 'neutral')
                    if mood not in mood_index:
                        mood_index[mood] = []
                    mood_index[mood].append(item['id'])
            except:
                continue
        
        return mood_index
    
    def _update_compression_stats(self, compressed_data: Dict):
        """Update compression statistics"""
        total_original = (compressed_data['memories']['total_original'] + 
                         compressed_data['conversations']['total_original'])
        total_compressed = (compressed_data['memories']['total_compressed'] + 
                           compressed_data['conversations']['total_compressed'])
        
        self.stats.update({
            'total_compressed': total_compressed,
            'total_original_size': total_original,
            'compression_ratio': (1 - (total_compressed / total_original)) * 100 if total_original > 0 else 0,
            'last_compression': datetime.now().isoformat()
        })
    
    def _should_skip_compression(self) -> bool:
        """Check if compression should be skipped"""
        # Skip if last compression was recent (within 1 hour)
        if self.stats['last_compression']:
            try:
                last_compression = datetime.fromisoformat(self.stats['last_compression'])
                if datetime.now() - last_compression < timedelta(hours=1):
                    return True
            except:
                pass
        
        return False
    
    def get_compressed_stats(self) -> Dict[str, Any]:
        """Get compression statistics"""
        return self.stats.copy()
    
    def decompress_memories(self, period: str = None) -> List[Dict]:
        """Decompress memories for a specific period or all"""
        try:
            latest_path = os.path.join(self.compressed_dir, 'memories_latest.gz')
            if not os.path.exists(latest_path):
                print("❌ No compressed memories found")
                return []
            
            with gzip.open(latest_path, 'rb') as f:
                compressed_data = pickle.load(f)
            
            if period:
                # Return specific period
                if period in compressed_data['groups']:
                    decompressed = gzip.decompress(compressed_data['groups'][period]['compressed'])
                    return json.loads(decompressed.decode('utf-8'))
                else:
                    return []
            else:
                # Return all memories
                all_memories = []
                for group_info in compressed_data['groups'].values():
                    decompressed = gzip.decompress(group_info['compressed'])
                    group_data = json.loads(decompressed.decode('utf-8'))
                    all_memories.extend(group_data)
                return all_memories
                
        except Exception as e:
            print(f"❌ Failed to decompress memories: {e}")
            return []
    
    def decompress_conversations(self, period: str = None) -> List[Dict]:
        """Decompress conversations for a specific period or all"""
        try:
            latest_path = os.path.join(self.compressed_dir, 'conversations_latest.gz')
            if not os.path.exists(latest_path):
                print("❌ No compressed conversations found")
                return []
            
            with gzip.open(latest_path, 'rb') as f:
                compressed_data = pickle.load(f)
            
            if period:
                # Return specific period
                if period in compressed_data['groups']:
                    decompressed = gzip.decompress(compressed_data['groups'][period]['compressed'])
                    return json.loads(decompressed.decode('utf-8'))
                else:
                    return []
            else:
                # Return all conversations
                all_conversations = []
                for group_info in compressed_data['groups'].values():
                    decompressed = gzip.decompress(group_info['compressed'])
                    group_data = json.loads(decompressed.decode('utf-8'))
                    all_conversations.extend(group_data)
                return all_conversations
                
        except Exception as e:
            print(f"❌ Failed to decompress conversations: {e}")
            return []
    
    def get_recent_from_cache(self, days: int = 7) -> Dict[str, List[Dict]]:
        """Get recent data from cache for fast access"""
        try:
            cache_path = os.path.join(self.cache_dir, 'access_cache.pkl')
            if not os.path.exists(cache_path):
                return {'memories': [], 'conversations': []}
            
            with open(cache_path, 'rb') as f:
                cache_data = pickle.load(f)
            
            return {
                'memories': cache_data.get('recent_memories', []),
                'conversations': cache_data.get('recent_conversations', [])
            }
            
        except Exception as e:
            print(f"❌ Failed to load cache: {e}")
            return {'memories': [], 'conversations': []}
    
    def cleanup_old_archives(self, keep_days: int = 30):
        """Clean up old compressed archives"""
        try:
            cutoff_date = datetime.now() - timedelta(days=keep_days)
            cleaned_count = 0
            
            for filename in os.listdir(self.compressed_dir):
                if filename.endswith('.gz') or filename.endswith('.json'):
                    file_path = os.path.join(self.compressed_dir, filename)
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    if file_time < cutoff_date:
                        os.remove(file_path)
                        cleaned_count += 1
            
            print(f"🧹 Cleaned up {cleaned_count} old archive files")
            
        except Exception as e:
            print(f"❌ Failed to cleanup archives: {e}")

# Global compressor instance
memory_compressor = MemoryCompressor()

def compress_luna_memories(force: bool = False) -> Dict[str, Any]:
    """Compress Luna's memories - main interface function"""
    return memory_compressor.compress_memories(force=force)

def get_compression_stats() -> Dict[str, Any]:
    """Get compression statistics"""
    return memory_compressor.get_compressed_stats()

def get_recent_memories(days: int = 7) -> Dict[str, List[Dict]]:
    """Get recent memories from cache"""
    return memory_compressor.get_recent_from_cache(days)

def decompress_all_memories() -> Tuple[List[Dict], List[Dict]]:
    """Decompress all memories and conversations"""
    memories = memory_compressor.decompress_memories()
    conversations = memory_compressor.decompress_conversations()
    return memories, conversations

if __name__ == "__main__":
    # Test compression
    print("🗜️ Testing memory compression system...")
    stats = compress_luna_memories(force=True)
    print(f"📊 Compression stats: {stats}")
    
    # Test decompression
    memories, conversations = decompress_all_memories()
    print(f"📖 Decompressed {len(memories)} memories and {len(conversations)} conversations")
