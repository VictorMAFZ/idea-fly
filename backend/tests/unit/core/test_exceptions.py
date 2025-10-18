"""
Tests for the centralized exception handling system.

These tests verify that custom exceptions are properly formatted
and integrated with FastAPI's exception handling.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch

from backend.src.core.exceptions import (
    ErrorCode,
    FieldError,
    ErrorDetails,
    BaseAPIException,
    AuthenticationException,
    InvalidCredentialsException,
    InvalidTokenException,
    ValidationException,
    EmailExistsException,
    UserNotFoundException,
    RateLimitException,
    create_validation_exception,
    create_multiple_field_validation_exception,
    is_api_exception,
    get_error_code_from_exception,
)


class TestErrorCode:
    """Test the ErrorCode enumeration."""
    
    def test_error_codes_have_correct_values(self):
        """Test that error codes have the expected string values."""
        assert ErrorCode.UNAUTHORIZED.value == "UNAUTHORIZED"
        assert ErrorCode.INVALID_CREDENTIALS.value == "INVALID_CREDENTIALS"
        assert ErrorCode.VALIDATION_ERROR.value == "VALIDATION_ERROR"
        assert ErrorCode.EMAIL_EXISTS.value == "EMAIL_EXISTS"
        assert ErrorCode.RATE_LIMIT_EXCEEDED.value == "RATE_LIMIT_EXCEEDED"


class TestFieldError:
    """Test the FieldError model."""
    
    def test_field_error_creation(self):
        """Test creating a field error with all properties."""
        field_error = FieldError(
            field="email",
            message="Invalid email format",
            code="INVALID_FORMAT",
            value="invalid-email"
        )
        
        assert field_error.field == "email"
        assert field_error.message == "Invalid email format"
        assert field_error.code == "INVALID_FORMAT"
        assert field_error.value == "invalid-email"
    
    def test_field_error_optional_value(self):
        """Test creating a field error without value."""
        field_error = FieldError(
            field="password",
            message="Password required",
            code="REQUIRED"
        )
        
        assert field_error.field == "password"
        assert field_error.value is None


class TestErrorDetails:
    """Test the ErrorDetails model."""
    
    def test_error_details_creation(self):
        """Test creating error details with all properties."""
        field_error = FieldError(
            field="email",
            message="Invalid format",
            code="INVALID_FORMAT"
        )
        
        details = ErrorDetails(
            field_errors=[field_error],
            suggestion="Please check your email format",
            documentation_url="https://docs.example.com/email",
            trace_id="trace-123",
            retry_after=60
        )
        
        assert len(details.field_errors) == 1
        assert details.field_errors[0].field == "email"
        assert details.suggestion == "Please check your email format"
        assert details.documentation_url == "https://docs.example.com/email"
        assert details.trace_id == "trace-123"
        assert details.retry_after == 60


class TestBaseAPIException:
    """Test the base API exception class."""
    
    def test_base_exception_creation(self):
        """Test creating a base API exception."""
        exception = BaseAPIException(
            status_code=400,
            error_code=ErrorCode.VALIDATION_ERROR,
            message="Test error message"
        )
        
        assert exception.status_code == 400
        assert exception.error_code == ErrorCode.VALIDATION_ERROR
        assert exception.error_message == "Test error message"
        assert exception.detail["success"] is False
        assert exception.detail["error"]["error_code"] == "VALIDATION_ERROR"
        assert exception.detail["error"]["message"] == "Test error message"
        assert exception.detail["data"] is None
    
    def test_base_exception_with_details(self):
        """Test creating a base API exception with details."""
        details = ErrorDetails(suggestion="Try again later")
        
        exception = BaseAPIException(
            status_code=429,
            error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
            message="Rate limit exceeded",
            details=details
        )
        
        assert exception.detail["error"]["details"]["suggestion"] == "Try again later"
    
    def test_base_exception_with_headers(self):
        """Test creating a base API exception with custom headers."""
        exception = BaseAPIException(
            status_code=401,
            error_code=ErrorCode.UNAUTHORIZED,
            message="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
        assert exception.headers == {"WWW-Authenticate": "Bearer"}


class TestAuthenticationExceptions:
    """Test authentication-related exceptions."""
    
    def test_authentication_exception(self):
        """Test basic authentication exception."""
        exception = AuthenticationException()
        
        assert exception.status_code == 401
        assert exception.error_code == ErrorCode.UNAUTHORIZED
        assert exception.headers == {"WWW-Authenticate": "Bearer"}
    
    def test_invalid_credentials_exception(self):
        """Test invalid credentials exception."""
        exception = InvalidCredentialsException()
        
        assert exception.status_code == 401
        assert exception.error_code == ErrorCode.INVALID_CREDENTIALS
        assert "incorrect" in exception.error_message.lower()
        assert exception.error_details.suggestion is not None
    
    def test_invalid_token_exception(self):
        """Test invalid token exception."""
        exception = InvalidTokenException()
        
        assert exception.status_code == 401
        assert exception.error_code == ErrorCode.INVALID_TOKEN
        assert "login again" in exception.error_details.suggestion


class TestValidationExceptions:
    """Test validation-related exceptions."""
    
    def test_validation_exception_basic(self):
        """Test basic validation exception."""
        exception = ValidationException()
        
        assert exception.status_code == 400
        assert exception.error_code == ErrorCode.VALIDATION_ERROR
        assert exception.error_message == "Validation failed"
    
    def test_validation_exception_with_field_errors(self):
        """Test validation exception with field errors."""
        field_error = FieldError(
            field="email",
            message="Invalid format",
            code="INVALID_FORMAT"
        )
        
        exception = ValidationException(
            message="Email validation failed",
            field_errors=[field_error]
        )
        
        assert len(exception.error_details.field_errors) == 1
        assert exception.error_details.field_errors[0].field == "email"


class TestBusinessLogicExceptions:
    """Test business logic exceptions."""
    
    def test_email_exists_exception(self):
        """Test email exists exception."""
        exception = EmailExistsException("test@example.com")
        
        assert exception.status_code == 409
        assert exception.error_code == ErrorCode.EMAIL_EXISTS
        assert "already exists" in exception.error_message
        assert exception.error_details.suggestion is not None
    
    def test_user_not_found_exception(self):
        """Test user not found exception."""
        exception = UserNotFoundException("user123")
        
        assert exception.status_code == 404
        assert exception.error_code == ErrorCode.USER_NOT_FOUND
        assert exception.error_message == "User not found"


class TestRateLimitException:
    """Test rate limiting exception."""
    
    def test_rate_limit_exception(self):
        """Test rate limit exception with default values."""
        exception = RateLimitException()
        
        assert exception.status_code == 429
        assert exception.error_code == ErrorCode.RATE_LIMIT_EXCEEDED
        assert exception.headers["Retry-After"] == "60"
        assert exception.error_details.retry_after == 60
    
    def test_rate_limit_exception_custom_retry(self):
        """Test rate limit exception with custom retry time."""
        exception = RateLimitException(
            message="Custom rate limit message",
            retry_after=120
        )
        
        assert exception.headers["Retry-After"] == "120"
        assert exception.error_details.retry_after == 120
        assert "120 seconds" in exception.error_details.suggestion


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_create_validation_exception(self):
        """Test creating a validation exception for a single field."""
        exception = create_validation_exception(
            "email",
            "invalid-email",
            "Invalid email format",
            "INVALID_FORMAT"
        )
        
        assert isinstance(exception, ValidationException)
        assert len(exception.error_details.field_errors) == 1
        field_error = exception.error_details.field_errors[0]
        assert field_error.field == "email"
        assert field_error.value == "invalid-email"
        assert field_error.message == "Invalid email format"
        assert field_error.code == "INVALID_FORMAT"
    
    def test_create_multiple_field_validation_exception(self):
        """Test creating a validation exception for multiple fields."""
        field_errors = [
            {
                "field": "email",
                "message": "Invalid format",
                "code": "INVALID_FORMAT",
                "value": "bad-email"
            },
            {
                "field": "password",
                "message": "Too short",
                "code": "TOO_SHORT"
            }
        ]
        
        exception = create_multiple_field_validation_exception(field_errors)
        
        assert isinstance(exception, ValidationException)
        assert len(exception.error_details.field_errors) == 2
        assert exception.error_details.field_errors[0].field == "email"
        assert exception.error_details.field_errors[1].field == "password"
    
    def test_is_api_exception(self):
        """Test checking if an exception is a custom API exception."""
        api_exception = AuthenticationException()
        regular_exception = ValueError("Regular error")
        
        assert is_api_exception(api_exception) is True
        assert is_api_exception(regular_exception) is False
    
    def test_get_error_code_from_exception(self):
        """Test extracting error code from exceptions."""
        api_exception = InvalidCredentialsException()
        regular_exception = ValueError("Regular error")
        
        assert get_error_code_from_exception(api_exception) == "INVALID_CREDENTIALS"
        assert get_error_code_from_exception(regular_exception) is None


class TestExceptionIntegration:
    """Test exception integration with FastAPI."""
    
    def test_exception_response_format(self):
        """Test that exceptions follow the expected response format."""
        exception = EmailExistsException("test@example.com")
        
        response_data = exception.detail
        
        # Verify response structure
        assert "success" in response_data
        assert "error" in response_data
        assert "data" in response_data
        
        assert response_data["success"] is False
        assert response_data["data"] is None
        
        # Verify error structure
        error = response_data["error"]
        assert "error_code" in error
        assert "message" in error
        assert "details" in error
        
        assert error["error_code"] == "EMAIL_EXISTS"
        assert isinstance(error["message"], str)
    
    @patch('backend.src.core.exceptions.logger')
    def test_exception_logging(self, mock_logger):
        """Test that exceptions are properly logged."""
        AuthenticationException("Test authentication error")
        
        # Verify that the logger was called
        mock_logger.warning.assert_called_once()
        
        # Check the log message
        call_args = mock_logger.warning.call_args
        assert "UNAUTHORIZED" in call_args[0][0]
        assert "Test authentication error" in call_args[0][0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])