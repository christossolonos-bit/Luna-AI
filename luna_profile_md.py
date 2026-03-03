"""
📄 Luna Profile MD — Organize user profiles as Markdown files

Each user gets a profile MD file (luna_knowledge/profiles/{username}.md) with:
- Structured sections (name, location, interests, occupation, preferences, etc.)
- Placeholders for gaps Luna can ask about
- Sync from DNA memory on updates
- Luna loads these for organized context and asks questions to fill gaps
"""

import os
import re
from datetime import datetime
from typing import List, Dict, Optional

# Profile sections — Luna asks questions to fill these in
PROFILE_SECTIONS = [
    ("name", "Name", "—"),
    ("location", "Location", "—"),
    ("interests", "Interests", "—"),
    ("occupation", "Occupation", "—"),
    ("preferences", "Preferences", "—"),
    ("topics_discussed", "Topics Discussed", "—"),
    ("relationship", "Relationship", "—"),
]

# Questions for !ask profile interview (gap key -> question)
PROFILE_QUESTIONS = {
    "name": "What should I call you?",
    "location": "Where are you from, or where do you live?",
    "interests": "What are your hobbies or interests?",
    "occupation": "What do you do? (job, school, etc.)",
    "preferences": "Any preferences I should know? (favorite things, likes, etc.)",
    "topics discussed": "What topics do you like to chat about?",
    "relationship": "How would you describe our relationship?",
}

# All profile sections (for !ask profile — always ask all, so user can update)
ALL_PROFILE_SECTIONS = [s[1].lower() for s in PROFILE_SECTIONS]

# Map gap key (from get_profile_gaps_from_md) to (fact_type, multi_value)
GAP_TO_FACT_TYPE = {
    "name": ("name", False),
    "location": ("location", False),
    "interests": ("interest", True),   # multi-value
    "occupation": ("occupation", False),
    "preferences": ("preference", False),
    "topics discussed": ("topics_discussed", False),  # profile field
    "relationship": ("relationship_level", False),   # profile field
}

PROFILES_DIR = os.path.join(os.path.dirname(__file__), "luna_knowledge", "profiles")


def _sanitize_filename(name: str) -> str:
    """Safe filename from username."""
    s = re.sub(r'[^\w\-.]', '_', name.strip() or "unknown")
    return s[:80] or "unknown"


def _ensure_profile_dir():
    os.makedirs(PROFILES_DIR, exist_ok=True)


def get_profile_path(username: str) -> str:
    """Path to user's profile MD file."""
    _ensure_profile_dir()
    return os.path.join(PROFILES_DIR, f"{_sanitize_filename(username)}.md")


def _facts_to_section_data(facts: List[Dict], profile: Dict) -> Dict[str, str]:
    """Convert DNA facts + profile to section values."""
    by_type = {}
    for f in facts:
        t, v = f.get("fact_type"), f.get("fact_value", "")
        if not t or not v:
            continue
        if t not in by_type:
            by_type[t] = []
        if v not in by_type[t]:
            by_type[t].append(v)
    # Single-value: take first
    for t in ("name", "location", "occupation"):
        by_type[t] = by_type.get(t, [None])[0] if by_type.get(t) else None
    # Multi-value: list
    interests = by_type.get("interest") or by_type.get("interests") or []
    if profile and profile.get("interests"):
        interests = list(set(interests) | set(profile["interests"]))[:15]
    prefs = profile.get("preferences") or {}
    topics = profile.get("topics_discussed") or []
    rel = profile.get("relationship_level") if profile else None
    if rel and str(rel) != "new":
        rel = str(rel)
    else:
        rel = None
    return {
        "name": by_type.get("name") or None,
        "location": by_type.get("location") or None,
        "interests": interests if interests else None,
        "occupation": by_type.get("occupation") or None,
        "preferences": prefs if prefs else None,
        "topics_discussed": topics[-10:] if topics else None,
        "relationship": rel,
    }


