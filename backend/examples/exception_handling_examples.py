"""
Example usage of the IdeaFly centralized exception handling system.

This module demonstrates how to use custom exceptions, error codes,
and error details in various scenarios throughout the application.
"""

from src.core.exceptions import (
    # Exception classes
    AuthenticationException,
    InvalidCredentialsException,
    InvalidTokenException,
    TokenExpiredException,
    AuthorizationException,
    AccountDisabledException,
    ValidationException,
    InvalidEmailException,
    WeakPasswordException,
    EmailExistsException,
    UserNotFoundException,
    OAuthException,
    OAuthStateException,
    RateLimitException,
    DatabaseException,
    
    # Utility functions
    create_validation_exception,
    create_multiple_field_validation_exception,
    
    # Models
    FieldError,
    ErrorDetails,
    ErrorCode,
)


def example_authentication_errors():
    """Examples of authentication-related exceptions."""
    print("=== Authentication Error Examples ===\n")
    
    # Basic authentication required
    try:
        raise AuthenticationException()
    except AuthenticationException as e:
        print("1. Basic Authentication Exception:")
        print(f"   Status Code: {e.status_code}")
        print(f"   Error Code: {e.error_code.value}")
        print(f"   Message: {e.error_message}")
        print(f"   Headers: {e.headers}")
        print()
    
    # Invalid credentials
    try:
        raise InvalidCredentialsException("The email or password you entered is incorrect")
    except InvalidCredentialsException as e:
        print("2. Invalid Credentials Exception:")
        print(f"   Status Code: {e.status_code}")
        print(f"   Error Code: {e.error_code.value}")
        print(f"   Message: {e.error_message}")
        print(f"   Suggestion: {e.error_details.suggestion}")
        print()
    
    # Token expired
    try:
        raise TokenExpiredException()
    except TokenExpiredException as e:
        print("3. Token Expired Exception:")
        print(f"   Status Code: {e.status_code}")
        print(f"   Error Code: {e.error_code.value}")
        print(f"   Message: {e.error_message}")
        print(f"   Suggestion: {e.error_details.suggestion}")
        print()


def example_authorization_errors():
    """Examples of authorization-related exceptions."""
    print("=== Authorization Error Examples ===\n")
    
    # Account disabled
    try:
        raise AccountDisabledException()
    except AccountDisabledException as e:
        print("1. Account Disabled Exception:")
        print(f"   Status Code: {e.status_code}")
        print(f"   Error Code: {e.error_code.value}")
        print(f"   Message: {e.error_message}")
        print(f"   Suggestion: {e.error_details.suggestion}")
        print()


