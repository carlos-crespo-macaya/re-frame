"""Minimal audio roundtrip test to verify voice processing works end-to-end."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.voice.session_manager import VoiceSession
from tests.fixtures import AudioSamples


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def audio_samples():
    """Provide audio samples for testing."""
    return AudioSamples


@pytest.fixture
def mock_voice_session_manager():
    """Mock voice session manager."""
    with patch("src.voice.router.voice_session_manager") as mock:
        yield mock


def test_audio_roundtrip_minimal(client, audio_samples, mock_voice_session_manager):
    """Minimal test to verify voice processing works end-to-end."""

    # Step 1: Create a voice session
    mock_session = MagicMock(spec=VoiceSession)
    mock_session.session_id = "voice-test-123"
    mock_session.status = "active"
    mock_session.language = "en-US"
    mock_session.send_audio = AsyncMock()
    mock_session.send_control = AsyncMock()

    mock_voice_session_manager.create_session = AsyncMock(return_value=mock_session)
    mock_voice_session_manager.get_session.return_value = mock_session
    mock_voice_session_manager.remove_session = AsyncMock()

    # Create session
    resp = client.post("/api/voice/sessions", json={"language": "en-US"})
    assert resp.status_code == 200
    session_data = resp.json()
    assert session_data["session_id"] == "voice-test-123"
    assert session_data["status"] == "active"

    # Step 2: Send audio data
    resp = client.post(
        f"/api/voice/sessions/{session_data['session_id']}/audio",
        json={"data": audio_samples.get_sample("hello"), "timestamp": 1234567890},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "received"

    # Verify send_audio was called
    mock_session.send_audio.assert_called_once()

    # Step 3: Test control commands
    resp = client.post(
        f"/api/voice/sessions/{session_data['session_id']}/control",
        json={"action": "end_turn"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

    # Step 4: End session
    resp = client.delete(f"/api/voice/sessions/{session_data['session_id']}")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ended"

    # Verify remove_session was called
    mock_voice_session_manager.remove_session.assert_called_once_with("voice-test-123")
