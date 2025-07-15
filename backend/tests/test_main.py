# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for the FastAPI main application."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

# Patch all external dependencies before importing the app
with (
    patch("src.main.create_cbt_assistant", MagicMock()),
    patch("src.main.session_manager", MagicMock()),
    patch("src.main.AudioConverter", MagicMock()),
):
    from src.main import app

from src.models import (
    HealthCheckResponse,
    LanguageDetectionRequest,
    MessageRequest,
    SessionInfo,
)


@pytest.fixture
def mock_session_manager():
    """Mock session manager for tests."""
    with patch("src.main.session_manager") as mock:
        # Setup default behaviors
        mock.get_session.return_value = None
        mock.get_session_readonly.return_value = None
        mock.sessions = {}
        mock.get_active_session_count.return_value = 0
        # Make async methods
        mock.start = AsyncMock()
        mock.stop = AsyncMock()
        yield mock


@pytest.fixture
def mock_audio_converter():
    """Mock audio converter for tests."""
    with patch("src.main.AudioConverter") as mock_class:
        # Mock class attributes and methods
        mock_class.SUPPORTED_INPUT_FORMATS = ["audio/wav", "audio/webm", "audio/pcm"]
        mock_class.validate_pcm_data = MagicMock(return_value=True)
        mock_class.convert_to_pcm = MagicMock(
            return_value=(
                b"pcm_data",
                {
                    "sample_rate": 16000,
                    "conversion_time": 10.5,
                    "input_size": 1000,
                    "output_size": 500,
                },
            )
        )
        yield mock_class


@pytest.fixture
def mock_create_cbt_assistant():
    """Mock CBT assistant creation."""
    with patch("src.main.create_cbt_assistant") as mock:
        mock_agent = MagicMock()
        mock.return_value = mock_agent
        yield mock


@pytest.fixture
def client(mock_session_manager, mock_audio_converter, mock_create_cbt_assistant):
    """Create a test client for the FastAPI app with mocked dependencies."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
async def async_client(
    mock_session_manager, mock_audio_converter, mock_create_cbt_assistant
):
    """Create an async test client for the FastAPI app with mocked dependencies."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


class TestHealthEndpoint:
    """Test the health check endpoint."""

    def test_health_check(self, client):
        """Test that health check returns expected response."""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "CBT Reframing Assistant API"
        assert data["version"] == "1.0.0"
        assert "timestamp" in data

        # Validate response model
        health_response = HealthCheckResponse(**data)
        assert health_response.status == "healthy"


class TestRootEndpoint:
    """Test the root endpoint."""

    @patch("pathlib.Path.exists")
    def test_root_without_index_html(self, mock_exists, client):
        """Test root endpoint when index.html doesn't exist."""
        mock_exists.return_value = False

        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert data["message"] == "CBT Assistant API"
        assert data["docs"] == "/docs"
        assert data["health"] == "/health"

    @patch("pathlib.Path.exists")
    @patch("src.main.FileResponse")
    def test_root_with_index_html(self, mock_file_response, mock_exists, client):
        """Test root endpoint when index.html exists."""
        mock_exists.return_value = True

        # Mock FileResponse to return a regular Response
        from fastapi import Response

        mock_file_response.return_value = Response(
            content=b"<html>Test</html>", media_type="text/html; charset=utf-8"
        )

        response = client.get("/")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/html; charset=utf-8"
        assert response.content == b"<html>Test</html>"


