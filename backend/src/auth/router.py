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
    ServerException,
    AuthenticationException
)
from .schemas import (
    UserRegistrationRequest,
    UserLoginRequest,
    GoogleTokenRequest,
    AuthResponse,
    UserResponse,
    ErrorResponse,
    LogoutResponse
)
from .service import create_auth_service, AuthenticationService
from .oauth_service import GoogleOAuthService, get_google_oauth_service
from ..dependencies.auth import get_current_user
from .models import User

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
        
    except ServerException as e:
        logger.error(f"Registration failed - server error: {e.error_message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": e.error_code.value,
                "message": "Internal server error occurred",
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


@router.post(
    "/login", 
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="User login",
    description="Authenticate user with email and password, return JWT token",
    operation_id="loginUser"
)
async def login_user(
    login_data: UserLoginRequest,
    auth_service: Annotated[AuthenticationService, Depends(get_auth_service)]
) -> AuthResponse:
    """
    Authenticate user with email and password.
    
    This endpoint handles user login by validating credentials and returning
    a JWT token for session management. The token should be included in
    subsequent requests via Authorization header.
    
    Args:
        login_data: User login credentials (email and password)
        auth_service: Authentication service from dependency injection
        
    Returns:
        AuthResponse: User profile and JWT token
        
    Raises:
        HTTPException 400: Invalid input format
        HTTPException 401: Invalid credentials or inactive account
        HTTPException 500: Internal server error
        
    Example:
        ```
        POST /auth/login
        {
            "email": "juan.perez@example.com",
            "password": "securePassword123"
        }
        
        Response:
        {
            "user": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Juan Pérez",
                "email": "juan.perez@example.com",
                "email_verified": true,
                "is_active": true,
                "created_at": "2025-10-20T10:30:00Z",
                "last_login": "2025-10-20T15:45:00Z"
            },
            "token": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 86400
            }
        }
        ```
    """
    try:
        logger.info(f"Login attempt for email: {login_data.email}")
        
        # Authenticate user and generate token
        user_profile, token = await auth_service.authenticate_user(login_data)
        
        logger.info(f"Login successful for user: {user_profile.id}")
        
        # Return token as AuthResponse (per API contract)
        return token
        
    except ValidationException as e:
        logger.warning(f"Login validation failed for {login_data.email}: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": e.error_code or "VALIDATION_ERROR",
                "message": e.message,
                "details": e.details
            }
        )
        
    except AuthenticationException as e:
        logger.warning(f"Authentication failed for {login_data.email}: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error_code": e.error_code or "INVALID_CREDENTIALS", 
                "message": e.message or "Email or password is incorrect",
                "details": None
            }
        )
        
    except DatabaseException as e:
        logger.error(f"Database error during login for {login_data.email}: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "DATABASE_ERROR",
                "message": "A database error occurred during login",
                "details": None
            }
        )
        
    except ServerException as e:
        logger.error(f"Server error during login for {login_data.email}: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": e.error_code or "SERVER_ERROR",
                "message": e.message or "An internal server error occurred",
                "details": None
            }
        )
        
    except Exception as e:
        logger.error(f"Login failed - unexpected error for {login_data.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred during login",
                "details": None
            }
        )


