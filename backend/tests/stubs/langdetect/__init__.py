"""Test stub for langdetect module to avoid import errors in tests."""


def detect(text: str) -> str:
    """Mock language detection - returns language based on text content."""
    # Simple heuristic for testing
    spanish_words = [
        "hola",
        "cómo",
        "está",
        "estoy",
        "necesito",
        "ayuda",
        "días",
        "pensamientos",
        "ansiedad",
        "experimentando",
        "acelerados",
        "este",
        "es",
        "texto",
        "español",
        "con",
        "muchas",
        "palabras",
        "definitivamente",
    ]
    text_lower = text.lower()

    # Check for Arabic/Russian
    if "это" in text_lower or "текст" in text_lower or "русском" in text_lower:
        return "ru"
    if "هذا" in text or "نص" in text or "العربية" in text:
        return "ar"

    # Check for English words first
    english_indicators = [
        "world",
        "class",
        "cognitive",
        "behavioral",
        "therapy",
        "this",
        "the",
        "and",
        "with",
    ]
    if any(word in text_lower for word in english_indicators):
        return "en"

    # Check for Spanish
    if any(word in text_lower for word in spanish_words):
        return "es"
    return "en"


def detect_langs(text: str) -> list:
    """Mock language detection with probabilities."""

    class LangProb:
        def __init__(self, lang: str, prob: float):
            self.lang = lang
            self.prob = prob

    detected = detect(text)

    # For unsupported languages (when English is returned as default but text doesn't look English)
    text_lower = text.lower()
    english_words = [
        "this",
        "is",
        "the",
        "and",
        "or",
        "but",
        "with",
        "for",
        "to",
        "in",
        "of",
        "a",
        "an",
        "world",
        "class",
        "cognitive",
        "behavioral",
        "therapy",
    ]
    looks_english = any(word in text_lower for word in english_words)

    if detected == "es":
        return [LangProb("es", 0.95), LangProb("en", 0.05)]
    elif detected == "en" and not looks_english:
        # Low confidence for unsupported languages
        return [LangProb("en", 0.0)]
    elif detected in ["ru", "ar"]:
        return [LangProb(detected, 0.95), LangProb("en", 0.05)]
    return [LangProb("en", 0.95), LangProb("es", 0.05)]


class LangDetectException(Exception):  # noqa: N818
    """Mock exception for language detection errors."""

    pass


class DetectorFactory:
    """Mock DetectorFactory for language detection."""

    seed = 0


__all__ = ["DetectorFactory", "LangDetectException", "detect", "detect_langs"]
