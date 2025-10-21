/**
 * Responsive Authentication Forms with Mobile-First Design.
 * 
 * Enhanced authentication forms optimized for mobile devices with
 * touch-friendly interactions, responsive breakpoints, and 
 * adaptive layouts.
 */

'use client';

import React, { useState, useCallback, useRef, useEffect } from 'react';
import { RegisterRequest, LoginRequest, AuthStatus } from '../../types/auth';
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
import {
  useFocusManager,
  useAccessibilityPreferences,
  useKeyboardNavigation,
  ScreenReaderOnly,
  KeyCodes
} from '@/utils/accessibility';

// ============================================================================
// RESPONSIVE UTILITIES
// ============================================================================

/**
 * Hook to detect mobile viewport
 */
const useIsMobile = () => {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkIsMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };

    checkIsMobile();
    window.addEventListener('resize', checkIsMobile);
    return () => window.removeEventListener('resize', checkIsMobile);
  }, []);

  return isMobile;
};

/**
 * Hook to detect touch device
 */
const useIsTouchDevice = () => {
  const [isTouch, setIsTouch] = useState(false);

  useEffect(() => {
    setIsTouch('ontouchstart' in window || navigator.maxTouchPoints > 0);
  }, []);

  return isTouch;
};

// ============================================================================
// RESPONSIVE REGISTER FORM COMPONENT
// ============================================================================

interface ResponsiveRegisterFormProps {
  onSubmit: (data: RegisterRequest) => Promise<void>;
  authStatus?: AuthStatus;
  error?: string | null;
  disabled?: boolean;
  className?: string;
  onSwitchToLogin?: () => void;
}

