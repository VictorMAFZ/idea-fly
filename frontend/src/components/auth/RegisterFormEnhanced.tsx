/**
 * Enhanced RegisterForm Component with Real-time Validation.
 * 
 * A comprehensive user registration form with real-time validation, 
 * accessibility features, and enhanced user experience.
 */

'use client';

import React, { useState, useCallback } from 'react';
import { RegisterRequest, AuthStatus } from '../../types/auth';
import { GoogleAuthButton } from './GoogleAuthButton';
import { useGoogleAuth } from '../../hooks/useGoogleAuth';
import { LoadingButton } from '../LoadingComponents';
import { 
  useFormValidation, 
  ValidationRules, 
  FieldError, 
  FieldWarning, 
  PasswordStrengthIndicator 
} from '@/utils/validation';

// ============================================================================
// TYPES AND INTERFACES
// ============================================================================

/**
 * RegisterForm component props
 */
export interface RegisterFormProps {
  /** Called when user submits valid registration data */
  onSubmit: (data: RegisterRequest) => Promise<void>;
  /** Current authentication status */
  authStatus?: AuthStatus;
  /** External error message to display */
  error?: string | null;
  /** Whether form should be disabled */
  disabled?: boolean;
  /** Additional CSS classes */
  className?: string;
  /** Callback when user wants to switch to login */
  onSwitchToLogin?: () => void;
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

/**
 * Enhanced RegisterForm Component with Real-time Validation
 */
export const RegisterForm: React.FC<RegisterFormProps> = ({
  onSubmit,
  authStatus = AuthStatus.IDLE,
  error,
  disabled = false,
  className = '',
  onSwitchToLogin
}) => {
  // ============================================================================
  // STATE AND VALIDATION
  // ============================================================================

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  
  // Initialize form validation with rules
  const {
    fields,
    isFormValid,
    updateField,
    handleFieldBlur,
    getFieldError,
    getFieldWarnings,
    isFieldValid,
    getFieldClassName,
    handleSubmit,
    resetForm
  } = useFormValidation(
    {
      name: '',
      email: '',
      password: '',
      confirmPassword: ''
    },
    {
      name: [
        ValidationRules.required('El nombre es obligatorio'),
        ValidationRules.name('El nombre debe tener entre 2 y 50 caracteres y solo contener letras')
      ],
      email: [
        ValidationRules.required('El email es obligatorio'),
        ValidationRules.email('Ingresa una dirección de email válida')
      ],
      password: [
        ValidationRules.required('La contraseña es obligatoria'),
        ValidationRules.strongPassword()
      ]
    }
  );

  // Add dynamic validation for confirm password
  const validationRules = {
    ...{
      name: [
        ValidationRules.required('El nombre es obligatorio'),
        ValidationRules.name('El nombre debe tener entre 2 y 50 caracteres y solo contener letras')
      ],
      email: [
        ValidationRules.required('El email es obligatorio'),
        ValidationRules.email('Ingresa una dirección de email válida')
      ],
      password: [
        ValidationRules.required('La contraseña es obligatoria'),
        ValidationRules.strongPassword()
      ]
    },
    confirmPassword: [
      ValidationRules.required('Confirma tu contraseña'),
      ValidationRules.confirmPassword(
        fields.password?.value || '', 
        'Las contraseñas no coinciden'
      )
    ]
  };

  // Google Auth integration
  const { signInWithGoogle, loading: isGoogleLoading, error: googleError } = useGoogleAuth();

  // ============================================================================
  // HANDLERS
  // ============================================================================

  /**
   * Handle input change with real-time validation
   */
  const handleInputChange = useCallback((
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const { name, value } = e.target;
    updateField(name, value);
    
    // Clear submit error when user starts typing
    if (submitError) {
      setSubmitError(null);
    }
  }, [updateField, submitError]);

  /**
   * Handle input blur for more thorough validation
   */
  const handleInputBlur = useCallback((
    e: React.FocusEvent<HTMLInputElement>
  ) => {
    const { name } = e.target;
    handleFieldBlur(name);
  }, [handleFieldBlur]);

  /**
   * Handle form submission
   */
  const onFormSubmit = handleSubmit(async (values) => {
    try {
      setIsSubmitting(true);
      setSubmitError(null);

      const registerData: RegisterRequest = {
        name: values.name.trim(),
        email: values.email.trim().toLowerCase(),
        password: values.password
      };

      await onSubmit(registerData);
    } catch (error) {
      console.error('Registration error:', error);
      setSubmitError(
        error instanceof Error 
          ? error.message 
          : 'Error al registrar usuario. Por favor intenta de nuevo.'
      );
    } finally {
      setIsSubmitting(false);
    }
  });

  /**
   * Handle Google authentication success
   */
  const handleGoogleSuccess = useCallback(async (token: string) => {
    try {
      setSubmitError(null);
      await signInWithGoogle(token);
    } catch (error) {
      console.error('Google auth error:', error);
      setSubmitError('Error al autenticar con Google. Por favor intenta de nuevo.');
    }
  }, [signInWithGoogle]);

  /**
   * Handle Google authentication error
   */
  const handleGoogleError = useCallback((error: string) => {
    console.error('Google auth error:', error);
    setSubmitError('Error al autenticar con Google. Por favor intenta de nuevo.');
  }, []);

  // ============================================================================
  // RENDER HELPERS
  // ============================================================================

  /**
   * Get input field CSS classes with validation styling
   */
  const getInputClasses = (fieldName: string): string => {
    const baseClasses = 'mt-1 block w-full px-3 py-2 border rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2 sm:text-sm transition-colors duration-200 disabled:bg-gray-100 disabled:cursor-not-allowed';
    return getFieldClassName(fieldName, baseClasses);
  };

  const isLoading = isSubmitting || isGoogleLoading || authStatus === AuthStatus.LOADING;
  const shouldDisable = disabled || isLoading;
  const displayError = error || submitError;

  // ============================================================================
  // RENDER
  // ============================================================================

  return (
    <div className={`max-w-md mx-auto ${className}`}>
      <div className="bg-white dark:bg-gray-800 py-8 px-4 shadow-lg rounded-lg sm:px-10">
        {/* Header */}
        <div className="sm:mx-auto sm:w-full sm:max-w-md">
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900 dark:text-white">
            Crear cuenta
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
            ¿Ya tienes una cuenta?{' '}
            <button
              type="button"
              onClick={onSwitchToLogin}
              className="font-medium text-blue-600 hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300 transition-colors duration-200"
              disabled={shouldDisable}
            >
              Inicia sesión aquí
            </button>
          </p>
        </div>

        {/* Form */}
        <div className="mt-8">
          {/* Google Authentication */}
          <GoogleAuthButton
            onSuccess={handleGoogleSuccess}
            onError={handleGoogleError}
            loading={isGoogleLoading}
            disabled={shouldDisable}
            text="Registrarse con Google"
            className="mb-6"
          />

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300 dark:border-gray-600" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white dark:bg-gray-800 text-gray-500 dark:text-gray-400">
                O regístrate con email
              </span>
            </div>
          </div>

          <form className="space-y-6 mt-6" onSubmit={onFormSubmit}>
            {/* General Error Display */}
            {displayError && (
              <div 
                className="bg-red-50 border border-red-300 text-red-700 px-4 py-3 rounded-md"
                role="alert"
              >
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium">Error de registro</h3>
                    <p className="mt-1 text-sm">{displayError}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Name Field */}
            <div>
              <label 
                htmlFor="name" 
                className="block text-sm font-medium text-gray-700 dark:text-gray-300"
              >
                Nombre completo
              </label>
              <input
                id="name"
                name="name"
                type="text"
                autoComplete="name"
                required
                value={fields.name?.value || ''}
                onChange={handleInputChange}
                onBlur={handleInputBlur}
                disabled={shouldDisable}
                className={getInputClasses('name')}
                placeholder="Ingresa tu nombre completo"
                aria-invalid={!isFieldValid('name')}
                aria-describedby={getFieldError('name') ? 'name-error' : undefined}
              />
              <FieldError error={getFieldError('name')} />
              {getFieldWarnings('name').map((warning, index) => (
                <FieldWarning key={index} warning={warning} />
              ))}
            </div>

            {/* Email Field */}
            <div>
              <label 
                htmlFor="email" 
                className="block text-sm font-medium text-gray-700 dark:text-gray-300"
              >
                Dirección de email
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={fields.email?.value || ''}
                onChange={handleInputChange}
                onBlur={handleInputBlur}
                disabled={shouldDisable}
                className={getInputClasses('email')}
                placeholder="correo@ejemplo.com"
                aria-invalid={!isFieldValid('email')}
                aria-describedby={getFieldError('email') ? 'email-error' : undefined}
              />
              <FieldError error={getFieldError('email')} />
              {getFieldWarnings('email').map((warning, index) => (
                <FieldWarning key={index} warning={warning} />
              ))}
            </div>

            {/* Password Field */}
            <div>
              <label 
                htmlFor="password" 
                className="block text-sm font-medium text-gray-700 dark:text-gray-300"
              >
                Contraseña
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="new-password"
                required
                value={fields.password?.value || ''}
                onChange={handleInputChange}
                onBlur={handleInputBlur}
                disabled={shouldDisable}
                className={getInputClasses('password')}
                placeholder="Mínimo 8 caracteres"
                aria-invalid={!isFieldValid('password')}
                aria-describedby={
                  getFieldError('password') ? 'password-error' : 'password-strength'
                }
              />
              <FieldError error={getFieldError('password')} />
              {getFieldWarnings('password').map((warning, index) => (
                <FieldWarning key={index} warning={warning} />
              ))}
              
              {/* Password Strength Indicator */}
              <PasswordStrengthIndicator 
                password={fields.password?.value || ''} 
                className="mt-2"
              />
            </div>

            {/* Confirm Password Field */}
            <div>
              <label 
                htmlFor="confirmPassword" 
                className="block text-sm font-medium text-gray-700 dark:text-gray-300"
              >
                Confirmar contraseña
              </label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                autoComplete="new-password"
                required
                value={fields.confirmPassword?.value || ''}
                onChange={handleInputChange}
                onBlur={handleInputBlur}
                disabled={shouldDisable}
                className={getInputClasses('confirmPassword')}
                placeholder="Confirma tu contraseña"
                aria-invalid={!isFieldValid('confirmPassword')}
                aria-describedby={getFieldError('confirmPassword') ? 'confirmPassword-error' : undefined}
              />
              <FieldError error={getFieldError('confirmPassword')} />
              {getFieldWarnings('confirmPassword').map((warning, index) => (
                <FieldWarning key={index} warning={warning} />
              ))}
            </div>

            {/* Submit Button */}
            <div>
              <LoadingButton
                type="submit"
                loading={isSubmitting}
                disabled={shouldDisable || !isFormValid}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
                loadingText="Creando cuenta..."
              >
                Crear cuenta
              </LoadingButton>
            </div>
          </form>

          {/* Terms and Privacy */}
          <p className="mt-6 text-xs text-center text-gray-500 dark:text-gray-400">
            Al registrarte, aceptas nuestros{' '}
            <a href="/terms" className="text-blue-600 hover:text-blue-500 dark:text-blue-400">
              Términos de Servicio
            </a>{' '}
            y{' '}
            <a href="/privacy" className="text-blue-600 hover:text-blue-500 dark:text-blue-400">
              Política de Privacidad
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default RegisterForm;