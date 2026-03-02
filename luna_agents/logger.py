"""
Central activity logger for Luna agents. Thread-safe, used by the Agents GUI.
"""
from __future__ import annotations

import threading
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Deque, List, Optional


@dataclass
class AgentEvent:
    """Single agent activity event."""
    agent: str
    action: str
    detail: str
    status: str  # "start", "ok", "skip", "error"
    timestamp: float = field(default_factory=lambda: __import__("time").time())

    def to_line(self) -> str:
        ts = datetime.fromtimestamp(self.timestamp).strftime("%H:%M:%S")
        icon = {"start": "▶", "ok": "✓", "skip": "○", "error": "✗"}.get(self.status, "•")
        return f"[{ts}] {icon} {self.agent}: {self.action} — {self.detail}"


class AgentLogger:
    """Thread-safe logger for agent activity. Keeps last N events."""
    _instance: Optional["AgentLogger"] = None
    _lock = threading.Lock()

    def __init__(self, max_events: int = 200):
        self._events: Deque[AgentEvent] = deque(maxlen=max_events)
        self._lock = threading.Lock()

    @classmethod
    def get(cls) -> "AgentLogger":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = AgentLogger()
        return cls._instance

    def log(self, agent: str, action: str, detail: str, status: str = "ok"):
        with self._lock:
            self._events.append(AgentEvent(agent=agent, action=action, detail=detail, status=status))

    def get_recent(self, n: int = 50) -> List[AgentEvent]:
        with self._lock:
            return list(self._events)[-n:]

    def get_all_lines(self, n: int = 100) -> List[str]:
        return [e.to_line() for e in self.get_recent(n)]

    def clear(self):
        with self._lock:
            self._events.clear()
