"""
FastAPI Main Application for IdeaFly Authentication System.

This module creates and configures the FastAPI application instance with CORS,
middleware, error handling, and route registration.
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.gzip import GZipMiddleware

from .core.config import get_settings
from .core.database import init_database, close_database
from .core.logging_config import setup_logging
from .core.logging import configure_logging, default_logger
from .core.middleware import setup_logging_middleware
from .core.security_middleware import setup_security_middleware
from .core.exceptions import (
    BaseAPIException,
    is_api_exception,
    get_error_code_from_exception,
)
from .api.health import include_health_routers

# Configure logging
logger = logging.getLogger(__name__)

# Get application settings
settings = get_settings()


# ============================================================================
# CUSTOM MIDDLEWARE
# ============================================================================

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging."""
    
    async def dispatch(self, request: Request, call_next):
        """Log incoming requests and outgoing responses."""
        start_time = time.time()
        
        # Log incoming request
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Response: {response.status_code} "
            f"({process_time:.3f}s) for {request.method} {request.url.path}"
        )
        
        # Add processing time header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers."""
    
    async def dispatch(self, request: Request, call_next):
        """Add security headers to all responses."""
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), payment=(), usb=(), "
            "magnetometer=(), gyroscope=(), speaker=(), vibrate=(), fullscreen=()"
        )
        
        return response


# ============================================================================
# APPLICATION LIFECYCLE
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager for startup and shutdown events.
    
    Handles database initialization and cleanup, logging setup,
    and other application-wide resource management.
    """
    # Startup
    logger.info("🚀 Starting IdeaFly Authentication System...")
    
    try:
        # Setup logging
        setup_logging()
        logger.info("✅ Logging configured successfully")
        
        # Initialize database
        await init_database()
        logger.info("✅ Database initialized successfully")
        
        # Application is ready
        logger.info("🎯 Application startup complete - ready to serve requests")
        
        yield  # Application runs here
        
    finally:
        # Shutdown
        logger.info("🔄 Shutting down IdeaFly Authentication System...")
        
        try:
            # Close database connections
            await close_database()
            logger.info("✅ Database connections closed")
            
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")
        
        logger.info("👋 Shutdown complete")


# ============================================================================
# APPLICATION FACTORY
# ============================================================================

def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application instance.
    
    Returns:
        FastAPI: Configured application instance
        
    Example:
        ```python
        app = create_application()
        ```
    """
    # Create FastAPI application
    app = FastAPI(
        title="IdeaFly Authentication API",
        description=(
            "Sistema de autenticación robusto para IdeaFly que permite "
            "registro e inicio de sesión tradicional (email/contraseña) "
            "y mediante OAuth con Google. Incluye JWT para manejo de "
            "sesiones y validación completa de datos."
        ),
        version="1.0.0",
        docs_url="/docs" if settings.api_debug else None,
        redoc_url="/redoc" if settings.api_debug else None,
        openapi_url="/openapi.json" if settings.api_debug else None,
        lifespan=lifespan,
        # Custom OpenAPI metadata
        contact={
            "name": "IdeaFly Development Team",
            "email": "dev@ideafly.com",
        },
        license_info={
            "name": "Proprietary",
        },
    )
    
    # Configure middleware stack (order matters - first added = outermost)
    configure_middleware(app)
    
    # Configure error handlers
    configure_exception_handlers(app)
    
    # Register routes
    register_routes(app)
    
    return app


def configure_middleware(app: FastAPI) -> None:
    """
    Configure application middleware stack.
    
    Args:
        app: FastAPI application instance
        
    Note:
        Middleware is applied in reverse order (last added = first executed)
    """
    # Configure structured logging
    logger_instance = configure_logging(
        environment=settings.environment,
        log_level=getattr(settings, 'log_level', 'INFO'),
        service_name="ideafly-backend"
    )
    
    # Setup comprehensive security middleware
    setup_security_middleware(
        app,
        environment=settings.environment,
        logger=logger_instance,
        enable_rate_limiting=not settings.api_debug,  # Disable rate limiting in debug mode
        enable_request_size_limit=True,
        max_request_size=10 * 1024 * 1024  # 10MB
    )
    
    # Setup comprehensive logging middleware
    setup_logging_middleware(
        app,
        logger=logger_instance,
        enable_request_logging=True,
        enable_security_logging=True,
        enable_error_logging=True,
        log_request_body=settings.api_debug,  # Only log bodies in debug mode
        log_response_body=False
    )
    
    # Keep existing custom middleware for backward compatibility
    app.add_middleware(LoggingMiddleware)
    
    # GZip compression for large responses
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Trusted host protection
    if not settings.api_debug:
        allowed_hosts = ["localhost", "127.0.0.1", settings.api_host]
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)
    
    # CORS configuration (applied first = executed last)
    configure_cors(app)


