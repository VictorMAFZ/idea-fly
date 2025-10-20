"""
User repository for IdeaFly Authentication System.

This module provides data access layer for user operations including
registration, authentication, and user management with comprehensive
error handling and validation.
"""

import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from uuid import UUID
import uuid

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import and_, or_, select, func

from ..auth.models import User, AuthProvider, OAuthProfile
from ..auth.schemas import UserRegistrationRequest, UserResponse
from ..core.security import hash_password, verify_password
from ..core.exceptions import (
    EmailExistsException,
    UserNotFoundException,
    ValidationException,
    DatabaseException,
    InvalidCredentialsException,
    create_validation_exception,
)

# Configure logging
logger = logging.getLogger(__name__)


# ============================================================================
# USER REPOSITORY CLASS
# ============================================================================

class UserRepository:
    """
    Repository class for user-related database operations.
    
    Provides a clean interface for user CRUD operations, registration,
    authentication, and user management with proper error handling.
    """
    
    def __init__(self, db: Session):
        """
        Initialize the repository with a database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    # ========================================================================
    # USER REGISTRATION METHODS
    # ========================================================================

    async def create_user(
        self, 
        user_data: UserRegistrationRequest,
        auth_provider: AuthProvider = AuthProvider.EMAIL
    ) -> User:
        """
        Create a new user with email/password authentication.
        
        Args:
            user_data: Registration data including name, email, password
            auth_provider: Authentication provider (defaults to EMAIL)
            
        Returns:
            User: Created user instance
            
        Raises:
            EmailExistsException: If email already exists
            ValidationException: If data validation fails
            DatabaseException: If database operation fails
            
        Example:
            ```python
            registration_data = UserRegistrationRequest(
                name="Juan Pérez",
                email="juan@example.com",
                password="securePassword123"
            )
            user = await repository.create_user(registration_data)
            ```
        """
        try:
            # Check if email already exists
            if await self.email_exists(user_data.email):
                raise EmailExistsException(user_data.email)
            
            # Hash the password
            hashed_password = hash_password(user_data.password)
            
            # Create user instance
            user = User(
                id=uuid.uuid4(),
                email=user_data.email.lower().strip(),
                name=user_data.name.strip(),
                hashed_password=hashed_password,
                auth_provider=auth_provider,
                is_active=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            # Add to database
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"✅ User created successfully: {user.email} (ID: {user.id})")
            return user
            
        except EmailExistsException:
            # Re-raise business logic exceptions
            self.db.rollback()
            raise
            
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Database integrity error creating user {user_data.email}: {e}")
            
            # Check if it's an email uniqueness violation
            if "user_email_unique" in str(e) or "email" in str(e).lower():
                raise EmailExistsException(user_data.email)
            else:
                raise DatabaseException("user creation", str(e))
                
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error creating user {user_data.email}: {e}")
            raise DatabaseException("user creation", str(e))
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error creating user {user_data.email}: {e}")
            raise DatabaseException("user creation", str(e))

    async def create_oauth_user(
        self,
        email: str,
        name: str,
        oauth_provider_id: str,
        oauth_provider_type: str = "google",
        auth_provider: AuthProvider = AuthProvider.GOOGLE
    ) -> User:
        """
        Create a new user from OAuth authentication.
        
        Args:
            email: User email from OAuth provider
            name: User name from OAuth provider
            oauth_provider_id: OAuth provider user ID
            oauth_provider_type: OAuth provider type (google, facebook, etc.)
            auth_provider: Authentication provider for the user
            
        Returns:
            User: Created user instance with OAuth profile
            
        Raises:
            EmailExistsException: If email already exists
            DatabaseException: If database operation fails
            
        Example:
            ```python
            user = await repository.create_oauth_user(
                email="juan@gmail.com",
                name="Juan Pérez",
                oauth_provider_id="google_user_123",
                oauth_provider_type="google"
            )
            ```
        """
        try:
            # Check if email already exists
            if await self.email_exists(email):
                raise EmailExistsException(email)
            
            # Create user instance (no password for OAuth-only users)
            user = User(
                id=uuid.uuid4(),
                email=email.lower().strip(),
                name=name.strip(),
                hashed_password=None,  # OAuth users don't have passwords initially
                auth_provider=auth_provider,
                is_active=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            # Add to database
            self.db.add(user)
            self.db.flush()  # Get user ID for OAuth profile
            
            # Create OAuth profile
            oauth_profile = OAuthProfile(
                id=uuid.uuid4(),
                user_id=user.id,
                provider=oauth_provider_type,
                provider_user_id=oauth_provider_id,
                email=email.lower().strip(),
                name=name.strip(),
                created_at=datetime.now(timezone.utc)
            )
            
            self.db.add(oauth_profile)
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"✅ OAuth user created successfully: {user.email} (Provider: {oauth_provider_type})")
            return user
            
        except EmailExistsException:
            # Re-raise business logic exceptions
            self.db.rollback()
            raise
            
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Database integrity error creating OAuth user {email}: {e}")
            
            if "user_email_unique" in str(e) or "email" in str(e).lower():
                raise EmailExistsException(email)
            else:
                raise DatabaseException("OAuth user creation", str(e))
                
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error creating OAuth user {email}: {e}")
            raise DatabaseException("OAuth user creation", str(e))
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error creating OAuth user {email}: {e}")
            raise DatabaseException("OAuth user creation", str(e))

    # ========================================================================
    # USER LOOKUP METHODS
    # ========================================================================

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: UUID of the user
            
        Returns:
            User: User instance if found, None otherwise
            
        Raises:
            DatabaseException: If database operation fails
            
        Example:
            ```python
            user = await repository.get_user_by_id(user_uuid)
            if user:
                print(f"Found user: {user.email}")
            ```
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if user:
                logger.debug(f"Found user by ID: {user_id}")
            else:
                logger.debug(f"User not found by ID: {user_id}")
                
            return user
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting user by ID {user_id}: {e}")
            raise DatabaseException("user lookup", str(e))

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            email: Email address to search for
            
        Returns:
            User: User instance if found, None otherwise
            
        Raises:
            DatabaseException: If database operation fails
            
        Example:
            ```python
            user = await repository.get_user_by_email("juan@example.com")
            if user:
                print(f"Found user: {user.name}")
            ```
        """
        try:
            user = self.db.query(User).filter(
                User.email == email.lower().strip()
            ).first()
            
            if user:
                logger.debug(f"Found user by email: {email}")
            else:
                logger.debug(f"User not found by email: {email}")
                
            return user
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting user by email {email}: {e}")
            raise DatabaseException("user lookup", str(e))

    async def get_active_user_by_email(self, email: str) -> Optional[User]:
        """
        Get active user by email address.
        
        Args:
            email: Email address to search for
            
        Returns:
            User: Active user instance if found, None otherwise
            
        Raises:
            DatabaseException: If database operation fails
        """
        try:
            user = self.db.query(User).filter(
                and_(
                    User.email == email.lower().strip(),
                    User.is_active == True
                )
            ).first()
            
            if user:
                logger.debug(f"Found active user by email: {email}")
            else:
                logger.debug(f"Active user not found by email: {email}")
                
            return user
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting active user by email {email}: {e}")
            raise DatabaseException("user lookup", str(e))

    async def get_user_with_oauth_profiles(self, user_id: UUID) -> Optional[User]:
        """
        Get user with OAuth profiles loaded.
        
        Args:
            user_id: UUID of the user
            
        Returns:
            User: User instance with oauth_profiles loaded, None if not found
            
        Raises:
            DatabaseException: If database operation fails
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if user:
                # Explicitly load OAuth profiles
                _ = user.oauth_profiles  # This triggers the lazy loading
                logger.debug(f"Found user with OAuth profiles: {user_id}")
            else:
                logger.debug(f"User not found: {user_id}")
                
            return user
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting user with OAuth profiles {user_id}: {e}")
            raise DatabaseException("user lookup", str(e))

    # ========================================================================
    # AUTHENTICATION METHODS
    # ========================================================================

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate user with email and password.
        
        Args:
            email: User email address
            password: Plain text password
            
        Returns:
            User: Authenticated user if credentials are valid, None otherwise
            
        Raises:
            DatabaseException: If database operation fails
            
        Example:
            ```python
            user = await repository.authenticate_user("juan@example.com", "password123")
            if user:
                print(f"Authentication successful for {user.email}")
            else:
                print("Invalid credentials")
            ```
        """
        try:
            # Get active user by email
            user = await self.get_active_user_by_email(email)
            
            if not user:
                logger.warning(f"Authentication failed - user not found: {email}")
                return None
            
            # Check if user has a password (not OAuth-only)
            if not user.hashed_password:
                logger.warning(f"Authentication failed - OAuth-only user attempted password login: {email}")
                return None
            
            # Verify password
            if not verify_password(password, user.hashed_password):
                logger.warning(f"Authentication failed - invalid password for user: {email}")
                return None
            
            logger.info(f"✅ Authentication successful for user: {email}")
            return user
            
        except SQLAlchemyError as e:
            logger.error(f"Database error during authentication for {email}: {e}")
            raise DatabaseException("user authentication", str(e))

    async def authenticate_oauth_user(
        self, 
        email: str, 
        oauth_provider_id: str, 
        oauth_provider_type: str = "google"
    ) -> Optional[User]:
        """
        Authenticate or create user via OAuth.
        
        Args:
            email: Email from OAuth provider
            oauth_provider_id: Provider-specific user ID
            oauth_provider_type: OAuth provider type
            
        Returns:
            User: Authenticated/created user instance
            
        Raises:
            DatabaseException: If database operation fails
        """
        try:
            # First, try to find existing OAuth profile
            oauth_profile = self.db.query(OAuthProfile).filter(
                and_(
                    OAuthProfile.provider == oauth_provider_type,
                    OAuthProfile.provider_user_id == oauth_provider_id
                )
            ).first()
            
            if oauth_profile:
                # Existing OAuth user
                user = oauth_profile.user
                if user and user.is_active:
                    logger.info(f"✅ OAuth authentication successful for existing user: {email}")
                    return user
            
            # Try to find user by email (for linking OAuth to existing account)
            user = await self.get_active_user_by_email(email)
            
            if user:
                # User exists with email but no OAuth profile - link them
                logger.info(f"Linking OAuth profile to existing user: {email}")
                
                # Create OAuth profile for existing user
                new_oauth_profile = OAuthProfile(
                    id=uuid.uuid4(),
                    user_id=user.id,
                    provider=oauth_provider_type,
                    provider_user_id=oauth_provider_id,
                    email=email.lower().strip(),
                    name=user.name,
                    created_at=datetime.now(timezone.utc)
                )
                
                self.db.add(new_oauth_profile)
                
                # Update user auth provider to mixed
                user.auth_provider = AuthProvider.MIXED
                user.updated_at = datetime.now(timezone.utc)
                
                self.db.commit()
                self.db.refresh(user)
                
                logger.info(f"✅ OAuth profile linked to existing user: {email}")
                return user
            
            # No existing user found - this should be handled by create_oauth_user
            logger.debug(f"No existing user found for OAuth authentication: {email}")
            return None
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error during OAuth authentication for {email}: {e}")
            raise DatabaseException("OAuth authentication", str(e))

    # ========================================================================
    # VALIDATION METHODS
    # ========================================================================

    async def email_exists(self, email: str) -> bool:
        """
        Check if email address already exists in the system.
        
        Args:
            email: Email address to check
            
        Returns:
            bool: True if email exists, False otherwise
            
        Raises:
            DatabaseException: If database operation fails
            
        Example:
            ```python
            if await repository.email_exists("juan@example.com"):
                print("Email already registered")
            ```
        """
        try:
            exists = self.db.query(User).filter(
                User.email == email.lower().strip()
            ).first() is not None
            
            logger.debug(f"Email exists check for {email}: {exists}")
            return exists
            
        except SQLAlchemyError as e:
            logger.error(f"Database error checking email existence {email}: {e}")
            raise DatabaseException("email validation", str(e))

    async def validate_registration_data(self, user_data: UserRegistrationRequest) -> None:
        """
        Validate registration data before user creation.
        
        Args:
            user_data: Registration data to validate
            
        Raises:
            EmailExistsException: If email already exists
            ValidationException: If data validation fails
            DatabaseException: If database operation fails
        """
        try:
            # Check email uniqueness
            if await self.email_exists(user_data.email):
                raise EmailExistsException(user_data.email)
            
            # Additional validation can be added here
            # (Pydantic handles most validation, but we can add business rules)
            
            logger.debug(f"Registration data validation passed for: {user_data.email}")
            
        except EmailExistsException:
            # Re-raise business logic exceptions
            raise
        except Exception as e:
            logger.error(f"Error validating registration data for {user_data.email}: {e}")
            raise ValidationException("Registration data validation failed")

    # ========================================================================
    # USER MANAGEMENT METHODS
    # ========================================================================

    async def update_user_last_login(self, user_id: UUID) -> None:
        """
        Update user's last login timestamp.
        
        Args:
            user_id: UUID of the user
            
        Raises:
            UserNotFoundException: If user not found
            DatabaseException: If database operation fails
        """
        try:
            user = await self.get_user_by_id(user_id)
            
            if not user:
                raise UserNotFoundException(str(user_id))
            
            user.updated_at = datetime.now(timezone.utc)
            self.db.commit()
            
            logger.debug(f"Updated last login for user: {user_id}")
            
        except UserNotFoundException:
            self.db.rollback()
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error updating last login for user {user_id}: {e}")
            raise DatabaseException("user update", str(e))

    async def deactivate_user(self, user_id: UUID) -> User:
        """
        Deactivate (soft delete) a user account.
        
        Args:
            user_id: UUID of the user to deactivate
            
        Returns:
            User: Deactivated user instance
            
        Raises:
            UserNotFoundException: If user not found
            DatabaseException: If database operation fails
        """
        try:
            user = await self.get_user_by_id(user_id)
            
            if not user:
                raise UserNotFoundException(str(user_id))
            
            user.is_active = False
            user.updated_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"User deactivated: {user.email} (ID: {user_id})")
            return user
            
        except UserNotFoundException:
            self.db.rollback()
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error deactivating user {user_id}: {e}")
            raise DatabaseException("user deactivation", str(e))

    async def reactivate_user(self, user_id: UUID) -> User:
        """
        Reactivate a deactivated user account.
        
        Args:
            user_id: UUID of the user to reactivate
            
        Returns:
            User: Reactivated user instance
            
        Raises:
            UserNotFoundException: If user not found
            DatabaseException: If database operation fails
        """
        try:
            user = await self.get_user_by_id(user_id)
            
            if not user:
                raise UserNotFoundException(str(user_id))
            
            user.is_active = True
            user.updated_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"User reactivated: {user.email} (ID: {user_id})")
            return user
            
        except UserNotFoundException:
            self.db.rollback()
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error reactivating user {user_id}: {e}")
            raise DatabaseException("user reactivation", str(e))

    # ========================================================================
    # QUERY METHODS
    # ========================================================================

    async def get_users_by_provider(
        self, 
        auth_provider: AuthProvider, 
        limit: int = 100, 
        offset: int = 0
    ) -> List[User]:
        """
        Get users by authentication provider with pagination.
        
        Args:
            auth_provider: Authentication provider to filter by
            limit: Maximum number of users to return
            offset: Number of users to skip
            
        Returns:
            List[User]: List of users matching the criteria
            
        Raises:
            DatabaseException: If database operation fails
        """
        try:
            users = self.db.query(User).filter(
                and_(
                    User.auth_provider == auth_provider,
                    User.is_active == True
                )
            ).offset(offset).limit(limit).all()
            
            logger.debug(f"Found {len(users)} users with provider {auth_provider.value}")
            return users
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting users by provider {auth_provider.value}: {e}")
            raise DatabaseException("user query", str(e))

    async def count_active_users(self) -> int:
        """
        Count total active users in the system.
        
        Returns:
            int: Number of active users
            
        Raises:
            DatabaseException: If database operation fails
        """
        try:
            count = self.db.query(func.count(User.id)).filter(
                User.is_active == True
            ).scalar()
            
            logger.debug(f"Total active users: {count}")
            return count or 0
            
        except SQLAlchemyError as e:
            logger.error(f"Database error counting active users: {e}")
            raise DatabaseException("user count", str(e))


