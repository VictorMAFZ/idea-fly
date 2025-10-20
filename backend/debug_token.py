import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

class MockSettings:
    jwt_secret_key = 'test'
    jwt_algorithm = 'HS256' 
    jwt_expire_minutes = 30
    environment = 'development'

import src.core.config
src.core.config.get_settings = lambda: MockSettings()

from src.auth.schemas import Token

try:
    token = Token(access_token='test_token_123', expires_in=3600)
    print('✅ Token created successfully')
    print(f'Token: {token}')
    print(f'Token dict: {token.model_dump()}')
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()