class TestSessionEndpoints:
    """Test session-related endpoints."""

    def test_get_session_info_found(self, client, mock_session_manager):
        """Test getting session info when session exists."""
        mock_session = MagicMock()
        mock_session.session_id = "test-123"
        mock_session.user_id = "user-456"
        mock_session.created_at = 1234567890.0
        mock_session.last_activity = 1234567900.0
        mock_session.age_seconds = 10.0
        mock_session.inactive_seconds = 5.0
        mock_session.request_queue = MagicMock()
        mock_session.metadata = {}
        mock_session_manager.get_session_readonly.return_value = mock_session

        response = client.get("/api/session/test-123")
        assert response.status_code == 200

        data = response.json()
        assert data["session_id"] == "test-123"
        assert data["user_id"] == "user-456"
        assert data["has_request_queue"] is True

        # Validate response model
        session_info = SessionInfo(**data)
        assert session_info.session_id == "test-123"

    def test_get_session_info_not_found(self, client, mock_session_manager):
        """Test getting session info when session doesn't exist."""
        mock_session_manager.get_session_readonly.return_value = None

        response = client.get("/api/session/test-123")
        assert response.status_code == 404
        assert response.json()["detail"] == "Session not found"

    def test_list_sessions(self, client, mock_session_manager):
        """Test listing all sessions."""
        mock_session = MagicMock()
        mock_session.session_id = "test-123"
        mock_session.age_seconds = 60.0
        mock_session.inactive_seconds = 10.0

        mock_session_manager.sessions = {"test-123": mock_session}
        mock_session_manager.get_active_session_count.return_value = 1

        response = client.get("/api/sessions")
        assert response.status_code == 200

        data = response.json()
        assert data["total_sessions"] == 1
        assert len(data["sessions"]) == 1
        assert data["sessions"][0]["session_id"] == "test-123"


class TestMessageEndpoints:
    """Test message-related endpoints."""

    def test_send_message_text_success(self, client, mock_session_manager):
        """Test sending a text message successfully."""
        mock_session = MagicMock()
        mock_queue = MagicMock()
        mock_session.request_queue = mock_queue
        mock_session_manager.get_session.return_value = mock_session

        request_data = MessageRequest(
            mime_type="text/plain", data="SGVsbG8gd29ybGQ="  # "Hello world" in base64
        )

        response = client.post("/api/send/test-123", json=request_data.model_dump())
        assert response.status_code == 200
        assert response.json()["status"] == "sent"
        assert response.json()["error"] is None

        # Verify the message was sent to the queue
        mock_queue.send_content.assert_called_once()

    def test_send_message_session_not_found(self, client, mock_session_manager):
        """Test sending message when session doesn't exist."""
        mock_session_manager.get_session.return_value = None

        request_data = MessageRequest(mime_type="text/plain", data="SGVsbG8gd29ybGQ=")

        response = client.post("/api/send/test-123", json=request_data.model_dump())
        assert response.status_code == 404
        assert response.json()["detail"] == "Session not found"

    def test_send_message_unsupported_mime_type(self, client, mock_session_manager):
        """Test sending message with unsupported mime type."""
        mock_session = MagicMock()
        mock_session.request_queue = MagicMock()
        mock_session.metadata = {}
        mock_session_manager.get_session.return_value = mock_session

        request_data = MessageRequest(
            mime_type="application/pdf", data="SGVsbG8gd29ybGQ="
        )

        response = client.post("/api/send/test-123", json=request_data.model_dump())
        assert response.status_code == 415
        assert "Mime type not supported" in response.json()["detail"]

    def test_send_message_audio_success(
        self, client, mock_session_manager, mock_audio_converter
    ):
        """Test sending audio message successfully."""
        mock_session = MagicMock()
        mock_queue = MagicMock()
        mock_session.request_queue = mock_queue
        mock_session_manager.get_session.return_value = mock_session

        # Mock successful audio conversion
        mock_audio_converter.convert_to_pcm.return_value = (
            b"pcm_data",
            {
                "sample_rate": 16000,
                "conversion_time": 10.5,
                "input_size": 1000,
                "output_size": 500,
            },
        )
        mock_audio_converter.validate_pcm_data.return_value = True

        request_data = MessageRequest(
            mime_type="audio/wav", data="YXVkaW9fZGF0YQ=="  # "audio_data" in base64
        )

        response = client.post("/api/send/test-123", json=request_data.model_dump())
        assert response.status_code == 200
        assert response.json()["status"] == "sent"

        # Verify audio was converted and sent
        mock_audio_converter.convert_to_pcm.assert_called_once()
        mock_queue.send_realtime.assert_called_once()

    def test_send_message_webm_not_implemented(self, client, mock_session_manager):
        """Test sending WebM audio returns not implemented error."""
        mock_session = MagicMock()
        mock_session.request_queue = MagicMock()
        mock_session.metadata = {}
        mock_session_manager.get_session.return_value = mock_session

        request_data = MessageRequest(mime_type="audio/webm", data="YXVkaW9fZGF0YQ==")

        response = client.post("/api/send/test-123", json=request_data.model_dump())
        assert response.status_code == 501
        assert "WebM audio conversion is not implemented" in response.json()["detail"]

    def test_send_message_audio_conversion_error(
        self, client, mock_session_manager, mock_audio_converter
    ):
        """Test audio conversion error returns proper status."""
        mock_session = MagicMock()
        mock_session.request_queue = MagicMock()
        mock_session.metadata = {}
        mock_session_manager.get_session.return_value = mock_session

        # Mock conversion error
        mock_audio_converter.convert_to_pcm.return_value = (
            None,
            {
                "error": "Invalid audio format",
                "conversion_time": 5.0,
                "input_size": 1000,
                "output_size": 0,
            },
        )

        request_data = MessageRequest(mime_type="audio/wav", data="YXVkaW9fZGF0YQ==")

        response = client.post("/api/send/test-123", json=request_data.model_dump())
        assert response.status_code == 422
        assert "Audio conversion failed" in response.json()["detail"]


