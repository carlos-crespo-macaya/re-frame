"""Unit tests for SSE endpoint behavior without streaming complexity."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from starlette.responses import StreamingResponse

# Patch dependencies before importing
with (
    patch("src.text.router.create_cbt_assistant", MagicMock()),
    patch("src.utils.session_manager.session_manager", MagicMock()),
):
    from src.text.router import sse_endpoint


@pytest.mark.asyncio
async def test_sse_endpoint_returns_streaming_response():
    """Test that SSE endpoint returns a StreamingResponse."""
    from src.utils.session_manager import SessionInfo as SessionInfoModel

    # Create mock request
    mock_request = AsyncMock()
    mock_request.method = "GET"
    mock_request.is_disconnected = AsyncMock(return_value=False)

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

        with patch("src.text.router.get_performance_monitor") as mock_perf:
            mock_monitor = AsyncMock()
            mock_perf.return_value = mock_monitor

            with patch("src.text.router.session_manager") as mock_sm:
                # Create a proper SessionInfo object
                mock_session_info = SessionInfoModel(
                    session_id="test-session-123", user_id="test-session-123"
                )
                mock_sm.create_session.return_value = mock_session_info
                mock_sm.get_session_readonly.return_value = None

                # Call the endpoint with language parameter
                response = await sse_endpoint(
                    mock_request, "test-session-123", language="en-US"
                )

                # Verify it returns a StreamingResponse
                assert isinstance(response, StreamingResponse)
                assert response.media_type == "text/event-stream"
                assert response.headers["Cache-Control"] == "no-cache"
                assert response.headers["Connection"] == "keep-alive"
                assert response.headers["X-Session-Id"] == "test-session-123"


@pytest.mark.asyncio
async def test_sse_stream_generator_sends_connected_message():
    """Test the stream generator sends the connected message."""
    from src.utils.session_manager import SessionInfo as SessionInfoModel

    # Create mock request
    mock_request = AsyncMock()
    mock_request.method = "GET"
    mock_request.is_disconnected = AsyncMock(
        return_value=True
    )  # Disconnect immediately

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

        with patch("src.text.router.get_performance_monitor") as mock_perf:
            mock_monitor = AsyncMock()
            mock_perf.return_value = mock_monitor

            with patch("src.text.router.session_manager") as mock_sm:
                # Create a proper SessionInfo object
                mock_session_info = SessionInfoModel(
                    session_id="test-session-123", user_id="test-session-123"
                )
                mock_sm.create_session.return_value = mock_session_info
                mock_sm.get_session_readonly.return_value = None

                # Call the endpoint and get the generator
                response = await sse_endpoint(
                    mock_request, "test-session-123", language="en-US"
                )

                # Manually consume the generator
                messages = []
                async for chunk in response.body_iterator:
                    # chunk might already be a string or bytes
                    if isinstance(chunk, bytes):
                        messages.append(chunk.decode("utf-8"))
                    else:
                        messages.append(chunk)
                    # Stop after first message
                    break

                # Verify the connected message
                assert len(messages) > 0
                first_message = messages[0]
                assert first_message.startswith("data: ")
                data = json.loads(first_message[6:].strip())
                assert data["type"] == "connected"
                assert data["session_id"] == "test-session-123"


@pytest.mark.asyncio
async def test_sse_endpoint_handles_head_request():
    """Test that SSE endpoint handles HEAD requests properly."""
    # Create mock request
    mock_request = AsyncMock()
    mock_request.method = "HEAD"

    # No need to mock anything else for HEAD request
    response = await sse_endpoint(mock_request, "test-session-123", language="en-US")

    # Verify it returns proper headers without body
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "text/event-stream"
    assert response.headers["Cache-Control"] == "no-cache"
