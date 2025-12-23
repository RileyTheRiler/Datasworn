"""
Logging Configuration for Starforged AI Game Master.
Provides centralized logging setup with consistent formatting.
"""

from __future__ import annotations
import logging
import sys
from pathlib import Path
from typing import Optional

# Define module-specific loggers for easy filtering
LOGGERS = {
    "starforged": "starforged",
    "narrator": "starforged.narrator",
    "director": "starforged.director",
    "nodes": "starforged.nodes",
    "rules": "starforged.rules",
    "memory": "starforged.memory",
    "feedback": "starforged.feedback",
    "llm": "starforged.llm",
    "ui": "starforged.ui",
    "api": "starforged.api",
}


def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    debug_mode: bool = False,
) -> logging.Logger:
    """
    Configure logging for the application.

    Args:
        level: Default logging level
        log_file: Optional file path for log output
        debug_mode: If True, sets level to DEBUG and adds more detail

    Returns:
        The root starforged logger
    """
    if debug_mode:
        level = logging.DEBUG

    # Create formatter
    if debug_mode:
        formatter = logging.Formatter(
            "%(asctime)s | %(name)-25s | %(levelname)-8s | %(filename)s:%(lineno)d | %(message)s",
            datefmt="%H:%M:%S",
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s",
            datefmt="%H:%M:%S",
        )

    # Get root starforged logger
    root_logger = logging.getLogger("starforged")
    root_logger.setLevel(level)

    # Clear existing handlers
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module.

    Args:
        name: Logger name (can be a key from LOGGERS or a custom name)

    Returns:
        Configured logger instance
    """
    logger_name = LOGGERS.get(name, f"starforged.{name}")
    return logging.getLogger(logger_name)


# Convenience function for creating contextual log messages
def log_context(
    logger: logging.Logger,
    level: int,
    message: str,
    **context,
) -> None:
    """
    Log a message with additional context.

    Args:
        logger: Logger instance
        level: Logging level
        message: Main message
        **context: Additional context to include
    """
    if context:
        context_str = " | ".join(f"{k}={v}" for k, v in context.items())
        message = f"{message} [{context_str}]"
    logger.log(level, message)


class LoggedOperation:
    """
    Context manager for logging operation start/end with timing.

    Usage:
        with LoggedOperation(logger, "Processing narrative"):
            # do work
    """

    def __init__(
        self,
        logger: logging.Logger,
        operation: str,
        level: int = logging.DEBUG,
    ):
        self.logger = logger
        self.operation = operation
        self.level = level
        self.start_time = None

    def __enter__(self):
        import time

        self.start_time = time.time()
        self.logger.log(self.level, f"Starting: {self.operation}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        import time

        elapsed = time.time() - self.start_time
        if exc_type:
            self.logger.warning(
                f"Failed: {self.operation} after {elapsed:.2f}s - {exc_type.__name__}: {exc_val}"
            )
        else:
            self.logger.log(self.level, f"Completed: {self.operation} in {elapsed:.2f}s")
        return False  # Don't suppress exceptions


# Initialize default logging on import
_initialized = False


def ensure_initialized():
    """Ensure logging is initialized at least once."""
    global _initialized
    if not _initialized:
        setup_logging()
        _initialized = True


# Auto-initialize with defaults
ensure_initialized()
