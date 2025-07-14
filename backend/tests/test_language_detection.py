"""Tests for language detection functionality."""

import pytest

from src.utils.language_detection import LanguageDetector


class TestLanguageDetector:
    """Test suite for LanguageDetector class."""

    def test_detect_english_text(self):
        """Test detection of English text."""
        text = "I'm feeling anxious about my presentation tomorrow"
        lang_code, confidence = LanguageDetector.detect_language(text)
        assert lang_code == "en"
        assert confidence > 0.8

    def test_detect_spanish_text(self):
        """Test detection of Spanish text."""
        text = "Me siento ansioso por mi presentación de mañana"
        lang_code, confidence = LanguageDetector.detect_language(text)
        assert lang_code == "es"
        assert confidence > 0.8

    def test_detect_empty_text(self):
        """Test handling of empty text."""
        lang_code, confidence = LanguageDetector.detect_language("")
        assert lang_code == "en"  # Default language
        assert confidence == 1.0

    def test_detect_whitespace_only(self):
        """Test handling of whitespace-only text."""
        lang_code, confidence = LanguageDetector.detect_language("   \n\t  ")
        assert lang_code == "en"  # Default language
        assert confidence == 1.0

    def test_detect_mixed_language(self):
        """Test detection with mixed language text."""
        # This text is mostly English with some Spanish
        text = "I'm feeling muy anxious about tomorrow"
        lang_code, _ = LanguageDetector.detect_language(text)
        assert lang_code in ["en", "es"]  # Could detect either

    def test_detect_unsupported_language(self):
        """Test detection of unsupported language defaults to English."""
        # French text (not supported)
        text = "Je suis anxieux à propos de ma présentation demain"
        lang_code, confidence = LanguageDetector.detect_language(text)
        # Should return default language since French is not supported
        assert lang_code == "en"
        assert confidence == 0.0  # Low confidence since no supported language detected

    def test_is_supported(self):
        """Test language support checking."""
        assert LanguageDetector.is_supported("en") is True
        assert LanguageDetector.is_supported("es") is True
        assert LanguageDetector.is_supported("fr") is False
        assert LanguageDetector.is_supported("de") is False

    def test_get_language_name(self):
        """Test getting language names."""
        assert LanguageDetector.get_language_name("en") == "English"
        assert LanguageDetector.get_language_name("es") == "Spanish"
        assert LanguageDetector.get_language_name("fr") == "Unknown"

    def test_should_use_detected_language(self):
        """Test confidence threshold checking."""
        assert LanguageDetector.should_use_detected_language(0.9) is True
        assert LanguageDetector.should_use_detected_language(0.8) is True
        assert LanguageDetector.should_use_detected_language(0.7) is True
        assert LanguageDetector.should_use_detected_language(0.6) is False

    def test_detect_with_fallback(self):
        """Test detection with automatic fallback."""
        # High confidence English
        text = "This is definitely English text with many words"
        assert LanguageDetector.detect_with_fallback(text) == "en"

        # High confidence Spanish
        text = "Este es definitivamente texto en español con muchas palabras"
        assert LanguageDetector.detect_with_fallback(text) == "es"

        # Short ambiguous text should fall back to default
        text = "OK"
        assert LanguageDetector.detect_with_fallback(text) == "en"

    def test_detect_short_text(self):
        """Test detection with very short text."""
        # Very short texts might have low confidence
        text = "Hola"
        lang_code, confidence = LanguageDetector.detect_language(text)
        # Should still detect Spanish but confidence might vary
        assert lang_code in ["es", "en"]

    def test_detect_numbers_only(self):
        """Test detection with numbers only."""
        text = "123 456 789"
        lang_code, confidence = LanguageDetector.detect_language(text)
        # Should return default language
        assert lang_code == "en"

    @pytest.mark.parametrize(
        "text,expected_lang",
        [
            ("Hello, how are you feeling today?", "en"),
            ("¿Hola, cómo te sientes hoy?", "es"),
            ("I'm experiencing anxiety", "en"),
            ("Estoy experimentando ansiedad", "es"),
            ("My thoughts are racing", "en"),
            ("Mis pensamientos están acelerados", "es"),
        ],
    )
    def test_common_cbt_phrases(self, text, expected_lang):
        """Test detection of common CBT-related phrases."""
        lang_code, confidence = LanguageDetector.detect_language(text)
        assert lang_code == expected_lang
        assert confidence > 0.7
