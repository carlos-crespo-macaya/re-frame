"""Minimal audio roundtrip test to verify audio processing works end-to-end."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.utils.session_manager import session_manager
from tests.fixtures import AudioSamples


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def audio_samples():
    """Provide audio samples for testing."""
    return AudioSamples


def test_audio_roundtrip_minimal(client, audio_samples):
    """Minimal test to verify audio processing works end-to-end."""
    session_id = "test-session-123"

    # Create a mock session with required metadata
    mock_session = MagicMock()
    mock_queue = AsyncMock()
    mock_runner = AsyncMock()
    mock_adk_session = MagicMock()
    mock_run_config = MagicMock()

    # Mock process_message to return empty events
    async def mock_process_message(*args, **kwargs):
        return []

    # Set up metadata with required components
    mock_session.metadata = {
        "message_queue": mock_queue,
        "runner": mock_runner,
        "adk_session": mock_adk_session,
        "run_config": mock_run_config,
    }

    # Enable voice mode for this test by patching the config module directly
    with patch("src.config.VOICE_MODE_ENABLED", True):
        with patch.object(session_manager, "get_session", return_value=mock_session):
            with patch("src.main.process_message", mock_process_message):
                resp = client.post(
                    f"/api/send/{session_id}",
                    json={
                        "mime_type": "audio/pcm",
                        "data": audio_samples.get_sample("hello"),
                    },
                )

    # Now we expect 200 since basic audio processing is implemented
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify response structure
    response_data = resp.json()
    assert response_data["status"] == "sent"
    assert response_data["error"] is None

    # The endpoint returns a simple status response, not the actual messages
    # Messages are delivered via SSE to the message_queue
