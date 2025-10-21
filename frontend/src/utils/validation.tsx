/**
 * Real-time Form Validation Utilities for IdeaFly Application.
 * 
 * Provides comprehensive validation rules, real-time feedback,
 * and enhanced user experience for form inputs.
 */

'use client';

import { useState, useCallback, useEffect } from 'react';

// ============================================================================
// TYPES AND INTERFACES
// ============================================================================

export interface ValidationRule {
  /** Validation function */
  validator: (value: string) => boolean;
  /** Error message when validation fails */
  message: string;
  /** Whether this rule should be checked on blur only */
  onBlurOnly?: boolean;
}

export interface FieldValidation {
  /** Field value */
  value: string;
  /** Whether field has been touched */
  touched: boolean;
  /** Whether field is currently being validated */
  validating: boolean;
  /** Validation error message */
  error: string | null;
  /** Whether field is valid */
  isValid: boolean;
  /** Validation warnings (non-blocking) */
  warnings: string[];
}

export interface FormValidationState {
  [fieldName: string]: FieldValidation;
}

// ============================================================================
// VALIDATION RULES
// ============================================================================

/**
 * Common validation rules for different field types.
 */
export const ValidationRules = {
  // Required field
  required: (message = 'Este campo es obligatorio'): ValidationRule => ({
    validator: (value: string) => value.trim().length > 0,
    message
  }),

  // Email validation
  email: (message = 'Ingresa una dirección de email válida'): ValidationRule => ({
    validator: (value: string) => {
      const emailRegex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;
      return emailRegex.test(value.trim().toLowerCase());
    },
    message
  }),

  // Minimum length
  minLength: (min: number, message?: string): ValidationRule => ({
    validator: (value: string) => value.length >= min,
    message: message || `Debe tener al menos ${min} caracteres`
  }),

  // Maximum length
  maxLength: (max: number, message?: string): ValidationRule => ({
    validator: (value: string) => value.length <= max,
    message: message || `No debe exceder ${max} caracteres`
  }),

  // Password strength
  strongPassword: (message = 'La contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula y un número'): ValidationRule => ({
    validator: (value: string) => {
      const hasMinLength = value.length >= 8;
      const hasUpperCase = /[A-Z]/.test(value);
      const hasLowerCase = /[a-z]/.test(value);
      const hasNumbers = /\d/.test(value);
      return hasMinLength && hasUpperCase && hasLowerCase && hasNumbers;
    },
    message,
    onBlurOnly: true
  }),

  // Name validation
  name: (message = 'El nombre debe tener entre 2 y 50 caracteres'): ValidationRule => ({
    validator: (value: string) => {
      const trimmed = value.trim();
      return trimmed.length >= 2 && trimmed.length <= 50 && /^[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ\s]+$/.test(trimmed);
    },
    message
  }),

  // Confirm password
  confirmPassword: (password: string, message = 'Las contraseñas no coinciden'): ValidationRule => ({
    validator: (value: string) => value === password,
    message
  }),

  // Custom pattern
  pattern: (regex: RegExp, message: string): ValidationRule => ({
    validator: (value: string) => regex.test(value),
    message
  }),

  // No whitespace
  noWhitespace: (message = 'No puede contener espacios'): ValidationRule => ({
    validator: (value: string) => !/\s/.test(value),
    message
  })
};

/**
 * Password strength levels and scoring.
 */
export const getPasswordStrength = (password: string) => {
  if (!password) return { level: 0, label: '', color: 'gray' };

  let score = 0;
  let feedback: string[] = [];

  // Length check
  if (password.length >= 8) score += 25;
  else feedback.push('Al menos 8 caracteres');

  // Character variety
  if (/[a-z]/.test(password)) score += 25;
  else feedback.push('Una letra minúscula');

  if (/[A-Z]/.test(password)) score += 25;
  else feedback.push('Una letra mayúscula');

  if (/\d/.test(password)) score += 25;
  else feedback.push('Un número');

  // Bonus points
  if (/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\?]/.test(password)) score += 10;
  if (password.length >= 12) score += 10;

  const levels = [
    { min: 0, max: 25, label: 'Muy débil', color: 'red' },
    { min: 26, max: 50, label: 'Débil', color: 'orange' },
    { min: 51, max: 75, label: 'Buena', color: 'yellow' },
    { min: 76, max: 90, label: 'Fuerte', color: 'green' },
    { min: 91, max: 100, label: 'Muy fuerte', color: 'green' }
  ];

  const level = levels.find(l => score >= l.min && score <= l.max) || levels[0];

  return {
    score,
    level: level.label,
    color: level.color,
    feedback: feedback.length > 0 ? `Necesita: ${feedback.join(', ')}` : 'Excelente contraseña'
  };
};

