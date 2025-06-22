"""Comprehensive tests for the reframe API endpoints."""

import json
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def mock_session_manager():
    """Mock the ADK session manager."""
    with patch("api.reframe.session_manager") as mock:
        yield mock


class TestReframeEndpoint:
    """Test the main reframe endpoint."""

    def test_reframe_success(self, client, mock_session_manager):
        """Test successful reframing request."""
        # Mock successful response
        mock_session_manager.process_user_input = AsyncMock(
            return_value={
                "success": True,
                "response": json.dumps({
                    "main_response": "Here's a different way to think about it: Your concern is valid, but it might not be as catastrophic as it feels."
                }),
                "transparency": {
                    "techniques_applied": ["cognitive_restructuring", "decatastrophizing"],
                    "reasoning_path": ["Identified catastrophizing", "Applied balanced thinking"],
                },
                "workflow_stage": "synthesis",
            }
        )

        response = client.post(
            "/api/reframe/",
            json={"thought": "Everyone will judge me at the meeting"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "different way to think" in data["response"]
        assert len(data["techniques_used"]) == 2
        assert "cognitive_restructuring" in data["techniques_used"]

    def test_reframe_with_context(self, client, mock_session_manager):
        """Test reframing with additional context."""
        mock_session_manager.process_user_input = AsyncMock(
            return_value={
                "success": True,
                "response": "Your past experiences are influencing your current perception.",
                "transparency": {"techniques_applied": ["evidence_analysis"]},
            }
        )

        response = client.post(
            "/api/reframe/",
            json={
                "thought": "I'll fail the presentation",
                "context": "Failed a presentation 5 years ago"
            }
        )

        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_reframe_validation_errors(self, client):
        """Test input validation."""
        # Thought too short
        response = client.post("/api/reframe/", json={"thought": "Bad"})
        assert response.status_code == 422

        # Thought too long
        response = client.post("/api/reframe/", json={"thought": "x" * 2001})
        assert response.status_code == 422

        # Missing thought
        response = client.post("/api/reframe/", json={})
        assert response.status_code == 422

    def test_reframe_crisis_detection(self, client, mock_session_manager):
        """Test crisis response handling."""
        mock_session_manager.process_user_input = AsyncMock(
            return_value={
                "success": True,
                "crisis_flag": True,
                "response": "Crisis support message",
                "transparency": {"crisis_detected": True},
            }
        )

        response = client.post(
            "/api/reframe/",
            json={"thought": "I don't want to go on anymore"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "crisis helpline" in data["response"] or "mental health professional" in data["response"]
        assert "crisis_detection" in data["techniques_used"]

    def test_reframe_processing_error(self, client, mock_session_manager):
        """Test handling of processing errors."""
        mock_session_manager.process_user_input = AsyncMock(
            return_value={
                "success": False,
                "error": "Failed to process thought",
                "workflow_stage": "intake",
            }
        )

        response = client.post(
            "/api/reframe/",
            json={"thought": "My thought about the situation"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "wasn't able to process" in data["response"]
        assert data["error"] == "Failed to process thought"

    def test_reframe_exception_handling(self, client, mock_session_manager):
        """Test exception handling."""
        mock_session_manager.process_user_input = AsyncMock(
            side_effect=Exception("Unexpected error")
        )

        response = client.post(
            "/api/reframe/",
            json={"thought": "This should cause an error"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "unexpected error occurred" in data["response"]
        assert data["error"] == "Internal server error"

    def test_reframe_malformed_json_response(self, client, mock_session_manager):
        """Test handling of malformed JSON in response."""
        mock_session_manager.process_user_input = AsyncMock(
            return_value={
                "success": True,
                "response": "This is plain text, not JSON",
                "transparency": {"techniques_applied": ["reframing"]},
            }
        )

        response = client.post(
            "/api/reframe/",
            json={"thought": "I'm worried about tomorrow"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["response"] == "This is plain text, not JSON"

    @pytest.mark.parametrize("thought,expected_technique", [
        ("Everything is terrible and will never get better", "decatastrophizing"),
        ("They must think I'm stupid", "cognitive_restructuring"),
        ("I should just avoid all social situations", "behavioral_experiments"),
    ])
    def test_reframe_various_thought_patterns(self, client, mock_session_manager, thought, expected_technique):
        """Test various thought patterns get appropriate responses."""
        mock_session_manager.process_user_input = AsyncMock(
            return_value={
                "success": True,
                "response": f"Reframed: {thought}",
                "transparency": {"techniques_applied": [expected_technique]},
            }
        )

        response = client.post("/api/reframe/", json={"thought": thought})
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert expected_technique in data["techniques_used"]


class TestTechniquesEndpoint:
    """Test the techniques listing endpoint."""

    def test_list_techniques(self, client):
        """Test techniques listing."""
        response = client.get("/api/reframe/techniques")
        
        assert response.status_code == 200
        data = response.json()
        assert "techniques" in data
        assert "cognitive_restructuring" in data["techniques"]
        
        # Check technique structure
        technique = data["techniques"]["cognitive_restructuring"]
        assert "name" in technique
        assert "description" in technique
        assert "helpful_for" in technique
        assert isinstance(technique["helpful_for"], list)

    def test_all_techniques_present(self, client):
        """Test all expected techniques are listed."""
        response = client.get("/api/reframe/techniques")
        techniques = response.json()["techniques"]
        
        expected_techniques = [
            "cognitive_restructuring",
            "evidence_analysis",
            "decatastrophizing",
            "behavioral_experiments",
            "self_compassion"
        ]
        
        for technique in expected_techniques:
            assert technique in techniques


class TestSessionEndpoints:
    """Test session-related endpoints."""

    def test_get_session_history_exists(self, client, mock_session_manager):
        """Test retrieving existing session history."""
        mock_history = {
            "session_id": "test-123",
            "created_at": "2024-01-01T00:00:00",
            "interactions": [
                {"thought": "Test thought", "response": "Test response"}
            ]
        }
        mock_session_manager.get_session_history.return_value = mock_history

        response = client.get("/api/reframe/session/test-123/history")
        
        assert response.status_code == 200
        data = response.json()
        assert data["session"]["session_id"] == "test-123"
        assert len(data["session"]["interactions"]) == 1

    def test_get_session_history_not_found(self, client, mock_session_manager):
        """Test retrieving non-existent session."""
        mock_session_manager.get_session_history.return_value = None

        response = client.get("/api/reframe/session/nonexistent/history")
        
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["error"] == "Session not found"


class TestObservabilityEndpoints:
    """Test observability endpoints."""

    def test_get_performance_metrics(self, client):
        """Test performance metrics endpoint."""
        with patch("REDACTED") as mock_obs:
            mock_obs.get_performance_summary.return_value = {
                "avg_response_time": 0.5,
                "total_requests": 100
            }
            mock_obs.get_error_analysis.return_value = {
                "error_rate": 0.02,
                "common_errors": []
            }

            response = client.get("/api/reframe/observability/performance")
            
            assert response.status_code == 200
            data = response.json()
            assert "performance" in data
            assert "errors" in data
            assert data["performance"]["avg_response_time"] == 0.5

    def test_enable_debug_mode(self, client):
        """Test enabling debug mode."""
        with patch("REDACTED") as mock_obs:
            response = client.post("/api/reframe/observability/debug/enable")
            
            assert response.status_code == 200
            assert "Debug mode enabled" in response.json()["message"]
            mock_obs.enable_debug_mode.assert_called_once()

    def test_disable_debug_mode(self, client):
        """Test disabling debug mode."""
        with patch("REDACTED") as mock_obs:
            response = client.post("/api/reframe/observability/debug/disable")
            
            assert response.status_code == 200
            assert "Debug mode disabled" in response.json()["message"]
            mock_obs.disable_debug_mode.assert_called_once()


class TestAPIIntegration:
    """Integration tests for API workflows."""

    @pytest.mark.asyncio
    async def test_full_reframe_workflow(self, client):
        """Test complete reframe workflow with real components."""
        # This would be an integration test with actual components
        # For now, we'll skip as it requires full setup
        pytest.skip("Integration test requires full component setup")

    def test_api_versioning(self, client):
        """Test API versioning is properly set up."""
        response = client.get("/")
        data = response.json()
        
        assert "version" in data
        assert data["version"] == "0.1.0"  # From settings

    def test_REDACTED(self, client):
        """Test API documentation endpoints are accessible."""
        # OpenAPI spec
        response = client.get("/api/openapi.json")
        assert response.status_code == 200
        assert "openapi" in response.json()
        
        # Note: Swagger UI and ReDoc require HTML responses
        # which TestClient doesn't handle well, so we just check they don't 404
        response = client.get("/api/docs")
        assert response.status_code != 404
        
        response = client.get("/api/redoc")
        assert response.status_code != 404