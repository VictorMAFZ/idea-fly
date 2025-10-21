"""
Structured Logging System for IdeaFly Backend.

Provides comprehensive logging functionality with structured logs,
different log levels, monitoring integration, and production readiness.
Features include:
- Structured JSON logging for production
- Human-readable logs for development
- Context injection and correlation IDs
- Performance metrics logging
- Security event logging
- Integration with monitoring services
"""

import json
import sys
import time
import traceback
import uuid
from datetime import datetime
from typing import Any, Dict, Optional, Union
from contextvars import ContextVar
from enum import Enum
from pathlib import Path

import structlog
from structlog.stdlib import LoggerFactory
from structlog import configure, get_logger
from pythonjsonlogger import jsonlogger


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

class LogLevel(str, Enum):
    """Log level enumeration."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogCategory(str, Enum):
    """Log category enumeration for filtering and monitoring."""
    AUTHENTICATION = "auth"
    AUTHORIZATION = "authz" 
    API_REQUEST = "api_request"
    API_RESPONSE = "api_response"
    DATABASE = "database"
    EXTERNAL_SERVICE = "external_service"
    SECURITY = "security"
    PERFORMANCE = "performance"
    BUSINESS_LOGIC = "business"
    SYSTEM = "system"
    ERROR = "error"
    AUDIT = "audit"


# Context variables for correlation tracking
correlation_id: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)
user_id: ContextVar[Optional[str]] = ContextVar('user_id', default=None)
request_id: ContextVar[Optional[str]] = ContextVar('request_id', default=None)


# ============================================================================
# STRUCTURED LOGGER CLASS
# ============================================================================

class StructuredLogger:
    """
    Enhanced structured logger with context injection and monitoring integration.
    """
    
    def __init__(
        self, 
        name: str = "ideafly", 
        level: LogLevel = LogLevel.INFO,
        json_logs: bool = False,
        log_file: Optional[str] = None,
        enable_console: bool = True
    ):
        """
        Initialize structured logger.
        
        Args:
            name: Logger name
            level: Minimum log level
            json_logs: Whether to use JSON format
            log_file: Optional log file path
            enable_console: Whether to enable console output
        """
        self.name = name
        self.level = level
        self.json_logs = json_logs
        self.log_file = log_file
        self.enable_console = enable_console
        
        self._configure_structlog()
        self.logger = get_logger(name)
    
    def _configure_structlog(self) -> None:
        """Configure structlog with appropriate processors."""
        processors = [
            # Add correlation context
            self._add_correlation_context,
            # Add timestamp
            structlog.processors.TimeStamper(fmt="ISO"),
            # Add log level
            structlog.stdlib.add_log_level,
            # Add logger name
            structlog.stdlib.add_logger_name,
            # Stack info for errors
            structlog.processors.StackInfoRenderer(),
            # Exception formatting
            structlog.dev.set_exc_info,
        ]
        
        if self.json_logs:
            # JSON formatting for production
            processors.extend([
                structlog.processors.dict_tracebacks,
                structlog.processors.JSONRenderer()
            ])
        else:
            # Human-readable formatting for development
            processors.extend([
                structlog.dev.ConsoleRenderer(colors=True)
            ])
        
        configure(
            processors=processors,
            wrapper_class=structlog.stdlib.BoundLogger,
            logger_factory=LoggerFactory(),
            cache_logger_on_first_use=True,
        )
    
    @staticmethod
    def _add_correlation_context(logger, name, event_dict):
        """Add correlation context to log events."""
        # Add correlation ID
        corr_id = correlation_id.get()
        if corr_id:
            event_dict['correlation_id'] = corr_id
        
        # Add user ID
        uid = user_id.get()
        if uid:
            event_dict['user_id'] = uid
        
        # Add request ID
        req_id = request_id.get()
        if req_id:
            event_dict['request_id'] = req_id
        
        # Add service info
        event_dict['service'] = 'ideafly-backend'
        event_dict['version'] = '1.0.0'
        
        return event_dict
    
    def _log(
        self, 
        level: LogLevel, 
        message: str, 
        category: LogCategory = LogCategory.SYSTEM,
        **kwargs
    ) -> None:
        """Internal logging method with structured data."""
        log_data = {
            'message': message,
            'category': category.value,
            **kwargs
        }
        
        # Get the appropriate logger method
        log_method = getattr(self.logger, level.value.lower())
        log_method(message, **log_data)
    
    def debug(
        self, 
        message: str, 
        category: LogCategory = LogCategory.SYSTEM,
        **kwargs
    ) -> None:
        """Log debug message."""
        self._log(LogLevel.DEBUG, message, category, **kwargs)
    
    def info(
        self, 
        message: str, 
        category: LogCategory = LogCategory.SYSTEM,
        **kwargs
    ) -> None:
        """Log info message."""
        self._log(LogLevel.INFO, message, category, **kwargs)
    
    def warning(
        self, 
        message: str, 
        category: LogCategory = LogCategory.SYSTEM,
        **kwargs
    ) -> None:
        """Log warning message."""
        self._log(LogLevel.WARNING, message, category, **kwargs)
    
    def error(
        self, 
        message: str, 
        category: LogCategory = LogCategory.ERROR,
        error: Optional[Exception] = None,
        **kwargs
    ) -> None:
        """Log error message with optional exception details."""
        if error:
            kwargs['error_type'] = type(error).__name__
            kwargs['error_message'] = str(error)
            kwargs['traceback'] = traceback.format_exc()
        
        self._log(LogLevel.ERROR, message, category, **kwargs)
    
    def critical(
        self, 
        message: str, 
        category: LogCategory = LogCategory.ERROR,
        error: Optional[Exception] = None,
        **kwargs
    ) -> None:
        """Log critical message with optional exception details."""
        if error:
            kwargs['error_type'] = type(error).__name__
            kwargs['error_message'] = str(error)
            kwargs['traceback'] = traceback.format_exc()
        
        self._log(LogLevel.CRITICAL, message, category, **kwargs)
    
    def audit(
        self, 
        action: str, 
        resource: str, 
        result: str = "success",
        **kwargs
    ) -> None:
        """Log audit events for security and compliance."""
        self.info(
            f"Audit: {action} on {resource}",
            category=LogCategory.AUDIT,
            action=action,
            resource=resource,
            result=result,
            **kwargs
        )
    
    def security(
        self, 
        event_type: str, 
        description: str, 
        severity: str = "medium",
        **kwargs
    ) -> None:
        """Log security events."""
        self.warning(
            f"Security Event: {event_type}",
            category=LogCategory.SECURITY,
            event_type=event_type,
            description=description,
            severity=severity,
            **kwargs
        )
    
    def performance(
        self, 
        operation: str, 
        duration_ms: float, 
        **kwargs
    ) -> None:
        """Log performance metrics."""
        self.info(
            f"Performance: {operation}",
            category=LogCategory.PERFORMANCE,
            operation=operation,
            duration_ms=duration_ms,
            **kwargs
        )


# ============================================================================
# LOGGING DECORATORS AND CONTEXT MANAGERS
# ============================================================================

class LoggingContext:
    """Context manager for setting logging context."""
    
    def __init__(
        self, 
        correlation_id_val: Optional[str] = None,
        user_id_val: Optional[str] = None,
        request_id_val: Optional[str] = None
    ):
        self.correlation_id_val = correlation_id_val or str(uuid.uuid4())
        self.user_id_val = user_id_val
        self.request_id_val = request_id_val
        
        self.tokens = []
    
    def __enter__(self):
        """Enter logging context."""
        self.tokens.append(correlation_id.set(self.correlation_id_val))
        
        if self.user_id_val:
            self.tokens.append(user_id.set(self.user_id_val))
        
        if self.request_id_val:
            self.tokens.append(request_id.set(self.request_id_val))
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit logging context."""
        for token in reversed(self.tokens):
            token.var.reset(token)


