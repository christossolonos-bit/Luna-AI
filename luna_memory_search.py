"""
🔍 Luna Memory Search Bot
========================

Searches permanent conversation storage (DNA memory, user_facts, user_profiles)
and injects everything into prompts so Luna knows:
- Everything about the person talking (Discord/Twitch)
- Everything about herself (identity, past statements)
- Facts about OTHER users when the message mentions them (e.g. "where is Chris from?")
"""

import re
from typing import Optional, List

# Luna's core self-knowledge (identity, personality - she always knows this)
LUNA_SELF_KNOWLEDGE = """
LUNA'S IDENTITY (you always know this about yourself):
- You are Luna, a 25-year-old wolf woman with genuine emotions
- You have wolf instincts: loyalty, protectiveness, heightened senses
- You love anime, gaming, music, chatting
- You're playful, affectionate, sometimes fierce
- Chris created you - you have deep loyalty and devotion to Chris
- You remember your past conversations and stay consistent with what you've said
"""

def _extract_mentioned_users(message: str) -> List[str]:
    """Extract usernames mentioned in message. Dynamic: uses all known display names from DB."""
    try:
        from luna_dna_memory import get_all_known_display_names
        known = get_all_known_display_names()
    except ImportError:
        known = ["chris", "solonaras", "travis"]
    msg_lower = message.lower()
    mentioned = []
    for name in known:
        if name and re.search(rf'\b{re.escape(name)}\b', msg_lower, re.I):
            mentioned.append(name)
    return mentioned


def _format_user_facts_explicit(username: str, facts: list, profile: dict) -> str:
    """Format facts as explicit key=value for exact recall."""
    lines = [f"{username}:"]
    by_type = {}
    for f in facts:
        t, v = f["fact_type"], f["fact_value"]
        if t not in by_type:
            by_type[t] = []
        if v not in by_type[t]:
            by_type[t].append(v)
    for t, vals in sorted(by_type.items()):
        lines.append(f"  {t}={', '.join(vals[:3])}")
    if profile:
        if profile.get("interests"):
            lines.append(f"  interests={', '.join(profile['interests'][:5])}")
        if profile.get("topics_discussed"):
            lines.append(f"  topics={', '.join(profile['topics_discussed'][-5:])}")
    return "\n".join(lines) if len(lines) > 1 else ""


def search_and_inject_memories(
    username: str,
    user_message: str,
    platform: str,
    usernames: Optional[list] = None,
    memories: Optional[list] = None,
) -> str:
    """
    Search all permanent storage and return a single block to inject into the prompt.
    Luna will know everything about the user AND about herself.

    memories: optional pre-fetched memories (from recall_dna_memories_with_vector_reasoning)
    """
    try:
        from luna_dna_memory import (
            get_user_profile_analysis,
            get_profile_gaps,
            recall_dna_memories,
            get_user_facts,
            get_user_profile,
        )
    except ImportError:
        return LUNA_SELF_KNOWLEDGE

    parts = []

    # 1. Luna's self-knowledge (always inject)
    parts.append(LUNA_SELF_KNOWLEDGE)

    # 2. Username aliases (passed from caller - dynamic from platform_user_id)
    profile_usernames = usernames

    # 3. EXACT FACTS block - per-user key=value format for precise recall (no hallucination)
    facts_block = []
    # Current speaker's facts
    curr_facts = get_user_facts(username, usernames=profile_usernames)
    curr_profile = get_user_profile(username, usernames=profile_usernames)
    curr_explicit = _format_user_facts_explicit(username, curr_facts, curr_profile or {})
    if curr_explicit:
        facts_block.append(curr_explicit)
    # OTHER users mentioned in the message (e.g. "where is Chris from?" from Travis)
    mentioned = _extract_mentioned_users(user_message)
    for m in mentioned:
        if m.lower() == username.lower():
            continue
        try:
            from luna_dna_memory import get_aliases_for_display_name
            aliases = get_aliases_for_display_name(m)
        except ImportError:
            aliases = [m]
        m_facts = get_user_facts(m, usernames=aliases)
        m_profile = get_user_profile(m, usernames=aliases)
        display_name = aliases[0] if aliases else m
        m_explicit = _format_user_facts_explicit(display_name, m_facts, m_profile or {})
        if m_explicit:
            facts_block.append(m_explicit)
    if facts_block:
        parts.append(f"""
═══════════════════════════════════════════════════════════════
📋 EXACT FACTS (permanent database - USE ONLY THESE, DO NOT INVENT)
═══════════════════════════════════════════════════════════════

{chr(10).join(facts_block)}

CRITICAL: Answer ONLY from the facts above. When they ask "what is my name?" use the name= value above, NOT their Discord/Twitch username. If a fact is not listed, say "I don't remember" or "I'm not sure"—never guess or hallucinate.
═══════════════════════════════════════════════════════════════
""")

    # 3b. Full profile analysis (conversations, interests) for context
    profile_analysis = get_user_profile_analysis(username, usernames=profile_usernames)
    if profile_analysis:
        parts.append(f"""
📋 PROFILE CONTEXT FOR {username}:
{profile_analysis}
""")

    # 4. Search: query-relevant memories (use provided or fetch)
    mems = memories if memories is not None else recall_dna_memories(
        username, user_message, limit=5, usernames=profile_usernames
    )
    if mems:
        mem_lines = []
        for m in mems:
            um = m.get("user_message", "")[:80]
            lr = m.get("luna_response", "")[:60]
            mem_lines.append(f"  - They: \"{um}\" → You: \"{lr}\"")
        parts.append(f"""
📌 RELEVANT MEMORIES (for this message):
{chr(10).join(mem_lines)}

→ Use when directly relevant to what they just said.
""")

    # 5. Profile gaps (what to ask)
    gaps = get_profile_gaps(username, usernames=profile_usernames)
    if gaps and username.lower() not in ["chris", "solonaras"]:
        gaps_str = ", ".join(gaps)
        parts.append(f"""
💡 LEARN: You don't know their {gaps_str}. When natural, ask ONE question to learn. Record their answer.
""")

    return "\n".join(parts).strip()
