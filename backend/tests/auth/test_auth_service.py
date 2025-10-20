"""
Unit tests for authentication service in IdeaFly Authentication System.

This module tests the AuthenticationService class, focusing on user registration
functionality including validation, error handling, and business logic.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timezone
from uuid import uuid4, UUID

from sqlalchemy.orm import Session

from src.auth.service import AuthenticationService
from src.auth.schemas import (
    UserRegistrationRequest, 
    UserResponse, 
    Token, 
    TokenType,
    AuthProvider as SchemaAuthProvider
)
from src.auth.models import User, AuthProvider
from src.core.exceptions import (
    EmailExistsException,
    ValidationException,
    DatabaseException,
    AuthenticationException
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_db_session():
    """Mock database session for testing."""
    session = Mock(spec=Session)
    return session


@pytest.fixture
def mock_user_repository():
    """Mock user repository for testing."""
    repository = Mock()
    repository.validate_registration_data = AsyncMock()
    repository.create_user = AsyncMock()
    return repository


@pytest.fixture
def auth_service(mock_db_session, mock_user_repository):
    """Authentication service instance for testing."""
    service = AuthenticationService(mock_db_session)
    # Replace the repository with our mock
    service.repository = mock_user_repository
    return service


@pytest.fixture
def sample_registration_request():
    """Sample registration request data."""
    return UserRegistrationRequest(
        name="Juan Pérez",
        email="juan.perez@example.com", 
        password="SecurePass123!"
    )


@pytest.fixture
def sample_user_model():
    """Sample user model from database."""
    user = Mock(spec=User)
    user.id = uuid4()
    user.name = "Juan Pérez"
    user.email = "juan.perez@example.com"
    user.hashed_password = "$2b$12$hashed_password_example"
    user.auth_provider = AuthProvider.EMAIL
    user.is_active = True
    user.created_at = datetime.now(timezone.utc)
    user.updated_at = datetime.now(timezone.utc)
    return user


@pytest.fixture 
def sample_token():
    """Sample JWT token."""
    return Token(
        access_token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        token_type=TokenType.BEARER,
        expires_in=3600,
        user_id=str(uuid4())
    )


@pytest.fixture
def sample_user_response():
    """Sample user response."""
    user_id = uuid4()
    return UserResponse(
        id=user_id,
        name="Juan Pérez", 
        email="juan.perez@example.com",
        auth_provider=SchemaAuthProvider.EMAIL,
        is_active=True,
        is_verified=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        last_login=None
    )


# ============================================================================
# REGISTRATION TESTS - SUCCESS CASES
# ============================================================================

class TestRegistrationSuccess:
    """Test successful user registration scenarios."""
    
    @pytest.mark.asyncio
    async def test_register_user_success(
        self, 
        auth_service,
        mock_user_repository,
        sample_registration_request,
        sample_user_model,
        sample_token,
        sample_user_response
    ):
        """Test successful user registration with valid data."""
        # Arrange
        mock_user_repository.validate_registration_data.return_value = None
        mock_user_repository.create_user.return_value = sample_user_model
        
        with patch.object(auth_service, '_validate_password_strength') as mock_validate_pwd, \
             patch.object(auth_service, '_create_token_for_user') as mock_create_token, \
             patch.object(auth_service, '_create_user_response') as mock_create_response:
            
            mock_validate_pwd.return_value = None
            mock_create_token.return_value = sample_token
            mock_create_response.return_value = sample_user_response
            
            # Act
            user_response, token = await auth_service.register_user(sample_registration_request)
            
            # Assert
            assert user_response == sample_user_response
            assert token == sample_token
            
            # Verify method calls
            mock_validate_pwd.assert_called_once_with(sample_registration_request.password)
            mock_user_repository.validate_registration_data.assert_called_once_with(sample_registration_request)
            mock_user_repository.create_user.assert_called_once_with(
                sample_registration_request, 
                auth_provider=AuthProvider.EMAIL
            )
            mock_create_token.assert_called_once_with(sample_user_model, auth_method="password")
            mock_create_response.assert_called_once_with(sample_user_model)

    @pytest.mark.asyncio
    async def test_register_user_valid_password_patterns(
        self,
        auth_service,
        mock_user_repository,
        sample_user_model,
        sample_token,
        sample_user_response
    ):
        """Test registration with various valid password patterns."""
        valid_passwords = [
            "SecurePass123!",
            "MyStr0ngP@ssw0rd",
            "C0mpl3x!P4ssw0rd",
            "Unique9Pass@",
            "Test123$Word"
        ]
        
        # Setup mocks
        mock_user_repository.validate_registration_data.return_value = None
        mock_user_repository.create_user.return_value = sample_user_model
        
        for password in valid_passwords:
            registration_request = UserRegistrationRequest(
                name="Test User",
                email="test@example.com",
                password=password
            )
            
            with patch.object(auth_service, '_validate_password_strength') as mock_validate_pwd, \
                 patch.object(auth_service, '_create_token_for_user') as mock_create_token, \
                 patch.object(auth_service, '_create_user_response') as mock_create_response:
                
                mock_validate_pwd.return_value = None
                mock_create_token.return_value = sample_token
                mock_create_response.return_value = sample_user_response
                
                # Act & Assert - should not raise exception
                user_response, token = await auth_service.register_user(registration_request)
                assert user_response == sample_user_response
                assert token == sample_token


# ============================================================================
# REGISTRATION TESTS - VALIDATION ERRORS
# ============================================================================

class TestRegistrationValidation:
    """Test registration validation and business rules."""
    
    @pytest.mark.asyncio
    async def test_register_user_email_already_exists(
        self,
        auth_service,
        mock_user_repository,
        sample_registration_request
    ):
        """Test registration fails when email already exists."""
        # Arrange
        mock_user_repository.validate_registration_data.side_effect = EmailExistsException(
            email=sample_registration_request.email
        )
        
        with patch.object(auth_service, '_validate_password_strength') as mock_validate_pwd:
            mock_validate_pwd.return_value = None
            
            # Act & Assert
            with pytest.raises(EmailExistsException) as exc_info:
                await auth_service.register_user(sample_registration_request)
                
            # Check that the correct exception type was raised
            assert exc_info.value.status_code == 409
            mock_validate_pwd.assert_called_once()
            mock_user_repository.validate_registration_data.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_user_weak_password(
        self,
        auth_service,
        mock_user_repository
    ):
        """Test registration fails with weak passwords."""
        # Use a valid request format but mock the password strength validation to fail
        registration_request = UserRegistrationRequest(
            name="Test User",
            email="test@example.com", 
            password="SecurePass123!"  # Valid format but we'll mock it to fail
        )
        
        with patch.object(auth_service, '_validate_password_strength') as mock_validate_pwd:
            mock_validate_pwd.side_effect = ValidationException(
                "Password does not meet strength requirements"
            )
            
            # Act & Assert
            with pytest.raises(ValidationException):
                await auth_service.register_user(registration_request)
                
            mock_validate_pwd.assert_called_once_with("SecurePass123!")

    @pytest.mark.asyncio
    async def test_register_user_repository_validation_error(
        self,
        auth_service,
        mock_user_repository,
        sample_registration_request
    ):
        """Test registration fails when repository validation fails."""
        # Arrange
        mock_user_repository.validate_registration_data.side_effect = ValidationException(
            "Invalid registration data"
        )
        
        with patch.object(auth_service, '_validate_password_strength') as mock_validate_pwd:
            mock_validate_pwd.return_value = None
            
            # Act & Assert
            with pytest.raises(ValidationException):
                await auth_service.register_user(sample_registration_request)


# ============================================================================
# REGISTRATION TESTS - DATABASE ERRORS
# ============================================================================

class TestRegistrationDatabaseErrors:
    """Test registration database error scenarios."""
    
    @pytest.mark.asyncio
    async def test_register_user_database_error_during_creation(
        self,
        auth_service,
        mock_user_repository,
        sample_registration_request
    ):
        """Test registration fails when database user creation fails."""
        # Arrange
        mock_user_repository.validate_registration_data.return_value = None
        mock_user_repository.create_user.side_effect = DatabaseException(
            operation="create_user",
            original_error="Connection timeout"
        )
        
        with patch.object(auth_service, '_validate_password_strength') as mock_validate_pwd:
            mock_validate_pwd.return_value = None
            
            # Act & Assert
            with pytest.raises(DatabaseException) as exc_info:
                await auth_service.register_user(sample_registration_request)
                
            # Check that the correct exception type and status code was raised
            assert exc_info.value.status_code == 503

    @pytest.mark.asyncio
    async def test_register_user_unexpected_error_becomes_database_exception(
        self,
        auth_service,
        mock_user_repository,
        sample_registration_request
    ):
        """Test that unexpected errors are wrapped as DatabaseException."""
        # Arrange
        mock_user_repository.validate_registration_data.return_value = None
        mock_user_repository.create_user.side_effect = Exception("Unexpected database error")
        
        with patch.object(auth_service, '_validate_password_strength') as mock_validate_pwd:
            mock_validate_pwd.return_value = None
            
            # Act & Assert
            with pytest.raises(DatabaseException) as exc_info:
                await auth_service.register_user(sample_registration_request)
                
            assert "user registration" in str(exc_info.value)
            assert "Unexpected database error" in str(exc_info.value)


# ============================================================================
# REGISTRATION TESTS - EDGE CASES
# ============================================================================

class TestRegistrationEdgeCases:
    """Test edge cases and boundary conditions for registration."""
    
    @pytest.mark.asyncio
    async def test_register_user_name_boundary_lengths(
        self,
        auth_service,
        mock_user_repository,
        sample_user_model,
        sample_token,
        sample_user_response
    ):
        """Test registration with boundary name lengths."""
        # Setup mocks
        mock_user_repository.validate_registration_data.return_value = None
        mock_user_repository.create_user.return_value = sample_user_model
        
        # Test minimum length (2 characters)
        short_name_request = UserRegistrationRequest(
            name="Jo",  # Minimum allowed
            email="jo@example.com",
            password="SecurePass123!"
        )
        
        # Test maximum length (100 characters) 
        long_name = "A" * 100  # Maximum allowed
        long_name_request = UserRegistrationRequest(
            name=long_name,
            email="long@example.com", 
            password="SecurePass123!"
        )
        
        test_cases = [short_name_request, long_name_request]
        
        for request in test_cases:
            with patch.object(auth_service, '_validate_password_strength') as mock_validate_pwd, \
                 patch.object(auth_service, '_create_token_for_user') as mock_create_token, \
                 patch.object(auth_service, '_create_user_response') as mock_create_response:
                
                mock_validate_pwd.return_value = None
                mock_create_token.return_value = sample_token
                mock_create_response.return_value = sample_user_response
                
                # Act & Assert - should not raise exception
                user_response, token = await auth_service.register_user(request)
                assert user_response == sample_user_response
                assert token == sample_token

    @pytest.mark.asyncio
    async def test_register_user_special_characters_in_name(
        self,
        auth_service,
        mock_user_repository,
        sample_user_model,
        sample_token,
        sample_user_response
    ):
        """Test registration with special characters in names."""
        # Setup mocks
        mock_user_repository.validate_registration_data.return_value = None
        mock_user_repository.create_user.return_value = sample_user_model
        
        special_names = [
            "José María",           # Accented characters
            "O'Connor",            # Apostrophe
            "Van der Berg",        # Multiple spaces
            "Ana-Sofia",           # Hyphen
            "María José García"    # Multiple accented chars
        ]
        
        for name in special_names:
            registration_request = UserRegistrationRequest(
                name=name,
                email="test@example.com",
                password="SecurePass123!"
            )
            
            with patch.object(auth_service, '_validate_password_strength') as mock_validate_pwd, \
                 patch.object(auth_service, '_create_token_for_user') as mock_create_token, \
                 patch.object(auth_service, '_create_user_response') as mock_create_response:
                
                mock_validate_pwd.return_value = None
                mock_create_token.return_value = sample_token
                mock_create_response.return_value = sample_user_response
                
                # Act & Assert - should not raise exception
                user_response, token = await auth_service.register_user(registration_request)
                assert user_response == sample_user_response
                assert token == sample_token


# ============================================================================
# INTEGRATION TESTS - METHOD COORDINATION
# ============================================================================

class TestRegistrationIntegration:
    """Test integration between registration service methods."""
    
    @pytest.mark.asyncio
    async def test_register_user_method_execution_order(
        self,
        auth_service,
        mock_user_repository,
        sample_registration_request,
        sample_user_model,
        sample_token,
        sample_user_response
    ):
        """Test that registration methods are called in correct order."""
        # Track method calls
        call_order = []
        
        def track_validate_password(*args, **kwargs):
            call_order.append('validate_password')
            return None
            
        def track_validate_data(*args, **kwargs):
            call_order.append('validate_data')
            return None
            
        def track_create_user(*args, **kwargs):
            call_order.append('create_user')
            return sample_user_model
            
        def track_create_token(*args, **kwargs):
            call_order.append('create_token')
            return sample_token
            
        def track_create_response(*args, **kwargs):
            call_order.append('create_response')
            return sample_user_response
        
        # Setup mocks with tracking
        mock_user_repository.validate_registration_data.side_effect = track_validate_data
        mock_user_repository.create_user.side_effect = track_create_user
        
        with patch.object(auth_service, '_validate_password_strength', side_effect=track_validate_password), \
             patch.object(auth_service, '_create_token_for_user', side_effect=track_create_token), \
             patch.object(auth_service, '_create_user_response', side_effect=track_create_response):
            
            # Act
            await auth_service.register_user(sample_registration_request)
            
            # Assert correct execution order
            expected_order = [
                'validate_password',
                'validate_data', 
                'create_user',
                'create_token',
                'create_response'
            ]
            assert call_order == expected_order

    @pytest.mark.asyncio
    async def test_register_user_creates_email_auth_provider(
        self,
        auth_service,
        mock_user_repository,
        sample_registration_request,
        sample_user_model,
        sample_token,
        sample_user_response
    ):
        """Test that registration correctly sets EMAIL auth provider."""
        # Setup mocks
        mock_user_repository.validate_registration_data.return_value = None
        mock_user_repository.create_user.return_value = sample_user_model
        
        with patch.object(auth_service, '_validate_password_strength') as mock_validate_pwd, \
             patch.object(auth_service, '_create_token_for_user') as mock_create_token, \
             patch.object(auth_service, '_create_user_response') as mock_create_response:
            
            mock_validate_pwd.return_value = None
            mock_create_token.return_value = sample_token
            mock_create_response.return_value = sample_user_response
            
            # Act
            await auth_service.register_user(sample_registration_request)
            
            # Assert that create_user was called with EMAIL provider
            mock_user_repository.create_user.assert_called_once_with(
                sample_registration_request,
                auth_provider=AuthProvider.EMAIL
            )

    @pytest.mark.asyncio 
    async def test_register_user_token_method_parameter(
        self,
        auth_service,
        mock_user_repository,
        sample_registration_request,
        sample_user_model,
        sample_token,
        sample_user_response
    ):
        """Test that token creation receives correct auth_method parameter."""
        # Setup mocks
        mock_user_repository.validate_registration_data.return_value = None
        mock_user_repository.create_user.return_value = sample_user_model
        
        with patch.object(auth_service, '_validate_password_strength') as mock_validate_pwd, \
             patch.object(auth_service, '_create_token_for_user') as mock_create_token, \
             patch.object(auth_service, '_create_user_response') as mock_create_response:
            
            mock_validate_pwd.return_value = None
            mock_create_token.return_value = sample_token
            mock_create_response.return_value = sample_user_response
            
            # Act
            await auth_service.register_user(sample_registration_request)
            
            # Assert that token creation was called with correct auth_method
            mock_create_token.assert_called_once_with(
                sample_user_model,
                auth_method="password"
            )


# ============================================================================
# ERROR LOGGING TESTS
# ============================================================================

class TestRegistrationLogging:
    """Test logging behavior during registration."""
    
    @pytest.mark.asyncio
    async def test_register_user_logs_success(
        self,
        auth_service,
        mock_user_repository,
        sample_registration_request,
        sample_user_model,
        sample_token,
        sample_user_response
    ):
        """Test that successful registration logs appropriate messages."""
        # Setup mocks
        mock_user_repository.validate_registration_data.return_value = None
        mock_user_repository.create_user.return_value = sample_user_model
        
        with patch.object(auth_service, '_validate_password_strength') as mock_validate_pwd, \
             patch.object(auth_service, '_create_token_for_user') as mock_create_token, \
             patch.object(auth_service, '_create_user_response') as mock_create_response, \
             patch('src.auth.service.logger') as mock_logger:
            
            mock_validate_pwd.return_value = None
            mock_create_token.return_value = sample_token
            mock_create_response.return_value = sample_user_response
            
            # Act
            await auth_service.register_user(sample_registration_request)
            
            # Assert logging calls
            mock_logger.info.assert_any_call(
                f"🔄 Starting user registration for: {sample_registration_request.email}"
            )
            mock_logger.info.assert_any_call(
                f"✅ User registration successful: {sample_user_model.email} (ID: {sample_user_model.id})"
            )

    @pytest.mark.asyncio
    async def test_register_user_logs_unexpected_error(
        self,
        auth_service,
        mock_user_repository,
        sample_registration_request
    ):
        """Test that unexpected errors are logged appropriately."""
        # Setup mocks
        mock_user_repository.validate_registration_data.return_value = None
        mock_user_repository.create_user.side_effect = Exception("Unexpected error")
        
        with patch.object(auth_service, '_validate_password_strength') as mock_validate_pwd, \
             patch('src.auth.service.logger') as mock_logger:
            
            mock_validate_pwd.return_value = None
            
            # Act & Assert
            with pytest.raises(DatabaseException):
                await auth_service.register_user(sample_registration_request)
                
            # Assert error logging
            mock_logger.error.assert_called_once()
            error_call_args = mock_logger.error.call_args[0][0]
            assert "❌ Unexpected error during registration" in error_call_args
            assert sample_registration_request.email in error_call_args