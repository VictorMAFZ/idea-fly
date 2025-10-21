"""
Integration tests for Google OAuth Flow.

Tests the complete OAuth authentication flow from endpoint to database:
- OAuth endpoint integration
- Database transactions
- Error propagation
- Authentication middleware
- End-to-end OAuth scenarios
"""

import pytest
import asyncio
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from unittest.mock import patch, Mock, AsyncMock

from src.main import app
from src.core.database import get_db_session, Base
from src.auth.models import User, OAuthProfile, AuthProvider, OAuthProviderType
from src.auth.oauth_service import GoogleOAuthService
from src.auth.schemas import GoogleTokenRequest


# Test database setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_oauth.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create test database session."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def override_get_db(db_session):
    """Override database dependency."""
    def _override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db_session] = _override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client(override_get_db):
    """Test client with database override."""
    return TestClient(app)


@pytest.fixture
def existing_user(db_session):
    """Create existing user for tests."""
    user = User(
        email="existing@example.com",
        name="Existing User",
        hashed_password="hashed_password",  # Traditional user
        auth_provider=AuthProvider.EMAIL,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def existing_oauth_user(db_session):
    """Create existing OAuth user for tests."""
    user = User(
        email="oauth_user@example.com",
        name="OAuth User",
        auth_provider=AuthProvider.GOOGLE,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    # Add OAuth profile
    oauth_profile = OAuthProfile(
        user_id=user.id,
        provider_type=OAuthProviderType.GOOGLE,
        provider_user_id="google123",
        provider_email="oauth_user@example.com"
    )
    db_session.add(oauth_profile)
    db_session.commit()
    db_session.refresh(user)
    return user


class TestGoogleOAuthEndpoint:
    """Integration tests for Google OAuth endpoint."""

    @patch('src.auth.oauth_service.GoogleOAuthService.authenticate_with_google')
    def test_oauth_endpoint_success_new_user(self, mock_auth, client, db_session):
        """Test successful OAuth authentication for new user."""
        # Mock successful authentication response
        mock_token_response = {
            "access_token": "jwt_token_12345",
            "token_type": "bearer",
            "user": {
                "id": 1,
                "email": "newuser@example.com",
                "name": "New OAuth User",
                "is_active": True,
                "auth_provider": "google",
                "created_at": "2025-10-20T10:00:00"
            }
        }
        mock_auth.return_value = Mock(**mock_token_response)
        mock_auth.return_value.dict.return_value = mock_token_response
        
        # Make request to OAuth endpoint
        response = client.post(
            "/auth/google",
            json={"access_token": "google_oauth_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["access_token"] == "jwt_token_12345"
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "newuser@example.com"
        assert data["user"]["name"] == "New OAuth User"
        assert data["user"]["auth_provider"] == "google"

    @patch('src.auth.oauth_service.GoogleOAuthService.authenticate_with_google')
    def test_oauth_endpoint_success_existing_user(self, mock_auth, client, existing_oauth_user):
        """Test successful OAuth authentication for existing user."""
        # Mock authentication response for existing user
        mock_token_response = {
            "access_token": "jwt_existing_token",
            "token_type": "bearer",
            "user": {
                "id": existing_oauth_user.id,
                "email": existing_oauth_user.email,
                "name": existing_oauth_user.name,
                "is_active": True,
                "auth_provider": "google",
                "created_at": existing_oauth_user.created_at.isoformat()
            }
        }
        mock_auth.return_value = Mock(**mock_token_response)
        mock_auth.return_value.dict.return_value = mock_token_response
        
        response = client.post(
            "/auth/google",
            json={"access_token": "google_oauth_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["access_token"] == "jwt_existing_token"
        assert data["user"]["email"] == existing_oauth_user.email

    @patch('src.auth.oauth_service.GoogleOAuthService.authenticate_with_google')
    def test_oauth_endpoint_invalid_token(self, mock_auth, client):
        """Test OAuth endpoint with invalid Google token."""
        from src.core.exceptions import AuthenticationException
        
        # Mock authentication failure
        mock_auth.side_effect = AuthenticationException("Invalid Google token")
        
        response = client.post(
            "/auth/google",
            json={"access_token": "invalid_token"}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "Invalid Google token" in data["detail"]

    def test_oauth_endpoint_missing_token(self, client):
        """Test OAuth endpoint with missing token."""
        response = client.post(
            "/auth/google",
            json={}  # Missing access_token
        )
        
        assert response.status_code == 422  # Validation error

    def test_oauth_endpoint_invalid_request_format(self, client):
        """Test OAuth endpoint with invalid request format."""
        response = client.post(
            "/auth/google",
            json={"wrong_field": "token"}
        )
        
        assert response.status_code == 422  # Validation error

    @patch('src.auth.oauth_service.GoogleOAuthService.authenticate_with_google')
    def test_oauth_endpoint_server_error(self, mock_auth, client):
        """Test OAuth endpoint handling server errors."""
        # Mock unexpected server error
        mock_auth.side_effect = Exception("Database connection failed")
        
        response = client.post(
            "/auth/google",
            json={"access_token": "valid_token"}
        )
        
        assert response.status_code == 500

    @patch('src.auth.oauth_service.GoogleOAuthService.authenticate_with_google')
    def test_oauth_endpoint_validation_error(self, mock_auth, client):
        """Test OAuth endpoint with validation errors."""
        from pydantic import ValidationException
        
        # Mock validation error during user processing
        mock_auth.side_effect = ValidationException(["Invalid user data"], GoogleTokenRequest)
        
        response = client.post(
            "/auth/google",
            json={"access_token": "valid_token"}
        )
        
        assert response.status_code == 400


class TestOAuthFlowDatabaseIntegration:
    """Integration tests with real database operations."""

    def test_create_new_oauth_user_flow(self, client, db_session):
        """Test creating new OAuth user in database."""
        with patch('httpx.AsyncClient.get') as mock_get:
            # Mock Google API responses
            token_info_response = Mock()
            token_info_response.status_code = 200
            token_info_response.json.return_value = {"scope": "email profile openid"}
            
            user_info_response = Mock()
            user_info_response.status_code = 200
            user_info_response.json.return_value = {
                "id": "google_new_123",
                "email": "integration_new@example.com",
                "verified_email": True,
                "name": "Integration New User",
                "given_name": "Integration",
                "family_name": "User"
            }
            user_info_response.raise_for_status = Mock()
            
            mock_get.return_value = AsyncMock(
                side_effect=[token_info_response, user_info_response]
            )
            
            with patch('src.core.security.create_access_token', return_value="test_jwt_token"):
                response = client.post(
                    "/auth/google",
                    json={"access_token": "google_token_new"}
                )
                
                assert response.status_code == 200
                data = response.json()
                
                # Verify response structure
                assert data["access_token"] == "test_jwt_token"
                assert data["token_type"] == "bearer"
                assert data["user"]["email"] == "integration_new@example.com"
                assert data["user"]["name"] == "Integration New User"
                
                # Verify user was created in database
                created_user = db_session.query(User).filter(
                    User.email == "integration_new@example.com"
                ).first()
                
                assert created_user is not None
                assert created_user.name == "Integration New User"
                assert created_user.auth_provider == AuthProvider.GOOGLE
                assert created_user.is_active is True
                assert created_user.hashed_password is None  # OAuth-only user
                
                # Verify OAuth profile was created
                oauth_profile = db_session.query(OAuthProfile).filter(
                    OAuthProfile.user_id == created_user.id
                ).first()
                
                assert oauth_profile is not None
                assert oauth_profile.provider_type == OAuthProviderType.GOOGLE
                assert oauth_profile.provider_user_id == "google_new_123"
                assert oauth_profile.provider_email == "integration_new@example.com"

    def test_authenticate_existing_oauth_user_flow(self, client, existing_oauth_user, db_session):
        """Test authenticating existing OAuth user."""
        with patch('httpx.AsyncClient.get') as mock_get:
            # Mock Google API responses
            token_info_response = Mock()
            token_info_response.status_code = 200
            token_info_response.json.return_value = {"scope": "email profile openid"}
            
            user_info_response = Mock()
            user_info_response.status_code = 200
            user_info_response.json.return_value = {
                "id": "google123",  # Matches existing OAuth profile
                "email": "oauth_user@example.com",
                "verified_email": True,
                "name": "OAuth User",
            }
            user_info_response.raise_for_status = Mock()
            
            mock_get.return_value = AsyncMock(
                side_effect=[token_info_response, user_info_response]
            )
            
            with patch('src.core.security.create_access_token', return_value="existing_jwt_token"):
                response = client.post(
                    "/auth/google",
                    json={"access_token": "google_token_existing"}
                )
                
                assert response.status_code == 200
                data = response.json()
                
                # Verify response
                assert data["access_token"] == "existing_jwt_token"
                assert data["user"]["email"] == existing_oauth_user.email
                assert data["user"]["id"] == existing_oauth_user.id
                
                # Verify no new user was created
                user_count = db_session.query(User).filter(
                    User.email == existing_oauth_user.email
                ).count()
                assert user_count == 1  # Still only one user

    def test_link_existing_email_user_with_oauth(self, client, existing_user, db_session):
        """Test linking existing email user with OAuth."""
        with patch('httpx.AsyncClient.get') as mock_get:
            # Mock Google API responses for existing email user
            token_info_response = Mock()
            token_info_response.status_code = 200
            token_info_response.json.return_value = {"scope": "email profile openid"}
            
            user_info_response = Mock()
            user_info_response.status_code = 200
            user_info_response.json.return_value = {
                "id": "google_link_456",
                "email": existing_user.email,  # Same email as existing user
                "verified_email": True,
                "name": existing_user.name,
            }
            user_info_response.raise_for_status = Mock()
            
            mock_get.return_value = AsyncMock(
                side_effect=[token_info_response, user_info_response]
            )
            
            with patch('src.core.security.create_access_token', return_value="linked_jwt_token"):
                response = client.post(
                    "/auth/google",
                    json={"access_token": "google_token_link"}
                )
                
                assert response.status_code == 200
                data = response.json()
                
                # Verify response
                assert data["access_token"] == "linked_jwt_token"
                assert data["user"]["email"] == existing_user.email
                
                # Verify user provider was updated to MIXED
                db_session.refresh(existing_user)
                assert existing_user.auth_provider == AuthProvider.MIXED
                
                # Verify OAuth profile was created
                oauth_profile = db_session.query(OAuthProfile).filter(
                    OAuthProfile.user_id == existing_user.id
                ).first()
                
                assert oauth_profile is not None
                assert oauth_profile.provider_type == OAuthProviderType.GOOGLE
                assert oauth_profile.provider_user_id == "google_link_456"

    def test_oauth_flow_with_google_api_failure(self, client, db_session):
        """Test OAuth flow when Google API fails."""
        with patch('httpx.AsyncClient.get') as mock_get:
            # Mock Google API failure
            error_response = Mock()
            error_response.status_code = 401
            
            mock_get.return_value = AsyncMock(return_value=error_response)
            
            response = client.post(
                "/auth/google",
                json={"access_token": "invalid_google_token"}
            )
            
            assert response.status_code == 401
            
            # Verify no user was created in database
            user_count = db_session.query(User).count()
            initial_count = 0  # Assuming clean database
            assert user_count == initial_count

    def test_oauth_flow_with_unverified_email(self, client, db_session):
        """Test OAuth flow rejection for unverified email."""
        with patch('httpx.AsyncClient.get') as mock_get:
            # Mock Google API responses with unverified email
            token_info_response = Mock()
            token_info_response.status_code = 200
            token_info_response.json.return_value = {"scope": "email profile openid"}
            
            user_info_response = Mock()
            user_info_response.status_code = 200
            user_info_response.json.return_value = {
                "id": "google_unverified_789",
                "email": "unverified@example.com",
                "verified_email": False,  # Email not verified
                "name": "Unverified User",
            }
            user_info_response.raise_for_status = Mock()
            
            mock_get.return_value = AsyncMock(
                side_effect=[token_info_response, user_info_response]
            )
            
            response = client.post(
                "/auth/google",
                json={"access_token": "google_token_unverified"}
            )
            
            assert response.status_code == 401
            data = response.json()
            assert "email must be verified" in data["detail"]
            
            # Verify no user was created
            user = db_session.query(User).filter(
                User.email == "unverified@example.com"
            ).first()
            assert user is None


class TestOAuthServiceDependencyIntegration:
    """Integration tests for OAuth service dependency injection."""

    def test_oauth_service_dependency_injection(self, client, db_session):
        """Test that OAuth service is properly injected."""
        with patch('src.auth.oauth_service.GoogleOAuthService') as MockOAuthService:
            # Setup mock service
            mock_service_instance = Mock()
            mock_service_instance.authenticate_with_google = AsyncMock()
            
            mock_token_response = Mock()
            mock_token_response.dict.return_value = {
                "access_token": "dependency_jwt",
                "token_type": "bearer",
                "user": {
                    "id": 1,
                    "email": "dependency@example.com",
                    "name": "Dependency Test",
                    "is_active": True,
                    "auth_provider": "google",
                    "created_at": "2025-10-20T10:00:00"
                }
            }
            mock_service_instance.authenticate_with_google.return_value = mock_token_response
            
            MockOAuthService.return_value = mock_service_instance
            
            # Mock the dependency function
            with patch('src.auth.router.get_google_oauth_service', return_value=mock_service_instance):
                response = client.post(
                    "/auth/google",
                    json={"access_token": "dependency_test_token"}
                )
                
                assert response.status_code == 200
                
                # Verify service was called with correct parameters
                mock_service_instance.authenticate_with_google.assert_called_once()
                call_args = mock_service_instance.authenticate_with_google.call_args
                assert call_args[0][0] == "dependency_test_token"  # access_token
                assert call_args[0][1] == db_session  # db session


class TestOAuthErrorPropagation:
    """Integration tests for error handling across the OAuth flow."""

    @patch('src.auth.oauth_service.GoogleOAuthService.authenticate_with_google')
    def test_authentication_error_propagation(self, mock_auth, client):
        """Test that AuthenticationException is properly propagated."""
        from src.core.exceptions import AuthenticationException
        
        mock_auth.side_effect = AuthenticationException("Token validation failed")
        
        response = client.post(
            "/auth/google",
            json={"access_token": "failing_token"}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "Token validation failed" in data["detail"]

    @patch('src.auth.oauth_service.GoogleOAuthService.authenticate_with_google')
    def test_validation_error_propagation(self, mock_auth, client):
        """Test that ValidationException is properly propagated."""
        from pydantic import ValidationException
        
        mock_auth.side_effect = ValidationException(["Invalid user data"], GoogleTokenRequest)
        
        response = client.post(
            "/auth/google",
            json={"access_token": "validation_failing_token"}
        )
        
        assert response.status_code == 400

    @patch('src.auth.oauth_service.GoogleOAuthService.authenticate_with_google')
    def test_unexpected_error_handling(self, mock_auth, client):
        """Test handling of unexpected errors."""
        mock_auth.side_effect = Exception("Unexpected database error")
        
        response = client.post(
            "/auth/google",
            json={"access_token": "unexpected_error_token"}
        )
        
        assert response.status_code == 500


class TestOAuthPerformanceAndConcurrency:
    """Integration tests for OAuth performance and concurrency scenarios."""

    @patch('httpx.AsyncClient.get')
    @patch('src.core.security.create_access_token')
    def test_concurrent_oauth_requests(self, mock_create_token, mock_get, client, db_session):
        """Test handling concurrent OAuth requests for the same user."""
        # Mock Google API responses
        token_info_response = Mock()
        token_info_response.status_code = 200
        token_info_response.json.return_value = {"scope": "email profile openid"}
        
        user_info_response = Mock()
        user_info_response.status_code = 200
        user_info_response.json.return_value = {
            "id": "concurrent_user_123",
            "email": "concurrent@example.com",
            "verified_email": True,
            "name": "Concurrent User"
        }
        user_info_response.raise_for_status = Mock()
        
        mock_get.return_value = AsyncMock(
            side_effect=[token_info_response, user_info_response] * 3
        )
        mock_create_token.return_value = "concurrent_jwt_token"
        
        # Simulate concurrent requests (though TestClient is synchronous)
        responses = []
        for i in range(3):
            response = client.post(
                "/auth/google",
                json={"access_token": f"concurrent_token_{i}"}
            )
            responses.append(response)
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
        
        # Verify only one user was created (no duplicates)
        user_count = db_session.query(User).filter(
            User.email == "concurrent@example.com"
        ).count()
        assert user_count == 1

    @patch('httpx.AsyncClient.get')
    def test_oauth_timeout_handling(self, mock_get, client):
        """Test OAuth flow timeout handling."""
        import httpx
        
        # Mock timeout error
        mock_get.side_effect = httpx.TimeoutException("Request timeout")
        
        response = client.post(
            "/auth/google",
            json={"access_token": "timeout_token"}
        )
        
        assert response.status_code == 401  # Should handle timeout gracefully
