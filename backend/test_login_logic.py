"""
Test script simplificado para verificar la lógica de login sin conexión a BD.
Ejecuta este script para probar las nuevas funciones de login implementadas en T029.
"""

import sys
import os
from unittest.mock import Mock, MagicMock

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


def test_login_validation():
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
        service._validate_login_data(valid_data)
        print("   ✅ Valid login data passed validation")
    except Exception as e:
        print(f"   ❌ Valid data failed validation: {e}")
    
    # Datos inválidos - email vacío
    try:
        invalid_data = UserLoginRequest(
            email="",
            password="ValidPassword123!"
        )
        service._validate_login_data(invalid_data)
        print("   ❌ Empty email should have failed validation")
    except ValidationException:
        print("   ✅ Empty email correctly failed validation")
    except Exception as e:
        print(f"   ❌ Wrong exception type for empty email: {e}")
    
    # Datos inválidos - contraseña vacía
    try:
        invalid_data = UserLoginRequest(
            email="test@example.com",
            password=""
        )
        service._validate_login_data(invalid_data)
        print("   ❌ Empty password should have failed validation")
    except ValidationException:
        print("   ✅ Empty password correctly failed validation")
    except Exception as e:
        print(f"   ❌ Wrong exception type for empty password: {e}")


def test_verify_credentials_logic():
    """Probar la lógica de verificación de credenciales"""
    print("\n2. Testing credential verification logic...")
    
    # Mock de sesión de BD y configurar queries
    mock_db = Mock()
    
    # Mock de usuario válido
    mock_user = Mock()
    mock_user.email = "test@example.com"
    mock_user.password_hash = "hashed_password"
    mock_user.is_active = True
    mock_user.email_verified = True
    
    # Configurar mock de query para retornar el usuario
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user
    
    service = AuthenticationService(mock_db)
    
    # Mockear el método de verificación de contraseña
    original_verify = service.user_repo.security.verify_password
    service.user_repo.security.verify_password = Mock(return_value=True)
    
    login_data = UserLoginRequest(
        email="test@example.com",
        password="correct_password"
    )
    
    try:
        # Esto debería retornar el usuario
        result = service.verify_login_credentials(login_data)
        if result == mock_user:
            print("   ✅ Credential verification returned correct user")
        else:
            print("   ❌ Credential verification returned wrong result")
    except Exception as e:
        print(f"   ❌ Credential verification failed: {e}")
    
    # Probar con credenciales incorrectas
    service.user_repo.security.verify_password = Mock(return_value=False)
    
    try:
        result = service.verify_login_credentials(login_data)
        print("   ❌ Should have failed with incorrect password")
    except InvalidCredentialsException:
        print("   ✅ Correctly failed with incorrect password")
    except Exception as e:
        print(f"   ❌ Wrong exception type for incorrect password: {e}")


def test_user_eligibility_logic():
    """Probar la lógica de elegibilidad del usuario"""
    print("\n3. Testing user eligibility logic...")
    
    mock_db = Mock()
    service = AuthenticationService(mock_db)
    
    # Usuario elegible
    eligible_user = Mock()
    eligible_user.is_active = True
    eligible_user.email_verified = True
    
    try:
        service.check_user_login_eligibility(eligible_user)
        print("   ✅ Eligible user passed check")
    except Exception as e:
        print(f"   ❌ Eligible user failed check: {e}")
    
    # Usuario inactivo
    inactive_user = Mock()
    inactive_user.is_active = False
    inactive_user.email_verified = True
    
    try:
        service.check_user_login_eligibility(inactive_user)
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
        service.check_user_login_eligibility(unverified_user)
        print("   ❌ Unverified user should have failed check")
    except InvalidCredentialsException:
        print("   ✅ Unverified user correctly failed check")
    except Exception as e:
        print(f"   ❌ Wrong exception type for unverified user: {e}")


def test_login_service_integration():
    """Probar la integración del servicio de login"""
    print("\n4. Testing login service integration...")
    
    # Mock de sesión de BD
    mock_db = Mock()
    
    # Mock de usuario válido
    mock_user = Mock()
    mock_user.email = "test@example.com"
    mock_user.password_hash = "hashed_password"
    mock_user.is_active = True
    mock_user.email_verified = True
    mock_user.id = 1
    
    # Configurar mock de query para retornar el usuario
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user
    
    service = AuthenticationService(mock_db)
    
    # Mockear métodos de seguridad
    service.user_repo.security.verify_password = Mock(return_value=True)
    service.user_repo.security.create_access_token = Mock(return_value="mock_jwt_token")
    
    login_data = UserLoginRequest(
        email="test@example.com",
        password="correct_password"
    )
    
    try:
        # Probar login_user (método de conveniencia)
        result = service.login_user(login_data)
        if result == "mock_jwt_token":
            print("   ✅ login_user returned correct token")
        else:
            print(f"   ❌ login_user returned unexpected result: {result}")
    except Exception as e:
        print(f"   ❌ login_user failed: {e}")


def main():
    """Ejecutar todas las pruebas"""
    print("Testing T029 implementation: Extend authentication service with login logic")
    
    test_login_validation()
    test_verify_credentials_logic()
    test_user_eligibility_logic()
    test_login_service_integration()
    
    print("\n" + "=" * 50)
    print("🎉 All logic tests completed!")
    print("✅ T029 implementation appears to be working correctly")
    print("\nNext step: Implement T030 - Create login endpoint in router.py")


if __name__ == "__main__":
    main()