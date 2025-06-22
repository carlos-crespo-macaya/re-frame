"""Rate limiting middleware for FastAPI."""

import logging
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class RateLimitExceeded(HTTPException):
    """Custom exception for rate limit exceeded."""

    def __init__(
        self,
        detail: str = "Rate limit exceeded",
        retry_after: int = 0,
        limit: int = 0,
        remaining: int = 0,
        reset: int = 0,
    ):
        super().__init__(status_code=429, detail=detail)
        self.retry_after = retry_after
        self.limit = limit
        self.remaining = remaining
        self.reset = reset


def get_client_ip(request: Request) -> str:
    """Extract client IP from request, handling proxies."""
    # Check X-Forwarded-For header (comma-separated list of IPs)
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        # Take the first IP (original client)
        return forwarded_for.split(",")[0].strip()

    # Check X-Real-IP header
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip

    # Fall back to direct client IP
    return request.client.host


class RateLimiter:
    """Rate limiter using sliding window algorithm."""

    def __init__(self, max_requests: int, window_seconds: int):
        """Initialize rate limiter.

        Args:
            max_requests: Maximum number of requests allowed in window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict[str, deque[float]] = defaultdict(deque)

    def _cleanup_old_requests(self, client_id: str, current_time: float) -> None:
        """Remove requests older than the time window."""
        if client_id not in self.requests:
            return

        cutoff_time = current_time - self.window_seconds
        client_requests = self.requests[client_id]

        # Remove old requests from the left side of deque
        while client_requests and client_requests[0] < cutoff_time:
            client_requests.popleft()

        # Clean up empty deques
        if not client_requests:
            del self.requests[client_id]

    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed for client.

        Args:
            client_id: Unique identifier for client

        Returns:
            True if request is allowed, False if rate limit exceeded
        """
        current_time = time.time()
        self._cleanup_old_requests(client_id, current_time)

        client_requests = self.requests[client_id]

        if len(client_requests) >= self.max_requests:
            return False

        # Add current request
        client_requests.append(current_time)
        return True

    def check_allowed(self, client_id: str) -> bool:
        """Check if request would be allowed without counting it.

        Args:
            client_id: Unique identifier for client

        Returns:
            True if request would be allowed, False if rate limit exceeded
        """
        current_time = time.time()
        self._cleanup_old_requests(client_id, current_time)

        client_requests = self.requests[client_id]
        return len(client_requests) < self.max_requests

    def get_reset_time(self, client_id: str) -> float | None:
        """Get the time when rate limit resets for client.

        Args:
            client_id: Unique identifier for client

        Returns:
            Unix timestamp when oldest request expires, or None if no requests
        """
        if client_id not in self.requests or not self.requests[client_id]:
            return None

        oldest_request = self.requests[client_id][0]
        return oldest_request + self.window_seconds

    def get_remaining_requests(self, client_id: str) -> int:
        """Get number of remaining requests for client.

        Args:
            client_id: Unique identifier for client

        Returns:
            Number of requests remaining in current window
        """
        current_time = time.time()
        self._cleanup_old_requests(client_id, current_time)

        used_requests = len(self.requests.get(client_id, []))
        return max(0, self.max_requests - used_requests)

    def get_rate_limit_info(self, client_id: str) -> tuple[int, int, int | None]:
        """Get complete rate limit information for client.

        Args:
            client_id: Unique identifier for client

        Returns:
            Tuple of (limit, remaining, reset_timestamp)
        """
        remaining = self.get_remaining_requests(client_id)
        reset_time = self.get_reset_time(client_id)
        reset_timestamp = int(reset_time) if reset_time else None

        return self.max_requests, remaining, reset_timestamp


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce rate limiting."""

    # Paths exempt from rate limiting
    EXEMPT_PATHS = {"/health", "/api/v1/health", "/docs", "/openapi.json", "/favicon.ico"}

    def __init__(self, app: ASGIApp, max_requests: int = 10, window_seconds: int = 3600):
        """Initialize rate limit middleware.

        Args:
            app: ASGI application
            max_requests: Maximum requests per window (default: 10)
            window_seconds: Time window in seconds (default: 3600 = 1 hour)
        """
        super().__init__(app)
        self.limiter = RateLimiter(max_requests, window_seconds)
        self.max_requests = max_requests
        self.window_seconds = window_seconds

        logger.info(
            f"Rate limiting initialized: {max_requests} requests per {window_seconds} seconds"
        )

    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        # Skip rate limiting for exempt paths
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)

        # Get client identifier
        client_id = get_client_ip(request)

        # Check if request would be allowed
        if not self.limiter.check_allowed(client_id):
            # Get rate limit info for response
            limit, remaining, reset_time = self.limiter.get_rate_limit_info(client_id)
            # Calculate retry after
            current_time = time.time()
            retry_after = int(reset_time - current_time) if reset_time else self.window_seconds

            # Log rate limit violation
            logger.warning(f"Rate limit exceeded for client {client_id} on {request.url.path}")

            # Return rate limit response directly
            return Response(
                content=f"Rate limit exceeded. Limit: {self.max_requests} requests per hour.",
                status_code=429,
                headers={
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(reset_time)) if reset_time else "",
                    "Retry-After": str(retry_after),
                },
            )

        # Mark request as counted
        self.limiter.is_allowed(client_id)

        # Process request
        response = await call_next(request)

        # Add rate limit headers to response
        limit, remaining_after, reset_time = self.limiter.get_rate_limit_info(client_id)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining_after)
        if reset_time:
            response.headers["X-RateLimit-Reset"] = str(int(reset_time))

        return response


def setup_rate_limiting(app, max_requests: int = 10, window_seconds: int = 3600):
    """Set up rate limiting middleware for the FastAPI application.

    Args:
        app: FastAPI application instance
        max_requests: Maximum requests per window (default: 10)
        window_seconds: Time window in seconds (default: 3600 = 1 hour)
    """
    app.add_middleware(
        RateLimitMiddleware, max_requests=max_requests, window_seconds=window_seconds
    )

    # Add exception handler for rate limit exceeded
    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        """Handle rate limit exceeded exceptions."""
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
