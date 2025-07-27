"""Tests for reactive behavior in text router.

These tests verify the reactive SSE endpoint behavior where:
1. No greeting is sent on initial connection
2. Language is determined by URL parameter only (no detection)
3. First message triggers appropriate greeting response
4. Session state correctly tracks greeting status
"""

import asyncio
import json
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


class TestReactiveSSEBehavior:
    """Test reactive SSE endpoint behavior using proper SSE test infrastructure."""

    @pytest.mark.skip(
        reason="SSE streaming tests are flaky - use test_sse_unit.py instead"
    )
    @pytest.mark.asyncio
    async def test_sse_no_greeting_on_connect(self, mock_session_manager):
        """Test that SSE endpoint doesn't send greeting on initial connection."""
        with patch(
            "src.text.router.start_agent_session", new_callable=AsyncMock
        ) as mock_start:
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

                # Use real AsyncClient
                async with AsyncClient(
                    transport=ASGITransport(app=app), base_url="http://test"
                ) as client:
                    # Start SSE connection and collect initial messages
                    messages = []
                    async with client.stream(
                        "GET", "/api/events/test-session-123"
                    ) as response:
                        # Collect up to 2 messages with timeout
                        start_time = asyncio.get_event_loop().time()
                        async for line in response.aiter_lines():
                            if asyncio.get_event_loop().time() - start_time > 2.0:
                                break
                            if line.startswith("data: "):
                                try:
                                    data = json.loads(line[6:])
                                    messages.append(data)
                                    if len(messages) >= 2:
                                        break
                                except json.JSONDecodeError:
                                    continue

                    # Should have connected event
                    assert len(messages) >= 1
                    assert messages[0]["type"] == "connected"

                    # Check for content events (greeting)
                    content_messages = [
                        msg for msg in messages if msg.get("type") == "content"
                    ]

                    # No greeting should be sent on connection
                    assert (
                        len(content_messages) == 0
                    ), f"No greeting should be sent on connection, but got {len(content_messages)} content events"

                    # run_async should not be called
                    mock_runner.run_async.assert_not_called()

    @pytest.mark.skip(
        reason="SSE streaming tests are flaky - use test_sse_unit.py instead"
    )
    @pytest.mark.asyncio
    async def test_sse_first_message_triggers_greeting(self, mock_session_manager):
        """Test that first user message triggers greeting response."""
        with patch(
            "src.text.router.start_agent_session", new_callable=AsyncMock
        ) as mock_start:
            # Mock the agent session setup
            mock_runner = AsyncMock()
            mock_session = AsyncMock()
            mock_session.id = "adk-session-123"
            mock_session.user_id = "test-session-123"
            mock_run_config = {}
            mock_start.return_value = (mock_runner, mock_session, mock_run_config)

            # Mock session retrieval for send_message
            mock_session_info = MagicMock()
            mock_session_info.metadata = {
                "runner": mock_runner,
                "adk_session": mock_session,
                "run_config": mock_run_config,
                "message_queue": asyncio.Queue(),
                "language": "en-US",
                "greeting_sent": False,
            }
            mock_session_manager.get_session.return_value = mock_session_info
            mock_session_manager.create_session.return_value = mock_session_info

            # Mock runner.run_async to return greeting
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

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                # Start SSE connection in background
                session_id = "test-session-123"

                async def stream_sse():
                    async with client.stream(
                        "GET", f"/api/events/{session_id}"
                    ) as response:
                        async for _line in response.aiter_lines():
                            pass  # Just consume the stream

                sse_task = asyncio.create_task(stream_sse())

                # Give connection time to establish
                await asyncio.sleep(0.1)

                # Send first message
                response = await client.post(
                    f"/api/send/{session_id}",
                    json={"data": "Hello", "mime_type": "text/plain"},
                )
                assert response.status_code == 200

                # Give time for greeting to be processed
                await asyncio.sleep(0.1)

                # Verify greeting was sent
                assert mock_runner.run_async.call_count >= 1

                # Check that greeting_sent flag is updated
                assert mock_session_info.metadata.get("greeting_sent") is True

                # Cancel SSE task
                sse_task.cancel()
                try:
                    await sse_task
                except asyncio.CancelledError:
                    pass

    @pytest.mark.skip(
        reason="SSE streaming tests are flaky - use test_sse_unit.py instead"
    )
    @pytest.mark.asyncio
    async def test_session_tracks_greeting_state(self, mock_session_manager):
        """Test that session correctly tracks whether greeting has been sent."""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            session_id = "test-session-state"

            # Mock session for tracking
            mock_session_info = MagicMock()
            mock_session_info.metadata = {}
            mock_session_manager.create_session.return_value = mock_session_info

            # Start SSE connection in background
            async def stream_sse():
                async with client.stream(
                    "GET", f"/api/events/{session_id}"
                ) as response:
                    async for _line in response.aiter_lines():
                        pass  # Just consume the stream

            sse_task = asyncio.create_task(stream_sse())
            await asyncio.sleep(0.1)  # Let connection establish

            # Check initial state - no greeting sent
            assert mock_session_info.metadata.get("greeting_sent", False) is False

            # Update session metadata for message handling
            mock_session_info.metadata.update(
                {
                    "runner": AsyncMock(),
                    "adk_session": AsyncMock(),
                    "run_config": {},
                    "message_queue": asyncio.Queue(),
                    "language": "en-US",
                }
            )
            mock_session_manager.get_session.return_value = mock_session_info

            # Send first message
            response = await client.post(
                f"/api/send/{session_id}",
                json={"data": "Hello", "mime_type": "text/plain"},
            )
            assert response.status_code == 200
            await asyncio.sleep(0.1)  # Give time for processing

            # After first message, greeting_sent should be True
            assert mock_session_info.metadata.get("greeting_sent") is True

            # Send second message
            response = await client.post(
                f"/api/send/{session_id}",
                json={"data": "I have another question", "mime_type": "text/plain"},
            )
            assert response.status_code == 200
            await asyncio.sleep(0.1)  # Give time for processing

            # greeting_sent should remain True
            assert mock_session_info.metadata.get("greeting_sent") is True

            # Cleanup
            sse_task.cancel()
            try:
                await sse_task
            except asyncio.CancelledError:
                pass

    @pytest.mark.skip(
        reason="SSE streaming tests are flaky - use test_sse_unit.py instead"
    )
    @pytest.mark.asyncio
    async def test_no_greeting_on_reconnect(self, mock_session_manager):
        """Test that greeting is not sent when reconnecting to existing session."""
        session_id = "test-session-reconnect"

        # Mock existing session with greeting already sent
        existing_session = MagicMock()
        existing_session.metadata = {
            "greeting_sent": True,
            "language": "en-US",
        }
        mock_session_manager.get_session_readonly.return_value = existing_session

        with patch(
            "src.text.router.start_agent_session", new_callable=AsyncMock
        ) as mock_start:
            # Mock the agent session setup
            mock_runner = AsyncMock()
            mock_session = AsyncMock()
            mock_session.id = f"adk-{session_id}"
            mock_session.user_id = session_id
            mock_run_config = {}
            mock_start.return_value = (mock_runner, mock_session, mock_run_config)

            # Mock runner.run_async
            mock_runner.run_async = AsyncMock()

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                # Connect and wait for initial events
                messages = []
                async with client.stream(
                    "GET", f"/api/events/{session_id}"
                ) as response:
                    # Collect first message with timeout
                    start_time = asyncio.get_event_loop().time()
                    async for line in response.aiter_lines():
                        if asyncio.get_event_loop().time() - start_time > 2.0:
                            break
                        if line.startswith("data: "):
                            try:
                                data = json.loads(line[6:])
                                messages.append(data)
                                if len(messages) >= 1:
                                    break
                            except json.JSONDecodeError:
                                continue

                # Should not send greeting on reconnect
                mock_runner.run_async.assert_not_called()

                # No content events should be present
                content_messages = [
                    msg for msg in messages if msg.get("type") == "content"
                ]
                assert len(content_messages) == 0

    @pytest.mark.skip(
        reason="SSE streaming tests are flaky - use test_sse_unit.py instead"
    )
    @pytest.mark.asyncio
    async def test_empty_message_does_not_trigger_greeting(self, mock_session_manager):
        """Test that empty messages don't trigger greeting."""
        with patch(
            "src.text.router.start_agent_session", new_callable=AsyncMock
        ) as mock_start:
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
                "message_queue": asyncio.Queue(),
                "language": "en-US",
                "greeting_sent": False,
            }
            mock_session_manager.get_session.return_value = mock_session_info
            mock_session_manager.create_session.return_value = mock_session_info

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                # Connect
                session_id = "test-session-123"

                async def stream_sse():
                    async with client.stream(
                        "GET", f"/api/events/{session_id}"
                    ) as response:
                        async for _line in response.aiter_lines():
                            pass  # Just consume the stream

                sse_task = asyncio.create_task(stream_sse())

                # Give connection time to establish
                await asyncio.sleep(0.1)

                # Send empty message
                response = await client.post(
                    f"/api/send/{session_id}",
                    json={"data": "", "mime_type": "text/plain"},
                )
                assert response.status_code == 200
                await asyncio.sleep(0.1)  # Give time for processing

                # Greeting should not be sent for empty message
                assert mock_session_info.metadata.get("greeting_sent") is False

                # Cancel SSE task
                sse_task.cancel()
                try:
                    await sse_task
                except asyncio.CancelledError:
                    pass
