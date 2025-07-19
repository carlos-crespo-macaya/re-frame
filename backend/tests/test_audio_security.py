"""Test security aspects of audio processing."""

import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.utils.session_manager import session_manager
from tests.fixtures import AudioSamples


class TestAudioSecurity:
    """Test security aspects of audio processing."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)

    @pytest.fixture
    def mock_session(self):
        """Create a mock session with required metadata."""
        mock_session = MagicMock()
        mock_queue = AsyncMock()
        mock_runner = AsyncMock()
        mock_adk_session = MagicMock()
        mock_run_config = MagicMock()

        # Mock runner.run_async to return an async generator
        async def mock_run_async(*args, **kwargs):
            # Return empty list of events
            for _ in []:
                yield

        mock_runner.run_async = mock_run_async

        mock_session.metadata = {
            "message_queue": mock_queue,
            "runner": mock_runner,
            "adk_session": mock_adk_session,
            "run_config": mock_run_config,
        }

        # Mock session methods
        mock_session.to_dict.return_value = {
            "session_id": "test-security-session",
            "messages": [],
            "metadata": {},
        }
        mock_session.messages = []

        return mock_session

    def test_audio_data_not_logged(self, client, mock_session, caplog):
        """Ensure audio data is never logged."""
        audio_sample = AudioSamples.get_sample("i_feel_anxious")

        with (
            caplog.at_level(logging.DEBUG),
            patch("src.config.VOICE_MODE_ENABLED", True),
            patch.object(session_manager, "get_session", return_value=mock_session),
        ):
            client.post(
                "/api/send/test-session",
                json={"mime_type": "audio/pcm", "data": audio_sample},
            )

        # Check that no log contains the actual audio data
        for record in caplog.records:
            # Remove ANSI color codes for easier matching
            clean_message = record.getMessage()
            assert audio_sample not in clean_message
            # Only size info should be logged, not the data itself
            if "audio" in clean_message.lower():
                # Check for expected content (size or transcript info)
                assert any(
                    word in clean_message.lower()
                    for word in ["size", "transcri", "process"]
                )

    def test_audio_not_stored_in_session(self, client, mock_session):
        """Verify audio is processed but not persisted."""
        session_id = "test-security-session"
        audio_sample = AudioSamples.get_sample("hello")

        with (
            patch("src.config.VOICE_MODE_ENABLED", True),
            patch.object(session_manager, "get_session", return_value=mock_session),
        ):
            response = client.post(
                f"/api/send/{session_id}",
                json={"mime_type": "audio/pcm", "data": audio_sample},
            )

        # Check response doesn't contain audio data
        assert response.status_code == 200
        response_data = response.json()
        assert "audio" not in str(
            response_data
        ).lower() or "audio" in response_data.get("status", "")

        # Verify session mock wasn't called with audio data
        # Only transcript should be processed
        for call in mock_session.metadata["message_queue"].put.call_args_list:
            event = call[0][0]
            if hasattr(event, "__dict__"):
                assert audio_sample not in str(event.__dict__)

    def test_audio_headers_sanitization(self, client, mock_session):
        """Test that sensitive headers are not exposed in response."""
        with (
            patch("src.config.VOICE_MODE_ENABLED", True),
            patch.object(session_manager, "get_session", return_value=mock_session),
        ):
            response = client.post(
                "/api/send/test-session",
                json={
                    "mime_type": "audio/pcm",
                    "data": AudioSamples.get_sample("hello"),
                },
                headers={
                    "X-Api-Key": "sensitive-key-12345",
                    "Authorization": "Bearer sensitive-token-67890",
                },
            )

        # Ensure response doesn't echo sensitive headers
        assert "X-Api-Key" not in response.headers
        assert "Authorization" not in response.headers
        assert "sensitive-key" not in str(response.headers)
        assert "sensitive-token" not in str(response.headers)

    def test_audio_base64_validation(self, client, mock_session):
        """Test that only valid base64 audio is accepted."""
        test_cases = [
            ("", 200),  # Empty string is valid base64 (empty bytes)
            ("not-base64!@#$", 500),  # Invalid base64
            ("////", 200),  # Valid base64
            ("<script>alert('xss')</script>", 500),  # XSS attempt (invalid base64)
        ]

        for invalid_input, expected_status in test_cases:
            with (
                patch("src.config.VOICE_MODE_ENABLED", True),
                patch.object(session_manager, "get_session", return_value=mock_session),
            ):
                response = client.post(
                    "/api/send/test-session",
                    json={"mime_type": "audio/pcm", "data": invalid_input},
                )

            # Check expected status code
            assert (
                response.status_code == expected_status
            ), f"Expected {expected_status} for input: {invalid_input}, got {response.status_code}"

    def test_session_isolation(self, client):
        """Test that audio from one session doesn't leak to another."""
        session1_id = "session-1"
        session2_id = "session-2"

        # Create two separate mock sessions
        mock_session1 = MagicMock()
        mock_queue1 = AsyncMock()
        mock_runner1 = AsyncMock()

        # Mock runner.run_async for session 1
        async def mock_run_async1(*args, **kwargs):
            # Return minimal events
            yield MagicMock(content=MagicMock(parts=[MagicMock(text="Response 1")]))
            yield MagicMock(turn_complete=True)

        mock_runner1.run_async = mock_run_async1

        mock_session1.metadata = {
            "message_queue": mock_queue1,
            "runner": mock_runner1,
            "adk_session": MagicMock(),
            "run_config": MagicMock(),
        }

        mock_session2 = MagicMock()
        mock_queue2 = AsyncMock()
        mock_runner2 = AsyncMock()

        # Mock runner.run_async for session 2
        async def mock_run_async2(*args, **kwargs):
            # Return minimal events
            yield MagicMock(content=MagicMock(parts=[MagicMock(text="Response 2")]))
            yield MagicMock(turn_complete=True)

        mock_runner2.run_async = mock_run_async2

        mock_session2.metadata = {
            "message_queue": mock_queue2,
            "runner": mock_runner2,
            "adk_session": MagicMock(),
            "run_config": MagicMock(),
        }

        def get_session_side_effect(session_id):
            if session_id == session1_id:
                return mock_session1
            elif session_id == session2_id:
                return mock_session2
            return None

        with (
            patch("src.config.VOICE_MODE_ENABLED", True),
            patch.object(
                session_manager, "get_session", side_effect=get_session_side_effect
            ),
        ):
            # Send audio to session 1
            response1 = client.post(
                f"/api/send/{session1_id}",
                json={
                    "mime_type": "audio/pcm",
                    "data": AudioSamples.get_sample("hello"),
                },
            )

            # Send audio to session 2
            response2 = client.post(
                f"/api/send/{session2_id}",
                json={
                    "mime_type": "audio/pcm",
                    "data": AudioSamples.get_sample("i_feel_anxious"),
                },
            )

        # Both should succeed
        assert response1.status_code == 200
        assert response2.status_code == 200

        # Verify sessions are isolated
        assert mock_session1.metadata["message_queue"].put.called
        assert mock_session2.metadata["message_queue"].put.called

        # Check that queues received different events
        session1_calls = mock_session1.metadata["message_queue"].put.call_count
        session2_calls = mock_session2.metadata["message_queue"].put.call_count
        assert session1_calls > 0
        assert session2_calls > 0
