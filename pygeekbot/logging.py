import logging
import sys
import os
from typing import Optional


def get_log_level_from_env() -> int:
    """Get log level from environment variable.

    Returns
    -------
    int
        Logging level (defaults to INFO if not set or invalid)
    """
    level_name = os.getenv("GEEKBOT_LOG_LEVEL", "INFO").upper()
    try:
        return getattr(logging, level_name)
    except AttributeError:
        return logging.INFO


def setup_logger(
    name: str = "geekbot",
    level: Optional[int] = None,
    log_file: Optional[str] = None,
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
) -> logging.Logger:
    """Configure and return a logger instance.

    Parameters
    ----------
    name : str = "geekbot"
        Name of the logger
    level : int = None
        Logging level. If None, uses GEEKBOT_LOG_LEVEL env var or defaults to INFO
    log_file : str = None
        Path to log file. If None, logs to stderr
    log_format : str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        Format string for log messages

    Returns
    -------
    logging.Logger
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Use provided level, env var, or default to INFO
    log_level = level if level is not None else get_log_level_from_env()
    logger.setLevel(log_level)

    formatter = logging.Formatter(log_format)

    # Add stderr handler if no handlers exist
    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Add file handler if log_file is specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
