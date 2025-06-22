"""Logging middleware and configuration."""

import logging
import logging.handlers
import sys
import time
import uuid
from pathlib import Path

from fastapi import FastAPI, Request

from config.settings import get_settings


def setup_logging(app: FastAPI) -> None:
    """Configure structured logging for the application with file rotation."""
    settings = get_settings()
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Formatters
    detailed_formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(funcName)s:%(lineno)d %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    simple_formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(simple_formatter)
    console_handler.setLevel(logging.INFO)
    
    # Main app log file (rotating)
    app_file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "re-frame.log",
        maxBytes=10_485_760,  # 10MB
        backupCount=5,
    )
    app_file_handler.setFormatter(detailed_formatter)
    app_file_handler.setLevel(logging.DEBUG)
    
    # Error log file (rotating)
    error_file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "re-frame_errors.log",
        maxBytes=10_485_760,  # 10MB
        backupCount=5,
    )
    error_file_handler.setFormatter(detailed_formatter)
    error_file_handler.setLevel(logging.ERROR)
    
    # API log file (rotating)
    api_file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "re-frame_api.log",
        maxBytes=10_485_760,  # 10MB
        backupCount=5,
    )
    api_file_handler.setFormatter(detailed_formatter)
    api_file_handler.setLevel(logging.DEBUG)
    
    # Agent log file (rotating)
    agent_file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "re-frame_agents.log",
        maxBytes=10_485_760,  # 10MB
        backupCount=5,
    )
    agent_file_handler.setFormatter(detailed_formatter)
    agent_file_handler.setLevel(logging.DEBUG)

    # Configure root logger
    logging.root.handlers = [console_handler, app_file_handler, error_file_handler]
    logging.root.setLevel(settings.log_level)
    
    # Configure API logger
    api_logger = logging.getLogger("api")
    api_logger.handlers = [console_handler, api_file_handler]
    api_logger.setLevel(logging.DEBUG)
    api_logger.propagate = False
    
    # Configure agents logger
    agents_logger = logging.getLogger("agents")
    agents_logger.handlers = [console_handler, agent_file_handler]
    agents_logger.setLevel(logging.DEBUG)
    agents_logger.propagate = False

    # Add request ID middleware
    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Log request
        logger = logging.getLogger("api.request")
        logger.info(
            f"Request started - {request.method} {request.url.path} from {request.client.host if request.client else 'unknown'} [ID: {request_id}]"
        )

        # Time the request
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        # Log response
        logger.info(
            f"Request completed - {request.method} {request.url.path} - Status: {response.status_code} - Duration: {round(duration, 3)}s [ID: {request_id}]"
        )

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response

    logger = logging.getLogger(__name__)
    logger.info("Logging middleware configured with file rotation")
    logger.info(f"Log files: logs/re-frame.log, logs/re-frame_errors.log, logs/re-frame_api.log, logs/re-frame_agents.log")