def log_execution_time(
    logger: StructuredLogger,
    operation_name: str,
    category: LogCategory = LogCategory.PERFORMANCE
):
    """Decorator to log execution time of functions."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = (time.time() - start_time) * 1000
                logger.performance(
                    operation_name,
                    duration_ms=duration,
                    function=func.__name__,
                    success=True
                )
                return result
            except Exception as e:
                duration = (time.time() - start_time) * 1000
                logger.performance(
                    operation_name,
                    duration_ms=duration,
                    function=func.__name__,
                    success=False
                )
                logger.error(
                    f"Error in {func.__name__}",
                    error=e,
                    category=category
                )
                raise
        return wrapper
    return decorator


def log_api_call(
    logger: StructuredLogger,
    log_request: bool = True,
    log_response: bool = True,
    mask_fields: Optional[list] = None
):
    """Decorator to log API calls."""
    mask_fields = mask_fields or ['password', 'token', 'secret']
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            if log_request:
                # Mask sensitive fields
                safe_kwargs = {
                    k: "***MASKED***" if k in mask_fields else v
                    for k, v in kwargs.items()
                }
                logger.info(
                    f"API Request: {func.__name__}",
                    category=LogCategory.API_REQUEST,
                    function=func.__name__,
                    args=safe_kwargs
                )
            
            try:
                result = func(*args, **kwargs)
                duration = (time.time() - start_time) * 1000
                
                if log_response:
                    logger.info(
                        f"API Response: {func.__name__}",
                        category=LogCategory.API_RESPONSE,
                        function=func.__name__,
                        duration_ms=duration,
                        success=True
                    )
                
                return result
            except Exception as e:
                duration = (time.time() - start_time) * 1000
                logger.error(
                    f"API Error: {func.__name__}",
                    category=LogCategory.API_RESPONSE,
                    function=func.__name__,
                    duration_ms=duration,
                    success=False,
                    error=e
                )
                raise
        return wrapper
    return decorator


# ============================================================================
# GLOBAL LOGGER INSTANCE
# ============================================================================

# Default logger instance
default_logger = StructuredLogger(
    name="ideafly",
    level=LogLevel.INFO,
    json_logs=False,  # Set to True for production
    enable_console=True
)

# Convenience functions using default logger
def debug(message: str, category: LogCategory = LogCategory.SYSTEM, **kwargs):
    """Log debug message using default logger."""
    default_logger.debug(message, category, **kwargs)

def info(message: str, category: LogCategory = LogCategory.SYSTEM, **kwargs):
    """Log info message using default logger."""
    default_logger.info(message, category, **kwargs)

def warning(message: str, category: LogCategory = LogCategory.SYSTEM, **kwargs):
    """Log warning message using default logger."""
    default_logger.warning(message, category, **kwargs)

def error(
    message: str, 
    category: LogCategory = LogCategory.ERROR, 
    error: Optional[Exception] = None,
    **kwargs
):
    """Log error message using default logger."""
    default_logger.error(message, category, error, **kwargs)

def critical(
    message: str, 
    category: LogCategory = LogCategory.ERROR, 
    error: Optional[Exception] = None,
    **kwargs
):
    """Log critical message using default logger."""
    default_logger.critical(message, category, error, **kwargs)

def audit(action: str, resource: str, result: str = "success", **kwargs):
    """Log audit event using default logger."""
    default_logger.audit(action, resource, result, **kwargs)

def security(event_type: str, description: str, severity: str = "medium", **kwargs):
    """Log security event using default logger."""
    default_logger.security(event_type, description, severity, **kwargs)

def performance(operation: str, duration_ms: float, **kwargs):
    """Log performance metric using default logger."""
    default_logger.performance(operation, duration_ms, **kwargs)


# ============================================================================
# CONFIGURATION HELPERS
# ============================================================================

def configure_production_logging(
    log_level: LogLevel = LogLevel.INFO,
    log_file: Optional[str] = None
) -> StructuredLogger:
    """Configure logging for production environment."""
    return StructuredLogger(
        name="ideafly-prod",
        level=log_level,
        json_logs=True,
        log_file=log_file,
        enable_console=True
    )

def configure_development_logging(
    log_level: LogLevel = LogLevel.DEBUG
) -> StructuredLogger:
    """Configure logging for development environment."""
    return StructuredLogger(
        name="ideafly-dev",
        level=log_level,
        json_logs=False,
        enable_console=True
    )

def get_logger_for_module(module_name: str) -> StructuredLogger:
    """Get logger instance for specific module."""
    return StructuredLogger(name=module_name)


# ============================================================================
# FASTAPI INTEGRATION
# ============================================================================

def setup_fastapi_logging():
    """Setup logging integration with FastAPI."""
    import logging
    
    # Configure uvicorn logger
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.handlers.clear()
    
    # Configure access logger 
    access_logger = logging.getLogger("uvicorn.access")
    access_logger.handlers.clear()
    
    # Set appropriate log levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)


# ============================================================================
# MONITORING INTEGRATION
# ============================================================================

class MonitoringLogger:
    """Logger with monitoring service integration."""
    
    def __init__(self, base_logger: StructuredLogger):
        self.base_logger = base_logger
        self.metrics_enabled = True  # Enable/disable metrics collection
    
    def log_with_metrics(
        self, 
        level: LogLevel, 
        message: str, 
        category: LogCategory,
        **kwargs
    ):
        """Log message and send metrics to monitoring service."""
        # Log normally
        self.base_logger._log(level, message, category, **kwargs)
        
        # Send metrics (placeholder for actual monitoring integration)
        if self.metrics_enabled:
            self._send_metrics(level, category, **kwargs)
    
    def _send_metrics(self, level: LogLevel, category: LogCategory, **kwargs):
        """Send metrics to monitoring service (placeholder)."""
        # TODO: Integrate with actual monitoring service (Prometheus, DataDog, etc.)
        pass


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Example usage
    logger = StructuredLogger("example", LogLevel.DEBUG)
    
    with LoggingContext(correlation_id_val="test-123", user_id_val="user-456"):
        logger.info("Application started", category=LogCategory.SYSTEM)
        logger.audit("user_login", "authentication_system")
        logger.security("failed_login", "Multiple failed login attempts", severity="high")
        
        try:
            # Simulate an error
            raise ValueError("Test error")
        except Exception as e:
            logger.error("Test error occurred", error=e)
    
    # Performance logging
    logger.performance("database_query", 150.5, query="SELECT * FROM users")
    
    print("Logging examples completed!")