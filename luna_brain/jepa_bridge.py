"""
JEPA bridge — optional integration with New AI Child's JEPA for understanding + emotions.
If New AI Child is not available or import fails, uses a lightweight fallback (sentence-transformers)
so the brain still gets embeddings and internal state.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional, Tuple, List

# Configurable path: env NEW_AI_CHILD_DIR, or sibling of Luna Waifu folder
_default_child = Path(__file__).resolve().parent.parent.parent / "New AI Child"
_child_path = Path(os.getenv("NEW_AI_CHILD_DIR", str(_default_child))).resolve()
if _child_path.exists() and str(_child_path) not in sys.path:
    sys.path.insert(0, str(_child_path))

_jepa_instance = None
_jepa_available = False
_jepa_use_fallback = False  # True = using sentence-transformers fallback, not full JEPA


def _try_import_full_jepa() -> bool:
    """Try to load full JEPA from New AI Child."""
    global _jepa_instance, _jepa_available, _jepa_use_fallback
    if _jepa_available:
        return not _jepa_use_fallback
    try:
        from mind import IntegratedMind  # type: ignore
        _jepa_instance = IntegratedMind()
        _jepa_available = True
        _jepa_use_fallback = False
        return True
    except Exception as e:
        print(f"[luna_brain] Full JEPA (New AI Child) not available: {e}")
        return False


def _init_fallback() -> bool:
    """Use sentence-transformers (same as Luna's vector reasoning) so brain still gets embeddings."""
    global _jepa_instance, _jepa_available, _jepa_use_fallback
    if _jepa_available:
        return True
    try:
        from sentence_transformers import SentenceTransformer
        _jepa_instance = SentenceTransformer("all-MiniLM-L6-v2")
        _jepa_available = True
        _jepa_use_fallback = True
        print("[luna_brain] JEPA available (lightweight fallback: sentence-transformers)")
        return True
    except Exception as e:
        print(f"[luna_brain] JEPA fallback not available: {e}")
        return False


def _try_import_jepa() -> bool:
    """Full JEPA first, then fallback. Either way JEPA is 'available' for the brain."""
    if _try_import_full_jepa():
        return True
    return _init_fallback()


def get_understanding(user_message: str) -> Tuple[Optional[List[float]], str]:
    """
    Get understanding embedding and internal-state summary for Luna's prompt.
    Uses full JEPA (New AI Child) when available, else sentence-transformers fallback.
    """
    if not _try_import_jepa():
        return None, ""

    if not _jepa_use_fallback:
        # Full JEPA from New AI Child
        try:
            mind = _jepa_instance
            input_tensor = mind.text_to_tensor(user_message)
            with __import__("torch").no_grad():
                embedding = mind.jepa.understand(input_tensor)
            emb_list = embedding.cpu().numpy().flatten().tolist()
            try:
                primary = mind.emotions.get_primary_emotion()
                state_line = f"Your current internal state (from your deeper mind): {getattr(primary, 'name', str(primary))}."
            except Exception:
                state_line = ""
            return emb_list, state_line
        except Exception as e:
            print(f"[luna_brain] JEPA understand error: {e}")
            return None, ""

    # Fallback: sentence-transformers embedding + simple state
    try:
        model = _jepa_instance
        emb = model.encode(user_message, convert_to_numpy=True)
        emb_list = emb.flatten().tolist()
        state_line = "Your current internal state (lightweight): engaged and attentive."
        return emb_list, state_line
    except Exception as e:
        print(f"[luna_brain] Fallback embedding error: {e}")
        return None, ""


def is_available() -> bool:
    """True if full JEPA or fallback is available."""
    return _try_import_jepa()


def is_full_jepa() -> bool:
    """True only when full New AI Child JEPA is in use (not fallback)."""
    return _jepa_available and not _jepa_use_fallback
