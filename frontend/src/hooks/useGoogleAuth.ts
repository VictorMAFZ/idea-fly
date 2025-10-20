/**
 * useGoogleAuth hook for managing Google OAuth authentication state.
 * 
 * This hook provides a clean interface for Google OAuth authentication,
 * including state management, error handling, and integration with the
 * application's authentication context.
 * 
 * Features:
 * - State management for OAuth flow
 * - Error handling and recovery
 * - Integration with AuthContext
 * - TypeScript support
 * - Loading states
 */

'use client';

import { useState, useCallback } from 'react';
import { useAuth } from './useAuth';
import { authService } from '../services/authService';

interface GoogleAuthState {
  /** Whether Google OAuth is currently processing */
  loading: boolean;
  /** Current error message, if any */
  error: string | null;
  /** Whether Google OAuth is available */
  isAvailable: boolean;
}

interface GoogleAuthActions {
  /** Sign in with Google OAuth access token */
  signInWithGoogle: (accessToken: string) => Promise<void>;
  /** Clear any existing errors */
  clearError: () => void;
  /** Reset the hook state */
  reset: () => void;
}

export interface UseGoogleAuthReturn extends GoogleAuthState, GoogleAuthActions {}

/**
 * Hook for managing Google OAuth authentication.
 * 
 * @returns Object containing state and actions for Google OAuth
 * 
 * @example
 * ```tsx
 * function LoginPage() {
 *   const { signInWithGoogle, loading, error } = useGoogleAuth();
 *   
 *   const handleGoogleSuccess = async (token: string) => {
 *     await signInWithGoogle(token);
 *   };
 *   
 *   return (
 *     <GoogleAuthButton 
 *       onSuccess={handleGoogleSuccess}
 *       loading={loading}
 *     />
 *   );
 * }
 * ```
 */
export function useGoogleAuth(): UseGoogleAuthReturn {
  // State management
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isAvailable] = useState(true); // Google OAuth is always available

  // Get auth context for user state management
  const { loginWithGoogleToken } = useAuth();

  /**
   * Sign in with Google OAuth access token.
   * 
   * @param accessToken - Google OAuth access token from the OAuth flow
   * @throws Will throw an error if authentication fails
   */
  const signInWithGoogle = useCallback(async (accessToken: string): Promise<void> => {
    if (!accessToken) {
      const errorMsg = 'Google access token is required';
      setError(errorMsg);
      throw new Error(errorMsg);
    }

    setLoading(true);
    setError(null);

    try {
      // Use the context's loginWithGoogleToken method
      await loginWithGoogleToken(accessToken);
      
      console.log('Google OAuth authentication successful');
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Google authentication failed';
      
      console.error('Google OAuth authentication failed:', err);
      setError(errorMessage);
      
      // Re-throw for component error handling
      throw new Error(errorMessage);
      
    } finally {
      setLoading(false);
    }
  }, [loginWithGoogleToken]);

  /**
   * Clear any existing error state.
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  /**
   * Reset all hook state to initial values.
   */
  const reset = useCallback(() => {
    setLoading(false);
    setError(null);
  }, []);

  return {
    // State
    loading,
    error,
    isAvailable,
    
    // Actions
    signInWithGoogle,
    clearError,
    reset,
  };
}

// Export for backward compatibility
export default useGoogleAuth;