"""
Authentication dependency injection for IdeaFly Authentication System.

This module provides FastAPI dependencies for authentication middleware,
user injection, and authorization checks for protected routes.
"""

import logging
from typing import Optional, Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from ..core.database import get_db_session
from ..core.security import (
    verify_token,
    get_current_user_id,
    extract_token_from_header,
    get_token_claims
)
from ..core.exceptions import (
    AuthenticationException,
    InvalidTokenException,
    TokenExpiredException,
    AuthorizationException,
    AccountDisabledException,
    UserNotFoundException,
)
from ..auth.models import User

# Configure logging
logger = logging.getLogger(__name__)

# HTTP Bearer token scheme for OpenAPI documentation
bearer_scheme = HTTPBearer(
    scheme_name="Bearer",
    description="JWT Bearer token for authentication",
    auto_error=False  # Don't automatically raise errors
)


# ============================================================================
# TOKEN EXTRACTION DEPENDENCIES
# ============================================================================

async def get_bearer_token(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)
) -> Optional[str]:
    """
    Extract JWT token from Authorization header or fallback methods.
    
    Args:
        request: FastAPI request object
        credentials: HTTP Bearer credentials from header
        
    Returns:
        str: JWT token if found, None otherwise
        
    Note:
        This dependency doesn't raise errors for missing tokens,
        allowing optional authentication in some endpoints.
    """
    # Try Bearer token from Authorization header first
    if credentials and credentials.scheme == "Bearer":
        return credentials.credentials
    
    # Fallback: extract from Authorization header manually
    authorization_header = request.headers.get("Authorization")
    if authorization_header:
        token = extract_token_from_header(authorization_header)
        if token:
            return token
    
    # Fallback: check for token in query parameters (for development/testing)
    token_from_query = request.query_params.get("token")
    if token_from_query:
        logger.warning("Token extracted from query parameter - use Authorization header in production")
        return token_from_query
    
    return None


async def get_validated_token(
    token: Optional[str] = Depends(get_bearer_token)
) -> Optional[str]:
    """
    Validate JWT token and return it if valid.
    
    Args:
        token: JWT token from previous dependency
        
    Returns:
        str: Valid JWT token or None
        
    Raises:
        AuthenticationError: If token is invalid or expired
        
    Note:
        This dependency validates the token but doesn't require it.
        Use get_required_token for protected routes.
    """
    if not token:
        return None
    
    # Verify token signature and expiration
    token_payload = verify_token(token)
    if not token_payload:
        logger.warning("Invalid or expired JWT token provided")
        raise InvalidTokenException("Invalid or expired token")
    
    return token


async def get_required_token(
    token: Optional[str] = Depends(get_validated_token)
) -> str:
    """
    Get required JWT token for protected routes.
    
    Args:
        token: Validated JWT token from previous dependency
        
    Returns:
        str: Valid JWT token
        
    Raises:
        AuthenticationError: If no valid token is provided
        
    Example:
        ```python
        @router.get("/protected")
        async def protected_route(
            token: str = Depends(get_required_token)
        ):
            # Route is automatically protected
            return {"message": "Access granted"}
        ```
    """
    if not token:
        logger.warning("Protected route accessed without valid authentication")
        raise AuthenticationException("Authentication required")
    
    return token


# ============================================================================
# USER INJECTION DEPENDENCIES
# ============================================================================

async def get_current_user_optional(
    db: Session = Depends(get_db_session),
    token: Optional[str] = Depends(get_validated_token)
) -> Optional[User]:
    """
    Get current authenticated user (optional).
    
    Args:
        db: Database session
        token: Validated JWT token
        
    Returns:
        User: Current user if authenticated, None otherwise
        
    Example:
        ```python
        @router.get("/profile")
        async def get_profile(
            current_user: Optional[User] = Depends(get_current_user_optional)
        ):
            if current_user:
                return {"user": current_user.name}
            else:
                return {"message": "Anonymous user"}
        ```
    """
    if not token:
        return None
    
    # Extract user ID from token
    user_id = get_current_user_id(token)
    if not user_id:
        logger.error("Token is valid but contains no user ID")
        return None
    
    # Query user from database
    try:
        user = db.query(User).filter(
            User.id == user_id,
            User.is_active == True
        ).first()
        
        if not user:
            logger.warning(f"User {user_id} not found or inactive")
            return None
            
        return user
        
    except Exception as e:
        logger.error(f"Database error while fetching user {user_id}: {e}")
        return None


