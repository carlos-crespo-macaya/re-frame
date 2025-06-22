"""Centralized logging configuration for the re-frame backend."""

import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path


def setup_logging(
    log_level: str = "INFO",
    log_dir: str = "logs",
    app_name: str = "re-frame",
    max_bytes: int = 10_485_760,  # 10MB
    backup_count: int = 5,
) -> None:
    """
    Set up comprehensive logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory to store log files
        app_name: Application name for log files
        max_bytes: Maximum size of each log file before rotation
        backup_count: Number of backup files to keep
    """
    # Create logs directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    simple_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
    )
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console handler (simple format)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)
    
    # Main application log file (rotating)
    app_log_file = log_path / f"{app_name}.log"
    app_file_handler = logging.handlers.RotatingFileHandler(
        app_log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
    )
    app_file_handler.setLevel(logging.DEBUG)
    app_file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(app_file_handler)
    
    # Error log file (rotating) - only ERROR and CRITICAL
    error_log_file = log_path / f"{app_name}_errors.log"
    error_file_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_file_handler)
    
    # Agent-specific log file for ADK agents
    agent_logger = logging.getLogger("agents")
    agent_log_file = log_path / f"{app_name}_agents.log"
    agent_file_handler = logging.handlers.RotatingFileHandler(
        agent_log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
    )
    agent_file_handler.setLevel(logging.DEBUG)
    agent_file_handler.setFormatter(detailed_formatter)
    agent_logger.addHandler(agent_file_handler)
    agent_logger.propagate = False  # Don't propagate to root logger
    
    # API request/response log file
    api_logger = logging.getLogger("api")
    api_log_file = log_path / f"{app_name}_api.log"
    api_file_handler = logging.handlers.RotatingFileHandler(
        api_log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
    )
    api_file_handler.setLevel(logging.DEBUG)
    api_file_handler.setFormatter(detailed_formatter)
    api_logger.addHandler(api_file_handler)
    api_logger.propagate = False
    
    # Add console handler to specialized loggers for important messages
    agent_logger.addHandler(console_handler)
    api_logger.addHandler(console_handler)
    
    # Log the startup
    root_logger.info(f"Logging initialized - Level: {log_level}, Directory: {log_path}")
    root_logger.info(f"Log files: {app_name}.log, {app_name}_errors.log, {app_name}_agents.log, {app_name}_api.log")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)