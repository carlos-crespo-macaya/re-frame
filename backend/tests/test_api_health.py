"""Tests for health check endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_basic_health_check(self, client):
        """Test basic health endpoint."""
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data
        assert "service" in data
        assert data["service"] == "re-frame-backend"

    def test_detailed_health_check(self, client):
        """Test detailed health check."""
        with patch("REDACTED") as mock_ai_health:
            mock_ai_health.return_value = {
                "status": "ok",
                "model": "gemini-1.5-flash",
                "available": True
            }
            
            response = client.get("/api/health/detailed")
            
            assert response.status_code == 200
            data = response.json()
            
            # Check overall structure
            assert data["status"] == "ok"
            assert "timestamp" in data
            assert "checks" in data
            
            # Check individual health checks
            checks = data["checks"]
            assert "google_ai" in checks
            assert checks["google_ai"]["status"] == "ok"

    def test_health_check_with_failing_dependency(self, client):
        """Test health check when a dependency is failing."""
        with patch("REDACTED") as mock_ai_health:
            mock_ai_health.return_value = {
                "status": "error",
                "error": "API key invalid"
            }
            
            response = client.get("/api/health/detailed")
            
            # Should still return 200 but indicate degraded status
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "degraded"
            assert data["checks"]["google_ai"]["status"] == "error"

    def test_health_check_exception_handling(self, client):
        """Test health check handles exceptions gracefully."""
        with patch("REDACTED") as mock_ai_health:
            mock_ai_health.side_effect = Exception("Connection failed")
            
            response = client.get("/api/health/detailed")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "degraded"
            assert "error" in data["checks"]["google_ai"]

    def test_liveness_probe(self, client):
        """Test Kubernetes liveness probe endpoint."""
        response = client.get("/api/health/live")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"

    def test_readiness_probe(self, client):
        """Test Kubernetes readiness probe endpoint."""
        with patch("REDACTED") as mock_ai_health:
            # When all dependencies are healthy
            mock_ai_health.return_value = {"status": "ok"}
            
            response = client.get("/api/health/ready")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ready"
            
            # When dependencies are not healthy
            mock_ai_health.return_value = {"status": "error"}
            
            response = client.get("/api/health/ready")
            
            # Should return 503 when not ready
            assert response.status_code == 503
            data = response.json()
            assert data["status"] == "not_ready"

    def test_startup_probe(self, client):
        """Test Kubernetes startup probe endpoint."""
        response = client.get("/api/health/startup")
        
        # Startup probe may return 503 if tested immediately after import
        assert response.status_code in [200, 503]
        data = response.json()
        
        if response.status_code == 200:
            assert data["status"] == "started"
            assert "startup_time" in data
            assert "uptime_seconds" in data
        else:
            assert data["status"] == "starting"
            assert "uptime_seconds" in data