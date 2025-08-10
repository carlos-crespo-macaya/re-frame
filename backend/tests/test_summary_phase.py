"""
Tests for the Summary Phase Agent.

This module tests the summary generation functionality including
insight extraction, action item generation, and summary formatting.
"""

from src.agents.summary_agent import (
    create_summary_agent,
    extract_key_insights,
    format_session_summary,
)


class TestSummaryTools:
    """Test the summary phase tool functions."""

    def test_extract_key_insights(self):
        """Test key insight extraction from session data."""
        result = extract_key_insights(
            thought="I'm going to fail this presentation",
            distortions=["FORTUNE", "CATAST"],
            balanced_thought="I'm prepared and one presentation doesn't define me",
        )

        assert result["status"] == "success"
        assert len(result["insight_categories"]) == 4
        assert "Thinking patterns noticed" in result["insight_categories"]
        assert "guidance" in result

    # Action item test removed per no-action philosophy

    def test_format_session_summary(self):
        """Test formatting of complete session summary."""
        result = format_session_summary(
            situation="Upcoming work presentation",
            thought="I'm going to fail this presentation",
            emotions={"anxiety": 8, "fear": 7},
            distortions=["Fortune Telling", "Catastrophizing"],
            balanced_thought="I'm prepared and one presentation doesn't define me",
            insights=[
                "You tend to predict negative outcomes",
                "Your anxiety peaks with performance situations",
            ],
        )

        assert result["status"] == "success"
        assert "summary_sections" in result
        sections = result["summary_sections"]
        assert sections["situation_explored"] == "Upcoming work presentation"
        assert sections["original_thought"] == "I'm going to fail this presentation"
        assert sections["emotions_identified"]["anxiety"] == 8
        assert len(sections["thinking_patterns"]) == 2
        assert "formatting_guidelines" in result


class TestSummaryAgent:
    """Test the summary agent creation and configuration."""

    def test_create_summary_agent(self):
        """Test summary agent creation with proper configuration."""
        agent = create_summary_agent()

        assert agent is not None
        assert agent.name == "SummaryAgent"
        assert len(agent.tools) == 2
        tool_names = [tool.__name__ for tool in agent.tools]
        assert "extract_key_insights" in tool_names
        assert "format_session_summary" in tool_names

    def test_summary_agent_instruction_content(self):
        """Test that summary agent has comprehensive instructions."""
        agent = create_summary_agent()

        instruction = agent.instruction
        assert "SUMMARY Phase Instructions" in instruction
        assert "summary specialist" in instruction
        assert "What We Explored" in instruction
        assert "What We Discovered" in instruction
        assert "How It Feels Now" in instruction
        assert "Key Takeaways" in instruction

    def test_summary_agent_includes_base_context(self):
        """Test that summary agent includes base CBT context."""
        agent = create_summary_agent()

        instruction = agent.instruction
        assert "evidence-based CBT techniques" in instruction
        assert "not replace professional therapy" in instruction
        assert "collaborative" in instruction

    def test_summary_agent_closing_options(self):
        """Test that summary agent includes proper closing options."""
        agent = create_summary_agent()

        instruction = agent.instruction
        assert "Closing Options" in instruction
        assert "download" in instruction
        assert "Thank them" in instruction