# ============================================================================
# REPOSITORY FACTORY FUNCTIONS
# ============================================================================

def create_user_repository(db: Session) -> UserRepository:
    """
    Factory function to create a UserRepository instance.
    
    Args:
        db: Database session
        
    Returns:
        UserRepository: Configured repository instance
        
    Example:
        ```python
        from .core.database import get_db_session
        
        db = get_db_session()
        repository = create_user_repository(db)
        user = await repository.get_user_by_email("juan@example.com")
        ```
    """
    return UserRepository(db)


# ============================================================================
# CONVENIENCE FUNCTIONS FOR COMMON OPERATIONS
# ============================================================================

async def register_new_user(
    db: Session, 
    user_data: UserRegistrationRequest
) -> User:
    """
    Convenience function to register a new user.
    
    Args:
        db: Database session
        user_data: Registration data
        
    Returns:
        User: Created user instance
        
    Raises:
        EmailExistsException: If email already exists
        ValidationException: If data validation fails
        DatabaseException: If database operation fails
        
    Example:
        ```python
        registration_data = UserRegistrationRequest(
            name="Juan Pérez",
            email="juan@example.com",
            password="securePassword123"
        )
        user = await register_new_user(db, registration_data)
        ```
    """
    repository = create_user_repository(db)
    
    # Validate data before creation
    await repository.validate_registration_data(user_data)
    
    # Create the user
    user = await repository.create_user(user_data)
    
    return user


async def authenticate_login(
    db: Session, 
    email: str, 
    password: str
) -> Optional[User]:
    """
    Convenience function to authenticate a user login.
    
    Args:
        db: Database session
        email: User email
        password: User password
        
    Returns:
        User: Authenticated user if successful, None otherwise
        
    Raises:
        DatabaseException: If database operation fails
        
    Example:
        ```python
        user = await authenticate_login(db, "juan@example.com", "password123")
        if user:
            print("Login successful")
        else:
            print("Invalid credentials")
        ```
    """
    repository = create_user_repository(db)
    user = await repository.authenticate_user(email, password)
    
    if user:
        # Update last login timestamp
        await repository.update_user_last_login(user.id)
    
    return user


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Main repository class
    "UserRepository",
    
    # Factory functions
    "create_user_repository",
    
    # Convenience functions
    "register_new_user",
    "authenticate_login",
]