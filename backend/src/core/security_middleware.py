"""
Security middleware configuration for IdeaFly Backend.

Provides comprehensive security middleware including headers, CORS,
rate limiting, and other security measures for production deployment.
"""

import time
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
from urllib.parse import urlparse

from fastapi import FastAPI, Request, Response, HTTPException, status
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware as StarletteBaseHTTPMiddleware
from starlette.responses import JSONResponse

from .logging import StructuredLogger, default_logger, LogCategory


# ============================================================================
# SECURITY HEADERS MIDDLEWARE
# ============================================================================

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.
    """
    
    def __init__(
        self,
        app,
        hsts_max_age: int = 31536000,  # 1 year
        include_subdomains: bool = True,
        preload: bool = True,
        content_type_options: str = "nosniff",
        frame_options: str = "DENY",
        xss_protection: str = "1; mode=block",
        referrer_policy: str = "strict-origin-when-cross-origin",
        permissions_policy: Optional[str] = None,
        csp_policy: Optional[str] = None
    ):
        """
        Initialize security headers middleware.
        
        Args:
            app: FastAPI application
            hsts_max_age: Max age for HSTS header (seconds)
            include_subdomains: Whether to include subdomains in HSTS
            preload: Whether to include preload in HSTS
            content_type_options: X-Content-Type-Options header value
            frame_options: X-Frame-Options header value
            xss_protection: X-XSS-Protection header value
            referrer_policy: Referrer-Policy header value
            permissions_policy: Permissions-Policy header value
            csp_policy: Content-Security-Policy header value
        """
        super().__init__(app)
        self.hsts_max_age = hsts_max_age
        self.include_subdomains = include_subdomains
        self.preload = preload
        self.content_type_options = content_type_options
        self.frame_options = frame_options
        self.xss_protection = xss_protection
        self.referrer_policy = referrer_policy
        self.permissions_policy = permissions_policy
        self.csp_policy = csp_policy
    
    async def dispatch(self, request: Request, call_next):
        """Add security headers to response."""
        response = await call_next(request)
        
        # Strict Transport Security (HSTS)
        if request.url.scheme == "https":
            hsts_value = f"max-age={self.hsts_max_age}"
            if self.include_subdomains:
                hsts_value += "; includeSubDomains"
            if self.preload:
                hsts_value += "; preload"
            response.headers["Strict-Transport-Security"] = hsts_value
        
        # Content Type Options
        response.headers["X-Content-Type-Options"] = self.content_type_options
        
        # Frame Options
        response.headers["X-Frame-Options"] = self.frame_options
        
        # XSS Protection
        response.headers["X-XSS-Protection"] = self.xss_protection
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = self.referrer_policy
        
        # Permissions Policy (Feature Policy)
        if self.permissions_policy:
            response.headers["Permissions-Policy"] = self.permissions_policy
        
        # Content Security Policy
        if self.csp_policy:
            response.headers["Content-Security-Policy"] = self.csp_policy
        
        # Additional security headers
        response.headers["X-Robots-Tag"] = "noindex, nofollow"
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
        response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Resource-Policy"] = "cross-origin"
        
        return response


# ============================================================================
# RATE LIMITING MIDDLEWARE
# ============================================================================

class RateLimitingMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiting middleware.
    For production, consider using Redis or similar for distributed rate limiting.
    """
    
    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        logger: Optional[StructuredLogger] = None,
        exclude_paths: Optional[List[str]] = None
    ):
        """
        Initialize rate limiting middleware.
        
        Args:
            app: FastAPI application
            requests_per_minute: Max requests per minute per IP
            requests_per_hour: Max requests per hour per IP
            logger: Logger instance
            exclude_paths: Paths to exclude from rate limiting
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.logger = logger or default_logger
        self.exclude_paths = exclude_paths or ["/health", "/metrics"]
        
        # In-memory storage (use Redis in production)
        self._minute_buckets: Dict[str, Dict] = {}
        self._hour_buckets: Dict[str, Dict] = {}
    
    async def dispatch(self, request: Request, call_next):
        """Check rate limits and process request."""
        # Skip rate limiting for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)
        
        client_ip = self._get_client_ip(request)
        current_time = datetime.now()
        
        # Check rate limits
        if not self._check_rate_limits(client_ip, current_time):
            self.logger.warning(
                f"Rate limit exceeded for IP: {client_ip}",
                category=LogCategory.SECURITY,
                client_ip=client_ip,
                path=request.url.path,
                method=request.method
            )
            
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "message": "Too many requests. Please try again later.",
                    "retry_after": 60
                },
                headers={"Retry-After": "60"}
            )
        
        # Update rate limit counters
        self._update_rate_limits(client_ip, current_time)
        
        return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address."""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _check_rate_limits(self, client_ip: str, current_time: datetime) -> bool:
        """Check if client has exceeded rate limits."""
        minute_key = current_time.strftime("%Y-%m-%d %H:%M")
        hour_key = current_time.strftime("%Y-%m-%d %H")
        
        # Check minute limit
        minute_bucket = self._minute_buckets.get(client_ip, {})
        minute_count = minute_bucket.get(minute_key, 0)
        if minute_count >= self.requests_per_minute:
            return False
        
        # Check hour limit
        hour_bucket = self._hour_buckets.get(client_ip, {})
        hour_count = hour_bucket.get(hour_key, 0)
        if hour_count >= self.requests_per_hour:
            return False
        
        return True
    
    def _update_rate_limits(self, client_ip: str, current_time: datetime):
        """Update rate limit counters."""
        minute_key = current_time.strftime("%Y-%m-%d %H:%M")
        hour_key = current_time.strftime("%Y-%m-%d %H")
        
        # Update minute counter
        if client_ip not in self._minute_buckets:
            self._minute_buckets[client_ip] = {}
        self._minute_buckets[client_ip][minute_key] = \
            self._minute_buckets[client_ip].get(minute_key, 0) + 1
        
        # Update hour counter
        if client_ip not in self._hour_buckets:
            self._hour_buckets[client_ip] = {}
        self._hour_buckets[client_ip][hour_key] = \
            self._hour_buckets[client_ip].get(hour_key, 0) + 1
        
        # Clean old buckets (keep only current and previous periods)
        self._cleanup_old_buckets(current_time)
    
    def _cleanup_old_buckets(self, current_time: datetime):
        """Clean up old rate limit buckets."""
        current_minute = current_time.strftime("%Y-%m-%d %H:%M")
        current_hour = current_time.strftime("%Y-%m-%d %H")
        
        # Keep current and previous minute
        prev_minute = (current_time - timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M")
        
        # Keep current and previous hour
        prev_hour = (current_time - timedelta(hours=1)).strftime("%Y-%m-%d %H")
        
        # Clean minute buckets
        for ip in list(self._minute_buckets.keys()):
            bucket = self._minute_buckets[ip]
            keys_to_keep = {current_minute, prev_minute}
            keys_to_remove = set(bucket.keys()) - keys_to_keep
            for key in keys_to_remove:
                del bucket[key]
            
            # Remove empty IP buckets
            if not bucket:
                del self._minute_buckets[ip]
        
        # Clean hour buckets
        for ip in list(self._hour_buckets.keys()):
            bucket = self._hour_buckets[ip]
            keys_to_keep = {current_hour, prev_hour}
            keys_to_remove = set(bucket.keys()) - keys_to_keep
            for key in keys_to_remove:
                del bucket[key]
            
            # Remove empty IP buckets
            if not bucket:
                del self._hour_buckets[ip]


# ============================================================================
# REQUEST SIZE LIMITING MIDDLEWARE
# ============================================================================

class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to limit request body size.
    """
    
    def __init__(
        self,
        app,
        max_size: int = 10 * 1024 * 1024,  # 10MB
        logger: Optional[StructuredLogger] = None
    ):
        """
        Initialize request size limit middleware.
        
        Args:
            app: FastAPI application
            max_size: Maximum request size in bytes
            logger: Logger instance
        """
        super().__init__(app)
        self.max_size = max_size
        self.logger = logger or default_logger
    
    async def dispatch(self, request: Request, call_next):
        """Check request size and process."""
        content_length = request.headers.get("content-length")
        
        if content_length:
            try:
                size = int(content_length)
                if size > self.max_size:
                    self.logger.warning(
                        f"Request size limit exceeded: {size} bytes",
                        category=LogCategory.SECURITY,
                        client_ip=self._get_client_ip(request),
                        path=request.url.path,
                        size_bytes=size,
                        max_size_bytes=self.max_size
                    )
                    
                    return JSONResponse(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        content={
                            "error": "Request too large",
                            "message": f"Request size exceeds maximum allowed size of {self.max_size} bytes"
                        }
                    )
            except ValueError:
                pass
        
        return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address."""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        if request.client:
            return request.client.host
        
        return "unknown"


# ============================================================================
# CORS CONFIGURATION
# ============================================================================

def get_cors_config(environment: str = "development") -> dict:
    """
    Get CORS configuration based on environment.
    
    Args:
        environment: Environment name (development, staging, production)
    
    Returns:
        CORS configuration dictionary
    """
    if environment == "production":
        return {
            "allow_origins": [
                "https://ideafly.com",
                "https://www.ideafly.com",
                "https://app.ideafly.com"
            ],
            "allow_credentials": True,
            "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": [
                "Authorization",
                "Content-Type",
                "X-Requested-With",
                "X-Correlation-ID"
            ],
            "expose_headers": ["X-Correlation-ID", "X-Request-ID"],
            "max_age": 86400  # 24 hours
        }
    elif environment == "staging":
        return {
            "allow_origins": [
                "https://staging.ideafly.com",
                "https://staging-app.ideafly.com",
                "http://localhost:3000",
                "http://localhost:3001"
            ],
            "allow_credentials": True,
            "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": [
                "Authorization",
                "Content-Type",
                "X-Requested-With",
                "X-Correlation-ID"
            ],
            "expose_headers": ["X-Correlation-ID", "X-Request-ID"],
            "max_age": 3600  # 1 hour
        }
    else:  # development
        return {
            "allow_origins": [
                "http://localhost:3000",
                "http://localhost:3001",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:3001"
            ],
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
            "expose_headers": ["X-Correlation-ID", "X-Request-ID"],
            "max_age": 600  # 10 minutes
        }


# ============================================================================
# SECURITY CONFIGURATION HELPERS
# ============================================================================

def get_security_headers_config(environment: str = "development") -> dict:
    """
    Get security headers configuration based on environment.
    
    Args:
        environment: Environment name
    
    Returns:
        Security headers configuration
    """
    if environment == "production":
        return {
            "hsts_max_age": 31536000,  # 1 year
            "include_subdomains": True,
            "preload": True,
            "content_type_options": "nosniff",
            "frame_options": "DENY",
            "xss_protection": "1; mode=block",
            "referrer_policy": "strict-origin-when-cross-origin",
            "permissions_policy": (
                "geolocation=(), microphone=(), camera=(), "
                "payment=(), usb=(), magnetometer=(), gyroscope=()"
            ),
            "csp_policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "connect-src 'self' https:; "
                "frame-ancestors 'none'; "
                "base-uri 'self'"
            )
        }
    elif environment == "staging":
        return {
            "hsts_max_age": 86400,  # 1 day
            "include_subdomains": False,
            "preload": False,
            "content_type_options": "nosniff",
            "frame_options": "SAMEORIGIN",
            "xss_protection": "1; mode=block",
            "referrer_policy": "strict-origin-when-cross-origin",
            "permissions_policy": None,
            "csp_policy": None
        }
    else:  # development
        return {
            "hsts_max_age": 0,
            "include_subdomains": False,
            "preload": False,
            "content_type_options": "nosniff",
            "frame_options": "SAMEORIGIN",
            "xss_protection": "1; mode=block",
            "referrer_policy": "no-referrer-when-downgrade",
            "permissions_policy": None,
            "csp_policy": None
        }


