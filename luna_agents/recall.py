"""
RecallAgent: Retrieves and ranks memories for the current query.
Runs before Luna generates a reply. Uses memory search + question-type boosting.
"""
from __future__ import annotations

from typing import Optional, Tuple, Any

from .logger import AgentLogger


def run_recall(
    username: str,
    user_message: str,
    platform: str,
    usernames: Optional[list] = None,
    user_id: Optional[str] = None,
) -> Tuple[str, Optional[Any], bool]:
    """
    Search and inject memories. Returns (memory_block, vector_reasoning or None, enhanced).
    """
    log = AgentLogger.get()
    log.log("RecallAgent", "run", f"recall for {username}", "start")

    try:
        from luna_memory_search import search_and_inject_memories
        from luna_dna_memory import recall_dna_memories, recall_dna_memories_with_vector_reasoning

        memories = []
        vector_reasoning = None
        enhanced = False
        try:
            result = recall_dna_memories_with_vector_reasoning(
                username, user_message, limit=5, usernames=usernames
            )
            memories = result.get("memories", [])
            vector_reasoning = result.get("vector_reasoning")
            enhanced = result.get("enhanced", False)
            if enhanced:
                log.log("RecallAgent", "vector", "vector reasoning enhanced", "ok")
        except ImportError:
            memories = recall_dna_memories(
                username, user_message, limit=5, usernames=usernames
            )

        block = search_and_inject_memories(
            username=username,
            user_message=user_message,
            platform=platform,
            usernames=usernames,
            memories=memories,
            user_id=user_id,
        )

        log.log("RecallAgent", "inject", f"memory block ready ({len(block)} chars)", "ok")
        return block, vector_reasoning, enhanced
    except Exception as e:
        log.log("RecallAgent", "error", str(e), "error")
        raise
