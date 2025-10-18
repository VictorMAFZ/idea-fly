"""
Core security utilities for IdeaFly Authentication System.

This module provides essential security functions including password hashing,
JWT token creation and validation, and other cryptographic utilities.
"""

import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Union

from jose import JWTError, jwt
from passlib.context import CryptContext
from passlib.hash import bcrypt

from .config import get_settings


# ============================================================================
# CONFIGURATION AND CONSTANTS
# ============================================================================

# Get application settings
settings = get_settings()

# Password hashing context with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration constants
JWT_ALGORITHM = settings.jwt_algorithm
JWT_SECRET_KEY = settings.jwt_secret_key
JWT_EXPIRE_MINUTES = settings.jwt_expire_minutes

# Security constants
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128
TOKEN_TYPE = "bearer"


# ============================================================================
# PASSWORD HASHING UTILITIES
# ============================================================================

def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.
    
    Args:
        password: The plain text password to hash
        
    Returns:
        str: The hashed password safe for database storage
        
    Raises:
        ValueError: If password is empty or None
        
    Example:
        >>> hashed = hash_password("my_secure_password")
        >>> # Returns: $2b$12$...
    """
    if not password:
        raise ValueError("Password cannot be empty")
    
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters long")
    
    if len(password) > MAX_PASSWORD_LENGTH:
        raise ValueError(f"Password cannot exceed {MAX_PASSWORD_LENGTH} characters")
    
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.
    
    Args:
        plain_password: The plain text password to verify
        hashed_password: The stored hashed password
        
    Returns:
        bool: True if password matches, False otherwise
        
    Example:
        >>> is_valid = verify_password("my_password", stored_hash)
        >>> # Returns: True or False
    """
    if not plain_password or not hashed_password:
        return False
    
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # Handle any bcrypt verification errors
        return False


def needs_rehash(hashed_password: str) -> bool:
    """
    Check if a hashed password needs to be rehashed due to updated security parameters.
    
    Args:
        hashed_password: The stored hashed password
        
    Returns:
        bool: True if password should be rehashed, False otherwise
        
    Example:
        >>> should_rehash = needs_rehash(stored_hash)
        >>> if should_rehash:
        ...     new_hash = hash_password(plain_password)
    """
    if not hashed_password:
        return False
    
    try:
        return pwd_context.needs_update(hashed_password)
    except Exception:
        # If we can't determine, assume it needs rehashing
        return True


# ============================================================================
# JWT TOKEN UTILITIES
# ============================================================================

