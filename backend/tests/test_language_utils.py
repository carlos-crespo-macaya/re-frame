"""Tests for language utilities."""

from src.utils.language_utils import (
    get_default_language,
    get_language_instruction,
    normalize_language_code,
    validate_language_code,
)
from tests.fixtures.language_fixtures import SHORT_LANGUAGE_CODES, SUPPORTED_LANGUAGES


class TestLanguageValidation:
    """Test language validation functions."""

    def test_validate_supported_language(self):
        """Test validation of supported languages."""
        assert validate_language_code("en-US") is True
        assert validate_language_code("es-ES") is True
        assert validate_language_code("pt-BR") is True
        assert validate_language_code("de-DE") is True
        assert validate_language_code("fr-FR") is True

    def test_validate_unsupported_language(self):
        """Test validation of unsupported languages."""
        assert validate_language_code("xx-XX") is False
        assert validate_language_code("klingon") is False
        assert validate_language_code("") is False
        assert validate_language_code(None) is False

    def test_validate_all_supported_languages(self):
        """Test that all supported languages validate correctly."""
        for lang_code in SUPPORTED_LANGUAGES:
            assert validate_language_code(lang_code) is True

    def test_normalize_language_code(self):
        """Test language code normalization."""
        # Short codes
        assert normalize_language_code("en") == "en-US"
        assert normalize_language_code("es") == "es-ES"
        assert normalize_language_code("pt") == "pt-BR"

        # Case variations
        assert normalize_language_code("EN-us") == "en-US"
        assert normalize_language_code("Es-eS") == "es-ES"
        assert normalize_language_code("PT-br") == "pt-BR"

        # Already normalized
        assert normalize_language_code("en-US") == "en-US"
        assert normalize_language_code("es-ES") == "es-ES"

        # Invalid inputs
        assert normalize_language_code("") == "en-US"
        assert normalize_language_code(None) == "en-US"
        assert normalize_language_code("invalid") == "en-US"

    def test_normalize_all_short_codes(self):
        """Test normalization of all short language codes."""
        for short_code, expected in SHORT_LANGUAGE_CODES.items():
            assert normalize_language_code(short_code) == expected

    def test_default_language(self):
        """Test default language retrieval."""
        assert get_default_language() == "en-US"


class TestLanguageInstructions:
    """Test language instruction generation."""

    def test_get_language_instruction_english(self):
        """Test English language instruction."""
        instruction = get_language_instruction("en-US")
        assert "Respond in English" in instruction
        assert "clear, simple language" in instruction

    def test_get_language_instruction_spanish(self):
        """Test Spanish language instruction."""
        instruction = get_language_instruction("es-ES")
        assert "Responde en español" in instruction
        assert "lenguaje claro y sencillo" in instruction

    def test_get_language_instruction_portuguese(self):
        """Test Portuguese language instruction."""
        instruction = get_language_instruction("pt-BR")
        assert "Responda em português" in instruction
        assert "linguagem clara e simples" in instruction

    def test_get_language_instruction_german(self):
        """Test German language instruction."""
        instruction = get_language_instruction("de-DE")
        assert "Antworten Sie auf Deutsch" in instruction
        assert "klare, einfache Sprache" in instruction

    def test_get_language_instruction_french(self):
        """Test French language instruction."""
        instruction = get_language_instruction("fr-FR")
        assert "Répondez en français" in instruction
        assert "langage clair et simple" in instruction

    def test_get_language_instruction_default(self):
        """Test default language instruction when no language specified."""
        instruction = get_language_instruction(None)
        assert "Respond in English" in instruction

        instruction = get_language_instruction("")
        assert "Respond in English" in instruction

    def test_get_language_instruction_unsupported(self):
        """Test language instruction for unsupported language."""
        instruction = get_language_instruction("xx-XX")
        assert "Respond in English" in instruction  # Should fallback to English

    def test_all_supported_languages_have_instructions(self):
        """Test that all supported languages have instructions."""
        for lang_code in SUPPORTED_LANGUAGES:
            instruction = get_language_instruction(lang_code)
            assert len(instruction) > 0
            # Should either be language-specific or English fallback
            assert any(
                phrase in instruction
                for phrase in [
                    "Respond",
                    "Responde",
                    "Responda",
                    "Antworten",
                    "Répondez",
                    "Rispondi",
                    "Antwoord",
                    "Odpowiadaj",
                    "उत्तर",
                    "返信",
                    "답변",
                    "回复",
                    "回覆",
                ]
            )
