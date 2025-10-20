/**
 * RegisterForm Component for IdeaFly Authentication System.
 * 
 * A comprehensive user registration form with validation, accessibility features,
 * and error handling for the US1 user story implementation.
 */

'use client';

import React, { useState, useCallback, useEffect, useRef } from 'react';
import { RegisterRequest, AuthStatus } from '../../types/auth';

// ============================================================================
// TYPES AND INTERFACES
// ============================================================================

/**
 * Form validation errors structure
 */
interface FormErrors {
  name?: string;
  email?: string;
  password?: string;
  confirmPassword?: string;
  general?: string;
}

/**
 * Form field validation state
 */
interface FormTouched {
  name: boolean;
  email: boolean;
  password: boolean;
  confirmPassword: boolean;
}

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
// VALIDATION UTILITIES
// ============================================================================

/**
 * Validate user name
 */
const validateName = (name: string): string | undefined => {
  if (!name.trim()) {
    return 'El nombre es requerido';
  }
  if (name.trim().length < 2) {
    return 'El nombre debe tener al menos 2 caracteres';
  }
  if (name.trim().length > 100) {
    return 'El nombre no puede tener más de 100 caracteres';
  }
  return undefined;
};

/**
 * Validate email address
 */
const validateEmail = (email: string): string | undefined => {
  if (!email.trim()) {
    return 'El email es requerido';
  }
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email.trim())) {
    return 'Por favor ingresa un email válido';
  }
  
  return undefined;
};

/**
 * Validate password strength
 */
const validatePassword = (password: string): string | undefined => {
  if (!password) {
    return 'La contraseña es requerida';
  }
  if (password.length < 8) {
    return 'La contraseña debe tener al menos 8 caracteres';
  }
  if (!/(?=.*[a-z])/.test(password)) {
    return 'La contraseña debe contener al menos una letra minúscula';
  }
  if (!/(?=.*[A-Z])/.test(password)) {
    return 'La contraseña debe contener al menos una letra mayúscula';
  }
  if (!/(?=.*\d)/.test(password)) {
    return 'La contraseña debe contener al menos un número';
  }
  return undefined;
};

/**
 * Validate password confirmation
 */
const validateConfirmPassword = (password: string, confirmPassword: string): string | undefined => {
  if (!confirmPassword) {
    return 'Por favor confirma tu contraseña';
  }
  if (password !== confirmPassword) {
    return 'Las contraseñas no coinciden';
  }
  return undefined;
};

// ============================================================================
// MAIN COMPONENT
// ============================================================================

