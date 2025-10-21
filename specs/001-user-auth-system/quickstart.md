# Quickstart: Sistema de Autenticación de Usuarios

**Feature**: Sistema de Autenticación de Usuarios  
**Phase**: 1 - Design & Contracts  
**Date**: 2025-10-18

## Overview

Esta guía proporciona instrucciones rápidas para implementar y probar el sistema de autenticación de IdeaFly con registro tradicional (email/contraseña) y autenticación OAuth con Google.

## Prerequisites

### Backend Setup
```bash
# Navigate to backend directory
cd backend/

# Install Python dependencies
pip install fastapi uvicorn sqlalchemy psycopg2-binary alembic
pip install python-jose[cryptography] passlib[bcrypt] python-multipart
pip install pydantic[email] httpx

# Environment variables (.env)
JWT_SECRET_KEY=your-super-secret-jwt-key-here
DATABASE_URL=postgresql://user:password@localhost:5433/ideafly_auth
GOOGLE_CLIENT_ID=your-google-oauth-client-id
GOOGLE_CLIENT_SECRET=your-google-oauth-client-secret
```

### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend/

# Install Node.js dependencies
npm install next react react-dom typescript @types/react @types/node
npm install @react-oauth/google axios tailwindcss
npm install @types/js-cookie js-cookie

# Environment variables (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-oauth-client-id
```

### Database Setup
```sql
-- Create PostgreSQL database
CREATE DATABASE ideafly_auth;
CREATE USER ideafly_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ideafly_auth TO ideafly_user;

