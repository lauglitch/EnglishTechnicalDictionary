def detect_grammar_class(word: str):
    word = word.lower()

    if word.endswith("ing"):
        return "verb"
    if word.endswith("tion"):
        return "noun"
    if word.endswith("ly"):
        return "adverb"
    if word.endswith("ive"):
        return "adjective"

    return "noun"


def analyze_word(word, definition, example, topic):
    score = 0.0
    flags = []

    text = f"{word} {definition} {example} {topic}".lower()

    if len(word) < 2:
        flags.append("word_too_short")
        score -= 0.5

    if any(bad in text for bad in ["fuck", "shit", "hate"]):
        flags.append("unsafe_content")
        score -= 1.0

    if len(definition) < 5:
        flags.append("weak_definition")
        score -= 0.3

    score = max(0.0, 1.0 + score)

    approved = score > 0.6 and len(flags) == 0

    return {
        "score": score,
        "flags": flags,
        "approved_by_ai": approved,
    }
