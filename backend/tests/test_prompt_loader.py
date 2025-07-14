"""Tests for prompt loader functionality."""

import pytest

from src.utils.prompt_loader import PromptLoader


class TestPromptLoader:
    """Test suite for PromptLoader class."""

    def test_load_default_prompt(self):
        """Test loading default English prompts."""
        # Load discovery prompt
        content = PromptLoader.load_prompt("discovery", "en")
        assert "Discovery Phase Instructions" in content
        assert "Role" in content
        assert "Task" in content

        # Load reframing prompt
        content = PromptLoader.load_prompt("reframing", "en")
        assert "Reframing Phase Instructions" in content

        # Load summary prompt
        content = PromptLoader.load_prompt("summary", "en")
        assert "Summary Phase Instructions" in content

    def test_load_spanish_prompt(self):
        """Test loading Spanish prompts."""
        # Load Spanish discovery prompt
        content = PromptLoader.load_prompt("discovery", "es")
        assert "Instrucciones de la Fase de Descubrimiento" in content
        assert "Rol" in content
        assert "Tarea" in content

        # Load Spanish reframing prompt
        content = PromptLoader.load_prompt("reframing", "es")
        assert "Instrucciones de la Fase de Reformulación" in content

        # Load Spanish summary prompt
        content = PromptLoader.load_prompt("summary", "es")
        assert "Instrucciones de la Fase de Resumen" in content

    def test_fallback_to_default_language(self):
        """Test fallback to default language when localized version not found."""
        # Try to load parser prompt in Spanish (doesn't exist)
        content = PromptLoader.load_prompt("parser", "es")
        # Should fall back to English version
        assert "Parser Phase Instructions" in content

    def test_prompt_not_found(self):
        """Test error when prompt doesn't exist."""
        with pytest.raises(FileNotFoundError) as exc_info:
            PromptLoader.load_prompt("nonexistent", "en")
        assert "not found" in str(exc_info.value)

    def test_get_available_languages(self):
        """Test getting available languages for prompts."""
        # Discovery should have both English and Spanish
        discovery_langs = PromptLoader.get_available_languages("discovery")
        assert "en" in discovery_langs
        assert "es" in discovery_langs

        # Parser should only have English
        parser_langs = PromptLoader.get_available_languages("parser")
        assert "en" in parser_langs
        assert "es" not in parser_langs

    def test_prompts_dir_exists(self):
        """Test that prompts directory exists."""
        assert PromptLoader.PROMPTS_DIR.exists()
        assert PromptLoader.PROMPTS_DIR.is_dir()

    def test_all_default_prompts_exist(self):
        """Test that all required default prompts exist."""
        required_prompts = ["discovery", "parser", "reframing", "summary"]
        for prompt_name in required_prompts:
            prompt_path = PromptLoader.PROMPTS_DIR / f"{prompt_name}.md"
            assert prompt_path.exists(), f"Missing prompt: {prompt_name}.md"

    def test_spanish_prompts_exist(self):
        """Test that Spanish translations exist for key prompts."""
        spanish_prompts = ["discovery_es", "reframing_es", "summary_es"]
        for prompt_name in spanish_prompts:
            prompt_path = PromptLoader.PROMPTS_DIR / f"{prompt_name}.md"
            assert prompt_path.exists(), f"Missing Spanish prompt: {prompt_name}.md"

    def test_prompt_content_structure(self):
        """Test that prompts have expected structure."""
        # Check English discovery prompt structure
        content = PromptLoader.load_prompt("discovery", "en")
        expected_sections = [
            "## Role",
            "## Task",
            "## Interaction Guidelines",
            "## Output Format",
            "## Crisis Protocol",
            "## Conversation Flow",
        ]
        for section in expected_sections:
            assert section in content, f"Missing section: {section}"

        # Check Spanish discovery prompt structure
        content_es = PromptLoader.load_prompt("discovery", "es")
        expected_sections_es = [
            "## Rol",
            "## Tarea",
            "## Pautas de Interacción",
            "## Formato de Salida",
            "## Protocolo de Crisis",
            "## Flujo de Conversación",
        ]
        for section in expected_sections_es:
            assert section in content_es, f"Missing Spanish section: {section}"

    def test_language_consistency_in_prompts(self):
        """Test that language-specific prompts mention language handling."""
        # English prompts should mention language handling
        discovery_en = PromptLoader.load_prompt("discovery", "en")
        assert "Language Handling" in discovery_en or "language" in discovery_en.lower()

        # Spanish prompts should mention language handling
        discovery_es = PromptLoader.load_prompt("discovery", "es")
        assert "Manejo del Idioma" in discovery_es or "idioma" in discovery_es.lower()

    @pytest.mark.parametrize(
        "prompt_name,language,expected_content",
        [
            ("discovery", "en", "automatic_thought"),
            ("discovery", "es", "automatic_thought"),  # JSON keys stay in English
            ("reframing", "en", "cognitive distortions"),
            ("reframing", "es", "distorsiones cognitivas"),
            ("summary", "en", "PDF"),
            ("summary", "es", "PDF"),
        ],
    )
    def test_prompt_contains_expected_content(
        self, prompt_name, language, expected_content
    ):
        """Test that prompts contain expected content."""
        content = PromptLoader.load_prompt(prompt_name, language)
        assert (
            expected_content in content or expected_content.lower() in content.lower()
        )
