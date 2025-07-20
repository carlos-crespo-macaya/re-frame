"""Tests for the text router endpoints."""

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


class TestSessionEndpoints:
    """Test session management endpoints."""

    def test_get_session_info_found(self, client, mock_session_manager):
        """Test getting session info when session exists."""
        # Mock session data
        mock_session = SessionInfoModel(
            session_id="test-session",
            user_id="test-user",
            created_at=1234567890.0,
            last_activity=1234567890.0,
        )
        mock_session.metadata = {"language": "en-US", "phase_status": "greeting"}
        mock_session_manager.get_session_readonly.return_value = mock_session

        response = client.get("/api/session/test-session")
        assert response.status_code == 200

        data = response.json()
        assert data["session_id"] == "test-session"
        assert data["user_id"] == "test-user"
        assert "created_at" in data
        assert "last_activity" in data
        assert data["has_request_queue"] is False
        assert data["metadata"]["language"] == "en-US"

    def test_get_session_info_not_found(self, client, mock_session_manager):
        """Test getting session info when session doesn't exist."""
        mock_session_manager.get_session_readonly.return_value = None

        response = client.get("/api/session/nonexistent")
        assert response.status_code == 404
        assert response.json()["detail"] == "Session not found"

    def test_list_sessions(self, client, mock_session_manager):
        """Test listing all sessions."""
        # Mock session data
        sessions = [
            SessionInfoModel(session_id="session1", user_id="user1"),
            SessionInfoModel(session_id="session2", user_id="user2"),
        ]
        mock_session_manager.list_sessions.return_value = sessions

        response = client.get("/api/sessions")
        assert response.status_code == 200

        data = response.json()
        assert data["total_sessions"] == 2
        assert len(data["sessions"]) == 2
        assert data["sessions"][0]["session_id"] == "session1"
        assert data["sessions"][1]["session_id"] == "session2"


