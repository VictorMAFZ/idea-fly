"""
Unit tests for Google OAuth Service.

Tests the Google OAuth authentication service including:
- Token validation
- User creation/lookup
- Error handling
- Retry logic
- Security measures
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from sqlalchemy.orm import Session

import httpx
from pydantic import ValidationException

from src.auth.oauth_service import GoogleOAuthService, GoogleUserInfo
from src.auth.models import User, OAuthProfile, AuthProvider, OAuthProviderType
from src.core.exceptions import AuthenticationException, ValidationException
from src.auth.schemas import Token


@pytest.fixture
def mock_db():
    """Mock database session."""
    return Mock(spec=Session)


@pytest.fixture
def mock_user_repository():
    """Mock user repository."""
    repository = Mock()
    repository.authenticate_oauth_user = AsyncMock()
    repository.create_oauth_user = AsyncMock()
    return repository


@pytest.fixture
def mock_user():
    """Mock user instance."""
    return User(
        id=1,
        email="test@example.com",
        name="Test User",
        is_active=True,
        auth_provider=AuthProvider.GOOGLE,
        created_at=datetime.now()
    )


@pytest.fixture
def google_user_info():
    """Sample Google user info."""
    return GoogleUserInfo(
        id="google123",
        email="test@example.com",
        verified_email=True,
        name="Test User",
        given_name="Test",
        family_name="User",
        picture="https://example.com/photo.jpg",
        locale="en"
    )


@pytest.fixture
def oauth_service(mock_db):
    """OAuth service instance with mocked dependencies."""
    service = GoogleOAuthService(mock_db)
    return service


class TestGoogleOAuthService:
    """Test suite for Google OAuth Service."""

    def test_init(self, mock_db):
        """Test service initialization."""
        service = GoogleOAuthService(mock_db)
        
        assert service.db == mock_db
        assert service.user_repository is not None
        assert service.http_client is not None
        assert service.GOOGLE_USER_INFO_URL == "https://www.googleapis.com/oauth2/v2/userinfo"
        assert service.GOOGLE_TOKEN_INFO_URL == "https://oauth2.googleapis.com/tokeninfo"

    @pytest.mark.asyncio
    async def test_authenticate_with_google_success(
        self, 
        oauth_service, 
        mock_db, 
        mock_user, 
        google_user_info
    ):
        """Test successful Google OAuth authentication."""
        # Mock dependencies
        oauth_service.user_repository = mock_user_repository()
        oauth_service.user_repository.authenticate_oauth_user.return_value = mock_user
        
        # Mock token validation
        with patch.object(oauth_service, '_validate_google_token', return_value=google_user_info):
            with patch.object(oauth_service, '_find_or_create_oauth_user', return_value=mock_user):
                with patch('src.auth.oauth_service.create_access_token', return_value="jwt_token"):
                    
                    result = await oauth_service.authenticate_with_google("valid_token", mock_db)
                    
                    # Verify result structure
                    assert isinstance(result, Token)
                    assert result.access_token == "jwt_token"
                    assert result.token_type == "bearer"
                    assert result.user.email == mock_user.email
                    assert result.user.name == mock_user.name

    @pytest.mark.asyncio
    async def test_authenticate_with_google_invalid_token(self, oauth_service, mock_db):
        """Test authentication with invalid Google token."""
        # Mock token validation to raise AuthenticationException
        with patch.object(oauth_service, '_validate_google_token', side_effect=AuthenticationException("Invalid token")):
            
            with pytest.raises(AuthenticationException, match="Invalid token"):
                await oauth_service.authenticate_with_google("invalid_token", mock_db)

    @pytest.mark.asyncio
    async def test_authenticate_with_google_server_error(self, oauth_service, mock_db, google_user_info):
        """Test authentication with server error during processing."""
        # Mock token validation success but user processing failure
        with patch.object(oauth_service, '_validate_google_token', return_value=google_user_info):
            with patch.object(oauth_service, '_find_or_create_oauth_user', side_effect=Exception("Database error")):
                
                with pytest.raises(AuthenticationException, match="Authentication failed due to server error"):
                    await oauth_service.authenticate_with_google("valid_token", mock_db)

    @pytest.mark.asyncio
    async def test_validate_google_token_success(self, oauth_service):
        """Test successful Google token validation."""
        token_info_response = Mock()
        token_info_response.status_code = 200
        token_info_response.json.return_value = {
            "scope": "email profile openid"
        }
        
        user_info_response = Mock()
        user_info_response.status_code = 200
        user_info_response.json.return_value = {
            "id": "google123",
            "email": "test@example.com",
            "verified_email": True,
            "name": "Test User",
            "given_name": "Test",
            "family_name": "User"
        }
        user_info_response.raise_for_status = Mock()
        
        # Mock HTTP client responses
        oauth_service.http_client.get = AsyncMock(side_effect=[token_info_response, user_info_response])
        
        result = await oauth_service._validate_google_token("valid_token")
        
        assert isinstance(result, GoogleUserInfo)
        assert result.email == "test@example.com"
        assert result.verified_email is True
        assert result.name == "Test User"

    @pytest.mark.asyncio
    async def test_validate_google_token_invalid_token(self, oauth_service):
        """Test token validation with invalid token."""
        # Mock 401 response from token info endpoint
        token_info_response = Mock()
        token_info_response.status_code = 401
        
        oauth_service.http_client.get = AsyncMock(return_value=token_info_response)
        
        with pytest.raises(AuthenticationException, match="Invalid Google token"):
            await oauth_service._validate_google_token("invalid_token")

    @pytest.mark.asyncio
    async def test_validate_google_token_unverified_email(self, oauth_service):
        """Test token validation with unverified email."""
        token_info_response = Mock()
        token_info_response.status_code = 200
        token_info_response.json.return_value = {
            "scope": "email profile openid"
        }
        
        user_info_response = Mock()
        user_info_response.status_code = 200
        user_info_response.json.return_value = {
            "id": "google123",
            "email": "test@example.com",
            "verified_email": False,  # Email not verified
            "name": "Test User"
        }
        user_info_response.raise_for_status = Mock()
        
        oauth_service.http_client.get = AsyncMock(side_effect=[token_info_response, user_info_response])
        
        with pytest.raises(AuthenticationException, match="Google account email must be verified"):
            await oauth_service._validate_google_token("valid_token")

    @pytest.mark.asyncio
    async def test_validate_google_token_retry_logic(self, oauth_service):
        """Test retry logic on server errors."""
        # Mock server error responses that should trigger retry
        error_response = Mock()
        error_response.status_code = 500
        
        success_response = Mock()
        success_response.status_code = 200
        success_response.json.return_value = {
            "scope": "email profile openid"
        }
        
        user_info_response = Mock()
        user_info_response.status_code = 200
        user_info_response.json.return_value = {
            "id": "google123",
            "email": "test@example.com",
            "verified_email": True,
            "name": "Test User"
        }
        user_info_response.raise_for_status = Mock()
        
        # First call fails with 500, second succeeds
        oauth_service.http_client.get = AsyncMock(side_effect=[
            httpx.HTTPStatusError("Server error", request=Mock(), response=error_response),
            success_response,
            user_info_response
        ])
        
        with patch('asyncio.sleep', return_value=None):  # Speed up test
            result = await oauth_service._validate_google_token("valid_token")
            
            assert isinstance(result, GoogleUserInfo)
            assert result.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_validate_google_token_max_retries_exceeded(self, oauth_service):
        """Test failure after exceeding maximum retries."""
        error_response = Mock()
        error_response.status_code = 500
        
        # Mock all attempts failing with server error
        oauth_service.http_client.get = AsyncMock(
            side_effect=httpx.HTTPStatusError("Server error", request=Mock(), response=error_response)
        )
        
        with patch('asyncio.sleep', return_value=None):  # Speed up test
            with pytest.raises(AuthenticationException, match="Failed to validate Google token"):
                await oauth_service._validate_google_token("valid_token")

    @pytest.mark.asyncio
    async def test_verify_token_info_success(self, oauth_service):
        """Test successful token info verification."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {
            "scope": "email profile openid",
            "aud": "client_id",
            "exp": "1234567890"
        }
        
        oauth_service.http_client.get = AsyncMock(return_value=response)
        
        # Should not raise any exception
        await oauth_service._verify_token_info("valid_token")

    @pytest.mark.asyncio
    async def test_verify_token_info_insufficient_scope(self, oauth_service):
        """Test token verification with insufficient scope."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {
            "scope": "openid",  # Missing email and profile scopes
            "aud": "client_id",
            "exp": "1234567890"
        }
        
        oauth_service.http_client.get = AsyncMock(return_value=response)
        
        with pytest.raises(AuthenticationException, match="Insufficient permissions from Google"):
            await oauth_service._verify_token_info("valid_token")

    @pytest.mark.asyncio
    async def test_verify_token_info_invalid_response(self, oauth_service):
        """Test token verification with invalid response."""
        response = Mock()
        response.status_code = 400
        
        oauth_service.http_client.get = AsyncMock(return_value=response)
        
        with pytest.raises(AuthenticationException, match="Invalid Google token"):
            await oauth_service._verify_token_info("invalid_token")

    @pytest.mark.asyncio
    async def test_find_or_create_oauth_user_existing_user(
        self, 
        oauth_service, 
        google_user_info, 
        mock_user
    ):
        """Test finding existing OAuth user."""
        oauth_service.user_repository = mock_user_repository()
        oauth_service.user_repository.authenticate_oauth_user.return_value = mock_user
        
        result = await oauth_service._find_or_create_oauth_user(google_user_info)
        
        assert result == mock_user
        oauth_service.user_repository.authenticate_oauth_user.assert_called_once_with(
            email=google_user_info.email,
            oauth_provider_id=google_user_info.id,
            oauth_provider_type="google"
        )

    @pytest.mark.asyncio
    async def test_find_or_create_oauth_user_new_user(
        self, 
        oauth_service, 
        google_user_info, 
        mock_user
    ):
        """Test creating new OAuth user."""
        oauth_service.user_repository = mock_user_repository()
        oauth_service.user_repository.authenticate_oauth_user.return_value = None  # No existing user
        oauth_service.user_repository.create_oauth_user.return_value = mock_user
        
        result = await oauth_service._find_or_create_oauth_user(google_user_info)
        
        assert result == mock_user
        oauth_service.user_repository.create_oauth_user.assert_called_once_with(
            email=google_user_info.email,
            name=google_user_info.name,
            oauth_provider_id=google_user_info.id,
            oauth_provider_type="google",
            auth_provider=AuthProvider.GOOGLE
        )

    @pytest.mark.asyncio
    async def test_find_or_create_oauth_user_repository_error(
        self, 
        oauth_service, 
        google_user_info
    ):
        """Test handling repository errors during user processing."""
        oauth_service.user_repository = mock_user_repository()
        oauth_service.user_repository.authenticate_oauth_user.side_effect = Exception("Database error")
        
        with pytest.raises(ValidationException, match="Failed to process user information"):
            await oauth_service._find_or_create_oauth_user(google_user_info)

    @pytest.mark.asyncio
    async def test_close_cleanup(self, oauth_service):
        """Test proper cleanup of HTTP client."""
        oauth_service.http_client.aclose = AsyncMock()
        
        await oauth_service.close()
        
        oauth_service.http_client.aclose.assert_called_once()

    def test_google_user_info_validation(self):
        """Test GoogleUserInfo model validation."""
        # Valid data
        valid_data = {
            "id": "google123",
            "email": "test@example.com",
            "verified_email": True,
            "name": "Test User"
        }
        
        user_info = GoogleUserInfo(**valid_data)
        assert user_info.id == "google123"
        assert user_info.email == "test@example.com"
        assert user_info.verified_email is True
        assert user_info.name == "Test User"
        
        # Invalid email should raise ValidationException
        invalid_data = {
            "id": "google123",
            "email": "invalid-email",  # Invalid email format
            "verified_email": True,
            "name": "Test User"
        }
        
        with pytest.raises(ValidationException):
            GoogleUserInfo(**invalid_data)

    @pytest.mark.asyncio
    async def test_network_error_handling(self, oauth_service):
        """Test handling of network errors."""
        # Mock network error
        oauth_service.http_client.get = AsyncMock(
            side_effect=httpx.RequestError("Connection failed")
        )
        
        with patch('asyncio.sleep', return_value=None):  # Speed up test
            with pytest.raises(AuthenticationException, match="Unable to connect to Google services"):
                await oauth_service._validate_google_token("valid_token")

    @pytest.mark.asyncio
    async def test_http_client_configuration(self, mock_db):
        """Test HTTP client is properly configured."""
        service = GoogleOAuthService(mock_db)
        
        # Check timeout configuration
        assert service.http_client.timeout.read == 30.0
        
        # Check connection limits
        assert service.http_client.limits.max_keepalive_connections == 5
        assert service.http_client.limits.max_connections == 10


# Integration-style tests that verify end-to-end behavior
class TestGoogleOAuthServiceIntegration:
    """Integration tests for OAuth service with mocked external dependencies."""

    @pytest.mark.asyncio
    async def test_full_oauth_flow_new_user(self, oauth_service, mock_db):
        """Test complete OAuth flow for new user creation."""
        # Mock successful Google API responses
        token_info_response = Mock()
        token_info_response.status_code = 200
        token_info_response.json.return_value = {"scope": "email profile openid"}
        
        user_info_response = Mock()
        user_info_response.status_code = 200
        user_info_response.json.return_value = {
            "id": "google123",
            "email": "newuser@example.com",
            "verified_email": True,
            "name": "New User"
        }
        user_info_response.raise_for_status = Mock()
        
        oauth_service.http_client.get = AsyncMock(side_effect=[token_info_response, user_info_response])
        
        # Mock repository methods
        oauth_service.user_repository = mock_user_repository()
        oauth_service.user_repository.authenticate_oauth_user.return_value = None  # No existing user
        
        new_user = User(
            id=2,
            email="newuser@example.com",
            name="New User",
            is_active=True,
            auth_provider=AuthProvider.GOOGLE,
            created_at=datetime.now()
        )
        oauth_service.user_repository.create_oauth_user.return_value = new_user
        
        with patch('src.auth.oauth_service.create_access_token', return_value="new_jwt_token"):
            
            result = await oauth_service.authenticate_with_google("google_token", mock_db)
            
            assert isinstance(result, Token)
            assert result.access_token == "new_jwt_token"
            assert result.user.email == "newuser@example.com"
            assert result.user.name == "New User"

    @pytest.mark.asyncio
    async def test_full_oauth_flow_existing_user(self, oauth_service, mock_db):
        """Test complete OAuth flow for existing user login."""
        # Mock successful Google API responses
        token_info_response = Mock()
        token_info_response.status_code = 200
        token_info_response.json.return_value = {"scope": "email profile openid"}
        
        user_info_response = Mock()
        user_info_response.status_code = 200
        user_info_response.json.return_value = {
            "id": "google456",
            "email": "existing@example.com",
            "verified_email": True,
            "name": "Existing User"
        }
        user_info_response.raise_for_status = Mock()
        
        oauth_service.http_client.get = AsyncMock(side_effect=[token_info_response, user_info_response])
        
        # Mock repository methods - existing user found
        oauth_service.user_repository = mock_user_repository()
        
        existing_user = User(
            id=1,
            email="existing@example.com",
            name="Existing User",
            is_active=True,
            auth_provider=AuthProvider.MIXED,
            created_at=datetime.now()
        )
        oauth_service.user_repository.authenticate_oauth_user.return_value = existing_user
        
        with patch('src.auth.oauth_service.create_access_token', return_value="existing_jwt_token"):
            
            result = await oauth_service.authenticate_with_google("google_token", mock_db)
            
            assert isinstance(result, Token)
            assert result.access_token == "existing_jwt_token"
            assert result.user.email == "existing@example.com"
            
            # Verify create_oauth_user was not called for existing user
            oauth_service.user_repository.create_oauth_user.assert_not_called()
