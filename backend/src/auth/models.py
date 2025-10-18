"""
SQLAlchemy models for IdeaFly Authentication System.

This module defines the database models for user authentication,
including User and OAuthProfile entities.
"""

import uuid
from datetime import datetime
from typing import Optional, List
from enum import Enum as PyEnum

from sqlalchemy import (
    Column, String, Boolean, DateTime, ForeignKey, 
    Enum, Text, Index, CheckConstraint, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func

from ..core.database import Base


class AuthProvider(PyEnum):
    """Authentication provider options."""
    EMAIL = "email"
    GOOGLE = "google"
    MIXED = "mixed"


class OAuthProviderType(PyEnum):
    """Supported OAuth providers."""
    GOOGLE = "google"
    FACEBOOK = "facebook"
    GITHUB = "github"
    LINKEDIN = "linkedin"


class User(Base):
    """
    User model representing a person with access to IdeaFly platform.
    
    Supports both email/password and OAuth authentication methods.
    """
    
    __tablename__ = "users"
    
    # Primary attributes
    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
        comment="Unique immutable identifier"
    )
    
    email = Column(
        String(254), 
        unique=True, 
        nullable=False,
        index=True,
        comment="Unique email for login and communication"
    )
    
    name = Column(
        String(100), 
        nullable=False,
        comment="Full name for personalization"
    )
    
    hashed_password = Column(
        String(255), 
        nullable=True,
        comment="Bcrypt hashed password, NULL for OAuth-only users"
    )
    
    is_active = Column(
        Boolean, 
        nullable=False, 
        default=True,
        index=True,
        comment="Flag for soft delete/suspension"
    )
    
    auth_provider = Column(
        Enum(AuthProvider),
        nullable=False,
        default=AuthProvider.EMAIL,
        index=True,
        comment="Preferred authentication method"
    )
    
    # Audit timestamps
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
        comment="Creation audit timestamp"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Modification audit timestamp"
    )
    
    # Relationships
    oauth_profiles = relationship(
        "OAuthProfile",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    # Constraints
    __table_args__ = (
        # Email format validation (basic RFC 5322 pattern)
        CheckConstraint(
            "email ~ '^[a-zA-Z0-9.!#$%&''*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'",
            name="user_email_format_check"
        ),
        # Name length validation
        CheckConstraint(
            "LENGTH(name) >= 2 AND LENGTH(name) <= 100",
            name="user_name_length_check"
        ),
        # Password required for email/mixed auth
        CheckConstraint(
            "(auth_provider = 'email' AND hashed_password IS NOT NULL) OR "
            "(auth_provider = 'google' AND hashed_password IS NULL) OR "
            "(auth_provider = 'mixed' AND hashed_password IS NOT NULL)",
            name="user_password_provider_check"
        ),
        # Performance indexes
        Index("idx_user_active_email", "email", postgresql_where=Column("is_active")),
        Index("idx_user_auth_provider", "auth_provider"),
        Index("idx_user_created_at", "created_at"),
    )
    
    @validates('email')
    def validate_email(self, key: str, address: str) -> str:
        """Validate email format and length."""
        if not address or len(address.strip()) == 0:
            raise ValueError("Email cannot be empty")
        
        # Basic length check before regex
        if len(address) > 254:
            raise ValueError("Email address too long")
            
        # Convert to lowercase for consistency
        return address.lower().strip()
    
    @validates('name')
    def validate_name(self, key: str, name: str) -> str:
        """Validate name length and content."""
        if not name or len(name.strip()) < 2:
            raise ValueError("Name must be at least 2 characters long")
        
        if len(name.strip()) > 100:
            raise ValueError("Name cannot exceed 100 characters")
            
        return name.strip()
    
    @validates('auth_provider')
    def validate_auth_provider(self, key: str, provider: AuthProvider) -> AuthProvider:
        """Validate auth provider consistency with password."""
        # Note: This validation runs before hashed_password is set during creation
        # Full validation is handled by database constraints
        return provider
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<User(id={self.id}, email={self.email}, provider={self.auth_provider.value})>"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": str(self.id),
            "email": self.email,
            "name": self.name,
            "is_active": self.is_active,
            "auth_provider": self.auth_provider.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class OAuthProfile(Base):
    """
    OAuth profile model for social authentication integration.
    
    Links users to their social media accounts (Google, Facebook, etc.).
    """
    
    __tablename__ = "oauth_profiles"
    
    # Primary attributes
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique profile identifier"
    )
    
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to the user account"
    )
    
    provider = Column(
        Enum(OAuthProviderType),
        nullable=False,
        comment="OAuth provider (google, facebook, etc.)"
    )
    
    provider_user_id = Column(
        String(255),
        nullable=False,
        comment="User ID from the OAuth provider"
    )
    
    provider_email = Column(
        String(254),
        nullable=True,
        comment="Email from OAuth provider (may differ from user.email)"
    )
    
    access_token_hash = Column(
        String(255),
        nullable=True,
        comment="Hashed access token for revocation"
    )
    
    # Audit timestamps
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Profile creation timestamp"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Profile update timestamp"
    )
    
    # Relationships
    user = relationship("User", back_populates="oauth_profiles")
    
    # Constraints
    __table_args__ = (
        # Unique provider + provider_user_id combination
        UniqueConstraint(
            "provider", "provider_user_id",
            name="oauth_provider_user_unique"
        ),
        # Non-empty provider user ID
        CheckConstraint(
            "LENGTH(provider_user_id) > 0",
            name="oauth_provider_user_id_not_empty"
        ),
        # Provider email format validation (when provided)
        CheckConstraint(
            "provider_email IS NULL OR provider_email ~ '^[a-zA-Z0-9.!#$%&''*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'",
            name="oauth_provider_email_format_check"
        ),
        # Performance indexes
        Index("idx_oauth_user_provider", "user_id", "provider"),
        Index("idx_oauth_provider_lookup", "provider", "provider_user_id"),
    )
    
    @validates('provider_user_id')
    def validate_provider_user_id(self, key: str, provider_id: str) -> str:
        """Validate provider user ID is not empty."""
        if not provider_id or len(provider_id.strip()) == 0:
            raise ValueError("Provider user ID cannot be empty")
        return provider_id.strip()
    
    @validates('provider_email')
    def validate_provider_email(self, key: str, email: Optional[str]) -> Optional[str]:
        """Validate provider email format if provided."""
        if email is None or len(email.strip()) == 0:
            return None
            
        if len(email) > 254:
            raise ValueError("Provider email address too long")
            
        return email.lower().strip()
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<OAuthProfile(id={self.id}, provider={self.provider.value}, user_id={self.user_id})>"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "provider": self.provider.value,
            "provider_user_id": self.provider_user_id,
            "provider_email": self.provider_email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# Export models for easy importing
__all__ = [
    "Base",
    "User", 
    "OAuthProfile",
    "AuthProvider",
    "OAuthProviderType",
]