-- Run from backend/ directory
alembic init alembic
alembic revision --autogenerate -m "Create users table"
alembic upgrade head
```

## Quick Implementation Steps

### 1. Backend Implementation (30 minutes)

**File: `backend/src/auth/models.py`**
```python
from sqlalchemy import Column, String, Boolean, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(254), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    auth_provider = Column(String(20), default='email', nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**File: `backend/src/auth/schemas.py`**
```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 86400

class UserResponse(BaseModel):
    id: UUID
    name: str
    email: str
    auth_provider: str
    is_active: bool
    created_at: datetime
    
    class Config:
        orm_mode = True
```

**File: `backend/src/auth/service.py`**
```python
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import httpx

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

class AuthService:
    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    async def get_google_user_info(self, oauth_code: str) -> dict:
        # Implementation for Google OAuth flow
        # Exchange code for token, then get user info
        pass
```

**File: `backend/src/auth/router.py`**
```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from .schemas import UserCreate, UserLogin, Token, UserResponse
from .service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()
auth_service = AuthService()

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    # Implementation: check email exists, hash password, create user, return token
    pass

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    # Implementation: verify credentials, return token
    pass

@router.post("/google/callback", response_model=Token)
async def google_oauth_callback(oauth_code: str):
    # Implementation: exchange OAuth code, create/login user, return token
    pass

@router.get("/users/me", response_model=UserResponse)
async def get_current_user(token: str = Depends(security)):
    # Implementation: decode JWT, return user info
    pass
```

### 2. Frontend Implementation (45 minutes)

**File: `frontend/src/contexts/AuthContext.tsx`**
```typescript
import React, { createContext, useContext, useState, useEffect } from 'react';

interface User {
  id: string;
  name: string;
  email: string;
  authProvider: string;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  googleAuth: (code: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    isAuthenticated: false,
    isLoading: true,
  });

  // Implementation of auth methods
  // ... login, register, logout, googleAuth functions

  return (
    <AuthContext.Provider value={{ ...authState, login, register, logout, googleAuth }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
```

**File: `frontend/src/components/auth/LoginForm.tsx`**
```typescript
import React, { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { GoogleAuthButton } from './GoogleAuthButton';

export const LoginForm: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login, isLoading } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(email, password);
    } catch (err) {
      setError('Email or password is incorrect');
    }
  };

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-6 text-center">Sign In</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded-md"
            required
          />
        </div>
        
        <div>
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded-md"
            required
          />
        </div>
        
        {error && <p className="text-red-500 text-sm">{error}</p>}
        
        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-blue-500 text-white p-3 rounded-md hover:bg-blue-600 disabled:opacity-50"
        >
          {isLoading ? 'Signing In...' : 'Sign In'}
        </button>
      </form>
      
      <div className="mt-4">
        <GoogleAuthButton />
      </div>
    </div>
  );
};
```

### 3. Google OAuth Setup

**Google Cloud Console Configuration:**
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create new project or select existing
3. Enable Google+ API and Google Identity API
4. Create OAuth 2.0 credentials
5. Add authorized origins: `http://localhost:3000` (development)
6. Add redirect URIs: `http://localhost:3000/auth/callback`

**Frontend Google Integration:**
```typescript
// frontend/src/components/auth/GoogleAuthButton.tsx
import { GoogleLogin } from '@react-oauth/google';
import { useAuth } from '@/contexts/AuthContext';

export const GoogleAuthButton: React.FC = () => {
  const { googleAuth } = useAuth();

  return (
    <GoogleLogin
      onSuccess={(credentialResponse) => {
        if (credentialResponse.credential) {
          googleAuth(credentialResponse.credential);
        }
      }}
      onError={() => {
        console.log('Login Failed');
      }}
      text="continue_with"
      shape="rectangular"
      theme="outline"
      size="large"
      width="100%"
    />
  );
};
```

## Testing the Implementation

### 1. Backend Testing
```bash
# Start FastAPI server
cd backend/
uvicorn src.main:app --reload --port 8000

# Test endpoints with curl
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "email": "test@example.com", "password": "password123"}'

curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

### 2. Frontend Testing
```bash
# Start Next.js development server
cd frontend/
npm run dev

# Navigate to http://localhost:3000
# Test registration flow
# Test login flow
# Test Google OAuth flow
```

### 3. Integration Testing
```python
# backend/tests/test_auth_integration.py
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_user_registration_flow():
    # Test complete registration -> login -> get profile flow
    response = client.post("/auth/register", json={
        "name": "Test User",
        "email": "test@example.com", 
        "password": "password123"
    })
    assert response.status_code == 201
    token = response.json()["access_token"]
    
    # Test authenticated request
    headers = {"Authorization": f"Bearer {token}"}
    profile_response = client.get("/users/me", headers=headers)
    assert profile_response.status_code == 200
```

## Success Criteria Validation

**Performance Checks:**
- ✅ Registration flow < 2 minutes (measured via frontend)
- ✅ Login response < 500ms (measured via API)
- ✅ Google OAuth < 30 seconds (measured end-to-end)

**Functionality Checks:**
- ✅ Email validation working
- ✅ Password hashing secure (bcrypt 12 rounds)
- ✅ JWT tokens valid for 24 hours
- ✅ Google OAuth integration functional
- ✅ Error messages clear and user-friendly

**Security Checks:**
- ✅ Passwords never stored in plain text
- ✅ JWT secret key from environment variable
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ CORS configured properly for frontend

## Next Steps

1. **Run Unit Tests**: Execute test suite to validate all components
2. **Performance Testing**: Use load testing tools to verify 1000+ concurrent users
3. **Security Audit**: Review JWT implementation and OAuth flow security
4. **UI/UX Testing**: Validate accessibility (WCAG) and responsive design
5. **Deploy to Staging**: Test end-to-end in staging environment

## Troubleshooting

**Common Issues:**
- **JWT Token Issues**: Verify SECRET_KEY matches between encoding/decoding
- **Google OAuth Errors**: Check Client ID and redirect URIs configuration
- **Database Connection**: Verify PostgreSQL is running and credentials are correct
- **CORS Issues**: Ensure backend allows frontend origin in CORS settings

**Debug Commands:**
```bash
# Backend logs
uvicorn src.main:app --reload --log-level debug

# Frontend debugging
npm run dev -- --debug

# Database connection test
psql postgresql://user:password@localhost:5433/ideafly_auth
```