def configure_cors(app: FastAPI) -> None:
    """
    Configure Cross-Origin Resource Sharing (CORS) settings.
    
    Args:
        app: FastAPI application instance
    """
    # Parse allowed origins from settings
    allowed_origins = [
        origin.strip() 
        for origin in settings.allowed_origins.split(",")
        if origin.strip()
    ]
    
    # Parse allowed methods
    allowed_methods = [
        method.strip() 
        for method in settings.allowed_methods.split(",")
        if method.strip()
    ]
    
    # Parse allowed headers
    allowed_headers = settings.allowed_headers.split(",") if settings.allowed_headers != "*" else ["*"]
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,  # Required for JWT cookies/headers
        allow_methods=allowed_methods,
        allow_headers=allowed_headers,
        expose_headers=["X-Process-Time"],  # Custom headers to expose
        max_age=3600,  # Cache preflight requests for 1 hour
    )
    
    logger.info(f"🌐 CORS configured - Origins: {allowed_origins}")


def configure_exception_handlers(app: FastAPI) -> None:
    """
    Configure global exception handlers for consistent error responses.
    
    Args:
        app: FastAPI application instance
    """
    
    @app.exception_handler(BaseAPIException)
    async def api_exception_handler(request: Request, exc: BaseAPIException):
        """Handle custom API exceptions with structured response format."""
        # The BaseAPIException already has the properly formatted detail
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail,  # Already contains success, error, data structure
            headers=getattr(exc, "headers", None),
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions with consistent JSON response format."""
        # Check if this is already our custom format (BaseAPIException inherits from HTTPException)
        if is_api_exception(exc):
            # Let the BaseAPIException handler take care of it
            return await api_exception_handler(request, exc)
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "error_code": f"HTTP_{exc.status_code}",
                    "message": exc.detail,
                    "details": None
                },
                "data": None
            },
            headers=getattr(exc, "headers", None),
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle request validation errors with detailed field information."""
        # Format validation errors to match our field error structure
        field_errors = []
        for error in exc.errors():
            field_errors.append({
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "code": error["type"].upper(),
                "value": error.get("input", "N/A"),
            })
        
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": {
                    "error_code": "VALIDATION_ERROR",
                    "message": "Validation failed for request data",
                    "details": {
                        "field_errors": field_errors,
                        "suggestion": "Please check the provided data and try again"
                    }
                },
                "data": None
            },
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions with generic error response."""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        
        # In production, don't expose internal error details
        error_details = None
        if settings.api_debug:
            error_details = {
                "exception_type": exc.__class__.__name__,
                "exception_message": str(exc),
                "suggestion": "This is an internal server error. Please contact support."
            }
        
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "error_code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                    "details": error_details
                },
                "data": None
            },
        )


def register_routes(app: FastAPI) -> None:
    """
    Register application routes and route groups.
    
    Args:
        app: FastAPI application instance
        
    Note:
        Routes will be registered when the corresponding modules are implemented
    """
    # Register comprehensive health and monitoring endpoints
    include_health_routers(app)
    
    # Root endpoint
    @app.get("/", tags=["root"])
    async def root():
        """Root endpoint with API information."""
        return {
            "success": True,
            "data": {
                "message": "IdeaFly Authentication API",
                "version": "1.0.0",
                "environment": settings.environment,
                "docs": "/docs" if settings.api_debug else "Not available in production",
                "health": "/health",
                "metrics": "/metrics",
                "monitoring": {
                    "health_detailed": "/health/detailed",
                    "readiness": "/health/ready", 
                    "liveness": "/health/live",
                    "metrics_prometheus": "/metrics/prometheus"
                }
            },
            "error": None
        }
    
    # Register authentication routes
    from .auth.router import router as auth_router
    app.include_router(auth_router)
    
    # TODO: Register user routes when implemented  
    # from .users.router import router as users_router
    # app.include_router(users_router, prefix="/users", tags=["users"])
    
    # NOTE: Authentication dependencies are available at:
    # from .dependencies import CurrentUser, CurrentUserOptional, ActiveUser
    # 
    # Example usage in route handlers:
    # @router.get("/protected")
    # async def protected_route(current_user: CurrentUser):
    #     return {"user": current_user.name}
    #
    # @router.get("/optional")  
    # async def optional_route(user: CurrentUserOptional):
    #     return {"user": user.name if user else "anonymous"}
    
    logger.info("📝 Routes registered successfully")


# ============================================================================
# APPLICATION INSTANCE
# ============================================================================

# Create the application instance
app = create_application()


# ============================================================================
# DEVELOPMENT SERVER
# ============================================================================

if __name__ == "__main__":
    """Run the application directly for development."""
    import uvicorn
    
    logger.info("🔧 Starting development server...")
    
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level="info" if settings.api_debug else "warning",
        access_log=settings.api_debug,
    )