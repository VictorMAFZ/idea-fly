/**
 * Custom hooks for authentication forms and UI state management.
 * 
 * Provides form-specific hooks that build upon the core AuthContext
 * to handle common authentication form patterns and state management.
 */

'use client';

import { useState, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { 
  RegisterRequest, 
  LoginRequest, 
  GoogleOAuthRequest,
  FormField,
  RegisterFormState,
  LoginFormState,
} from '../types/auth';

// ============================================================================
// FORM FIELD UTILITIES
// ============================================================================

/**
 * Create initial form field state.
 */
function createFormField<T = string>(initialValue: T): FormField<T> {
  return {
    value: initialValue,
    error: null,
    touched: false,
    validating: false,
  };
}

/**
 * Validate email format.
 */
function validateEmail(email: string): string | null {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!email) return 'Email is required';
  if (!emailRegex.test(email)) return 'Please enter a valid email address';
  return null;
}

/**
 * Validate password strength.
 */
function validatePassword(password: string): string | null {
  if (!password) return 'Password is required';
  if (password.length < 8) return 'Password must be at least 8 characters';
  if (!/(?=.*[a-z])/.test(password)) return 'Password must contain at least one lowercase letter';
  if (!/(?=.*[A-Z])/.test(password)) return 'Password must contain at least one uppercase letter';
  if (!/(?=.*\d)/.test(password)) return 'Password must contain at least one number';
  if (!/(?=.*[@$!%*?&])/.test(password)) return 'Password must contain at least one special character';
  return null;
}

/**
 * Validate name field.
 */
