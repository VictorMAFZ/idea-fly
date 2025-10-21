/**
 * ErrorBoundary Component for IdeaFly Application.
 * 
 * Provides comprehensive error handling with user-friendly feedback,
 * error reporting, retry mechanisms, and fallback UI components.
 * Follows React Error Boundary pattern with enhanced UX features.
 */

'use client';

import React, { Component, ReactNode, ErrorInfo } from 'react';
import { logger } from '../utils/logger';

// ============================================================================
// TYPES AND INTERFACES
// ============================================================================

interface ErrorBoundaryProps {
  /** Child components to render */
  children: ReactNode;
  /** Custom fallback component */
  fallback?: React.ComponentType<ErrorFallbackProps>;
  /** Callback when error occurs */
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  /** Whether to show retry button */
  showRetry?: boolean;
  /** Custom error message */
  errorMessage?: string;
  /** Whether to isolate errors (prevent propagation) */
  isolate?: boolean;
}

interface ErrorBoundaryState {
  /** Whether an error has occurred */
  hasError: boolean;
  /** The error object */
  error: Error | null;
  /** Error info from React */
  errorInfo: ErrorInfo | null;
  /** Number of retry attempts */
  retryCount: number;
  /** Error ID for tracking */
  errorId: string | null;
}

interface ErrorFallbackProps {
  /** The error that occurred */
  error: Error | null;
  /** Error info from React */
  errorInfo: ErrorInfo | null;
  /** Function to retry/reset the error boundary */
  retry: () => void;
  /** Number of retry attempts */
  retryCount: number;
  /** Unique error ID */
  errorId: string | null;
  /** Custom error message */
  errorMessage?: string;
}

// ============================================================================
// CONSTANTS
// ============================================================================

/** Maximum number of retry attempts */
const MAX_RETRY_ATTEMPTS = 3;

/** Error types for categorization */
const ErrorTypes = {
  NETWORK: 'network',
  AUTHENTICATION: 'auth',
  VALIDATION: 'validation',
  RUNTIME: 'runtime',
  CHUNK_LOAD: 'chunk_load',
  UNKNOWN: 'unknown'
} as const;

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Generate a unique error ID for tracking.
 */
