"""Logging configuration for the application.

Provides structured logging using structlog with JSON output for production
and human-readable output for development.
"""

import logging
import sys
from typing import Any, Dict

import structlog
from structlog.types import EventDict

from app.core.config import get_settings

settings = get_settings()


def add_correlation_id(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add correlation ID to log entries.
    
    Args:
        logger: The logger instance
        method_name: The method name being called
        event_dict: The event dictionary
    
    Returns:
        EventDict: Updated event dictionary with correlation ID
    """
    # In a real application, you would extract this from request context
    # For now, we'll use a placeholder
    event_dict["correlation_id"] = getattr(logger, "correlation_id", None)
    return event_dict


def add_service_info(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add service information to log entries.
    
    Args:
        logger: The logger instance
        method_name: The method name being called
        event_dict: The event dictionary
    
    Returns:
        EventDict: Updated event dictionary with service info
    """
    event_dict["service"] = "facturx-api"
    event_dict["version"] = "0.1.0"
    return event_dict


def setup_logging() -> None:
    """Configure structured logging for the application."""
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL),
    )
    
    # Configure structlog
    processors = [
        structlog.contextvars.merge_contextvars,
        add_service_info,
        add_correlation_id,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    if settings.LOG_FORMAT == "json":
        # JSON output for production
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Human-readable output for development
        processors.extend([
            structlog.dev.ConsoleRenderer(colors=True),
        ])
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure specific loggers
    logging.getLogger("uvicorn.access").handlers = []
    logging.getLogger("uvicorn.error").handlers = []
    
    # Reduce noise from third-party libraries
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    logger = structlog.get_logger(__name__)
    logger.info(
        "Logging configured",
        log_level=settings.LOG_LEVEL,
        log_format=settings.LOG_FORMAT,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance.
    
    Args:
        name: Logger name
    
    Returns:
        structlog.BoundLogger: Configured logger instance
    """
    return structlog.get_logger(name)


class LoggingMiddleware:
    """Middleware for request/response logging."""
    
    def __init__(self, app):
        self.app = app
        self.logger = get_logger(__name__)
    
    async def __call__(self, scope, receive, send):
        """Process request and log details."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Extract request info
        method = scope["method"]
        path = scope["path"]
        query_string = scope.get("query_string", b"").decode()
        
        # Log request
        self.logger.info(
            "Request started",
            method=method,
            path=path,
            query_string=query_string,
        )
        
        # Process request
        start_time = structlog.get_logger().info
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status_code = message["status"]
                self.logger.info(
                    "Request completed",
                    method=method,
                    path=path,
                    status_code=status_code,
                )
            await send(message)
        
        await self.app(scope, receive, send_wrapper)
