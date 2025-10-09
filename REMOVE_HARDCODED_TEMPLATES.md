# 🔧 Remove Hardcoded Self-Talk Templates

## Problem
Luna still has hardcoded self-talk templates in multiple duplicate functions.

## Solution
Delete these entire function definitions (they're duplicates):

### 1. Delete lines ~8025-8145 (first duplicate generate_dynamic_thought)
Search for:
```python
    def generate_dynamic_thought():
        """Generate a simple thought when the main generation fails - context-aware fallback"""
```
Starting around line 8025

**Delete entire function** until you reach the next function definition

### 2. Delete lines ~8528-8648 (second duplicate generate_dynamic_thought)  
Search for the SECOND occurrence of:
```python
    def generate_dynamic_thought():
```
Starting around line 8528

**Delete entire function** until you reach the next function definition

## Keep Only
The FIRST `generate_dynamic_thought()` around line 6867 which uses Ollama generation properly.

## Quick Fix
1. Open main.py
2. Search for "def generate_dynamic_thought"
3. Keep ONLY the first one (around line 6867)
4. Delete the second one (around line 8025)
5. Delete the third one (around line 8528)
6. Save and restart Luna

## Or Run This Command
```python
# In Python console or new script:
import re

with open('main.py', 'r') as f:
    lines = f.readlines()

# Find all occurrences of generate_dynamic_thought
occurrences = []
for i, line in enumerate(lines):
    if 'def generate_dynamic_thought():' in line and line.strip().startswith('def'):
        occurrences.append(i)

print(f"Found {len(occurrences)} occurrences at lines: {occurrences}")
# Keep first, delete others
```

