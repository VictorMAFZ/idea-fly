/**
 * Authentication Context for IdeaFly Application.
 * 
 * Provides centralized authentication state management using React Context.
 * Handles login, logout, registration, token persistence, and session management.
 */

'use client';

import React, { 
  createContext, 
  useContext, 
  useReducer, 
  useEffect, 
  useCallback,
  useMemo,
  ReactNode 
} from 'react';

import { 
  AuthContextType,
  AuthState,
  AuthStatus,
  User,
  RegisterRequest,
  LoginRequest,
  GoogleOAuthRequest,
  AuthResponse,
  TokenType,
  AuthProvider as AuthProviderEnum,
} from '../types/auth';

// ============================================================================
// CONSTANTS
// ============================================================================

/** Local storage key for persisting auth token */
const AUTH_TOKEN_KEY = 'ideafly_auth_token';
/** Local storage key for persisting user data */
const AUTH_USER_KEY = 'ideafly_auth_user';
/** Local storage key for token expiry */
const AUTH_EXPIRY_KEY = 'ideafly_auth_expiry';

/** Default token validity duration (24 hours in milliseconds) */
const DEFAULT_TOKEN_DURATION = 24 * 60 * 60 * 1000;

// ============================================================================
// INITIAL STATE
// ============================================================================

/** Initial authentication state */
const initialAuthState: AuthState = {
  status: AuthStatus.IDLE,
  user: null,
  token: null,
  tokenExpiry: null,
  error: null,
  loading: false,
};

// ============================================================================
// ACTION TYPES
// ============================================================================

type AuthActionType =
  | 'SET_LOADING'
  | 'SET_ERROR'
  | 'CLEAR_ERROR'
  | 'LOGIN_SUCCESS'
  | 'LOGOUT'
  | 'REFRESH_USER_SUCCESS'
  | 'TOKEN_EXPIRED'
  | 'HYDRATE_FROM_STORAGE';

interface AuthAction {
  type: AuthActionType;
  payload?: any;
}

// ============================================================================
// REDUCER
// ============================================================================

function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'SET_LOADING':
      return {
        ...state,
        loading: action.payload,
        error: null, // Clear error when starting new operation
      };

    case 'SET_ERROR':
      return {
        ...state,
        loading: false,
        status: AuthStatus.ERROR,
        error: action.payload,
      };

    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null,
        status: state.user ? AuthStatus.AUTHENTICATED : AuthStatus.UNAUTHENTICATED,
      };

    case 'LOGIN_SUCCESS':
      const { user, token, tokenExpiry } = action.payload;
      return {
        ...state,
        loading: false,
        status: AuthStatus.AUTHENTICATED,
        user,
        token,
        tokenExpiry,
        error: null,
      };

    case 'LOGOUT':
      return {
        ...initialAuthState,
        status: AuthStatus.UNAUTHENTICATED,
      };

    case 'REFRESH_USER_SUCCESS':
      return {
        ...state,
        user: action.payload,
        error: null,
      };

    case 'TOKEN_EXPIRED':
      return {
        ...initialAuthState,
        status: AuthStatus.UNAUTHENTICATED,
        error: 'Your session has expired. Please login again.',
      };

    case 'HYDRATE_FROM_STORAGE':
      const { user: storedUser, token: storedToken, tokenExpiry: storedExpiry } = action.payload;
      
      // Check if token is expired
      const now = Date.now();
      const isExpired = !storedExpiry || now >= storedExpiry;
      
      if (isExpired) {
        return {
          ...initialAuthState,
          status: AuthStatus.UNAUTHENTICATED,
        };
      }
      
      return {
        ...state,
        status: AuthStatus.AUTHENTICATED,
        user: storedUser,
        token: storedToken,
        tokenExpiry: storedExpiry,
        loading: false,
      };

    default:
      return state;
  }
}

// ============================================================================
// STORAGE UTILITIES
// ============================================================================

/**
 * Save authentication data to localStorage.
 */
function saveAuthToStorage(user: User, token: string, tokenExpiry: number): void {
  try {
    localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user));
    localStorage.setItem(AUTH_TOKEN_KEY, token);
    localStorage.setItem(AUTH_EXPIRY_KEY, tokenExpiry.toString());
  } catch (error) {
    console.error('Failed to save auth data to storage:', error);
  }
}

/**
 * Load authentication data from localStorage.
 */
function loadAuthFromStorage(): { user: User | null; token: string | null; tokenExpiry: number | null } {
  try {
    const userStr = localStorage.getItem(AUTH_USER_KEY);
    const token = localStorage.getItem(AUTH_TOKEN_KEY);
    const expiryStr = localStorage.getItem(AUTH_EXPIRY_KEY);
    
    const user = userStr ? JSON.parse(userStr) : null;
    const tokenExpiry = expiryStr ? parseInt(expiryStr, 10) : null;
    
    return { user, token, tokenExpiry };
  } catch (error) {
    console.error('Failed to load auth data from storage:', error);
    return { user: null, token: null, tokenExpiry: null };
  }
}