def _format_section_value(key: str, val) -> str:
    """Format a section value for MD."""
    if val is None:
        return "—"
    if key == "interests" and isinstance(val, list):
        return "\n".join(f"- {v}" for v in val) if val else "—"
    if key == "topics_discussed" and isinstance(val, list):
        return ", ".join(val[-10:]) if val else "—"
    if key == "preferences" and isinstance(val, dict):
        return ", ".join(f"{k}={v}" for k, v in list(val.items())[:8]) if val else "—"
    return str(val).strip()


def sync_profile_from_dna(username: str, usernames: List[str] = None) -> bool:
    """
    Sync user profile from DNA memory to MD file.
    Call after save_user_fact or save_user_profile.
    """
    try:
        from luna_dna_memory import get_user_facts, get_user_profile
    except ImportError:
        return False
    facts = get_user_facts(username, usernames=usernames)
    profile = get_user_profile(username, usernames=usernames) or {}
    data = _facts_to_section_data(facts, profile)
    return save_profile_md(username, data)


def save_profile_md(username: str, data: Dict) -> bool:
    """Write profile data to MD file."""
    try:
        _ensure_profile_dir()
        path = get_profile_path(username)
        lines = [
            f"# {username}",
            "",
            f"> Profile • Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
        ]
        for key, title, _ in PROFILE_SECTIONS:
            val = data.get(key)
            formatted = _format_section_value(key, val)
            lines.append(f"## {title}")
            lines.append(formatted)
            lines.append("")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return True
    except Exception as e:
        print(f"⚠️ Profile MD save failed for {username}: {e}")
        return False


def load_profile_md(username: str) -> Optional[str]:
    """Load profile MD content. Returns None if file doesn't exist."""
    path = get_profile_path(username)
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


def get_profile_gaps_from_md(username: str) -> List[str]:
    """Return list of empty sections (Luna asks to fill these)."""
    content = load_profile_md(username)
    if not content:
        return [s[1].lower() for s in PROFILE_SECTIONS]
    gaps = []
    for key, title, placeholder in PROFILE_SECTIONS:
        # Look for ## Title\n— or ## Title\n\n
        pat = re.compile(rf"##\s+{re.escape(title)}\s*\n([^\n#]*)", re.I)
        m = pat.search(content)
        if m:
            val = m.group(1).strip()
            if not val or val == "—" or val.lower() == "(luna will ask)":
                gaps.append(title.lower())
    return gaps


def save_profile_answer(username: str, gap_key: str, answer: str, user_id: str = None) -> bool:
    """
    Save user's answer for a profile gap to DNA memory.
    gap_key: from get_profile_gaps_from_md (e.g. "name", "location")
    """
    if not answer or len(answer.strip()) < 1:
        return False
    answer = answer.strip()[:500]
    mapping = GAP_TO_FACT_TYPE.get(gap_key.lower())
    if not mapping:
        return False
    fact_type, multi = mapping
    try:
        from luna_dna_memory import save_user_fact, save_user_profile, get_user_profile, link_user_identity
        link_user_identity("discord", username, user_id)
        if fact_type in ("topics_discussed", "relationship_level", "preference"):
            prof = get_user_profile(username) or {}
            if fact_type == "topics_discussed":
                topics = prof.get("topics_discussed") or []
                for t in answer.replace(",", " ").split():
                    t = t.strip()
                    if t and len(t) > 2 and t not in topics:
                        topics.append(t)
                save_user_profile(username, {"topics_discussed": topics[-20:]})
            elif fact_type == "relationship_level":
                save_user_profile(username, {"relationship_level": answer})
            else:
                prefs = prof.get("preferences") or {}
                idx = len(prefs)
                prefs[f"preference_{idx}"] = answer
                save_user_profile(username, {"preferences": prefs})
        else:
            save_user_fact(username, fact_type, answer, multi_value=multi)
        return True
    except Exception as e:
        print(f"⚠️ save_profile_answer failed: {e}")
        return False


def get_profile_md_for_context(username: str, usernames: List[str] = None) -> str:
    """
    Get profile MD content for prompt injection.
    Syncs from DNA first so MD is up to date.
    """
    sync_profile_from_dna(username, usernames=usernames)
    content = load_profile_md(username)
    if not content:
        return ""
    return content