function generateErrorId(): string {
  return `err_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Categorize error type based on error message and properties.
 */
function categorizeError(error: Error): string {
  const message = error.message.toLowerCase();
  
  if (message.includes('loading chunk') || message.includes('import')) {
    return ErrorTypes.CHUNK_LOAD;
  }
  
  if (message.includes('network') || message.includes('fetch')) {
    return ErrorTypes.NETWORK;
  }
  
  if (message.includes('unauthorized') || message.includes('authentication')) {
    return ErrorTypes.AUTHENTICATION;
  }
  
  if (message.includes('validation') || message.includes('invalid')) {
    return ErrorTypes.VALIDATION;
  }
  
  return ErrorTypes.RUNTIME;
}

/**
 * Check if error is recoverable (can retry).
 */
function isRecoverableError(error: Error): boolean {
  const errorType = categorizeError(error);
  return [ErrorTypes.NETWORK, ErrorTypes.CHUNK_LOAD].includes(errorType as any);
}

/**
 * Get user-friendly error message based on error type.
 */
function getUserFriendlyMessage(error: Error, customMessage?: string): string {
  if (customMessage) return customMessage;
  
  const errorType = categorizeError(error);
  
  switch (errorType) {
    case ErrorTypes.NETWORK:
      return 'Problema de conexión. Por favor, verifica tu conexión a internet e intenta nuevamente.';
      
    case ErrorTypes.AUTHENTICATION:
      return 'Sesión expirada. Por favor, inicia sesión nuevamente.';
      
    case ErrorTypes.VALIDATION:
      return 'Datos inválidos. Por favor, verifica la información e intenta nuevamente.';
      
    case ErrorTypes.CHUNK_LOAD:
      return 'Error al cargar la aplicación. Por favor, recarga la página.';
      
    case ErrorTypes.RUNTIME:
      return 'Ha ocurrido un error inesperado. Nuestro equipo ha sido notificado.';
      
    default:
      return 'Ha ocurrido un error inesperado. Por favor, intenta nuevamente.';
  }
}

// ============================================================================
// DEFAULT FALLBACK COMPONENT
// ============================================================================

/**
 * Default error fallback UI component.
 */
function DefaultErrorFallback({
  error,
  errorInfo,
  retry,
  retryCount,
  errorId,
  errorMessage
}: ErrorFallbackProps) {
  const friendlyMessage = getUserFriendlyMessage(error!, errorMessage);
  const canRetry = error ? isRecoverableError(error) : false;
  const hasRetriesLeft = retryCount < MAX_RETRY_ATTEMPTS;

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4 py-12">
      <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-6">
        <div className="flex">
          {/* Error Icon */}
          <div className="flex-shrink-0">
            <svg 
              className="h-6 w-6 text-red-400" 
              fill="none" 
              viewBox="0 0 24 24" 
              stroke="currentColor"
              aria-hidden="true"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 19.5c-.77.833.192 2.5 1.732 2.5z" 
              />
            </svg>
          </div>
          
          {/* Content */}
          <div className="ml-3">
            <h3 className="text-sm font-medium text-gray-800">
              Error en la Aplicación
            </h3>
            <div className="mt-2 text-sm text-gray-500">
              <p>{friendlyMessage}</p>
            </div>
            
            {/* Error ID */}
            {errorId && (
              <div className="mt-3 text-xs text-gray-400">
                ID de Error: {errorId}
              </div>
            )}
            
            {/* Actions */}
            <div className="mt-4">
              <div className="flex space-x-3">
                {/* Retry Button */}
                {canRetry && hasRetriesLeft && (
                  <button
                    onClick={retry}
                    className="bg-red-600 hover:bg-red-700 text-white text-sm px-4 py-2 rounded-md transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                    aria-label="Reintentar operación"
                  >
                    Reintentar {retryCount > 0 && `(${MAX_RETRY_ATTEMPTS - retryCount} restantes)`}
                  </button>
                )}
                
                {/* Reload Button */}
                <button
                  onClick={() => window.location.reload()}
                  className="bg-gray-600 hover:bg-gray-700 text-white text-sm px-4 py-2 rounded-md transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
                  aria-label="Recargar página"
                >
                  Recargar Página
                </button>
                
                {/* Home Button */}
                <button
                  onClick={() => window.location.href = '/'}
                  className="bg-blue-600 hover:bg-blue-700 text-white text-sm px-4 py-2 rounded-md transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  aria-label="Ir al inicio"
                >
                  Ir al Inicio
                </button>
              </div>
            </div>
            
            {/* Error Details (Development) */}
            {process.env.NODE_ENV === 'development' && (
              <details className="mt-4">
                <summary className="cursor-pointer text-sm text-gray-600 hover:text-gray-800">
                  Detalles Técnicos (Desarrollo)
                </summary>
                <div className="mt-2 p-3 bg-gray-100 rounded-md">
                  <pre className="text-xs text-gray-800 whitespace-pre-wrap break-words">
                    <strong>Error:</strong> {error?.message}
                    {'\n\n'}
                    <strong>Stack:</strong> {error?.stack}
                    {errorInfo?.componentStack && (
                      <>
                        {'\n\n'}
                        <strong>Component Stack:</strong> {errorInfo.componentStack}
                      </>
                    )}
                  </pre>
                </div>
              </details>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// ERROR BOUNDARY CLASS COMPONENT
// ============================================================================

/**
 * React Error Boundary component with enhanced error handling.
 */
class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  private resetTimeoutId: number | null = null;

  constructor(props: ErrorBoundaryProps) {
    super(props);
    
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: 0,
      errorId: null
    };
  }

  /**
   * Static method to update state when an error occurs.
   */
  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return {
      hasError: true,
      error,
      errorId: generateErrorId()
    };
  }

  /**
   * Lifecycle method called when an error occurs.
   */
  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    const errorId = this.state.errorId || generateErrorId();
    
    // Update state with error info
    this.setState({
      errorInfo,
      errorId
    });

    // Log error
    this.logError(error, errorInfo, errorId);
    
    // Call custom error handler
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
    
    // Report error to monitoring service in production
    if (process.env.NODE_ENV === 'production') {
      this.reportError(error, errorInfo, errorId);
    }
  }

  /**
   * Log error with structured logging.
   */
  private logError(error: Error, errorInfo: ErrorInfo, errorId: string) {
    logger.error('ErrorBoundary caught an error', {
      errorId,
      errorType: categorizeError(error),
      errorMessage: error.message,
      errorStack: error.stack,
      componentStack: errorInfo.componentStack,
      retryCount: this.state.retryCount,
      userAgent: navigator.userAgent,
      url: window.location.href,
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Report error to external monitoring service.
   */
  private reportError(error: Error, errorInfo: ErrorInfo, errorId: string) {
    // TODO: Implement error reporting to service like Sentry, LogRocket, etc.
    console.warn('Error reporting not implemented:', { errorId, error, errorInfo });
  }

  /**
   * Retry handler - reset error boundary state.
   */
  private handleRetry = () => {
    if (this.state.retryCount >= MAX_RETRY_ATTEMPTS) {
      logger.warn('Maximum retry attempts reached', {
        errorId: this.state.errorId,
        retryCount: this.state.retryCount
      });
      return;
    }

    logger.info('Retrying after error', {
      errorId: this.state.errorId,
      retryCount: this.state.retryCount + 1
    });

    this.setState(prevState => ({
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: prevState.retryCount + 1,
      errorId: null
    }));
  };

  /**
   * Reset error boundary state after successful recovery.
   */
  componentDidUpdate(prevProps: ErrorBoundaryProps, prevState: ErrorBoundaryState) {
    // Auto-reset after successful render without error
    if (prevState.hasError && !this.state.hasError) {
      // Clear any existing timeout
      if (this.resetTimeoutId) {
        clearTimeout(this.resetTimeoutId);
      }
      
      // Reset retry count after successful recovery
      this.resetTimeoutId = window.setTimeout(() => {
        this.setState({ retryCount: 0 });
      }, 5000); // Reset after 5 seconds of successful operation
    }
  }

  /**
   * Cleanup when component unmounts.
   */
  componentWillUnmount() {
    if (this.resetTimeoutId) {
      clearTimeout(this.resetTimeoutId);
    }
  }

  /**
   * Render method - show fallback UI or children.
   */
  render() {
    if (this.state.hasError) {
      const FallbackComponent = this.props.fallback || DefaultErrorFallback;
      
      return (
        <FallbackComponent
          error={this.state.error}
          errorInfo={this.state.errorInfo}
          retry={this.handleRetry}
          retryCount={this.state.retryCount}
          errorId={this.state.errorId}
          errorMessage={this.props.errorMessage}
        />
      );
    }

    return this.props.children;
  }
}

// ============================================================================
// HOOK FOR PROGRAMMATIC ERROR HANDLING
// ============================================================================

/**
 * Hook for handling errors programmatically in functional components.
 */
export function useErrorHandler() {
  const [error, setError] = React.useState<Error | null>(null);

  const handleError = React.useCallback((error: Error | string) => {
    const errorObject = typeof error === 'string' ? new Error(error) : error;
    setError(errorObject);
  }, []);

  const clearError = React.useCallback(() => {
    setError(null);
  }, []);

  // Throw error to be caught by ErrorBoundary
  React.useEffect(() => {
    if (error) {
      throw error;
    }
  }, [error]);

  return { handleError, clearError, error };
}

// ============================================================================
// SPECIALIZED ERROR BOUNDARY COMPONENTS
// ============================================================================

/**
 * Error boundary specifically for authentication flows.
 */
export function AuthErrorBoundary({ children }: { children: ReactNode }) {
  return (
    <ErrorBoundary
      errorMessage="Ha ocurrido un error con la autenticación. Por favor, intenta iniciar sesión nuevamente."
      onError={(error) => {
        // Redirect to login on auth errors
        if (categorizeError(error) === ErrorTypes.AUTHENTICATION) {
          setTimeout(() => {
            window.location.href = '/login';
          }, 2000);
        }
      }}
      showRetry={false}
    >
      {children}
    </ErrorBoundary>
  );
}

/**
 * Error boundary for form components.
 */
export function FormErrorBoundary({ children }: { children: ReactNode }) {
  return (
    <ErrorBoundary
      errorMessage="Error en el formulario. Por favor, verifica los datos e intenta nuevamente."
      showRetry={true}
      isolate={true}
    >
      {children}
    </ErrorBoundary>
  );
}

// ============================================================================
// EXPORTS
// ============================================================================

export default ErrorBoundary;
export type { ErrorBoundaryProps, ErrorFallbackProps };