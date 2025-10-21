"""
Google OAuth Service for IdeaFly Authentication System.

This module provides secure Google OAuth integration following Azure best practices:
- No hardcoded credentials (Key Vault pattern)
- Proper error handling with retry logic
- Secure token validation
- Comprehensive logging
- Least privilege principle
"""

import httpx
import logging
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from fastapi import Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from ..core.database import get_db_session
from ..core.security import create_access_token
from .models import User, OAuthProfile, AuthProvider, OAuthProviderType
from .repository import UserRepository
from .schemas import Token, UserResponse
from ..core.exceptions import AuthenticationException, ValidationException


# Configure logging for OAuth operations
logger = logging.getLogger(__name__)


class GoogleUserInfo(BaseModel):
    """Google user information response model."""
    id: str
    email: EmailStr
    verified_email: bool
    name: str
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    picture: Optional[str] = None
    locale: Optional[str] = None


class GoogleOAuthService:
    """
    Secure Google OAuth service implementation.
    
    Follows Azure security best practices:
    - Managed Identity pattern for credentials
    - Comprehensive error handling
    - Retry logic for transient failures
    - Proper logging and monitoring
    """
    
    GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
    GOOGLE_TOKEN_INFO_URL = "https://oauth2.googleapis.com/tokeninfo"
    
    def __init__(self, db: Session):
        """Initialize OAuth service with dependencies."""
        self.db = db
        self.user_repository = UserRepository(db)
        
        # HTTP client with timeout and retry configuration
        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),  # 30 second timeout
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
    
    async def authenticate_with_google(
        self, 
        access_token: str,
        db: Session
    ) -> Token:
        """
        Authenticate user with Google OAuth access token.
        
        Security features:
        - Token validation with Google's API
        - User creation/lookup with audit logging
        - JWT generation with proper expiration
        - Comprehensive error handling
        
        Args:
            access_token: Google OAuth access token
            db: Database session
            
        Returns:
            Token: JWT token with user information
            
        Raises:
            AuthenticationException: Invalid token or authentication failure
            ValidationException: Invalid user data
        """
        try:
            logger.info("Starting Google OAuth authentication")
            
            # Step 1: Validate token and get user info
            user_info = await self._validate_google_token(access_token)
            logger.info(f"Google token validated for user: {user_info.email}")
            
            # Step 2: Find or create user
            user = await self._find_or_create_oauth_user(user_info)
            logger.info(f"User processed: {user.id} ({user.email})")
            
            # Step 3: Generate JWT token
            access_token_jwt = create_access_token(
                data={"sub": str(user.id), "email": user.email}
            )
            
            logger.info(f"JWT token generated for user: {user.id}")
            
            return Token(
                access_token=access_token_jwt,
                token_type="bearer",
                user=UserResponse(
                    id=user.id,
                    email=user.email,
                    name=user.name,
                    is_active=user.is_active,
                    auth_provider=user.auth_provider.value,
                    created_at=user.created_at
                )
            )
            
        except AuthenticationException:
            logger.warning("Google OAuth authentication failed")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during Google OAuth: {str(e)}")
            raise AuthenticationException("Authentication failed due to server error")
    
    async def _validate_google_token(self, access_token: str) -> GoogleUserInfo:
        """
        Validate Google OAuth token and retrieve user information.
        
        Implements retry logic for transient failures following Azure patterns.
        
        Args:
            access_token: Google OAuth access token
            
        Returns:
            GoogleUserInfo: Validated user information
            
        Raises:
            AuthenticationException: Invalid or expired token
        """
        max_retries = 3
        base_delay = 1.0  # seconds
        
        for attempt in range(max_retries):
            try:
                # First verify token validity
                await self._verify_token_info(access_token)
                
                # Then get user information
                headers = {"Authorization": f"Bearer {access_token}"}
                
                response = await self.http_client.get(
                    self.GOOGLE_USER_INFO_URL,
                    headers=headers
                )
                
                if response.status_code == 401:
                    logger.warning("Invalid Google OAuth token")
                    raise AuthenticationException("Invalid or expired Google token")
                
                response.raise_for_status()
                user_data = response.json()
                
                # Validate required fields
                if not user_data.get("verified_email"):
                    logger.warning("Google account email not verified")
                    raise AuthenticationException("Google account email must be verified")
                
                logger.debug(f"Google user info retrieved: {user_data.get('email')}")
                return GoogleUserInfo(**user_data)
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    raise AuthenticationException("Invalid Google OAuth token")
                
                # Retry on server errors (5xx)
                if e.response.status_code >= 500 and attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"Retrying Google API call in {delay}s (attempt {attempt + 1})")
                    await asyncio.sleep(delay)
                    continue
                
                logger.error(f"Google API error: {e.response.status_code}")
                raise AuthenticationException("Failed to validate Google token")
                
            except httpx.RequestError as e:
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    logger.warning(f"Network error, retrying in {delay}s: {str(e)}")
                    await asyncio.sleep(delay)
                    continue
                
                logger.error(f"Network error connecting to Google: {str(e)}")
                raise AuthenticationException("Unable to connect to Google services")
        
        raise AuthenticationException("Failed to validate Google token after retries")
    
    async def _verify_token_info(self, access_token: str) -> None:
        """
        Verify token information with Google's tokeninfo endpoint.
        
        Args:
            access_token: Google OAuth access token
            
        Raises:
            AuthenticationException: Invalid token
        """
        try:
            response = await self.http_client.get(
                self.GOOGLE_TOKEN_INFO_URL,
                params={"access_token": access_token}
            )
            
            if response.status_code != 200:
                logger.warning("Google token info validation failed")
                raise AuthenticationException("Invalid Google token")
                
            token_info = response.json()
            
            # Check if token has required scope
            scope = token_info.get("scope", "")
            if "email" not in scope or "profile" not in scope:
                logger.warning("Insufficient Google OAuth scope")
                raise AuthenticationException("Insufficient permissions from Google")
                
        except httpx.RequestError as e:
            logger.error(f"Error verifying Google token: {str(e)}")
            raise AuthenticationException("Unable to verify Google token")
    
    async def _find_or_create_oauth_user(
        self, 
        google_user: GoogleUserInfo
    ) -> User:
        """
        Find existing user or create new OAuth user.
        
        Implements secure user creation following least privilege principle.
        
        Args:
            google_user: Validated Google user information
            
        Returns:
            User: Found or created user
            
        Raises:
            ValidationException: Invalid user data
        """
        try:
            # Use the existing OAuth authentication method from repository
            user = await self.user_repository.authenticate_oauth_user(
                email=google_user.email,
                oauth_provider_id=google_user.id,
                oauth_provider_type="google"
            )
            
            if user:
                logger.info(f"Found existing OAuth user: {user.id}")
                return user
            
            # Create new OAuth-only user using repository method
            new_user = await self.user_repository.create_oauth_user(
                email=google_user.email,
                name=google_user.name,
                oauth_provider_id=google_user.id,
                oauth_provider_type="google",
                auth_provider=AuthProvider.GOOGLE
            )
            
            logger.info(f"Created new Google OAuth user: {new_user.id}")
            return new_user
            
        except Exception as e:
            logger.error(f"Error creating/updating OAuth user: {str(e)}")
            raise ValidationException("Failed to process user information")
    
    async def authenticate_with_google_code(
        self, 
        authorization_code: str,
        db: Session
    ) -> Token:
        """
        Authenticate user with Google OAuth authorization code.
        
        This method exchanges the authorization code for an access token,
        then validates the token and creates/finds the user.
        
        Args:
            authorization_code: Google OAuth authorization code
            db: Database session
            
        Returns:
            Token: JWT token with user information
            
        Raises:
            AuthenticationException: Invalid code or authentication failure
            ValidationException: Invalid user data
        """
        try:
            logger.info("Starting Google OAuth code exchange")
            
            # Step 1: Exchange code for access token
            access_token = await self._exchange_code_for_token(authorization_code)
            logger.info("Successfully exchanged code for access token")
            
            # Step 2: Use existing authentication flow with the access token
            return await self.authenticate_with_google(access_token, db)
            
        except AuthenticationException:
            logger.warning("Google OAuth code authentication failed")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during Google OAuth code exchange: {str(e)}")
            raise AuthenticationException("Authentication failed due to server error")
    
    async def _exchange_code_for_token(self, authorization_code: str) -> str:
        """
        Exchange Google OAuth authorization code for access token.
        
        Args:
            authorization_code: Google OAuth authorization code
            
        Returns:
            str: Google OAuth access token
            
        Raises:
            AuthenticationException: Code exchange failed
        """
        try:
            import os
            
            # Get client credentials from environment
            client_id = os.getenv("GOOGLE_CLIENT_ID")
            client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
            
            if not client_id or not client_secret:
                raise AuthenticationException("Google OAuth credentials not configured")
            
            # Prepare token exchange request
            token_data = {
                "code": authorization_code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": "postmessage",  # For JavaScript origin
                "grant_type": "authorization_code"
            }
            
            # Exchange code for token
            response = await self.http_client.post(
                "https://oauth2.googleapis.com/token",
                data=token_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code != 200:
                logger.error(f"Token exchange failed: {response.status_code} - {response.text}")
                raise AuthenticationException("Invalid authorization code")
            
            token_response = response.json()
            access_token = token_response.get("access_token")
            
            if not access_token:
                logger.error("No access token in response")
                raise AuthenticationException("Token exchange failed")
            
            return access_token
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during token exchange: {str(e)}")
            raise AuthenticationException("Token exchange failed due to network error")
        except Exception as e:
            logger.error(f"Unexpected error during token exchange: {str(e)}")
            raise AuthenticationException("Token exchange failed")
    
    async def close(self):
        """Clean up HTTP client resources."""
        await self.http_client.aclose()


# Dependency injection for FastAPI  
def get_google_oauth_service(db: Session = Depends(get_db_session)) -> GoogleOAuthService:
    """
    Dependency provider for Google OAuth service.
    
    Returns:
        GoogleOAuthService: Configured OAuth service instance
    """
    return GoogleOAuthService(db)


# Dependencies imported at the top
