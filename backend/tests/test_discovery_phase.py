"""
Tests for the Clarify Phase Agent.

This module tests the clarify phase functionality including
thought extraction, emotion identification, and phase transitions.
"""

# from unittest.mock import patch  # No longer needed

from src.agents.discovery_agent import (
    create_discovery_agent,
    extract_thought_details,
    identify_emotions,
)
from src.agents.state import Phase
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
        """Test that tools work for clarify to reframe (phase transitions handled by orchestrator)."""
        # Phase transitions are now handled by the orchestrator
        # so we just verify the phase order is correct
        from src.agents.state import PHASE_ORDER

        clarify_index = PHASE_ORDER.index(Phase.CLARIFY)
        next_phase = PHASE_ORDER[clarify_index + 1]
        assert next_phase == Phase.REFRAME


class TestDiscoveryAgent:
    """Test the discovery agent creation and configuration."""

    def test_create_discovery_agent_basic(self):
        """Test basic discovery agent creation."""
        agent = create_discovery_agent()

        assert agent.name == "DiscoveryAgent"
        assert agent.model == "gemini-2.0-flash"
        assert len(agent.tools) == 2  # No phase transition tool

    def test_discovery_agent_has_correct_tools(self):
        """Test discovery agent has all required tools."""
        agent = create_discovery_agent()

        tool_names = [tool.__name__ for tool in agent.tools]
        # No phase transition tool in new architecture
        assert "extract_thought_details" in tool_names
        assert "identify_emotions" in tool_names

    def test_discovery_agent_instruction_contains_key_elements(self):
        """Test agent instruction includes all necessary components."""
        agent = create_discovery_agent()

        instruction = agent.instruction

        # Check for CBT context
        assert "Cognitive Behavioral Therapy" in instruction
        assert "does not replace professional therapy" in instruction

        # Check for clarify phase specifics
        assert "CLARIFY phase" in instruction or "clarify" in instruction.lower()
        assert (
            "explore their thoughts and feelings" in instruction
            or "explore your situation" in instruction
        )

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

    def test_clarify_phase_enum_exists(self):
        """Test that CLARIFY is a valid conversation phase."""
        assert Phase.CLARIFY
        assert Phase.CLARIFY.value == "clarify"

    def test_clarify_follows_warmup_phase(self):
        """Test phase transition from warmup to clarify."""
        from src.agents.state import PHASE_ORDER

        # Check that clarify follows warmup in phase order
        warmup_index = PHASE_ORDER.index(Phase.WARMUP)
        clarify_index = PHASE_ORDER.index(Phase.CLARIFY)
        assert clarify_index == warmup_index + 1

        # Check that clarify leads to reframe
        reframe_index = PHASE_ORDER.index(Phase.REFRAME)
        assert reframe_index == clarify_index + 1

    def test_discovery_uses_clarify_phase_instruction(self):
        """Test that discovery agent uses clarify phase instructions."""
        agent = create_discovery_agent()

        # Verify clarify phase instruction is included
        assert (
            "CLARIFY phase" in agent.instruction
            or "clarify" in agent.instruction.lower()
        )
