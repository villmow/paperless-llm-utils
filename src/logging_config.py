"""
Centralized logging configuration using structlog.

This module configures structlog with:
- ISO formatted timestamps with milliseconds
- Colored console output
- Structured key-value logging
- Log level filtering
"""

import structlog
import logging
import sys


def configure_logging():
    """
    Configure structlog for the application.

    Sets up processors for:
    - Adding timestamps in ISO format
    - Adding log levels
    - Formatting output for console with colors
    """

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso", utc=False),
            structlog.dev.ConsoleRenderer(
                colors=True,
                exception_formatter=structlog.dev.plain_traceback,
            ),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )


# Initialize logging when this module is imported
configure_logging()