class TestSSEEndpoint:
    """Test Server-Sent Events endpoint."""

    @pytest.mark.asyncio
    async def test_sse_endpoint_text_mode(self, async_client, mock_session_manager):
        """Test SSE endpoint in text mode."""
        mock_session = MagicMock()
        mock_session.session_id = "test-123"
        mock_session.response_queue = AsyncMock()
        mock_session.response_queue.get.side_effect = [
            ("content", "Hello"),
            ("turn_complete", {"turn_complete": True}),
        ]
        mock_session_manager.get_session.return_value = mock_session

        response = await async_client.get(
            "/api/events/test-123?is_audio=false&language=en-US", follow_redirects=False
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

    # Removed test_sse_endpoint_session_not_found as SSE endpoint creates new sessions


class TestLanguageDetection:
    """Test language detection endpoint."""

    def test_detect_language_not_implemented(self, client):
        """Test language detection endpoint (currently not implemented)."""
        request_data = LanguageDetectionRequest(text="Hello world")

        response = client.post("/api/language/detect", json=request_data.model_dump())
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "not_implemented"
        assert "will be implemented" in data["message"]
        assert data["language"] is None
        assert data["confidence"] is None


class TestPDFEndpoint:
    """Test PDF download endpoint."""

    def test_download_pdf(self, client):
        """Test PDF download endpoint."""
        response = client.get("/api/pdf/test-123")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert (
            response.headers["content-disposition"]
            == 'attachment; filename="reframe-summary-test-123.pdf"'
        )
        assert response.content.startswith(b"Mock PDF content")


class TestStartupShutdown:
    """Test application startup and shutdown events."""

    @pytest.mark.asyncio
    async def test_startup_event(self, mock_session_manager):
        """Test startup event handler."""
        mock_session_manager.start = AsyncMock()

        # Import and call the startup handler directly
        from src.main import startup_event

        await startup_event()
        mock_session_manager.start.assert_called_once()

    @pytest.mark.asyncio
    async def test_shutdown_event(self, mock_session_manager):
        """Test shutdown event handler."""
        mock_session_manager.stop = AsyncMock()

        # Import and call the shutdown handler directly
        from src.main import shutdown_event

        await shutdown_event()
        mock_session_manager.stop.assert_called_once()


class TestCORSConfiguration:
    """Test CORS configuration."""

    def test_cors_headers(self, client):
        """Test that CORS headers are properly set."""
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers


class TestOpenAPIGeneration:
    """Test OpenAPI schema generation."""

    def test_openapi_schema(self, client):
        """Test that OpenAPI schema can be generated."""
        response = client.get("/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        assert schema["openapi"] == "3.1.0"
        assert "CBT Reframing Assistant API" in schema["info"]["title"]

        # Verify key endpoints are documented
        paths = schema["paths"]
        assert "/health" in paths
        assert "/api/send/{session_id}" in paths
        assert "/api/events/{session_id}" in paths
        assert "/api/sessions" in paths

        # Verify models are defined
        components = schema["components"]["schemas"]
        assert "HealthCheckResponse" in components
        assert "MessageRequest" in components
        assert "MessageResponse" in components
        assert "SessionInfo" in components
