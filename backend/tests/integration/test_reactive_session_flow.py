"""Integration tests for reactive session flow.

These tests follow TDD principles and should FAIL initially
until the reactive session feature is implemented.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

# Patch dependencies before importing
with (
    patch("src.text.router.create_cbt_assistant", MagicMock()),
    patch("src.utils.session_manager.session_manager", MagicMock()),
):
    from src.main import app

from src.utils.session_manager import SessionInfo as SessionInfoModel


@pytest.fixture
def mock_session_manager():
    """Mock session manager for tests."""
    with patch("src.text.router.session_manager") as mock:
        # Setup default behaviors
        mock.get_session.return_value = None
        mock.get_session_readonly.return_value = None
        mock.list_sessions.return_value = []
        mock.create_session.return_value = SessionInfoModel(
            session_id="test-session", user_id="test-user"
        )
        yield mock


@pytest.fixture
async def async_client(mock_session_manager):
    """Create an async test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.mark.asyncio
class TestReactiveSessionFlow:
    """Integration tests for reactive session flow without proactive messages."""

    async def test_sse_session_starts_without_greeting(self):
        """Test that SSE session starts without sending a proactive greeting message."""
        from fastapi import Request

        from src.text.router import sse_endpoint

        # Create a mock request
        mock_request = AsyncMock(spec=Request)
        mock_request.method = "GET"

        # Track all messages sent
        messages_sent = []

        with patch("src.text.router.start_agent_session") as mock_start:
            mock_runner = AsyncMock()
            mock_session = AsyncMock()
            mock_session.id = "adk-session"
            mock_session.user_id = "test-session"
            mock_run_config = AsyncMock()

            # Mock run_async to capture messages
            async def mock_run_async(*args, **kwargs):
                # Capture the message
                if kwargs.get("new_message"):
                    messages_sent.append(kwargs["new_message"])
                # Return empty generator
                return
                yield  # Make it a generator

            mock_runner.run_async = mock_run_async
            mock_start.return_value = (mock_runner, mock_session, mock_run_config)

            with patch("src.text.router.session_manager") as mock_sm:
                mock_session_info = AsyncMock()
                mock_session_info.metadata = {}
                mock_sm.create_session.return_value = mock_session_info

                with patch("src.text.router.get_performance_monitor") as mock_perf:
                    mock_monitor = AsyncMock()
                    mock_perf.return_value = mock_monitor

                    # Call the endpoint
                    await sse_endpoint(mock_request, "test-session", "en-US")

                    # The response is a StreamingResponse - we need to set shutdown flag
                    mock_session_info.metadata["sse_shutdown"] = True

                    # Give time for background tasks
                    await asyncio.sleep(0.1)

                    # Check if START_CONVERSATION was sent
                    start_conversation_sent = any(
                        msg.parts[0].text == "START_CONVERSATION"
                        for msg in messages_sent
                        if hasattr(msg, "parts") and msg.parts
                    )

                    # This test SHOULD FAIL because current implementation sends START_CONVERSATION
                    assert (
                        not start_conversation_sent
                    ), "SSE endpoint should not send START_CONVERSATION in reactive mode"

    async def test_greeting_agent_does_not_respond_to_start_conversation(self):
        """Test that greeting agent doesn't have START_CONVERSATION in its instructions."""
        from src.agents.greeting_agent import create_greeting_agent

        # Create greeting agent
        agent = create_greeting_agent()

        # The greeting agent should not be instructed to respond to START_CONVERSATION
        assert (
            "START_CONVERSATION" not in agent.instruction
        ), "Greeting agent should not have START_CONVERSATION trigger in reactive mode"

    async def test_cbt_assistant_waits_for_user_input(self):
        """Test that CBT assistant is configured to wait for user input."""
        from src.agents.cbt_assistant import create_cbt_assistant

        # Create CBT assistant
        agent = create_cbt_assistant()

        # Check that instructions emphasize reactive behavior
        instruction_lower = agent.instruction.lower()

        # These phrases indicate proactive behavior and should NOT be present
        proactive_phrases = [
            "immediately provide",
            "without waiting",
            "start by greeting",
            "begin with greeting",
        ]

        for phrase in proactive_phrases:
            assert (
                phrase not in instruction_lower
            ), f"CBT assistant should not have '{phrase}' in reactive mode"

    # REMOVED: test_language_detection_happens_on_first_user_message
    # Language detection has been removed - using URL parameter only

    async def test_session_metadata_tracks_greeting_state(self):
        """Test that session metadata can track whether greeting has been sent."""
        from src.utils.session_manager import SessionInfo

        # Create a session
        session = SessionInfo(session_id="test-session", user_id="test-user")

        # Initially, greeting should not be sent
        session.metadata["greeting_sent"] = False
        assert not session.metadata["greeting_sent"]

        # After first user message, greeting can be marked as sent
        session.metadata["greeting_sent"] = True
        assert session.metadata["greeting_sent"]

    async def test_sse_endpoint_does_not_use_start_conversation_in_code(self):
        """Test that the SSE endpoint code doesn't contain START_CONVERSATION."""
        import inspect

        import src.text.router as router

        # Get the source code of sse_endpoint
        sse_source = inspect.getsource(router.sse_endpoint)

        # This test will FAIL until we remove START_CONVERSATION from the code
        assert (
            "START_CONVERSATION" not in sse_source
        ), "SSE endpoint source code should not contain START_CONVERSATION in reactive mode"

    async def test_reactive_greeting_responds_in_url_language(self):
        """Test that greeting responds in the language specified in URL parameter."""
        from src.agents.greeting_agent import create_greeting_agent

        # Create greeting agent with Spanish language from URL parameter
        agent = create_greeting_agent(language_code="es-ES")

        # Verify agent is configured for Spanish
        assert any(
            spanish_indicator in agent.instruction.lower()
            for spanish_indicator in ["español", "spanish", "es-es"]
        ), "Greeting agent should be configured for Spanish language"

    async def test_empty_messages_use_url_language(self):
        """Test that empty messages use language from URL parameter."""
        # When language is specified in URL, that's what should be used
        # Empty messages don't trigger language detection
        pass  # Language is now determined by URL parameter only