def example_validation_errors():
    """Examples of validation-related exceptions."""
    print("=== Validation Error Examples ===\n")
    
    # Single field validation error
    try:
        raise create_validation_exception(
            "email",
            "not-an-email",
            "Please enter a valid email address",
            "INVALID_FORMAT"
        )
    except ValidationException as e:
        print("1. Single Field Validation Exception:")
        print(f"   Status Code: {e.status_code}")
        print(f"   Error Code: {e.error_code.value}")
        print(f"   Message: {e.error_message}")
        print(f"   Field Errors: {len(e.error_details.field_errors)}")
        for field_error in e.error_details.field_errors:
            print(f"     - Field: {field_error.field}")
            print(f"       Message: {field_error.message}")
            print(f"       Code: {field_error.code}")
            print(f"       Value: {field_error.value}")
        print()
    
    # Multiple field validation errors
    try:
        field_errors = [
            {
                "field": "email",
                "message": "Email format is invalid",
                "code": "INVALID_FORMAT",
                "value": "bad-email"
            },
            {
                "field": "password",
                "message": "Password must be at least 8 characters",
                "code": "TOO_SHORT",
                "value": "[REDACTED]"
            },
            {
                "field": "name",
                "message": "Name is required",
                "code": "REQUIRED"
            }
        ]
        
        raise create_multiple_field_validation_exception(field_errors)
    except ValidationException as e:
        print("2. Multiple Field Validation Exception:")
        print(f"   Status Code: {e.status_code}")
        print(f"   Error Code: {e.error_code.value}")
        print(f"   Message: {e.error_message}")
        print(f"   Field Errors: {len(e.error_details.field_errors)}")
        for i, field_error in enumerate(e.error_details.field_errors, 1):
            print(f"     {i}. Field: {field_error.field}")
            print(f"        Message: {field_error.message}")
            print(f"        Code: {field_error.code}")
            if field_error.value is not None:
                print(f"        Value: {field_error.value}")
        print()
    
    # Invalid email exception
    try:
        raise InvalidEmailException("not-an-email-address")
    except ValidationException as e:
        print("3. Invalid Email Exception:")
        print(f"   Status Code: {e.status_code}")
        print(f"   Error Code: {e.error_code.value}")
        print(f"   Message: {e.error_message}")
        field_error = e.error_details.field_errors[0]
        print(f"   Field: {field_error.field}")
        print(f"   Field Message: {field_error.message}")
        print(f"   Invalid Value: {field_error.value}")
        print()
    
    # Weak password exception
    try:
        requirements = [
            "At least 8 characters long",
            "Contains uppercase letter",
            "Contains lowercase letter",
            "Contains number",
            "Contains special character"
        ]
        raise WeakPasswordException(requirements)
    except ValidationException as e:
        print("4. Weak Password Exception:")
        print(f"   Status Code: {e.status_code}")
        print(f"   Error Code: {e.error_code.value}")
        print(f"   Message: {e.error_message}")
        print(f"   Suggestion: {e.error_details.suggestion}")
        print()


def example_business_logic_errors():
    """Examples of business logic exceptions."""
    print("=== Business Logic Error Examples ===\n")
    
    # Email already exists
    try:
        raise EmailExistsException("user@example.com")
    except EmailExistsException as e:
        print("1. Email Exists Exception:")
        print(f"   Status Code: {e.status_code}")
        print(f"   Error Code: {e.error_code.value}")
        print(f"   Message: {e.error_message}")
        print(f"   Suggestion: {e.error_details.suggestion}")
        print()
    
    # User not found
    try:
        raise UserNotFoundException("user-123")
    except UserNotFoundException as e:
        print("2. User Not Found Exception:")
        print(f"   Status Code: {e.status_code}")
        print(f"   Error Code: {e.error_code.value}")
        print(f"   Message: {e.error_message}")
        print(f"   Suggestion: {e.error_details.suggestion}")
        print()


def example_oauth_errors():
    """Examples of OAuth-related exceptions."""
    print("=== OAuth Error Examples ===\n")
    
    # OAuth state mismatch
    try:
        raise OAuthStateException()
    except OAuthException as e:
        print("1. OAuth State Exception:")
        print(f"   Status Code: {e.status_code}")
        print(f"   Error Code: {e.error_code.value}")
        print(f"   Message: {e.error_message}")
        print(f"   Suggestion: {e.error_details.suggestion}")
        print()


def example_rate_limiting_errors():
    """Examples of rate limiting exceptions."""
    print("=== Rate Limiting Error Examples ===\n")
    
    # Rate limit exceeded
    try:
        raise RateLimitException(
            message="Too many login attempts from this IP address",
            retry_after=300  # 5 minutes
        )
    except RateLimitException as e:
        print("1. Rate Limit Exception:")
        print(f"   Status Code: {e.status_code}")
        print(f"   Error Code: {e.error_code.value}")
        print(f"   Message: {e.error_message}")
        print(f"   Retry After: {e.error_details.retry_after} seconds")
        print(f"   Suggestion: {e.error_details.suggestion}")
        print(f"   Headers: {e.headers}")
        print()


