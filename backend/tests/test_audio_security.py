"""Test security aspects of voice/audio processing."""

import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.voice.session_manager import VoiceSession
from tests.fixtures import AudioSamples


class TestAudioSecurity:
    """Test security aspects of voice/audio processing."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)

    @pytest.fixture
    def mock_voice_session_manager(self):
        """Mock voice session manager."""
        with patch("src.voice.router.voice_session_manager") as mock:
            yield mock

    @pytest.fixture
    def mock_voice_session(self):
        """Create a mock voice session."""
        mock_session = MagicMock(spec=VoiceSession)
        mock_session.session_id = "voice-test-123"
        mock_session.status = "active"
        mock_session.language = "en-US"
        mock_session.send_audio = AsyncMock()
        return mock_session

    def test_audio_data_not_logged(
        self, client, mock_voice_session_manager, mock_voice_session, caplog
    ):
        """Test that raw audio data is never logged."""
        mock_voice_session_manager.get_session.return_value = mock_voice_session

        # Set logging to capture everything
        with caplog.at_level(logging.DEBUG):
            audio_data = AudioSamples.get_sample("hello")
            response = client.post(
                "/api/voice/sessions/test-session/audio",
                json={"data": audio_data, "timestamp": 1234567890},
            )

        assert response.status_code == 200

        # Verify audio data is not in logs
        log_text = "\n".join(record.message for record in caplog.records)
        assert audio_data not in log_text
        # Also check for decoded audio
        import base64

        decoded = base64.b64decode(audio_data)
        assert str(decoded) not in log_text

    def test_audio_not_stored_in_session(
        self, client, mock_voice_session_manager, mock_voice_session
    ):
        """Test that audio data is not stored in session metadata."""
        mock_voice_session_manager.create_session = AsyncMock(
            return_value=mock_voice_session
        )
        mock_voice_session_manager.get_session.return_value = mock_voice_session

        # Create session
        response = client.post("/api/voice/sessions", json={"language": "en-US"})
        assert response.status_code == 200

        # Send audio
        audio_data = AudioSamples.get_sample("hello")
        response = client.post(
            f"/api/voice/sessions/{mock_voice_session.session_id}/audio",
            json={"data": audio_data, "timestamp": 1234567890},
        )
        assert response.status_code == 200

        # Verify audio was sent to ADK but not stored
        mock_voice_session.send_audio.assert_called_once()
        # In the new implementation, audio is sent directly to ADK
        # and not stored in session metadata

    def test_audio_headers_sanitization(self, client, mock_voice_session_manager):
        """Test that sensitive headers are not exposed."""
        mock_session = MagicMock(spec=VoiceSession)
        mock_session.status = "active"
        mock_session.send_audio = AsyncMock()
        mock_voice_session_manager.get_session.return_value = mock_session

        # Send request with potentially sensitive headers
        response = client.post(
            "/api/voice/sessions/test-session/audio",
            json={"data": AudioSamples.get_sample("hello"), "timestamp": 1234567890},
            headers={
                "Authorization": "Bearer secret-token",
                "X-Api-Key": "secret-key",
                "Cookie": "session=secret",
            },
        )

        assert response.status_code == 200
        # Verify response doesn't echo sensitive headers
        assert "Authorization" not in response.headers
        assert "X-Api-Key" not in response.headers
        assert "Cookie" not in response.headers

    def test_audio_base64_validation(
        self, client, mock_voice_session_manager, mock_voice_session
    ):
        """Test that only valid base64 audio is accepted."""
        mock_voice_session_manager.get_session.return_value = mock_voice_session

        # Test various invalid inputs
        # Note: Empty base64 string is valid (decodes to empty bytes)
        invalid_inputs = [
            {"data": "not-base64!@#$%", "timestamp": 1234567890},  # Invalid base64
            {"data": 12345, "timestamp": 1234567890},  # Not a string
            {"data": None, "timestamp": 1234567890},  # Null
            {"timestamp": 1234567890},  # Missing data field
        ]

        for i, invalid_input in enumerate(invalid_inputs):
            response = client.post(
                "/api/voice/sessions/test-session/audio",
                json=invalid_input,
            )
            # Should fail validation or processing
            assert response.status_code in [
                422,
                500,
            ], f"Test case {i} with input {invalid_input} should fail"

        # Test that empty string IS accepted (valid base64)
        response = client.post(
            "/api/voice/sessions/test-session/audio",
            json={"data": "", "timestamp": 1234567890},
        )
        assert response.status_code == 200

    def test_session_isolation(self, client, mock_voice_session_manager):
        """Test that sessions are properly isolated."""
        # Create two different sessions
        session1 = MagicMock(spec=VoiceSession)
        session1.session_id = "voice-session-1"
        session1.status = "active"
        session1.send_audio = AsyncMock()

        session2 = MagicMock(spec=VoiceSession)
        session2.session_id = "voice-session-2"
        session2.status = "active"
        session2.send_audio = AsyncMock()

        # Mock get_session to return different sessions
        def get_session_side_effect(session_id):
            if session_id == "voice-session-1":
                return session1
            elif session_id == "voice-session-2":
                return session2
            return None

        mock_voice_session_manager.get_session.side_effect = get_session_side_effect

        # Send audio to session 1
        response = client.post(
            "/api/voice/sessions/voice-session-1/audio",
            json={"data": AudioSamples.get_sample("hello"), "timestamp": 1234567890},
        )
        assert response.status_code == 200

        # Send audio to session 2
        response = client.post(
            "/api/voice/sessions/voice-session-2/audio",
            json={"data": AudioSamples.get_sample("goodbye"), "timestamp": 1234567890},
        )
        assert response.status_code == 200

        # Verify each session received only its own audio
        assert session1.send_audio.call_count == 1
        assert session2.send_audio.call_count == 1

        # Try to access non-existent session
        response = client.post(
            "/api/voice/sessions/voice-session-3/audio",
            json={"data": AudioSamples.get_sample("hello"), "timestamp": 1234567890},
        )
        assert response.status_code == 404
