"""Tests for rate limiting middleware."""

import time
from unittest.mock import Mock

from fastapi import FastAPI, Request
from fastapi.responses import Response
from fastapi.testclient import TestClient

from middleware.rate_limiting import (
    RateLimiter,
    RateLimitExceeded,
    RateLimitMiddleware,
    get_client_ip,
)


class TestRateLimiter:
    """Test the RateLimiter class."""

    def test_initialization(self):
        """Test RateLimiter initialization."""
        limiter = RateLimiter(max_requests=10, window_seconds=3600)
        assert limiter.max_requests == 10
        assert limiter.window_seconds == 3600
        assert len(limiter.requests) == 0

    def test_is_allowed_first_request(self):
        """Test that first request is always allowed."""
        limiter = RateLimiter(max_requests=10, window_seconds=3600)
        assert limiter.is_allowed("client1") is True

    def test_is_allowed_within_limit(self):
        """Test requests within limit are allowed."""
        limiter = RateLimiter(max_requests=3, window_seconds=3600)

        # Make 3 requests - all should be allowed
        for _ in range(3):
            assert limiter.is_allowed("client1") is True

    def test_is_allowed_exceeds_limit(self):
        """Test that exceeding limit blocks requests."""
        limiter = RateLimiter(max_requests=2, window_seconds=3600)

        # First 2 requests allowed
        assert limiter.is_allowed("client1") is True
        assert limiter.is_allowed("client1") is True

        # Third request blocked
        assert limiter.is_allowed("client1") is False

    def test_window_expiration(self):
        """Test that old requests are cleaned up after window expires."""
        limiter = RateLimiter(max_requests=1, window_seconds=1)

        # First request allowed
        assert limiter.is_allowed("client1") is True

        # Second request blocked
        assert limiter.is_allowed("client1") is False

        # Wait for window to expire
        time.sleep(1.1)

        # Request should be allowed again
        assert limiter.is_allowed("client1") is True

    def test_different_clients_tracked_separately(self):
        """Test that different clients have separate limits."""
        limiter = RateLimiter(max_requests=1, window_seconds=3600)

        # First client uses their limit
        assert limiter.is_allowed("client1") is True
        assert limiter.is_allowed("client1") is False

        # Second client should still be allowed
        assert limiter.is_allowed("client2") is True

    def test_get_reset_time(self):
        """Test getting the reset time for a client."""
        limiter = RateLimiter(max_requests=1, window_seconds=3600)

        # No requests yet
        assert limiter.get_reset_time("client1") is None

        # Make a request
        current_time = time.time()
        limiter.is_allowed("client1")

        # Reset time should be ~3600 seconds from now
        reset_time = limiter.get_reset_time("client1")
        assert reset_time is not None
        assert 3599 <= (reset_time - current_time) <= 3601

    def test_get_remaining_requests(self):
        """Test getting remaining requests for a client."""
        limiter = RateLimiter(max_requests=3, window_seconds=3600)

        # Initially should have all requests
        assert limiter.get_remaining_requests("client1") == 3

        # Use one request
        limiter.is_allowed("client1")
        assert limiter.get_remaining_requests("client1") == 2

        # Use remaining requests
        limiter.is_allowed("client1")
        limiter.is_allowed("client1")
        assert limiter.get_remaining_requests("client1") == 0


class TestGetClientIP:
    """Test the get_client_ip function."""

    def test_direct_client_ip(self):
        """Test getting IP from direct connection."""
        request = Mock(spec=Request)
        request.client.host = "192.168.1.1"
        request.headers = {}

        assert get_client_ip(request) == "192.168.1.1"

    def test_x_forwarded_for_single_ip(self):
        """Test getting IP from X-Forwarded-For with single IP."""
        request = Mock(spec=Request)
        request.client.host = "10.0.0.1"
        request.headers = {"x-forwarded-for": "203.0.113.1"}

        assert get_client_ip(request) == "203.0.113.1"

    def test_x_forwarded_for_multiple_ips(self):
        """Test getting IP from X-Forwarded-For with multiple IPs."""
        request = Mock(spec=Request)
        request.client.host = "10.0.0.1"
        request.headers = {"x-forwarded-for": "203.0.113.1, 198.51.100.1, 10.0.0.1"}

        # Should return the first (original client) IP
        assert get_client_ip(request) == "203.0.113.1"

    def test_x_real_ip(self):
        """Test getting IP from X-Real-IP header."""
        request = Mock(spec=Request)
        request.client.host = "10.0.0.1"
        request.headers = {"x-real-ip": "203.0.113.2"}

        assert get_client_ip(request) == "203.0.113.2"

    def test_header_priority(self):
        """Test that X-Forwarded-For takes priority over X-Real-IP."""
        request = Mock(spec=Request)
        request.client.host = "10.0.0.1"
        request.headers = {"x-forwarded-for": "203.0.113.1", "x-real-ip": "203.0.113.2"}

        assert get_client_ip(request) == "203.0.113.1"