def example_server_errors():
    """Examples of server error exceptions."""
    print("=== Server Error Examples ===\n")
    
    # Database error
    try:
        raise DatabaseException("user registration", "Connection timeout")
    except DatabaseException as e:
        print("1. Database Exception:")
        print(f"   Status Code: {e.status_code}")
        print(f"   Error Code: {e.error_code.value}")
        print(f"   Message: {e.error_message}")
        print(f"   Suggestion: {e.error_details.suggestion}")
        print()


def example_fastapi_integration():
    """Example of how exceptions integrate with FastAPI."""
    print("=== FastAPI Integration Example ===\n")
    
    # Show the JSON response format
    try:
        raise InvalidCredentialsException("Invalid email or password")
    except InvalidCredentialsException as e:
        print("FastAPI Response Format:")
        print("Status Code:", e.status_code)
        print("Response Body:")
        
        import json
        response_body = json.dumps(e.detail, indent=2)
        print(response_body)
        print()
        
        if e.headers:
            print("Response Headers:")
            for key, value in e.headers.items():
                print(f"  {key}: {value}")
        print()


def example_error_handling_patterns():
    """Examples of common error handling patterns."""
    print("=== Error Handling Patterns ===\n")
    
    # Pattern 1: Service layer exception handling
    print("1. Service Layer Pattern:")
    print("""
def create_user_account(email: str, password: str):
    try:
        # Check if email already exists
        if user_service.email_exists(email):
            raise EmailExistsException(email)
        
        # Validate email format
        if not is_valid_email(email):
            raise InvalidEmailException(email)
        
        # Validate password strength
        if not is_strong_password(password):
            requirements = get_password_requirements()
            raise WeakPasswordException(requirements)
        
        # Create the user
        return user_service.create_user(email, password)
        
    except DatabaseException as e:
        # Log the database error and re-raise
        logger.error(f"Database error creating user: {e}")
        raise
    except Exception as e:
        # Convert unexpected errors to server errors
        logger.error(f"Unexpected error creating user: {e}")
        raise DatabaseException("user creation", str(e))
    """)
    
    # Pattern 2: Route handler exception handling
    print("2. FastAPI Route Handler Pattern:")
    print("""
@router.post("/register")
async def register_user(user_data: UserRegistrationRequest):
    try:
        user = await auth_service.register_user(
            email=user_data.email,
            password=user_data.password,
            name=user_data.name
        )
        return {"success": True, "data": user, "error": None}
    
    except EmailExistsException:
        # Custom exceptions are automatically handled by FastAPI
        raise
    except ValidationException:
        # Validation exceptions are automatically handled
        raise
    except Exception as e:
        # Convert unexpected errors
        logger.error(f"Unexpected error in registration: {e}")
        raise DatabaseException("user registration", str(e))
    """)
    
    # Pattern 3: Dependency injection error handling
    print("3. Dependency Injection Pattern:")
    print("""
async def get_current_user(token: str = Depends(get_bearer_token)):
    try:
        # Validate token format
        if not token:
            raise AuthenticationException("Token required")
        
        # Verify token signature and expiration
        payload = verify_jwt_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise InvalidTokenException("Token missing user ID")
        
        # Get user from database
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundException(user_id)
        
        if not user.is_active:
            raise AccountDisabledException()
        
        return user
        
    except AuthenticationException:
        # Re-raise authentication errors
        raise
    except Exception as e:
        # Convert unexpected errors
        logger.error(f"Error in authentication: {e}")
        raise AuthenticationException("Authentication service error")
    """)


def main():
    """Run all examples."""
    print("IdeaFly Exception Handling System Examples")
    print("=" * 50)
    print()
    
    example_authentication_errors()
    example_authorization_errors()
    example_validation_errors()
    example_business_logic_errors()
    example_oauth_errors()
    example_rate_limiting_errors()
    example_server_errors()
    example_fastapi_integration()
    example_error_handling_patterns()
    
    print("=" * 50)
    print("Examples completed successfully!")


if __name__ == "__main__":
    main()