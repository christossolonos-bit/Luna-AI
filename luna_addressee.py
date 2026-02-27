"""
Decision logic for when Luna replies.
Adapted from SEL's score_addressee_intent - distinguishes messages TO Luna vs ABOUT Luna vs TO someone else.
"""

from __future__ import annotations

import re
from typing import Any, Mapping, Optional, Sequence

# Implicit references to Luna when she's not named (she/her, the bot, etc.)
_IMPLICIT_LUNA_RE = re.compile(
    r"\b(?:the\s+bot|the\s+ai|the\s+wolf\s+girl?|that\s+wolf\s+girl?|the\s+wolf\b|that\s+wolf\b|"
    r"the\s+ai\s+bot|our\s+wolf|our\s+bot)\b",
    flags=re.IGNORECASE,
)
_PRONOUN_SHE_HER = re.compile(r"\b(she'?s?|her|hers)\b", flags=re.IGNORECASE)

_GREETING_TARGET_RE = re.compile(
    r"^(hi|hey|hello|yo|sup|hiya|howdy|gm|good morning|good afternoon|good evening)\b[,\s]*@?([a-z0-9_\-]{2,32})",
    flags=re.IGNORECASE,
)

BROADCAST_GREETINGS = {
    "all", "everyone", "everybody", "folks", "friends", "chat", "guys", "yall", "y'all", "there",
}

_WORD_RE = re.compile(r"[a-z0-9_']+")
_SECOND_PERSON_WORDS = {"you", "your", "yours", "yourself", "u", "ur", "ya"}

# Other bots/entities in channel Luna should not intercept messages for
KNOWN_OTHER_NAMES = {"sel", "akane", "cel", "bot"}

# User explicitly instructs Luna NOT to reply - suppress response
_NOT_FOR_LUNA_RE = re.compile(
    r"(?:not\s+for\s+luna|don'?t\s+(?:answer|reply|respond)\s+luna|luna\s+don'?t\s+(?:answer|reply|respond)|"
    r"luna\s+(?:ignore|skip|don'?t)\b|ignore\s+luna|skip\s+luna|"
    r"not\s+luna\s+to\s+answer|luna\s+not\s+to\s+answer)",
    flags=re.IGNORECASE,
)


def _name_token_variants(name: str) -> set[str]:
    parts = re.findall(r"[a-z0-9_]+", (name or "").strip().lower())
    if not parts:
        return set()
    variants = {p for p in parts if len(p) >= 2}
    if len(parts) >= 2:
        joined = "".join(parts)
        if len(joined) >= 3:
            variants.add(joined)
    return variants


def is_direct_question_to_bot(content: str, bot_name: str) -> bool:
    lowered = (content or "").lower()
    return bot_name.lower() in lowered and "?" in lowered


def _luna_in_recent_context(recent_messages: Sequence[Mapping[str, Any]], bot_name: str) -> bool:
    """True if Luna was mentioned in the last few messages (for pronoun resolution)."""
    if not recent_messages:
        return False
    combined = " ".join(m.get("message", "") or "" for m in recent_messages[-4:]).lower()
    return "luna" in combined or bot_name.lower() in combined


def _is_invitation_or_question_about_luna(content: str) -> bool:
    """True if message invites Luna's input (question, ask her, what would she say, etc.)."""
    c = (content or "").lower()
    if "?" in c:
        return True
    return bool(re.search(
        r"(?:what would (?:she|her) say|ask (?:her|luna)|tell (?:her|luna)|"
        r"(?:she|luna) should|can (?:she|luna)|would (?:she|luna)|"
        r"wonder what (?:she|luna)|(?:she|luna) think)",
        c,
    ))


