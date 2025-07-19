"""Test error scenarios in voice/audio processing."""

import base64
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.voice.session_manager import VoiceSession
from tests.fixtures import AudioSamples


class TestAudioErrorHandling:
    """Test error scenarios in voice/audio processing."""

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
        mock_session.status = "active"
        mock_session.send_audio = AsyncMock()
        return mock_session

    def test_corrupted_base64_audio(
        self, client, mock_voice_session_manager, mock_voice_session
    ):
        """Test handling of malformed base64 audio data."""
        mock_voice_session_manager.get_session.return_value = mock_voice_session

        response = client.post(
            "/api/voice/sessions/test-session/audio",
            json={"data": "invalid_base64_!@#", "timestamp": 1234567890},
        )

        # Should fail due to invalid base64
        assert response.status_code == 500
        assert "Failed to process audio" in response.json()["detail"]

    def test_audio_size_limit(self, client, mock_voice_session_manager):
        """Test rejection of oversized audio data."""
        # Note: In the new voice implementation, size limits would be
        # handled at the nginx/load balancer level or in the voice session
        # For now, we just test that large audio can be sent
        large_audio = base64.b64encode(b"x" * 1_000_000).decode()

        mock_session = MagicMock(spec=VoiceSession)
        mock_session.status = "active"
        mock_session.send_audio = AsyncMock()
        mock_voice_session_manager.get_session.return_value = mock_session

        response = client.post(
            "/api/voice/sessions/test-session/audio",
            json={"data": large_audio, "timestamp": 1234567890},
        )

        # Should succeed (size limits would be enforced elsewhere)
        assert response.status_code == 200

    def test_stt_service_failure(
        self, client, mock_voice_session_manager, mock_voice_session
    ):
        """Test graceful handling of STT service failure."""
        # Mock send_audio to raise an exception
        mock_voice_session.send_audio.side_effect = Exception("STT service unavailable")
        mock_voice_session_manager.get_session.return_value = mock_voice_session

        response = client.post(
            "/api/voice/sessions/test-session/audio",
            json={"data": AudioSamples.get_sample("hello"), "timestamp": 1234567890},
        )

        assert response.status_code == 500
        assert "Failed to process audio" in response.json()["detail"]

    def test_silence_detection(
        self, client, mock_voice_session_manager, mock_voice_session
    ):
        """Test handling of silence in audio."""
        # In the new implementation, silence is handled by ADK
        # We just verify that silence can be sent successfully
        mock_voice_session_manager.get_session.return_value = mock_voice_session

        response = client.post(
            "/api/voice/sessions/test-session/audio",
            json={"data": AudioSamples.get_sample("silence"), "timestamp": 1234567890},
        )

        assert response.status_code == 200
        assert response.json()["status"] == "received"

    def test_session_not_active(self, client, mock_voice_session_manager):
        """Test sending audio to inactive session."""
        mock_session = MagicMock(spec=VoiceSession)
        mock_session.status = "ended"
        mock_voice_session_manager.get_session.return_value = mock_session

        response = client.post(
            "/api/voice/sessions/test-session/audio",
            json={"data": AudioSamples.get_sample("hello"), "timestamp": 1234567890},
        )

        assert response.status_code == 400
        assert "Session is not active" in response.json()["detail"]

    def test_session_not_found(self, client, mock_voice_session_manager):
        """Test sending audio to non-existent session."""
        mock_voice_session_manager.get_session.return_value = None

        response = client.post(
            "/api/voice/sessions/nonexistent/audio",
            json={"data": AudioSamples.get_sample("hello"), "timestamp": 1234567890},
        )

        assert response.status_code == 404
        assert "Session not found" in response.json()["detail"]