/**
 * Clear authentication data from localStorage.
 */
function clearAuthFromStorage(): void {
  try {
    localStorage.removeItem(AUTH_USER_KEY);
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(AUTH_EXPIRY_KEY);
  } catch (error) {
    console.error('Failed to clear auth data from storage:', error);
  }
}

// ============================================================================
// CONTEXT CREATION
// ============================================================================

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// ============================================================================
// PROVIDER COMPONENT
// ============================================================================

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [state, dispatch] = useReducer(authReducer, initialAuthState);

  // ========================================
  // TOKEN MANAGEMENT
  // ========================================

  const isTokenExpired = useCallback((): boolean => {
    if (!state.tokenExpiry) return true;
    return Date.now() >= state.tokenExpiry;
  }, [state.tokenExpiry]);

  const isAuthenticated = useCallback((): boolean => {
    return state.status === AuthStatus.AUTHENTICATED && 
           state.user !== null && 
           state.token !== null &&
           !isTokenExpired();
  }, [state.status, state.user, state.token, isTokenExpired]);

  // ========================================
  // AUTH ACTIONS
  // ========================================

  const handleAuthSuccess = useCallback((authResponse: AuthResponse, user: User): void => {
    const { access_token, expires_in } = authResponse;
    const tokenExpiry = Date.now() + (expires_in * 1000); // expires_in is in seconds
    
    // Save to storage
    saveAuthToStorage(user, access_token, tokenExpiry);
    
    // Update state
    dispatch({
      type: 'LOGIN_SUCCESS',
      payload: {
        user,
        token: access_token,
        tokenExpiry,
      },
    });
  }, []);

  const register = useCallback(async (request: RegisterRequest): Promise<void> => {
    dispatch({ type: 'SET_LOADING', payload: true });
    
    try {
      // TODO: Replace with actual API call when httpClient is implemented
      // This is a placeholder until T014 is completed
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API call
      
      // Mock successful registration response
      const mockAuthResponse: AuthResponse = {
        access_token: `mock_token_${Date.now()}`,
        token_type: TokenType.BEARER,
        expires_in: 86400, // 24 hours in seconds
      };
      
      const mockUser: User = {
        id: `user_${Date.now()}`,
        name: request.name,
        email: request.email,
        auth_provider: AuthProviderEnum.EMAIL,
        is_active: true,
        created_at: new Date().toISOString(),
      };
      
      handleAuthSuccess(mockAuthResponse, mockUser);
    } catch (error: any) {
      dispatch({ 
        type: 'SET_ERROR', 
        payload: error?.message || 'Registration failed. Please try again.' 
      });
      throw error;
    }
  }, [handleAuthSuccess]);

  const login = useCallback(async (request: LoginRequest): Promise<void> => {
    dispatch({ type: 'SET_LOADING', payload: true });
    
    try {
      // TODO: Replace with actual API call when httpClient is implemented
      await new Promise(resolve => setTimeout(resolve, 800));
      
      // Mock successful login response
      const mockAuthResponse: AuthResponse = {
        access_token: `mock_token_${Date.now()}`,
        token_type: TokenType.BEARER,
        expires_in: 86400, // 24 hours in seconds
      };
      
      const mockUser: User = {
        id: `user_${Date.now()}`,
        name: 'Mock User',
        email: request.email,
        auth_provider: AuthProviderEnum.EMAIL,
        is_active: true,
        created_at: new Date().toISOString(),
      };
      
      handleAuthSuccess(mockAuthResponse, mockUser);
    } catch (error: any) {
      dispatch({ 
        type: 'SET_ERROR', 
        payload: error?.message || 'Login failed. Please check your credentials.' 
      });
      throw error;
    }
  }, [handleAuthSuccess]);

  const loginWithGoogle = useCallback(async (request: GoogleOAuthRequest): Promise<void> => {
    dispatch({ type: 'SET_LOADING', payload: true });
    
    try {
      // TODO: Replace with actual Google OAuth flow when implemented
      await new Promise(resolve => setTimeout(resolve, 1200));
      
      // Mock successful Google OAuth response
      const mockAuthResponse: AuthResponse = {
        access_token: `google_token_${Date.now()}`,
        token_type: TokenType.BEARER,
        expires_in: 86400, // 24 hours in seconds
      };
      
      const mockUser: User = {
        id: `google_user_${Date.now()}`,
        name: 'Google User',
        email: 'user@google.com',
        auth_provider: AuthProviderEnum.GOOGLE,
        is_active: true,
        created_at: new Date().toISOString(),
      };
      
      handleAuthSuccess(mockAuthResponse, mockUser);
    } catch (error: any) {
      dispatch({ 
        type: 'SET_ERROR', 
        payload: error?.message || 'Google login failed. Please try again.' 
      });
      throw error;
    }
  }, [handleAuthSuccess]);

  const logout = useCallback(async (): Promise<void> => {
    dispatch({ type: 'SET_LOADING', payload: true });
    
    try {
      // TODO: Call logout endpoint when implemented
      await new Promise(resolve => setTimeout(resolve, 300));
      
      // Clear storage
      clearAuthFromStorage();
      
      // Update state
      dispatch({ type: 'LOGOUT' });
    } catch (error: any) {
      // Even if logout API fails, clear local state
      clearAuthFromStorage();
      dispatch({ type: 'LOGOUT' });
      console.error('Logout API call failed, but local session cleared:', error);
    }
  }, []);

  const refreshUser = useCallback(async (): Promise<void> => {
    if (!state.token || isTokenExpired()) {
      dispatch({ type: 'TOKEN_EXPIRED' });
      return;
    }
    
    dispatch({ type: 'SET_LOADING', payload: true });
    
    try {
      // TODO: Call /users/me endpoint when implemented
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // For now, keep existing user data
      dispatch({ 
        type: 'REFRESH_USER_SUCCESS', 
        payload: state.user 
      });
    } catch (error: any) {
      dispatch({ 
        type: 'SET_ERROR', 
        payload: error?.message || 'Failed to refresh user profile.' 
      });
    }
  }, [state.token, state.user, isTokenExpired]);

  const clearError = useCallback((): void => {
    dispatch({ type: 'CLEAR_ERROR' });
  }, []);

  // ========================================
  // INITIALIZATION & PERSISTENCE
  // ========================================

  // Hydrate from localStorage on mount
  useEffect(() => {
    const stored = loadAuthFromStorage();
    if (stored.user && stored.token && stored.tokenExpiry) {
      dispatch({
        type: 'HYDRATE_FROM_STORAGE',
        payload: stored,
      });
    } else {
      dispatch({ type: 'LOGOUT' }); // Ensure clean unauthenticated state
    }
  }, []);

  // Auto-logout on token expiration
  useEffect(() => {
    if (state.tokenExpiry && state.status === AuthStatus.AUTHENTICATED) {
      const timeUntilExpiry = state.tokenExpiry - Date.now();
      
      if (timeUntilExpiry <= 0) {
        // Token already expired
        dispatch({ type: 'TOKEN_EXPIRED' });
        clearAuthFromStorage();
      } else {
        // Set timeout for future expiration
        const timeoutId = setTimeout(() => {
          dispatch({ type: 'TOKEN_EXPIRED' });
          clearAuthFromStorage();
        }, timeUntilExpiry);
        
        return () => clearTimeout(timeoutId);
      }
    }
  }, [state.tokenExpiry, state.status]);

  // ========================================
  // CONTEXT VALUE
  // ========================================

  const contextValue = useMemo((): AuthContextType => ({
    // State
    status: state.status,
    user: state.user,
    token: state.token,
    tokenExpiry: state.tokenExpiry,
    error: state.error,
    loading: state.loading,
    
    // Actions
    register,
    login,
    loginWithGoogle,
    logout,
    refreshUser,
    clearError,
    isAuthenticated,
    isTokenExpired,
  }), [
    state.status,
    state.user,
    state.token,
    state.tokenExpiry,
    state.error,
    state.loading,
    register,
    login,
    loginWithGoogle,
    logout,
    refreshUser,
    clearError,
    isAuthenticated,
    isTokenExpired,
  ]);

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}

