/**
 * Loading States and Skeleton Components for IdeaFly Application.
 * 
 * Provides reusable loading indicators, skeleton screens, and
 * loading states for improved user experience during async operations.
 */

'use client';

import React from 'react';

// ============================================================================
// TYPES AND INTERFACES
// ============================================================================

interface LoadingSpinnerProps {
  /** Size of the spinner */
  size?: 'sm' | 'md' | 'lg' | 'xl';
  /** Color scheme */
  color?: 'primary' | 'white' | 'gray';
  /** Custom className */
  className?: string;
  /** Accessible label */
  label?: string;
}

interface SkeletonProps {
  /** Width of skeleton */
  width?: string | number;
  /** Height of skeleton */
  height?: string | number;
  /** Shape variant */
  variant?: 'text' | 'circular' | 'rectangular';
  /** Custom className */
  className?: string;
  /** Animation speed */
  animation?: 'pulse' | 'wave' | 'none';
}

interface LoadingButtonProps {
  /** Whether button is in loading state */
  loading: boolean;
  /** Button children when not loading */
  children: React.ReactNode;
  /** Loading text */
  loadingText?: string;
  /** Button props */
  [key: string]: any;
}

// ============================================================================
// LOADING SPINNER COMPONENT
// ============================================================================

/**
 * Customizable loading spinner with different sizes and colors.
 */
export function LoadingSpinner({ 
  size = 'md', 
  color = 'primary', 
  className = '',
  label = 'Cargando...'
}: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8',
    xl: 'h-12 w-12'
  };

  const colorClasses = {
    primary: 'text-blue-600',
    white: 'text-white',
    gray: 'text-gray-400'
  };

  return (
    <div className={`inline-flex items-center ${className}`} role="status" aria-label={label}>
      <svg 
        className={`animate-spin ${sizeClasses[size]} ${colorClasses[color]}`}
        fill="none" 
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <circle 
          className="opacity-25" 
          cx="12" 
          cy="12" 
          r="10" 
          stroke="currentColor" 
          strokeWidth="4"
        />
        <path 
          className="opacity-75" 
          fill="currentColor" 
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
      <span className="sr-only">{label}</span>
    </div>
  );
}

// ============================================================================
// SKELETON COMPONENT
// ============================================================================

/**
 * Skeleton placeholder component for loading states.
 */
export function Skeleton({ 
  width = '100%', 
  height = '1rem', 
  variant = 'text',
  className = '',
  animation = 'pulse'
}: SkeletonProps) {
  const baseClasses = 'bg-gray-200 dark:bg-gray-700';
  
  const variantClasses = {
    text: 'rounded',
    circular: 'rounded-full',
    rectangular: 'rounded-md'
  };

  const animationClasses = {
    pulse: 'animate-pulse',
    wave: 'animate-pulse', // Could implement wave animation with CSS
    none: ''
  };

  const style = {
    width: typeof width === 'number' ? `${width}px` : width,
    height: typeof height === 'number' ? `${height}px` : height
  };

  return (
    <div 
      className={`${baseClasses} ${variantClasses[variant]} ${animationClasses[animation]} ${className}`}
      style={style}
      aria-hidden="true"
    />
  );
}

// ============================================================================
// LOADING BUTTON COMPONENT
// ============================================================================

/**
 * Button component with loading state and spinner.
 */
export function LoadingButton({ 
  loading, 
  children, 
  loadingText = 'Cargando...',
  disabled,
  className = '',
  ...props 
}: LoadingButtonProps) {
  return (
    <button
      {...props}
      disabled={loading || disabled}
      className={`inline-flex items-center justify-center ${className}`}
    >
      {loading && (
        <LoadingSpinner 
          size="sm" 
          color="white" 
          className="mr-2" 
          label={loadingText}
        />
      )}
      {loading ? loadingText : children}
    </button>
  );
}

// ============================================================================
// FORM SKELETON COMPONENTS
// ============================================================================

/**
 * Skeleton for form input fields.
 */
export function FormInputSkeleton({ className = '' }: { className?: string }) {
  return (
    <div className={`space-y-2 ${className}`}>
      <Skeleton height="1.25rem" width="30%" />
      <Skeleton height="2.5rem" className="rounded-md" />
    </div>
  );
}

/**
 * Skeleton for form with multiple fields.
 */
export function FormSkeleton({ fields = 3, className = '' }: { fields?: number; className?: string }) {
  return (
    <div className={`space-y-6 ${className}`}>
      {Array.from({ length: fields }, (_, i) => (
        <FormInputSkeleton key={i} />
      ))}
      <Skeleton height="2.75rem" className="rounded-md" />
    </div>
  );
}

