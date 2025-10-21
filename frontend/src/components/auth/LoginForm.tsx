/**
 * LoginForm Component for IdeaFly Authentication System.
 * 
 * A comprehensive user login form with validation, accessibility features,
 * and error handling for the US2 user story implementation.
 */

'use client';

import React, { useState, useCallback, useEffect, useRef } from 'react';
import { LoginRequest, AuthStatus } from '../../types/auth';
import GoogleAuthButtonAlternative from './GoogleAuthButtonAlternative';
import { useGoogleAuth } from '../../hooks/useGoogleAuth';
import { LoadingButton, LoadingSpinner } from '../LoadingComponents';

// ============================================================================
// TYPES AND INTERFACES
// ============================================================================

/**
 * Form validation errors structure
 */
interface FormErrors {
  email?: string;
  password?: string;
  general?: string;
}

/**
 * Form field validation state
 */
interface FormTouched {
  email: boolean;
  password: boolean;
}

/**
 * LoginForm component props
 */
export interface LoginFormProps {
  /** Called when user submits valid login data */
  onSubmit: (data: LoginRequest) => Promise<void>;
  /** Current authentication status */
  authStatus?: AuthStatus;
  /** External error message to display */
  error?: string | null;
  /** Whether form should be disabled */
  disabled?: boolean;
  /** Additional CSS classes */
  className?: string;
  /** Callback for "forgot password" link */
  onForgotPassword?: () => void;
  /** Callback for "register" link */
  onRegister?: () => void;
}

// ============================================================================
// VALIDATION FUNCTIONS
// ============================================================================

/**
 * Validates email format using RFC 5322 compliant regex
 */
const validateEmail = (email: string): string | undefined => {
  if (!email.trim()) {
    return 'El correo electrónico es requerido';
  }

  const emailRegex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;
  
  if (!emailRegex.test(email)) {
    return 'Por favor ingresa un correo electrónico válido';
  }

  return undefined;
};

/**
 * Validates password requirements
 */
const validatePassword = (password: string): string | undefined => {
  if (!password) {
    return 'La contraseña es requerida';
  }

  if (password.length < 8) {
    return 'La contraseña debe tener al menos 8 caracteres';
  }

  return undefined;
};

/**
 * Validates entire form and returns all errors
 */
const validateForm = (formData: LoginRequest): FormErrors => {
  return {
    email: validateEmail(formData.email),
    password: validatePassword(formData.password),
  };
};

// ============================================================================
// MAIN COMPONENT
// ============================================================================

/**
 * LoginForm Component
 * 
 * Provides a complete login form with:
 * - Real-time validation
 * - Accessibility features
 * - Loading states
 * - Error handling
 * - Responsive design
 */
