/**
 * Login Page for IdeaFly Authentication System.
 * 
 * Next.js 14 App Router page that implements the T034 task for US2 user story.
 * Provides a complete login flow using LoginForm component and useAuth hook.
 */

'use client';

import React, { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { LoginForm } from '../../components/auth/LoginForm';
import { useAuth } from '../../hooks/useAuth';
import { LoginRequest, AuthStatus } from '../../types/auth';

// ============================================================================
// METADATA AND SEO
// ============================================================================

// Note: Metadata is handled at layout level for App Router

// ============================================================================
// MAIN COMPONENT
// ============================================================================

/**
 * Login page component.
 * 
 * Features:
 * - Uses LoginForm component for form UI and validation
 * - Integrates with useAuth hook for authentication logic
 * - Handles success/error states and navigation
 * - Provides loading feedback and error display
 * - Redirects authenticated users to dashboard
 * - Supports redirect_to query parameter for post-login navigation
 * - Responsive design with proper accessibility
 */
export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { 
    loginWithService, 
    user, 
    loading, 
    error, 
    clearError,
    isAuthenticated,
    status 
  } = useAuth();

  // Local state for page-specific functionality
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [loginError, setLoginError] = useState<string | null>(null);

  // Get redirect destination from query params
  const redirectTo = searchParams.get('redirect_to') || '/dashboard';

  // ============================================================================
  // EFFECTS
  // ============================================================================

  /**
   * Redirect authenticated users to dashboard or specified redirect URL
   */
  useEffect(() => {
    if (isAuthenticated() && user) {
      console.log('User already authenticated, redirecting to:', redirectTo);
      router.push(redirectTo);
    }
  }, [isAuthenticated, user, router, redirectTo]);

  /**
   * Sync auth errors with local state
   */
  useEffect(() => {
    if (error) {
      setLoginError(error);
      setIsSubmitting(false);
    }
  }, [error]);

  /**
   * Clear errors when component unmounts or when user starts typing
   */
  useEffect(() => {
    return () => {
      clearError();
    };
  }, [clearError]);

  // ============================================================================
  // EVENT HANDLERS
  // ============================================================================

  /**
   * Handle form submission
   */
  const handleLogin = async (data: LoginRequest): Promise<void> => {
    try {
      setIsSubmitting(true);
      setLoginError(null);
      clearError();

      console.log('Attempting login for:', data.email);
      
      await loginWithService(data);
      
      console.log('Login successful, redirecting to:', redirectTo);
      // Note: Redirect is handled by useEffect when isAuthenticated becomes true
      
    } catch (err) {
      console.error('Login failed:', err);
      
      // Extract error message for display
      let errorMessage = 'Error de inicio de sesión. Por favor intenta nuevamente.';
      
      if (err instanceof Error) {
        errorMessage = err.message;
      } else if (typeof err === 'string') {
        errorMessage = err;
      }
      
      setLoginError(errorMessage);
      setIsSubmitting(false);
    }
  };

  /**
   * Handle navigation to registration page
   */
  const handleRegisterNavigation = (): void => {
    clearError();
    setLoginError(null);
    
    // Preserve redirect_to when going to registration
    const registerUrl = redirectTo !== '/dashboard' 
      ? `/register?redirect_to=${encodeURIComponent(redirectTo)}`
      : '/register';
      
    router.push(registerUrl);
  };

  /**
   * Handle forgot password functionality
   */
  const handleForgotPassword = (): void => {
    // TODO: Implement forgot password flow in future user story
    console.log('Forgot password clicked - to be implemented');
    alert('La funcionalidad de recuperación de contraseña será implementada próximamente.');
  };

  /**
   * Clear all errors
   */
  const handleClearErrors = (): void => {
    clearError();
    setLoginError(null);
  };

  // ============================================================================
  // DERIVED STATE
  // ============================================================================

  const authStatus = status;
  const isLoading = loading || isSubmitting;
  const displayError = loginError || error;

  // Show loading state for authenticated users being redirected
  if (isAuthenticated() && user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">
            Redirigiendo al dashboard...
          </p>
        </div>
      </div>
    );
  }

  // ============================================================================
  // RENDER
  // ============================================================================

  return (
    <div className="min-h-screen flex flex-col justify-center py-12 sm:px-6 lg:px-8 bg-gray-50 dark:bg-gray-900">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            IdeaFly
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Inicia sesión en tu cuenta
          </p>
        </div>

        {/* Success message from registration */}
        {searchParams.get('registered') === 'true' && (
          <div className="mt-6 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-md">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-green-800 dark:text-green-200">
                  ¡Registro exitoso! Ahora puedes iniciar sesión con tu cuenta.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Login Form */}
        <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
          <div className="bg-white dark:bg-gray-800 py-8 px-4 shadow sm:rounded-lg sm:px-10">
            <LoginForm
              onSubmit={handleLogin}
              authStatus={authStatus}
              error={displayError}
              disabled={isLoading}
              onForgotPassword={handleForgotPassword}
              onRegister={handleRegisterNavigation}
            />

            {/* Clear errors button (debugging) */}
            {displayError && (
              <div className="mt-4 text-center">
                <button
                  onClick={handleClearErrors}
                  className="text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                >
                  Limpiar errores
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Footer Links */}
        <div className="mt-6 text-center">
          <div className="space-y-2">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              ¿No tienes cuenta?{' '}
              <button
                onClick={handleRegisterNavigation}
                className="text-blue-600 hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300 font-medium"
              >
                Regístrate gratis
              </button>
            </p>
            
            <div className="text-xs text-gray-500 dark:text-gray-500">
              <a 
                href="/privacy" 
                className="hover:text-gray-700 dark:hover:text-gray-300"
              >
                Política de Privacidad
              </a>
              {' • '}
              <a 
                href="/terms" 
                className="hover:text-gray-700 dark:hover:text-gray-300"
              >
                Términos de Servicio
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Development Info (only in development) */}
      {process.env.NODE_ENV === 'development' && (
        <div className="fixed bottom-4 right-4 bg-gray-800 text-white p-3 rounded-lg text-xs max-w-sm">
          <div className="font-mono space-y-1">
            <div>Auth Status: {authStatus}</div>
            <div>Loading: {loading ? 'true' : 'false'}</div>
            <div>Submitting: {isSubmitting ? 'true' : 'false'}</div>
            <div>Authenticated: {isAuthenticated() ? 'true' : 'false'}</div>
            <div>User: {user ? user.email : 'null'}</div>
            <div>Redirect To: {redirectTo}</div>
            {displayError && (
              <div className="text-red-400">Error: {displayError}</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

// ============================================================================
// COMPONENT METADATA FOR NEXT.JS
// ============================================================================

/**
 * Page metadata for SEO and browser tab
 * This would be handled by metadata export in the page file for static metadata
 * or generateMetadata function for dynamic metadata
 */
export const metadata = {
  title: 'Iniciar Sesión - IdeaFly',
  description: 'Inicia sesión en tu cuenta de IdeaFly para acceder a tus proyectos y colaboraciones.',
  robots: 'noindex, nofollow', // Prevent indexing of auth pages
};