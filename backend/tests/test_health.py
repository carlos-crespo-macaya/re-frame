"""Tests for health check endpoints."""
import sys
from pathlib import Path

# Add the parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint returns expected information."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "re-frame API"
    assert "version" in data
    assert "endpoints" in data


def test_health_check():
    """Test basic health check endpoint."""
    response = client.get("/api/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["service"] == "re-frame API"


def test_detailed_health_check():
    """Test detailed health check endpoint."""
    response = client.get("/api/health/detailed")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "components" in data
    assert "configuration" in data

    # Check component statuses
    components = data["components"]
    assert components["api"] == "healthy"
    assert components["rate_limiting"] == "healthy"
    assert components["logging"] == "healthy"
