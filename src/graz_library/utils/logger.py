"""Logging utilities for the Graz Library tool"""

import logging
import sys
from pathlib import Path
from typing import Optional


# Create logs directory if it doesn't exist
LOG_DIR = Path.home() / ".graz-library" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "graz-library.log"


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Get or create a logger with the specified name and level

    Args:
        name: Logger name (usually __name__)
        level: Logging level (default: INFO)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Only add handlers if they don't exist (avoid duplicates)
    if logger.handlers:
        return logger

    logger.setLevel(level)

    # Console handler - INFO level
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(console_format)

    # File handler - DEBUG level (more detailed)
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_format)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


def set_log_level(level: int) -> None:
    """Set log level for all handlers

    Args:
        level: Logging level (e.g., logging.DEBUG)
    """
    for logger_name in logging.Logger.manager.loggerDict:
        logger = logging.getLogger(logger_name)
        if isinstance(logger, logging.Logger):
            logger.setLevel(level)
            for handler in logger.handlers:
                handler.setLevel(level)
