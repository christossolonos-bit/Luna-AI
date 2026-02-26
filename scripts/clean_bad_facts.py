#!/usr/bin/env python3
"""One-time cleanup: remove bad fact extractions (e.g. name='from Cyprus')."""

import sqlite3
import sys
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "luna_dna_memory.db")

def is_bad_name(val: str) -> bool:
    """Values that look like location phrases, not names."""
    v = val.strip().lower()
    return v.startswith("from ") or v.startswith("in ")

def clean_bad_facts():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Find bad name facts
    cursor.execute("SELECT fact_id, username, fact_type, fact_value FROM user_facts WHERE fact_type = 'name'")
    rows = cursor.fetchall()
    removed = 0
    for fact_id, username, fact_type, fact_value in rows:
        if is_bad_name(fact_value):
            cursor.execute("DELETE FROM user_facts WHERE fact_id = ?", (fact_id,))
            removed += 1
            print(f"  Removed: {username}|{fact_type}|{fact_value}")
    
    conn.commit()
    conn.close()
    return removed

if __name__ == "__main__":
    print(f"Cleaning bad facts in {DB_PATH}")
    n = clean_bad_facts()
    print(f"Removed {n} bad fact(s)")
    sys.exit(0 if n >= 0 else 1)
