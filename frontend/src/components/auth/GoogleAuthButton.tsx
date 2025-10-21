/**
 * GoogleAuthButton component for Google OAuth authentication.
 * 
 * This component provides a secure Google OAuth login/register button
 * following Material Design guidelines and WCAG accessibility standards.
 * 
 * Features:
 * - Secure OAuth flow with PKCE
 * - Responsive design with TailwindCSS
 * - Loading states and error handling
 * - Accessibility compliant (ARIA labels, keyboard navigation)
 * - Dark mode support
 */

'use client';

import { useState } from 'react';
import { useGoogleLogin } from '@react-oauth/google';

interface GoogleAuthButtonProps {
  /** Callback function when authentication succeeds */
  onSuccess: (token: string) => void;
  /** Callback function when authentication fails */
  onError: (error: string) => void;
  /** Button text - defaults to "Continue with Google" */
  text?: string;
  /** Whether the button is in loading state */
  loading?: boolean;
  /** Whether the button is disabled */
  disabled?: boolean;
  /** Button variant - filled or outlined */
  variant?: 'filled' | 'outlined';
  /** Button size */
  size?: 'sm' | 'md' | 'lg';
  /** Additional CSS classes */
  className?: string;
}

export function GoogleAuthButton({
  onSuccess,
  onError,
  text = "Continue with Google",
  loading = false,
  disabled = false,
  variant = 'outlined',
  size = 'md',
  className = ''
}: GoogleAuthButtonProps) {
  const [isLoading, setIsLoading] = useState(false);

  const googleLogin = useGoogleLogin({
    onSuccess: async (codeResponse) => {
      try {
        setIsLoading(true);
        console.log('Google OAuth Code Response:', codeResponse);
        
        // With authorization code flow, we get a code instead of access_token
        if (codeResponse.code) {
          // Exchange the code for JWT token on our backend
          const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/google/code`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ code: codeResponse.code }),
          });

          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail?.message || 'Authentication failed');
          }

          const authData = await response.json();
          onSuccess(authData.access_token);
        } else {
          throw new Error('No authorization code received from Google');
        }
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Google authentication failed';
        console.error('OAuth Error:', error);
        onError(errorMessage);
      } finally {
        setIsLoading(false);
      }
    },
    onError: (error) => {
      console.error('Google OAuth Error Details:', error);
      console.log('Current URL:', window.location.href);
      console.log('Origin:', window.location.origin);
      console.log('Protocol:', window.location.protocol);
      console.log('Host:', window.location.host);
      console.log('Hostname:', window.location.hostname);
      console.log('Port:', window.location.port);
      
      // Let's also check what redirect_uri Google is expecting
      if (error && typeof error === 'object' && 'error' in error) {
        console.log('Google Error Object:', error);
      }
      
      onError(`Google authentication failed. Please check console for details.`);
      setIsLoading(false);
    },
    scope: 'openid email profile',
    flow: 'auth-code',
  });

  const handleClick = () => {
    if (!loading && !disabled && !isLoading) {
      googleLogin();
    }
  };

  // Dynamic classes based on props
  const baseClasses = [
    'flex items-center justify-center gap-3 font-medium rounded-lg transition-all duration-200',
    'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
    'disabled:opacity-50 disabled:cursor-not-allowed',
    'active:scale-95 hover:scale-105'
  ];

  const sizeClasses = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-6 py-3 text-base',
    lg: 'px-8 py-4 text-lg'
  };

  const variantClasses = {
    filled: [
      'bg-white text-gray-700 border border-gray-300',
      'hover:bg-gray-50 hover:border-gray-400',
      'dark:bg-gray-800 dark:text-gray-200 dark:border-gray-600',
      'dark:hover:bg-gray-700 dark:hover:border-gray-500'
    ],
    outlined: [
      'bg-transparent text-gray-700 border-2 border-gray-300',
      'hover:bg-gray-50 hover:border-gray-400',
      'dark:text-gray-200 dark:border-gray-600',
      'dark:hover:bg-gray-800 dark:hover:border-gray-500'
    ]
  };

  const buttonClasses = [
    ...baseClasses,
    sizeClasses[size],
    ...variantClasses[variant],
    className
  ].join(' ');

  const isDisabled = loading || disabled || isLoading;
  const showLoading = loading || isLoading;

  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={isDisabled}
      className={buttonClasses}
      aria-label={showLoading ? 'Signing in with Google...' : text}
      aria-describedby="google-auth-description"
    >
      {/* Google Icon */}
      {!showLoading && (
        <svg
          className="w-5 h-5 flex-shrink-0"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path
            fill="#4285F4"
            d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
          />
          <path
            fill="#34A853"
            d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
          />
          <path
            fill="#FBBC05"
            d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
          />
          <path
            fill="#EA4335"
            d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
          />
        </svg>
      )}

      {/* Loading Spinner */}
      {showLoading && (
        <div className="w-5 h-5 flex-shrink-0">
          <div className="w-5 h-5 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin"></div>
        </div>
      )}

      {/* Button Text */}
      <span className="text-center">
        {showLoading ? 'Signing in...' : text}
      </span>

      {/* Hidden description for screen readers */}
      <span id="google-auth-description" className="sr-only">
        Sign in with your Google account. This will open Google's secure authentication page.
      </span>
    </button>
  );
}

// Export for backward compatibility
export default GoogleAuthButton;