// ============================================================================
// VALIDATION HOOK
// ============================================================================

/**
 * Hook for managing real-time form validation.
 */
export function useFormValidation(
  initialValues: Record<string, string> = {},
  validationRules: Record<string, ValidationRule[]> = {}
) {
  const [fields, setFields] = useState<FormValidationState>(() => {
    const initial: FormValidationState = {};
    Object.keys(initialValues).forEach(fieldName => {
      initial[fieldName] = {
        value: initialValues[fieldName] || '',
        touched: false,
        validating: false,
        error: null,
        isValid: true,
        warnings: []
      };
    });
    return initial;
  });

  const [isFormValid, setIsFormValid] = useState(false);
  const [submitAttempted, setSubmitAttempted] = useState(false);

  // Validate a single field
  const validateField = useCallback((fieldName: string, value: string, onBlurValidation = false) => {
    const rules = validationRules[fieldName] || [];
    let error: string | null = null;
    const warnings: string[] = [];

    for (const rule of rules) {
      // Skip blur-only rules during real-time validation
      if (!onBlurValidation && rule.onBlurOnly) continue;

      if (!rule.validator(value)) {
        error = rule.message;
        break;
      }
    }

    // Check for warnings (like password strength)
    if (fieldName === 'password' && value) {
      const strength = getPasswordStrength(value);
      if (strength.score && strength.score < 51 && strength.feedback) {
        warnings.push(strength.feedback);
      }
    }

    return { error, warnings, isValid: error === null };
  }, [validationRules]);

  // Update field value and validate
  const updateField = useCallback((fieldName: string, value: string, touched = false) => {
    setFields(prev => {
      const validation = validateField(fieldName, value, false);
      
      const newField = {
        ...prev[fieldName],
        value,
        touched: touched || prev[fieldName]?.touched || false,
        ...validation
      };

      return {
        ...prev,
        [fieldName]: newField
      };
    });
  }, [validateField]);

  // Handle field blur (more thorough validation)
  const handleFieldBlur = useCallback((fieldName: string) => {
    setFields(prev => {
      const currentField = prev[fieldName];
      if (!currentField) return prev;

      const validation = validateField(fieldName, currentField.value, true);
      
      return {
        ...prev,
        [fieldName]: {
          ...currentField,
          touched: true,
          ...validation
        }
      };
    });
  }, [validateField]);

  // Get field error message (only show if touched or submit attempted)
  const getFieldError = useCallback((fieldName: string): string | null => {
    const field = fields[fieldName];
    if (!field) return null;
    
    return (field.touched || submitAttempted) ? field.error : null;
  }, [fields, submitAttempted]);

  // Get field warnings
  const getFieldWarnings = useCallback((fieldName: string): string[] => {
    const field = fields[fieldName];
    return field?.warnings || [];
  }, [fields]);

  // Check if field is valid (considering touched state)
  const isFieldValid = useCallback((fieldName: string): boolean => {
    const field = fields[fieldName];
    if (!field) return false;
    
    return field.isValid || (!field.touched && !submitAttempted);
  }, [fields, submitAttempted]);

  // Get field CSS classes for styling
  const getFieldClassName = useCallback((fieldName: string, baseClasses = ''): string => {
    const field = fields[fieldName];
    if (!field) return baseClasses;

    const isValid = isFieldValid(fieldName);
    const hasError = getFieldError(fieldName) !== null;
    const hasWarnings = getFieldWarnings(fieldName).length > 0;

    let classes = baseClasses;
    
    if (field.touched || submitAttempted) {
      if (hasError) {
        classes += ' border-red-300 focus:border-red-500 focus:ring-red-500';
      } else if (hasWarnings) {
        classes += ' border-yellow-300 focus:border-yellow-500 focus:ring-yellow-500';
      } else if (field.value && isValid) {
        classes += ' border-green-300 focus:border-green-500 focus:ring-green-500';
      }
    }

    return classes;
  }, [fields, isFieldValid, getFieldError, getFieldWarnings, submitAttempted]);

  // Reset form
  const resetForm = useCallback(() => {
    setFields(prev => {
      const reset: FormValidationState = {};
      Object.keys(prev).forEach(fieldName => {
        reset[fieldName] = {
          value: initialValues[fieldName] || '',
          touched: false,
          validating: false,
          error: null,
          isValid: true,
          warnings: []
        };
      });
      return reset;
    });
    setSubmitAttempted(false);
  }, [initialValues]);

  // Handle form submission
  const handleSubmit = useCallback((onSubmit: (values: Record<string, string>) => void | Promise<void>) => {
    return async (e: React.FormEvent) => {
      e.preventDefault();
      setSubmitAttempted(true);

      // Validate all fields with blur-level validation
      const updatedFields: FormValidationState = {};
      let hasErrors = false;

      Object.keys(fields).forEach(fieldName => {
        const field = fields[fieldName];
        const validation = validateField(fieldName, field.value, true);
        
        updatedFields[fieldName] = {
          ...field,
          touched: true,
          ...validation
        };

        if (!validation.isValid) {
          hasErrors = true;
        }
      });

      setFields(updatedFields);

      if (!hasErrors) {
        const values: Record<string, string> = {};
        Object.keys(updatedFields).forEach(fieldName => {
          values[fieldName] = updatedFields[fieldName].value;
        });

        await onSubmit(values);
      }
    };
  }, [fields, validateField]);

  // Update form validity when fields change
  useEffect(() => {
    const allValid = Object.values(fields).every(field => field.isValid && field.value.trim() !== '');
    setIsFormValid(allValid);
  }, [fields]);

  return {
    fields,
    isFormValid,
    submitAttempted,
    updateField,
    handleFieldBlur,
    getFieldError,
    getFieldWarnings,
    isFieldValid,
    getFieldClassName,
    resetForm,
    handleSubmit,
    validateField
  };
}

