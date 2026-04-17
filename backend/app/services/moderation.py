import re

BAD_WORDS = ["fuck", "shit", "bitch"]
TECH_MIN_LENGTH = 3


def analyze_word(word: str, definition: str):
    text = f"{word} {definition}".lower()

    score = 1.0
    flags = []

    # profanity
    for bad in BAD_WORDS:
        if bad in text:
            score -= 0.7
            flags.append("profanity")

    # links (spam)
    if "http" in text:
        score -= 0.5
        flags.append("contains_link")

    # too short
    if len(word) < TECH_MIN_LENGTH:
        score -= 0.4
        flags.append("too_short")

    # non-technical (very basic heuristic)
    if len(definition.split()) < 3:
        score -= 0.3
        flags.append("low_quality_definition")

    # normalize
    score = max(0.0, min(score, 1.0))

    return {"score": score, "flags": flags, "approved_by_ai": score > 0.6}