async def get_current_user(
    db: Session = Depends(get_db_session),
    token: str = Depends(get_required_token)
) -> User:
    """
    Get current authenticated user (required).
    
    Args:
        db: Database session
        token: Required valid JWT token
        
    Returns:
        User: Current authenticated user
        
    Raises:
        AuthenticationError: If user is not found or inactive
        
    Example:
        ```python
        @router.get("/dashboard")
        async def dashboard(
            current_user: User = Depends(get_current_user)
        ):
            return {"welcome": f"Hello, {current_user.name}!"}
        ```
    """
    # Extract user ID from token
    user_id = get_current_user_id(token)
    if not user_id:
        logger.error("Valid token contains no user ID")
        raise InvalidTokenException("Invalid token payload")
    
    # Query user from database
    try:
        user = db.query(User).filter(
            User.id == user_id,
            User.is_active == True
        ).first()
        
        if not user:
            logger.warning(f"Authenticated user {user_id} not found or inactive")
            raise UserNotFoundException(str(user_id))
            
        return user
        
    except AuthenticationException:
        # Re-raise authentication exceptions
        raise
    except Exception as e:
        logger.error(f"Database error while fetching user {user_id}: {e}")
        raise AuthenticationException("Authentication service error")


# ============================================================================
# AUTHORIZATION DEPENDENCIES
# ============================================================================

async def get_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Ensure current user is active.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User: Active user
        
    Raises:
        AuthorizationError: If user account is inactive
        
    Example:
        ```python
        @router.post("/create-resource")
        async def create_resource(
            user: User = Depends(get_active_user)
        ):
            # Only active users can create resources
            return {"created_by": user.name}
        ```
    """
    if not current_user.is_active:
        logger.warning(f"Inactive user {current_user.id} attempted to access protected resource")
        raise AccountDisabledException("Account is disabled")
    
    return current_user


def require_email_verified(
    current_user: User = Depends(get_active_user)
) -> User:
    """
    Ensure current user has verified their email.
    
    Args:
        current_user: Current active user
        
    Returns:
        User: User with verified email
        
    Raises:
        AuthorizationError: If user email is not verified
        
    Example:
        ```python
        @router.post("/sensitive-action")
        async def sensitive_action(
            user: User = Depends(require_email_verified)
        ):
            # Only users with verified emails can perform this action
            return {"message": "Action performed"}
        ```
    """
    # Note: Email verification field to be added to User model in future tasks
    # For now, all users are considered verified
    return current_user


# ============================================================================
# UTILITY DEPENDENCIES
# ============================================================================

async def get_token_claims(
    token: str = Depends(get_required_token)
) -> dict:
    """
    Get JWT token claims for the current request.
    
    Args:
        token: Valid JWT token
        
    Returns:
        dict: Token claims/payload
        
    Example:
        ```python
        @router.get("/token-info")
        async def token_info(
            claims: dict = Depends(get_token_claims)
        ):
            return {
                "issued_at": claims.get("iat"),
                "expires_at": claims.get("exp"),
                "auth_method": claims.get("auth_method")
            }
        ```
    """
    from ..core.security import get_token_claims as extract_claims
    return extract_claims(token)


async def get_user_id_from_token(
    token: str = Depends(get_required_token)
) -> str:
    """
    Extract user ID from JWT token.
    
    Args:
        token: Valid JWT token
        
    Returns:
        str: User ID from token
        
    Raises:
        AuthenticationError: If user ID is not in token
        
    Example:
        ```python
        @router.get("/my-resources")
        async def my_resources(
            user_id: str = Depends(get_user_id_from_token)
        ):
            # Use user_id without loading full user object
            return {"user_id": user_id}
        ```
    """
    user_id = get_current_user_id(token)
    if not user_id:
        raise InvalidTokenException("Token does not contain user ID")
    
    return user_id


# ============================================================================
# TYPE ANNOTATIONS FOR COMMON DEPENDENCIES
# ============================================================================

# Common type annotations for dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentUserOptional = Annotated[Optional[User], Depends(get_current_user_optional)]
ActiveUser = Annotated[User, Depends(get_active_user)]
VerifiedUser = Annotated[User, Depends(require_email_verified)]
ValidToken = Annotated[str, Depends(get_required_token)]
TokenClaims = Annotated[dict, Depends(get_token_claims)]
UserId = Annotated[str, Depends(get_user_id_from_token)]

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Exceptions
    "AuthenticationError",
    "AuthorizationError",
    
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
]