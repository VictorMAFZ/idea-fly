"""
Authentication module for IdeaFly.

Provides user authentication functionality including models, schemas, services,
and API endpoints for registration, login, and OAuth integration.
"""

from .models import User, OAuthProfile, AuthProvider as ModelAuthProvider, OAuthProviderType, Base
from .schemas import (
    UserRegistrationRequest, UserLoginRequest, GoogleOAuthRequest,
    Token, AuthResponse, UserResponse, ErrorResponse, ValidationErrorResponse, LogoutResponse,
    UserInDB, UserCreate, UserUpdate, TokenPayload,
    AuthProvider, TokenType
)

__all__ = [
    # Models
    "User",
    "OAuthProfile", 
    "ModelAuthProvider",  # Renamed to avoid conflict with schema AuthProvider
    "OAuthProviderType",
    "Base",
    
    # Request schemas
    "UserRegistrationRequest",
    "UserLoginRequest",
    "GoogleOAuthRequest",
    
    # Response schemas  
    "Token",
    "AuthResponse",
    "UserResponse",
    "ErrorResponse",
    "ValidationErrorResponse",
    "LogoutResponse",
    
    # Internal schemas
    "UserInDB",
    "UserCreate", 
    "UserUpdate",
    "TokenPayload",
    
    # Enums
    "AuthProvider",
    "TokenType",
]
# Handles user authentication, registration, and session management