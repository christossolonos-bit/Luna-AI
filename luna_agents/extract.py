"""
ExtractAgent: Extracts facts from user messages before Luna responds.
Runs on every user message to learn names, age, interests, etc.
"""
from __future__ import annotations

from typing import List, Optional, Tuple

from .logger import AgentLogger


def run_extract(
    user_message: str,
    platform: str,
    username: str,
    user_id: Optional[str] = None,
) -> int:
    """
    Extract and save facts from message. Returns count of facts saved.
    """
    log = AgentLogger.get()
    log.log("ExtractAgent", "run", f"message from {username} ({platform})", "start")

    try:
        from luna_dna_memory import save_facts_from_message, link_user_identity

        link_user_identity(platform, username, user_id)
        n = save_facts_from_message(user_message, platform, username, user_id)

        if n > 0:
            log.log("ExtractAgent", "saved", f"{n} facts from message", "ok")
        else:
            log.log("ExtractAgent", "skip", "no facts to extract", "skip")
        return n
    except Exception as e:
        log.log("ExtractAgent", "error", str(e), "error")
        raise
