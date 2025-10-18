"""
Logging configuration for IdeaFly Authentication System.

This module provides centralized logging setup with proper formatting,
levels, and output destinations.
"""

import logging
import logging.config
import sys
from typing import Dict, Any

from .config import get_settings

# Get application settings
settings = get_settings()


def setup_logging() -> None:
    """
    Setup application logging configuration.
    
    Configures formatters, handlers, and loggers with appropriate
    levels based on debug mode and environment settings.
    """
    
    # Determine log level based on debug mode
    log_level = "DEBUG" if settings.api_debug else "INFO"
    
    # Logging configuration dictionary
    logging_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "detailed": {
                "format": (
                    "[%(asctime)s] %(levelname)s in %(name)s "
                    "[%(filename)s:%(lineno)d]: %(message)s"
                ),
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": (
                    "%(asctime)s %(name)s %(levelname)s %(filename)s "
                    "%(lineno)d %(message)s"
                )
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "detailed" if settings.api_debug else "default",
                "stream": sys.stdout
            },
            "error_console": {
                "class": "logging.StreamHandler",
                "level": "ERROR",
                "formatter": "detailed",
                "stream": sys.stderr
            }
        },
        "loggers": {
            # Root logger
            "": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False
            },
            # Application loggers
            "src": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False
            },
            "src.main": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False
            },
            "src.core": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False
            },
            "src.auth": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False
            },
            # Third-party loggers
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            },
            "uvicorn.access": {
                "level": "INFO" if settings.api_debug else "WARNING",
                "handlers": ["console"],
                "propagate": False
            },
            "fastapi": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            },
            "sqlalchemy": {
                "level": "INFO" if settings.api_debug else "WARNING",
                "handlers": ["console"],
                "propagate": False
            },
            "sqlalchemy.engine": {
                "level": "INFO" if settings.api_debug else "WARNING",
                "handlers": ["console"],
                "propagate": False
            },
            "alembic": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            }
        }
    }
    
    # Apply logging configuration
    logging.config.dictConfig(logging_config)
    
    # Get logger for this module
    logger = logging.getLogger(__name__)
    logger.info(f"📋 Logging configured - Level: {log_level}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with proper configuration.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        logging.Logger: Configured logger instance
        
    Example:
        ```python
        logger = get_logger(__name__)
        logger.info("This is a log message")
        ```
    """
    return logging.getLogger(name)