/**
 * Accessible Authentication Forms with WCAG 2.1 AA Compliance.
 * 
 * Enhanced authentication forms that include comprehensive accessibility features
 * including focus management, keyboard navigation, screen reader support,
 * and ARIA enhancements.
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
  useFocusOnMount,
  SkipLink,
  ScreenReaderOnly,
  FocusTrap,
  AccessibleFormField,
  KeyCodes
} from '@/utils/accessibility';

// ============================================================================
// ACCESSIBLE REGISTER FORM COMPONENT
// ============================================================================

interface AccessibleRegisterFormProps {
  onSubmit: (data: RegisterRequest) => Promise<void>;
  authStatus?: AuthStatus;
  error?: string | null;
  disabled?: boolean;
  className?: string;
  onSwitchToLogin?: () => void;
}

export const AccessibleRegisterForm: React.FC<AccessibleRegisterFormProps> = ({
  onSubmit,
  authStatus = AuthStatus.IDLE,
  error,
  disabled = false,
  className = '',
  onSwitchToLogin
}) => {
  // ============================================================================
  // ACCESSIBILITY SETUP
  // ============================================================================

  const { announce } = useFocusManager();
  const { prefersReducedMotion } = useAccessibilityPreferences();
  const formRef = useRef<HTMLFormElement>(null);
  const titleRef = useRef<HTMLHeadingElement>(null);
  
  // Focus title on mount
  useEffect(() => {
    if (titleRef.current) {
      titleRef.current.focus();
    }
  }, []);
  
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
        // Note: confirmPassword validation will be added dynamically
      ]
    }
  );

  const { signInWithGoogle, loading: isGoogleLoading } = useGoogleAuth();

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
  // DYNAMIC STYLES
  // ============================================================================

  const getInputClasses = (fieldName: string): string => {
    const baseClasses = `mt-1 block w-full px-3 py-2 border rounded-md shadow-sm 
      placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2 
      sm:text-sm disabled:bg-gray-100 disabled:cursor-not-allowed
      ${prefersReducedMotion ? '' : 'transition-colors duration-200'}`;
    return getFieldClassName(fieldName, baseClasses);
  };

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
    <div className={`max-w-md mx-auto ${className}`} {...keyboardHandlers}>
      {/* Skip Links */}
      <SkipLink href="#register-form">Saltar al formulario de registro</SkipLink>
      <SkipLink href="#google-auth">Saltar a autenticación con Google</SkipLink>

      <div className="bg-white dark:bg-gray-800 py-8 px-4 shadow-lg rounded-lg sm:px-10">
        {/* Header */}
        <div className="sm:mx-auto sm:w-full sm:max-w-md">
          <h1 
            ref={titleRef}
            tabIndex={-1}
            className="mt-6 text-center text-3xl font-extrabold text-gray-900 dark:text-white"
          >
            Crear cuenta
          </h1>
          <p className="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
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

        {/* Form */}
        <div className="mt-8">
          {/* Google Authentication */}
          <div id="google-auth" className="mb-6">
            <GoogleAuthButton
              onSuccess={handleGoogleSuccess}
              onError={handleGoogleError}
              loading={isGoogleLoading}
              disabled={shouldDisable}
              text="Registrarse con Google"
            />
          </div>

          <div className="relative" role="separator" aria-label="O regístrate con email">
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
            id="register-form"
            ref={formRef}
            className="space-y-6 mt-6" 
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
            <AccessibleFormField
              id="name"
              label="Nombre completo"
              required
              error={getFieldError('name')}
              helpText="Ingresa tu nombre completo para crear tu perfil"
            >
              <input
                name="name"
                type="text"
                autoComplete="name"
                value={fields.name?.value || ''}
                onChange={handleInputChange}
                onBlur={handleInputBlur}
                disabled={shouldDisable}
                className={getInputClasses('name')}
                placeholder="Tu nombre completo"
              />
            </AccessibleFormField>

            {/* Email Field */}
            <AccessibleFormField
              id="email"
              label="Dirección de email"
              required
              error={getFieldError('email')}
              helpText="Usaremos este email para enviar confirmaciones y notificaciones"
            >
              <input
                name="email"
                type="email"
                autoComplete="email"
                value={fields.email?.value || ''}
                onChange={handleInputChange}
                onBlur={handleInputBlur}
                disabled={shouldDisable}
                className={getInputClasses('email')}
                placeholder="correo@ejemplo.com"
              />
            </AccessibleFormField>

            {/* Password Field */}
            <AccessibleFormField
              id="password"
              label="Contraseña"
              required
              error={getFieldError('password')}
              helpText="Mínimo 8 caracteres con mayúsculas, minúsculas y números"
            >
              <input
                name="password"
                type="password"
                autoComplete="new-password"
                value={fields.password?.value || ''}
                onChange={handleInputChange}
                onBlur={handleInputBlur}
                disabled={shouldDisable}
                className={getInputClasses('password')}
                placeholder="Crea una contraseña segura"
              />
            </AccessibleFormField>

            {/* Password Strength Indicator */}
            {fields.password?.value && (
              <PasswordStrengthIndicator 
                password={fields.password.value} 
                className="mt-2"
              />
            )}

            {/* Confirm Password Field */}
            <AccessibleFormField
              id="confirmPassword"
              label="Confirmar contraseña"
              required
              error={getFieldError('confirmPassword')}
              helpText="Repite la contraseña para confirmar"
            >
              <input
                name="confirmPassword"
                type="password"
                autoComplete="new-password"
                value={fields.confirmPassword?.value || ''}
                onChange={handleInputChange}
                onBlur={handleInputBlur}
                disabled={shouldDisable}
                className={getInputClasses('confirmPassword')}
                placeholder="Confirma tu contraseña"
              />
            </AccessibleFormField>

            {/* Form Status */}
            <ScreenReaderOnly>
              <div aria-live="polite" aria-atomic="true">
                {isLoading && 'Procesando registro...'}
                {!isFormValid && 'Completa todos los campos requeridos'}
                {isFormValid && !isLoading && 'Formulario válido, listo para enviar'}
              </div>
            </ScreenReaderOnly>

            {/* Submit Button */}
            <div>
              <LoadingButton
                type="submit"
                loading={isSubmitting}
                disabled={shouldDisable || !isFormValid}
                className="w-full flex justify-center py-2 px-4 border border-transparent 
                  rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 
                  hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 
                  focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed 
                  transition-colors duration-200"
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
          <nav className="mt-6 text-xs text-center text-gray-500 dark:text-gray-400">
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
    </div>
  );
};