/**
 * RegisterForm Component
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
  // STATE MANAGEMENT
  // ============================================================================

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });

  const [errors, setErrors] = useState<FormErrors>({});
  const [touched, setTouched] = useState<FormTouched>({
    name: false,
    email: false,
    password: false,
    confirmPassword: false
  });

  // Refs for accessibility
  const nameInputRef = useRef<HTMLInputElement>(null);
  const errorAnnouncementRef = useRef<HTMLDivElement>(null);

  // ============================================================================
  // COMPUTED VALUES
  // ============================================================================

  const isLoading = authStatus === AuthStatus.LOADING;
  const isFormDisabled = disabled || isLoading;

  // Validate entire form
  const validateForm = useCallback(() => {
    const newErrors: FormErrors = {};

    const nameError = validateName(formData.name);
    if (nameError) newErrors.name = nameError;

    const emailError = validateEmail(formData.email);
    if (emailError) newErrors.email = emailError;

    const passwordError = validatePassword(formData.password);
    if (passwordError) newErrors.password = passwordError;

    const confirmPasswordError = validateConfirmPassword(formData.password, formData.confirmPassword);
    if (confirmPasswordError) newErrors.confirmPassword = confirmPasswordError;

    return newErrors;
  }, [formData]);

  const formErrors = validateForm();
  const hasErrors = Object.keys(formErrors).length > 0;
  const isFormValid = !hasErrors && formData.name && formData.email && formData.password && formData.confirmPassword;

  // ============================================================================
  // EVENT HANDLERS
  // ============================================================================

  const handleInputChange = useCallback((field: keyof typeof formData) => {
    return (e: React.ChangeEvent<HTMLInputElement>) => {
      const value = e.target.value;
      setFormData(prev => ({ ...prev, [field]: value }));
      
      // Clear field error when user starts typing
      if (errors[field as keyof FormErrors]) {
        setErrors(prev => ({ ...prev, [field]: undefined }));
      }
    };
  }, [errors]);

  const handleInputBlur = useCallback((field: keyof FormTouched) => {
    return () => {
      setTouched(prev => ({ ...prev, [field]: true }));
    };
  }, []);

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();

    // Mark all fields as touched
    setTouched({
      name: true,
      email: true,
      password: true,
      confirmPassword: true
    });

    // Validate form
    const validationErrors = validateForm();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      
      // Focus first error field
      const firstErrorField = Object.keys(validationErrors)[0];
      if (firstErrorField === 'name' && nameInputRef.current) {
        nameInputRef.current.focus();
      }
      return;
    }

    // Clear errors and submit
    setErrors({});
    
    try {
      await onSubmit({
        name: formData.name.trim(),
        email: formData.email.trim().toLowerCase(),
        password: formData.password
      });
    } catch (err) {
      // Error handling is managed by parent component
      console.error('Registration submission error:', err);
    }
  }, [formData, validateForm, onSubmit]);

  // ============================================================================
  // EFFECTS
  // ============================================================================

  // Focus name input on mount
  useEffect(() => {
    if (nameInputRef.current) {
      nameInputRef.current.focus();
    }
  }, []);

  // Announce errors to screen readers
  useEffect(() => {
    if (error && errorAnnouncementRef.current) {
      errorAnnouncementRef.current.textContent = error;
    }
  }, [error]);

  // ============================================================================
  // RENDER HELPERS
  // ============================================================================

  const renderFieldError = (field: keyof FormErrors) => {
    const fieldError = (touched[field as keyof FormTouched] && formErrors[field]) || errors[field];
    
    if (!fieldError) return null;

    return (
      <p 
        className="mt-1 text-sm text-red-600"
        role="alert"
        aria-live="polite"
      >
        {fieldError}
      </p>
    );
  };

  const getFieldClassName = (field: keyof FormErrors) => {
    const baseClasses = "block w-full px-3 py-2 border rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition-colors duration-200";
    const hasFieldError = (touched[field as keyof FormTouched] && formErrors[field]) || errors[field];
    
    if (hasFieldError) {
      return `${baseClasses} border-red-300 text-red-900 placeholder-red-300 focus:ring-red-500 focus:border-red-500`;
    }
    
    return `${baseClasses} border-gray-300 text-gray-900`;
  };

  // ============================================================================
  // RENDER
  // ============================================================================

  return (
    <div className={`w-full max-w-md mx-auto ${className}`}>
      {/* Screen reader announcements */}
      <div 
        ref={errorAnnouncementRef}
        className="sr-only" 
        aria-live="assertive" 
        aria-atomic="true"
      />

      {/* Form header */}
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Crear cuenta
        </h2>
        <p className="text-sm text-gray-600">
          Únete a IdeaFly y comienza a desarrollar tus ideas
        </p>
      </div>

      {/* Error message */}
      {error && (
        <div 
          className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md"
          role="alert"
          aria-live="polite"
        >
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Registration form */}
      <form onSubmit={handleSubmit} noValidate className="space-y-4">
        {/* Name field */}
        <div>
          <label 
            htmlFor="register-name" 
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Nombre completo
          </label>
          <input
            ref={nameInputRef}
            id="register-name"
            name="name"
            type="text"
            autoComplete="name"
            required
            disabled={isFormDisabled}
            value={formData.name}
            onChange={handleInputChange('name')}
            onBlur={handleInputBlur('name')}
            className={getFieldClassName('name')}
            placeholder="Ingresa tu nombre completo"
            aria-describedby={formErrors.name ? "name-error" : undefined}
            aria-invalid={!!formErrors.name}
          />
          {renderFieldError('name')}
        </div>

        {/* Email field */}
        <div>
          <label 
            htmlFor="register-email" 
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Email
          </label>
          <input
            id="register-email"
            name="email"
            type="email"
            autoComplete="email"
            required
            disabled={isFormDisabled}
            value={formData.email}
            onChange={handleInputChange('email')}
            onBlur={handleInputBlur('email')}
            className={getFieldClassName('email')}
            placeholder="tu@ejemplo.com"
            aria-describedby={formErrors.email ? "email-error" : undefined}
            aria-invalid={!!formErrors.email}
          />
          {renderFieldError('email')}
        </div>

        {/* Password field */}
        <div>
          <label 
            htmlFor="register-password" 
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Contraseña
          </label>
          <input
            id="register-password"
            name="password"
            type="password"
            autoComplete="new-password"
            required
            disabled={isFormDisabled}
            value={formData.password}
            onChange={handleInputChange('password')}
            onBlur={handleInputBlur('password')}
            className={getFieldClassName('password')}
            placeholder="Mínimo 8 caracteres"
            aria-describedby={formErrors.password ? "password-error" : "password-help"}
            aria-invalid={!!formErrors.password}
          />
          {renderFieldError('password')}
          {!formErrors.password && (
            <p id="password-help" className="mt-1 text-xs text-gray-500">
              Debe contener al menos 8 caracteres con mayúsculas, minúsculas y números
            </p>
          )}
        </div>

        {/* Confirm password field */}
        <div>
          <label 
            htmlFor="register-confirm-password" 
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Confirmar contraseña
          </label>
          <input
            id="register-confirm-password"
            name="confirmPassword"
            type="password"
            autoComplete="new-password"
            required
            disabled={isFormDisabled}
            value={formData.confirmPassword}
            onChange={handleInputChange('confirmPassword')}
            onBlur={handleInputBlur('confirmPassword')}
            className={getFieldClassName('confirmPassword')}
            placeholder="Repite tu contraseña"
            aria-describedby={formErrors.confirmPassword ? "confirm-password-error" : undefined}
            aria-invalid={!!formErrors.confirmPassword}
          />
          {renderFieldError('confirmPassword')}
        </div>

        {/* Submit button */}
        <button
          type="submit"
          disabled={isFormDisabled || !isFormValid}
          className={`
            w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white
            transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
            ${isFormDisabled || !isFormValid
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700 active:bg-blue-800'
            }
          `}
          aria-describedby="submit-button-help"
        >
          {isLoading ? (
            <div className="flex items-center">
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Creando cuenta...
            </div>
          ) : (
            'Crear cuenta'
          )}
        </button>

        {/* Login link */}
        {onSwitchToLogin && (
          <div className="text-center mt-4">
            <p className="text-sm text-gray-600">
              ¿Ya tienes cuenta?{' '}
              <button
                type="button"
                onClick={onSwitchToLogin}
                disabled={isFormDisabled}
                className="font-medium text-blue-600 hover:text-blue-500 focus:outline-none focus:underline transition-colors duration-200 disabled:text-gray-400"
              >
                Inicia sesión
              </button>
            </p>
          </div>
        )}
      </form>
    </div>
  );
};

// ============================================================================
// EXPORTS
// ============================================================================

export default RegisterForm;