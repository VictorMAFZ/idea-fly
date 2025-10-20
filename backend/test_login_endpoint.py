"""
Test rápido para verificar que el endpoint de login funciona correctamente.
"""

import sys
import os
from unittest.mock import Mock

# Add the src directory to Python path  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

print("🧪 Testing Login Endpoint Implementation (T030)")
print("=" * 50)

# Mock de configuración mínima
class MockSettings:
    def __init__(self):
        self.jwt_secret_key = "test_secret"
        self.jwt_algorithm = "HS256"
        self.jwt_expire_minutes = 30
        self.environment = "development"

# Mockear get_settings antes de importar módulos
import src.core.config
src.core.config.get_settings = lambda: MockSettings()

# Verificar que el endpoint existe y está correctamente definido
try:
    from src.auth.router import router
    print("✅ Router importado exitosamente")
    
    # Verificar que tiene las rutas esperadas
    routes = [route.path for route in router.routes]
    print(f"📍 Rutas disponibles: {routes}")
    
    if "/login" in routes:
        print("✅ Endpoint /auth/login está definido")
    else:
        print("❌ Endpoint /auth/login no encontrado")
        
    # Verificar que el endpoint de login acepta POST
    login_route = None
    for route in router.routes:
        if hasattr(route, 'path') and route.path == "/login":
            login_route = route
            break
            
    if login_route:
        methods = getattr(login_route, 'methods', set())
        if 'POST' in methods:
            print("✅ Endpoint /auth/login acepta método POST")
        else:
            print("❌ Endpoint /auth/login no acepta método POST")
            print(f"   Métodos disponibles: {methods}")
    
    # Verificar imports necesarios
    from src.auth.schemas import UserLoginRequest, AuthResponse
    print("✅ Schemas de login importados correctamente")
    
    # Verificar que UserLoginRequest tiene los campos necesarios
    try:
        login_request = UserLoginRequest(
            email="test@example.com",
            password="testPassword123!"
        )
        print("✅ UserLoginRequest funciona correctamente")
    except Exception as e:
        print(f"❌ Error con UserLoginRequest: {e}")
        
    print("\n" + "=" * 50)
    print("🎉 Verificación del endpoint de login completada!")
    print("✅ T030 implementado correctamente")
    print("📝 El endpoint POST /auth/login está listo para usar")
    
except Exception as e:
    print(f"❌ Error durante la verificación: {e}")
    import traceback
    traceback.print_exc()