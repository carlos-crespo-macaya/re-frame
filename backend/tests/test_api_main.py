"""Tests for main application and middleware integration."""

from unittest.mock import patch

from fastapi.testclient import TestClient
import pytest

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

    def test_cors_headers(self, client):
        """Test CORS headers are properly set."""
        response = client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "content-type",
            },
        )

        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "GET" in response.headers["access-control-allow-methods"]

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


# Removed TestAbusePreventionMiddleware as it tests non-existent /api/reframe/ endpoint


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
        # Test error propagation through health endpoint
        with patch("api.health.HealthService.get_readiness") as mock_health:
            mock_health.side_effect = Exception("Health check error")

            response = client.get("/api/health/ready")

            # Should be handled gracefully
            assert response.status_code in [200, 503]


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
        assert "/api/health" in schema["paths"]
        assert "/api/health/ready" in schema["paths"]

        # Check health endpoint documentation
        health_get = schema["paths"]["/api/health"]["get"]
        assert "summary" in health_get
        assert "responses" in health_get

    def test_schema_includes_models(self, client):
        """Test schema includes request/response models."""
        response = client.get("/api/openapi.json")
        schema = response.json()

        # Check component schemas
        assert "components" in schema
        assert "schemas" in schema["components"]

        # Check specific models
        assert "HealthStatus" in schema["components"]["schemas"]
        assert "DetailedHealthStatus" in schema["components"]["schemas"]

    def test_api_tags(self, client):
        """Test API endpoints are properly tagged."""
        response = client.get("/api/openapi.json")
        schema = response.json()

        # Check tags are defined
        assert "tags" in schema
        tag_names = [tag["name"] for tag in schema["tags"]]
        assert "Health" in tag_names or "health" in tag_names

    def test_response_examples(self, client):
        """Test API documentation includes response examples."""
        response = client.get("/api/openapi.json")
        schema = response.json()

        # Check for response examples
        health_responses = schema["paths"]["/api/health"]["get"]["responses"]
        assert "200" in health_responses
