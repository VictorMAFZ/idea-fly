"""
Security testing utilities for IdeaFly Authentication System.

This module provides utilities for testing authentication and security functions.
Should only be used in development and testing environments.
"""

from typing import Dict, Any
from datetime import datetime, timedelta, timezone

from .security import (
    create_user_token, 
    hash_password, 
    JWT_EXPIRE_MINUTES
)


def create_test_user_token(
    user_id: str = "test-user-123", 
    email: str = "test@example.com",
    auth_method: str = "password",
    expired: bool = False
) -> str:
    """
    Create a JWT token for testing purposes.
    
    Args:
        user_id: Test user ID (default: "test-user-123")
        email: Test email (default: "test@example.com")
        auth_method: Authentication method (default: "password")
        expired: Whether to create an expired token (default: False)
        
    Returns:
        str: Test JWT token
        
    Example:
        >>> token = create_test_user_token()
        >>> expired_token = create_test_user_token(expired=True)
    """
    if expired:
        # Create token that expired 1 hour ago
        expires_delta = timedelta(minutes=-60)
    else:
        # Use default expiration
        expires_delta = None
    
    return create_user_token(
        user_id=user_id,
        email=email,
        auth_method=auth_method,
        expires_delta=expires_delta
    )


def create_test_user_data() -> Dict[str, Any]:
    """
    Create test user data with hashed password.
    
    Returns:
        dict: Test user data ready for database insertion
        
    Example:
        >>> user_data = create_test_user_data()
        >>> # Can be used to create test users in database
    """
    return {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Test User",
        "email": "test@example.com",
        "hashed_password": hash_password("testpassword123"),
        "auth_provider": "email",
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }


def create_oauth_test_user_data() -> Dict[str, Any]:
    """
    Create test OAuth user data (no password).
    
    Returns:
        dict: Test OAuth user data ready for database insertion
        
    Example:
        >>> oauth_user = create_oauth_test_user_data()
        >>> # Can be used to create test OAuth users
    """
    return {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "name": "OAuth Test User",
        "email": "oauth.test@example.com", 
        "hashed_password": None,  # No password for OAuth users
        "auth_provider": "google",
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }


# Test credentials for development
TEST_USERS = {
    "email_user": {
        "email": "test@example.com",
        "password": "testpassword123",
        "name": "Test User"
    },
    "oauth_user": {
        "email": "oauth.test@example.com",
        "name": "OAuth Test User",
        "provider": "google"
    }
}


def get_test_password() -> str:
    """Get a valid test password that meets security requirements."""
    return "TestPassword123!"


__all__ = [
    "create_test_user_token",
    "create_test_user_data", 
    "create_oauth_test_user_data",
    "get_test_password",
    "TEST_USERS",
]