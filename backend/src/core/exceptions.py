"""
Centralized exception handling for IdeaFly Authentication System.

This module provides custom exception classes, error codes, and utilities
for consistent error handling across the authentication API.
"""

import logging
from typing import Optional, Dict, Any, List, Union
from enum import Enum

from fastapi import HTTPException, status
from pydantic import BaseModel, Field

# Configure logging
logger = logging.getLogger(__name__)


# ============================================================================
# ERROR CODES ENUMERATION
# ============================================================================

class ErrorCode(str, Enum):
    """
    Standardized error codes for the authentication system.
    
    These codes provide consistent, programmatic error identification
    that frontend applications can handle appropriately.
    """
    # Authentication Errors (401)
    UNAUTHORIZED = "UNAUTHORIZED"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    INVALID_TOKEN = "INVALID_TOKEN"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_REVOKED = "TOKEN_REVOKED"
    
    # Authorization Errors (403)
    FORBIDDEN = "FORBIDDEN"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    ACCOUNT_DISABLED = "ACCOUNT_DISABLED"
    EMAIL_NOT_VERIFIED = "EMAIL_NOT_VERIFIED"
    
    # Validation Errors (400, 422)
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    INVALID_EMAIL_FORMAT = "INVALID_EMAIL_FORMAT"
    PASSWORD_TOO_WEAK = "PASSWORD_TOO_WEAK"
    
    # Business Logic Errors (409, 400)
    EMAIL_EXISTS = "EMAIL_EXISTS"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    DUPLICATE_RESOURCE = "DUPLICATE_RESOURCE"
    INVALID_OPERATION = "INVALID_OPERATION"
    
    # OAuth Errors (400, 401)
    OAUTH_ERROR = "OAUTH_ERROR"
    OAUTH_STATE_MISMATCH = "OAUTH_STATE_MISMATCH"
    OAUTH_CODE_INVALID = "OAUTH_CODE_INVALID"
    OAUTH_PROVIDER_ERROR = "OAUTH_PROVIDER_ERROR"
    
    # Rate Limiting (429)
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    TOO_MANY_ATTEMPTS = "TOO_MANY_ATTEMPTS"
    
    # Server Errors (500+)
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    
    # Network and Infrastructure (503, 504)
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"


# ============================================================================
# ERROR DETAILS MODELS
# ============================================================================

class FieldError(BaseModel):
    """Represents a validation error for a specific field."""
    field: str = Field(..., description="Name of the field with error")
    message: str = Field(..., description="Error message for the field")
    code: str = Field(..., description="Specific error code for the field")
    value: Optional[Any] = Field(None, description="The invalid value provided")


class ErrorDetails(BaseModel):
    """Additional error details for complex errors."""
    field_errors: Optional[List[FieldError]] = Field(None, description="Field-specific validation errors")
    suggestion: Optional[str] = Field(None, description="Suggested action to resolve the error")
    documentation_url: Optional[str] = Field(None, description="Link to relevant documentation")
    trace_id: Optional[str] = Field(None, description="Request trace ID for debugging")
    retry_after: Optional[int] = Field(None, description="Seconds to wait before retrying (for rate limits)")


class ApiErrorResponse(BaseModel):
    """Standard API error response format."""
    success: bool = Field(False, description="Always false for error responses")
    error: "ErrorInfo" = Field(..., description="Error information")
    data: Optional[Any] = Field(None, description="Always null for error responses")