class TestRateLimitMiddleware:
    """Test the RateLimitMiddleware."""

    def create_test_app(self, max_requests=10, window_seconds=3600):
        """Create a test FastAPI app with rate limiting middleware."""
        app = FastAPI()

        # Add exception handler for rate limit exceeded BEFORE middleware
        @app.exception_handler(RateLimitExceeded)
        async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
            return Response(
                content=exc.detail,
                status_code=exc.status_code,
                headers={
                    "X-RateLimit-Limit": str(exc.limit),
                    "X-RateLimit-Remaining": str(exc.remaining),
                    "X-RateLimit-Reset": str(exc.reset) if exc.reset else "",
                    "Retry-After": str(exc.retry_after),
                },
            )

        # Add rate limiting middleware AFTER exception handler
        app.add_middleware(
            RateLimitMiddleware, max_requests=max_requests, window_seconds=window_seconds
        )

        @app.get("/test")
        async def test_endpoint():
            return {"status": "ok"}

        @app.get("/health")
        async def health_endpoint():
            return {"status": "healthy"}

        return TestClient(app)

    def test_middleware_allows_requests_within_limit(self):
        """Test that middleware allows requests within rate limit."""
        client = self.create_test_app(max_requests=3, window_seconds=3600)

        # All 3 requests should succeed
        for i in range(3):
            response = client.get("/test")
            assert response.status_code == 200
            assert response.json() == {"status": "ok"}

    def test_middleware_blocks_exceeding_requests(self):
        """Test that middleware blocks requests exceeding rate limit."""
        client = self.create_test_app(max_requests=2, window_seconds=3600)

        # First 2 requests succeed
        for _ in range(2):
            response = client.get("/test")
            assert response.status_code == 200

        # Third request should be blocked
        response = client.get("/test")
        assert response.status_code == 429
        assert "rate limit exceeded" in response.text.lower()

    def test_rate_limit_headers(self):
        """Test that rate limit headers are included in responses."""
        client = self.create_test_app(max_requests=5, window_seconds=3600)

        # First request
        response = client.get("/test")
        assert response.status_code == 200
        assert response.headers["X-RateLimit-Limit"] == "5"
        assert response.headers["X-RateLimit-Remaining"] == "4"
        assert "X-RateLimit-Reset" in response.headers

        # Use up remaining requests
        for _ in range(4):
            response = client.get("/test")

        # Last allowed request should show 0 remaining
        assert response.headers["X-RateLimit-Remaining"] == "0"

        # Next request should be blocked
        response = client.get("/test")
        assert response.status_code == 429
        assert response.headers["X-RateLimit-Remaining"] == "0"

    def test_health_endpoint_exempt(self):
        """Test that health endpoint is exempt from rate limiting."""
        client = self.create_test_app(max_requests=1, window_seconds=3600)

        # Use up the rate limit on regular endpoint
        response = client.get("/test")
        assert response.status_code == 200

        response = client.get("/test")
        assert response.status_code == 429

        # Health endpoint should still work
        for _ in range(5):
            response = client.get("/health")
            assert response.status_code == 200
            assert response.json() == {"status": "healthy"}

    def test_retry_after_header(self):
        """Test that Retry-After header is included when rate limited."""
        client = self.create_test_app(max_requests=1, window_seconds=60)

        # Use up the limit
        client.get("/test")

        # Next request should include Retry-After
        response = client.get("/test")
        assert response.status_code == 429
        assert "Retry-After" in response.headers
        retry_after = int(response.headers["Retry-After"])
        assert 55 <= retry_after <= 60  # Should be close to window_seconds


class TestRateLimitExceeded:
    """Test the RateLimitExceeded exception."""

    def test_exception_attributes(self):
        """Test RateLimitExceeded exception attributes."""
        exc = RateLimitExceeded(
            detail="Rate limit exceeded", retry_after=3600, limit=10, remaining=0, reset=1234567890
        )

        assert exc.detail == "Rate limit exceeded"
        assert exc.retry_after == 3600
        assert exc.limit == 10
        assert exc.remaining == 0
        assert exc.reset == 1234567890
