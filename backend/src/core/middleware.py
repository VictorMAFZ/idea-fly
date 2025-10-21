"""
FastAPI Logging Middleware for IdeaFly Backend.

Provides comprehensive request/response logging, correlation tracking,
and performance monitoring for FastAPI applications.
"""

import time
import uuid
from typing import Callable, Optional
from urllib.parse import parse_qs, urlparse

from fastapi import FastAPI, Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from .logging import (
    LoggingContext,
    LogCategory,
    StructuredLogger,
    default_logger
)


# ============================================================================
# REQUEST LOGGING MIDDLEWARE
# ============================================================================

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses with structured data.
    """
    
    def __init__(
        self, 
        app: ASGIApp,
        logger: Optional[StructuredLogger] = None,
        log_request_body: bool = False,
        log_response_body: bool = False,
        skip_paths: Optional[list] = None,
        mask_headers: Optional[list] = None,
        mask_query_params: Optional[list] = None
    ):
        """
        Initialize request logging middleware.
        
        Args:
            app: ASGI application
            logger: Logger instance to use
            log_request_body: Whether to log request body
            log_response_body: Whether to log response body
            skip_paths: List of paths to skip logging
            mask_headers: List of header names to mask
            mask_query_params: List of query parameters to mask
        """
        super().__init__(app)
        self.logger = logger or default_logger
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.skip_paths = skip_paths or ["/health", "/metrics", "/docs", "/redoc", "/openapi.json"]
        self.mask_headers = mask_headers or [
            "authorization", "cookie", "x-api-key", "x-auth-token"
        ]
        self.mask_query_params = mask_query_params or [
            "password", "token", "secret", "key"
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and response with logging."""
        start_time = time.time()
        
        # Skip logging for specified paths
        if request.url.path in self.skip_paths:
            return await call_next(request)
        
        # Generate correlation ID
        correlation_id = str(uuid.uuid4())
        request_id = str(uuid.uuid4())
        
        # Extract user information if available
        user_id = None
        if hasattr(request.state, 'user') and request.state.user:
            user_id = getattr(request.state.user, 'id', None)
        
        # Set logging context
        with LoggingContext(
            correlation_id_val=correlation_id,
            request_id_val=request_id,
            user_id_val=user_id
        ):
            # Log incoming request
            await self._log_request(request, correlation_id, request_id)
            
            # Process request
            try:
                response = await call_next(request)
                duration_ms = (time.time() - start_time) * 1000
                
                # Log outgoing response
                await self._log_response(request, response, duration_ms, correlation_id)
                
                # Add correlation headers to response
                response.headers["X-Correlation-ID"] = correlation_id
                response.headers["X-Request-ID"] = request_id
                
                return response
            
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                
                # Log error
                self.logger.error(
                    f"Request processing error: {request.method} {request.url.path}",
                    category=LogCategory.API_REQUEST,
                    method=request.method,
                    path=request.url.path,
                    duration_ms=duration_ms,
                    error=e,
                    correlation_id=correlation_id,
                    request_id=request_id
                )
                
                raise
    
    async def _log_request(self, request: Request, correlation_id: str, request_id: str):
        """Log incoming request details."""
        # Prepare request data
        request_data = {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": self._mask_query_params(dict(request.query_params)),
            "headers": self._mask_headers(dict(request.headers)),
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent"),
            "correlation_id": correlation_id,
            "request_id": request_id
        }
        
        # Add request body if enabled
        if self.log_request_body:
            try:
                body = await request.body()
                if body:
                    # Only log non-binary content
                    try:
                        request_data["body"] = body.decode("utf-8")[:1000]  # Limit size
                    except UnicodeDecodeError:
                        request_data["body"] = "<binary data>"
            except Exception:
                request_data["body"] = "<unable to read body>"
        
        self.logger.info(
            f"Incoming request: {request.method} {request.url.path}",
            category=LogCategory.API_REQUEST,
            **request_data
        )
    
    async def _log_response(
        self, 
        request: Request, 
        response: Response, 
        duration_ms: float, 
        correlation_id: str
    ):
        """Log outgoing response details."""
        # Prepare response data
        response_data = {
            "status_code": response.status_code,
            "headers": self._mask_headers(dict(response.headers)),
            "duration_ms": duration_ms,
            "correlation_id": correlation_id
        }
        
        # Determine log level based on status code
        if 400 <= response.status_code < 500:
            log_level = "warning"
            message = f"Client error response: {request.method} {request.url.path}"
        elif response.status_code >= 500:
            log_level = "error"
            message = f"Server error response: {request.method} {request.url.path}"
        else:
            log_level = "info"
            message = f"Successful response: {request.method} {request.url.path}"
        
        # Log response
        log_method = getattr(self.logger, log_level)
        log_method(
            message,
            category=LogCategory.API_RESPONSE,
            **response_data
        )
        
        # Log performance metrics
        self.logger.performance(
            f"{request.method} {request.url.path}",
            duration_ms=duration_ms,
            status_code=response.status_code,
            method=request.method,
            path=request.url.path
        )
    
    def _mask_headers(self, headers: dict) -> dict:
        """Mask sensitive headers."""
        masked = {}
        for key, value in headers.items():
            if key.lower() in self.mask_headers:
                masked[key] = "***MASKED***"
            else:
                masked[key] = value
        return masked
    
    def _mask_query_params(self, params: dict) -> dict:
        """Mask sensitive query parameters."""
        masked = {}
        for key, value in params.items():
            if key.lower() in self.mask_query_params:
                masked[key] = "***MASKED***"
            else:
                masked[key] = value
        return masked
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address."""
        # Check for forwarded headers first (for load balancers/proxies)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fall back to direct connection
        if request.client:
            return request.client.host
        
        return "unknown"


# ============================================================================
# SECURITY LOGGING MIDDLEWARE
# ============================================================================

class SecurityLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging security-related events.
    """
    
    def __init__(
        self, 
        app: ASGIApp,
        logger: Optional[StructuredLogger] = None,
        track_failed_auth: bool = True,
        track_rate_limiting: bool = True,
        sensitive_endpoints: Optional[list] = None
    ):
        """
        Initialize security logging middleware.
        
        Args:
            app: ASGI application
            logger: Logger instance to use
            track_failed_auth: Whether to track failed authentication
            track_rate_limiting: Whether to track rate limiting events
            sensitive_endpoints: List of sensitive endpoint patterns
        """
        super().__init__(app)
        self.logger = logger or default_logger
        self.track_failed_auth = track_failed_auth
        self.track_rate_limiting = track_rate_limiting
        self.sensitive_endpoints = sensitive_endpoints or [
            "/api/auth/login",
            "/api/auth/register", 
            "/api/auth/reset-password",
            "/api/users/profile"
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request for security logging."""
        response = await call_next(request)
        
        # Log security events based on response
        await self._log_security_events(request, response)
        
        return response
    
    async def _log_security_events(self, request: Request, response: Response):
        """Log security-related events."""
        # Track failed authentication attempts
        if (self.track_failed_auth and 
            request.url.path in self.sensitive_endpoints and
            response.status_code == 401):
            
            self.logger.security(
                "authentication_failure",
                f"Failed authentication attempt on {request.url.path}",
                severity="medium",
                path=request.url.path,
                method=request.method,
                client_ip=self._get_client_ip(request),
                user_agent=request.headers.get("user-agent")
            )
        
        # Track suspicious activity (multiple 403s, etc.)
        if response.status_code == 403:
            self.logger.security(
                "authorization_failure",
                f"Access denied to {request.url.path}",
                severity="low",
                path=request.url.path,
                method=request.method,
                client_ip=self._get_client_ip(request)
            )
        
        # Track rate limiting
        if (self.track_rate_limiting and response.status_code == 429):
            self.logger.security(
                "rate_limit_exceeded",
                f"Rate limit exceeded for {request.url.path}",
                severity="medium",
                path=request.url.path,
                client_ip=self._get_client_ip(request)
            )
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address."""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        if request.client:
            return request.client.host
        
        return "unknown"


# ============================================================================
# ERROR LOGGING MIDDLEWARE
# ============================================================================

class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for comprehensive error logging and handling.
    """
    
    def __init__(
        self, 
        app: ASGIApp,
        logger: Optional[StructuredLogger] = None,
        log_stack_trace: bool = True,
        include_request_data: bool = True
    ):
        """
        Initialize error logging middleware.
        
        Args:
            app: ASGI application
            logger: Logger instance to use
            log_stack_trace: Whether to include stack traces
            include_request_data: Whether to include request data in error logs
        """
        super().__init__(app)
        self.logger = logger or default_logger
        self.log_stack_trace = log_stack_trace
        self.include_request_data = include_request_data
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with error handling."""
        try:
            return await call_next(request)
        except Exception as e:
            # Log the error with context
            await self._log_error(request, e)
            
            # Re-raise to let FastAPI handle the response
            raise
    
    async def _log_error(self, request: Request, error: Exception):
        """Log error with detailed context."""
        error_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
        }
        
        if self.include_request_data:
            error_data.update({
                "method": request.method,
                "path": request.url.path,
                "client_ip": self._get_client_ip(request),
                "user_agent": request.headers.get("user-agent")
            })
        
        self.logger.error(
            f"Unhandled error in {request.method} {request.url.path}",
            category=LogCategory.ERROR,
            error=error if self.log_stack_trace else None,
            **error_data
        )
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address."""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        if request.client:
            return request.client.host
        
        return "unknown"


# ============================================================================
# MIDDLEWARE SETUP HELPERS
# ============================================================================

def setup_logging_middleware(
    app: FastAPI,
    logger: Optional[StructuredLogger] = None,
    enable_request_logging: bool = True,
    enable_security_logging: bool = True,
    enable_error_logging: bool = True,
    log_request_body: bool = False,
    log_response_body: bool = False
):
    """
    Setup all logging middleware for FastAPI application.
    
    Args:
        app: FastAPI application instance
        logger: Logger instance to use
        enable_request_logging: Whether to enable request/response logging
        enable_security_logging: Whether to enable security event logging
        enable_error_logging: Whether to enable error logging
        log_request_body: Whether to log request bodies
        log_response_body: Whether to log response bodies
    """
    if enable_error_logging:
        app.add_middleware(
            ErrorLoggingMiddleware,
            logger=logger
        )
    
    if enable_security_logging:
        app.add_middleware(
            SecurityLoggingMiddleware,
            logger=logger
        )
    
    if enable_request_logging:
        app.add_middleware(
            RequestLoggingMiddleware,
            logger=logger,
            log_request_body=log_request_body,
            log_response_body=log_response_body
        )


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def create_app_with_logging() -> FastAPI:
    """Example of creating FastAPI app with logging middleware."""
    from fastapi import FastAPI
    from .logging import configure_development_logging
    
    app = FastAPI(title="IdeaFly API")
    logger = configure_development_logging()
    
    # Setup logging middleware
    setup_logging_middleware(
        app, 
        logger=logger,
        log_request_body=False,  # Set to True for debugging
        log_response_body=False  # Set to True for debugging
    )
    
    return app