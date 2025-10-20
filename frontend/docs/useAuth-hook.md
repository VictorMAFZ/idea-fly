# useAuth Hook Documentation

## Overview

The `useAuth` hook provides a centralized interface for authentication operations in the IdeaFly application. It wraps both the `AuthContext` and `authService` to provide a clean, type-safe API for components.

## Features

- ✅ **Full Authentication Flow**: Registration, login, logout, and user refresh
- ✅ **Service Integration**: Wraps authService for API communication
- ✅ **State Management**: Integrates with AuthContext for global state
- ✅ **Error Handling**: Comprehensive error handling with user-friendly messages
- ✅ **Loading States**: Built-in loading indicators for async operations
- ✅ **TypeScript**: Full type safety with detailed interfaces
- ✅ **Convenience Hooks**: Additional utility hooks for common patterns

## Basic Usage

```tsx
import { useAuth } from '../hooks/useAuth';

function MyComponent() {
  const { 
    user, 
    loading, 
    error,
    registerWithService,
    loginWithService,
    logoutWithService,
    clearError 
  } = useAuth();

  const handleRegister = async (data) => {
    try {
      await registerWithService(data);
      // User is now registered and logged in
    } catch (err) {
      // Error is automatically set in state
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  
  return user ? (
    <div>Welcome, {user.name}!</div>
  ) : (
    <div>Please log in</div>
  );
}
```

## API Reference

### Main Hook: `useAuth()`

Returns `UseAuthReturn` interface with:

#### State Properties
- `user: User | null` - Current authenticated user
- `token: string | null` - JWT access token
- `status: AuthStatus` - Authentication status enum
- `loading: boolean` - Loading state for async operations
- `error: string | null` - Current error message
- `tokenExpiry: number | null` - Token expiration timestamp

#### Authentication Methods
- `registerWithService(data: RegisterRequest): Promise<void>` - Register new user
- `loginWithService(data: LoginRequest): Promise<void>` - Login with email/password
- `loginWithGoogleService(data: GoogleOAuthRequest): Promise<void>` - Login with Google
- `logoutWithService(): Promise<void>` - Logout current user
- `refreshUserProfile(): Promise<void>` - Refresh user data from server

#### Context Methods (Advanced)
- `register(data: RegisterRequest): Promise<void>` - Direct context register
- `login(data: LoginRequest): Promise<void>` - Direct context login
- `loginWithGoogle(data: GoogleOAuthRequest): Promise<void>` - Direct context Google login
- `logout(): Promise<void>` - Direct context logout
- `refreshUser(): Promise<void>` - Direct context refresh
- `clearError(): void` - Clear error state
- `isAuthenticated(): boolean` - Check if user is authenticated
- `isTokenExpired(): boolean` - Check if token is expired

### Convenience Hooks

#### `useAuthState()`
Returns only the authentication state (no methods):
```tsx
const { user, status, loading, error, isAuthenticated } = useAuthState();
```

#### `useCurrentUser()`
Returns just the current user:
```tsx
const user = useCurrentUser(); // User | null
```

#### `useIsAuthenticated()`
Returns authentication status:
```tsx
const isAuthenticated = useIsAuthenticated(); // boolean
```

## Usage Patterns

### Registration Form
```tsx
function RegisterForm() {
  const { registerWithService, loading, error, clearError } = useAuth();
  
  const handleSubmit = async (formData) => {
    clearError(); // Clear any previous errors
    try {
      await registerWithService({
        name: formData.name,
        email: formData.email,
        password: formData.password
      });
      // Success - user is now registered and logged in
      router.push('/dashboard');
    } catch (err) {
      // Error is automatically set in hook state
      console.error('Registration failed:', err);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {error && <div className="error">{error}</div>}
      {/* form fields */}
      <button type="submit" disabled={loading}>
        {loading ? 'Registering...' : 'Register'}
      </button>
    </form>
  );
}
```

### Login Form
```tsx
function LoginForm() {
  const { loginWithService, loading, error, clearError } = useAuth();
  
  const handleSubmit = async (formData) => {
    clearError();
    try {
      await loginWithService({
        email: formData.email,
        password: formData.password
      });
      router.push('/dashboard');
    } catch (err) {
      console.error('Login failed:', err);
    }
  };

  // Similar form implementation...
}
```

### Protected Component
```tsx
function ProtectedComponent() {
  const { user, loading } = useAuth();
  
  if (loading) return <Spinner />;
  if (!user) return <LoginPrompt />;
  
  return <Dashboard user={user} />;
}
```

### Navigation Bar
```tsx
function NavBar() {
  const { user, logoutWithService } = useAuth();
  
  const handleLogout = async () => {
    try {
      await logoutWithService();
      router.push('/');
    } catch (err) {
      console.error('Logout failed:', err);
    }
  };

  return (
    <nav>
      {user ? (
        <div>
          <span>Welcome, {user.name}</span>
          <button onClick={handleLogout}>Logout</button>
        </div>
      ) : (
        <Link href="/login">Login</Link>
      )}
    </nav>
  );
}
```

### Conditional Rendering
```tsx
function ConditionalContent() {
  const isAuthenticated = useIsAuthenticated();
  const user = useCurrentUser();
  
  return (
    <div>
      {isAuthenticated ? (
        <UserDashboard user={user} />
      ) : (
        <PublicLanding />
      )}
    </div>
  );
}
```

## Error Handling

The hook provides automatic error handling:

1. **Service Errors**: API errors are caught and set in state
2. **Context Errors**: Context operations handle their own errors
3. **Network Errors**: HTTP errors are handled by the service layer
4. **Token Expiry**: Automatic logout on token expiration

Errors are accessible via the `error` property and can be cleared with `clearError()`.

## Integration Notes

### Service Integration
- Uses `authService.register()` for registration
- Uses `authService.login()` for login
- Uses `authService.googleCallback()` for OAuth
- Uses `authService.logout()` for logout
- Uses `authService.getUserProfile()` for user refresh

### Context Integration
- Wraps `AuthContext` for state management
- Provides direct access to context methods
- Handles loading states and error propagation
- Manages token persistence and expiration

### Type Safety
- All methods have proper TypeScript types
- Request/response interfaces match backend contracts
- Comprehensive error typing with specific error types

## Next Steps

After T023 completion, the hook is ready for:
- **T024**: Registration page implementation
- **T025**: AuthContext integration updates
- **T029-T033**: Login flow implementation
- **T039-T047**: Google OAuth integration

The hook provides the foundation for all authentication operations in the application.