"""
Dependency injection for IdeaFly Authentication System.

This module provides FastAPI dependencies for authentication, database sessions,
and other cross-cutting concerns that can be injected into route handlers.
"""

# Authentication dependencies
from .auth import (
    # Token dependencies
    get_bearer_token,
    get_validated_token,
    get_required_token,
    
    # User dependencies
    get_current_user_optional,
    get_current_user,
    get_active_user,
    require_email_verified,
    
    # Utility dependencies
    get_token_claims,
    get_user_id_from_token,
    
    # Type annotations
    CurrentUser,
    CurrentUserOptional,
    ActiveUser,
    VerifiedUser,
    ValidToken,
    TokenClaims,
    UserId,
)

# Re-export database dependency for convenience
from ..core.database import get_db_session

__all__ = [
    # Token dependencies
    "get_bearer_token",
    "get_validated_token",
    "get_required_token",
    
    # User dependencies
    "get_current_user_optional",
    "get_current_user",
    "get_active_user",
    "require_email_verified",
    
    # Utility dependencies
    "get_token_claims", 
    "get_user_id_from_token",
    
    # Type annotations
    "CurrentUser",
    "CurrentUserOptional",
    "ActiveUser", 
    "VerifiedUser",
    "ValidToken",
    "TokenClaims",
    "UserId",
    
    # Database dependency
    "get_db_session",
]