class ErrorInfo(BaseModel):
    """Error information structure."""
    error_code: str = Field(..., description="Programmatic error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[ErrorDetails] = Field(None, description="Additional error details")


# ============================================================================
# BASE EXCEPTION CLASSES
# ============================================================================

class BaseAPIException(HTTPException):
    """
    Base exception class for all API exceptions.
    
    Provides consistent error response formatting and logging.
    """
    
    def __init__(
        self,
        status_code: int,
        error_code: ErrorCode,
        message: str,
        details: Optional[ErrorDetails] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        self.error_code = error_code
        self.error_message = message
        self.error_details = details
        
        # Create consistent error response
        error_response = {
            "success": False,
            "error": {
                "error_code": error_code.value,
                "message": message,
                "details": details.dict() if details else None
            },
            "data": None
        }
        
        super().__init__(
            status_code=status_code,
            detail=error_response,
            headers=headers
        )
        
        # Log the error for monitoring
        logger.warning(
            f"API Exception: {error_code.value} - {message}",
            extra={
                "error_code": error_code.value,
                "status_code": status_code,
                "details": details.dict() if details else None
            }
        )


# ============================================================================
# AUTHENTICATION EXCEPTIONS
# ============================================================================

class AuthenticationException(BaseAPIException):
    """Base class for authentication-related errors (401)."""
    
    def __init__(
        self,
        error_code: ErrorCode = ErrorCode.UNAUTHORIZED,
        message: str = "Authentication required",
        details: Optional[ErrorDetails] = None
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code=error_code,
            message=message,
            details=details,
            headers={"WWW-Authenticate": "Bearer"}
        )


class InvalidCredentialsException(AuthenticationException):
    """Exception for invalid login credentials."""
    
    def __init__(self, message: str = "Email or password is incorrect"):
        super().__init__(
            error_code=ErrorCode.INVALID_CREDENTIALS,
            message=message,
            details=ErrorDetails(
                suggestion="Please check your email and password and try again"
            )
        )


class InvalidTokenException(AuthenticationException):
    """Exception for invalid or malformed JWT tokens."""
    
    def __init__(self, message: str = "Invalid authentication token"):
        super().__init__(
            error_code=ErrorCode.INVALID_TOKEN,
            message=message,
            details=ErrorDetails(
                suggestion="Please login again to get a new token"
            )
        )


class TokenExpiredException(AuthenticationException):
    """Exception for expired JWT tokens."""
    
    def __init__(self, message: str = "Authentication token has expired"):
        super().__init__(
            error_code=ErrorCode.TOKEN_EXPIRED,
            message=message,
            details=ErrorDetails(
                suggestion="Please login again to refresh your session"
            )
        )


# ============================================================================
# AUTHORIZATION EXCEPTIONS
# ============================================================================

class AuthorizationException(BaseAPIException):
    """Base class for authorization-related errors (403)."""
    
    def __init__(
        self,
        error_code: ErrorCode = ErrorCode.FORBIDDEN,
        message: str = "Access denied",
        details: Optional[ErrorDetails] = None
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code=error_code,
            message=message,
            details=details
        )


class AccountDisabledException(AuthorizationException):
    """Exception for disabled user accounts."""
    
    def __init__(self, message: str = "User account is disabled"):
        super().__init__(
            error_code=ErrorCode.ACCOUNT_DISABLED,
            message=message,
            details=ErrorDetails(
                suggestion="Please contact support to reactivate your account"
            )
        )


class InsufficientPermissionsException(AuthorizationException):
    """Exception for insufficient permissions."""
    
    def __init__(self, message: str = "Insufficient permissions for this operation"):
        super().__init__(
            error_code=ErrorCode.INSUFFICIENT_PERMISSIONS,
            message=message,
            details=ErrorDetails(
                suggestion="Contact your administrator for required permissions"
            )
        )


# ============================================================================
# VALIDATION EXCEPTIONS
# ============================================================================

class ValidationException(BaseAPIException):
    """Base class for validation-related errors (400, 422)."""
    
    def __init__(
        self,
        message: str = "Validation failed",
        field_errors: Optional[List[FieldError]] = None,
        status_code: int = status.HTTP_400_BAD_REQUEST
    ):
        details = ErrorDetails(field_errors=field_errors) if field_errors else None
        
        super().__init__(
            status_code=status_code,
            error_code=ErrorCode.VALIDATION_ERROR,
            message=message,
            details=details
        )


class InvalidEmailException(ValidationException):
    """Exception for invalid email format."""
    
    def __init__(self, email: str):
        field_error = FieldError(
            field="email",
            message="Invalid email format",
            code="INVALID_FORMAT",
            value=email
        )
        
        super().__init__(
            message="Email format is invalid",
            field_errors=[field_error]
        )


class WeakPasswordException(ValidationException):
    """Exception for passwords that don't meet security requirements."""
    
    def __init__(self, requirements: List[str]):
        field_error = FieldError(
            field="password",
            message="Password does not meet security requirements",
            code="WEAK_PASSWORD",
            value="[REDACTED]"
        )
        
        super().__init__(
            message="Password is too weak",
            field_errors=[field_error],
            status_code=status.HTTP_400_BAD_REQUEST
        )
        
        # Override details to include requirements
        self.error_details = ErrorDetails(
            field_errors=[field_error],
            suggestion=f"Password must meet the following requirements: {', '.join(requirements)}"
        )


# ============================================================================
# BUSINESS LOGIC EXCEPTIONS
# ============================================================================

class BusinessLogicException(BaseAPIException):
    """Base class for business logic errors."""
    
    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        details: Optional[ErrorDetails] = None,
        status_code: int = status.HTTP_400_BAD_REQUEST
    ):
        super().__init__(
            status_code=status_code,
            error_code=error_code,
            message=message,
            details=details
        )


class EmailExistsException(BusinessLogicException):
    """Exception for attempting to register with an existing email."""
    
    def __init__(self, email: str):
        super().__init__(
            error_code=ErrorCode.EMAIL_EXISTS,
            message="An account with this email already exists",
            details=ErrorDetails(
                suggestion="Try logging in instead, or use a different email address"
            ),
            status_code=status.HTTP_409_CONFLICT
        )


class UserNotFoundException(BusinessLogicException):
    """Exception for operations on non-existent users."""
    
    def __init__(self, identifier: str):
        super().__init__(
            error_code=ErrorCode.USER_NOT_FOUND,
            message="User not found",
            details=ErrorDetails(
                suggestion="Please check the user identifier and try again"
            ),
            status_code=status.HTTP_404_NOT_FOUND
        )


# ============================================================================
# OAUTH EXCEPTIONS
# ============================================================================

class OAuthException(BaseAPIException):
    """Base class for OAuth-related errors."""
    
    def __init__(
        self,
        error_code: ErrorCode = ErrorCode.OAUTH_ERROR,
        message: str = "OAuth authentication failed",
        details: Optional[ErrorDetails] = None,
        status_code: int = status.HTTP_400_BAD_REQUEST
    ):
        super().__init__(
            status_code=status_code,
            error_code=error_code,
            message=message,
            details=details
        )


class OAuthStateException(OAuthException):
    """Exception for OAuth state parameter mismatch."""
    
    def __init__(self):
        super().__init__(
            error_code=ErrorCode.OAUTH_STATE_MISMATCH,
            message="OAuth state parameter mismatch",
            details=ErrorDetails(
                suggestion="Please restart the OAuth flow for security reasons"
            ),
            status_code=status.HTTP_400_BAD_REQUEST
        )


class OAuthCodeException(OAuthException):
    """Exception for invalid OAuth authorization codes."""
    
    def __init__(self, provider: str):
        super().__init__(
            error_code=ErrorCode.OAUTH_CODE_INVALID,
            message=f"Invalid authorization code from {provider}",
            details=ErrorDetails(
                suggestion="Please restart the OAuth authentication process"
            ),
            status_code=status.HTTP_400_BAD_REQUEST
        )


# ============================================================================
# RATE LIMITING EXCEPTIONS
# ============================================================================

class RateLimitException(BaseAPIException):
    """Exception for rate limiting violations."""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: int = 60
    ):
        details = ErrorDetails(
            retry_after=retry_after,
            suggestion=f"Please wait {retry_after} seconds before trying again"
        )
        
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
            message=message,
            details=details,
            headers={"Retry-After": str(retry_after)}
        )


