"""Simple in-memory cache for reducing API calls."""

import hashlib
import time
from typing import Any


class SimpleCache:
    """In-memory cache with TTL support."""

    def __init__(self, ttl_seconds: int = 3600):
        """Initialize cache with time-to-live in seconds."""
        self._cache: dict[str, tuple[Any, float]] = {}
        self.ttl_seconds = ttl_seconds

    def _generate_key(self, *args: Any, **kwargs: Any) -> str:
        """Generate a cache key from arguments."""
        # Create a string representation of all arguments
        key_parts = [str(arg) for arg in args]
        key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
        key_string = "|".join(key_parts)

        # Return a hash for consistent key length
        return hashlib.md5(key_string.encode()).hexdigest()

    def get(self, *args: Any, **kwargs: Any) -> Any | None:
        """Get value from cache if it exists and hasn't expired."""
        key = self._generate_key(*args, **kwargs)

        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp < self.ttl_seconds:
                return value
            # Remove expired entry
            del self._cache[key]

        return None

    def set(self, value: Any, *args: Any, **kwargs: Any) -> None:
        """Store value in cache with current timestamp."""
        key = self._generate_key(*args, **kwargs)
        self._cache[key] = (value, time.time())

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()


# Global cache instance for common responses
response_cache = SimpleCache(ttl_seconds=3600)  # 1 hour cache
