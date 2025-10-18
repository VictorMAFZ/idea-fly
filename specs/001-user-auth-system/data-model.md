# Data Model: Sistema de Autenticación de Usuarios

**Phase**: 1 - Design & Contracts  
**Date**: 2025-10-18  
**Prerequisites**: [research.md](./research.md)

## Entity Definitions

### Core Entities

#### User
**Purpose**: Representa una persona con acceso a la plataforma IdeaFly

**Attributes**:
- `id`: UUID (Primary Key) - Identificador único inmutable
- `email`: String (Unique, Required) - Email único para login y comunicación  
- `name`: String (Required) - Nombre completo del usuario para personalización
- `hashed_password`: String (Optional) - Password hasheada con bcrypt, NULL para usuarios OAuth-only
- `is_active`: Boolean (Default: True) - Flag para soft delete / suspensión
- `auth_provider`: Enum ['email', 'google', 'mixed'] - Método de autenticación preferido
- `created_at`: Timestamp - Auditoría de creación
- `updated_at`: Timestamp - Auditoría de modificación

**Validation Rules**:
- Email debe cumplir RFC 5322 format
- Password requerido si auth_provider = 'email' o 'mixed'
- Name longitud mínima 2 caracteres, máxima 100
- Email único a nivel de constraint de base de datos

**State Transitions**:
```
[New] → register() → [Active]
[Active] → deactivate() → [Inactive]  
[Inactive] → reactivate() → [Active]
```

#### Session (Implicit - JWT Based)
**Purpose**: Representa una sesión activa de usuario sin persistencia en BD

**Attributes** (JWT Claims):
- `user_id`: UUID - Referencia al usuario autenticado
- `email`: String - Email del usuario (para convenience)
- `iat`: Timestamp - Issued at (creación del token)
- `exp`: Timestamp - Expiration (24h por defecto)
- `auth_method`: String - Método usado ('password' o 'google_oauth')

**Validation Rules**:
- Token debe estar firmado con JWT_SECRET_KEY
- exp debe ser > current timestamp
- user_id debe corresponder a usuario activo

#### OAuth Profile (Phase 1.5 - Opcional)
**Purpose**: Almacena información de proveedores OAuth para usuarios que usan autenticación social

**Attributes**:
- `id`: UUID (Primary Key)
- `user_id`: UUID (Foreign Key → User.id)
- `provider`: Enum ['google'] - Proveedor OAuth (extensible)
- `provider_user_id`: String - ID del usuario en el proveedor
- `provider_email`: String - Email del proveedor (puede diferir de User.email)
- `access_token_hash`: String (Optional) - Hash del access token para revocation
- `created_at`: Timestamp
- `updated_at`: Timestamp

**Validation Rules**:
- Unique constraint en (provider, provider_user_id)
- provider_email debe ser válido si presente
- user_id debe referenciar usuario existente

## Relationships

```
User (1) ←→ (0..1) OAuth Profile
- Un usuario puede tener máximo un perfil OAuth por proveedor
- Un perfil OAuth pertenece a exactamente un usuario
- Cascade delete: eliminar usuario elimina perfil OAuth
```

## Database Schema (SQLAlchemy)

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(254) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    hashed_password VARCHAR(255), -- NULL for OAuth-only users
    is_active BOOLEAN NOT NULL DEFAULT true,
    auth_provider VARCHAR(20) NOT NULL DEFAULT 'email',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active) WHERE is_active = true;
CREATE INDEX idx_users_auth_provider ON users(auth_provider);

-- OAuth profiles (Phase 1.5)
CREATE TABLE oauth_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL,
    provider_user_id VARCHAR(255) NOT NULL,
    provider_email VARCHAR(254),
    access_token_hash VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(provider, provider_user_id)
);

CREATE INDEX idx_oauth_user_id ON oauth_profiles(user_id);
CREATE INDEX idx_oauth_provider ON oauth_profiles(provider, provider_user_id);
```

## Data Transfer Objects (DTOs)

### Request DTOs (Pydantic)

```python
# User registration
class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)

# User login  
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Google OAuth callback
class GoogleOAuthCallback(BaseModel):
    code: str
    state: Optional[str] = None
```

### Response DTOs (Pydantic)

```python
# Authentication token
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 86400  # 24 hours

# User info response
class UserResponse(BaseModel):
    id: UUID
    name: str
    email: str
    auth_provider: str
    is_active: bool
    created_at: datetime

# Error response
class ErrorResponse(BaseModel):
    error_code: str
    message: str
    details: Optional[dict] = None
```

### Frontend TypeScript Interfaces

```typescript
// User data
interface User {
  id: string;
  name: string;
  email: string;
  authProvider: 'email' | 'google' | 'mixed';
  isActive: boolean;
  createdAt: string;
}

// Authentication response
interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

// Registration payload
interface RegisterRequest {
  name: string;
  email: string;
  password: string;
}

// Login payload
interface LoginRequest {
  email: string;
  password: string;
}

// Auth context state
interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}
```

## Data Validation Matrix

| Field | Frontend Validation | Backend Validation | Database Constraint |
|-------|-------------------|-------------------|-------------------|
| email | Email format, required | EmailStr (Pydantic), unique check | VARCHAR(254), UNIQUE, NOT NULL |
| password | Min 8 chars, required | Min 8 chars, hash with bcrypt | VARCHAR(255), nullable |
| name | Min 2 chars, max 100, required | Min 2, max 100 chars | VARCHAR(100), NOT NULL |
| user_id | UUID format | UUID validation | UUID, PRIMARY KEY |

## Performance Considerations

**Indexing Strategy**:
- Primary index on `users.email` (unique constraint + login queries)
- Partial index on `users.is_active` for active users only
- Composite index on `oauth_profiles(provider, provider_user_id)` for OAuth lookups

**Query Optimization**:
- User lookup by email: O(log n) with B-tree index
- JWT validation: In-memory, no DB query needed
- OAuth profile lookup: Single query with JOIN to users table

**Scaling Considerations**:
- UUID primary keys prevent hotspots in distributed scenarios
- Soft delete via `is_active` preserves referential integrity
- JWT tokens avoid session storage, enable horizontal scaling
- Separate OAuth profiles table allows multiple providers per user

## Migration Strategy

**Phase 1**: Core users table with email/password auth
**Phase 1.5**: Add OAuth profiles table for Google integration  
**Phase 2**: Add refresh tokens table (future enhancement)
**Phase 3**: Add audit logging table (compliance requirement)

Each phase maintains backward compatibility with previous schema versions.