/**
 * LogoutButton component for user logout functionality.
 * 
 * This component provides a secure logout button with proper loading states
 * and accessibility features following design system guidelines.
 * 
 * Features:
 * - Secure logout with token invalidation
 * - Loading states and error handling
 * - Accessibility compliant (ARIA labels, keyboard navigation)
 * - Responsive design with TailwindCSS
 * - Confirmation dialog support
 * - Dark mode support
 */

'use client';

import { useState } from 'react';
// Using inline SVG icons instead of lucide-react for consistency

interface LogoutButtonProps {
  /** Callback function when logout succeeds */
  onSuccess?: () => void;
  /** Callback function when logout fails */
  onError?: (error: string) => void;
  /** Button text - defaults to "Logout" */
  text?: string;
  /** Whether to show icon */
  showIcon?: boolean;
  /** Whether the button is in loading state */
  loading?: boolean;
  /** Whether the button is disabled */
  disabled?: boolean;
  /** Button variant - filled, outlined, or ghost */
  variant?: 'filled' | 'outlined' | 'ghost';
  /** Button size */
  size?: 'sm' | 'md' | 'lg';
  /** Additional CSS classes */
  className?: string;
  /** Whether to show confirmation dialog before logout */
  showConfirmation?: boolean;
  /** Confirmation message text */
  confirmationText?: string;
}

export function LogoutButton({
  onSuccess,
  onError,
  text = "Logout",
  showIcon = true,
  loading = false,
  disabled = false,
  variant = 'ghost',
  size = 'md',
  className = '',
  showConfirmation = false,
  confirmationText = "Are you sure you want to logout?"
}: LogoutButtonProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);

  // Combine loading states
  const isButtonLoading = loading || isLoading;

  // Handle logout click
  const handleLogoutClick = () => {
    if (showConfirmation) {
      setShowConfirmDialog(true);
    } else {
      executeLogout();
    }
  };

  // Execute the actual logout
  const executeLogout = async () => {
    try {
      setIsLoading(true);
      setShowConfirmDialog(false);

      // Import auth service dynamically to avoid circular imports
      const { logout } = await import('../../services/authService');
      
      // Call logout service
      await logout();
      
      // Call success callback
      onSuccess?.();
      
    } catch (error) {
      const errorMessage = error instanceof Error 
        ? error.message 
        : 'An unexpected error occurred during logout';
      
      console.error('Logout error:', error);
      onError?.(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle confirmation dialog actions
  const handleConfirmLogout = () => {
    executeLogout();
  };

  const handleCancelLogout = () => {
    setShowConfirmDialog(false);
  };

  // Size classes
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base'
  };

  // Variant classes
  const variantClasses = {
    filled: 'bg-red-600 hover:bg-red-700 focus:ring-red-500 text-white border border-red-600',
    outlined: 'border border-red-300 text-red-700 hover:bg-red-50 focus:ring-red-500 bg-white dark:border-red-600 dark:text-red-400 dark:hover:bg-red-950 dark:bg-gray-900',
    ghost: 'text-gray-700 hover:bg-gray-100 focus:ring-gray-500 dark:text-gray-300 dark:hover:bg-gray-800'
  };

  // Icon size based on button size
  const iconSize = {
    sm: 14,
    md: 16,
    lg: 18
  };

  const baseClasses = `
    inline-flex items-center justify-center
    font-medium rounded-lg
    transition-all duration-200
    focus:outline-none focus:ring-2 focus:ring-offset-2
    disabled:opacity-50 disabled:cursor-not-allowed
    dark:focus:ring-offset-gray-800
  `.trim();

  return (
    <>
      <button
        type="button"
        onClick={handleLogoutClick}
        disabled={disabled || isButtonLoading}
        className={`
          ${baseClasses}
          ${sizeClasses[size]}
          ${variantClasses[variant]}
          ${className}
        `.replace(/\s+/g, ' ').trim()}
        aria-label={`${text} - Sign out of your account`}
        data-testid="logout-button"
      >
        {isButtonLoading ? (
          <>
            <svg 
              width={iconSize[size]} 
              height={iconSize[size]}
              className="animate-spin mr-2" 
              aria-hidden="true"
              fill="none" 
              viewBox="0 0 24 24"
            >
              <circle 
                cx="12" 
                cy="12" 
                r="10" 
                stroke="currentColor" 
                strokeWidth="4" 
                className="opacity-25"
              />
              <path 
                fill="currentColor" 
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                className="opacity-75"
              />
            </svg>
            <span>Signing out...</span>
          </>
        ) : (
          <>
            {showIcon && (
              <svg 
                width={iconSize[size]} 
                height={iconSize[size]}
                className="mr-2" 
                aria-hidden="true"
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
                strokeWidth="2"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4m4 14l4-4m0 0l-4-4m4 4H9"
                />
              </svg>
            )}
            <span>{text}</span>
          </>
        )}
      </button>

      {/* Confirmation Dialog */}
      {showConfirmDialog && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
          role="dialog"
          aria-modal="true"
          aria-labelledby="logout-dialog-title"
          data-testid="logout-confirmation-dialog"
        >
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 max-w-sm mx-4">
            <h3 
              id="logout-dialog-title"
              className="text-lg font-semibold text-gray-900 dark:text-white mb-4"
            >
              Confirm Logout
            </h3>
            <p className="text-gray-600 dark:text-gray-300 mb-6">
              {confirmationText}
            </p>
            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={handleCancelLogout}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-600"
                data-testid="cancel-logout-button"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleConfirmLogout}
                disabled={isButtonLoading}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 border border-transparent rounded-lg hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed"
                data-testid="confirm-logout-button"
              >
                {isButtonLoading ? 'Signing out...' : 'Logout'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default LogoutButton;