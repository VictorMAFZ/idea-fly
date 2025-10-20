"""
FastAPI router for authentication endpoints.

This module defines API routes for user authentication, registration,
and session management in the IdeaFly Authentication System.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.database import get_db_session
from ..core.exceptions import (
    EmailExistsException,
    ValidationException,
    DatabaseException,
    SecurityException,
    AuthenticationException,
    handle_api_exception
)
from .schemas import (
    UserRegistrationRequest,
    UserLoginRequest,
    AuthResponse,
    UserResponse,
    ErrorResponse
)
from .service import create_auth_service, AuthenticationService

# Configure logging
logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},  
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Not Found"},
        409: {"model": ErrorResponse, "description": "Conflict"},
        422: {"model": ErrorResponse, "description": "Validation Error"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)


# Dependency to get authentication service
def get_auth_service(
    db: Annotated[Session, Depends(get_db_session)]
) -> AuthenticationService:
    """
    Dependency to provide authentication service instance.
    
    Args:
        db: Database session from dependency injection
        
    Returns:
        AuthenticationService: Configured service instance
    """
    return create_auth_service(db)


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user account",
    description="Create a new user account with email and password authentication",
    operation_id="registerUser",
    responses={
        201: {
            "description": "User registered successfully",
            "model": AuthResponse,
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                        "expires_in": 86400,
                        "user": {
                            "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                            "name": "Juan Pérez",
                            "email": "juan.perez@example.com",
                            "is_active": True,
                            "created_at": "2025-10-20T10:30:00Z",
                            "updated_at": "2025-10-20T10:30:00Z"
                        }
                    }
                }
            }
        },
        400: {
            "description": "Invalid input data",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "error_code": "VALIDATION_ERROR",
                        "message": "Password must be at least 8 characters long",
                        "details": {
                            "field": "password",
                            "constraint": "min_length"
                        }
                    }
                }
            }
        },
        409: {
            "description": "Email already registered",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "error_code": "EMAIL_EXISTS",
                        "message": "User with this email already exists",
                        "details": {
                            "email": "juan.perez@example.com"
                        }
                    }
                }
            }
        }
    }
)
async def register_user(
    registration_data: UserRegistrationRequest,
    auth_service: Annotated[AuthenticationService, Depends(get_auth_service)]
) -> AuthResponse:
    """
    Register a new user account.
    
    Creates a new user account with the provided registration data,
    performs validation, and returns authentication tokens for immediate login.
    
    Args:
        registration_data: User registration information (name, email, password)
        auth_service: Authentication service from dependency injection
        
    Returns:
        AuthResponse: JWT tokens and user information
        
    Raises:
        HTTPException: Various HTTP error codes based on validation/business logic
    """
    try:
        logger.info(f"Registration attempt for email: {registration_data.email}")
        
        # Call authentication service to register user
        auth_response = await auth_service.register_user(registration_data)
        
        logger.info(f"User registered successfully: {registration_data.email}")
        
        return auth_response
        
    except EmailExistsException as e:
        logger.warning(f"Registration failed - email exists: {registration_data.email}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error_code": e.error_code.value,
                "message": e.error_message,
                "details": {
                    "email": registration_data.email
                }
            }
        )
        
    except ValidationException as e:
        logger.warning(f"Registration failed - validation error: {e.error_message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": e.error_code.value,
                "message": e.error_message,
                "details": e.error_details
            }
        )
        
    except SecurityException as e:
        logger.error(f"Registration failed - security error: {e.error_message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": e.error_code.value,
                "message": "Internal security error occurred",
                "details": None
            }
        )
        
    except DatabaseException as e:
        logger.error(f"Registration failed - database error: {e.error_message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": e.error_code.value,
                "message": "Database operation failed",
                "details": None
            }
        )
        
    except Exception as e:
        logger.error(f"Registration failed - unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": None
            }
        )


# Health check endpoint for the auth router
@router.get(
    "/health",
    response_model=dict,
    summary="Authentication service health check",
    description="Check if authentication service is operational",
    operation_id="authHealthCheck"
)
async def auth_health_check(
    auth_service: Annotated[AuthenticationService, Depends(get_auth_service)]
) -> dict:
    """
    Health check for authentication service.
    
    Returns status information about the authentication service
    and its dependencies.
    
    Args:
        auth_service: Authentication service from dependency injection
        
    Returns:
        dict: Health status information
    """
    try:
        # Simple health check - verify service can be created
        service_status = "healthy" if auth_service else "unhealthy"
        
        return {
            "status": service_status,
            "service": "authentication",
            "timestamp": "2025-10-20T00:00:00Z",
            "version": "1.0.0"
        }
        
    except Exception as e:
        logger.error(f"Auth health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error_code": "SERVICE_UNAVAILABLE",
                "message": "Authentication service is not available",
                "details": None
            }
        )


# Export router for main app registration
__all__ = ["router"]