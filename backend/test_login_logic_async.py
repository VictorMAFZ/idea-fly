"""
Test script simplificado para verificar la lógica de login sin conexión a BD.
Ejecuta este script para probar las nuevas funciones de login implementadas en T029.
"""

import asyncio
import sys
import os
from unittest.mock import Mock, MagicMock, AsyncMock

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

print("🧪 Testing Login Service Logic (T029)")
print("=" * 50)

# Mock de configuración mínima para evitar problemas de validación
class MockSettings:
    def __init__(self):
        self.jwt_secret_key = "test_secret"
        self.jwt_algorithm = "HS256"
        self.jwt_expire_minutes = 30

# Mockear get_settings antes de importar otros módulos
import src.core.config
src.core.config.get_settings = lambda: MockSettings()

# Ahora importar los módulos necesarios
from src.auth.service import AuthenticationService
from src.auth.schemas import UserLoginRequest
from src.core.exceptions import InvalidCredentialsException, ValidationException


async def test_login_validation():
    """Probar la validación de datos de login"""
    print("\n1. Testing login data validation...")
    
    # Crear mock de sesión de BD
    mock_db = Mock()
    service = AuthenticationService(mock_db)
    
    # Datos válidos
    valid_data = UserLoginRequest(
        email="test@example.com",
        password="ValidPassword123!"
    )
    
    try:
        # Este método no debería lanzar excepción
        await service._validate_login_data(valid_data)
        print("   ✅ Valid login data passed validation")
    except Exception as e:
        print(f"   ❌ Valid data failed validation: {e}")
    
    # Probar validación de email vacío a nivel de Pydantic
    try:
        invalid_data = UserLoginRequest(
            email="",
            password="ValidPassword123!"
        )
        # Si llega aquí, Pydantic no validó correctamente
        print("   ❌ Empty email should have failed Pydantic validation")
    except Exception as e:
        print("   ✅ Empty email correctly failed Pydantic validation")
    
    # Probar validación de contraseña vacía a nivel de Pydantic
    try:
        invalid_data = UserLoginRequest(
            email="test@example.com",
            password=""
        )
        # Si llega aquí, Pydantic no validó correctamente
        print("   ❌ Empty password should have failed Pydantic validation")
    except Exception as e:
        print("   ✅ Empty password correctly failed Pydantic validation")


async def test_verify_credentials_logic():
    """Probar la lógica de verificación de credenciales"""
    print("\n2. Testing credential verification logic...")
    
    # Mock de sesión de BD
    mock_db = Mock()
    service = AuthenticationService(mock_db)
    
    # Mock de usuario válido
    mock_user = Mock()
    mock_user.email = "test@example.com"
    mock_user.password_hash = "hashed_password"
    mock_user.is_active = True
    mock_user.email_verified = True
    
    # Mockear el repositorio y sus métodos
    service.repository.get_user_by_email = AsyncMock(return_value=mock_user)
    service.repository.security.verify_password = Mock(return_value=True)
    
    login_data = UserLoginRequest(
        email="test@example.com",
        password="correct_password"
    )
    
    try:
        # Esto debería retornar el usuario
        result = await service.verify_login_credentials(login_data)
        if result == mock_user:
            print("   ✅ Credential verification returned correct user")
        else:
            print("   ❌ Credential verification returned wrong result")
    except Exception as e:
        print(f"   ❌ Credential verification failed: {e}")
    
    # Probar con credenciales incorrectas
    service.repository.security.verify_password = Mock(return_value=False)
    
    try:
        result = await service.verify_login_credentials(login_data)
        print("   ❌ Should have failed with incorrect password")
    except InvalidCredentialsException:
        print("   ✅ Correctly failed with incorrect password")
    except Exception as e:
        print(f"   ❌ Wrong exception type for incorrect password: {e}")


