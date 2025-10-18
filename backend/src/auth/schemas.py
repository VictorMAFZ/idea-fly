"""
Pydantic schemas for IdeaFly Authentication System.

This module defines data transfer objects (DTOs) for API requests and responses,
including validation rules and serialization formats.
"""

import re
from datetime import datetime, timezone
from typing import Optional, Any, Dict, List
from uuid import UUID

from pydantic import BaseModel, Field, validator, EmailStr
from enum import Enum


class AuthProvider(str, Enum):
    """Authentication provider options."""
    EMAIL = "email"
    GOOGLE = "google"
    MIXED = "mixed"


class TokenType(str, Enum):
    """JWT token type."""
    BEARER = "bearer"


# Request Schemas (Input DTOs)

class UserRegistrationRequest(BaseModel):
    """Schema for user registration requests (UserCreate)."""
    
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Full name of the user",
        example="Juan Pérez"
    )
    
    email: EmailStr = Field(
        ...,
        description="Valid email address for login and communication",
        example="juan.perez@example.com"
    )
    
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Strong password (min 8 characters)",
        example="securePassword123"
    )
    
    @validator('name')
    def validate_name(cls, v: str) -> str:
        """Validate name contains at least one alphabetic character."""
        if not re.search(r'[a-zA-ZñÑáéíóúÁÉÍÓÚ]', v):
            raise ValueError("Name must contain at least one letter")
        return v.strip()
    
    @validator('password')
    def validate_password_strength(cls, v: str) -> str:
        """Validate password meets security requirements."""
        # At least 8 characters
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        # At least one letter and one number
        if not re.search(r'[a-zA-Z]', v):
            raise ValueError("Password must contain at least one letter")
        if not re.search(r'\d', v):
            raise ValueError("Password must contain at least one number")
        
        # No common weak patterns
        weak_patterns = ['password', '12345', 'qwerty', 'admin', 'letmein']
        if any(pattern in v.lower() for pattern in weak_patterns):
            raise ValueError("Password cannot contain common weak patterns")
        
        return v

    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "name": "Juan Pérez",
                "email": "juan.perez@example.com",
                "password": "securePassword123"
            }
        }


class UserLoginRequest(BaseModel):
    """Schema for user login requests."""
    
    email: EmailStr = Field(
        ...,
        description="User email address",
        example="juan.perez@example.com"
    )
    
    password: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="User password",
        example="securePassword123"
    )

    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "email": "juan.perez@example.com",
                "password": "securePassword123"
            }
        }


class GoogleOAuthRequest(BaseModel):
    """Schema for Google OAuth callback requests."""
    
    code: str = Field(
        ...,
        min_length=1,
        description="Authorization code from Google OAuth flow",
        example="4/0AdQt8qh..."
    )
    
    state: Optional[str] = Field(
        None,
        description="State parameter for CSRF protection",
        example="random_state_string"
    )

    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "code": "4/0AdQt8qh...",
                "state": "random_state_string"
            }
        }


# Response Schemas (Output DTOs)

class Token(BaseModel):
    """JWT token response schema."""
    
    access_token: str = Field(
        ...,
        description="JWT access token",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    )
    
    token_type: TokenType = Field(
        default=TokenType.BEARER,
        description="Token type (always 'bearer')",
        example="bearer"
    )
    
    expires_in: int = Field(
        ...,
        gt=0,
        description="Token expiration time in seconds",
        example=86400
    )

    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 86400
            }
        }


# Alias for backward compatibility and clarity
AuthResponse = Token


class UserResponse(BaseModel):
    """Schema for user profile responses."""
    
    id: UUID = Field(
        ...,
        description="Unique user identifier",
        example="550e8400-e29b-41d4-a716-446655440000"
    )
    
    name: str = Field(
        ...,
        description="Full name of the user",
        example="Juan Pérez"
    )
    
    email: EmailStr = Field(
        ...,
        description="User email address",
        example="juan.perez@example.com"
    )
    
    auth_provider: AuthProvider = Field(
        ...,
        description="Primary authentication method",
        example=AuthProvider.EMAIL
    )
    
    is_active: bool = Field(
        ...,
        description="Whether the user account is active",
        example=True
    )
    
    created_at: datetime = Field(
        ...,
        description="Account creation timestamp",
        example="2025-10-18T10:30:00Z"
    )

    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Juan Pérez",
                "email": "juan.perez@example.com",
                "auth_provider": "email",
                "is_active": True,
                "created_at": "2025-10-18T10:30:00Z"
            }
        }


