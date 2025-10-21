/**
 * ProtectedRoute Higher-Order Component for IdeaFly Application.
 * 
 * Provides component-level route protection and authentication checks.
 * This HOC can be used to wrap individual components or pages that require
 * authentication, offering more granular control than middleware alone.
 */

'use client';

import React, { useEffect, useState, ComponentType } from 'react';
import { useRouter } from 'next/navigation';
import { useIsAuthenticated, useCurrentUser, useAuth } from '../hooks/useAuth';

// ============================================================================
// TYPES AND INTERFACES
// ============================================================================

/**
 * Configuration options for the ProtectedRoute HOC.
 */
interface ProtectedRouteOptions {
  /** Redirect path for unauthenticated users */
  redirectTo?: string;
  /** Whether to show loading spinner during auth check */
  showLoading?: boolean;
  /** Custom loading component */
  loadingComponent?: ComponentType;
  /** Whether to require active user account */
  requireActive?: boolean;
  /** Required user roles (future enhancement) */
  requiredRoles?: string[];
  /** Custom fallback component for unauthorized users */
  fallbackComponent?: ComponentType;
  /** Whether to check authentication on component mount */
  checkOnMount?: boolean;
}

/**
 * Props passed to the loading component.
 */
interface LoadingProps {
  message?: string;
}

/**
 * Props passed to the fallback component.
 */
interface FallbackProps {
  reason: 'unauthenticated' | 'inactive' | 'insufficient_role';
  redirectTo: string;
  onRedirect: () => void;
}

// ============================================================================
// DEFAULT COMPONENTS
// ============================================================================

/**
 * Default loading component with spinner and message.
 */
const DefaultLoadingComponent: React.FC<LoadingProps> = ({ 
  message = "Verificando autenticación..." 
}) => (
  <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center">
    <div className="text-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
      <p className="mt-4 text-gray-600">{message}</p>
    </div>
  </div>
);

/**
 * Default fallback component for unauthorized access.
 */
const DefaultFallbackComponent: React.FC<FallbackProps> = ({ 
  reason, 
  redirectTo, 
  onRedirect 
}) => (
  <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center">
    <div className="text-center max-w-md mx-auto px-4">
      <div className="mb-6">
        <svg className="h-16 w-16 text-red-500 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.802-.833-2.572 0L4.242 16.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
      </div>
      
      <h2 className="text-2xl font-bold text-gray-900 mb-4">
        Acceso No Autorizado
      </h2>
      
      <p className="text-gray-600 mb-6">
        {reason === 'unauthenticated' && "Debes iniciar sesión para acceder a esta página."}
        {reason === 'inactive' && "Tu cuenta ha sido desactivada. Contacta al soporte para más información."}
        {reason === 'insufficient_role' && "No tienes permisos suficientes para acceder a esta página."}
      </p>
      
      <button
        onClick={onRedirect}
        className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
      >
        {reason === 'unauthenticated' ? 'Iniciar Sesión' : 'Ir al Inicio'}
      </button>
    </div>
  </div>
);

// ============================================================================
// PROTECTED ROUTE HOC
// ============================================================================

/**
 * Higher-Order Component that adds authentication protection to any component.
 * 
 * @param WrappedComponent - The component to protect
 * @param options - Configuration options for protection behavior
 * @returns Protected component with authentication checks
 * 
 * @example
 * ```tsx
 * // Basic usage
 * const ProtectedDashboard = withProtectedRoute(Dashboard);
 * 
 * // With options
 * const ProtectedAdminPanel = withProtectedRoute(AdminPanel, {
 *   redirectTo: '/login',
 *   requireActive: true,
 *   requiredRoles: ['admin']
 * });
 * 
 * // Usage in component
 * export default withProtectedRoute(MyComponent);
 * ```
 */
