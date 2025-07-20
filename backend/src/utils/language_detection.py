"""Language detection utility for automatic language identification."""

from typing import ClassVar

from langdetect import DetectorFactory, LangDetectException, detect_langs

# Set seed for consistent results
DetectorFactory.seed = 0


class LanguageDetector:
    """Handles automatic language detection for user input."""

    SUPPORTED_LANGUAGES: ClassVar[dict[str, str]] = {
        "en": "English",
        "es": "Spanish",
    }
    DEFAULT_LANGUAGE: ClassVar[str] = "en"
    CONFIDENCE_THRESHOLD: ClassVar[float] = 0.7

    @classmethod
    def detect_language(cls, text: str) -> tuple[str, float]:
        """
        Detect the language of the given text.

        Args:
            text: The text to analyze

        Returns:
            Tuple of (language_code, confidence)
            Falls back to DEFAULT_LANGUAGE if detection fails
        """
        if not text or not text.strip():
            return cls.DEFAULT_LANGUAGE, 1.0

        try:
            detections = detect_langs(text)
            if not detections:
                return cls.DEFAULT_LANGUAGE, 0.0

            for detection in detections:
                if detection.lang in cls.SUPPORTED_LANGUAGES:
                    return detection.lang, detection.prob

            # If no supported language detected, use default
            return cls.DEFAULT_LANGUAGE, 0.0

        except LangDetectException:
            return cls.DEFAULT_LANGUAGE, 0.0

    @classmethod
    def is_supported(cls, language_code: str) -> bool:
        """Check if a language is supported."""
        return language_code in cls.SUPPORTED_LANGUAGES

    @classmethod
    def get_language_name(cls, language_code: str) -> str:
        """Get the full name of a language from its code."""
        return cls.SUPPORTED_LANGUAGES.get(language_code, "Unknown")

    @classmethod
    def should_use_detected_language(cls, confidence: float) -> bool:
        """Determine if we should use the detected language based on confidence."""
        return confidence >= cls.CONFIDENCE_THRESHOLD

    @classmethod
    def detect_with_fallback(cls, text: str) -> str:
        """
        Detect language with automatic fallback to default.

        Args:
            text: The text to analyze

        Returns:
            The detected language code if confident, otherwise DEFAULT_LANGUAGE
        """
        language_code, confidence = cls.detect_language(text)

        if cls.should_use_detected_language(confidence):
            return language_code
        return cls.DEFAULT_LANGUAGE
