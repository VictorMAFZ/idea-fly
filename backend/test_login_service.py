"""
Test script para verificar la funcionalidad de login del servicio de autenticación.
Ejecuta este script para probar las nuevas funciones de login implementadas en T029.
"""

import asyncio
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno para prueba
load_dotenv('.env.test')

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.auth.service import AuthenticationService, create_auth_service
from src.auth.schemas import UserLoginRequest
from src.core.database import get_session_factory
from src.core.exceptions import InvalidCredentialsException, ValidationException


async def test_login_functionality():
    """Test the new login functionality."""
    print("🧪 Testing Login Functionality (T029)")
    print("=" * 50)
    
    # Create database session
    session_factory = get_session_factory()
    db = session_factory()
    
    try:
        # Create service instance
        service = create_auth_service(db)
        
        # Test 1: Valid login data validation
        print("\n1️⃣ Testing login data validation...")
        try:
            login_data = UserLoginRequest(
                email="test@example.com",
                password="validPassword123"
            )
            await service._validate_login_data(login_data)
            print("   ✅ Valid login data validation passed")
        except Exception as e:
            print(f"   ❌ Valid login data validation failed: {e}")
        
        # Test 2: Invalid login data validation
        print("\n2️⃣ Testing invalid login data validation...")
        try:
            invalid_login_data = UserLoginRequest(
                email="",  # Empty email
                password="validPassword123"
            )
            await service._validate_login_data(invalid_login_data)
            print("   ❌ Should have failed validation")
        except ValidationException as e:
            print("   ✅ Invalid login data correctly rejected")
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
        
        # Test 3: Login eligibility check for non-existent user
        print("\n3️⃣ Testing login eligibility check...")
        eligibility = await service.check_user_login_eligibility("nonexistent@example.com")
        print(f"   📋 Eligibility result: {eligibility['eligible']}")
        print(f"   📋 Reason: {eligibility['reason']}")
        print(f"   📋 Message: {eligibility['message']}")
        
        # Test 4: Credential verification for non-existent user
        print("\n4️⃣ Testing credential verification...")
        is_valid = await service.verify_login_credentials("nonexistent@example.com", "password")
        print(f"   📋 Credentials valid: {is_valid}")
        
        # Test 5: Login method with UserLoginRequest
        print("\n5️⃣ Testing authenticate_user method...")
        try:
            login_data = UserLoginRequest(
                email="nonexistent@example.com",
                password="testPassword123"
            )
            user, token = await service.authenticate_user(login_data)
            print(f"   ❌ Should have failed authentication")
        except InvalidCredentialsException as e:
            print("   ✅ Authentication correctly failed for invalid credentials")
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
        
        # Test 6: Login method with separate parameters
        print("\n6️⃣ Testing login_user method...")
        try:
            user, token = await service.login_user("nonexistent@example.com", "testPassword123")
            print(f"   ❌ Should have failed authentication")
        except InvalidCredentialsException as e:
            print("   ✅ Login correctly failed for invalid credentials")
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
        
        print("\n🎉 All login functionality tests completed!")
        print("📝 Note: To test with real users, create an account first using the registration endpoint.")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    # Run the test
    asyncio.run(test_login_functionality())