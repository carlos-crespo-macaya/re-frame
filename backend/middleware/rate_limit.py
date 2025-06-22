"""
Rate limiting middleware to prevent abuse
"""

import hashlib
import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiting middleware
    In production, this should use Redis or similar
    """

    def __init__(self, app, rate_limit: int = 10, window: int = 3600):
        """
        Initialize rate limiter

        Args:
            app: The ASGI application
            rate_limit: Number of requests allowed per window
            window: Time window in seconds (default: 1 hour)
        """
        super().__init__(app)
        self.rate_limit = rate_limit
        self.window = window
        self.cache: dict[str, tuple[int, float]] = {}  # client_id -> (count, window_start)

    def _get_client_id(self, request: Request) -> str:
        """
        Get a unique identifier for the client
        Uses IP address + user agent hash
        """
        client_host = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "")

        # Create hash of IP + user agent for privacy
        identifier = f"{client_host}:{user_agent}"
        return hashlib.sha256(identifier.encode()).hexdigest()[:16]

    def _is_rate_limited(self, client_id: str) -> bool:
        """
        Check if client has exceeded rate limit
        """
        now = time.time()

        if client_id in self.cache:
            count, window_start = self.cache[client_id]

            # Check if we're still in the same window
            if now - window_start < self.window:
                if count >= self.rate_limit:
                    return True
                # Increment count
                self.cache[client_id] = (count + 1, window_start)
            else:
                # New window, reset count
                self.cache[client_id] = (1, now)
        else:
            # First request from this client
            self.cache[client_id] = (1, now)

        # Clean up old entries (simple cleanup every 100 requests)
        if len(self.cache) > 100:
            self._cleanup_cache(now)

        return False

    def _cleanup_cache(self, current_time: float):
        """Remove expired entries from cache"""
        expired_keys = [
            key
            for key, (_, window_start) in self.cache.items()
            if current_time - window_start > self.window
        ]
        for key in expired_keys:
            del self.cache[key]

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path.startswith("/api/health"):
            return await call_next(request)

        client_id = self._get_client_id(request)

        if self._is_rate_limited(client_id):
            logger.warning(f"Rate limit exceeded for client {client_id}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": "Too many requests. Please try again later.",
                    "retry_after": self.window,
                },
                headers={
                    "Retry-After": str(self.window),
                    "X-RateLimit-Limit": str(self.rate_limit),
                    "X-RateLimit-Window": str(self.window),
                },
            )

        response = await call_next(request)

        # Add rate limit headers
        if client_id in self.cache:
            count, _ = self.cache[client_id]
            response.headers["X-RateLimit-Limit"] = str(self.rate_limit)
            response.headers["X-RateLimit-Remaining"] = str(max(0, self.rate_limit - count))
            response.headers["X-RateLimit-Window"] = str(self.window)

        return response
