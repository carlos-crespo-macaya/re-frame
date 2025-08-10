"""
Simplified tests for the Reframing Phase implementation.
Focus on testing the core functionality without complex async patterns.
"""

from src.agents.parser_agent import create_parser_agent
from src.agents.reframing_agent import (
    create_balanced_thought,
    create_reframing_agent,
    gather_evidence_for_thought,
)


class TestParserAgent:
    """Test the parser agent creation."""

    def test_parser_agent_creates(self):
        """Test parser agent can be created."""
        agent = create_parser_agent()
        assert agent.name == "ParserAgent"
        assert len(agent.tools) == 1

    def test_parser_agent_has_correct_instruction(self):
        """Test parser agent has correct instruction."""
        agent = create_parser_agent()
        assert "Parser Agent Role" in agent.instruction


class TestReframingAgent:
    """Test the reframing agent functionality."""

    def test_reframing_agent_creates(self):
        """Test that reframing agent can be created."""
        agent = create_reframing_agent()
        assert agent.name == "ReframingAgent"
        assert len(agent.tools) == 3  # All reframing tools (no design_micro_action)

    def test_evidence_gathering_for(self):
        """Test evidence gathering for supporting evidence."""
        result = gather_evidence_for_thought("I always mess things up", "for")

        assert result["status"] == "success"
        assert result["evidence_type"] == "for"
        assert len(result["suggested_prompts"]) > 0
        assert "What makes you think" in result["suggested_prompts"][0]

    def test_evidence_gathering_against(self):
        """Test evidence gathering for contradicting evidence."""
        result = gather_evidence_for_thought("I always mess things up", "against")

        assert result["status"] == "success"
        assert result["evidence_type"] == "against"
        assert any(
            "not completely true" in prompt for prompt in result["suggested_prompts"]
        )

    def test_balanced_thought_creation(self):
        """Test balanced thought creation guidance."""
        result = create_balanced_thought(
            original_thought="I never do anything right",
            evidence_for=["I made a mistake yesterday"],
            evidence_against=[
                "I completed my project on time",
                "My boss praised my work last week",
            ],
            distortions=["AO"],
        )

        assert result["status"] == "success"
        assert "criteria" in result
        assert "believable" in result["criteria"]
        assert len(result["instructions"]) > 0
        assert len(result["avoid"]) > 0


class TestAgentInstructions:
    """Test that agents have proper instructions."""

    def test_parser_agent_instructions(self):
        """Test parser agent has proper CBT context and instructions."""
        agent = create_parser_agent()

        # Check for key instruction elements
        assert "silent data extraction specialist" in agent.instruction
        assert "cognitive distortions" in agent.instruction
        assert "JSON" in agent.instruction
        assert "never interact with the user directly" in agent.instruction

    def test_reframing_agent_instructions(self):
        """Test reframing agent has proper CBT context and instructions."""
        agent = create_reframing_agent()

        # Check for key instruction elements
        assert "reframing specialist" in agent.instruction
        assert "Socratic questioning" in agent.instruction
        assert "balanced alternative thought" in agent.instruction
        assert "Crisis Protocol" in agent.instruction
