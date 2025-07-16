"""Logging configuration for QuestMaster AI."""

import logging
import sys
from typing import Optional

import structlog
from rich.console import Console
from rich.logging import RichHandler


def setup_logging(
    log_level: str = "INFO",
    debug: bool = False,
    json_logs: bool = False,
    console: Optional[Console] = None,
) -> None:
    """Set up logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        debug: Enable debug mode
        json_logs: Output logs in JSON format
        console: Rich console instance for colored output
    """
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                console=console or Console(stderr=True),
                rich_tracebacks=True,
                show_path=debug,
                show_time=True,
            )
        ],
        level=getattr(logging, log_level.upper()),
        force=True,
    )

    # Configure structlog
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
    ]

    if json_logs:
        processors.extend([
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ])
    else:
        processors.extend([
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
            structlog.dev.ConsoleRenderer(colors=True),
        ])

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance.
    
    Args:
        name: Logger name, typically __name__
        
    Returns:
        Configured structlog logger instance
    """
    return structlog.get_logger(name)