def create_access_token(
    data: Dict[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token with user data and expiration.
    
    Args:
        data: The data to encode in the token (user_id, email, etc.)
        expires_delta: Custom expiration time (defaults to JWT_EXPIRE_MINUTES)
        
    Returns:
        str: The encoded JWT token
        
    Raises:
        ValueError: If data is empty or invalid
        
    Example:
        >>> token = create_access_token({
        ...     "sub": str(user.id),
        ...     "email": user.email,
        ...     "auth_method": "password"
        ... })
    """
    if not data:
        raise ValueError("Token data cannot be empty")
    
    # Create a copy of the data to avoid modifying the original
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    
    # Add standard JWT claims
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": TOKEN_TYPE
    })
    
    # Encode and return the token
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def create_user_token(
    user_id: str, 
    email: str, 
    auth_method: str = "password",
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT token for a specific user with standard claims.
    
    Args:
        user_id: The user's unique identifier (UUID as string)
        email: The user's email address
        auth_method: Authentication method used ("password", "google_oauth")
        expires_delta: Custom expiration time
        
    Returns:
        str: The encoded JWT token
        
    Example:
        >>> token = create_user_token(
        ...     user_id=str(user.id),
        ...     email=user.email,
        ...     auth_method="password"
        ... )
    """
    token_data = {
        "sub": user_id,  # Standard JWT "subject" claim
        "email": email,
        "auth_method": auth_method
    }
    
    return create_access_token(token_data, expires_delta)


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT token.
    
    Args:
        token: The JWT token to decode
        
    Returns:
        dict: The decoded token payload
        
    Raises:
        JWTError: If token is invalid, expired, or malformed
        ValueError: If token is empty
        
    Example:
        >>> payload = decode_token(token)
        >>> user_id = payload.get("sub")
        >>> email = payload.get("email")
    """
    if not token:
        raise ValueError("Token cannot be empty")
    
    try:
        payload = jwt.decode(
            token, 
            JWT_SECRET_KEY, 
            algorithms=[JWT_ALGORITHM]
        )
        return payload
    except JWTError as e:
        raise JWTError(f"Token validation failed: {str(e)}") from e


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify a JWT token and return payload if valid.
    
    This is a safe version of decode_token that returns None instead of raising exceptions.
    
    Args:
        token: The JWT token to verify
        
    Returns:
        dict or None: The token payload if valid, None if invalid
        
    Example:
        >>> payload = verify_token(token)
        >>> if payload:
        ...     user_id = payload.get("sub")
        ... else:
        ...     # Token is invalid or expired
        ...     return {"error": "Invalid token"}
    """
    try:
        return decode_token(token)
    except (JWTError, ValueError):
        return None


def get_token_expiry(token: str) -> Optional[datetime]:
    """
    Extract the expiration time from a JWT token.
    
    Args:
        token: The JWT token to examine
        
    Returns:
        datetime or None: The expiration time if token is valid, None otherwise
        
    Example:
        >>> expiry = get_token_expiry(token)
        >>> if expiry and expiry < datetime.now(timezone.utc):
        ...     print("Token is expired")
    """
    payload = verify_token(token)
    if not payload:
        return None
    
    exp_timestamp = payload.get("exp")
    if not exp_timestamp:
        return None
    
    try:
        return datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
    except (ValueError, OSError):
        return None


def is_token_expired(token: str) -> bool:
    """
    Check if a JWT token is expired.
    
    Args:
        token: The JWT token to check
        
    Returns:
        bool: True if token is expired or invalid, False if still valid
        
    Example:
        >>> if is_token_expired(token):
        ...     return {"error": "Token expired"}
    """
    expiry = get_token_expiry(token)
    if not expiry:
        return True  # Invalid token is considered expired
    
    return expiry <= datetime.now(timezone.utc)


# ============================================================================
# SECURITY UTILITIES
# ============================================================================

def generate_secure_token(length: int = 32) -> str:
    """
    Generate a cryptographically secure random token.
    
    Args:
        length: The length of the token in bytes (default: 32)
        
    Returns:
        str: A URL-safe random token
        
    Example:
        >>> csrf_token = generate_secure_token()
        >>> # Returns something like: "k8hN2mL9pQ7wR5tY3xV6zA2bC4dE1fG9"
    """
    return secrets.token_urlsafe(length)


def generate_state_token() -> str:
    """
    Generate a state token for OAuth CSRF protection.
    
    Returns:
        str: A secure random state token
        
    Example:
        >>> state = generate_state_token()
        >>> # Use in OAuth flow for CSRF protection
    """
    return generate_secure_token(24)


def constant_time_compare(a: str, b: str) -> bool:
    """
    Compare two strings in constant time to prevent timing attacks.
    
    Args:
        a: First string to compare
        b: Second string to compare
        
    Returns:
        bool: True if strings are equal, False otherwise
        
    Example:
        >>> is_equal = constant_time_compare(provided_token, expected_token)
    """
    if not isinstance(a, str) or not isinstance(b, str):
        return False
    
    return secrets.compare_digest(a, b)


def validate_password_strength(password: str) -> Dict[str, Union[bool, str]]:
    """
    Validate password strength according to security requirements.
    
    Args:
        password: The password to validate
        
    Returns:
        dict: Validation result with 'valid' boolean and 'message' string
        
    Example:
        >>> result = validate_password_strength("weak")
        >>> # Returns: {"valid": False, "message": "Password too short"}
        >>> 
        >>> result = validate_password_strength("Strong123!")
        >>> # Returns: {"valid": True, "message": "Password meets requirements"}
    """
    if not password:
        return {"valid": False, "message": "Password is required"}
    
    if len(password) < MIN_PASSWORD_LENGTH:
        return {
            "valid": False, 
            "message": f"Password must be at least {MIN_PASSWORD_LENGTH} characters long"
        }
    
    if len(password) > MAX_PASSWORD_LENGTH:
        return {
            "valid": False, 
            "message": f"Password cannot exceed {MAX_PASSWORD_LENGTH} characters"
        }
    
    # Check for at least one letter
    if not any(c.isalpha() for c in password):
        return {"valid": False, "message": "Password must contain at least one letter"}
    
    # Check for at least one digit
    if not any(c.isdigit() for c in password):
        return {"valid": False, "message": "Password must contain at least one number"}
    
    # Check for common weak patterns
    weak_patterns = ['password', '12345', 'qwerty', 'admin', 'letmein']
    password_lower = password.lower()
    for pattern in weak_patterns:
        if pattern in password_lower:
            return {"valid": False, "message": "Password contains common weak patterns"}
    
    return {"valid": True, "message": "Password meets security requirements"}


# ============================================================================
# TOKEN EXTRACTION UTILITIES
# ============================================================================

def extract_token_from_header(authorization_header: Optional[str]) -> Optional[str]:
    """
    Extract JWT token from Authorization header.
    
    Args:
        authorization_header: The Authorization header value ("Bearer <token>")
        
    Returns:
        str or None: The extracted token if valid format, None otherwise
        
    Example:
        >>> token = extract_token_from_header("Bearer eyJhbGciOiJIUzI1NiIs...")
        >>> # Returns: "eyJhbGciOiJIUzI1NiIs..."
    """
    if not authorization_header:
        return None
    
    # Expected format: "Bearer <token>"
    parts = authorization_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    
    return parts[1]


def get_current_user_id(token: str) -> Optional[str]:
    """
    Extract user ID from a valid JWT token.
    
    Args:
        token: The JWT token to extract user ID from
        
    Returns:
        str or None: The user ID if token is valid, None otherwise
        
    Example:
        >>> user_id = get_current_user_id(token)
        >>> if user_id:
        ...     user = get_user_by_id(user_id)
    """
    payload = verify_token(token)
    if not payload:
        return None
    
    return payload.get("sub")  # "sub" is the standard JWT subject claim


def get_token_claims(token: str) -> Dict[str, Any]:
    """
    Get all claims from a JWT token safely.
    
    Args:
        token: The JWT token to extract claims from
        
    Returns:
        dict: The token claims if valid, empty dict if invalid
        
    Example:
        >>> claims = get_token_claims(token)
        >>> user_id = claims.get("sub")
        >>> email = claims.get("email")
        >>> auth_method = claims.get("auth_method")
    """
    payload = verify_token(token)
    return payload if payload else {}


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Password utilities
    "hash_password",
    "verify_password", 
    "needs_rehash",
    "validate_password_strength",
    
    # JWT utilities
    "create_access_token",
    "create_user_token",
    "decode_token",
    "verify_token",
    "get_token_expiry",
    "is_token_expired",
    
    # Security utilities
    "generate_secure_token",
    "generate_state_token",
    "constant_time_compare",
    
    # Token extraction utilities
    "extract_token_from_header",
    "get_current_user_id",
    "get_token_claims",
    
    # Constants
    "JWT_ALGORITHM",
    "JWT_SECRET_KEY", 
    "JWT_EXPIRE_MINUTES",
    "TOKEN_TYPE",
    "MIN_PASSWORD_LENGTH",
    "MAX_PASSWORD_LENGTH",
]