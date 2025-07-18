"""
Centralized logging configuration using structlog.
"""

import logging
import sys
from typing import Any

import structlog
from structlog.processors import CallsiteParameter, CallsiteParameterAdder
from structlog.stdlib import LoggerFactory


def setup_logging(log_level: str = "INFO") -> None:
    """
    Configure structlog for the application.

    Args:
        log_level: The logging level (DEBUG, INFO, WARNING, ERROR)
    """
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            CallsiteParameterAdder(
                parameters=[
                    CallsiteParameter.FILENAME,
                    CallsiteParameter.FUNC_NAME,
                    CallsiteParameter.LINENO,
                ],
                additional_ignores=["logging", "__main__"],
            ),
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.UnicodeDecoder(),
            structlog.processors.dict_tracebacks,
            structlog.dev.ConsoleRenderer(colors=True),
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> Any:
    """
    Get a logger instance with the given name.

    Args:
        name: The logger name

    Returns:
        A configured structlog logger
    """
    return structlog.get_logger(name)


def log_agent_event(logger: Any, event_type: str, **kwargs: Any) -> None:
    """
    Helper to log agent-related events with consistent formatting.

    Args:
        logger: The logger instance
        event_type: Type of event (e.g., "message_received", "response_generated")
        **kwargs: Additional context to log
    """
    logger.info("agent_event", event_type=event_type, **kwargs)


def log_session_event(
    logger: Any,
    session_id: str,
    event_type: str,
    **kwargs: Any,
) -> None:
    """
    Helper to log session-related events.

    Args:
        logger: The logger instance
        session_id: The session ID
        event_type: Type of event (e.g., "created", "ended")
        **kwargs: Additional context to log
    """
    logger.info("session_event", session_id=session_id, event_type=event_type, **kwargs)
