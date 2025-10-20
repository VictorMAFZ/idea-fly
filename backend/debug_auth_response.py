import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

class MockSettings:
    jwt_secret_key = 'test'
    jwt_algorithm = 'HS256' 
    jwt_expire_minutes = 30
    environment = 'development'

import src.core.config
src.core.config.get_settings = lambda: MockSettings()

from src.auth.schemas import UserResponse, Token, AuthResponse
from uuid import uuid4
from datetime import datetime, timezone

try:
    user = UserResponse(
        id=uuid4(),
        email="test@example.com",
        name="Test User",
        is_active=True,
        auth_provider="email",
        created_at=datetime.now(timezone.utc)
    )
    print('✅ UserResponse created successfully')

    token = Token(
        access_token="test_token",
        expires_in=86400
    )
    print('✅ Token created successfully')
    
    auth_resp = AuthResponse(user=user, token=token)
    print('✅ AuthResponse created successfully')
    print(f'AuthResponse: {auth_resp}')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()