"""
Minimal HIM-like memory store: embeddings + text snippets.
Uses a simple buffer with optional vector similarity (numpy) for retrieval.
"""
from __future__ import annotations

import time
from collections import deque
from typing import List, Optional, Tuple

# Optional: numpy for similarity search
try:
    import numpy as np
    _NUMPY_AVAILABLE = True
except ImportError:
    np = None
    _NUMPY_AVAILABLE = False


class BrainStore:
    """In-memory store of (embedding, user_text, luna_text, channel_id, timestamp)."""

    def __init__(self, max_turns: int = 500, top_k_retrieve: int = 5):
        self.max_turns = max_turns
        self.top_k_retrieve = top_k_retrieve
        self._turns: deque = deque(maxlen=max_turns)
        self._embeddings: List[list] = []  # same order as _turns, for numpy search

    def add(self, user_text: str, luna_text: str, embedding: Optional[List[float]] = None,
            channel_id: Optional[str] = None, user_id: Optional[str] = None) -> None:
        entry = {
            "user": user_text,
            "luna": luna_text,
            "embedding": embedding,
            "channel_id": channel_id or "",
            "user_id": user_id or "",
            "ts": time.time(),
        }
        self._turns.append(entry)
        if embedding is not None and _NUMPY_AVAILABLE:
            self._embeddings.append(embedding)
        else:
            self._embeddings.append([])
        # Keep same length
        while len(self._embeddings) > len(self._turns):
            self._embeddings.pop(0)
        while len(self._turns) > self.max_turns and len(self._embeddings) > 0:
            self._embeddings.pop(0)

    def retrieve(self, query_embedding: Optional[List[float]] = None,
                 channel_id: Optional[str] = None, k: Optional[int] = None) -> List[dict]:
        k = k or self.top_k_retrieve
        if not self._turns:
            return []

        # Filter by channel if requested
        turns = list(self._turns)
        embeddings = list(self._embeddings)
        if channel_id:
            paired = [(t, e) for t, e in zip(self._turns, self._embeddings) if t.get("channel_id") == channel_id]
            turns = [t for t, _ in paired]
            embeddings = [e for _, e in paired]

        if not turns:
            return []

        # Vector similarity if we have query embedding and numpy
        if query_embedding and _NUMPY_AVAILABLE and embeddings and len(embeddings[0]) == len(query_embedding):
            try:
                arr = np.array(embeddings, dtype=np.float32)
                q = np.array(query_embedding, dtype=np.float32).reshape(1, -1)
                # Cosine similarity
                norms = np.linalg.norm(arr, axis=1, keepdims=True)
                norms[norms == 0] = 1
                arr_n = arr / norms
                q_n = q / (np.linalg.norm(q) or 1)
                sim = arr_n @ q_n.T
                sim = sim.flatten()
                idx = np.argsort(-sim)[:k]
                return [turns[i] for i in idx]
            except Exception:
                pass

        # Fallback: last k turns
        return list(turns[-k:])

    def format_context(self, entries: List[dict], max_chars: int = 1500) -> str:
        lines = []
        for e in entries:
            line = f"User: {e.get('user', '')[:200]} ... Luna: {e.get('luna', '')[:200]}"
            lines.append(line)
        text = "\n".join(lines)
        if len(text) > max_chars:
            text = text[-max_chars:]
        return text.strip() or ""
