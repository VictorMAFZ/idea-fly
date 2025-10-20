/**
 * useAuth Hook for IdeaFly Authentication System.
 * 
 * Custom React hook that provides authentication functionality to components.
 * Wraps authService and AuthContext to provide a clean interface for:
 * - User registration
 * - Login/logout
 * - Authentication state management
 * - Error handling
 * - Loading states
 */

'use client';

import { useContext, useCallback } from 'react';
import AuthContext from '../contexts/AuthContext';
import { authService } from '../services/authService';
import { 
  RegisterRequest, 
  LoginRequest, 
  GoogleOAuthRequest,
  AuthContextType,
  User 
} from '../types/auth';

// ============================================================================
// HOOK INTERFACE
// ============================================================================

/**
 * Return type for useAuth hook.
 * Extends AuthContextType with additional convenience methods.
 */
export interface UseAuthReturn extends AuthContextType {
  /** Register a new user account with authService integration */
  registerWithService: (data: RegisterRequest) => Promise<void>;
  /** Login with email and password using authService */
  loginWithService: (data: LoginRequest) => Promise<void>;
  /** Login with Google OAuth using authService */
  loginWithGoogleService: (data: GoogleOAuthRequest) => Promise<void>;
  /** Logout current user using authService */
  logoutWithService: () => Promise<void>;
  /** Refresh current user data using authService */
  refreshUserProfile: () => Promise<void>;
}

// ============================================================================
// HOOK IMPLEMENTATION
// ============================================================================

/**
 * Custom hook for authentication operations.
 * 
 * Provides a clean interface for components to interact with the authentication
 * system without directly dealing with the AuthContext or authService.
 * 
 * @returns Object with authentication state and methods
 * 
 * @example
 * ```tsx
 * function LoginForm() {
 *   const { loginWithService, loading, error, clearError } = useAuth();
 *   
 *   const handleSubmit = async (data: LoginRequest) => {
 *     clearError();
 *     try {
 *       await loginWithService(data);
 *       // User is now logged in
 *     } catch (err) {
 *       // Error is handled automatically by the hook
 *     }
 *   };
 *   
 *   return null; // Component implementation
 * }
 * ```
 */
