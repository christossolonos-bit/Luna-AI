"""
StoreAgent: Saves conversation to DNA memory and brain after Luna replies.
Ensures identity linking and persistence.
"""
from __future__ import annotations

from typing import Optional

from .logger import AgentLogger


def run_store(
    user_message: str,
    luna_reply: str,
    platform: str,
    username: str,
    user_id: Optional[str] = None,
    channel_id: Optional[str] = None,
    brain_store_turn=None,
) -> None:
    """
    Save turn to DNA memory and brain. Called after Luna generates a reply.
    """
    log = AgentLogger.get()
    log.log("StoreAgent", "run", f"saving turn for {username}", "start")

    try:
        from luna_dna_memory import save_dna_memory, get_user_aliases, link_user_identity

        link_user_identity(platform, username, user_id)
        save_dna_memory(user_message, luna_reply, platform, username, user_id=user_id)
        log.log("StoreAgent", "dna", "saved to DNA memory", "ok")

        if brain_store_turn:
            try:
                brain_store_turn(user_message, luna_reply, user_id=user_id, channel_id=channel_id)
                log.log("StoreAgent", "brain", "stored in HIM+JEPA brain", "ok")
            except Exception as e:
                log.log("StoreAgent", "brain", str(e), "error")
    except Exception as e:
        log.log("StoreAgent", "error", str(e), "error")
        raise
