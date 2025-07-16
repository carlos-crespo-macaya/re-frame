"""Test stub for langdetect module to avoid import errors in tests."""

def detect(text: str) -> str:
    """Mock language detection - always returns 'en' for testing."""
    return 'en'


def detect_langs(text: str) -> list:
    """Mock language detection with probabilities."""
    class LangProb:
        def __init__(self, lang: str, prob: float):
            self.lang = lang
            self.prob = prob
    
    return [LangProb('en', 1.0)]


class LangDetectException(Exception):
    """Mock exception for language detection errors."""
    pass


__all__ = ['detect', 'detect_langs', 'LangDetectException']