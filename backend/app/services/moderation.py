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


def analyze_word(word: str, definition: str, example: str, topic: str):
    text = f"{word} {definition} {example} {topic}".lower()

    score = 1.0
    flags = []

    if any(bad in text for bad in ["fuck", "shit", "bitch"]):
        score -= 0.7
        flags.append("profanity")

    if len(definition.split()) < 4:
        score -= 0.3
        flags.append("weak_definition")

    if example and len(example.split()) < 4:
        score -= 0.2
        flags.append("weak_example")

    if topic and len(topic) < 3:
        score -= 0.2
        flags.append("weak_topic")

    grammar_class = detect_grammar_class(word)

    score = max(0.0, min(score, 1.0))

    return {
        "score": score,
        "flags": flags,
        "approved_by_ai": score > 0.6,
        "grammar_class": grammar_class,
    }
