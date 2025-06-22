"""Logging middleware and configuration."""

import logging
import sys
import time
import uuid

from fastapi import FastAPI, Request

from config.settings import get_settings


def setup_logging(app: FastAPI) -> None:
    """Configure structured logging for the application."""
    settings = get_settings()

    # Configure basic formatter
    log_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    log_handler.setFormatter(formatter)

    # Configure root logger
    logging.root.handlers = [log_handler]
    logging.root.setLevel(settings.log_level)

    # Add request ID middleware
    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Log request
        logger = logging.getLogger("api.request")
        logger.info(
            "Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client_host": request.client.host if request.client else None,
            },
        )

        # Time the request
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        # Log response
        logger.info(
            "Request completed",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "duration_seconds": round(duration, 3),
            },
        )

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response

    logging.getLogger(__name__).info("Logging middleware configured")
