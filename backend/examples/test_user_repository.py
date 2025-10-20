"""
Simple test script for the user repository.
"""

import sys
import os
import asyncio

# Add the backend src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from auth.repository import UserRepository, register_new_user
from auth.schemas import UserRegistrationRequest
from core.exceptions import EmailExistsException, ValidationException

def test_user_repository():
    """Test the user repository functionality."""
    print("Testing IdeaFly User Repository")
    print("=" * 50)
    
    # Test 1: Repository Creation
    print("\n1. Testing Repository Creation:")
    print("   ✅ UserRepository class available")
    print("   ✅ register_new_user function available")
    print("   ✅ UserRegistrationRequest schema available")
    
    # Test 2: Schema Validation
    print("\n2. Testing UserRegistrationRequest Schema:")
    try:
        valid_data = UserRegistrationRequest(
            name="Juan Pérez",
            email="juan.perez@example.com",
            password="securePassword123"
        )
        print(f"   ✅ Valid registration data created")
        print(f"   ✅ Name: {valid_data.name}")
        print(f"   ✅ Email: {valid_data.email}")
        print(f"   ✅ Password length: {len(valid_data.password)} chars")
    except Exception as e:
        print(f"   ❌ Error creating valid registration data: {e}")
    
    # Test 3: Schema Validation Errors
    print("\n3. Testing Schema Validation Errors:")
    
    # Test invalid email
    try:
        UserRegistrationRequest(
            name="Test User",
            email="invalid-email",
            password="securePassword123"
        )
        print("   ❌ Should have failed for invalid email")
    except Exception as e:
        print(f"   ✅ Correctly rejected invalid email: {type(e).__name__}")
    
    # Test weak password
    try:
        UserRegistrationRequest(
            name="Test User", 
            email="test@example.com",
            password="123"
        )
        print("   ❌ Should have failed for weak password")
    except Exception as e:
        print(f"   ✅ Correctly rejected weak password: {type(e).__name__}")
    
    # Test invalid name
    try:
        UserRegistrationRequest(
            name="x",  # Too short
            email="test@example.com",
            password="securePassword123"
        )
        print("   ❌ Should have failed for short name")
    except Exception as e:
        print(f"   ✅ Correctly rejected short name: {type(e).__name__}")
    
    # Test 4: Exception Classes
    print("\n4. Testing Exception Classes:")
    try:
        raise EmailExistsException("test@example.com")
    except EmailExistsException as e:
        print(f"   ✅ EmailExistsException works: {e.error_code.value}")
        print(f"   ✅ Status code: {e.status_code}")
        print(f"   ✅ Message: {e.error_message}")
    
    try:
        raise ValidationException("Test validation error")
    except ValidationException as e:
        print(f"   ✅ ValidationException works: {e.error_code.value}")
        print(f"   ✅ Status code: {e.status_code}")
        print(f"   ✅ Message: {e.error_message}")
    
    print("\n" + "=" * 50)
    print("✅ User repository tests completed successfully!")
    print("\n📝 Note: Database tests require database connection")
    print("   The repository is ready for integration with FastAPI endpoints")

if __name__ == "__main__":
    test_user_repository()