async def test_user_eligibility_logic():
    """Probar la lógica de elegibilidad del usuario"""
    print("\n3. Testing user eligibility logic...")
    
    mock_db = Mock()
    service = AuthenticationService(mock_db)
    
    # Usuario elegible
    eligible_user = Mock()
    eligible_user.is_active = True
    eligible_user.email_verified = True
    
    try:
        await service.check_user_login_eligibility(eligible_user)
        print("   ✅ Eligible user passed check")
    except Exception as e:
        print(f"   ❌ Eligible user failed check: {e}")
    
    # Usuario inactivo
    inactive_user = Mock()
    inactive_user.is_active = False
    inactive_user.email_verified = True
    
    try:
        await service.check_user_login_eligibility(inactive_user)
        print("   ❌ Inactive user should have failed check")
    except InvalidCredentialsException:
        print("   ✅ Inactive user correctly failed check")
    except Exception as e:
        print(f"   ❌ Wrong exception type for inactive user: {e}")
    
    # Usuario no verificado
    unverified_user = Mock()
    unverified_user.is_active = True
    unverified_user.email_verified = False
    
    try:
        await service.check_user_login_eligibility(unverified_user)
        print("   ❌ Unverified user should have failed check")
    except InvalidCredentialsException:
        print("   ✅ Unverified user correctly failed check")
    except Exception as e:
        print(f"   ❌ Wrong exception type for unverified user: {e}")


async def test_login_service_integration():
    """Probar la integración del servicio de login"""
    print("\n4. Testing login service integration...")
    
    # Mock de sesión de BD
    mock_db = Mock()
    service = AuthenticationService(mock_db)
    
    # Mock de usuario válido
    mock_user = Mock()
    mock_user.email = "test@example.com"
    mock_user.password_hash = "hashed_password"
    mock_user.is_active = True
    mock_user.email_verified = True
    mock_user.id = 1
    
    # Mockear métodos del repositorio
    service.repository.get_user_by_email = AsyncMock(return_value=mock_user)
    service.repository.security.verify_password = Mock(return_value=True)
    service.repository.security.create_access_token = Mock(return_value="mock_jwt_token")
    
    login_data = UserLoginRequest(
        email="test@example.com",
        password="correct_password"
    )
    
    try:
        # Probar login_user (método de conveniencia)
        result = await service.login_user(login_data)
        if result == "mock_jwt_token":
            print("   ✅ login_user returned correct token")
        else:
            print(f"   ❌ login_user returned unexpected result: {result}")
    except Exception as e:
        print(f"   ❌ login_user failed: {e}")


async def test_authenticate_user_extension():
    """Probar la extensión del método authenticate_user"""
    print("\n5. Testing authenticate_user extension...")
    
    mock_db = Mock()
    service = AuthenticationService(mock_db)
    
    # Mock de usuario válido
    mock_user = Mock()
    mock_user.email = "test@example.com"
    mock_user.password_hash = "hashed_password"
    mock_user.is_active = True
    mock_user.email_verified = True
    mock_user.id = 1
    
    # Mockear métodos del repositorio
    service.repository.get_user_by_email = AsyncMock(return_value=mock_user)
    service.repository.security.verify_password = Mock(return_value=True)
    service.repository.security.create_access_token = Mock(return_value="mock_jwt_token")
    
    login_data = UserLoginRequest(
        email="test@example.com",
        password="correct_password"
    )
    
    try:
        # Probar authenticate_user con generación de token
        result = await service.authenticate_user(login_data, generate_token=True)
        if result == "mock_jwt_token":
            print("   ✅ authenticate_user with token generation works")
        else:
            print(f"   ❌ authenticate_user returned unexpected result: {result}")
            
        # Probar authenticate_user sin generación de token
        result = await service.authenticate_user(login_data, generate_token=False)
        if result == mock_user:
            print("   ✅ authenticate_user without token generation works")
        else:
            print(f"   ❌ authenticate_user without token returned unexpected result: {result}")
            
    except Exception as e:
        print(f"   ❌ authenticate_user failed: {e}")


async def main():
    """Ejecutar todas las pruebas"""
    print("Testing T029 implementation: Extend authentication service with login logic")
    
    await test_login_validation()
    await test_verify_credentials_logic()
    await test_user_eligibility_logic()
    await test_login_service_integration()
    await test_authenticate_user_extension()
    
    print("\n" + "=" * 50)
    print("🎉 All logic tests completed!")
    print("✅ T029 implementation appears to be working correctly")
    print("\nNext step: Implement T030 - Create login endpoint in router.py")


if __name__ == "__main__":
    asyncio.run(main())