// ============================================================================
// ACCESSIBLE LOGIN FORM COMPONENT
// ============================================================================

interface AccessibleLoginFormProps {
  onSubmit: (data: LoginRequest) => Promise<void>;
  authStatus?: AuthStatus;
  error?: string | null;
  disabled?: boolean;
  className?: string;
  onSwitchToRegister?: () => void;
  onForgotPassword?: () => void;
}

export const AccessibleLoginForm: React.FC<AccessibleLoginFormProps> = ({
  onSubmit,
  authStatus = AuthStatus.IDLE,
  error,
  disabled = false,
  className = '',
  onSwitchToRegister,
  onForgotPassword
}) => {
  // ============================================================================
  // ACCESSIBILITY SETUP
  // ============================================================================

  const { announce } = useFocusManager();
  const { prefersReducedMotion } = useAccessibilityPreferences();
  const formRef = useRef<HTMLFormElement>(null);
  const titleRef = useRef<HTMLHeadingElement>(null);
  
  // Focus title on mount
  useEffect(() => {
    if (titleRef.current) {
      titleRef.current.focus();
    }
  }, []);
  
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
  // DYNAMIC STYLES
  // ============================================================================

  const getInputClasses = (fieldName: string): string => {
    const baseClasses = `mt-1 block w-full px-3 py-2 border rounded-md shadow-sm 
      placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2 
      sm:text-sm disabled:bg-gray-100 disabled:cursor-not-allowed
      ${prefersReducedMotion ? '' : 'transition-colors duration-200'}`;
    return getFieldClassName(fieldName, baseClasses);
  };

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
    <div className={`max-w-md mx-auto ${className}`} {...keyboardHandlers}>
      {/* Skip Links */}
      <SkipLink href="#login-form">Saltar al formulario de inicio de sesión</SkipLink>
      <SkipLink href="#google-auth">Saltar a autenticación con Google</SkipLink>

      <div className="bg-white dark:bg-gray-800 py-8 px-4 shadow-lg rounded-lg sm:px-10">
        {/* Header */}
        <div className="sm:mx-auto sm:w-full sm:max-w-md">
          <h1 
            ref={titleRef}
            tabIndex={-1}
            className="mt-6 text-center text-3xl font-extrabold text-gray-900 dark:text-white"
          >
            Iniciar sesión
          </h1>
          <p className="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
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

        {/* Form */}
        <div className="mt-8">
          {/* Google Authentication */}
          <div id="google-auth" className="mb-6">
            <GoogleAuthButton
              onSuccess={handleGoogleSuccess}
              onError={handleGoogleError}
              loading={isGoogleLoading}
              disabled={shouldDisable}
              text="Iniciar sesión con Google"
            />
          </div>

          <div className="relative" role="separator" aria-label="O inicia sesión con email">
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
            id="login-form"
            ref={formRef}
            className="space-y-6 mt-6" 
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
            <AccessibleFormField
              id="email"
              label="Dirección de email"
              required
              error={getFieldError('email')}
              helpText="El email que usaste para registrarte"
            >
              <input
                name="email"
                type="email"
                autoComplete="email"
                value={fields.email?.value || ''}
                onChange={handleInputChange}
                onBlur={handleInputBlur}
                disabled={shouldDisable}
                className={getInputClasses('email')}
                placeholder="correo@ejemplo.com"
              />
            </AccessibleFormField>

            {/* Password Field */}
            <AccessibleFormField
              id="password"
              label="Contraseña"
              required
              error={getFieldError('password')}
              helpText="Tu contraseña de cuenta"
            >
              <input
                name="password"
                type="password"
                autoComplete="current-password"
                value={fields.password?.value || ''}
                onChange={handleInputChange}
                onBlur={handleInputBlur}
                disabled={shouldDisable}
                className={getInputClasses('password')}
                placeholder="Tu contraseña"
              />
            </AccessibleFormField>

            {/* Additional Options */}
            <div className="flex items-center justify-between">
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

            {/* Form Status */}
            <ScreenReaderOnly>
              <div aria-live="polite" aria-atomic="true">
                {isLoading && 'Iniciando sesión...'}
                {!isFormValid && 'Completa todos los campos requeridos'}
                {isFormValid && !isLoading && 'Formulario válido, listo para enviar'}
              </div>
            </ScreenReaderOnly>

            {/* Submit Button */}
            <div>
              <LoadingButton
                type="submit"
                loading={isSubmitting}
                disabled={shouldDisable || !isFormValid}
                className="w-full flex justify-center py-2 px-4 border border-transparent 
                  rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 
                  hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 
                  focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed 
                  transition-colors duration-200"
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
          <nav className="mt-6 text-xs text-center text-gray-500 dark:text-gray-400">
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
    </div>
  );
};

export default {
  AccessibleRegisterForm,
  AccessibleLoginForm
};