class ErrorResponse(BaseModel):
    """Schema for API error responses."""
    
    error_code: str = Field(
        ...,
        description="Specific error code for programmatic handling",
        example="INVALID_CREDENTIALS"
    )
    
    message: str = Field(
        ...,
        description="Human-readable error message",
        example="Email or password is incorrect"
    )
    
    details: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional error details (field validation errors, etc.)",
        example={"field": "email", "issue": "Invalid format"}
    )

    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "error_code": "VALIDATION_ERROR",
                "message": "Password must be at least 8 characters long",
                "details": {
                    "field": "password",
                    "constraint": "min_length"
                }
            }
        }


class ValidationErrorResponse(BaseModel):
    """Schema for Pydantic validation error responses."""
    
    error_code: str = Field(
        default="VALIDATION_ERROR",
        description="Error code for validation failures"
    )
    
    message: str = Field(
        default="Request validation failed",
        description="General validation error message"
    )
    
    details: List[Dict[str, Any]] = Field(
        ...,
        description="List of field validation errors"
    )

    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "error_code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": [
                    {
                        "field": "email",
                        "message": "field required",
                        "type": "value_error.missing"
                    },
                    {
                        "field": "password",
                        "message": "ensure this value has at least 8 characters",
                        "type": "value_error.any_str.min_length"
                    }
                ]
            }
        }


class LogoutResponse(BaseModel):
    """Schema for logout success response."""
    
    message: str = Field(
        default="Logged out successfully",
        description="Logout confirmation message"
    )

    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "message": "Logged out successfully"
            }
        }


# Internal Schemas (for service layer use)

class UserInDB(BaseModel):
    """Schema representing User model in database (with hashed_password)."""
    
    id: UUID
    name: str
    email: EmailStr
    hashed_password: Optional[str] = None  # None for OAuth-only users
    auth_provider: AuthProvider
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration."""
        orm_mode = True
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class UserCreate(BaseModel):
    """Internal schema for user creation (service layer)."""
    
    name: str
    email: EmailStr
    password: Optional[str] = None  # None for OAuth users
    auth_provider: AuthProvider = AuthProvider.EMAIL

    @validator('password')
    def validate_password_required_for_email_auth(cls, v, values):
        """Ensure password is provided for email authentication."""
        auth_provider = values.get('auth_provider', AuthProvider.EMAIL)
        
        if auth_provider in (AuthProvider.EMAIL, AuthProvider.MIXED) and not v:
            raise ValueError("Password is required for email authentication")
        
        if auth_provider == AuthProvider.GOOGLE and v:
            raise ValueError("Password should not be provided for Google OAuth")
        
        return v


class UserUpdate(BaseModel):
    """Schema for user updates."""
    
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None

    @validator('name')
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate name if provided."""
        if v is not None:
            if len(v.strip()) < 2:
                raise ValueError("Name must be at least 2 characters long")
            if not re.search(r'[a-zA-ZñÑáéíóúÁÉÍÓÚ]', v):
                raise ValueError("Name must contain at least one letter")
            return v.strip()
        return v


# JWT Token Payload Schemas

class TokenPayload(BaseModel):
    """JWT token payload schema."""
    
    user_id: UUID = Field(..., alias='sub')
    email: EmailStr
    auth_method: str  # 'password' or 'google_oauth'
    iat: datetime  # Issued at
    exp: datetime  # Expiration

    class Config:
        """Pydantic configuration."""
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: int(v.timestamp()),
            UUID: lambda v: str(v)
        }


# Export all schemas for easy importing
__all__ = [
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