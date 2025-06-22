"""Rate limiting middleware using slowapi."""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowREDACTED
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from config.settings import get_settings

logger = logging.getLogger(__name__)


def get_rate_limit_key(request: Request) -> str:
    """Generate rate limit key from request.

    Uses IP address for anonymous users.
    Could be extended to use user ID for authenticated users.
    """
    return get_remote_address(request)


# Create limiter instance
limiter = Limiter(key_func=get_rate_limit_key)


def setup_rate_limiting(app: FastAPI) -> None:
    """Configure rate limiting for the application."""
    settings = get_settings()

    # Add limiter to app state
    app.state.limiter = limiter

    # Add exception handler
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Create custom error handler with helpful message
    @app.exception_handler(RateLimitExceeded)
    async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
        response = {
            "error": "Rate limit exceeded",
            "message": f"You have exceeded the limit of {settings.rate_limit_requests} requests per hour.",
            "detail": "This limit helps ensure fair access for all users. Please try again later.",
        }
        return JSONResponse(
            status_code=429,
            content=response,
            headers={
                "X-RateLimit-Limit": str(settings.rate_limit_requests),
                "X-RateLimit-Reset": str(exc.retry_after),
            },
        )

    logger.info(
        f"Rate limiting configured: {settings.rate_limit_requests} requests per {settings.rate_limit_period} seconds"
    )


def get_rate_limit() -> str:
    """Get rate limit string for decorators."""
    settings = get_settings()
    return f"{settings.rate_limit_requests}/{settings.rate_limit_period}seconds"
