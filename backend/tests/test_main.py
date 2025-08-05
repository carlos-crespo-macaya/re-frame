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

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

# Patch all external dependencies before importing the app
with (
    patch("src.text.router.create_cbt_assistant", MagicMock()),
    patch("src.utils.session_manager.session_manager", MagicMock()),
    patch("src.utils.audio_converter.AudioConverter", MagicMock()),
):
    from src.main import app

from src.models.api import HealthCheckResponse


@pytest.fixture
def mock_session_manager():
    """Mock session manager for tests."""
    with patch("src.utils.session_manager.session_manager") as mock:
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
def mock_voice_session_manager():
    """Mock voice session manager for tests."""
    with patch("src.voice.session_manager.voice_session_manager") as mock:
        # Make async methods
        mock.start = AsyncMock()
        mock.stop = AsyncMock()
        yield mock


@pytest.fixture
def client(mock_session_manager, mock_voice_session_manager):
    """Create a test client for the FastAPI app with mocked dependencies."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
async def async_client(mock_session_manager, mock_voice_session_manager):
    """Create an async test client for the FastAPI app with mocked dependencies."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


class TestHealthEndpoint:
    """Test the health check endpoint."""

    def test_health_check(self, client):
        """Test that health check returns expected response."""
        response = client.get("/api/health")
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
        assert response.content == b"<html>Test</html>"
        assert response.headers["content-type"] == "text/html; charset=utf-8"


class TestMetricsEndpoint:
    """Test the metrics endpoint."""

    @patch("src.utils.metrics_router.get_performance_monitor")
    def test_get_metrics(self, mock_get_monitor, client):
        """Test that metrics endpoint returns performance data."""
        # Mock performance monitor to return realistic metrics
        mock_monitor = MagicMock()
        mock_monitor.get_metrics.return_value = {
            "uptime_seconds": 3600.0,
            "total_requests": 100,
            "error_count": 1,
            "error_rate": 0.01,
            "throughput_rps": 0.028,
            "active_sessions": 0,
            "response_times": {
                "min": 0.01,
                "max": 0.1,
                "avg": 0.05,
                "p50": 0.045,
                "p95": 0.09,
                "p99": 0.099,
            },
        }
        mock_get_monitor.return_value = mock_monitor

        response = client.get("/api/metrics")
        assert response.status_code == 200

        data = response.json()
        assert data["total_requests"] == 100
        assert data["error_rate"] == 0.01
        assert data["active_sessions"] == 0
        assert "uptime_seconds" in data
        assert data["uptime_seconds"] > 0


class TestStartupShutdown:
    """Test lifespan events."""

    @pytest.mark.asyncio
    async def test_lifespan(self):
        """Test that lifespan properly starts and stops session managers."""
        with (
            patch("src.main.session_manager") as mock_session_manager,
            patch("src.main.voice_session_manager") as mock_voice_session_manager,
            patch("src.main.get_performance_monitor") as mock_get_monitor,
        ):
            # Setup mocks
            mock_session_manager.start = AsyncMock()
            mock_session_manager.stop = AsyncMock()
            mock_voice_session_manager.start = AsyncMock()
            mock_voice_session_manager.stop = AsyncMock()

            # Create monitor mock that returns an async function
            mock_monitor = MagicMock()

            # Create a real async function that will be used as the task
            async def mock_log_periodic():
                try:
                    await asyncio.sleep(300)  # Simulate periodic logging
                except asyncio.CancelledError:
                    raise

            mock_monitor.log_periodic_summary = mock_log_periodic
            mock_get_monitor.return_value = mock_monitor

            # Import lifespan
            from src.main import app, lifespan

            # Run lifespan context manager
            async with lifespan(app):
                # Verify startup calls
                mock_session_manager.start.assert_called_once()
                mock_voice_session_manager.start.assert_called_once()
                assert hasattr(app.state, "monitor_task")
                assert isinstance(app.state.monitor_task, asyncio.Task)

            # Verify shutdown calls
            mock_session_manager.stop.assert_called_once()
            mock_voice_session_manager.stop.assert_called_once()
            # The task should be cancelled
            assert app.state.monitor_task.cancelled()


class TestCORSConfiguration:
    """Test CORS middleware configuration."""

    def test_cors_headers(self, client):
        """Test that CORS headers are set correctly for allowed origin."""
        # Test GET request with Origin header to check CORS
        response = client.get(
            "/api/health", headers={"Origin": "http://localhost:3000"}
        )
        assert response.status_code == 200
        # Check that CORS headers are present
        assert "access-control-allow-origin" in response.headers
        assert (
            response.headers["access-control-allow-origin"] == "http://localhost:3000"
        )


class TestOpenAPIGeneration:
    """Test OpenAPI schema generation."""

    def test_openapi_schema(self, client):
        """Test that OpenAPI schema is generated correctly."""
        response = client.get("/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        assert schema["info"]["title"] == "CBT Reframing Assistant API"
        assert schema["info"]["version"] == "1.0.0"
        assert "/api/health" in schema["paths"]
        assert "/api/metrics" in schema["paths"]

        # Check that text and voice endpoints are included via routers
        assert "/api/events/{session_id}" in schema["paths"]  # Text router
        assert "/api/voice/sessions" in schema["paths"]  # Voice router
