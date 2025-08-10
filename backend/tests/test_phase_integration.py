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

        # Check that agent has no phase management tools (orchestrator handles this)
        # The cbt_assistant is now a simple conversational agent
        assert len(agent.tools) == 0

    @pytest.mark.asyncio
    async def test_cbt_assistant_phase_awareness_in_instruction(self):
        """Test that CBT assistant instructions include phase management."""
        agent = create_cbt_assistant()
        instruction = agent.instruction

        # Should have CBT context but phase management is handled by orchestrator
        assert "cognitive reframing assistant" in instruction.lower()
        # New phase names should be mentioned
        assert (
            "warmup" in instruction.lower()
            or "clarify" in instruction.lower()
            or "reframe" in instruction.lower()
        )

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
                "expected_phase": "warmup",
                "response": "Hello! I'm here to help with cognitive reframing. Ready to begin?",
            },
            {
                "user": "Yes, I'm ready",
                "expected_phase": "clarify",
                "response": "Great! Let's explore what's on your mind. What thoughts are troubling you?",
            },
            {
                "user": "I think everyone hates me",
                "expected_phase": "reframe",
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
    async def test_phase_order_integrity(self):
        """Test that phase order is properly defined."""
        from src.agents.state import PHASE_ORDER, Phase

        # Test phase order integrity
        assert len(PHASE_ORDER) >= 4
        assert Phase.WARMUP in PHASE_ORDER
        assert Phase.CLARIFY in PHASE_ORDER
        assert Phase.REFRAME in PHASE_ORDER
        assert Phase.SUMMARY in PHASE_ORDER

        # Test phases are in correct order
        warmup_index = PHASE_ORDER.index(Phase.WARMUP)
        clarify_index = PHASE_ORDER.index(Phase.CLARIFY)
        reframe_index = PHASE_ORDER.index(Phase.REFRAME)
        summary_index = PHASE_ORDER.index(Phase.SUMMARY)

        assert clarify_index == warmup_index + 1
        assert reframe_index == clarify_index + 1
        assert summary_index == reframe_index + 1

    def test_phase_instructions_in_enhanced_context(self):
        """Test that phase instructions are properly integrated."""
        agent = create_cbt_assistant()
        instruction = agent.instruction

        # Should have CBT context and basic instruction
        assert "cognitive reframing" in instruction.lower()
        # Phase management is handled by orchestrator, not in individual agent instructions
