"""Simplified tests for reactive behavior in text router - TDD approach.

These tests verify the reactive SSE endpoint behavior where:
1. No greeting is sent on initial connection
2. Language detection overrides URL parameter for text responses
3. First message triggers appropriate greeting response
4. Session state correctly tracks greeting status

Note: These tests are written to FAIL initially (RED phase of TDD).
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestReactiveSSEBehavior:
    """Test reactive SSE endpoint behavior."""

    @pytest.mark.asyncio
    async def test_sse_no_greeting_on_connect(self):
        """Test that SSE endpoint doesn't send greeting on initial connection."""
        from fastapi import Request

        from src.text.router import sse_endpoint

        # Create a mock request
        mock_request = MagicMock(spec=Request)
        mock_request.method = "GET"

        with patch("src.text.router.start_agent_session") as mock_start:
            # Mock the agent session setup
            mock_runner = MagicMock()
            mock_runner.run_async = AsyncMock()
            mock_session = MagicMock()
            mock_session.id = "adk-session-123"
            mock_session.user_id = "test-session-123"
            mock_run_config = {}
            mock_start.return_value = (mock_runner, mock_session, mock_run_config)

            # Mock session manager
            with patch("src.text.router.session_manager") as mock_sm:
                mock_session_info = MagicMock()
                mock_session_info.metadata = {}
                mock_sm.create_session.return_value = mock_session_info

                # Mock performance monitor
                with patch("src.text.router.get_performance_monitor") as mock_perf:
                    mock_monitor = MagicMock()
                    mock_monitor.start_session = AsyncMock()
                    mock_perf.return_value = mock_monitor

                    # Call the endpoint
                    await sse_endpoint(
                        mock_request, "test-session-123", "en-US"
                    )

                    # EXPECTED TO FAIL: Currently calls run_async with START_CONVERSATION
                    # The current implementation sends a greeting on connection
                    # Check that run_async was NOT called (it should not send greeting on connect)
                    mock_runner.run_async.assert_not_called()

    @pytest.mark.asyncio
    async def test_first_message_triggers_greeting(self):
        """Test that first user message triggers greeting response."""
        from src.models import MessageRequest
        from src.text.router import send_message_endpoint

        with patch("src.text.router.session_manager") as mock_sm:
            # Mock session with greeting_sent = False
            mock_session = MagicMock()
            mock_runner = MagicMock()
            mock_adk_session = MagicMock()
            mock_run_config = {}
            mock_queue = AsyncMock()

            mock_session.metadata = {
                "runner": mock_runner,
                "adk_session": mock_adk_session,
                "run_config": mock_run_config,
                "message_queue": mock_queue,
                "language": "en-US",
                "greeting_sent": False,  # Not sent yet
            }
            mock_sm.get_session.return_value = mock_session

            # Mock process_message
            with patch("src.text.router.process_message") as mock_process:
                mock_process.return_value = []

                # Mock performance monitor
                with patch("src.text.router.get_performance_monitor") as mock_perf:
                    mock_monitor = MagicMock()
                    mock_monitor.track_request = MagicMock()
                    mock_monitor.track_request.return_value.__aenter__ = AsyncMock()
                    mock_monitor.track_request.return_value.__aexit__ = AsyncMock()
                    mock_perf.return_value = mock_monitor

                    # Send first message
                    message = MessageRequest(data="Hello", mime_type="text/plain")
                    await send_message_endpoint("test-session-123", message)

                    # EXPECTED TO FAIL: Need to check for greeting trigger
                    # The implementation should check greeting_sent and trigger greeting
                    assert mock_session.metadata.get("greeting_sent") is True

    @pytest.mark.asyncio
    async def test_language_detection_on_first_message(self):
        """Test that language is detected on first message and overrides URL parameter."""
        from src.models import MessageRequest
        from src.text.router import send_message_endpoint

        with patch("src.text.router.session_manager") as mock_sm:
            # Mock session with Spanish from URL
            mock_session = MagicMock()
            mock_runner = MagicMock()
            mock_adk_session = MagicMock()
            mock_run_config = {}
            mock_queue = AsyncMock()

            mock_session.metadata = {
                "runner": mock_runner,
                "adk_session": mock_adk_session,
                "run_config": mock_run_config,
                "message_queue": mock_queue,
                "language": "es-ES",  # Spanish from URL
                "greeting_sent": False,
            }
            mock_sm.get_session.return_value = mock_session

            # Mock language detection
            with patch("src.text.router.detect_language") as mock_detect:
                mock_detect.return_value = ("en", 0.95)  # Detect English

                # Mock process_message
                with patch("src.text.router.process_message") as mock_process:
                    mock_process.return_value = []

                    # Mock performance monitor
                    with patch("src.text.router.get_performance_monitor") as mock_perf:
                        mock_monitor = MagicMock()
                        mock_monitor.track_request = MagicMock()
                        mock_monitor.track_request.return_value.__aenter__ = AsyncMock()
                        mock_monitor.track_request.return_value.__aexit__ = AsyncMock()
                        mock_perf.return_value = mock_monitor

                        # Send English message
                        message = MessageRequest(
                            data="Hello, I need help with anxiety",
                            mime_type="text/plain",
                        )
                        await send_message_endpoint(
                            "test-session-123", message
                        )

                        # EXPECTED TO FAIL: Language detection not implemented
                        # Should detect language and update session
                        mock_detect.assert_called_once_with(
                            "Hello, I need help with anxiety"
                        )
                        assert mock_session.metadata["language"] == "en-US"

    @pytest.mark.asyncio
    async def test_no_language_detection_on_subsequent_messages(self):
        """Test that language detection only happens on first message."""
        from src.models import MessageRequest
        from src.text.router import send_message_endpoint

        with patch("src.text.router.session_manager") as mock_sm:
            # Mock session with greeting already sent
            mock_session = MagicMock()
            mock_runner = MagicMock()
            mock_adk_session = MagicMock()
            mock_run_config = {}
            mock_queue = AsyncMock()

            mock_session.metadata = {
                "runner": mock_runner,
                "adk_session": mock_adk_session,
                "run_config": mock_run_config,
                "message_queue": mock_queue,
                "language": "en-US",
                "greeting_sent": True,  # Already sent
            }
            mock_sm.get_session.return_value = mock_session

            # Mock language detection
            with patch("src.text.router.detect_language") as mock_detect:
                mock_detect.return_value = ("es", 0.95)  # Would detect Spanish

                # Mock process_message
                with patch("src.text.router.process_message") as mock_process:
                    mock_process.return_value = []

                    # Mock performance monitor
                    with patch("src.text.router.get_performance_monitor") as mock_perf:
                        mock_monitor = MagicMock()
                        mock_monitor.track_request = MagicMock()
                        mock_monitor.track_request.return_value.__aenter__ = AsyncMock()
                        mock_monitor.track_request.return_value.__aexit__ = AsyncMock()
                        mock_perf.return_value = mock_monitor

                        # Send Spanish message
                        message = MessageRequest(
                            data="Hola, tengo otra pregunta", mime_type="text/plain"
                        )
                        await send_message_endpoint(
                            "test-session-123", message
                        )

                        # EXPECTED TO FAIL: Language detection happens on all messages currently
                        # Should NOT detect language on subsequent messages
                        mock_detect.assert_not_called()
                        # Language should remain English
                        assert mock_session.metadata["language"] == "en-US"

    @pytest.mark.asyncio
    async def test_greeting_sent_flag_prevents_duplicate_greeting(self):
        """Test that greeting_sent flag prevents sending greeting twice."""
        from src.models import MessageRequest
        from src.text.router import send_message_endpoint

        # Test with two sequential messages
        with patch("src.text.router.session_manager") as mock_sm:
            # Mock session
            mock_session = MagicMock()
            mock_runner = MagicMock()
            mock_adk_session = MagicMock()
            mock_run_config = {}
            mock_queue = AsyncMock()

            mock_session.metadata = {
                "runner": mock_runner,
                "adk_session": mock_adk_session,
                "run_config": mock_run_config,
                "message_queue": mock_queue,
                "language": "en-US",
                "greeting_sent": False,
            }
            mock_sm.get_session.return_value = mock_session

            # Mock process_message
            with patch("src.text.router.process_message") as mock_process:
                mock_process.return_value = []

                # Mock create_cbt_assistant for greeting trigger
                with patch("src.text.router.create_cbt_assistant") as mock_create:
                    mock_create.return_value = MagicMock()

                    # Mock performance monitor
                    with patch("src.text.router.get_performance_monitor") as mock_perf:
                        mock_monitor = MagicMock()
                        mock_monitor.track_request = MagicMock()
                        mock_monitor.track_request.return_value.__aenter__ = AsyncMock()
                        mock_monitor.track_request.return_value.__aexit__ = AsyncMock()
                        mock_perf.return_value = mock_monitor

                        # First message - should trigger greeting
                        message1 = MessageRequest(data="Hello", mime_type="text/plain")
                        await send_message_endpoint("test-session-123", message1)

                        # Simulate that greeting was sent
                        mock_session.metadata["greeting_sent"] = True

                        # Second message - should NOT trigger greeting
                        message2 = MessageRequest(
                            data="Another message", mime_type="text/plain"
                        )
                        await send_message_endpoint("test-session-123", message2)

                        # EXPECTED TO FAIL: Greeting logic not implemented
                        # Should only create assistant once for greeting
                        assert mock_create.call_count <= 1

    def test_detect_language_import(self):
        """Test that detect_language function exists and is importable."""
        # EXPECTED TO FAIL: detect_language might not be imported
        from src.text.router import detect_language

        assert detect_language is not None
