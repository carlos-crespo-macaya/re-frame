"""Tests for reactive behavior in text router - TDD approach.

These tests verify the reactive SSE endpoint behavior where:
1. No greeting is sent on initial connection
2. Language detection overrides URL parameter for text responses
3. First message triggers appropriate greeting response
4. Session state correctly tracks greeting status

Note: These tests are written to FAIL initially (RED phase of TDD).
"""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
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
def client(mock_session_manager):
    """Create a test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
async def async_client(mock_session_manager):
    """Create an async test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


class TestReactiveSSEBehavior:
    """Test reactive SSE endpoint behavior."""

    @pytest.mark.asyncio
    async def test_sse_no_greeting_on_connect(self, async_client):
        """Test that SSE endpoint doesn't send greeting on initial connection."""
        with patch("src.text.router.start_agent_session") as mock_start:
            # Mock the agent session setup
            mock_runner = AsyncMock()
            mock_session = AsyncMock()
            mock_session.id = "adk-session-123"
            mock_session.user_id = "test-session-123"
            mock_run_config = {}
            mock_start.return_value = (mock_runner, mock_session, mock_run_config)

            # Mock runner.run_async to NOT be called on connection
            mock_runner.run_async = AsyncMock()

            # Mock performance monitor
            with patch("src.text.router.get_performance_monitor") as mock_perf:
                mock_monitor = AsyncMock()
                mock_perf.return_value = mock_monitor

                # Connect to SSE endpoint
                async with async_client.stream(
                    "GET", "/api/events/test-session-123"
                ) as response:
                    assert response.status_code == 200

                    # Read initial events with timeout
                    events = []
                    try:
                        async with asyncio.timeout(2):  # 2 second timeout
                            async for line in response.aiter_lines():
                                if line.startswith("data: "):
                                    data = json.loads(line[6:])
                                    events.append(data)

                                    # Stop after we get enough events to verify
                                    if len(events) >= 3 or any(
                                        e.get("type") == "content" for e in events
                                    ):
                                        break
                    except TimeoutError:
                        pass  # Expected - no more events after initial ones

                    # Should have connected event
                    assert events[0]["type"] == "connected"

                    # Check for content events (greeting)
                    content_events = [e for e in events if e.get("type") == "content"]

                    # EXPECTED TO FAIL: Currently sends greeting on connect
                    # This assertion will fail because the current implementation
                    # sends a greeting immediately on connection
                    assert (
                        len(content_events) == 0
                    ), f"No greeting should be sent on connection, but got {len(content_events)} content events"

                    # EXPECTED TO FAIL: run_async is called with START_CONVERSATION
                    # This will fail because current implementation calls it
                    mock_runner.run_async.assert_not_called()

    @pytest.mark.asyncio
    async def test_sse_first_message_triggers_greeting(
        self, async_client, mock_session_manager
    ):
        """Test that first user message triggers greeting response."""
        with patch("src.text.router.start_agent_session") as mock_start:
            # Mock the agent session setup
            mock_runner = AsyncMock()
            mock_session = AsyncMock()
            mock_session.id = "adk-session-123"
            mock_session.user_id = "test-session-123"
            mock_run_config = {}
            mock_start.return_value = (mock_runner, mock_session, mock_run_config)

            # Mock session retrieval for send_message
            mock_session_info = AsyncMock()
            mock_session_info.metadata = {
                "runner": mock_runner,
                "adk_session": mock_session,
                "run_config": mock_run_config,
                "message_queue": AsyncMock(),
                "language": "en-US",
                "greeting_sent": False,  # Track greeting state
            }
            mock_session_manager.get_session.return_value = mock_session_info
            mock_session_manager.create_session.return_value = mock_session_info

            # Mock runner.run_async to return greeting on first call
            greeting_events = [
                MagicMock(
                    content=MagicMock(
                        parts=[MagicMock(text="Hello! Welcome to CBT Assistant.")]
                    )
                )
            ]
            mock_runner.run_async.return_value = AsyncMock()
            mock_runner.run_async.return_value.__aiter__.return_value = iter(
                greeting_events
            )

            # Connect to SSE endpoint
            async with async_client.stream(
                "GET", "/api/events/test-session-123"
            ) as sse_response:
                assert sse_response.status_code == 200

                # Send first message
                send_response = await async_client.post(
                    "/api/send/test-session-123",
                    json={"data": "Hello", "mime_type": "text/plain"},
                )
                assert send_response.status_code == 200

                # Verify greeting was sent (would be called with special greeting trigger)
                assert mock_runner.run_async.call_count >= 1

                # Check that greeting_sent flag is updated
                assert mock_session_info.metadata.get("greeting_sent") is True

    @pytest.mark.asyncio
    async def test_language_detection_overrides_url_parameter(
        self, async_client, mock_session_manager
    ):
        """Test that detected language from first message overrides URL parameter."""
        with patch("src.text.router.start_agent_session") as mock_start:
            # Mock the agent session setup with Spanish from URL
            mock_runner = AsyncMock()
            mock_session = AsyncMock()
            mock_session.id = "adk-session-123"
            mock_session.user_id = "test-session-123"
            mock_run_config = {}
            mock_start.return_value = (mock_runner, mock_session, mock_run_config)

            # Mock session for send_message
            mock_session_info = AsyncMock()
            mock_session_info.metadata = {
                "runner": mock_runner,
                "adk_session": mock_session,
                "run_config": mock_run_config,
                "message_queue": AsyncMock(),
                "language": "es-ES",  # Initial language from URL
                "greeting_sent": False,
            }
            mock_session_manager.get_session.return_value = mock_session_info
            mock_session_manager.create_session.return_value = mock_session_info

            # Mock language detection
            with patch("src.text.router.detect_language") as mock_detect:
                mock_detect.return_value = ("en", 0.95)  # Detect English

                # Connect with Spanish in URL
                async with async_client.stream(
                    "GET", "/api/events/test-session-123?language=es-ES"
                ) as response:
                    assert response.status_code == 200

                    # Send English message
                    send_response = await async_client.post(
                        "/api/send/test-session-123",
                        json={
                            "data": "Hello, I need help with my anxiety",
                            "mime_type": "text/plain",
                        },
                    )
                    assert send_response.status_code == 200

                    # Language should be updated to English
                    assert mock_session_info.metadata["language"] == "en-US"

                    # Verify language detection was called
                    mock_detect.assert_called_once_with(
                        "Hello, I need help with my anxiety"
                    )

    @pytest.mark.asyncio
    async def test_session_tracks_greeting_state(
        self, async_client, mock_session_manager
    ):
        """Test that session correctly tracks whether greeting has been sent."""
        with patch("src.text.router.start_agent_session") as mock_start:
            # Mock the agent session setup
            mock_runner = AsyncMock()
            mock_session = AsyncMock()
            mock_session.id = "adk-session-123"
            mock_session.user_id = "test-session-123"
            mock_run_config = {}
            mock_start.return_value = (mock_runner, mock_session, mock_run_config)

            # Mock session creation
            mock_session_info = MagicMock()
            mock_session_info.metadata = {}
            mock_session_manager.create_session.return_value = mock_session_info

            # Connect to SSE endpoint
            async with async_client.stream(
                "GET", "/api/events/test-session-123"
            ) as response:
                assert response.status_code == 200

                # Check initial state - no greeting sent
                assert mock_session_info.metadata.get("greeting_sent", False) is False

            # For subsequent message handling
            mock_session_info.metadata.update(
                {
                    "runner": mock_runner,
                    "adk_session": mock_session,
                    "run_config": mock_run_config,
                    "message_queue": AsyncMock(),
                    "language": "en-US",
                }
            )
            mock_session_manager.get_session.return_value = mock_session_info

            # Send first message
            await async_client.post(
                "/api/send/test-session-123",
                json={"data": "Hello", "mime_type": "text/plain"},
            )

            # After first message, greeting_sent should be True
            assert mock_session_info.metadata.get("greeting_sent") is True

            # Send second message
            await async_client.post(
                "/api/send/test-session-123",
                json={"data": "I have another question", "mime_type": "text/plain"},
            )

            # greeting_sent should remain True
            assert mock_session_info.metadata.get("greeting_sent") is True

    @pytest.mark.asyncio
    async def test_greeting_uses_detected_language(
        self, async_client, mock_session_manager
    ):
        """Test that greeting is sent in the detected language, not URL parameter."""
        with patch("src.text.router.start_agent_session") as mock_start:
            # Mock the agent session setup
            mock_runner = AsyncMock()
            mock_session = AsyncMock()
            mock_session.id = "adk-session-123"
            mock_session.user_id = "test-session-123"
            mock_run_config = {}
            mock_start.return_value = (mock_runner, mock_session, mock_run_config)

            # Mock session
            mock_session_info = AsyncMock()
            mock_message_queue = asyncio.Queue()
            mock_session_info.metadata = {
                "runner": mock_runner,
                "adk_session": mock_session,
                "run_config": mock_run_config,
                "message_queue": mock_message_queue,
                "language": "en-US",  # Initial language from URL
                "greeting_sent": False,
            }
            mock_session_manager.get_session.return_value = mock_session_info
            mock_session_manager.create_session.return_value = mock_session_info

            # Mock language detection to Spanish
            with patch("src.text.router.detect_language") as mock_detect:
                mock_detect.return_value = ("es", 0.98)

                # Mock create_cbt_assistant to verify language parameter
                with patch(
                    "src.text.router.create_cbt_assistant"
                ) as mock_create_assistant:
                    mock_create_assistant.return_value = MagicMock()

                    # Connect with English in URL
                    async with async_client.stream(
                        "GET", "/api/events/test-session-123?language=en-US"
                    ) as response:
                        assert response.status_code == 200

                        # Send Spanish message
                        send_response = await async_client.post(
                            "/api/send/test-session-123",
                            json={
                                "data": "Hola, necesito ayuda con mi ansiedad",
                                "mime_type": "text/plain",
                            },
                        )
                        assert send_response.status_code == 200

                        # Verify assistant was recreated with Spanish
                        # This would happen when greeting is triggered with new language
                        assert mock_session_info.metadata["language"] == "es-ES"

    @pytest.mark.asyncio
    async def test_no_greeting_on_reconnect(self, async_client, mock_session_manager):
        """Test that greeting is not sent when reconnecting to existing session."""
        session_id = "test-session-reconnect"

        # Mock existing session with greeting already sent
        existing_session = MagicMock()
        existing_session.metadata = {
            "greeting_sent": True,
            "language": "en-US",
        }
        mock_session_manager.get_session_readonly.return_value = existing_session

        with patch("src.text.router.start_agent_session") as mock_start:
            # Mock the agent session setup
            mock_runner = AsyncMock()
            mock_session = AsyncMock()
            mock_session.id = f"adk-{session_id}"
            mock_session.user_id = session_id
            mock_run_config = {}
            mock_start.return_value = (mock_runner, mock_session, mock_run_config)

            # Mock runner.run_async
            mock_runner.run_async = AsyncMock()

            # Connect to SSE endpoint
            async with async_client.stream(
                "GET", f"/api/events/{session_id}"
            ) as response:
                assert response.status_code == 200

                # Collect initial events
                events = []
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = json.loads(line[6:])
                        events.append(data)
                        if len(events) >= 2:  # connected + heartbeat
                            break

                # Should not send greeting on reconnect
                mock_runner.run_async.assert_not_called()

                # No content events should be present
                content_events = [e for e in events if e.get("type") == "content"]
                assert len(content_events) == 0

    @pytest.mark.asyncio
    async def test_language_detection_only_on_first_message(
        self, async_client, mock_session_manager
    ):
        """Test that language detection only happens on the first user message."""
        with patch("src.text.router.start_agent_session") as mock_start:
            # Mock the agent session setup
            mock_runner = AsyncMock()
            mock_session = AsyncMock()
            mock_session.id = "adk-session-123"
            mock_session.user_id = "test-session-123"
            mock_run_config = {}
            mock_start.return_value = (mock_runner, mock_session, mock_run_config)

            # Mock session
            mock_session_info = MagicMock()
            mock_session_info.metadata = {
                "runner": mock_runner,
                "adk_session": mock_session,
                "run_config": mock_run_config,
                "message_queue": AsyncMock(),
                "language": "en-US",
                "greeting_sent": False,
            }
            mock_session_manager.get_session.return_value = mock_session_info
            mock_session_manager.create_session.return_value = mock_session_info

            # Mock language detection
            with patch("src.text.router.detect_language") as mock_detect:
                mock_detect.return_value = ("en", 0.95)

                # Connect
                async with async_client.stream(
                    "GET", "/api/events/test-session-123"
                ) as response:
                    assert response.status_code == 200

                    # First message - should detect language
                    await async_client.post(
                        "/api/send/test-session-123",
                        json={"data": "Hello, I need help", "mime_type": "text/plain"},
                    )
                    assert mock_detect.call_count == 1
                    mock_session_info.metadata["greeting_sent"] = True

                    # Second message - should NOT detect language
                    await async_client.post(
                        "/api/send/test-session-123",
                        json={
                            "data": "Hola, tengo otra pregunta",
                            "mime_type": "text/plain",
                        },
                    )
                    assert mock_detect.call_count == 1  # Still 1, not called again

    @pytest.mark.asyncio
    async def test_empty_message_does_not_trigger_greeting(
        self, async_client, mock_session_manager
    ):
        """Test that empty messages don't trigger greeting."""
        with patch("src.text.router.start_agent_session") as mock_start:
            # Mock the agent session setup
            mock_runner = AsyncMock()
            mock_session = AsyncMock()
            mock_session.id = "adk-session-123"
            mock_session.user_id = "test-session-123"
            mock_run_config = {}
            mock_start.return_value = (mock_runner, mock_session, mock_run_config)

            # Mock session
            mock_session_info = MagicMock()
            mock_session_info.metadata = {
                "runner": mock_runner,
                "adk_session": mock_session,
                "run_config": mock_run_config,
                "message_queue": AsyncMock(),
                "language": "en-US",
                "greeting_sent": False,
            }
            mock_session_manager.get_session.return_value = mock_session_info
            mock_session_manager.create_session.return_value = mock_session_info

            # Connect
            async with async_client.stream(
                "GET", "/api/events/test-session-123"
            ) as response:
                assert response.status_code == 200

                # Send empty message
                await async_client.post(
                    "/api/send/test-session-123",
                    json={"data": "", "mime_type": "text/plain"},
                )

                # Greeting should not be sent for empty message
                assert mock_session_info.metadata.get("greeting_sent") is False
