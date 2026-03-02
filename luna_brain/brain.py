"""
Combined HIM + JEPA brain: turn() and store_turn() for Luna.
Uses config, store, and jepa_bridge from this package.
"""
from __future__ import annotations

from typing import Optional, Tuple

from . import config
from .store import BrainStore
from .jepa_bridge import get_understanding, is_available as jepa_available


# Singleton store (same process as Luna)
_store: Optional[BrainStore] = None


def _get_store() -> BrainStore:
    global _store
    if _store is None:
        _store = BrainStore(
            max_turns=config.BRAIN_MEMORY_MAX_TURNS,
            top_k_retrieve=config.BRAIN_MEMORY_TOP_K,
        )
    return _store


def turn(
    user_message: str,
    user_id: Optional[str] = None,
    channel_id: Optional[str] = None,
    platform: Optional[str] = None,
) -> Tuple[str, str]:
    """
    One turn: get context and internal state for Luna's prompt.
    Returns (context_string, internal_state_string).
    """
    store = _get_store()
    # Get JEPA understanding (embedding + internal state)
    embedding, internal_state = get_understanding(user_message)
    # Retrieve similar / recent turns from store
    entries = store.retrieve(
        query_embedding=embedding,
        channel_id=channel_id,
        k=config.BRAIN_MEMORY_TOP_K,
    )
    context = store.format_context(entries, max_chars=1500)
    if context:
        context = f"[HIM+JEPA memory - relevant past context]\n{context}\n"
    return context, internal_state


def store_turn(
    user_message: str,
    luna_reply: str,
    user_id: Optional[str] = None,
    channel_id: Optional[str] = None,
    embedding: Optional[list] = None,
) -> None:
    """Store one turn (user message + Luna reply) in the brain."""
    if embedding is None:
        embedding, _ = get_understanding(user_message)
    store = _get_store()
    store.add(
        user_text=user_message,
        luna_text=luna_reply,
        embedding=embedding,
        channel_id=channel_id,
        user_id=user_id,
    )


def is_jepa_available() -> bool:
    """Whether JEPA (New AI Child) is available."""
    return jepa_available()


def save_brain(path: str) -> bool:
    """Save brain store to JSON file. Returns True if saved."""
    try:
        import json
        store = _get_store()
        data = store.export_state()
        if not data.get("turns"):
            return False
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=0, ensure_ascii=False)
        return True
    except Exception:
        return False


def load_brain(path: str) -> bool:
    """Load brain store from JSON file. Returns True if loaded."""
    import os
    import json
    if not os.path.exists(path):
        return False
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        store = _get_store()
        n = store.import_state(data)
        return n > 0
    except Exception:
        return False