def score_addressee_intent(
    content: str,
    bot_name: str,
    *,
    is_reply_to_luna: bool,
    is_reply_to_other: bool,
    is_mentioned_luna: bool,
    mentioned_other_names: Sequence[str] | None = None,
    recent_other_names: Sequence[str] | None = None,
    greeting_target: Optional[str] = None,
    force_addressed: bool = False,
    is_from_other_bot: bool = False,
    recent_messages: Sequence[Mapping[str, Any]] | None = None,
    current_topic: Optional[str] = None,
    current_author: Optional[str] = None,
) -> dict:
    """
    Score whether a message is addressed to Luna vs another person (e.g. SEL, Akane).

    Uses token-level cues, Discord metadata (reply target, mentions), and context.
    recent_messages: previous messages in channel (exclude current) for context.
    current_topic: channel's current topic (e.g. "luna" = discussing Luna).
    current_author: display name of who sent this message (for continuation detection).
    Returns dict with luna_score, other_score, luna_reasons, other_reasons.
    """
    lowered = (content or "").strip().lower()
    tokens = _WORD_RE.findall(lowered)
    token_set = set(tokens)

    bot_variants = _name_token_variants(bot_name)
    name_called = bool(bot_variants.intersection(token_set))
    direct_question_to_luna = is_direct_question_to_bot(content, bot_name)
    if "?" in lowered and (is_reply_to_luna or is_mentioned_luna or force_addressed):
        direct_question_to_luna = True

    second_person_hits = sum(1 for t in tokens if t in _SECOND_PERSON_WORDS)

    luna_score = 0.0
    other_score = 0.0
    luna_reasons: list[str] = []
    other_reasons: list[str] = []

    if force_addressed:
        luna_score += 5.0
        luna_reasons.append("force_addressed")
    if is_mentioned_luna:
        luna_score += 3.8
        luna_reasons.append("mention_luna")
    if is_reply_to_luna:
        luna_score += 3.0
        luna_reasons.append("reply_to_luna")
    if name_called:
        luna_score += 2.0
        luna_reasons.append("name_called")
    if direct_question_to_luna:
        luna_score += 1.8
        luna_reasons.append("direct_question_to_luna")

    # Strong: replying to someone else = message is for them, not Luna
    if is_reply_to_other:
        other_score += 4.0
        other_reasons.append("reply_to_other")

    # Other names mentioned (SEL, Akane) - likely addressing them
    other_names = list(mentioned_other_names or []) + list(recent_other_names or [])
    other_name_variants: set[str] = set()
    for n in other_names:
        other_name_variants |= _name_token_variants(n)
    other_name_in_tokens = bool(other_name_variants.intersection(token_set))
    if other_name_in_tokens:
        other_score += 2.5
        other_reasons.append("other_name_mentioned")
    # "what do YOU think about luna" - "you" + reply to other = you = them
    if second_person_hits >= 1 and is_reply_to_other:
        other_score += 2.0
        other_reasons.append("second_person_reply_to_other")
    if second_person_hits >= 1 and other_name_in_tokens:
        other_score += 1.5
        other_reasons.append("second_person_with_other_name")

    # Greeting target: "hi @sel" vs "hi @luna"
    if greeting_target:
        gt_lower = greeting_target.lower().strip()
        if gt_lower in BROADCAST_GREETINGS:
            pass  # "hi everyone" - neutral
        elif gt_lower in bot_variants or gt_lower == "luna":
            luna_score += 1.5
            luna_reasons.append("greeting_to_luna")
        elif gt_lower in other_name_variants or gt_lower in KNOWN_OTHER_NAMES:
            other_score += 2.0
            other_reasons.append("greeting_to_other")

    # Luna mentioned as topic ("about luna") but not addressee
    if name_called and is_reply_to_other:
        # "what do you think about luna?" replied to SEL - luna is topic, SEL is addressee
        luna_score -= 2.0  # Reduce - we're the topic, not the addressee
        other_reasons.append("luna_as_topic_reply_to_other")

    # Another bot (e.g. Adam) referenced Luna - she should notice and can decide to chime in
    if is_from_other_bot and name_called:
        luna_score += 4.5
        luna_reasons.append("luna_referenced_by_other_bot")

    # Context awareness: Luna discussed without her name (she/her, the bot, the wolf)
    recent = list(recent_messages or [])[:-1]  # Exclude current message
    luna_in_recent = _luna_in_recent_context(recent, bot_name)
    has_implicit_ref = bool(_IMPLICIT_LUNA_RE.search(lowered))
    has_pronoun_ref = bool(_PRONOUN_SHE_HER.search(lowered)) and luna_in_recent
    topic_is_luna = current_topic and "luna" in (current_topic or "").lower()
    is_inviting = _is_invitation_or_question_about_luna(content or "")

    if has_implicit_ref:
        luna_score += 2.5
        luna_reasons.append("implicit_reference_the_bot_wolf")
    if has_pronoun_ref:
        luna_score += 2.5
        luna_reasons.append("pronoun_reference_she_her")
    if topic_is_luna and not name_called:
        luna_score += 1.5
        luna_reasons.append("topic_is_luna")
    if is_inviting and (name_called or has_implicit_ref or has_pronoun_ref or topic_is_luna):
        luna_score += 1.5
        luna_reasons.append("invitation_or_question")

    # "Your" addressing Luna (e.g. "he never tried to steal your snacks" = Luna's snacks)
    if "your" in token_set and luna_in_recent and not is_reply_to_other:
        luna_score += 2.5
        luna_reasons.append("your_addressing_luna")

    # Continuation: same user was just talking TO Luna (their prior message had "luna")
    if current_author and recent:
        for m in reversed(recent[-6:]):
            if (m.get("username") or "").lower() == (current_author or "").lower():
                prev_msg = (m.get("message") or "").lower()
                if "luna" in prev_msg or bot_name.lower() in prev_msg:
                    luna_score += 3.0
                    luna_reasons.append("continuation_same_user_talked_to_luna")
                break

    return {
        "luna_score": luna_score,
        "other_score": other_score,
        "luna_reasons": luna_reasons,
        "other_reasons": other_reasons,
    }


def is_explicit_not_for_luna(content: str) -> bool:
    """True if user explicitly instructs Luna not to reply/answer."""
    return bool(content and _NOT_FOR_LUNA_RE.search(content.strip()))


def should_luna_reply(
    content: str,
    bot_name: str,
    *,
    is_reply_to_luna: bool,
    is_reply_to_other: bool,
    is_mentioned_luna: bool,
    mentioned_other_names: Sequence[str] | None = None,
    recent_other_names: Sequence[str] | None = None,
    greeting_target: Optional[str] = None,
    force_addressed: bool = False,
    is_from_other_bot: bool = False,
    recent_messages: Sequence[Mapping[str, Any]] | None = None,
    current_topic: Optional[str] = None,
    current_author: Optional[str] = None,
) -> bool:
    """
    Returns True if Luna should reply (message is directed at her).
    """
    if is_explicit_not_for_luna(content or ""):
        return False
    result = score_addressee_intent(
        content=content,
        bot_name=bot_name,
        is_reply_to_luna=is_reply_to_luna,
        is_reply_to_other=is_reply_to_other,
        is_mentioned_luna=is_mentioned_luna,
        mentioned_other_names=mentioned_other_names,
        recent_other_names=recent_other_names,
        greeting_target=greeting_target,
        force_addressed=force_addressed,
        is_from_other_bot=is_from_other_bot,
        recent_messages=recent_messages,
        current_topic=current_topic,
        current_author=current_author,
    )
    return result["luna_score"] > result["other_score"]
