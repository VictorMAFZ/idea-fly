"""
Authentication service for IdeaFly Authentication System.

This module provides the business logic layer for user authentication,
registration, JWT token management, and OAuth integration. It orchestrates
operations between the repository layer and the API endpoints.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from ..auth.models import User, AuthProvider
from ..auth.schemas import (
    UserRegistrationRequest,
    UserLoginRequest,
    UserResponse,
    Token,
    GoogleOAuthRequest,
    AuthProvider as SchemaAuthProvider
)
from ..auth.repository import UserRepository, create_user_repository
from ..core.security import (
    create_access_token,
    verify_token,
    get_current_user_id,
    validate_password_strength
)
from ..core.config import get_settings
from ..core.exceptions import (
    InvalidCredentialsException,
    EmailExistsException,
    UserNotFoundException,
    ValidationException,
    AuthenticationException,
    TokenExpiredException,
    InvalidTokenException,
    DatabaseException,
    OAuthException,
    create_validation_exception,
)

# Configure logging
logger = logging.getLogger(__name__)

# Get application settings
settings = get_settings()


# ============================================================================
# AUTHENTICATION SERVICE CLASS
# ============================================================================

class AuthenticationService:
    """
    Service class for authentication operations.
    
    Provides high-level business logic for user registration, login,
    token management, and OAuth integration. Acts as orchestrator
    between repository layer and API endpoints.
    """

    def __init__(self, db: Session):
        """
        Initialize the authentication service.
        
        Args:
            db: Database session for repository operations
        """
        self.db = db
        self.repository = create_user_repository(db)

    # ========================================================================
    # USER REGISTRATION METHODS
    # ========================================================================

    async def register_user(
        self, 
        registration_data: UserRegistrationRequest
    ) -> Tuple[UserResponse, Token]:
        """
        Register a new user with email and password.
        
        This method orchestrates the complete user registration process:
        1. Validates registration data
        2. Checks password strength requirements
        3. Creates new user in database
        4. Generates JWT token for immediate login
        5. Returns user profile and token
        
        Args:
            registration_data: User registration information
            
        Returns:
            Tuple[UserResponse, Token]: User profile and authentication token
            
        Raises:
            EmailExistsException: If email is already registered
            ValidationException: If data validation fails
            DatabaseException: If database operation fails
            
        Example:
            ```python
            service = AuthenticationService(db)
            user_data = UserRegistrationRequest(
                name="Juan Pérez",
                email="juan@example.com",
                password="securePassword123"
            )
            user_profile, token = await service.register_user(user_data)
            ```
        """
        try:
            logger.info(f"🔄 Starting user registration for: {registration_data.email}")
            
            # Step 1: Validate password strength (additional business rules)
            await self._validate_password_strength(registration_data.password)
            
            # Step 2: Validate registration data and check email uniqueness
            await self.repository.validate_registration_data(registration_data)
            
            # Step 3: Create user in database
            user = await self.repository.create_user(
                registration_data, 
                auth_provider=AuthProvider.EMAIL
            )
            
            # Step 4: Generate authentication token
            token_data = await self._create_token_for_user(
                user, 
                auth_method="password"
            )
            
            # Step 5: Convert to response format
            user_response = await self._create_user_response(user)
            
            logger.info(f"✅ User registration successful: {user.email} (ID: {user.id})")
            
            return user_response, token_data
            
        except (EmailExistsException, ValidationException, DatabaseException):
            # Re-raise business logic and database exceptions
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error during registration for {registration_data.email}: {e}")
            raise DatabaseException("user registration", str(e))

    async def register_oauth_user(
        self,
        email: str,
        name: str,
        oauth_provider_id: str,
        oauth_provider_type: str = "google"
    ) -> Tuple[UserResponse, Token]:
        """
        Register a new user via OAuth authentication.
        
        Args:
            email: Email from OAuth provider
            name: Name from OAuth provider
            oauth_provider_id: Provider-specific user ID
            oauth_provider_type: OAuth provider type (google, facebook, etc.)
            
        Returns:
            Tuple[UserResponse, Token]: User profile and authentication token
            
        Raises:
            EmailExistsException: If email is already registered
            ValidationException: If OAuth data is invalid
            DatabaseException: If database operation fails
        """
        try:
            logger.info(f"🔄 Starting OAuth user registration for: {email} (Provider: {oauth_provider_type})")
            
            # Validate OAuth data
            await self._validate_oauth_data(email, name, oauth_provider_id)
            
            # Determine auth provider
            auth_provider = AuthProvider.GOOGLE if oauth_provider_type == "google" else AuthProvider.MIXED
            
            # Create OAuth user
            user = await self.repository.create_oauth_user(
                email=email,
                name=name,
                oauth_provider_id=oauth_provider_id,
                oauth_provider_type=oauth_provider_type,
                auth_provider=auth_provider
            )
            
            # Generate authentication token
            token_data = await self._create_token_for_user(
                user, 
                auth_method=f"{oauth_provider_type}_oauth"
            )
            
            # Convert to response format
            user_response = await self._create_user_response(user)
            
            logger.info(f"✅ OAuth user registration successful: {user.email} (Provider: {oauth_provider_type})")
            
            return user_response, token_data
            
        except (EmailExistsException, ValidationException, DatabaseException):
            # Re-raise business logic and database exceptions
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error during OAuth registration for {email}: {e}")
            raise DatabaseException("OAuth user registration", str(e))

    # ========================================================================
    # USER AUTHENTICATION METHODS
    # ========================================================================

    async def authenticate_user(
        self, 
        login_data: UserLoginRequest
    ) -> Tuple[UserResponse, Token]:
        """
        Authenticate user with email and password.
        
        Args:
            login_data: User login credentials
            
        Returns:
            Tuple[UserResponse, Token]: User profile and authentication token
            
        Raises:
            InvalidCredentialsException: If credentials are invalid
            UserNotFoundException: If user doesn't exist
            DatabaseException: If database operation fails
            
        Example:
            ```python
            service = AuthenticationService(db)
            login_data = UserLoginRequest(
                email="juan@example.com",
                password="securePassword123"
            )
            user_profile, token = await service.authenticate_user(login_data)
            ```
        """
        try:
            logger.info(f"🔄 Starting authentication for: {login_data.email}")
            
            # Authenticate user credentials
            user = await self.repository.authenticate_user(
                login_data.email, 
                login_data.password
            )
            
            if not user:
                logger.warning(f"❌ Authentication failed for: {login_data.email}")
                raise InvalidCredentialsException()
            
            # Update last login timestamp
            await self.repository.update_user_last_login(user.id)
            
            # Generate authentication token
            token_data = await self._create_token_for_user(
                user, 
                auth_method="password"
            )
            
            # Convert to response format
            user_response = await self._create_user_response(user)
            
            logger.info(f"✅ Authentication successful: {user.email}")
            
            return user_response, token_data
            
        except InvalidCredentialsException:
            # Re-raise authentication exceptions
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error during authentication for {login_data.email}: {e}")
            raise DatabaseException("user authentication", str(e))

    async def authenticate_oauth_user(
        self,
        email: str,
        oauth_provider_id: str,
        oauth_provider_type: str = "google"
    ) -> Optional[Tuple[UserResponse, Token]]:
        """
        Authenticate existing user via OAuth or return None for new registration.
        
        Args:
            email: Email from OAuth provider
            oauth_provider_id: Provider-specific user ID
            oauth_provider_type: OAuth provider type
            
        Returns:
            Optional[Tuple[UserResponse, Token]]: User and token if found, None for new registration
            
        Raises:
            DatabaseException: If database operation fails
        """
        try:
            logger.info(f"🔄 OAuth authentication attempt for: {email} (Provider: {oauth_provider_type})")
            
            # Try to authenticate existing OAuth user
            user = await self.repository.authenticate_oauth_user(
                email=email,
                oauth_provider_id=oauth_provider_id,
                oauth_provider_type=oauth_provider_type
            )
            
            if not user:
                logger.info(f"ℹ️ No existing OAuth user found for: {email}")
                return None
            
            # Update last login timestamp
            await self.repository.update_user_last_login(user.id)
            
            # Generate authentication token
            token_data = await self._create_token_for_user(
                user, 
                auth_method=f"{oauth_provider_type}_oauth"
            )
            
            # Convert to response format
            user_response = await self._create_user_response(user)
            
            logger.info(f"✅ OAuth authentication successful: {user.email}")
            
            return user_response, token_data
            
        except Exception as e:
            logger.error(f"❌ Unexpected error during OAuth authentication for {email}: {e}")
            raise DatabaseException("OAuth authentication", str(e))

    # ========================================================================
    # TOKEN MANAGEMENT METHODS
    # ========================================================================

    async def refresh_token(self, current_token: str) -> Token:
        """
        Refresh an existing JWT token.
        
        Args:
            current_token: Current JWT token to refresh
            
        Returns:
            Token: New JWT token with extended expiration
            
        Raises:
            InvalidTokenException: If token is invalid or malformed
            TokenExpiredException: If token is expired
            UserNotFoundException: If user no longer exists
            DatabaseException: If database operation fails
        """
        try:
            logger.info("🔄 Token refresh requested")
            
            # Verify current token (allows slightly expired tokens for refresh)
            token_data = verify_token(current_token)
            
            if not token_data:
                raise InvalidTokenException("Cannot decode token for refresh")
            
            # Get user ID from token
            user_id = token_data.get("sub")
            if not user_id:
                raise InvalidTokenException("Token missing user ID")
            
            # Verify user still exists and is active
            user = await self.repository.get_user_by_id(UUID(user_id))
            if not user:
                raise UserNotFoundException(user_id)
            
            if not user.is_active:
                raise AuthenticationException("User account is inactive")
            
            # Get auth method from original token
            auth_method = token_data.get("auth_method", "password")
            
            # Create new token
            new_token = await self._create_token_for_user(user, auth_method)
            
            logger.info(f"✅ Token refreshed for user: {user.email}")
            
            return new_token
            
        except (InvalidTokenException, TokenExpiredException, UserNotFoundException, AuthenticationException):
            # Re-raise authentication exceptions
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error during token refresh: {e}")
            raise DatabaseException("token refresh", str(e))

    async def validate_token(self, token: str) -> UserResponse:
        """
        Validate a JWT token and return user information.
        
        Args:
            token: JWT token to validate
            
        Returns:
            UserResponse: User profile if token is valid
            
        Raises:
            InvalidTokenException: If token is invalid or malformed
            TokenExpiredException: If token is expired
            UserNotFoundException: If user no longer exists
            DatabaseException: If database operation fails
        """
        try:
            logger.debug("🔄 Token validation requested")
            
            # Verify token
            token_data = verify_token(token)
            
            if not token_data:
                raise InvalidTokenException("Invalid or malformed token")
            
            # Get user ID from token
            user_id = token_data.get("sub")
            if not user_id:
                raise InvalidTokenException("Token missing user ID")
            
            # Get user from database
            user = await self.repository.get_user_by_id(UUID(user_id))
            if not user:
                raise UserNotFoundException(user_id)
            
            if not user.is_active:
                raise AuthenticationException("User account is inactive")
            
            # Convert to response format
            user_response = await self._create_user_response(user)
            
            logger.debug(f"✅ Token validated for user: {user.email}")
            
            return user_response
            
        except (InvalidTokenException, TokenExpiredException, UserNotFoundException, AuthenticationException):
            # Re-raise authentication exceptions
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error during token validation: {e}")
            raise DatabaseException("token validation", str(e))

    # ========================================================================
    # USER PROFILE METHODS
    # ========================================================================

    async def get_user_profile(self, user_id: UUID) -> UserResponse:
        """
        Get user profile by ID.
        
        Args:
            user_id: User UUID
            
        Returns:
            UserResponse: User profile information
            
        Raises:
            UserNotFoundException: If user doesn't exist
            DatabaseException: If database operation fails
        """
        try:
            logger.debug(f"🔄 Getting user profile for: {user_id}")
            
            user = await self.repository.get_user_by_id(user_id)
            if not user:
                raise UserNotFoundException(str(user_id))
            
            user_response = await self._create_user_response(user)
            
            logger.debug(f"✅ User profile retrieved: {user.email}")
            
            return user_response
            
        except UserNotFoundException:
            # Re-raise business logic exceptions
            raise
        except Exception as e:
            logger.error(f"❌ Error getting user profile {user_id}: {e}")
            raise DatabaseException("user profile retrieval", str(e))

    async def update_user_profile(
        self, 
        user_id: UUID, 
        name: Optional[str] = None
    ) -> UserResponse:
        """
        Update user profile information.
        
        Args:
            user_id: User UUID
            name: New name (optional)
            
        Returns:
            UserResponse: Updated user profile
            
        Raises:
            UserNotFoundException: If user doesn't exist
            ValidationException: If update data is invalid
            DatabaseException: If database operation fails
        """
        try:
            logger.info(f"🔄 Updating user profile for: {user_id}")
            
            user = await self.repository.get_user_by_id(user_id)
            if not user:
                raise UserNotFoundException(str(user_id))
            
            # Update name if provided
            if name is not None:
                if len(name.strip()) < 2:
                    raise create_validation_exception(
                        "name", name, "Name must be at least 2 characters", "TOO_SHORT"
                    )
                user.name = name.strip()
            
            # Update timestamp
            user.updated_at = datetime.now(timezone.utc)
            
            # Commit changes
            self.db.commit()
            self.db.refresh(user)
            
            user_response = await self._create_user_response(user)
            
            logger.info(f"✅ User profile updated: {user.email}")
            
            return user_response
            
        except (UserNotFoundException, ValidationException):
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error updating user profile {user_id}: {e}")
            raise DatabaseException("user profile update", str(e))

    # ========================================================================
    # ACCOUNT MANAGEMENT METHODS
    # ========================================================================

    async def deactivate_account(self, user_id: UUID) -> UserResponse:
        """
        Deactivate (soft delete) a user account.
        
        Args:
            user_id: User UUID to deactivate
            
        Returns:
            UserResponse: Deactivated user profile
            
        Raises:
            UserNotFoundException: If user doesn't exist
            DatabaseException: If database operation fails
        """
        try:
            logger.info(f"🔄 Deactivating account for: {user_id}")
            
            user = await self.repository.deactivate_user(user_id)
            user_response = await self._create_user_response(user)
            
            logger.info(f"✅ Account deactivated: {user.email}")
            
            return user_response
            
        except UserNotFoundException:
            # Re-raise business logic exceptions
            raise
        except Exception as e:
            logger.error(f"❌ Error deactivating account {user_id}: {e}")
            raise DatabaseException("account deactivation", str(e))

    # ========================================================================
    # PRIVATE HELPER METHODS
    # ========================================================================

    async def _create_token_for_user(
        self, 
        user: User, 
        auth_method: str = "password"
    ) -> Token:
        """
        Create JWT token for authenticated user.
        
        Args:
            user: User instance
            auth_method: Authentication method used
            
        Returns:
            Token: JWT token with expiration info
        """
        # Prepare token data
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "name": user.name,
            "auth_method": auth_method,
            "auth_provider": user.auth_provider.value,
        }
        
        # Create JWT token
        access_token = create_access_token(data=token_data)
        
        # Calculate expiration time
        expires_in = settings.jwt_expire_minutes * 60  # Convert to seconds
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=expires_in
        )

    async def _create_user_response(self, user: User) -> UserResponse:
        """
        Convert User model to UserResponse schema.
        
        Args:
            user: User database model
            
        Returns:
            UserResponse: API response schema
        """
        return UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            auth_provider=SchemaAuthProvider(user.auth_provider.value),
            is_active=user.is_active,
            created_at=user.created_at
        )

    async def _validate_password_strength(self, password: str) -> None:
        """
        Validate password meets security requirements.
        
        Args:
            password: Password to validate
            
        Raises:
            ValidationException: If password doesn't meet requirements
        """
        validation_result = validate_password_strength(password)
        
        if not validation_result["is_valid"]:
            requirements = [
                "At least 8 characters long",
                "Contains uppercase letter", 
                "Contains lowercase letter",
                "Contains number",
                "Contains special character"
            ]
            
            raise create_validation_exception(
                "password",
                "[REDACTED]",
                validation_result["message"],
                "WEAK_PASSWORD"
            )

    async def _validate_oauth_data(
        self, 
        email: str, 
        name: str, 
        oauth_provider_id: str
    ) -> None:
        """
        Validate OAuth user data.
        
        Args:
            email: Email from OAuth provider
            name: Name from OAuth provider
            oauth_provider_id: Provider user ID
            
        Raises:
            ValidationException: If OAuth data is invalid
        """
        if not email or not email.strip():
            raise create_validation_exception(
                "email", email, "Email is required from OAuth provider", "REQUIRED"
            )
        
        if not name or len(name.strip()) < 2:
            raise create_validation_exception(
                "name", name, "Valid name is required from OAuth provider", "INVALID_VALUE"
            )
        
        if not oauth_provider_id or not oauth_provider_id.strip():
            raise create_validation_exception(
                "oauth_provider_id", oauth_provider_id, "OAuth provider ID is required", "REQUIRED"
            )


# ============================================================================
# SERVICE FACTORY FUNCTIONS
# ============================================================================

def create_auth_service(db: Session) -> AuthenticationService:
    """
    Factory function to create an AuthenticationService instance.
    
    Args:
        db: Database session
        
    Returns:
        AuthenticationService: Configured service instance
        
    Example:
        ```python
        from .core.database import get_db_session
        from .auth.service import create_auth_service
        
        db = get_db_session()
        auth_service = create_auth_service(db)
        user, token = await auth_service.register_user(registration_data)
        ```
    """
    return AuthenticationService(db)


# ============================================================================
# CONVENIENCE FUNCTIONS FOR COMMON OPERATIONS
# ============================================================================

async def register_new_user_with_token(
    db: Session,
    registration_data: UserRegistrationRequest
) -> Tuple[UserResponse, Token]:
    """
    Convenience function to register a new user and get immediate login token.
    
    Args:
        db: Database session
        registration_data: User registration data
        
    Returns:
        Tuple[UserResponse, Token]: User profile and authentication token
        
    Example:
        ```python
        user, token = await register_new_user_with_token(db, registration_data)
        print(f"User {user.name} registered with token: {token.access_token[:20]}...")
        ```
    """
    service = create_auth_service(db)
    return await service.register_user(registration_data)


async def login_user_with_credentials(
    db: Session,
    email: str,
    password: str
) -> Tuple[UserResponse, Token]:
    """
    Convenience function to authenticate user and get login token.
    
    Args:
        db: Database session
        email: User email
        password: User password
        
    Returns:
        Tuple[UserResponse, Token]: User profile and authentication token
        
    Example:
        ```python
        user, token = await login_user_with_credentials(db, email, password)
        print(f"User {user.name} logged in successfully")
        ```
    """
    service = create_auth_service(db)
    login_data = UserLoginRequest(email=email, password=password)
    return await service.authenticate_user(login_data)


async def get_user_from_token(
    db: Session,
    token: str
) -> UserResponse:
    """
    Convenience function to get user profile from JWT token.
    
    Args:
        db: Database session
        token: JWT token
        
    Returns:
        UserResponse: User profile
        
    Example:
        ```python
        user = await get_user_from_token(db, jwt_token)
        print(f"Current user: {user.name}")
        ```
    """
    service = create_auth_service(db)
    return await service.validate_token(token)


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Main service class
    "AuthenticationService",
    
    # Factory functions
    "create_auth_service",
    
    # Convenience functions
    "register_new_user_with_token",
    "login_user_with_credentials", 
    "get_user_from_token",
]