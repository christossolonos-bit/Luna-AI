"""
PersistAgent: Saves brain store to disk on shutdown, loads on startup.
Ensures conversation continuity across restarts.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from .logger import AgentLogger

BRAIN_PERSIST_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), ".luna_brain_persist.json"
)


def run_save() -> bool:
    """Save brain store to disk. Returns True if saved."""
    log = AgentLogger.get()
    log.log("PersistAgent", "run", "saving brain to disk", "start")

    try:
        from luna_brain import save_brain
        ok = save_brain(BRAIN_PERSIST_PATH)
        if ok:
            log.log("PersistAgent", "save", "brain persisted", "ok")
        else:
            log.log("PersistAgent", "skip", "no brain data to save", "skip")
        return ok
    except ImportError:
        log.log("PersistAgent", "skip", "brain not available", "skip")
        return False
    except Exception as e:
        log.log("PersistAgent", "error", str(e), "error")
        return False


def run_load() -> bool:
    """Load brain store from disk. Returns True if loaded."""
    log = AgentLogger.get()
    log.log("PersistAgent", "run", "loading brain from disk", "start")

    if not os.path.exists(BRAIN_PERSIST_PATH):
        log.log("PersistAgent", "skip", "no persist file found", "skip")
        return False

    try:
        from luna_brain import load_brain
        ok = load_brain(BRAIN_PERSIST_PATH)
        if ok:
            log.log("PersistAgent", "load", "brain restored from disk", "ok")
        else:
            log.log("PersistAgent", "skip", "load returned false", "skip")
        return ok
    except ImportError:
        log.log("PersistAgent", "skip", "brain not available", "skip")
        return False
    except Exception as e:
        log.log("PersistAgent", "error", str(e), "error")
        return False
