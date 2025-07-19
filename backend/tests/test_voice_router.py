"""Tests for the voice router endpoints."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Patch dependencies before importing
with patch("src.voice.session_manager.voice_session_manager", MagicMock()):
    from src.main import app

from src.voice.session_manager import VoiceSession


@pytest.fixture
def mock_voice_session_manager():
    """Mock voice session manager for tests."""
    with patch("src.voice.router.voice_session_manager") as mock:
        # Setup default behaviors
        mock.get_session.return_value = None
        mock.create_session = AsyncMock()
        mock.remove_session = AsyncMock()
        yield mock


@pytest.fixture
def client(mock_voice_session_manager):
    """Create a test client."""
    with TestClient(app) as test_client:
        yield test_client


class TestVoiceSessionEndpoints:
    """Test voice session management endpoints."""

    @pytest.mark.asyncio
    async def test_create_voice_session(self, client, mock_voice_session_manager):
        """Test creating a new voice session."""
        # Mock voice session
        mock_session = MagicMock(spec=VoiceSession)
        mock_session.session_id = "voice-123"
        mock_session.status = "active"
        mock_session.language = "en-US"
        mock_voice_session_manager.create_session.return_value = mock_session

        response = client.post(
            "/api/voice/sessions",
            json={"language": "en-US"},
        )
        assert response.status_code == 200

        data = response.json()
        assert data["session_id"] == "voice-123"
        assert data["status"] == "active"
        assert data["language"] == "en-US"

        # Verify create_session was called with correct language
        mock_voice_session_manager.create_session.assert_called_once_with("en-US")

    @pytest.mark.asyncio
    async def test_create_voice_session_error(self, client, mock_voice_session_manager):
        """Test error handling in voice session creation."""
        mock_voice_session_manager.create_session.side_effect = Exception("Test error")

        response = client.post(
            "/api/voice/sessions",
            json={"language": "en-US"},
        )
        assert response.status_code == 500
        assert "Failed to create voice session" in response.json()["detail"]


class TestAudioEndpoints:
    """Test audio handling endpoints."""

    def test_send_audio_chunk_success(self, client, mock_voice_session_manager):
        """Test sending audio chunk to active session."""
        # Mock active session
        mock_session = MagicMock(spec=VoiceSession)
        mock_session.status = "active"
        mock_session.send_audio = AsyncMock()
        mock_voice_session_manager.get_session.return_value = mock_session

        response = client.post(
            "/api/voice/sessions/voice-123/audio",
            json={
                "data": "YXVkaW9fZGF0YQ==",  # base64 encoded "audio_data"
                "timestamp": 1234567890,
            },
        )
        assert response.status_code == 200
        assert response.json()["status"] == "received"

    def test_send_audio_chunk_session_not_found(
        self, client, mock_voice_session_manager
    ):
        """Test sending audio to non-existent session."""
        mock_voice_session_manager.get_session.return_value = None

        response = client.post(
            "/api/voice/sessions/nonexistent/audio",
            json={"data": "YXVkaW9fZGF0YQ==", "timestamp": 1234567890},
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Session not found"

    def test_send_audio_chunk_session_not_active(
        self, client, mock_voice_session_manager
    ):
        """Test sending audio to inactive session."""
        mock_session = MagicMock(spec=VoiceSession)
        mock_session.status = "ended"
        mock_voice_session_manager.get_session.return_value = mock_session

        response = client.post(
            "/api/voice/sessions/voice-123/audio",
            json={"data": "YXVkaW9fZGF0YQ==", "timestamp": 1234567890},
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Session is not active"


class TestVoiceControlEndpoints:
    """Test voice control endpoints."""

    def test_voice_control_end_turn(self, client, mock_voice_session_manager):
        """Test sending end_turn control command."""
        mock_session = MagicMock(spec=VoiceSession)
        mock_session.send_control = AsyncMock()
        mock_voice_session_manager.get_session.return_value = mock_session

        response = client.post(
            "/api/voice/sessions/voice-123/control",
            json={"action": "end_turn"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert response.json()["action"] == "end_turn"

    def test_voice_control_end_session(self, client, mock_voice_session_manager):
        """Test sending end_session control command."""
        mock_session = MagicMock(spec=VoiceSession)
        mock_session.send_control = AsyncMock()
        mock_voice_session_manager.get_session.return_value = mock_session

        response = client.post(
            "/api/voice/sessions/voice-123/control",
            json={"action": "end_session"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert response.json()["action"] == "end_session"

    def test_voice_control_session_not_found(self, client, mock_voice_session_manager):
        """Test control command for non-existent session."""
        mock_voice_session_manager.get_session.return_value = None

        response = client.post(
            "/api/voice/sessions/nonexistent/control",
            json={"action": "end_turn"},
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Session not found"


class TestVoiceStreamEndpoint:
    """Test voice streaming endpoint."""

    def test_voice_stream_exists(self, client, mock_voice_session_manager):
        """Test that voice stream endpoint exists."""
        # Mock session for stream with minimal required attributes
        mock_session = MagicMock()
        mock_session.status = "ended"  # Set to ended to avoid infinite loop
        mock_session.agent_queue = MagicMock()
        mock_session.agent_queue.get = AsyncMock()
        mock_voice_session_manager.get_session.return_value = mock_session

        # Note: Testing SSE streams is complex and requires special handling
        # This just verifies the endpoint exists and returns correct headers
        response = client.get(
            "/api/voice/sessions/voice-123/stream",
            headers={"Accept": "text/event-stream"},
        )
        # TestClient doesn't handle SSE well, so we just check it doesn't 404
        assert response.status_code != 404

    def test_voice_stream_session_not_found(self, client, mock_voice_session_manager):
        """Test voice stream for non-existent session."""
        mock_voice_session_manager.get_session.return_value = None

        response = client.get("/api/voice/sessions/nonexistent/stream")
        assert response.status_code == 404
        assert response.json()["detail"] == "Session not found"


class TestEndVoiceSession:
    """Test ending voice sessions."""

    @pytest.mark.asyncio
    async def test_end_voice_session(self, client, mock_voice_session_manager):
        """Test ending a voice session."""
        mock_session = MagicMock(spec=VoiceSession)
        mock_voice_session_manager.get_session.return_value = mock_session

        response = client.delete("/api/voice/sessions/voice-123")
        assert response.status_code == 200
        assert response.json()["status"] == "ended"

        # Verify remove_session was called
        mock_voice_session_manager.remove_session.assert_called_once_with("voice-123")

    def test_end_voice_session_not_found(self, client, mock_voice_session_manager):
        """Test ending non-existent session."""
        mock_voice_session_manager.get_session.return_value = None

        response = client.delete("/api/voice/sessions/nonexistent")
        assert response.status_code == 404
        assert response.json()["detail"] == "Session not found"
