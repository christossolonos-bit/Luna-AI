"""
Clean duplicate memory strands that cause Luna to repeat phrases.
Run: python scripts/clean_duplicate_memories.py

Also consider: python scripts/filter_learning_data.py rewrite
to reduce "Oh? X checking in..." pattern in luna_learning_data.jsonl.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from luna_dna_memory import initialize_dna_memory, clean_duplicate_memories

if __name__ == "__main__":
    initialize_dna_memory()
    result = clean_duplicate_memories()
    print(f"Removed {result['deleted']} duplicate strands, kept {result['kept']} unique memories.")
