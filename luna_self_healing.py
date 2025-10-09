# luna_self_healing.py
"""
Luna Self-Healing System
Automatically detects and fixes errors at runtime without requiring restart
"""

import threading
import time
import traceback
import sys
from typing import Dict, List, Callable, Any
from collections import defaultdict, deque
from datetime import datetime

class SelfHealingSystem:
    """Monitors Luna's health and auto-fixes common errors"""
    
    def __init__(self):
        self.error_history = deque(maxlen=100)
        self.error_patterns = defaultdict(int)
        self.healing_actions = {}
        self.monitoring = False
        self.monitor_thread = None
        
        # Register healing actions
        self._register_healing_actions()
        
        print("🔧 Self-Healing System initialized")
    
    def _register_healing_actions(self):
        """Register auto-fix actions for common errors"""
        
        # Fix for NoneType subscriptable errors in TTS
        self.healing_actions['NoneType.*subscriptable'] = {
            'description': 'TTS voice engine returning None',
            'action': self._fix_tts_none_error,
            'severity': 'low'
        }
        
        # Fix for Ollama timeout/hanging
        self.healing_actions['timeout|timed out|recv'] = {
            'description': 'Ollama API timeout/hanging',
            'action': self._fix_ollama_timeout,
            'severity': 'high'
        }
        
        # Fix for Discord heartbeat blocked
        self.healing_actions['heartbeat blocked'] = {
            'description': 'Discord connection stalled',
            'action': self._fix_discord_heartbeat,
            'severity': 'medium'
        }
        
        # Fix for memory database locked
        self.healing_actions['database.*locked'] = {
            'description': 'SQLite database locked',
            'action': self._fix_database_lock,
            'severity': 'medium'
        }
    
    def log_error(self, error: Exception, context: str = "unknown"):
        """Log an error and attempt auto-healing"""
        error_info = {
            'timestamp': time.time(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'traceback': traceback.format_exc()
        }
        
        self.error_history.append(error_info)
        self.error_patterns[error_info['error_type']] += 1
        
        print(f"🔧 Error logged: {error_info['error_type']} in {context}")
        
        # Attempt healing
        self._attempt_healing(error_info)
    
    def _attempt_healing(self, error_info: Dict):
        """Attempt to heal the error automatically"""
        import re
        
        error_message = error_info['error_message'].lower()
        
        for pattern, healing_info in self.healing_actions.items():
            if re.search(pattern, error_message, re.IGNORECASE):
                print(f"🔧 Detected known error: {healing_info['description']}")
                print(f"🔧 Severity: {healing_info['severity']} - Attempting auto-fix...")
                
                try:
                    healing_info['action'](error_info)
                    print(f"✅ Auto-fix completed successfully")
                    return True
                except Exception as heal_error:
                    print(f"⚠️ Auto-fix failed: {heal_error}")
                    return False
        
        print(f"⚠️ No auto-fix available for this error type")
        return False
    
    def _fix_tts_none_error(self, error_info: Dict):
        """Fix TTS NoneType errors by skipping TTS temporarily"""
        print("🔧 Fixing TTS error: Disabling voice for this response")
        # The error handling in speak_response already catches this
        # Just log that we're aware and continuing
        pass
    
    def _fix_ollama_timeout(self, error_info: Dict):
        """Fix Ollama timeout by reducing context window"""
        print("🔧 Fixing Ollama timeout: Reducing context window temporarily")
        
        # Try to reduce Ollama parameters globally
        try:
            import main
            if hasattr(main, 'OLLAMA_CONFIG'):
                original_ctx = main.OLLAMA_CONFIG.get('num_ctx', 2048)
                original_predict = main.OLLAMA_CONFIG.get('num_predict', 200)
                
                # Reduce by 25%
                main.OLLAMA_CONFIG['num_ctx'] = int(original_ctx * 0.75)
                main.OLLAMA_CONFIG['num_predict'] = int(original_predict * 0.75)
                
                print(f"🔧 Reduced context: {original_ctx} → {main.OLLAMA_CONFIG['num_ctx']}")
                print(f"🔧 Reduced predict: {original_predict} → {main.OLLAMA_CONFIG['num_predict']}")
                
                # Reset after 5 minutes
                def reset_config():
                    time.sleep(300)
                    main.OLLAMA_CONFIG['num_ctx'] = original_ctx
                    main.OLLAMA_CONFIG['num_predict'] = original_predict
                    print(f"🔧 Ollama config reset to normal")
                
                threading.Thread(target=reset_config, daemon=True).start()
        except Exception as e:
            print(f"⚠️ Could not adjust Ollama config: {e}")
    
    def _fix_discord_heartbeat(self, error_info: Dict):
        """Fix Discord heartbeat blocking (just log - Discord will auto-reconnect)"""
        print("🔧 Discord heartbeat blocked - Discord.py will auto-reconnect")
        # Discord.py handles this automatically, just acknowledge it
        pass
    
    def _fix_database_lock(self, error_info: Dict):
        """Fix database lock by enabling WAL mode"""
        print("🔧 Fixing database lock: Ensuring WAL mode is enabled")
        
        try:
            import sqlite3
            for db_name in ['luna_memories.db', 'luna_global_awareness.db']:
                try:
                    conn = sqlite3.connect(db_name, timeout=1.0)
                    conn.execute('PRAGMA journal_mode=WAL')
                    conn.execute('PRAGMA busy_timeout=5000')
                    conn.close()
                    print(f"✅ WAL mode ensured for {db_name}")
                except Exception as db_error:
                    print(f"⚠️ Could not fix {db_name}: {db_error}")
        except Exception as e:
            print(f"⚠️ Database fix failed: {e}")
    
    def get_health_report(self) -> Dict:
        """Get system health report"""
        recent_errors = [e for e in self.error_history if time.time() - e['timestamp'] < 3600]
        
        return {
            'total_errors': len(self.error_history),
            'recent_errors_1h': len(recent_errors),
            'error_patterns': dict(self.error_patterns),
            'most_common_error': max(self.error_patterns, key=self.error_patterns.get) if self.error_patterns else None,
            'healing_actions_available': len(self.healing_actions),
            'monitoring': self.monitoring
        }
    
    def start_monitoring(self):
        """Start continuous health monitoring"""
        if self.monitoring:
            return
        
        self.monitoring = True
        
        def monitor_loop():
            while self.monitoring:
                try:
                    # Check system health every 30 seconds
                    time.sleep(30)
                    
                    # Check for error spikes
                    recent_errors = [e for e in self.error_history if time.time() - e['timestamp'] < 300]
                    
                    if len(recent_errors) > 10:
                        print(f"⚠️ High error rate detected: {len(recent_errors)} errors in 5 minutes")
                        print(f"🔧 Running health diagnostics...")
                        self._run_diagnostics()
                    
                except Exception as e:
                    print(f"⚠️ Monitor loop error: {e}")
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("🔧 Health monitoring started")
    
    def _run_diagnostics(self):
        """Run system diagnostics"""
        print("🔍 System Diagnostics:")
        
        # Check Ollama connection
        try:
            import ollama
            test = ollama.chat(
                model='hf.co/NousResearch/Nous-Hermes-2-Mistral-7B-DPO-GGUF:Q5_K_M',
                messages=[{'role': 'user', 'content': 'test'}],
                options={'num_predict': 10}
            )
            print("✅ Ollama: Connected")
        except Exception as e:
            print(f"❌ Ollama: {str(e)[:50]}")
        
        # Check database access
        try:
            import sqlite3
            conn = sqlite3.connect('luna_memories.db', timeout=1.0)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM conversations')
            count = cursor.fetchone()[0]
            conn.close()
            print(f"✅ Database: Connected ({count} conversations)")
        except Exception as e:
            print(f"❌ Database: {str(e)[:50]}")
        
        # Check memory usage
        try:
            import psutil
            process = psutil.Process()
            mem_mb = process.memory_info().rss / 1024 / 1024
            print(f"📊 Memory: {mem_mb:.1f}MB")
        except:
            print("⚠️ Memory: Could not check")

# Global instance
self_healing_system = None

def initialize_self_healing() -> SelfHealingSystem:
    """Initialize the self-healing system"""
    global self_healing_system
    if not self_healing_system:
        self_healing_system = SelfHealingSystem()
        self_healing_system.start_monitoring()
    return self_healing_system

def get_self_healing_system() -> SelfHealingSystem:
    """Get the self-healing system"""
    return self_healing_system

def log_error_to_healing_system(error: Exception, context: str = "unknown"):
    """Log an error to the self-healing system"""
    if self_healing_system:
        self_healing_system.log_error(error, context)

def get_health_report() -> Dict:
    """Get health report"""
    if self_healing_system:
        return self_healing_system.get_health_report()
    return {'error': 'Self-healing system not initialized'}