function validateName(name: string): string | null {
  if (!name) return 'Name is required';
  if (name.length < 2) return 'Name must be at least 2 characters';
  if (name.length > 100) return 'Name must be less than 100 characters';
  if (!/^[a-zA-Z\s'-]+$/.test(name)) return 'Name can only contain letters, spaces, hyphens, and apostrophes';
  return null;
}

// ============================================================================
// REGISTRATION FORM HOOK
// ============================================================================

/**
 * Hook for managing registration form state and submission.
 */
export function useRegisterForm() {
  const { register, loading, error, clearError } = useAuth();
  
  const [formState, setFormState] = useState<RegisterFormState>({
    name: createFormField(''),
    email: createFormField(''),
    password: createFormField(''),
    confirmPassword: createFormField(''),
    isSubmitting: false,
    submitError: null,
  });

  const updateField = useCallback(<K extends keyof Omit<RegisterFormState, 'isSubmitting' | 'submitError'>>(
    field: K,
    value: string,
    validate: boolean = false
  ) => {
    setFormState(prev => {
      const newField = {
        ...prev[field],
        value,
        touched: true,
      };

      if (validate) {
        switch (field) {
          case 'name':
            newField.error = validateName(value);
            break;
          case 'email':
            newField.error = validateEmail(value);
            break;
          case 'password':
            newField.error = validatePassword(value);
            break;
          case 'confirmPassword':
            newField.error = value !== prev.password.value ? 'Passwords do not match' : null;
            break;
        }
      }

      return {
        ...prev,
        [field]: newField,
        submitError: null, // Clear submit error when user types
      };
    });
  }, []);

  const validateForm = useCallback((): boolean => {
    const nameError = validateName(formState.name.value);
    const emailError = validateEmail(formState.email.value);
    const passwordError = validatePassword(formState.password.value);
    const confirmPasswordError = formState.password.value !== formState.confirmPassword.value 
      ? 'Passwords do not match' 
      : null;

    setFormState(prev => ({
      ...prev,
      name: { ...prev.name, error: nameError, touched: true },
      email: { ...prev.email, error: emailError, touched: true },
      password: { ...prev.password, error: passwordError, touched: true },
      confirmPassword: { ...prev.confirmPassword, error: confirmPasswordError, touched: true },
    }));

    return !nameError && !emailError && !passwordError && !confirmPasswordError;
  }, [formState.name.value, formState.email.value, formState.password.value, formState.confirmPassword.value]);

  const submitForm = useCallback(async (): Promise<boolean> => {
    clearError(); // Clear any existing auth errors
    
    if (!validateForm()) {
      return false;
    }

    setFormState(prev => ({ ...prev, isSubmitting: true, submitError: null }));

    try {
      const request: RegisterRequest = {
        name: formState.name.value.trim(),
        email: formState.email.value.trim().toLowerCase(),
        password: formState.password.value,
      };

      await register(request);
      return true;
    } catch (error: any) {
      setFormState(prev => ({
        ...prev,
        isSubmitting: false,
        submitError: error?.message || 'Registration failed. Please try again.',
      }));
      return false;
    } finally {
      setFormState(prev => ({ ...prev, isSubmitting: false }));
    }
  }, [register, clearError, validateForm, formState.name.value, formState.email.value, formState.password.value]);

  const resetForm = useCallback(() => {
    setFormState({
      name: createFormField(''),
      email: createFormField(''),
      password: createFormField(''),
      confirmPassword: createFormField(''),
      isSubmitting: false,
      submitError: null,
    });
    clearError();
  }, [clearError]);

  return {
    formState,
    updateField,
    submitForm,
    resetForm,
    isValid: !formState.name.error && !formState.email.error && !formState.password.error && !formState.confirmPassword.error,
    isSubmitting: formState.isSubmitting || loading,
    submitError: formState.submitError || error,
  };
}

// ============================================================================
// LOGIN FORM HOOK
// ============================================================================

/**
 * Hook for managing login form state and submission.
 */
export function useLoginForm() {
  const { login, loading, error, clearError } = useAuth();
  
  const [formState, setFormState] = useState<LoginFormState>({
    email: createFormField(''),
    password: createFormField(''),
    rememberMe: createFormField(false),
    isSubmitting: false,
    submitError: null,
  });

  const updateField = useCallback(<K extends keyof Omit<LoginFormState, 'isSubmitting' | 'submitError'>>(
    field: K,
    value: K extends 'rememberMe' ? boolean : string,
    validate: boolean = false
  ) => {
    setFormState(prev => {
      const newField = {
        ...prev[field],
        value,
        touched: true,
      };

      if (validate && typeof value === 'string') {
        switch (field) {
          case 'email':
            newField.error = validateEmail(value);
            break;
          case 'password':
            newField.error = !value ? 'Password is required' : null;
            break;
        }
      }

      return {
        ...prev,
        [field]: newField,
        submitError: null,
      };
    });
  }, []);

  const validateForm = useCallback((): boolean => {
    const emailError = validateEmail(formState.email.value);
    const passwordError = !formState.password.value ? 'Password is required' : null;

    setFormState(prev => ({
      ...prev,
      email: { ...prev.email, error: emailError, touched: true },
      password: { ...prev.password, error: passwordError, touched: true },
    }));

    return !emailError && !passwordError;
  }, [formState.email.value, formState.password.value]);

  const submitForm = useCallback(async (): Promise<boolean> => {
    clearError();
    
    if (!validateForm()) {
      return false;
    }

    setFormState(prev => ({ ...prev, isSubmitting: true, submitError: null }));

    try {
      const request: LoginRequest = {
        email: formState.email.value.trim().toLowerCase(),
        password: formState.password.value,
      };
      
      // Note: remember_me will be handled when session persistence is enhanced

      await login(request);
      return true;
    } catch (error: any) {
      setFormState(prev => ({
        ...prev,
        isSubmitting: false,
        submitError: error?.message || 'Login failed. Please check your credentials.',
      }));
      return false;
    } finally {
      setFormState(prev => ({ ...prev, isSubmitting: false }));
    }
  }, [login, clearError, validateForm, formState.email.value, formState.password.value, formState.rememberMe.value]);

  const resetForm = useCallback(() => {
    setFormState({
      email: createFormField(''),
      password: createFormField(''),
      rememberMe: createFormField(false),
      isSubmitting: false,
      submitError: null,
    });
    clearError();
  }, [clearError]);

  return {
    formState,
    updateField,
    submitForm,
    resetForm,
    isValid: !formState.email.error && !formState.password.error,
    isSubmitting: formState.isSubmitting || loading,
    submitError: formState.submitError || error,
  };
}

// ============================================================================
// GOOGLE AUTH HOOK
// ============================================================================

/**
 * Hook for managing Google OAuth authentication.
 */
export function useGoogleAuth() {
  const { loginWithGoogle, loading, error, clearError } = useAuth();
  const [isInitiating, setIsInitiating] = useState(false);

  const initiateGoogleAuth = useCallback(async (): Promise<boolean> => {
    clearError();
    setIsInitiating(true);

    try {
      // TODO: This will be implemented when Google OAuth is set up
      // For now, simulate the OAuth request
      const mockRequest: GoogleOAuthRequest = {
        code: `mock_google_code_${Date.now()}`,
        state: `mock_state_${Date.now()}`,
      };

      await loginWithGoogle(mockRequest);
      return true;
    } catch (error: any) {
      console.error('Google authentication failed:', error);
      return false;
    } finally {
      setIsInitiating(false);
    }
  }, [loginWithGoogle, clearError]);

  return {
    initiateGoogleAuth,
    isLoading: isInitiating || loading,
    error,
    clearError,
  };
}

// ============================================================================
// AUTH STATUS HOOK
// ============================================================================

/**
 * Hook for getting current authentication status with loading states.
 */
export function useAuthStatus() {
  const { status, loading, isAuthenticated, isTokenExpired } = useAuth();
  
  return {
    status,
    loading,
    isAuthenticated: isAuthenticated(),
    isTokenExpired: isTokenExpired(),
    isLoading: loading,
    isIdle: status === 'idle',
    isError: status === 'error',
  };
}

// ============================================================================
// EXPORTS
// ============================================================================

export {
  validateEmail,
  validatePassword,
  validateName,
  createFormField,
};