export function withProtectedRoute<P extends object>(
  WrappedComponent: ComponentType<P>,
  options: ProtectedRouteOptions = {}
): ComponentType<P> {
  const {
    redirectTo = '/login',
    showLoading = true,
    loadingComponent: LoadingComponent = DefaultLoadingComponent,
    requireActive = false,
    requiredRoles = [],
    fallbackComponent: FallbackComponent = DefaultFallbackComponent,
    checkOnMount = true
  } = options;

  const ProtectedComponent: React.FC<P> = (props) => {
    const router = useRouter();
    const isAuthenticated = useIsAuthenticated();
    const user = useCurrentUser();
    const { loading } = useAuth();
    
    const [authCheckComplete, setAuthCheckComplete] = useState(!checkOnMount);
    const [authError, setAuthError] = useState<'unauthenticated' | 'inactive' | 'insufficient_role' | null>(null);

    // ============================================================================
    // AUTHENTICATION CHECKS
    // ============================================================================

    useEffect(() => {
      if (!checkOnMount) return;

      const performAuthChecks = async () => {
        try {
          // Wait for auth loading to complete
          if (loading) return;

          // Check if user is authenticated
          if (!isAuthenticated) {
            setAuthError('unauthenticated');
            return;
          }

          // Check if user object is available
          if (!user) {
            setAuthError('unauthenticated');
            return;
          }

          // Check if user account is active
          if (!user.is_active) {
            setAuthError('inactive');
            return;
          }

          // Check user roles if required (future enhancement)
          if (requiredRoles.length > 0) {
            // TODO: Implement role checking when user roles are added to the model
            // const userRoles = user.roles || [];
            // const hasRequiredRole = requiredRoles.some(role => userRoles.includes(role));
            // if (!hasRequiredRole) {
            //   setAuthError('insufficient_role');
            //   return;
            // }
          }

          // All checks passed
          setAuthError(null);
          setAuthCheckComplete(true);

        } catch (error) {
          console.error('Auth check error:', error);
          setAuthError('unauthenticated');
        }
      };

      performAuthChecks();
    }, [isAuthenticated, user, loading, requireActive, requiredRoles]);

    // ============================================================================
    // REDIRECT HANDLER
    // ============================================================================

    const handleRedirect = () => {
      if (authError === 'unauthenticated') {
        // Add return URL for seamless redirect after login
        const currentPath = window.location.pathname;
        const loginUrl = `${redirectTo}?returnTo=${encodeURIComponent(currentPath)}`;
        router.push(loginUrl);
      } else {
        router.push('/');
      }
    };

    // ============================================================================
    // RENDER LOGIC
    // ============================================================================

    // Show loading while auth is being checked
    if (loading || (checkOnMount && !authCheckComplete)) {
      return showLoading ? <LoadingComponent message="Verificando autenticación..." /> : null;
    }

    // Show error/fallback if authentication failed
    if (authError) {
      return (
        <FallbackComponent
          reason={authError}
          redirectTo={redirectTo}
          onRedirect={handleRedirect}
        />
      );
    }

    // Render the protected component
    return <WrappedComponent {...props} />;
  };

  // ============================================================================
  // COMPONENT METADATA
  // ============================================================================

  ProtectedComponent.displayName = `withProtectedRoute(${WrappedComponent.displayName || WrappedComponent.name})`;

  return ProtectedComponent;
}

// ============================================================================
// CONVENIENCE COMPONENTS
// ============================================================================

/**
 * Pre-configured ProtectedRoute component for common use cases.
 * Can be used as a wrapper component instead of HOC.
 * 
 * @example
 * ```tsx
 * <ProtectedRoute>
 *   <Dashboard />
 * </ProtectedRoute>
 * 
 * <ProtectedRoute requireActive redirectTo="/account-disabled">
 *   <AdminPanel />
 * </ProtectedRoute>
 * ```
 */
export const ProtectedRoute: React.FC<{
  children: React.ReactNode;
} & ProtectedRouteOptions> = ({ children, ...options }) => {
  const ProtectedWrapper = withProtectedRoute(({ children }: { children: React.ReactNode }) => <>{children}</>, options);
  return <ProtectedWrapper>{children}</ProtectedWrapper>;
};

/**
 * Hook for checking if current user has required permissions.
 * Useful for conditional rendering within components.
 * 
 * @param options - Permission requirements
 * @returns Object with permission status and user info
 * 
 * @example
 * ```tsx
 * const { hasPermission, isLoading, reason } = usePermissions({
 *   requireActive: true,
 *   requiredRoles: ['admin']
 * });
 * 
 * if (isLoading) return <Spinner />;
 * if (!hasPermission) return <div>Access denied: {reason}</div>;
 * return <AdminContent />;
 * ```
 */
export function usePermissions(options: Pick<ProtectedRouteOptions, 'requireActive' | 'requiredRoles'> = {}) {
  const { requireActive = false, requiredRoles = [] } = options;
  const isAuthenticated = useIsAuthenticated();
  const user = useCurrentUser();
  const { loading } = useAuth();

  const [hasPermission, setHasPermission] = useState(false);
  const [reason, setReason] = useState<string | null>(null);

  useEffect(() => {
    if (loading) return;

    if (!isAuthenticated || !user) {
      setHasPermission(false);
      setReason('unauthenticated');
      return;
    }

    if (!user.is_active) {
      setHasPermission(false);
      setReason('inactive');
      return;
    }

    if (requiredRoles.length > 0) {
      // TODO: Implement role checking
      setHasPermission(false);
      setReason('insufficient_role');
      return;
    }

    setHasPermission(true);
    setReason(null);
  }, [isAuthenticated, user, loading, requireActive, requiredRoles]);

  return {
    hasPermission,
    isLoading: loading,
    reason,
    user,
    isAuthenticated
  };
}

// ============================================================================
// EXPORTS
// ============================================================================

export default withProtectedRoute;

export type {
  ProtectedRouteOptions,
  LoadingProps,
  FallbackProps
};