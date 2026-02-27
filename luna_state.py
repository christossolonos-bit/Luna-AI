"""
Luna State - SEL-style hormone vector and personality knobs for consistency.

Provides:
- Hormone vector (dopamine, serotonin, cortisol, oxytocin, melatonin, novelty)
- Personality knobs (teasing, emoji_rate, verbosity, etc.) updated by feedback
- Persistent state via JSON file
"""

from __future__ import annotations

import json
import math
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, Optional

DECAY_RATE = 0.01
CYCLE_PERIOD_SEC = 900.0  # 15 minutes
CYCLE_STRENGTH = 0.05
STATE_FILE = "luna_state.json"


def _clamp(value: float, lo: float = -1.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


@dataclass
class HormoneVector:
    """Mood state - influences tone and variation subtly."""
    dopamine: float = 0.0
    serotonin: float = 0.0
    cortisol: float = 0.0
    oxytocin: float = 0.0
    melatonin: float = 0.0
    novelty: float = 0.0

    def apply(self, deltas: Dict[str, float]) -> "HormoneVector":
        for key, delta in deltas.items():
            if hasattr(self, key):
                setattr(self, key, _clamp(getattr(self, key) + delta))
        return self

    def decay(self) -> "HormoneVector":
        for f in ("dopamine", "serotonin", "cortisol", "oxytocin", "melatonin", "novelty"):
            v = getattr(self, f)
            setattr(self, f, v - v * DECAY_RATE)
        return self

    def mood_hint(self) -> str:
        return (
            f"Current mood: dopamine {self.dopamine:+.2f}, serotonin {self.serotonin:+.2f}, "
            f"oxytocin {self.oxytocin:+.2f}, cortisol {self.cortisol:+.2f}, "
            f"melatonin {self.melatonin:+.2f}, novelty {self.novelty:+.2f}. "
            "Let this influence tone and variation subtly."
        )


@dataclass
class LunaGlobalState:
    """Persistent personality knobs - updated by feedback, kept stable."""
    teasing_level: float = 0.4
    emoji_rate: float = 0.35
    preferred_length: str = "medium"  # short, medium, long
    vulnerability_level: float = 0.4
    confidence: float = 0.6
    playfulness: float = 0.6
    verbosity: float = 0.5
    empathy: float = 0.6
    randomness: float = 0.4
    total_messages_sent: int = 0
    positive_reactions_count: int = 0
    negative_reactions_count: int = 0
    last_updated: float = field(default_factory=time.time)

    def style_hint(self) -> str:
        return (
            f"Teasing level: {self.teasing_level:.2f}. Emoji rate: {self.emoji_rate:.2f}. "
            f"Preferred length: {self.preferred_length}. Vulnerability: {self.vulnerability_level:.2f}. "
            f"Confidence: {self.confidence:.2f}. Playfulness: {self.playfulness:.2f}. "
            f"Verbosity: {self.verbosity:.2f}. Empathy: {self.empathy:.2f}. "
            f"Randomness: {self.randomness:.2f}. "
            "Stay consistent with these traits."
        )


def _simple_sentiment(message: str) -> str:
    """Heuristic sentiment from message text (no LLM)."""
    msg = message.lower()
    pos = ["love", "great", "awesome", "thanks", "thank", "happy", "lol", "haha", "❤", "💕", "😊", "👍"]
    neg = ["hate", "bad", "awful", "stupid", "dumb", "suck", "annoying", "boring"]
    if any(p in msg for p in pos):
        return "positive"
    if any(n in msg for n in neg):
        return "negative"
    return "neutral"


def apply_message_effects(
    vector: HormoneVector,
    sentiment: str,
    intensity: float = 0.5,
    playful: bool = False,
) -> HormoneVector:
    """Update hormones based on incoming message classification."""
    delta_scale = max(0.05, min(1.25, intensity))
    deltas: Dict[str, float] = {}

    if sentiment == "positive":
        deltas.update(
            dopamine=0.10 * delta_scale,
            serotonin=0.06 * delta_scale,
            oxytocin=0.06 * delta_scale,
            cortisol=-0.04 * delta_scale,
            melatonin=-0.02 * delta_scale,
            novelty=0.03 * delta_scale,
        )
    elif sentiment == "negative":
        deltas.update(
            cortisol=0.10 * delta_scale,
            dopamine=-0.06 * delta_scale,
            serotonin=-0.05 * delta_scale,
            melatonin=0.03 * delta_scale,
            novelty=-0.02 * delta_scale,
        )
    else:
        deltas.update(cortisol=0.01 * delta_scale, novelty=0.01 * delta_scale)

    if playful:
        deltas["melatonin"] = deltas.get("melatonin", 0) - 0.03 * delta_scale
        deltas["dopamine"] = deltas.get("dopamine", 0) + 0.02 * delta_scale
        deltas["novelty"] = deltas.get("novelty", 0) + 0.02 * delta_scale

    return vector.apply(deltas)


def apply_cycle_drift(vector: HormoneVector) -> HormoneVector:
    """Gentle cyclic drift to keep hormones alive."""
    phase = time.time() / CYCLE_PERIOD_SEC
    cycle_deltas = {
        "dopamine": math.sin(phase) * CYCLE_STRENGTH,
        "serotonin": math.cos(phase) * (CYCLE_STRENGTH * 0.6),
        "cortisol": math.sin(phase + 1.2) * (CYCLE_STRENGTH * 0.4),
        "oxytocin": math.cos(phase + 0.7) * (CYCLE_STRENGTH * 0.5),
        "melatonin": -math.sin(phase + 2.0) * (CYCLE_STRENGTH * 0.3),
        "novelty": math.sin(phase + 0.3) * (CYCLE_STRENGTH * 0.7),
    }
    return vector.apply(cycle_deltas)


def apply_feedback(
    global_state: LunaGlobalState,
    positive: bool,
    strength: float = 0.02,
) -> LunaGlobalState:
    """Update personality knobs based on reaction feedback."""
    if positive:
        global_state.positive_reactions_count += 1
        global_state.teasing_level = _clamp(global_state.teasing_level + strength * 0.5, 0, 1)
        global_state.playfulness = _clamp(global_state.playfulness + strength * 0.3, 0, 1)
        global_state.empathy = _clamp(global_state.empathy + strength * 0.2, 0, 1)
        global_state.confidence = _clamp(global_state.confidence + strength * 0.1, 0, 1)
    else:
        global_state.negative_reactions_count += 1
        global_state.teasing_level = _clamp(global_state.teasing_level - strength * 0.5, 0, 1)
        global_state.randomness = _clamp(global_state.randomness - strength * 0.3, 0, 1)
        global_state.verbosity = _clamp(global_state.verbosity - strength * 0.2, 0, 1)
    global_state.last_updated = time.time()
    return global_state


class LunaStateManager:
    """Manages Luna's hormone vector and global state with persistence."""

    def __init__(self, state_path: Optional[str] = None):
        self.path = Path(state_path or STATE_FILE)
        self.hormones = HormoneVector()
        self.global_state = LunaGlobalState()
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            h = data.get("hormones", {})
            self.hormones = HormoneVector(
                dopamine=h.get("dopamine", 0),
                serotonin=h.get("serotonin", 0),
                cortisol=h.get("cortisol", 0),
                oxytocin=h.get("oxytocin", 0),
                melatonin=h.get("melatonin", 0),
                novelty=h.get("novelty", 0),
            )
            g = data.get("global_state", {})
            self.global_state = LunaGlobalState(
                teasing_level=g.get("teasing_level", 0.4),
                emoji_rate=g.get("emoji_rate", 0.35),
                preferred_length=g.get("preferred_length", "medium"),
                vulnerability_level=g.get("vulnerability_level", 0.4),
                confidence=g.get("confidence", 0.6),
                playfulness=g.get("playfulness", 0.6),
                verbosity=g.get("verbosity", 0.5),
                empathy=g.get("empathy", 0.6),
                randomness=g.get("randomness", 0.4),
                total_messages_sent=g.get("total_messages_sent", 0),
                positive_reactions_count=g.get("positive_reactions_count", 0),
                negative_reactions_count=g.get("negative_reactions_count", 0),
                last_updated=g.get("last_updated", time.time()),
            )
        except Exception:
            pass

    def save(self) -> None:
        try:
            data = {
                "hormones": asdict(self.hormones),
                "global_state": {
                    "teasing_level": self.global_state.teasing_level,
                    "emoji_rate": self.global_state.emoji_rate,
                    "preferred_length": self.global_state.preferred_length,
                    "vulnerability_level": self.global_state.vulnerability_level,
                    "confidence": self.global_state.confidence,
                    "playfulness": self.global_state.playfulness,
                    "verbosity": self.global_state.verbosity,
                    "empathy": self.global_state.empathy,
                    "randomness": self.global_state.randomness,
                    "total_messages_sent": self.global_state.total_messages_sent,
                    "positive_reactions_count": self.global_state.positive_reactions_count,
                    "negative_reactions_count": self.global_state.negative_reactions_count,
                    "last_updated": self.global_state.last_updated,
                },
            }
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def on_message_received(self, user_message: str) -> None:
        """Update hormones from incoming message."""
        sentiment = _simple_sentiment(user_message)
        playful = "lol" in user_message.lower() or "haha" in user_message.lower() or "~" in user_message
        intensity = 0.5
        self.hormones = apply_message_effects(
            self.hormones, sentiment, intensity, playful
        )
        self.hormones = apply_cycle_drift(self.hormones)
        self.save()

    def on_luna_replied(self) -> None:
        """Track that Luna sent a message."""
        self.global_state.total_messages_sent += 1
        self.save()

    def on_reaction_feedback(self, positive: bool) -> None:
        """Apply reaction feedback (e.g. 👍❤️ vs 👎)."""
        self.global_state = apply_feedback(self.global_state, positive)
        self.save()

    def get_mood_hint(self) -> str:
        """Get mood string for prompt injection."""
        return self.hormones.mood_hint()

    def get_style_hint(self) -> str:
        """Get personality knobs string for prompt injection."""
        return self.global_state.style_hint()


# Singleton for Luna
_state_manager: Optional[LunaStateManager] = None


def get_luna_state(base_dir: Optional[str] = None) -> LunaStateManager:
    global _state_manager
    if _state_manager is None:
        path = None
        if base_dir:
            path = os.path.join(base_dir, STATE_FILE)
        _state_manager = LunaStateManager(path)
    return _state_manager
