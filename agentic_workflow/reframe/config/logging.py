"""Logging configuration for the agentic workflow system."""

from datetime import UTC, datetime
import logging
import logging.handlers
from pathlib import Path
import sys


def setup_logging(
    log_level: str = "INFO", log_file: Path | str | None = None, log_to_console: bool = True
) -> logging.Logger:
    """Set up logging configuration for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file. If None, uses default location
        log_to_console: Whether to also log to console

    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)

    # Default log file with timestamp
    log_file_path: Path
    if log_file is None:
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        log_file_path = log_dir / f"agentic_workflow_{timestamp}.log"
    else:
        log_file_path = Path(log_file)

    # Create logger
    logger = logging.getLogger("agentic_workflow")
    logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file_path, maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB
    )
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler (optional)
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S"
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    # Log the startup
    logger.info(f"Logging initialized - Level: {log_level}, File: {log_file}")

    return logger


# Default logger instance
logger = setup_logging()