// ============================================================================
// HOOK FOR CONSUMING CONTEXT
// ============================================================================

/**
 * Hook to access authentication context.
 * Must be used within AuthProvider.
 * 
 * @returns AuthContextType - Authentication state and actions
 * 
 * @example
 * ```tsx
 * function LoginButton() {
 *   const { login, loading, isAuthenticated } = useAuth();
 *   
 *   const handleLogin = async () => {
 *     try {
 *       await login({ email: 'user@example.com', password: 'password' });
 *     } catch (error) {
 *       console.error('Login failed:', error);
 *     }
 *   };
 *   
 *   if (isAuthenticated()) {
 *     return <span>Already logged in</span>;
 *   }
 *   
 *   return (
 *     <button onClick={handleLogin} disabled={loading}>
 *       {loading ? 'Logging in...' : 'Login'}
 *     </button>
 *   );
 * }
 * ```
 */
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error(
      'useAuth must be used within an AuthProvider. ' +
      'Make sure your component is wrapped with <AuthProvider>.'
    );
  }
  
  return context;
}

// ============================================================================
// UTILITY HOOKS
// ============================================================================

/**
 * Hook that returns whether the user is currently authenticated.
 */
export function useIsAuthenticated(): boolean {
  const { isAuthenticated } = useAuth();
  return isAuthenticated();
}

/**
 * Hook that returns the current user, or null if not authenticated.
 */
export function useCurrentUser(): User | null {
  const { user, isAuthenticated } = useAuth();
  return isAuthenticated() ? user : null;
}

/**
 * Hook that triggers logout and provides logout state.
 */
export function useLogout(): {
  logout: () => Promise<void>;
  isLoggingOut: boolean;
} {
  const { logout, loading } = useAuth();
  
  return {
    logout,
    isLoggingOut: loading,
  };
}

// ============================================================================
// EXPORTS
// ============================================================================

export default AuthContext;
export type { AuthProviderProps };