def get_rate_limiting_config(environment: str = "development") -> dict:
    """
    Get rate limiting configuration based on environment.
    
    Args:
        environment: Environment name
    
    Returns:
        Rate limiting configuration
    """
    if environment == "production":
        return {
            "requests_per_minute": 60,
            "requests_per_hour": 1000,
            "exclude_paths": ["/health", "/metrics"]
        }
    elif environment == "staging":
        return {
            "requests_per_minute": 120,
            "requests_per_hour": 2000,
            "exclude_paths": ["/health", "/metrics", "/docs", "/redoc"]
        }
    else:  # development
        return {
            "requests_per_minute": 1000,
            "requests_per_hour": 10000,
            "exclude_paths": ["/health", "/metrics", "/docs", "/redoc", "/openapi.json"]
        }


def setup_security_middleware(
    app: FastAPI,
    environment: str = "development",
    logger: Optional[StructuredLogger] = None,
    enable_rate_limiting: bool = True,
    enable_request_size_limit: bool = True,
    max_request_size: int = 10 * 1024 * 1024
):
    """
    Setup all security middleware for FastAPI application.
    
    Args:
        app: FastAPI application instance
        environment: Environment name
        logger: Logger instance
        enable_rate_limiting: Whether to enable rate limiting
        enable_request_size_limit: Whether to enable request size limiting
        max_request_size: Maximum request size in bytes
    """
    # Add CORS middleware
    cors_config = get_cors_config(environment)
    app.add_middleware(CORSMiddleware, **cors_config)
    
    # Add security headers middleware
    security_config = get_security_headers_config(environment)
    app.add_middleware(SecurityHeadersMiddleware, **security_config)
    
    # Add rate limiting middleware (if enabled)
    if enable_rate_limiting:
        rate_config = get_rate_limiting_config(environment)
        app.add_middleware(
            RateLimitingMiddleware,
            logger=logger,
            **rate_config
        )
    
    # Add request size limit middleware (if enabled)
    if enable_request_size_limit:
        app.add_middleware(
            RequestSizeLimitMiddleware,
            max_size=max_request_size,
            logger=logger
        )


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def create_secure_app() -> FastAPI:
    """Example of creating a secure FastAPI app."""
    from fastapi import FastAPI
    import os
    
    app = FastAPI(
        title="IdeaFly API",
        description="Secure API with comprehensive security middleware",
        version="1.0.0"
    )
    
    environment = os.getenv("ENVIRONMENT", "development")
    
    # Setup security middleware
    setup_security_middleware(
        app,
        environment=environment,
        enable_rate_limiting=True,
        enable_request_size_limit=True
    )
    
    return app