# ============================================================================
# SERVER ERROR EXCEPTIONS
# ============================================================================

class ServerException(BaseAPIException):
    """Base class for server-side errors (5xx)."""
    
    def __init__(
        self,
        error_code: ErrorCode = ErrorCode.INTERNAL_SERVER_ERROR,
        message: str = "Internal server error",
        details: Optional[ErrorDetails] = None,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    ):
        # Log server errors as errors (not warnings)
        logger.error(
            f"Server Exception: {error_code.value} - {message}",
            extra={
                "error_code": error_code.value,
                "status_code": status_code,
                "details": details.dict() if details else None
            }
        )
        
        super().__init__(
            status_code=status_code,
            error_code=error_code,
            message=message,
            details=details
        )


class DatabaseException(ServerException):
    """Exception for database-related errors."""
    
    def __init__(self, operation: str, original_error: Optional[str] = None):
        details = ErrorDetails(
            suggestion="Please try again later or contact support if the problem persists"
        )
        
        if original_error:
            logger.error(f"Database error during {operation}: {original_error}")
        
        super().__init__(
            error_code=ErrorCode.DATABASE_ERROR,
            message=f"Database error during {operation}",
            details=details,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )


class ExternalServiceException(ServerException):
    """Exception for external service failures."""
    
    def __init__(self, service_name: str, operation: str):
        super().__init__(
            error_code=ErrorCode.EXTERNAL_SERVICE_ERROR,
            message=f"External service error: {service_name} is unavailable",
            details=ErrorDetails(
                suggestion="Please try again later"
            ),
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_validation_exception(
    field_name: str,
    field_value: Any,
    error_message: str,
    error_code: str = "INVALID_VALUE"
) -> ValidationException:
    """
    Create a validation exception for a specific field.
    
    Args:
        field_name: Name of the field with validation error
        field_value: The invalid value provided
        error_message: Human-readable error message
        error_code: Specific error code for the field
        
    Returns:
        ValidationException: Configured validation exception
        
    Example:
        ```python
        raise create_validation_exception(
            "email", "invalid-email", "Email format is invalid", "INVALID_FORMAT"
        )
        ```
    """
    field_error = FieldError(
        field=field_name,
        message=error_message,
        code=error_code,
        value=field_value
    )
    
    return ValidationException(
        message=f"Validation failed for field: {field_name}",
        field_errors=[field_error]
    )


def create_multiple_field_validation_exception(
    field_errors: List[Dict[str, Any]]
) -> ValidationException:
    """
    Create a validation exception for multiple fields.
    
    Args:
        field_errors: List of field error dictionaries
        
    Returns:
        ValidationException: Configured validation exception
        
    Example:
        ```python
        errors = [
            {"field": "email", "message": "Invalid format", "code": "INVALID_FORMAT", "value": "bad-email"},
            {"field": "password", "message": "Too short", "code": "TOO_SHORT", "value": "[REDACTED]"}
        ]
        raise create_multiple_field_validation_exception(errors)
        ```
    """
    field_error_objects = [
        FieldError(
            field=error["field"],
            message=error["message"],
            code=error["code"],
            value=error.get("value")
        )
        for error in field_errors
    ]
    
    return ValidationException(
        message="Multiple validation errors occurred",
        field_errors=field_error_objects
    )


def is_api_exception(exception: Exception) -> bool:
    """
    Check if an exception is a custom API exception.
    
    Args:
        exception: Exception to check
        
    Returns:
        bool: True if it's a custom API exception
    """
    return isinstance(exception, BaseAPIException)


def get_error_code_from_exception(exception: Exception) -> Optional[str]:
    """
    Extract error code from an exception.
    
    Args:
        exception: Exception to extract error code from
        
    Returns:
        str: Error code if available, None otherwise
    """
    if isinstance(exception, BaseAPIException):
        return exception.error_code.value
    return None


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Enums
    "ErrorCode",
    
    # Models
    "FieldError",
    "ErrorDetails",
    "ApiErrorResponse",
    "ErrorInfo",
    
    # Base Exceptions
    "BaseAPIException",
    
    # Authentication Exceptions
    "AuthenticationException",
    "InvalidCredentialsException",
    "InvalidTokenException",
    "TokenExpiredException",
    
    # Authorization Exceptions
    "AuthorizationException",
    "AccountDisabledException",
    "InsufficientPermissionsException",
    
    # Validation Exceptions
    "ValidationException",
    "InvalidEmailException",
    "WeakPasswordException",
    
    # Business Logic Exceptions
    "BusinessLogicException",
    "EmailExistsException",
    "UserNotFoundException",
    
    # OAuth Exceptions
    "OAuthException",
    "OAuthStateException",
    "OAuthCodeException",
    
    # Rate Limiting
    "RateLimitException",
    
    # Server Exceptions
    "ServerException",
    "DatabaseException",
    "ExternalServiceException",
    
    # Utilities
    "create_validation_exception",
    "create_multiple_field_validation_exception",
    "is_api_exception",
    "get_error_code_from_exception",
]