"""Tests for main application and middleware integration."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
import json

from main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


class TestMainApplication:
    """Test main application endpoints and configuration."""

    def test_root_endpoint(self, client):
        """Test root endpoint returns API information."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "re-frame API"
        assert "version" in data
        assert "endpoints" in data
        assert data["endpoints"]["health"] == "/api/health"
        assert data["endpoints"]["reframe"] == "/api/reframe"

    def test_cors_headers(self, client):
        """Test CORS headers are properly set."""
        response = client.options(
            "/api/reframe/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            }
        )
        
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "POST" in response.headers["access-control-allow-methods"]

    def test_request_id_header(self, client):
        """Test request ID is added to responses."""
        response = client.get("/api/health")
        
        assert response.status_code == 200
        assert "x-request-id" in response.headers
        assert len(response.headers["x-request-id"]) > 0

    def test_global_exception_handler(self, client):
        """Test global exception handler."""
        # Create an endpoint that raises an exception
        @app.get("/test-error")
        async def test_error():
            raise Exception("Test exception")
        
        response = client.get("/test-error")
        
        assert response.status_code == 500
        data = response.json()
        assert data["error"] == "Internal server error"
        assert "request_id" in data


class TestRateLimiting:
    """Test rate limiting middleware."""

    def test_rate_limit_enforcement(self, client):
        """Test rate limits are enforced."""
        # Make requests up to the limit
        for i in range(10):
            response = client.post(
                "/api/reframe/",
                json={"thought": f"Test thought {i}"}
            )
            assert response.status_code in [200, 429]
            
            if response.status_code == 429:
                # Hit rate limit
                data = response.json()
                assert "Rate limit exceeded" in data["detail"]
                break

    def test_rate_limit_headers(self, client):
        """Test rate limit headers are included."""
        response = client.get("/api/health")
        
        assert "x-ratelimit-limit" in response.headers
        assert "x-ratelimit-remaining" in response.headers
        assert "x-ratelimit-reset" in response.headers

    def test_exempt_paths_not_rate_limited(self, client):
        """Test certain paths are exempt from rate limiting."""
        # Health check should always work
        for _ in range(20):
            response = client.get("/api/health")
            assert response.status_code == 200


class TestAbusePreventionMiddleware:
    """Test abuse prevention middleware."""

    def test_toxic_content_detection(self, client):
        """Test toxic content is blocked."""
        with patch("middleware.abuse_prevention.ToxicityChecker.check_toxicity") as mock_check:
            mock_check.return_value = {"is_toxic": True, "score": 0.9}
            
            response = client.post(
                "/api/reframe/",
                json={"thought": "I hate everyone and everything"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is False
            assert "supportive" in data.get("response", "").lower()

    def test_pattern_abuse_detection(self, client):
        """Test pattern-based abuse detection."""
        # Simulate multiple suspicious requests
        with patch("middleware.abuse_prevention.request_history") as mock_history:
            # Mock suspicious pattern
            mock_history.get.return_value = [
                {"timestamp": 0, "path": f"/api/endpoint{i}"} 
                for i in range(20)
            ]
            
            response = client.post(
                "/api/reframe/",
                json={"thought": "Normal thought"}
            )
            
            # Should be blocked due to suspicious pattern
            if response.status_code == 429:
                data = response.json()
                assert "suspicious activity" in data.get("detail", "").lower()

    def test_sql_injection_prevention(self, client):
        """Test SQL injection attempts are blocked."""
        response = client.post(
            "/api/reframe/",
            json={"thought": "'; DROP TABLE users; --"}
        )
        
        # Should either be blocked or sanitized
        assert response.status_code in [200, 400, 429]
        if response.status_code == 200:
            data = response.json()
            # If it gets through, it should be handled safely
            assert "DROP TABLE" not in data.get("response", "")


class TestMiddlewareIntegration:
    """Test integration of all middleware components."""

    def test_middleware_order(self, client):
        """Test middleware are applied in correct order."""
        # Make a request and check headers to verify middleware order
        response = client.get("/api/health")
        
        # Should have headers from various middleware
        assert "x-request-id" in response.headers  # Logging middleware
        assert "x-ratelimit-limit" in response.headers  # Rate limiting
        
    def test_middleware_error_propagation(self, client):
        """Test errors propagate correctly through middleware."""
        with patch("api.reframe.session_manager.process_user_input") as mock_process:
            mock_process.side_effect = Exception("Processing error")
            
            response = client.post(
                "/api/reframe/",
                json={"thought": "Test thought"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is False
            assert "unexpected error" in data["response"]


class TestAPIDocumentation:
    """Test API documentation generation."""

    def test_openapi_schema_generation(self, client):
        """Test OpenAPI schema is properly generated."""
        response = client.get("/api/openapi.json")
        
        assert response.status_code == 200
        schema = response.json()
        
        # Check OpenAPI version
        assert schema["openapi"].startswith("3.")
        
        # Check API info
        assert schema["info"]["title"] == "re-frame API"
        assert "description" in schema["info"]
        
        # Check paths are documented
        assert "/api/reframe/" in schema["paths"]
        assert "/api/health" in schema["paths"]
        
        # Check reframe endpoint documentation
        reframe_post = schema["paths"]["/api/reframe/"]["post"]
        assert "summary" in reframe_post
        assert "requestBody" in reframe_post
        assert "responses" in reframe_post

    def test_schema_includes_models(self, client):
        """Test schema includes request/response models."""
        response = client.get("/api/openapi.json")
        schema = response.json()
        
        # Check component schemas
        assert "components" in schema
        assert "schemas" in schema["components"]
        
        # Check specific models
        assert "ReframeRequest" in schema["components"]["schemas"]
        assert "ReframeResponse" in schema["components"]["schemas"]
        
        # Check model properties
        reframe_request = schema["components"]["schemas"]["ReframeRequest"]
        assert "thought" in reframe_request["properties"]
        assert reframe_request["properties"]["thought"]["minLength"] == 5
        assert reframe_request["properties"]["thought"]["maxLength"] == 2000

    def test_api_tags(self, client):
        """Test API endpoints are properly tagged."""
        response = client.get("/api/openapi.json")
        schema = response.json()
        
        # Check tags are defined
        assert "tags" in schema
        tag_names = [tag["name"] for tag in schema["tags"]]
        assert "health" in tag_names
        assert "reframe" in tag_names

    def test_response_examples(self, client):
        """Test API documentation includes response examples."""
        response = client.get("/api/openapi.json")
        schema = response.json()
        
        # Check for response examples
        reframe_responses = schema["paths"]["/api/reframe/"]["post"]["responses"]
        assert "200" in reframe_responses
        assert "422" in reframe_responses  # Validation error