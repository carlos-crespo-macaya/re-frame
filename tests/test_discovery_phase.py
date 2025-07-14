"""
Tests for the Discovery Phase Agent.

This module tests the discovery phase functionality including
thought extraction, emotion identification, and phase transitions.
"""

from unittest.mock import patch

from src.agents.discovery_agent import (
    create_discovery_agent,
    extract_thought_details,
    identify_emotions,
)
from src.agents.phase_manager import ConversationPhase, check_phase_transition
from src.knowledge.cbt_context import CBT_MODEL


class TestDiscoveryTools:
    """Test the discovery phase tool functions."""

    def test_extract_thought_details_returns_structured_response(self):
        """Test that extract_thought_details returns expected structure."""
        user_input = "I felt really anxious when my boss criticized my work in front of everyone."

        result = extract_thought_details(user_input)

        assert result["status"] == "success"
        assert "message" in result
        assert "components_to_explore" in result
        assert "situation" in result["components_to_explore"]
        assert "automatic_thoughts" in result["components_to_explore"]
        assert "emotions" in result["components_to_explore"]
        assert "next_steps" in result

    def test_identify_emotions_returns_guidance(self):
        """Test that identify_emotions provides emotion guidance."""
        emotion_desc = "I felt worried and scared about what might happen"

        result = identify_emotions(emotion_desc)

        assert result["status"] == "success"
        assert "message" in result
        assert "emotion_guidance" in result
        assert "validate_first" in result["emotion_guidance"]
        assert "explore_intensity" in result["emotion_guidance"]

    def test_phase_transition_tool_integration(self):
        """Test phase transition tool works for discovery to reframing."""
        result = check_phase_transition("reframing")

        assert result["status"] == "success"
        assert "reframing" in result["message"]
        assert result["target_phase"] == "reframing"


class TestDiscoveryAgent:
    """Test the discovery agent creation and configuration."""

    def test_create_discovery_agent_basic(self):
        """Test basic discovery agent creation."""
        agent = create_discovery_agent()

        assert agent.name == "DiscoveryAgent"
        assert agent.model == "gemini-2.0-flash"
        assert len(agent.tools) == 3

    def test_discovery_agent_has_correct_tools(self):
        """Test discovery agent has all required tools."""
        agent = create_discovery_agent()

        tool_names = [tool.__name__ for tool in agent.tools]
        assert "check_phase_transition" in tool_names
        assert "extract_thought_details" in tool_names
        assert "identify_emotions" in tool_names

    def test_discovery_agent_instruction_contains_key_elements(self):
        """Test agent instruction includes all necessary components."""
        agent = create_discovery_agent()

        instruction = agent.instruction

        # Check for CBT context
        assert "Cognitive Behavioral Therapy" in instruction
        assert "does not replace professional therapy" in instruction

        # Check for discovery phase specifics
        assert "DISCOVERY phase" in instruction
        assert "explore their thoughts and feelings" in instruction

        # Check for CBT model components
        for component in CBT_MODEL["components"]:
            assert component in instruction

        # Check for crisis detection
        assert "Crisis Detection" in instruction
        assert "self-harm" in instruction

    def test_discovery_agent_with_custom_model(self):
        """Test creating agent with different model."""
        agent = create_discovery_agent(model="gemini-1.5-pro")

        assert agent.model == "gemini-1.5-pro"


class TestDiscoveryScenarios:
    """Test complete discovery phase scenarios."""

    def test_discovery_flow_with_anxiety_scenario(self):
        """Test discovery phase handling anxiety-related thoughts."""
        # Simulate user sharing anxious thoughts
        user_input = "I can't stop thinking about the presentation tomorrow"

        # Tool should be able to extract thought details
        thought_result = extract_thought_details(user_input)
        assert thought_result["status"] == "success"

        # Tool should help identify anxiety
        emotion_result = identify_emotions("anxious and worried")
        assert emotion_result["status"] == "success"

    def test_discovery_handles_multiple_emotions(self):
        """Test discovery phase with complex emotions."""
        # Test emotion identification with multiple emotions
        complex_emotions = "I feel angry, sad, and disappointed all at once"

        result = identify_emotions(complex_emotions)
        assert result["status"] == "success"
        assert "validate_first" in result["emotion_guidance"]

    def test_discovery_crisis_instruction_present(self):
        """Test that crisis detection instructions are included."""
        agent = create_discovery_agent()

        instruction = agent.instruction
        crisis_keywords = ["crisis", "self-harm", "suicide", "safety"]

        assert any(keyword in instruction.lower() for keyword in crisis_keywords)

    def test_discovery_validates_before_exploring(self):
        """Test that validation comes before exploration in instructions."""
        agent = create_discovery_agent()

        instruction = agent.instruction

        # Check that validation is emphasized
        assert "Validate" in instruction
        assert "without judgment" in instruction
        assert "empathetic" in instruction


class TestDiscoveryIntegration:
    """Test discovery phase integration with overall system."""

    def test_discovery_phase_enum_exists(self):
        """Test that DISCOVERY is a valid conversation phase."""
        assert ConversationPhase.DISCOVERY
        assert ConversationPhase.DISCOVERY.value == "discovery"

    def test_discovery_follows_greeting_phase(self):
        """Test phase transition from greeting to discovery."""
        from src.agents.phase_manager import PHASE_TRANSITIONS

        # Check that discovery can follow greeting
        assert (
            ConversationPhase.DISCOVERY in PHASE_TRANSITIONS[ConversationPhase.GREETING]
        )

        # Check that discovery leads to reframing
        assert (
            ConversationPhase.REFRAMING
            in PHASE_TRANSITIONS[ConversationPhase.DISCOVERY]
        )

    @patch("src.agents.phase_manager.PhaseManager.get_phase_instruction")
    def test_discovery_uses_phase_manager_instruction(self, mock_get_instruction):
        """Test that discovery agent uses phase manager instructions."""
        mock_get_instruction.return_value = "Test discovery instruction"

        agent = create_discovery_agent()

        mock_get_instruction.assert_called_with(ConversationPhase.DISCOVERY)
        assert "Test discovery instruction" in agent.instruction