// ============================================================================
// AUTH-SPECIFIC LOADING COMPONENTS
// ============================================================================

/**
 * Loading state for authentication forms.
 */
export function AuthFormLoading({ title = 'Cargando...' }: { title?: string }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4 py-12">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <Skeleton variant="circular" width="4rem" height="4rem" className="mx-auto mb-4" />
          <Skeleton height="2rem" width="60%" className="mx-auto mb-2" />
          <Skeleton height="1rem" width="80%" className="mx-auto" />
        </div>
        
        <div className="bg-white shadow-md rounded-lg p-8">
          <div className="text-center mb-6">
            <Skeleton height="1.5rem" width="40%" className="mx-auto" />
          </div>
          
          <FormSkeleton fields={3} />
          
          <div className="mt-6 space-y-3">
            <Skeleton height="2.75rem" className="rounded-md" />
            <div className="text-center">
              <Skeleton height="1rem" width="60%" className="mx-auto" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Loading state for dashboard/protected pages.
 */
export function DashboardLoading() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header Skeleton */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <Skeleton height="2rem" width="8rem" />
            <div className="flex items-center space-x-4">
              <Skeleton variant="circular" width="2rem" height="2rem" />
              <Skeleton height="1rem" width="6rem" />
            </div>
          </div>
        </div>
      </div>
      
      {/* Main Content Skeleton */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Welcome Section */}
          <div className="bg-white overflow-hidden shadow rounded-lg mb-6">
            <div className="px-4 py-5 sm:p-6">
              <Skeleton height="2rem" width="40%" className="mb-4" />
              <Skeleton height="1rem" width="80%" className="mb-2" />
              <Skeleton height="1rem" width="60%" />
            </div>
          </div>
          
          {/* Grid Content */}
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }, (_, i) => (
              <div key={i} className="bg-white overflow-hidden shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <Skeleton height="1.5rem" width="70%" className="mb-3" />
                  <Skeleton height="1rem" width="100%" className="mb-2" />
                  <Skeleton height="1rem" width="100%" className="mb-2" />
                  <Skeleton height="1rem" width="80%" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}

// ============================================================================
// LOADING OVERLAY COMPONENT
// ============================================================================

/**
 * Full-screen loading overlay.
 */
export function LoadingOverlay({ 
  visible, 
  message = 'Cargando...', 
  className = '' 
}: { 
  visible: boolean; 
  message?: string; 
  className?: string; 
}) {
  if (!visible) return null;

  return (
    <div 
      className={`fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 ${className}`}
      role="dialog"
      aria-modal="true"
      aria-label="Loading"
    >
      <div className="bg-white rounded-lg p-6 text-center shadow-xl">
        <LoadingSpinner size="lg" className="mb-4" />
        <p className="text-gray-700 font-medium">{message}</p>
      </div>
    </div>
  );
}

// ============================================================================
// LAZY LOADING WRAPPER
// ============================================================================

/**
 * Wrapper component for lazy-loaded content with skeleton.
 */
export function LazyWrapper({ 
  loading, 
  skeleton, 
  children,
  className = ''
}: {
  loading: boolean;
  skeleton: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={className}>
      {loading ? skeleton : children}
    </div>
  );
}

// ============================================================================
// PROGRESSIVE LOADING COMPONENT
// ============================================================================

/**
 * Progressive loading component with multiple states.
 */
export function ProgressiveLoading({
  stage,
  stages = [
    { label: 'Conectando...', progress: 25 },
    { label: 'Autenticando...', progress: 50 },
    { label: 'Cargando datos...', progress: 75 },
    { label: 'Finalizando...', progress: 100 }
  ],
  className = ''
}: {
  stage: number;
  stages?: Array<{ label: string; progress: number }>;
  className?: string;
}) {
  const currentStage = stages[stage] || stages[0];
  
  return (
    <div className={`text-center ${className}`}>
      <LoadingSpinner size="lg" className="mb-4" />
      <p className="text-gray-700 font-medium mb-2">{currentStage.label}</p>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div 
          className="bg-blue-600 h-2 rounded-full transition-all duration-500 ease-out"
          style={{ width: `${currentStage.progress}%` }}
        />
      </div>
    </div>
  );
}

// ============================================================================
// EXPORTS
// ============================================================================

export default {
  Spinner: LoadingSpinner,
  Skeleton,
  Button: LoadingButton,
  FormSkeleton,
  AuthFormLoading,
  DashboardLoading,
  Overlay: LoadingOverlay,
  LazyWrapper,
  ProgressiveLoading
};