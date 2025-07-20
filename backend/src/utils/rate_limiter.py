"""Rate limiting utility for API endpoints."""

import time
from collections import defaultdict

from src.utils.logging import get_logger

logger = get_logger(__name__)


class RateLimiter:
    """Simple rate limiter using a sliding window approach."""

    def __init__(self, max_requests: int, window_seconds: int):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum number of requests allowed in the window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict[str, list[float]] = defaultdict(list)

    async def check_request(self, client_id: str) -> bool:
        """
        Check if a request is allowed for the given client.

        Args:
            client_id: Unique identifier for the client (e.g., IP address)

        Returns:
            True if request is allowed, False if rate limit exceeded
        """
        current_time = time.time()
        window_start = current_time - self.window_seconds

        # Clean up old requests outside the window
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id] if req_time > window_start
        ]

        # Check if we've exceeded the limit
        if len(self.requests[client_id]) >= self.max_requests:
            logger.warning(
                "rate_limit_exceeded",
                client_id=client_id,
                requests_in_window=len(self.requests[client_id]),
                max_requests=self.max_requests,
            )
            return False

        # Record this request
        self.requests[client_id].append(current_time)
        return True

    def get_stats(self, client_id: str) -> tuple[int, int]:
        """
        Get current stats for a client.

        Args:
            client_id: Unique identifier for the client

        Returns:
            Tuple of (current_requests, seconds_until_reset)
        """
        current_time = time.time()
        window_start = current_time - self.window_seconds

        # Clean up old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id] if req_time > window_start
        ]

        current_requests = len(self.requests[client_id])

        # Calculate seconds until the oldest request expires
        if current_requests > 0:
            oldest_request = min(self.requests[client_id])
            seconds_until_reset = int(
                oldest_request + self.window_seconds - current_time
            )
        else:
            seconds_until_reset = 0

        return current_requests, max(0, seconds_until_reset)
