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


def _detect_fact_question_type(message: str) -> Optional[str]:
    """Detect fact type asked (age, name, location, etc.) for surfacing the right answer."""
    m = message.strip().lower()
    if re.search(r'\b(age|how old|years old|my age)\b', m):
        return "age"
    if re.search(r'\b(my name|what\'?s my name|name\?|who am i)\b', m):
        return "name"
    if re.search(r'\b(where (do i|am i) live|from|location|my location)\b', m):
        return "location"
    if re.search(r'\b(what do i (do|like)|my job|occupation|work)\b', m):
        return "occupation"
    return None


def _get_fact_value(facts: list, fact_type: str) -> Optional[str]:
    """Get first value for fact_type from facts list."""
    for f in facts:
        if f.get("fact_type") == fact_type:
            return f.get("fact_value")
    return None


def _format_user_facts_explicit(username: str, facts: list, profile: dict,
                                question_type: Optional[str] = None) -> str:
    """Format facts as explicit key=value for exact recall. Prioritize question_type first."""
    lines = [f"{username}:"]
    by_type = {}
    for f in facts:
        t, v = f["fact_type"], f["fact_value"]
        if t not in by_type:
            by_type[t] = []
        if v not in by_type[t]:
            by_type[t].append(v)
    # Sort: put question-relevant fact first when detected
    items = sorted(by_type.items())
    if question_type and question_type in by_type:
        items = [(question_type, by_type[question_type])] + [
            (k, v) for k, v in items if k != question_type
        ]
    for t, vals in items:
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
    user_id: Optional[str] = None,
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
            _is_name_question,
        )
    except ImportError:
        return LUNA_SELF_KNOWLEDGE

    parts = []

    # 1. Luna's self-knowledge (always inject)
    parts.append(LUNA_SELF_KNOWLEDGE)

    # 2. Username aliases (passed from caller - dynamic from platform_user_id)
    profile_usernames = usernames

    # 2b. Detect fact question type for surfacing the right answer
    question_type = _detect_fact_question_type(user_message)

    # 3. EXACT FACTS block - per-user key=value format for precise recall (no hallucination)
    facts_block = []
    # Current speaker's facts
    curr_facts = get_user_facts(username, usernames=profile_usernames)
    curr_profile = get_user_profile(username, usernames=profile_usernames)
    # Fallback: when user asks "what is my name?" and we have no name, inject creator's name if known
    try:
        from luna_clean import CHRIS_DISCORD_USER_ID
        if user_id and str(user_id) == str(CHRIS_DISCORD_USER_ID):
            has_name = any(f.get("fact_type") == "name" for f in curr_facts)
            if not has_name and _is_name_question(user_message):
                curr_facts = curr_facts + [{"fact_type": "name", "fact_value": "Chris"}]
    except ImportError:
        pass
    curr_explicit = _format_user_facts_explicit(
        username, curr_facts, curr_profile or {}, question_type=question_type
    )
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
        # When user asks a fact question and we have the answer, surface it prominently
        answer_hint = ""
        if question_type:
            fact_val = _get_fact_value(curr_facts, question_type)
            if fact_val:
                label = {"age": "age", "name": "name", "location": "where they live",
                        "occupation": "what they do"}.get(question_type, question_type)
                answer_hint = f"\n⚡ USER IS ASKING ABOUT {label.upper()}: {username}'s {question_type}={fact_val}. USE THIS VALUE in your answer.\n"
        parts.append(f"""
═══════════════════════════════════════════════════════════════
📋 EXACT FACTS (permanent database - GROUND TRUTH ONLY)
═══════════════════════════════════════════════════════════════
{answer_hint}
{chr(10).join(facts_block)}

CRITICAL - FACTUAL ACCURACY:
- Answer ONLY from the facts above. Never invent details (e.g. snacks, jokes, anecdotes) that are not explicitly listed.
- When asked about a fact you HAVE above (age, name, location, etc.), you MUST use that value. Never say "I don't know" for a fact that is listed.
- When asked "what is my name?" use the name= value above, NOT their Discord/Twitch username.
- When asked "who is X?" or "tell me about X": use ONLY the EXACT FACTS for X. If X has no facts or few facts, say briefly what you know and admit you don't know more. Do NOT make up stories, habits, or details.
- If a fact is not listed, say "I don't remember" or "I'm not sure"—never guess or hallucinate.
- When challenged "did you make that up?" or "did you invent that?": check the facts above. If the detail is NOT listed, admit honestly: "I made that up" or "I don't have that in my memory—I invented it." Never defend invented details.
═══════════════════════════════════════════════════════════════
""")

    # 3b. Organized profile (MD) — structured sections, Luna asks to fill gaps
    try:
        from luna_profile_md import get_profile_md_for_context, get_profile_gaps_from_md
        profile_md = get_profile_md_for_context(username, usernames=profile_usernames)
        if profile_md:
            parts.append(f"""
📋 ORGANIZED PROFILE FOR {username} (sections to fill when you learn more):
{profile_md}

→ Use the facts above. Empty sections (—) are gaps: when natural, ask ONE question to fill them. Record their answer.
""")
    except ImportError:
        profile_md = None
    # 3c. Full profile analysis (conversations, interests) for context
    profile_analysis = get_user_profile_analysis(username, usernames=profile_usernames)
    if profile_analysis:
        parts.append(f"""
📋 PROFILE CONTEXT FOR {username}:
{profile_analysis}

⚠️ WARNING: Past conversations above may contain your previous mistakes or inventions. Verify against EXACT FACTS only. Do NOT treat past replies as ground truth.
""")

    # 4. Search: query-relevant memories (use provided or fetch)
    mems = memories if memories is not None else recall_dna_memories(
        username, user_message, limit=5, usernames=profile_usernames
    )
    if mems:
        try:
            from luna_continuous_learning import sanitize_repetitive_luna_opening
        except ImportError:
            def sanitize_repetitive_luna_opening(x): return x
        mem_lines = []
        for m in mems:
            um = m.get("user_message", "")[:80]
            lr = sanitize_repetitive_luna_opening(m.get("luna_response", "")[:60])
            mem_lines.append(f"  - They: \"{um}\" → You: \"{lr}\"")
        parts.append(f"""
📌 RELEVANT MEMORIES (for this message):
{chr(10).join(mem_lines)}

→ Use when directly relevant. WARNING: Past replies may contain errors or inventions. For factual questions about people, rely on EXACT FACTS only—do not repeat unverified details from memories.
→ CRITICAL: Do NOT repeat or recap your past replies (the "You: ..." lines above) in your response. They are for context only. Answer ONLY the current message.
""")

    # 5. Profile gaps (what to ask) — prefer MD gaps when available
    try:
        from luna_profile_md import get_profile_gaps_from_md, load_profile_md
        if load_profile_md(username):
            gaps = get_profile_gaps_from_md(username)
        else:
            gaps = get_profile_gaps(username, usernames=profile_usernames)
    except ImportError:
        gaps = get_profile_gaps(username, usernames=profile_usernames)
    if gaps and username.lower() not in ["chris", "solonaras"]:
        gaps_str = ", ".join(gaps)
        parts.append(f"""
💡 LEARN: Profile sections to fill: {gaps_str}. When natural, ask ONE question to learn. Record their answer—it will be saved to their profile.
""")

    return "\n".join(parts).strip()
