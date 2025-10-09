"""
Script to remove all hardcoded thought templates from main.py
Run this to clean up pre-written self-talk messages
"""

import re

# Read main.py
with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern to find large template arrays
patterns_to_remove = [
    # Find context_thoughts arrays
    (r'context_thoughts = \[[^\]]*?"Tch\.\.\. I was just thinking[^\]]+\]', 
     'context_thoughts = []  # Templates removed - using Ollama generation'),
    
    # Find general_thoughts arrays  
    (r'general_thoughts = \[[^\]]*?"Tch\.\.\. I\'ve been thinking about our conversations[^\]]+\]',
     'general_thoughts = []  # Templates removed - using Ollama generation'),
    
    # Find simple template selections
    (r'selected_thought = random\.choice\(context_thoughts\)',
     '# Skip - generate via Ollama instead\n        return None'),
    
    (r'selected_thought = random\.choice\(general_thoughts\)',
     '# Skip - generate via Ollama instead\n        return None'),
]

# Apply replacements
modified = content
for pattern, replacement in patterns_to_remove:
    modified = re.sub(pattern, replacement, modified, flags=re.DOTALL)

# Write back
with open('main.py', 'w', encoding='utf-8') as f:
    f.write(modified)

print("✅ Removed hardcoded thought templates from main.py")
print("🔄 Please restart Luna for changes to take effect")

