"""
OrganizeAgent: Deduplicates, cleans, and merges profiles.
Runs on admin command or periodically.
"""
from __future__ import annotations

from typing import Dict, Any

from .logger import AgentLogger


def run_organize() -> Dict[str, Any]:
    """
    Compile profiles from history and clean bad facts.
    Returns combined stats.
    """
    log = AgentLogger.get()
    log.log("OrganizeAgent", "run", "organizing memory", "start")

    try:
        from luna_dna_memory import compile_profiles_from_history, clean_bad_facts, clean_duplicate_memories

        compile_result = compile_profiles_from_history()
        log.log(
            "OrganizeAgent",
            "compile",
            f"processed {compile_result['processed']} msgs, {compile_result['facts_added']} facts",
            "ok",
        )

        clean_result = clean_bad_facts()
        log.log(
            "OrganizeAgent",
            "clean",
            f"removed {clean_result['deleted']} bad facts",
            "ok",
        )

        dup_result = clean_duplicate_memories()
        log.log(
            "OrganizeAgent",
            "dedupe",
            f"removed {dup_result['deleted']} duplicate memories",
            "ok",
        )

        return {
            "processed": compile_result["processed"],
            "users_updated": compile_result["users_updated"],
            "facts_added": compile_result["facts_added"],
            "facts_deleted": clean_result["deleted"],
            "duplicates_deleted": dup_result["deleted"],
        }
    except Exception as e:
        log.log("OrganizeAgent", "error", str(e), "error")
        raise
