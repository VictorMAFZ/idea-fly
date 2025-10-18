# Research: Sistema de Autenticación de Usuarios

**Phase**: 0 - Outline & Research  
**Date**: 2025-10-18  
**Feature**: [Sistema de Autenticación de Usuarios](./spec.md)

## Research Tasks Completed

### 1. JWT Implementation Best Practices for FastAPI

**Decision**: Usar `python-jose[cryptography]` con algoritmo HS256 para tokens JWT

**Rationale**: 
- `python-jose` es la librería recomendada oficialmente por FastAPI para JWT
- Soporte nativo para múltiples algoritmos criptográficos
- Excelente integración con Pydantic para validación de claims
- Amplia documentación y comunidad activa

**Alternatives Considered**:
- `PyJWT`: Más básica, requiere más configuración manual
- `authlib`: Más compleja, overhead innecesario para nuestros requisitos
- `cryptography` directamente: Demasiado low-level, aumenta complejidad

**Implementation Details**:
- Secret key gestionada via variable de entorno `JWT_SECRET_KEY`
- Token expiration: 24 horas (configurable)
- Claims incluidos: user_id, email, exp, iat
- Algoritmo: HS256 (simétrico, adecuado para monolito)

### 2. Password Hashing Strategy

**Decision**: Usar `passlib[bcrypt]` con configuración CryptContext

**Rationale**:
- bcrypt es el estándar actual para hashing de contraseñas
- Resistente a ataques de fuerza bruta y rainbow tables
- Costo computacional configurable (rounds)
- Soporte nativo en passlib con integración FastAPI

**Alternatives Considered**:
- `scrypt`: Más moderno pero menos compatible
- `argon2`: Excelente seguridad pero overhead de memoria
- `pbkdf2`: Estándar más antiguo, menos resistente

**Implementation Details**:
- Configuración: bcrypt con 12 rounds (balance seguridad/performance)
- Salt automático por bcrypt
- Validación de contraseñas con time-constant comparison

### 3. Google OAuth 2.0 Integration Pattern

**Decision**: Implementar Authorization Code Flow con PKCE

**Rationale**:
- Flow más seguro para aplicaciones públicas (SPA)
- PKCE previene ataques de intercepción de código
- Recomendado por Google y OAuth 2.1 spec
- Compatible con `@react-oauth/google` en frontend

**Alternatives Considered**:
- Implicit Flow: Deprecado por problemas de seguridad
- Client Credentials: No aplicable para usuarios finales
- Device Code Flow: Para dispositivos sin navegador

**Implementation Details**:
- Frontend: `@react-oauth/google` maneja PKCE automáticamente
- Backend: Endpoint `/auth/google/callback` intercambia code por user info
- Scopes requeridos: `openid`, `profile`, `email`
- User info obtenido via Google People API

### 4. Session Management Architecture

**Decision**: JWT stateless con refresh token opcional (Phase 2)

**Rationale**:
- Stateless permite escalado horizontal sin sticky sessions
- Reduce carga en base de datos para validación
- Compatible con arquitectura microservicios futura
- Simplicidad para MVP (sin refresh tokens inicialmente)

**Alternatives Considered**:
- Server-side sessions: Requiere Redis/sticky sessions
- Refresh tokens: Añade complejidad, dejado para Phase 2
- Database sessions: No escala, alto overhead

**Implementation Details**:
- JWT almacenado en localStorage (frontend)
- Axios interceptor añade Bearer token automáticamente
- Middleware Next.js valida token para rutas protegidas
- Logout limpia localStorage (no blacklist de tokens para MVP)

### 5. Database Schema Design

**Decision**: Tabla `users` con OAuth profile separado opcional

**Rationale**:
- Flexibilidad para usuarios con múltiples métodos de auth
- Normalización de datos de perfil OAuth
- Escalabilidad para futuros proveedores OAuth
- Cumple con principios Clean Architecture

**Alternatives Considered**:
- Single table con campos OAuth opcionales: Menos normalizado
- Separate tables por provider: Duplicación excesiva para MVP
- JSON fields para OAuth data: Menos queryable

**Implementation Details**:
```sql
users:
- id (UUID, PK)
- email (VARCHAR, UNIQUE)
- name (VARCHAR)
- hashed_password (VARCHAR, NULLABLE)
- is_active (BOOLEAN)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

oauth_profiles (Phase 1.5):
- id (UUID, PK)
- user_id (UUID, FK)
- provider (ENUM: google, facebook, etc)
- provider_user_id (VARCHAR)
- provider_email (VARCHAR)
```

### 6. Frontend State Management Pattern

**Decision**: React Context + Custom Hooks para auth state

**Rationale**:
- Simplicidad: no requiere Redux para auth únicamente
- Performance: Context + hooks evita re-renders innecesarios
- TypeScript friendly: Tipos bien definidos
- Escalable: fácil migración a Zustand si crece complejidad

**Alternatives Considered**:
- Redux Toolkit: Overhead excesivo para auth state únicamente
- Zustand: Excelente, pero Context suficiente para MVP
- SWR/React Query: Para data fetching, no auth state

**Implementation Details**:
- `AuthContext` provee: user, isAuthenticated, login, logout, register
- `useAuth` hook encapsula lógica de auth
- Persistent state via localStorage con hidratación server-side
- Loading states para UX durante auth operations

### 7. Error Handling Strategy

**Decision**: Centralizada con códigos de error consistentes

**Rationale**:
- UX consistente con mensajes de error claros
- Facilita debugging y monitoring
- Internacionalización futura simplificada
- Cumple principio de Diseño Centrado en el Usuario

**Implementation Details**:
- Backend: Custom exception classes con HTTP status codes
- Frontend: Error boundary + toast notifications
- Códigos de error: AUTH_001 (invalid credentials), AUTH_002 (email exists), etc.
- Logging estructurado para debugging

## Validation & Next Steps

✅ **All technical unknowns resolved**
✅ **Best practices research completed**  
✅ **Architecture decisions documented**
✅ **Ready for Phase 1: Design & Contracts**

**Dependencies Confirmed**:
- Google OAuth API credentials (ENV configuration required)
- PostgreSQL database setup
- JWT secret key generation
- CORS configuration for frontend-backend communication

**Performance Validations**:
- bcrypt 12 rounds: ~100ms per hash (acceptable for registration)
- JWT validation: <5ms (in-memory verification)
- OAuth flow: <5s network dependent (Google SLA)
- Database queries: <50ms with proper indexing (email unique index)