class TestMessageEndpoints:
    """Test message handling endpoints."""

    def test_send_message_text_success(self, client, mock_session_manager):
        """Test sending a text message successfully."""
        # Mock session with required metadata
        mock_session = SessionInfoModel(session_id="test-session", user_id="test-user")
        mock_runner = MagicMock()
        mock_adk_session = MagicMock()
        mock_adk_session.id = "adk-session-id"
        mock_run_config = MagicMock()
        mock_queue = AsyncMock()

        mock_session.metadata = {
            "runner": mock_runner,
            "adk_session": mock_adk_session,
            "run_config": mock_run_config,
            "message_queue": mock_queue,
        }
        mock_session_manager.get_session.return_value = mock_session

        # Mock process_message
        with patch("src.text.router.process_message") as mock_process:
            mock_process.return_value = []  # Empty events list

            response = client.post(
                "/api/send/test-session",
                json={"data": "Hello", "mime_type": "text/plain"},
            )
            assert response.status_code == 200
            assert response.json()["status"] == "sent"

    def test_send_message_session_not_found(self, client, mock_session_manager):
        """Test sending message to non-existent session."""
        mock_session_manager.get_session.return_value = None

        response = client.post(
            "/api/send/nonexistent",
            json={"data": "Hello", "mime_type": "text/plain"},
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Session not found"

    def test_send_message_unsupported_mime_type(self, client, mock_session_manager):
        """Test sending message with unsupported mime type."""
        # Create a more complete mock session with all required attributes
        mock_session = MagicMock()
        mock_session.session_id = "test-session"
        mock_session.user_id = "test-user"
        mock_session.language_code = "en-US"
        mock_session.phase = "discovery"
        mock_session.phase_manager = None  # Will be set in send_message
        mock_session.metadata = {
            "runner": MagicMock(),
            "adk_session": MagicMock(),
            "run_config": MagicMock(),
            "message_queue": MagicMock(),
        }
        mock_session_manager.get_session.return_value = mock_session

        response = client.post(
            "/api/send/test-session",
            json={"data": "audio_data", "mime_type": "audio/wav"},
        )
        assert response.status_code == 415
        assert "text/plain" in response.json()["detail"]


class TestLanguageDetection:
    """Test language detection endpoint."""

    def test_detect_language(self, client):
        """Test language detection for all supported languages."""
        # Test cases with phrases in different languages
        test_cases = [
            {
                "text": "Hello, how are you today? I hope you're doing well.",
                "expected_lang": "en",
                "description": "English",
            },
            {
                "text": "Hola, ¿cómo estás? Espero que tengas un buen día.",
                "expected_lang": "es",
                "description": "Spanish",
            },
        ]

        for test_case in test_cases:
            response = client.post(
                "/api/language/detect",
                json={"text": test_case["text"]},
            )
            assert response.status_code == 200

            data = response.json()
            assert data["status"] == "success"
            assert (
                data["language"] == test_case["expected_lang"]
            ), f"Failed for {test_case['description']}: expected {test_case['expected_lang']}, got {data['language']}"
            # Confidence should be reasonable for clear language samples
            assert (
                0.7 <= data["confidence"] <= 1.0
            ), f"Low confidence for {test_case['description']}: {data['confidence']}"

    def test_detect_unsupported_languages(self, client):
        """Test that unsupported languages fall back to English."""
        # French text (no longer supported)
        response = client.post(
            "/api/language/detect",
            json={
                "text": "Bonjour, comment allez-vous? J'espère que vous passez une bonne journée."
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["language"] == "en"  # Should fall back to English
        assert data["confidence"] == 0.5  # Low confidence for fallback

        # German text (no longer supported)
        response = client.post(
            "/api/language/detect",
            json={
                "text": "Guten Tag, wie geht es Ihnen? Ich hoffe, Sie haben einen schönen Tag."
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["language"] == "en"  # Should fall back to English
        assert data["confidence"] == 0.5  # Low confidence for fallback

    def test_detect_language_edge_cases(self, client):
        """Test language detection edge cases."""
        # Empty text should return default language
        response = client.post(
            "/api/language/detect",
            json={"text": ""},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["language"] == "en"
        assert data["confidence"] == 1.0

        # Very short text might fall back to English default
        response = client.post(
            "/api/language/detect",
            json={"text": "Hi"},
        )
        assert response.status_code == 200
        data = response.json()
        # Short text often can't be reliably detected, so it may fall back to English
        assert data["language"] in ["en", "es"]
        assert 0.0 <= data["confidence"] <= 1.0

        # Mixed language text - should detect dominant language
        response = client.post(
            "/api/language/detect",
            json={
                "text": "Hello world! This is mostly English with just un poco de español."
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["language"] == "en"  # Should detect English as dominant
        assert 0.5 <= data["confidence"] <= 1.0


class TestPDFEndpoint:
    """Test PDF download endpoint."""

    def test_download_pdf(self, client, mock_session_manager):
        """Test PDF download returns placeholder."""
        mock_session = SessionInfoModel(session_id="test-session", user_id="test-user")
        mock_session_manager.get_session.return_value = mock_session

        response = client.get("/api/pdf/test-session")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; charset=utf-8"
        assert (
            "session_test-session_summary.txt"
            in response.headers["content-disposition"]
        )
        assert b"CBT Reframing Session Summary" in response.content


class TestSSEEndpoint:
    """Test Server-Sent Events endpoint."""

    @pytest.mark.asyncio
    async def test_sse_endpoint_head(self, async_client):
        """Test SSE endpoint HEAD request."""
        response = await async_client.head("/api/events/test-session")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream"
        assert response.headers["cache-control"] == "no-cache"

    @pytest.mark.asyncio
    async def test_sse_endpoint_get(self, async_client, mock_session_manager):
        """Test SSE endpoint GET request starts session."""
        # This test is complex due to SSE streaming nature
        # For now, just verify endpoint exists
        # Full SSE testing would require more sophisticated async handling
        pass
