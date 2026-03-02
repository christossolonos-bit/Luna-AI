"""
Filter luna_learning_data.jsonl to reduce "Oh? [user] checking in..." pattern.
Removes or rewrites entries that reinforce repetitive openings.
Run: python scripts/filter_learning_data.py
"""
from __future__ import annotations

import json
import os
import re
import shutil
from pathlib import Path

LEARNING_FILE = Path(__file__).resolve().parent.parent / "luna_learning_data.jsonl"
BACKUP_SUFFIX = ".backup_before_filter"

# Patterns that indicate the repetitive "checking in" opening
REPETITIVE_PATTERNS = [
    re.compile(r'^Ohh?\??\s+\S+\s+checking\s+(in|up)\s+on\s+me', re.I),
    re.compile(r'^Ohh?\??\s+\{[^}]+\}\s+checking\s+(in|up)', re.I),
    re.compile(r'^Oh\?\s+\S+\s+checking\s+in\s+on\s+me', re.I),
    re.compile(r'^Ohhh\?\s+\S+\s+checking\s+up\s+on\s+me', re.I),
    re.compile(r'^Oh\?\s+\S+\s+checking\s+in\s+on\s+me\s+while', re.I),
]


def _is_repetitive_output(output: str) -> bool:
    """True if output starts with the repetitive 'checking in' pattern."""
    if not output or len(output) < 10:
        return False
    first_100 = output[:100].strip()
    return any(p.search(first_100) for p in REPETITIVE_PATTERNS)


def _rewrite_opening(output: str) -> str:
    """Replace repetitive opening with a varied alternative."""
    for p in REPETITIVE_PATTERNS:
        m = p.search(output)
        if m:
            # Find end of the repetitive phrase (up to "Cute~" or first sentence)
            rest = output[m.end():].lstrip()
            # Skip "Cute~" or "Cute." if present
            if rest.lower().startswith("cute~") or rest.lower().startswith("cute."):
                rest = rest[5:].lstrip()
            elif rest.lower().startswith("cute"):
                rest = rest[4:].lstrip()
            # Use varied openings
            openings = ["Hey—", "Hmm—", "So—", "Well—", "Anyway—"]
            import random
            new_open = random.choice(openings)
            return f"{new_open} {rest}"
    return output


def filter_learning_data(mode: str = "rewrite") -> dict:
    """
    Filter learning data. mode: "remove" (drop lines) or "rewrite" (replace opening).
    Returns {kept, removed, rewritten, total}.
    """
    if not LEARNING_FILE.exists():
        print(f"Error: {LEARNING_FILE} not found")
        return {"kept": 0, "removed": 0, "rewritten": 0, "total": 0}

    # Backup
    backup_path = LEARNING_FILE.with_suffix(LEARNING_FILE.suffix + BACKUP_SUFFIX)
    shutil.copy2(LEARNING_FILE, backup_path)
    print(f"Backup: {backup_path}")

    kept = 0
    removed = 0
    rewritten = 0
    out_lines = []

    with open(LEARNING_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                out_lines.append(line)
                kept += 1
                continue

            output = obj.get("output", "") or ""
            if not _is_repetitive_output(output):
                out_lines.append(line.strip())
                kept += 1
                continue

            if mode == "remove":
                removed += 1
                continue

            # rewrite
            new_output = _rewrite_opening(output)
            obj["output"] = new_output
            out_lines.append(json.dumps(obj, ensure_ascii=False))
            rewritten += 1

    total = kept + removed + rewritten

    with open(LEARNING_FILE, "w", encoding="utf-8") as f:
        for ln in out_lines:
            f.write(ln.rstrip() + "\n")

    return {"kept": kept, "removed": removed, "rewritten": rewritten, "total": total}


if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "rewrite"
    if mode not in ("remove", "rewrite"):
        print("Usage: python filter_learning_data.py [remove|rewrite]")
        sys.exit(1)
    result = filter_learning_data(mode=mode)
    print(f"Done: kept={result['kept']} removed={result['removed']} rewritten={result['rewritten']} total={result['total']}")