// ============================================================================
// VALIDATION COMPONENTS
// ============================================================================

/**
 * Field error display component.
 */
export function FieldError({ error, className = '' }: { error: string | null; className?: string }) {
  if (!error) return null;

  return (
    <p className={`text-sm text-red-600 dark:text-red-400 mt-1 ${className}`} role="alert">
      {error}
    </p>
  );
}

/**
 * Field warning display component.
 */
export function FieldWarning({ warning, className = '' }: { warning: string; className?: string }) {
  return (
    <p className={`text-sm text-yellow-600 dark:text-yellow-400 mt-1 ${className}`}>
      ⚠️ {warning}
    </p>
  );
}

/**
 * Password strength indicator component.
 */
export function PasswordStrengthIndicator({ password, className = '' }: { password: string; className?: string }) {
  const strength = getPasswordStrength(password);
  
  if (!password) return null;

  const colorClasses = {
    red: 'bg-red-500',
    orange: 'bg-orange-500',
    yellow: 'bg-yellow-500',
    green: 'bg-green-500',
    gray: 'bg-gray-300'
  };

  return (
    <div className={`mt-2 ${className}`}>
      <div className="flex justify-between text-sm">
        <span className="text-gray-600 dark:text-gray-400">Fortaleza:</span>
        <span className={`font-medium ${strength.color === 'green' ? 'text-green-600' : strength.color === 'red' ? 'text-red-600' : 'text-yellow-600'}`}>
          {strength.level}
        </span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
        <div 
          className={`h-2 rounded-full transition-all duration-300 ${colorClasses[strength.color as keyof typeof colorClasses]}`}
          style={{ width: `${strength.score}%` }}
        />
      </div>
      {strength.feedback && (
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
          {strength.feedback}
        </p>
      )}
    </div>
  );
}

export default {
  ValidationRules,
  useFormValidation,
  getPasswordStrength,
  FieldError,
  FieldWarning,
  PasswordStrengthIndicator
};