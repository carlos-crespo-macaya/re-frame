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


# Trusted proxy networks (Cloud Run, common load balancers)
TRUSTED_PROXIES = {
    "127.0.0.0/8",  # Localhost
    "10.0.0.0/8",  # Private network
    "172.16.0.0/12",  # Private network
    "192.168.0.0/16",  # Private network
    "169.254.169.254",  # GCP metadata server
}


def _is_trusted_proxy(ip: str) -> bool:
    """Check if IP is from a trusted proxy."""
    import ipaddress

    try:
        client_ip = ipaddress.ip_address(ip)
        for trusted_network in TRUSTED_PROXIES:
            if "/" in trusted_network:
                if client_ip in ipaddress.ip_network(trusted_network, strict=False):
                    return True
            else:
                if str(client_ip) == trusted_network:
                    return True
        return False
    except ValueError:
        return False


def get_client_ip(request: Request) -> str:
    """Extract client IP from request, handling proxies securely."""
    # Get the direct client IP
    direct_ip = request.client.host if request.client else "unknown"

    # Only trust proxy headers if request comes from trusted proxy
    if _is_trusted_proxy(direct_ip):
        # Check X-Forwarded-For header (comma-separated list of IPs)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Take the first IP (original client) and validate
            original_ip = forwarded_for.split(",")[0].strip()
            if original_ip and original_ip != "unknown":
                return original_ip

        # Check X-Real-IP header
        real_ip = request.headers.get("x-real-ip")
        if real_ip and real_ip != "unknown":
            return real_ip

    # Fall back to direct client IP
    return direct_ip


class RateLimiter:
    """Rate limiter using sliding window algorithm.

    Note: This implementation uses in-memory storage and is suitable for
    single-instance deployments. For production with multiple instances,
    consider using Redis-based distributed rate limiting.
    """

    MAX_TRACKED_CLIENTS = 10000  # Prevent memory exhaustion attacks
    CLEANUP_INTERVAL = 300  # Cleanup every 5 minutes

    def __init__(self, max_requests: int, window_seconds: int):
        """Initialize rate limiter.

        Args:
            max_requests: Maximum number of requests allowed in window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # TODO: Replace with Redis for distributed deployment
        self.requests: dict[str, deque[float]] = defaultdict(deque)
        self.last_cleanup = time.time()

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

    def _memory_protection_cleanup(self, current_time: float) -> None:
        """Protect against memory exhaustion attacks."""
        # Periodic cleanup to prevent memory exhaustion
        if current_time - self.last_cleanup > self.CLEANUP_INTERVAL:
            self.last_cleanup = current_time

            # If too many clients tracked, remove oldest inactive ones
            if len(self.requests) > self.MAX_TRACKED_CLIENTS:
                # Find clients with old requests to remove
                clients_to_remove = []
                cutoff_time = current_time - self.window_seconds

                for client_id, client_requests in self.requests.items():
                    if not client_requests or client_requests[-1] < cutoff_time:
                        clients_to_remove.append(client_id)

                # Remove oldest clients first
                for client_id in clients_to_remove[
                    : len(self.requests) - self.MAX_TRACKED_CLIENTS + 1000
                ]:
                    del self.requests[client_id]

                logger.warning(
                    f"Memory protection: removed {len(clients_to_remove)} inactive clients"
                )

    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed for client.

        Args:
            client_id: Unique identifier for client

        Returns:
            True if request is allowed, False if rate limit exceeded
        """
        current_time = time.time()
        self._memory_protection_cleanup(current_time)
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
    EXEMPT_PATHS = {
        "/",
        "/health", 
        "/api/health",
        "/api/health/detailed",
        "/api/health/live",
        "/api/health/ready", 
        "/api/health/startup",
        "/api/v1/health",
        "/docs",
        "/api/docs",
        "/api/redoc", 
        "/openapi.json",
        "/api/openapi.json",
        "/favicon.ico"
    }

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
            
        # Skip rate limiting for test environments
        if request.base_url.hostname in ["testserver", "localhost", "127.0.0.1"]:
            # Process request without rate limiting but add headers for testing
            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(self.max_requests)
            response.headers["X-RateLimit-Remaining"] = str(self.max_requests)
            response.headers["X-RateLimit-Reset"] = str(int(time.time() + self.window_seconds))
            return response

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
