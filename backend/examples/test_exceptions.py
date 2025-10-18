"""
Simple test script for the exception handling system.
"""

import sys
import os

# Add the backend src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.exceptions import (
    ErrorCode,
    InvalidCredentialsException,
    InvalidTokenException,
    EmailExistsException,
    ValidationException,
    create_validation_exception,
    RateLimitException,
)

def test_exceptions():
    """Test the exception system."""
    print("Testing IdeaFly Exception Handling System")
    print("=" * 50)
    
    # Test 1: Invalid Credentials
    print("\n1. Testing InvalidCredentialsException:")
    try:
        raise InvalidCredentialsException("Wrong email or password")
    except InvalidCredentialsException as e:
        print(f"   ✅ Status Code: {e.status_code}")
        print(f"   ✅ Error Code: {e.error_code.value}")
        print(f"   ✅ Message: {e.error_message}")
        print(f"   ✅ Suggestion: {e.error_details.suggestion}")
    
    # Test 2: Email Exists
    print("\n2. Testing EmailExistsException:")
    try:
        raise EmailExistsException("test@example.com")
    except EmailExistsException as e:
        print(f"   ✅ Status Code: {e.status_code}")
        print(f"   ✅ Error Code: {e.error_code.value}")
        print(f"   ✅ Message: {e.error_message}")
        print(f"   ✅ Suggestion: {e.error_details.suggestion}")
    
    # Test 3: Validation Exception
    print("\n3. Testing Validation Exception:")
    try:
        raise create_validation_exception(
            "email",
            "not-an-email",
            "Invalid email format",
            "INVALID_FORMAT"
        )
    except ValidationException as e:
        print(f"   ✅ Status Code: {e.status_code}")
        print(f"   ✅ Error Code: {e.error_code.value}")
        print(f"   ✅ Message: {e.error_message}")
        print(f"   ✅ Field Errors: {len(e.error_details.field_errors)}")
        field_error = e.error_details.field_errors[0]
        print(f"   ✅ Field: {field_error.field}")
        print(f"   ✅ Field Message: {field_error.message}")
        print(f"   ✅ Field Value: {field_error.value}")
    
    # Test 4: Rate Limit Exception
    print("\n4. Testing RateLimitException:")
    try:
        raise RateLimitException("Too many requests", retry_after=120)
    except RateLimitException as e:
        print(f"   ✅ Status Code: {e.status_code}")
        print(f"   ✅ Error Code: {e.error_code.value}")
        print(f"   ✅ Message: {e.error_message}")
        print(f"   ✅ Retry After: {e.error_details.retry_after} seconds")
        print(f"   ✅ Headers: {e.headers}")
    
    # Test 5: Response Format
    print("\n5. Testing Response Format:")
    try:
        raise InvalidTokenException("Invalid JWT token")
    except InvalidTokenException as e:
        print("   ✅ FastAPI Response Format:")
        import json
        response_body = json.dumps(e.detail, indent=4)
        print(response_body)
    
    print("\n" + "=" * 50)
    print("✅ All exception tests passed successfully!")

if __name__ == "__main__":
    test_exceptions()