@router.post(
    "/google",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate with Google OAuth",
    description="""
    Authenticate user using Google OAuth access token.
    
    This endpoint accepts a Google OAuth access token obtained from the frontend
    and validates it with Google's API. If valid, it either:
    - Returns existing user if account exists
    - Creates new account for new users
    - Links OAuth to existing email account
    
    **Security Features:**
    - Token validation with Google API
    - Automatic user linking by email
    - Secure JWT generation
    - Comprehensive audit logging
    
    **Flow:**
    1. Frontend obtains Google OAuth token
    2. Sends token to this endpoint
    3. Backend validates with Google
    4. User created/found/linked
    5. JWT token returned
    """,
    responses={
        200: {
            "description": "OAuth authentication successful",
            "model": AuthResponse
        },
        400: {
            "description": "Invalid request format",
            "model": ErrorResponse
        },
        401: {
            "description": "Invalid or expired Google token",
            "model": ErrorResponse
        },
        422: {
            "description": "Validation errors in request data",
            "model": ErrorResponse
        },
        500: {
            "description": "Internal server error during OAuth process",
            "model": ErrorResponse
        }
    }
)
async def authenticate_with_google(
    oauth_request: GoogleTokenRequest,
    db: Annotated[Session, Depends(get_db_session)],
    oauth_service: Annotated[GoogleOAuthService, Depends(get_google_oauth_service)]
) -> AuthResponse:
    """
    Authenticate user with Google OAuth access token.
    
    Args:
        oauth_request: Request containing Google OAuth access token
        db: Database session from dependency injection
        oauth_service: Google OAuth service from dependency injection
        
    Returns:
        AuthResponse: JWT token and user information
        
    Raises:
        HTTPException: Various HTTP errors based on authentication result
    """
    try:
        logger.info("Processing Google OAuth authentication request")
        
        # Authenticate with Google OAuth service
        token_response = await oauth_service.authenticate_with_google(
            access_token=oauth_request.access_token,
            db=db
        )
        
        logger.info(f"Google OAuth authentication successful for user: {token_response.user.email}")
        
        return token_response
        
    except AuthenticationException as e:
        logger.warning(f"Google OAuth authentication failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error_code": "OAUTH_AUTHENTICATION_FAILED",
                "message": str(e),
                "details": "Please ensure you are using a valid Google OAuth token"
            }
        )
        
    except ValidationException as e:
        logger.warning(f"Google OAuth validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error_code": "OAUTH_VALIDATION_ERROR",
                "message": str(e),
                "details": "User information from Google could not be processed"
            }
        )
        
    except DatabaseException as e:
        logger.error(f"Database error during Google OAuth: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "DATABASE_ERROR",
                "message": "Failed to process OAuth authentication",
                "details": None
            }
        )
        
    except Exception as e:
        logger.error(f"Unexpected error during Google OAuth: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "OAUTH_SERVER_ERROR", 
                "message": "An unexpected error occurred during OAuth authentication",
                "details": None
            }
        )


@router.get(
    "/users/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
    description="Retrieve the profile information of the currently authenticated user",
    operation_id="getCurrentUser",
    responses={
        200: {
            "model": UserResponse,
            "description": "User profile retrieved successfully"
        },
        401: {
            "model": ErrorResponse,
            "description": "Authentication required"
        }
    }
)
async def get_current_user_profile(
    current_user: Annotated[User, Depends(get_current_user)]
) -> UserResponse:
    """
    Get current authenticated user profile.
    
    This endpoint returns the profile information of the currently authenticated user
    based on the JWT token provided in the Authorization header.
    
    Args:
        current_user: Current authenticated user from JWT token
        
    Returns:
        UserResponse: User profile information
        
    Raises:
        HTTPException: If user is not authenticated (401)
    """
    try:
        logger.info(f"Profile request for user: {current_user.email} (ID: {current_user.id})")
        
        # Convert User model to UserResponse schema
        user_response = UserResponse(
            id=current_user.id,
            name=current_user.name,
            email=current_user.email,
            is_active=current_user.is_active,
            auth_provider=current_user.auth_provider,
            created_at=current_user.created_at
        )
        
        return user_response
        
    except Exception as e:
        logger.error(f"Error retrieving profile for user {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "PROFILE_ERROR",
                "message": "An error occurred while retrieving user profile",
                "details": None
            }
        )


@router.post(
    "/logout",
    response_model=LogoutResponse,
    status_code=status.HTTP_200_OK,
    summary="User logout",
    description="Logout current authenticated user and invalidate their session",
    operation_id="logoutUser",
    responses={
        200: {
            "model": LogoutResponse,
            "description": "User logged out successfully"
        },
        401: {
            "model": ErrorResponse,
            "description": "Authentication required"
        }
    }
)
async def logout_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> LogoutResponse:
    """
    Logout authenticated user.
    
    This endpoint logs out the current authenticated user by invalidating their session.
    In a stateless JWT system, this primarily serves as a client-side logout trigger
    since JWT tokens cannot be invalidated server-side without additional infrastructure.
    
    The client should remove the JWT token from storage after receiving this response.
    
    Args:
        current_user: Current authenticated user from JWT token
        
    Returns:
        LogoutResponse: Logout confirmation message
        
    Raises:
        HTTPException: If user is not authenticated (401)
    """
    try:
        logger.info(f"User logout: {current_user.email} (ID: {current_user.id})")
        
        # In a stateless JWT system, we don't maintain server-side sessions to invalidate
        # The logout is primarily handled client-side by removing the token
        # However, we can log the logout event for security/audit purposes
        
        # Future enhancement: Implement JWT blacklist/token revocation
        # This would require a token blacklist storage mechanism (Redis, database)
        
        return LogoutResponse(
            message="Logged out successfully"
        )
        
    except Exception as e:
        logger.error(f"Logout error for user {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "LOGOUT_ERROR", 
                "message": "An error occurred during logout",
                "details": None
            }
        )


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