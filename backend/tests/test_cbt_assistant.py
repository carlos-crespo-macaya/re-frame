"""Tests for CBT Assistant Agent."""

from unittest.mock import MagicMock, patch

import pytest
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part

from src.agents.cbt_assistant import create_cbt_assistant
from src.knowledge.cbt_context import BASE_CBT_CONTEXT


class TestCBTAssistant:
    """Test the CBT Assistant agent."""

    def test_agent_has_name(self):
        """Test that agent has correct name."""
        agent = create_cbt_assistant()
        assert agent.name == "CBTAssistant"

    def test_agent_uses_gemini_model(self):
        """Test that agent uses correct Gemini model."""
        agent = create_cbt_assistant()
        assert agent.model == "gemini-2.0-flash"

    def test_agent_uses_custom_model(self):
        """Test that agent can use custom model."""
        agent = create_cbt_assistant(model="gemini-2.0-flash-live-001")
        assert agent.model == "gemini-2.0-flash-live-001"

    def test_agent_includes_base_context(self):
        """Test that agent instruction includes base CBT context."""
        agent = create_cbt_assistant()
        instruction_text = str(agent.instruction)
        assert BASE_CBT_CONTEXT in instruction_text
        assert "cognitive reframing" in instruction_text

    @pytest.mark.asyncio
    async def test_agent_responds_to_hello(self):
        """Test that agent responds to hello using runner."""
        # Create agent and runner
        agent = create_cbt_assistant()
        runner = InMemoryRunner(agent=agent)

        # Session info
        user_id = "test_user"
        session_id = "test_session"

        # Create session first
        await runner.session_service.create_session(
            app_name=runner.app_name,
            user_id=user_id,
            session_id=session_id,
        )

        # Create message
        message = Content(parts=[Part(text="Hello")], role="user")

        # Mock the runner's run_async to avoid actual API calls
        mock_event = MagicMock()
        mock_event.is_final_response.return_value = True
        mock_event.content = Content(
            parts=[Part(text="Hello! I'm here to help with cognitive reframing.")],
            role="model",
        )

        async def mock_run_async(*_args, **_kwargs):
            yield mock_event

        # Patch the runner's run_async method
        with patch.object(runner, "run_async", mock_run_async):
            # Run and check response
            response_text = None
            async for event in runner.run_async(
                user_id=user_id, session_id=session_id, new_message=message
            ):
                if event.is_final_response() and event.content and event.content.parts:
                    response_text = event.content.parts[0].text

            assert response_text is not None
            assert "help" in response_text.lower()


class TestCBTAssistantIntegration:
    """Integration tests for CBT Assistant."""

    @pytest.mark.asyncio
    async def test_agent_conversational_flow(self):
        """Test a basic conversational flow."""
        # Create agent and runner
        agent = create_cbt_assistant()
        runner = InMemoryRunner(agent=agent)

        # Session info
        user_id = "test_user"
        session_id = "test_conv"

        # Create session first
        await runner.session_service.create_session(
            app_name=runner.app_name,
            user_id=user_id,
            session_id=session_id,
        )

        # Test multiple exchanges
        test_messages = [
            "I'm feeling anxious about work",
            "I think everyone judges me",
            "Thank you for listening",
        ]

        # Mock responses for each message
        mock_responses = [
            "I understand you're feeling anxious about work. Let's explore that together.",
            "It sounds like you're experiencing mind reading. Let's examine this thought.",
            "You're welcome. Remember, I'm here to help you with cognitive reframing.",
        ]

        for i, msg in enumerate(test_messages):
            message = Content(parts=[Part(text=msg)], role="user")

            # Create mock event for this message
            mock_event = MagicMock()
            mock_event.is_final_response.return_value = True
            mock_event.content = Content(
                parts=[Part(text=mock_responses[i])], role="model"
            )

            # Create a closure to capture mock_event
            def create_mock_run_async(event):
                async def mock_run_async(*_args, **_kwargs):
                    yield event

                return mock_run_async

            # Patch the runner's run_async method
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

                assert response_text is not None
                assert len(response_text) > 10