export const LoginForm: React.FC<LoginFormProps> = ({
  onSubmit,
  authStatus = AuthStatus.IDLE,
  error = null,
  disabled = false,
  className = '',
  onForgotPassword,
  onRegister,
}) => {
  // ============================================================================
  // STATE MANAGEMENT
  // ============================================================================

  const [formData, setFormData] = useState<LoginRequest>({
    email: '',
    password: '',
  });

  const [errors, setErrors] = useState<FormErrors>({});
  const [touched, setTouched] = useState<FormTouched>({
    email: false,
    password: false,
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  // Refs for focus management
  const emailRef = useRef<HTMLInputElement>(null);
  const passwordRef = useRef<HTMLInputElement>(null);
  const submitButtonRef = useRef<HTMLButtonElement>(null);

  // Google OAuth hook
  const { 
    signInWithGoogle: handleGoogleAuth, 
    loading: googleLoading, 
    error: googleError,
    clearError: clearGoogleError 
  } = useGoogleAuth();

  // ============================================================================
  // DERIVED STATE
  // ============================================================================

  const isLoading = authStatus === AuthStatus.LOADING || isSubmitting || googleLoading;
  const isFormDisabled = disabled || isLoading;

  // Check if form has any errors for submit button state
  const formErrors = validateForm(formData);
  const hasErrors = Object.values(formErrors).some(error => !!error);
  const hasValues = formData.email.trim() && formData.password.trim();
  const canSubmit = !hasErrors && hasValues && !isFormDisabled;

  // Combined error message
  const displayError = error || googleError;

  // ============================================================================
  // EVENT HANDLERS
  // ============================================================================

  /**
   * Handle input field changes with validation
   */
  const handleInputChange = useCallback((field: keyof LoginRequest, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));

    // Clear field-specific error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }

    // Clear general error when user makes changes
    if (errors.general) {
      setErrors(prev => ({ ...prev, general: undefined }));
    }
  }, [errors]);

  /**
   * Handle field blur for validation feedback
   */
  const handleFieldBlur = useCallback((field: keyof FormTouched) => {
    setTouched(prev => ({ ...prev, [field]: true }));

    // Validate field on blur
    const fieldValue = formData[field];
    let fieldError: string | undefined;

    switch (field) {
      case 'email':
        fieldError = validateEmail(fieldValue);
        break;
      case 'password':
        fieldError = validatePassword(fieldValue);
        break;
    }

    if (fieldError) {
      setErrors(prev => ({ ...prev, [field]: fieldError }));
    }
  }, [formData]);

  /**
   * Handle form submission
   */
  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();

    // Mark all fields as touched for validation display
    setTouched({
      email: true,
      password: true,
    });

    // Validate form
    const validationErrors = validateForm(formData);
    const hasValidationErrors = Object.values(validationErrors).some(error => !!error);

    if (hasValidationErrors) {
      setErrors(validationErrors);
      
      // Focus first field with error
      if (validationErrors.email && emailRef.current) {
        emailRef.current.focus();
      } else if (validationErrors.password && passwordRef.current) {
        passwordRef.current.focus();
      }
      
      return;
    }

    try {
      setIsSubmitting(true);
      setErrors({});
      
      await onSubmit({
        email: formData.email.toLowerCase().trim(),
        password: formData.password,
      });
      
    } catch (error) {
      console.error('Login form submission error:', error);
      setErrors({
        general: 'Ocurrió un error inesperado. Por favor intenta nuevamente.',
      });
    } finally {
      setIsSubmitting(false);
    }
  }, [formData, onSubmit]);

  /**
   * Toggle password visibility
   */
  const handleTogglePassword = useCallback(() => {
    setShowPassword(prev => !prev);
  }, []);

  /**
   * Handle successful Google OAuth
   */
  const handleGoogleSuccess = useCallback(async (accessToken: string) => {
    try {
      clearGoogleError(); // Clear any previous Google errors
      await handleGoogleAuth(accessToken);
    } catch (error) {
      console.error('Google authentication error:', error);
      // Error is already handled by the useGoogleAuth hook
    }
  }, [handleGoogleAuth, clearGoogleError]);

  /**
   * Handle Google OAuth error
   */
  const handleGoogleError = useCallback((error: string) => {
    console.error('Google OAuth error:', error);
    // Error is already set by the useGoogleAuth hook
  }, []);

  // ============================================================================
  // KEYBOARD NAVIGATION
  // ============================================================================

  const handleKeyDown = useCallback((e: React.KeyboardEvent, nextRef?: React.RefObject<HTMLElement>) => {
    if (e.key === 'Enter' && nextRef?.current) {
      e.preventDefault();
      nextRef.current.focus();
    }
  }, []);

  // ============================================================================
  // EFFECTS
  // ============================================================================

  /**
   * Clear form errors when external error prop changes
   */
  useEffect(() => {
    if (displayError) {
      setErrors(prev => ({ ...prev, general: displayError }));
    }
  }, [displayError]);

  /**
   * Clear errors when user starts typing after an error
   */
  useEffect(() => {
    if (errors.general && (formData.email || formData.password)) {
      setErrors(prev => ({ ...prev, general: undefined }));
      clearGoogleError(); // Also clear Google errors when user starts interacting
    }
  }, [formData.email, formData.password, errors.general, clearGoogleError]);

  /**
   * Auto-focus email field on mount
   */
  useEffect(() => {
    if (emailRef.current) {
      emailRef.current.focus();
    }
  }, []);

  // ============================================================================
  // RENDER HELPERS
  // ============================================================================

  /**
   * Render input field with validation
   */
  const renderInputField = (
    field: keyof LoginRequest,
    label: string,
    type: string = 'text',
    placeholder?: string,
    ref?: React.RefObject<HTMLInputElement>,
    autoComplete?: string
  ) => {
    const fieldError = touched[field as keyof FormTouched] ? errors[field] : undefined;
    const hasError = !!fieldError;
    
    return (
      <div className="space-y-2">
        <label 
          htmlFor={field} 
          className="block text-sm font-medium text-gray-700 dark:text-gray-300"
        >
          {label}
          <span className="text-red-500 ml-1" aria-hidden="true">*</span>
        </label>
        
        <div className="relative">
          <input
            ref={ref}
            id={field}
            name={field}
            type={type}
            value={formData[field]}
            onChange={(e) => handleInputChange(field, e.target.value)}
            onBlur={() => handleFieldBlur(field as keyof FormTouched)}
            onKeyDown={(e) => {
              if (field === 'email') {
                handleKeyDown(e, passwordRef);
              } else if (field === 'password') {
                handleKeyDown(e, submitButtonRef);
              }
            }}
            placeholder={placeholder}
            autoComplete={autoComplete}
            disabled={isFormDisabled}
            required
            aria-invalid={hasError}
            aria-describedby={hasError ? `${field}-error` : undefined}
            className={`
              block w-full px-3 py-2 border rounded-md shadow-sm 
              placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
              disabled:bg-gray-50 disabled:text-gray-500 disabled:cursor-not-allowed
              ${hasError 
                ? 'border-red-300 focus:ring-red-500 focus:border-red-500' 
                : 'border-gray-300 dark:border-gray-600'
              }
              dark:bg-gray-700 dark:text-white dark:placeholder-gray-400
            `}
          />
          
          {/* Password visibility toggle */}
          {field === 'password' && (
            <button
              type="button"
              onClick={handleTogglePassword}
              disabled={isFormDisabled}
              className="absolute inset-y-0 right-0 pr-3 flex items-center"
              aria-label={showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}
            >
              <span className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
                {showPassword ? (
                  <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
                  </svg>
                ) : (
                  <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                )}
              </span>
            </button>
          )}
        </div>
        
        {/* Error message */}
        {hasError && (
          <p 
            id={`${field}-error`}
            role="alert"
            className="text-sm text-red-600 dark:text-red-400"
          >
            {fieldError}
          </p>
        )}
      </div>
    );
  };

  // ============================================================================
  // RENDER
  // ============================================================================

  return (
    <div className={`w-full max-w-md mx-auto ${className}`}>
      <form onSubmit={handleSubmit} className="space-y-6" noValidate>
        {/* Form Title */}
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Iniciar Sesión
          </h2>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Ingresa a tu cuenta para continuar
          </p>
        </div>

        {/* General Error Message */}
        {(errors.general || error) && (
          <div 
            role="alert"
            className="rounded-md bg-red-50 dark:bg-red-900/20 p-4 border border-red-200 dark:border-red-800"
          >
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-800 dark:text-red-200">
                  {errors.general || error}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Form Fields */}
        <div className="space-y-4">
          {renderInputField(
            'email',
            'Correo Electrónico',
            'email',
            'tu@ejemplo.com',
            emailRef,
            'email'
          )}

          {renderInputField(
            'password',
            'Contraseña',
            showPassword ? 'text' : 'password',
            'Ingresa tu contraseña',
            passwordRef,
            'current-password'
          )}
        </div>

        {/* Forgot Password Link */}
        {onForgotPassword && (
          <div className="text-right">
            <button
              type="button"
              onClick={onForgotPassword}
              disabled={isFormDisabled}
              className="text-sm text-blue-600 hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300 disabled:opacity-50"
            >
              ¿Olvidaste tu contraseña?
            </button>
          </div>
        )}

        {/* Submit Button */}
        <LoadingButton
          ref={submitButtonRef}
          type="submit"
          loading={isLoading}
          loadingText="Iniciando sesión..."
          disabled={!canSubmit}
          className={`
            w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white
            focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
            disabled:opacity-50 disabled:cursor-not-allowed
            transition-colors duration-200
            ${canSubmit
              ? 'bg-blue-600 hover:bg-blue-700 active:bg-blue-800'
              : 'bg-gray-400 dark:bg-gray-600'
            }
          `}
        >
          Iniciar Sesión
        </LoadingButton>

        {/* Divider */}
        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-300 dark:border-gray-600" />
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white dark:bg-gray-800 text-gray-500 dark:text-gray-400">
              O continúa con
            </span>
          </div>
        </div>

        {/* Google OAuth Button */}
        <GoogleAuthButtonAlternative
          onSuccess={handleGoogleSuccess}
          onError={handleGoogleError}
          disabled={isFormDisabled}
        />

        {/* Register Link */}
        {onRegister && (
          <div className="text-center">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              ¿No tienes cuenta?{' '}
              <button
                type="button"
                onClick={onRegister}
                disabled={isFormDisabled}
                className="text-blue-600 hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300 font-medium disabled:opacity-50"
              >
                Regístrate aquí
              </button>
            </p>
          </div>
        )}
      </form>
    </div>
  );
};

export default LoginForm;