export const ResponsiveRegisterForm: React.FC<ResponsiveRegisterFormProps> = ({
  onSubmit,
  authStatus = AuthStatus.IDLE,
  error,
  disabled = false,
  className = '',
  onSwitchToLogin
}) => {
  // ============================================================================
  // RESPONSIVE HOOKS
  // ============================================================================

  const isMobile = useIsMobile();
  const isTouch = useIsTouchDevice();
  const { announce } = useFocusManager();
  const { prefersReducedMotion } = useAccessibilityPreferences();
  const titleRef = useRef<HTMLHeadingElement>(null);
  
  // ============================================================================
  // FORM STATE AND VALIDATION
  // ============================================================================

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  
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
        ValidationRules.name('El nombre debe tener entre 2 y 50 caracteres')
      ],
      email: [
        ValidationRules.required('El email es obligatorio'),
        ValidationRules.email('Ingresa una dirección de email válida')
      ],
      password: [
        ValidationRules.required('La contraseña es obligatoria'),
        ValidationRules.strongPassword()
      ],
      confirmPassword: [
        ValidationRules.required('Confirma tu contraseña')
      ]
    }
  );

  const { signInWithGoogle, loading: isGoogleLoading } = useGoogleAuth();

  // Focus management
  useEffect(() => {
    if (titleRef.current && !isMobile) {
      titleRef.current.focus();
    }
  }, [isMobile]);

  // ============================================================================
  // KEYBOARD NAVIGATION
  // ============================================================================

  const keyboardHandlers = useKeyboardNavigation({
    [KeyCodes.ESCAPE]: useCallback(() => {
      if (onSwitchToLogin) {
        announce('Cambiando a formulario de inicio de sesión');
        onSwitchToLogin();
      }
    }, [onSwitchToLogin, announce])
  });

  // ============================================================================
  // HANDLERS
  // ============================================================================

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    updateField(name, value);
    
    if (submitError) {
      setSubmitError(null);
    }
  }, [updateField, submitError]);

  const handleInputBlur = useCallback((e: React.FocusEvent<HTMLInputElement>) => {
    const { name } = e.target;
    handleFieldBlur(name);
  }, [handleFieldBlur]);

  const onFormSubmit = handleSubmit(async (values) => {
    try {
      setIsSubmitting(true);
      setSubmitError(null);
      announce('Procesando registro...', 'assertive');

      const registerData: RegisterRequest = {
        name: values.name.trim(),
        email: values.email.trim().toLowerCase(),
        password: values.password
      };

      await onSubmit(registerData);
      announce('Registro exitoso', 'assertive');
    } catch (error) {
      const errorMessage = error instanceof Error 
        ? error.message 
        : 'Error al registrar usuario. Por favor intenta de nuevo.';
      
      setSubmitError(errorMessage);
      announce(`Error: ${errorMessage}`, 'assertive');
    } finally {
      setIsSubmitting(false);
    }
  });

  const handleGoogleSuccess = useCallback(async (token: string) => {
    try {
      setSubmitError(null);
      announce('Autenticando con Google...', 'assertive');
      await signInWithGoogle(token);
      announce('Autenticación con Google exitosa', 'assertive');
    } catch (error) {
      const errorMessage = 'Error al autenticar con Google. Por favor intenta de nuevo.';
      setSubmitError(errorMessage);
      announce(`Error: ${errorMessage}`, 'assertive');
    }
  }, [signInWithGoogle, announce]);

  const handleGoogleError = useCallback((error: string) => {
    const errorMessage = 'Error al autenticar con Google. Por favor intenta de nuevo.';
    setSubmitError(errorMessage);
    announce(`Error: ${errorMessage}`, 'assertive');
  }, [announce]);

  // ============================================================================
  // RESPONSIVE STYLES
  // ============================================================================

  // Mobile-optimized input classes
  const getInputClasses = (fieldName: string): string => {
    const baseClasses = `block w-full border rounded-md shadow-sm placeholder-gray-400 
      focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 
      disabled:bg-gray-100 disabled:cursor-not-allowed
      ${isTouch ? 'px-4 py-3 text-base min-h-[48px]' : 'px-3 py-2 text-sm'}
      ${prefersReducedMotion ? '' : 'transition-colors duration-200'}`;
    return getFieldClassName(fieldName, baseClasses);
  };

  // Responsive container classes
  const containerClasses = isMobile 
    ? 'min-h-screen flex items-center justify-center px-4 py-6 bg-gray-50'
    : 'max-w-md mx-auto';

  const cardClasses = isMobile
    ? 'w-full max-w-sm bg-white rounded-lg shadow-lg p-6'
    : 'bg-white py-8 px-4 shadow-lg rounded-lg sm:px-10';

  const isLoading = isSubmitting || isGoogleLoading || authStatus === AuthStatus.LOADING;
  const shouldDisable = disabled || isLoading;
  const displayError = error || submitError;

  // ============================================================================
  // ANNOUNCE ERRORS
  // ============================================================================

  useEffect(() => {
    if (displayError) {
      announce(`Error de registro: ${displayError}`, 'assertive');
    }
  }, [displayError, announce]);

  // ============================================================================
  // RENDER
  // ============================================================================

  return (
    <div className={`${containerClasses} ${className}`} {...keyboardHandlers}>
      <div className={cardClasses}>
        {/* Header */}
        <div className="text-center mb-6">
          <h1 
            ref={titleRef}
            tabIndex={-1}
            className={`${isMobile ? 'text-2xl' : 'text-3xl'} font-extrabold text-gray-900 dark:text-white mb-2`}
          >
            Crear cuenta
          </h1>
          <p className={`${isMobile ? 'text-sm' : 'text-base'} text-gray-600 dark:text-gray-400`}>
            ¿Ya tienes una cuenta?{' '}
            <button
              type="button"
              onClick={onSwitchToLogin}
              disabled={shouldDisable}
              className="font-medium text-blue-600 hover:text-blue-500 dark:text-blue-400 
                dark:hover:text-blue-300 focus:outline-none focus:underline 
                disabled:opacity-50 disabled:cursor-not-allowed
                transition-colors duration-200"
              aria-label="Cambiar a formulario de inicio de sesión"
            >
              Inicia sesión aquí
            </button>
          </p>
        </div>

        {/* Google Authentication */}
        <div className="mb-6">
          <GoogleAuthButton
            onSuccess={handleGoogleSuccess}
            onError={handleGoogleError}
            loading={isGoogleLoading}
            disabled={shouldDisable}
            text="Registrarse con Google"
            size={isMobile ? 'lg' : 'md'}
          />
        </div>

        <div className="relative mb-6" role="separator" aria-label="O regístrate con email">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-300 dark:border-gray-600" />
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white dark:bg-gray-800 text-gray-500 dark:text-gray-400">
              O regístrate con email
            </span>
          </div>
        </div>

        <form 
          className={`space-y-${isMobile ? '5' : '6'}`}
          onSubmit={onFormSubmit}
          noValidate
          aria-label="Formulario de registro"
        >
          {/* Error Alert */}
          {displayError && (
            <div 
              className="bg-red-50 border border-red-300 text-red-700 px-4 py-3 rounded-md"
              role="alert"
              aria-atomic="true"
            >
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg 
                    className="h-5 w-5 text-red-400" 
                    viewBox="0 0 20 20" 
                    fill="currentColor"
                    aria-hidden="true"
                  >
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
              className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
            >
              Nombre completo
              <span className="text-red-500 ml-1" aria-label="required">*</span>
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
              placeholder="Tu nombre completo"
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
              className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
            >
              Dirección de email
              <span className="text-red-500 ml-1" aria-label="required">*</span>
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
              className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
            >
              Contraseña
              <span className="text-red-500 ml-1" aria-label="required">*</span>
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
              placeholder="Crea una contraseña segura"
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
            {fields.password?.value && (
              <PasswordStrengthIndicator 
                password={fields.password.value} 
                className="mt-2"
              />
            )}
          </div>

          {/* Confirm Password Field */}
          <div>
            <label 
              htmlFor="confirmPassword" 
              className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
            >
              Confirmar contraseña
              <span className="text-red-500 ml-1" aria-label="required">*</span>
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

          {/* Form Status for Screen Readers */}
          <ScreenReaderOnly>
            <div aria-live="polite" aria-atomic="true">
              {isLoading && 'Procesando registro...'}
              {!isFormValid && 'Completa todos los campos requeridos'}
              {isFormValid && !isLoading && 'Formulario válido, listo para enviar'}
            </div>
          </ScreenReaderOnly>

          {/* Submit Button */}
          <div className={isMobile ? 'pt-2' : 'pt-4'}>
            <LoadingButton
              type="submit"
              loading={isSubmitting}
              disabled={shouldDisable || !isFormValid}
              className={`w-full flex justify-center border border-transparent 
                rounded-md shadow-sm font-medium text-white bg-blue-600 
                hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 
                focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed 
                transition-colors duration-200
                ${isTouch ? 'py-3 px-4 text-base min-h-[48px]' : 'py-2 px-4 text-sm'}`}
              loadingText="Creando cuenta..."
              aria-describedby={!isFormValid ? 'form-invalid-help' : undefined}
            >
              Crear cuenta
            </LoadingButton>
            
            {!isFormValid && (
              <div id="form-invalid-help" className="sr-only">
                Completa todos los campos requeridos antes de crear la cuenta
              </div>
            )}
          </div>
        </form>

        {/* Terms and Privacy */}
        <nav className={`${isMobile ? 'mt-4 text-xs' : 'mt-6 text-xs'} text-center text-gray-500 dark:text-gray-400`}>
          Al registrarte, aceptas nuestros{' '}
          <a 
            href="/terms" 
            className="text-blue-600 hover:text-blue-500 dark:text-blue-400 focus:outline-none focus:underline"
            target="_blank"
            rel="noopener noreferrer"
          >
            Términos de Servicio
          </a>{' '}
          y{' '}
          <a 
            href="/privacy" 
            className="text-blue-600 hover:text-blue-500 dark:text-blue-400 focus:outline-none focus:underline"
            target="_blank"
            rel="noopener noreferrer"
          >
            Política de Privacidad
          </a>
        </nav>
      </div>
    </div>
  );
};

// ============================================================================
// RESPONSIVE LOGIN FORM COMPONENT
// ============================================================================

interface ResponsiveLoginFormProps {
  onSubmit: (data: LoginRequest) => Promise<void>;
  authStatus?: AuthStatus;
  error?: string | null;
  disabled?: boolean;
  className?: string;
  onSwitchToRegister?: () => void;
  onForgotPassword?: () => void;
}

export const ResponsiveLoginForm: React.FC<ResponsiveLoginFormProps> = ({
  onSubmit,
  authStatus = AuthStatus.IDLE,
  error,
  disabled = false,
  className = '',
  onSwitchToRegister,
  onForgotPassword
}) => {
  // ============================================================================
  // RESPONSIVE HOOKS
  // ============================================================================

  const isMobile = useIsMobile();
  const isTouch = useIsTouchDevice();
  const { announce } = useFocusManager();
  const { prefersReducedMotion } = useAccessibilityPreferences();
  const titleRef = useRef<HTMLHeadingElement>(null);
  
  // ============================================================================
  // FORM STATE AND VALIDATION
  // ============================================================================

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  
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
      email: '',
      password: ''
    },
    {
      email: [
        ValidationRules.required('El email es obligatorio'),
        ValidationRules.email('Ingresa una dirección de email válida')
      ],
      password: [
        ValidationRules.required('La contraseña es obligatoria')
      ]
    }
  );

  const { signInWithGoogle, loading: isGoogleLoading } = useGoogleAuth();

  // Focus management
  useEffect(() => {
    if (titleRef.current && !isMobile) {
      titleRef.current.focus();
    }
  }, [isMobile]);

  // ============================================================================
  // KEYBOARD NAVIGATION
  // ============================================================================

  const keyboardHandlers = useKeyboardNavigation({
    [KeyCodes.ESCAPE]: useCallback(() => {
      if (onSwitchToRegister) {
        announce('Cambiando a formulario de registro');
        onSwitchToRegister();
      }
    }, [onSwitchToRegister, announce])
  });

  // ============================================================================
  // HANDLERS
  // ============================================================================

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    updateField(name, value);
    
    if (submitError) {
      setSubmitError(null);
    }
  }, [updateField, submitError]);

  const handleInputBlur = useCallback((e: React.FocusEvent<HTMLInputElement>) => {
    const { name } = e.target;
    handleFieldBlur(name);
  }, [handleFieldBlur]);

  const onFormSubmit = handleSubmit(async (values) => {
    try {
      setIsSubmitting(true);
      setSubmitError(null);
      announce('Iniciando sesión...', 'assertive');

      const loginData: LoginRequest = {
        email: values.email.trim().toLowerCase(),
        password: values.password
      };

      await onSubmit(loginData);
      announce('Inicio de sesión exitoso', 'assertive');
    } catch (error) {
      const errorMessage = error instanceof Error 
        ? error.message 
        : 'Error al iniciar sesión. Por favor intenta de nuevo.';
      
      setSubmitError(errorMessage);
      announce(`Error: ${errorMessage}`, 'assertive');
    } finally {
      setIsSubmitting(false);
    }
  });

  const handleGoogleSuccess = useCallback(async (token: string) => {
    try {
      setSubmitError(null);
      announce('Autenticando con Google...', 'assertive');
      await signInWithGoogle(token);
      announce('Autenticación con Google exitosa', 'assertive');
    } catch (error) {
      const errorMessage = 'Error al autenticar con Google. Por favor intenta de nuevo.';
      setSubmitError(errorMessage);
      announce(`Error: ${errorMessage}`, 'assertive');
    }
  }, [signInWithGoogle, announce]);

  const handleGoogleError = useCallback((error: string) => {
    const errorMessage = 'Error al autenticar con Google. Por favor intenta de nuevo.';
    setSubmitError(errorMessage);
    announce(`Error: ${errorMessage}`, 'assertive');
  }, [announce]);

  // ============================================================================
  // RESPONSIVE STYLES
  // ============================================================================

  // Mobile-optimized input classes
  const getInputClasses = (fieldName: string): string => {
    const baseClasses = `block w-full border rounded-md shadow-sm placeholder-gray-400 
      focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 
      disabled:bg-gray-100 disabled:cursor-not-allowed
      ${isTouch ? 'px-4 py-3 text-base min-h-[48px]' : 'px-3 py-2 text-sm'}
      ${prefersReducedMotion ? '' : 'transition-colors duration-200'}`;
    return getFieldClassName(fieldName, baseClasses);
  };

  // Responsive container classes
  const containerClasses = isMobile 
    ? 'min-h-screen flex items-center justify-center px-4 py-6 bg-gray-50'
    : 'max-w-md mx-auto';

  const cardClasses = isMobile
    ? 'w-full max-w-sm bg-white rounded-lg shadow-lg p-6'
    : 'bg-white py-8 px-4 shadow-lg rounded-lg sm:px-10';

  const isLoading = isSubmitting || isGoogleLoading || authStatus === AuthStatus.LOADING;
  const shouldDisable = disabled || isLoading;
  const displayError = error || submitError;

  // ============================================================================
  // ANNOUNCE ERRORS
  // ============================================================================

  useEffect(() => {
    if (displayError) {
      announce(`Error de inicio de sesión: ${displayError}`, 'assertive');
    }
  }, [displayError, announce]);

  // ============================================================================
  // RENDER
  // ============================================================================

  return (
    <div className={`${containerClasses} ${className}`} {...keyboardHandlers}>
      <div className={cardClasses}>
        {/* Header */}
        <div className="text-center mb-6">
          <h1 
            ref={titleRef}
            tabIndex={-1}
            className={`${isMobile ? 'text-2xl' : 'text-3xl'} font-extrabold text-gray-900 dark:text-white mb-2`}
          >
            Iniciar sesión
          </h1>
          <p className={`${isMobile ? 'text-sm' : 'text-base'} text-gray-600 dark:text-gray-400`}>
            ¿No tienes una cuenta?{' '}
            <button
              type="button"
              onClick={onSwitchToRegister}
              disabled={shouldDisable}
              className="font-medium text-blue-600 hover:text-blue-500 dark:text-blue-400 
                dark:hover:text-blue-300 focus:outline-none focus:underline 
                disabled:opacity-50 disabled:cursor-not-allowed
                transition-colors duration-200"
              aria-label="Cambiar a formulario de registro"
            >
              Regístrate aquí
            </button>
          </p>
        </div>

        {/* Google Authentication */}
        <div className="mb-6">
          <GoogleAuthButton
            onSuccess={handleGoogleSuccess}
            onError={handleGoogleError}
            loading={isGoogleLoading}
            disabled={shouldDisable}
            text="Iniciar sesión con Google"
            size={isMobile ? 'lg' : 'md'}
          />
        </div>

        <div className="relative mb-6" role="separator" aria-label="O inicia sesión con email">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-300 dark:border-gray-600" />
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white dark:bg-gray-800 text-gray-500 dark:text-gray-400">
              O inicia sesión con email
            </span>
          </div>
        </div>

        <form 
          className={`space-y-${isMobile ? '5' : '6'}`}
          onSubmit={onFormSubmit}
          noValidate
          aria-label="Formulario de inicio de sesión"
        >
          {/* Error Alert */}
          {displayError && (
            <div 
              className="bg-red-50 border border-red-300 text-red-700 px-4 py-3 rounded-md"
              role="alert"
              aria-atomic="true"
            >
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg 
                    className="h-5 w-5 text-red-400" 
                    viewBox="0 0 20 20" 
                    fill="currentColor"
                    aria-hidden="true"
                  >
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium">Error de inicio de sesión</h3>
                  <p className="mt-1 text-sm">{displayError}</p>
                </div>
              </div>
            </div>
          )}

          {/* Email Field */}
          <div>
            <label 
              htmlFor="email" 
              className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
            >
              Dirección de email
              <span className="text-red-500 ml-1" aria-label="required">*</span>
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
            <div className="flex justify-between items-center mb-1">
              <label 
                htmlFor="password" 
                className="block text-sm font-medium text-gray-700 dark:text-gray-300"
              >
                Contraseña
                <span className="text-red-500 ml-1" aria-label="required">*</span>
              </label>
              {onForgotPassword && (
                <button
                  type="button"
                  onClick={onForgotPassword}
                  disabled={shouldDisable}
                  className="text-sm text-blue-600 hover:text-blue-500 dark:text-blue-400 
                    dark:hover:text-blue-300 focus:outline-none focus:underline 
                    disabled:opacity-50 transition-colors duration-200"
                  aria-label="Recuperar contraseña olvidada"
                >
                  ¿Olvidaste tu contraseña?
                </button>
              )}
            </div>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              required
              value={fields.password?.value || ''}
              onChange={handleInputChange}
              onBlur={handleInputBlur}
              disabled={shouldDisable}
              className={getInputClasses('password')}
              placeholder="Tu contraseña"
              aria-invalid={!isFieldValid('password')}
              aria-describedby={getFieldError('password') ? 'password-error' : undefined}
            />
            <FieldError error={getFieldError('password')} />
            {getFieldWarnings('password').map((warning, index) => (
              <FieldWarning key={index} warning={warning} />
            ))}
          </div>

          {/* Remember Me */}
          {!isMobile && (
            <div className="flex items-center">
              <input
                id="remember-me"
                name="remember-me"
                type="checkbox"
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 
                  rounded disabled:opacity-50"
                disabled={shouldDisable}
              />
              <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-900 dark:text-gray-300">
                Recordarme
              </label>
            </div>
          )}

          {/* Form Status for Screen Readers */}
          <ScreenReaderOnly>
            <div aria-live="polite" aria-atomic="true">
              {isLoading && 'Iniciando sesión...'}
              {!isFormValid && 'Completa todos los campos requeridos'}
              {isFormValid && !isLoading && 'Formulario válido, listo para enviar'}
            </div>
          </ScreenReaderOnly>

          {/* Submit Button */}
          <div className={isMobile ? 'pt-2' : 'pt-4'}>
            <LoadingButton
              type="submit"
              loading={isSubmitting}
              disabled={shouldDisable || !isFormValid}
              className={`w-full flex justify-center border border-transparent 
                rounded-md shadow-sm font-medium text-white bg-blue-600 
                hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 
                focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed 
                transition-colors duration-200
                ${isTouch ? 'py-3 px-4 text-base min-h-[48px]' : 'py-2 px-4 text-sm'}`}
              loadingText="Iniciando sesión..."
              aria-describedby={!isFormValid ? 'form-invalid-help' : undefined}
            >
              Iniciar sesión
            </LoadingButton>
            
            {!isFormValid && (
              <div id="form-invalid-help" className="sr-only">
                Completa todos los campos requeridos antes de iniciar sesión
              </div>
            )}
          </div>
        </form>

        {/* Terms and Privacy */}
        <nav className={`${isMobile ? 'mt-4 text-xs' : 'mt-6 text-xs'} text-center text-gray-500 dark:text-gray-400`}>
          Al iniciar sesión, aceptas nuestros{' '}
          <a 
            href="/terms" 
            className="text-blue-600 hover:text-blue-500 dark:text-blue-400 focus:outline-none focus:underline"
            target="_blank"
            rel="noopener noreferrer"
          >
            Términos de Servicio
          </a>{' '}
          y{' '}
          <a 
            href="/privacy" 
            className="text-blue-600 hover:text-blue-500 dark:text-blue-400 focus:outline-none focus:underline"
            target="_blank"
            rel="noopener noreferrer"
          >
            Política de Privacidad
          </a>
        </nav>
      </div>
    </div>
  );
};

export default {
  ResponsiveRegisterForm,
  ResponsiveLoginForm
};