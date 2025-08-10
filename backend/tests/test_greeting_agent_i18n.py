"""Tests for greeting agent with internationalization support."""

from src.agents.greeting_agent import create_greeting_agent

# Language detection removed - using URL parameter only
# from src.agents.greeting_agent import detect_user_language


class TestGreetingAgentI18n:
    """Test suite for greeting agent language detection."""

    # REMOVED: test_detect_user_language_english
    # Language detection has been removed - using URL parameter only

    # REMOVED: test_detect_user_language_spanish
    # Language detection has been removed - using URL parameter only

    # REMOVED: test_detect_user_language_unsupported
    # Language detection has been removed - using URL parameter only

    # REMOVED: test_detect_user_language_empty
    # Language detection has been removed - using URL parameter only

    def test_greeting_agent_has_language_detection_tool(self):
        """Test that greeting agent has no tools (orchestrator handles transitions)."""
        # In new implementation, orchestrator handles all transitions
        agent = create_greeting_agent()
        # Agent should have no tools
        assert len(agent.tools) == 0
        # Phase transitions are deterministic, not tool-driven

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

    # REMOVED: test_various_greetings (parametrized)
    # Language detection has been removed - using URL parameter only

    # REMOVED: test_mixed_language_input
    # Language detection has been removed - using URL parameter only

    # REMOVED: test_language_detection_consistency
    # Language detection has been removed - using URL parameter only