export function useAuth(): UseAuthReturn {
  // Get authentication context
  const context = useContext(AuthContext);
  
  if (!context) {
    throw new Error(
      'useAuth must be used within an AuthProvider. ' +
      'Make sure to wrap your component with <AuthProvider>.'
    );
  }

  const {
    user,
    token,
    status,
    loading,
    error,
    tokenExpiry,
    register,
    login,
    loginWithGoogle,
    logout,
    refreshUser,
    clearError,
    isAuthenticated,
    isTokenExpired,
  } = context;

  // ============================================================================
  // REGISTRATION WITH SERVICE INTEGRATION
  // ============================================================================

  /**
   * Register a new user account using authService.
   * Integrates with backend API and updates context state.
   * 
   * @param data - Registration form data
   * @throws Will throw an error if registration fails
   */
  const registerWithService = useCallback(async (data: RegisterRequest): Promise<void> => {
    try {
      // Call authentication service
      const response = await authService.register(data);
      
      if (response.success && response.data) {
        // Use context's register method which handles state management
        await register(data);
      } else {
        const errorMessage = response.error?.message || 'Registration failed. Please try again.';
        throw new Error(errorMessage);
      }
      
    } catch (error) {
      // Error is handled by the context's register method
      throw error;
    }
  }, [register]);

  // ============================================================================
  // LOGIN WITH SERVICE INTEGRATION
  // ============================================================================

  /**
   * Login with email and password using authService.
   * Integrates with backend API and updates context state.
   * 
   * @param data - Login form data
   * @throws Will throw an error if login fails
   */
  const loginWithService = useCallback(async (data: LoginRequest): Promise<void> => {
    try {
      // Call authentication service
      const response = await authService.login(data);
      
      if (response.success && response.data) {
        // Use context's login method which handles state management
        await login(data);
      } else {
        const errorMessage = response.error?.message || 'Login failed. Please check your credentials.';
        throw new Error(errorMessage);
      }
      
    } catch (error) {
      // Error is handled by the context's login method
      throw error;
    }
  }, [login]);

  // ============================================================================
  // GOOGLE OAUTH WITH SERVICE INTEGRATION
  // ============================================================================

  /**
   * Login with Google OAuth using authService.
   * Integrates with backend API and updates context state.
   * 
   * @param data - Google OAuth callback data
   * @throws Will throw an error if OAuth login fails
   */
  const loginWithGoogleService = useCallback(async (data: GoogleOAuthRequest): Promise<void> => {
    try {
      // Call authentication service
      const response = await authService.googleCallback(data);
      
      if (response.success && response.data) {
        // Use context's Google login method which handles state management
        await loginWithGoogle(data);
      } else {
        const errorMessage = response.error?.message || 'Google login failed. Please try again.';
        throw new Error(errorMessage);
      }
      
    } catch (error) {
      // Error is handled by the context's loginWithGoogle method
      throw error;
    }
  }, [loginWithGoogle]);

  // ============================================================================
  // LOGOUT WITH SERVICE INTEGRATION
  // ============================================================================

  /**
   * Logout current user using authService.
   * Integrates with backend API and updates context state.
   * 
   * @throws Will throw an error if logout fails
   */
  const logoutWithService = useCallback(async (): Promise<void> => {
    try {
      // Call authentication service (may fail if token expired - that's OK)
      try {
        await authService.logout();
      } catch (logoutError) {
        // Ignore logout service errors - still clear local state
        console.warn('Logout service call failed:', logoutError);
      }
      
      // Always use context logout to clear local state
      await logout();
      
    } catch (error) {
      // Context logout should not fail, but handle just in case
      throw error;
    }
  }, [logout]);

  // ============================================================================
  // USER REFRESH WITH SERVICE INTEGRATION
  // ============================================================================

  /**
   * Refresh current user data from server using authService.
   * Integrates with backend API and updates context state.
   * 
   * @throws Will throw an error if refresh fails
   */
  const refreshUserProfile = useCallback(async (): Promise<void> => {
    try {
      // Ensure user is authenticated
      if (!isAuthenticated() || !token) {
        throw new Error('User not authenticated');
      }

      // Call authentication service
      const response = await authService.getUserProfile();
      
      if (response.success && response.data) {
        // Use context's refresh method to update state
        await refreshUser();
      } else {
        const errorMessage = response.error?.message || 'Failed to refresh user data.';
        throw new Error(errorMessage);
      }
      
    } catch (error) {
      // Error is handled by the context's refreshUser method
      throw error;
    }
  }, [isAuthenticated, token, refreshUser]);

  // ============================================================================
  // RETURN HOOK INTERFACE
  // ============================================================================

  return {
    // Authentication state from context
    user,
    token,
    status,
    loading,
    error,
    tokenExpiry,
    
    // Context methods (original interface)
    register,
    login,
    loginWithGoogle,
    logout,
    refreshUser,
    clearError,
    isAuthenticated,
    isTokenExpired,
    
    // Enhanced methods with service integration
    registerWithService,
    loginWithService,
    loginWithGoogleService,
    logoutWithService,
    refreshUserProfile,
  };
}

// ============================================================================
// CONVENIENCE HOOKS
// ============================================================================

/**
 * Hook for accessing just the authentication state.
 * Useful when you only need to read auth state without methods.
 * 
 * @returns Authentication state only
 */
export function useAuthState() {
  const { user, status, loading, error, tokenExpiry, isAuthenticated } = useAuth();
  
  return {
    user,
    status,
    loading,
    error,
    tokenExpiry,
    isAuthenticated: isAuthenticated(),
  };
}

/**
 * Hook for accessing just the current user.
 * Useful for components that only need user data.
 * 
 * @returns Current user or null
 */
export function useCurrentUser(): User | null {
  const { user } = useAuth();
  return user;
}

/**
 * Hook for checking if user is authenticated.
 * Useful for conditional rendering.
 * 
 * @returns Boolean indicating if user is authenticated
 */
export function useIsAuthenticated(): boolean {
  const { isAuthenticated } = useAuth();
  return isAuthenticated();
}

export default useAuth;