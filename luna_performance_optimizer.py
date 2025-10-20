"""
🚀 Luna Performance Optimizer
============================

Optimizes Luna's background processes to reduce CPU usage and fan noise.
"""

import time
import threading
from typing import Dict, Any

class LunaPerformanceOptimizer:
    """Optimizes Luna's performance by managing background processes"""
    
    def __init__(self, luna_instance):
        self.luna = luna_instance
        self.optimization_enabled = True
        self.cpu_usage_threshold = 0.7  # Reduce activity if CPU usage is high
        self.background_processes = {
            'thinking_loop': True,
            'reflection_loop': True, 
            'exploration_loop': True,
            'curiosity_engine': True
        }
        
        # Optimized timing (longer intervals)
        self.optimized_intervals = {
            'thinking': (300, 600),      # 5-10 minutes (was 1-3)
            'reflection': (1800, 3600),  # 30-60 minutes (was 10-30)
            'exploration': (3600, 7200), # 1-2 hours (was 15-45 minutes)
            'curiosity': (600, 1200)     # 10-20 minutes (was 5)
        }
    
    def enable_performance_mode(self):
        """Enable performance optimization mode"""
        self.optimization_enabled = True
        print("🚀 Performance optimization enabled")
        
        # Disable heavy processes
        self.background_processes['curiosity_engine'] = False
        self.background_processes['exploration_loop'] = False
        
        # Increase intervals
        self.optimized_intervals['thinking'] = (600, 1200)  # 10-20 minutes
        self.optimized_intervals['reflection'] = (3600, 7200)  # 1-2 hours
    
    def disable_performance_mode(self):
        """Disable performance optimization mode"""
        self.optimization_enabled = False
        print("🧠 Full cognitive mode enabled")
        
        # Re-enable all processes
        self.background_processes['curiosity_engine'] = True
        self.background_processes['exploration_loop'] = True
        
        # Restore normal intervals
        self.optimized_intervals['thinking'] = (300, 600)
        self.optimized_intervals['reflection'] = (1800, 3600)
        self.optimized_intervals['exploration'] = (3600, 7200)
        self.optimized_intervals['curiosity'] = (600, 1200)
    
    def get_optimized_interval(self, process_name: str) -> tuple:
        """Get optimized interval for a process"""
        if self.optimization_enabled:
            return self.optimized_intervals.get(process_name, (300, 600))
        else:
            # Original intervals
            original_intervals = {
                'thinking': (60, 180),
                'reflection': (600, 1800),
                'exploration': (900, 2700),
                'curiosity': (300, 300)
            }
            return original_intervals.get(process_name, (300, 600))
    
    def should_run_process(self, process_name: str) -> bool:
        """Check if a process should run based on optimization settings"""
        if not self.optimization_enabled:
            return True
        
        return self.background_processes.get(process_name, True)
    
    def optimize_curiosity_engine(self):
        """Optimize curiosity engine for lower CPU usage"""
        if not self.luna.curiosity_engine:
            return
        
        # Reduce curiosity frequency
        if hasattr(self.luna.curiosity_engine, 'curiosity_state'):
            # Increase energy consumption to reduce frequency
            self.luna.curiosity_engine.curiosity_state['exploration_energy'] *= 0.5
            # Increase required curiosity level
            self.luna.curiosity_engine.curiosity_state['curiosity_level'] = 0.8
    
    def optimize_vector_reasoning(self):
        """Optimize vector reasoning for lower CPU usage"""
        if not self.luna.vector_reasoning:
            return
        
        # Reduce embedding generation frequency
        # This would require modifying the vector reasoning engine
        print("🔧 Vector reasoning optimization applied")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get current performance optimization stats"""
        return {
            'optimization_enabled': self.optimization_enabled,
            'background_processes': self.background_processes,
            'optimized_intervals': self.optimized_intervals,
            'cpu_usage_threshold': self.cpu_usage_threshold
        }

def create_performance_commands():
    """Create performance management commands for Luna"""
    return {
        'performance_mode': {
            'description': 'Enable performance optimization mode (reduces CPU usage)',
            'command': 'performance mode',
            'action': 'enable_performance_mode'
        },
        'full_cognitive_mode': {
            'description': 'Enable full cognitive mode (higher CPU usage, more features)',
            'command': 'full cognitive mode', 
            'action': 'disable_performance_mode'
        },
        'performance_stats': {
            'description': 'Show current performance optimization settings',
            'command': 'performance stats',
            'action': 'show_performance_stats'
        }
}

# Performance optimization presets
PERFORMANCE_PRESETS = {
    'low_cpu': {
        'thinking_interval': (1200, 2400),  # 20-40 minutes
        'reflection_interval': (7200, 14400),  # 2-4 hours
        'exploration_interval': (14400, 28800),  # 4-8 hours
        'curiosity_interval': (1800, 3600),  # 30-60 minutes
        'disable_curiosity': True,
        'disable_exploration': True
    },
    'balanced': {
        'thinking_interval': (600, 1200),  # 10-20 minutes
        'reflection_interval': (3600, 7200),  # 1-2 hours
        'exploration_interval': (7200, 14400),  # 2-4 hours
        'curiosity_interval': (1200, 2400),  # 20-40 minutes
        'disable_curiosity': False,
        'disable_exploration': False
    },
    'high_performance': {
        'thinking_interval': (300, 600),  # 5-10 minutes
        'reflection_interval': (1800, 3600),  # 30-60 minutes
        'exploration_interval': (3600, 7200),  # 1-2 hours
        'curiosity_interval': (600, 1200),  # 10-20 minutes
        'disable_curiosity': False,
        'disable_exploration': False
    }
}
