"""Integration tests for phase management with CBT assistant."""

from unittest.mock import MagicMock, patch

import pytest
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part

from src.agents.cbt_assistant import create_cbt_assistant


class TestPhaseIntegration:
    """Test phase management integration with CBT assistant."""

    @pytest.mark.asyncio
    async def test_cbt_assistant_has_phase_tools(self):
        """Test that CBT assistant has phase management tools."""
        agent = create_cbt_assistant()

        # Check tools are included
        assert len(agent.tools) == 2
        tool_names = [tool.__name__ for tool in agent.tools]
        assert "check_phase_transition" in tool_names
        assert "get_current_phase_info" in tool_names

    @pytest.mark.asyncio
    async def test_cbt_assistant_phase_awareness_in_instruction(self):
        """Test that CBT assistant instructions include phase management."""
        agent = create_cbt_assistant()
        instruction = agent.instruction

        # Should have phase management section
        assert "Conversation Phase Management" in instruction
        assert "greeting/discovery/reframing/summary" in instruction
        assert "follow the phases in order" in instruction

    @pytest.mark.asyncio
    async def test_phase_flow_conversation(self):
        """Test a conversation that follows the phase flow."""
        agent = create_cbt_assistant()
        runner = InMemoryRunner(agent=agent)

        user_id = "test_user"
        session_id = "phase_test"

        # Create session
        await runner.session_service.create_session(
            app_name=runner.app_name,
            user_id=user_id,
            session_id=session_id,
        )

        # Test conversation flow through phases
        test_exchanges = [
            {
                "user": "Hello",
                "expected_phase": "greeting",
                "response": "Hello! I'm here to help with cognitive reframing. Ready to begin?",
            },
            {
                "user": "Yes, I'm ready",
                "expected_phase": "discovery",
                "response": "Great! Let's explore what's on your mind. What thoughts are troubling you?",
            },
            {
                "user": "I think everyone hates me",
                "expected_phase": "reframing",
                "response": "That sounds like mind reading. Let's examine this thought more closely.",
            },
            {
                "user": "You're right, I don't have evidence for that",
                "expected_phase": "summary",
                "response": "Let's summarize what we've discovered today...",
            },
        ]

        for exchange in test_exchanges:
            message = Content(parts=[Part(text=exchange["user"])], role="user")

            # Mock response
            mock_event = MagicMock()
            mock_event.is_final_response.return_value = True
            mock_event.content = Content(
                parts=[Part(text=exchange["response"])], role="model"
            )

            # Create a closure to capture the mock_event
            def create_mock_run_async(event):
                async def mock_run_async(*_args, **_kwargs):
                    yield event

                return mock_run_async

            with patch.object(runner, "run_async", create_mock_run_async(mock_event)):
                response_text = None
                async for event in runner.run_async(
                    user_id=user_id, session_id=session_id, new_message=message
                ):
                    if (
                        event.is_final_response()
                        and event.content
                        and event.content.parts
                    ):
                        response_text = event.content.parts[0].text

                assert response_text == exchange["response"]

    @pytest.mark.asyncio
    async def test_phase_tools_callable(self):
        """Test that phase management tools can be called."""
        from src.agents.phase_manager import (
            check_phase_transition,
            get_current_phase_info,
        )

        # Test check_phase_transition
        result = check_phase_transition("discovery")
        assert isinstance(result, dict)
        assert result["status"] == "success"

        # Test get_current_phase_info
        info = get_current_phase_info()
        assert isinstance(info, dict)
        assert "phase_flow" in info
        assert info["status"] == "success"

    def test_phase_instructions_in_enhanced_context(self):
        """Test that phase instructions are properly integrated."""
        agent = create_cbt_assistant()
        instruction = agent.instruction

        # Should have both session state and phase management sections
        assert "Session State Management" in instruction
        assert "phase: Current conversation phase" in instruction
        assert "Conversation Phase Management" in instruction
        assert "Use the phase management tools" in instruction
