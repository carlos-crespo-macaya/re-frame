"""Tests for greeting agent with internationalization support."""

import pytest

from src.agents.greeting_agent import create_greeting_agent, detect_user_language


class TestGreetingAgentI18n:
    """Test suite for greeting agent language detection."""

    def test_detect_user_language_english(self):
        """Test language detection for English input."""
        result = detect_user_language("Hello, I'm feeling anxious today")
        assert result["language_code"] == "en"
        assert result["language_name"] == "English"
        assert result["supported"] is True

    def test_detect_user_language_spanish(self):
        """Test language detection for Spanish input."""
        result = detect_user_language("Hola, me siento ansioso hoy")
        assert result["language_code"] == "es"
        assert result["language_name"] == "Spanish"
        assert result["supported"] is True

    def test_detect_user_language_unsupported(self):
        """Test language detection for unsupported language."""
        # Japanese input (unsupported)
        result = detect_user_language("こんにちは、今日は不安を感じています")
        assert result["language_code"] == "en"  # Falls back to English
        assert result["language_name"] == "English"
        assert result["supported"] is True

    def test_detect_user_language_empty(self):
        """Test language detection for empty input."""
        result = detect_user_language("")
        assert result["language_code"] == "en"
        assert result["language_name"] == "English"
        assert result["supported"] is True

    def test_greeting_agent_has_language_detection_tool(self):
        """Test that greeting agent has language detection tool."""
        # In reactive implementation, language detection happens in router, not agent
        agent = create_greeting_agent()
        tool_names = [tool.__name__ for tool in agent.tools]
        # Greeting agent should only have phase transition tool
        assert "check_phase_transition" in tool_names
        assert "detect_user_language" not in tool_names

    def test_greeting_agent_instruction_mentions_language(self):
        """Test that greeting agent instructions mention language detection."""
        agent = create_greeting_agent()
        assert "language" in agent.instruction.lower()
        # In reactive implementation, agent doesn't detect language itself
        # but should still be aware of the user's language
        assert (
            "pre-selected language" in agent.instruction.lower()
            or "specified language" in agent.instruction.lower()
        )

    @pytest.mark.parametrize(
        "user_input,expected_code",
        [
            ("Hi there!", "en"),
            ("¡Hola, necesito ayuda!", "es"),
            ("Good morning, I need help", "en"),
            ("Buenos días, necesito ayuda", "es"),
            ("I'm struggling with negative thoughts", "en"),
            ("Estoy luchando con pensamientos negativos", "es"),
        ],
    )
    def test_various_greetings(self, user_input, expected_code):
        """Test language detection for various greeting phrases."""
        result = detect_user_language(user_input)
        assert result["language_code"] == expected_code

    def test_mixed_language_input(self):
        """Test handling of mixed language input."""
        # English with Spanish word
        result = detect_user_language("Hello, I'm feeling muy anxious")
        # Should detect the dominant language
        assert result["language_code"] in ["en", "es"]
        assert result["supported"] is True

    def test_language_detection_consistency(self):
        """Test that language detection is consistent for similar inputs."""
        inputs = [
            "I feel anxious",
            "I'm feeling anxious",
            "I am anxious",
            "Feeling anxious today",
        ]
        results = [detect_user_language(inp)["language_code"] for inp in inputs]
        # All should detect as English
        assert all(code == "en" for code in results)

        spanish_inputs = [
            "Me siento ansioso por la presentación",
            "Estoy ansioso por el trabajo",
            "Me encuentro ansioso por todo esto",
            "Muy ansioso hoy por la situación",
        ]
        spanish_results = [
            detect_user_language(inp)["language_code"] for inp in spanish_inputs
        ]
        # All should detect as Spanish
        assert all(code == "es" for code in spanish_results)
