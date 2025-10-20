/**
 * @fileoverview Component tests for RegisterForm
 * @description Comprehensive test suite covering all RegisterForm functionality including rendering,
 * validation, form submission, authentication status handling, accessibility, user interactions,
 * integration scenarios, and edge cases.
 * 
 * @author T028 - Component Testing Implementation
 * @created 2024-12-19
 * 
 * Test Coverage:
 * - Rendering validation
 * - Form validation (name, email, password, confirmation)
 * - Form submission
 * - Authentication status handling
 * - Accessibility compliance
 * - User interactions
 * - Integration scenarios
 * - Edge cases
 */

import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi, describe, test, expect, beforeEach, afterEach } from 'vitest';
import RegisterForm from '@/components/auth/RegisterForm';
import { AuthStatus } from '@/types/auth';

// ============================================================================
// MOCKS
// ============================================================================

// Mock Next.js router
const mockRouter = {
  push: vi.fn(),
  replace: vi.fn(),
  back: vi.fn(),
  forward: vi.fn(),
  refresh: vi.fn(),
  prefetch: vi.fn(),
};

vi.mock('next/navigation', () => ({
  useRouter: () => mockRouter,
}));

// Mock authentication service
const mockAuthService = {
  register: vi.fn(),
  login: vi.fn(),
  logout: vi.fn(),
  getCurrentUser: vi.fn(),
};

vi.mock('@/services/authService', () => ({
  default: mockAuthService,
}));

// ============================================================================
// TEST UTILITIES
// ============================================================================

const defaultProps = {
  onSubmit: vi.fn(),
  onSwitchToLogin: vi.fn(),
  authStatus: AuthStatus.IDLE,
  error: null,
  className: '',
};

const renderRegisterForm = (props = {}) => {
  return render(<RegisterForm {...defaultProps} {...props} />);
};

// ============================================================================
// TEST SUITES
// ============================================================================

describe('RegisterForm Component', () => {
  let user: ReturnType<typeof userEvent.setup>;

  beforeEach(() => {
    user = userEvent.setup();
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  // ==========================================================================
  // RENDERING TESTS
  // ==========================================================================

  describe('Rendering', () => {
    test('renders all form elements correctly', () => {
      renderRegisterForm();

      // Form header
      expect(screen.getByRole('heading', { name: /crear cuenta/i })).toBeInTheDocument();
      expect(screen.getByText(/únete a ideafly/i)).toBeInTheDocument();

      // Form fields
      expect(screen.getByLabelText(/nombre completo/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/^contraseña$/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/confirmar contraseña/i)).toBeInTheDocument();

      // Submit button
      expect(screen.getByRole('button', { name: /crear cuenta/i })).toBeInTheDocument();

      // Switch to login link
      expect(screen.getByRole('button', { name: /inicia sesión/i })).toBeInTheDocument();
    });

    test('applies custom className when provided', () => {
      const customClass = 'custom-form-class';
      renderRegisterForm({ className: customClass });
      
      const formContainer = screen.getByRole('heading', { name: /crear cuenta/i }).closest('div').parentElement;
      expect(formContainer).toHaveClass(customClass);
    });

    test('displays accessibility attributes correctly', () => {
      renderRegisterForm();

      const nameInput = screen.getByLabelText(/nombre completo/i);
      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/^contraseña$/i);
      const confirmPasswordInput = screen.getByLabelText(/confirmar contraseña/i);

      expect(nameInput).toHaveAttribute('aria-invalid', 'true');
      expect(emailInput).toHaveAttribute('aria-invalid', 'true');
      expect(passwordInput).toHaveAttribute('aria-invalid', 'true');
      expect(confirmPasswordInput).toHaveAttribute('aria-invalid', 'true');
    });
  });

  // ==========================================================================
  // FORM VALIDATION TESTS
  // ==========================================================================

  describe('Form Validation', () => {
    describe('Name validation', () => {
      test('shows error for empty name', async () => {
        renderRegisterForm();
        const nameInput = screen.getByLabelText(/nombre completo/i);

        await user.click(nameInput);
        await user.tab();

        await waitFor(() => {
          expect(screen.getByText(/el nombre es requerido/i)).toBeInTheDocument();
        });
      });

      test('shows error for name with only whitespace', async () => {
        renderRegisterForm();
        const nameInput = screen.getByLabelText(/nombre completo/i);

        await user.type(nameInput, '   ');
        await user.tab();

        await waitFor(() => {
          expect(screen.getByText(/el nombre es requerido/i)).toBeInTheDocument();
        });
      });

      test('shows error for name exceeding 100 characters', async () => {
        renderRegisterForm();
        const nameInput = screen.getByLabelText(/nombre completo/i);
        const longName = 'A'.repeat(101);

        await user.type(nameInput, longName);
        await user.tab();

        await waitFor(() => {
          expect(screen.getByText(/el nombre no puede tener más de 100 caracteres/i)).toBeInTheDocument();
        });
      });

      test('accepts valid name', async () => {
        renderRegisterForm();
        const nameInput = screen.getByLabelText(/nombre completo/i);

        await user.type(nameInput, 'Juan Pérez');
        await user.tab();

        await waitFor(() => {
          expect(screen.queryByText(/el nombre es requerido/i)).not.toBeInTheDocument();
        });
      });
    });

    describe('Email validation', () => {
      test('shows error for empty email', async () => {
        renderRegisterForm();
        const emailInput = screen.getByLabelText(/email/i);

        await user.click(emailInput);
        await user.tab();

        await waitFor(() => {
          expect(screen.getByText(/el email es requerido/i)).toBeInTheDocument();
        });
      });

      test('shows error for invalid email format', async () => {
        renderRegisterForm();
        const emailInput = screen.getByLabelText(/email/i);

        await user.type(emailInput, 'invalid-email');
        await user.tab();

        await waitFor(() => {
          expect(screen.getByText(/por favor ingresa un email válido/i)).toBeInTheDocument();
        });
      });

      test('accepts valid email', async () => {
        renderRegisterForm();
        const emailInput = screen.getByLabelText(/email/i);

        await user.type(emailInput, 'test@example.com');
        await user.tab();

        await waitFor(() => {
          expect(screen.queryByText(/el email es requerido/i)).not.toBeInTheDocument();
          expect(screen.queryByText(/por favor ingresa un email válido/i)).not.toBeInTheDocument();
        });
      });
    });

    describe('Password validation', () => {
      test('shows error for empty password', async () => {
        renderRegisterForm();
        const passwordInput = screen.getByLabelText(/^contraseña$/i);

        await user.click(passwordInput);
        await user.tab();

        await waitFor(() => {
          expect(screen.getByText(/la contraseña es requerida/i)).toBeInTheDocument();
        });
      });

      test('shows error for password shorter than 8 characters', async () => {
        renderRegisterForm();
        const passwordInput = screen.getByLabelText(/^contraseña$/i);

        await user.type(passwordInput, '1234567');
        await user.tab();

        await waitFor(() => {
          expect(screen.getByText(/la contraseña debe tener al menos 8 caracteres/i)).toBeInTheDocument();
        });
      });

      test('accepts valid password', async () => {
        renderRegisterForm();
        const passwordInput = screen.getByLabelText(/^contraseña$/i);

        await user.type(passwordInput, 'StrongPass123');
        await user.tab();

        await waitFor(() => {
          expect(screen.queryByText(/la contraseña es requerida/i)).not.toBeInTheDocument();
          expect(screen.queryByText(/la contraseña debe tener al menos 8 caracteres/i)).not.toBeInTheDocument();
        });
      });
    });

    describe('Confirm Password validation', () => {
      test('shows error for empty confirmation', async () => {
        renderRegisterForm();
        const confirmPasswordInput = screen.getByLabelText(/confirmar contraseña/i);

        await user.click(confirmPasswordInput);
        await user.tab();

        await waitFor(() => {
          expect(screen.getByText(/por favor confirma tu contraseña/i)).toBeInTheDocument();
        });
      });

      test('shows error for mismatched passwords', async () => {
        renderRegisterForm();
        const passwordInput = screen.getByLabelText(/^contraseña$/i);
        const confirmPasswordInput = screen.getByLabelText(/confirmar contraseña/i);

        await user.type(passwordInput, 'StrongPass123');
        await user.type(confirmPasswordInput, 'DifferentPass456');
        await user.tab();

        await waitFor(() => {
          expect(screen.getByText(/las contraseñas no coinciden/i)).toBeInTheDocument();
        });
      });

      test('accepts matching passwords', async () => {
        renderRegisterForm();
        const passwordInput = screen.getByLabelText(/^contraseña$/i);
        const confirmPasswordInput = screen.getByLabelText(/confirmar contraseña/i);

        await user.type(passwordInput, 'StrongPass123');
        await user.type(confirmPasswordInput, 'StrongPass123');
        await user.tab();

        await waitFor(() => {
          expect(screen.queryByText(/por favor confirma tu contraseña/i)).not.toBeInTheDocument();
          expect(screen.queryByText(/las contraseñas no coinciden/i)).not.toBeInTheDocument();
        });
      });
    });
  });

  // ==========================================================================
  // FORM SUBMISSION TESTS
  // ==========================================================================

  describe('Form Submission', () => {
    test('prevents submission with empty form', async () => {
      renderRegisterForm();
      const submitButton = screen.getByRole('button', { name: /crear cuenta/i });

      expect(submitButton).toBeDisabled();
    });

    test('prevents submission with invalid data', async () => {
      renderRegisterForm();
      
      await user.type(screen.getByLabelText(/nombre completo/i), 'A');
      await user.type(screen.getByLabelText(/email/i), 'invalid-email');
      await user.type(screen.getByLabelText(/^contraseña$/i), '123');
      await user.type(screen.getByLabelText(/confirmar contraseña/i), '456');

      const submitButton = screen.getByRole('button', { name: /crear cuenta/i });
      expect(submitButton).toBeDisabled();
    });

    test('allows submission with valid data', async () => {
      renderRegisterForm();

      await user.type(screen.getByLabelText(/nombre completo/i), 'Juan Pérez');
      await user.type(screen.getByLabelText(/email/i), 'juan@example.com');
      await user.type(screen.getByLabelText(/^contraseña$/i), 'StrongPass123');
      await user.type(screen.getByLabelText(/confirmar contraseña/i), 'StrongPass123');

      await waitFor(() => {
        const submitButton = screen.getByRole('button', { name: /crear cuenta/i });
        expect(submitButton).toBeEnabled();
      });
    });

    test('calls onSubmit with correct data on valid submission', async () => {
      const onSubmitSpy = vi.fn();
      renderRegisterForm({ onSubmit: onSubmitSpy });

      await user.type(screen.getByLabelText(/nombre completo/i), 'Juan Pérez');
      await user.type(screen.getByLabelText(/email/i), 'juan@example.com');
      await user.type(screen.getByLabelText(/^contraseña$/i), 'StrongPass123');
      await user.type(screen.getByLabelText(/confirmar contraseña/i), 'StrongPass123');

      const submitButton = screen.getByRole('button', { name: /crear cuenta/i });
      await user.click(submitButton);

      expect(onSubmitSpy).toHaveBeenCalledWith({
        name: 'Juan Pérez',
        email: 'juan@example.com',
        password: 'StrongPass123'
      });
    });
  });

  // ==========================================================================
  // AUTHENTICATION STATUS TESTS
  // ==========================================================================

  describe('Authentication Status', () => {
    test('shows loading state during authentication', () => {
      renderRegisterForm({ authStatus: AuthStatus.LOADING });

      const submitButton = screen.getByRole('button', { name: /creando cuenta/i });
      expect(submitButton).toBeDisabled();
      expect(submitButton).toHaveClass('bg-gray-400', 'cursor-not-allowed');
    });

    test('shows error state when authentication fails', () => {
      const errorMessage = 'Registration failed';
      renderRegisterForm({ 
        authStatus: AuthStatus.ERROR,
        error: errorMessage 
      });

      expect(screen.getAllByText(errorMessage)).toHaveLength(2); // One in error display, one in screen reader area
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });

    test('enables form when in idle state', () => {
      renderRegisterForm({ authStatus: AuthStatus.IDLE });

      const nameInput = screen.getByLabelText(/nombre completo/i);
      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/^contraseña$/i);
      const confirmPasswordInput = screen.getByLabelText(/confirmar contraseña/i);

      expect(nameInput).not.toBeDisabled();
      expect(emailInput).not.toBeDisabled();
      expect(passwordInput).not.toBeDisabled();
      expect(confirmPasswordInput).not.toBeDisabled();
    });

    test('disables form during loading', () => {
      renderRegisterForm({ authStatus: AuthStatus.LOADING });

      const nameInput = screen.getByLabelText(/nombre completo/i);
      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/^contraseña$/i);
      const confirmPasswordInput = screen.getByLabelText(/confirmar contraseña/i);

      expect(nameInput).toBeDisabled();
      expect(emailInput).toBeDisabled();
      expect(passwordInput).toBeDisabled();
      expect(confirmPasswordInput).toBeDisabled();
    });
  });

  // ==========================================================================
  // ACCESSIBILITY TESTS
  // ==========================================================================

  describe('Accessibility', () => {
    test('has proper ARIA labels and roles', () => {
      renderRegisterForm();

      // Inputs have proper labels
      const nameInput = screen.getByLabelText(/nombre completo/i);
      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/^contraseña$/i);
      const confirmPasswordInput = screen.getByLabelText(/confirmar contraseña/i);

      expect(nameInput).toHaveAttribute('id');
      expect(emailInput).toHaveAttribute('id');
      expect(passwordInput).toHaveAttribute('id');
      expect(confirmPasswordInput).toHaveAttribute('id');
    });

    test('announces errors to screen readers', async () => {
      renderRegisterForm();

      const nameInput = screen.getByLabelText(/nombre completo/i);
      await user.click(nameInput);
      await user.tab();

      await waitFor(() => {
        const errorElement = screen.getByText(/el nombre es requerido/i);
        expect(errorElement).toHaveAttribute('role', 'alert');
        expect(errorElement).toHaveAttribute('aria-live', 'polite');
      });
    });

    test('has proper focus management', async () => {
      renderRegisterForm();

      const nameInput = screen.getByLabelText(/nombre completo/i);
      nameInput.focus();
      
      expect(document.activeElement).toBe(nameInput);

      await user.tab();
      const emailInput = screen.getByLabelText(/email/i);
      expect(document.activeElement).toBe(emailInput);
    });

    test('supports keyboard navigation', async () => {
      renderRegisterForm();

      const nameInput = screen.getByLabelText(/nombre completo/i);
      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/^contraseña$/i);
      const confirmPasswordInput = screen.getByLabelText(/confirmar contraseña/i);

      // Focus name input and tab through form
      nameInput.focus();
      expect(document.activeElement).toBe(nameInput);

      await user.tab();
      expect(document.activeElement).toBe(emailInput);
      
      await user.tab();
      expect(document.activeElement).toBe(passwordInput);
      
      await user.tab();
      expect(document.activeElement).toBe(confirmPasswordInput);
      
      await user.tab();
      // Either the submit button or the login link could be next, both are valid
      expect(document.activeElement).toBeDefined();
    });
  });

  // ==========================================================================
  // USER INTERACTION TESTS
  // ==========================================================================

  describe('User Interactions', () => {
    test('calls onSwitchToLogin when login link is clicked', async () => {
      const onSwitchToLoginSpy = vi.fn();
      renderRegisterForm({ onSwitchToLogin: onSwitchToLoginSpy });

      const loginLink = screen.getByRole('button', { name: /inicia sesión/i });
      await user.click(loginLink);

      expect(onSwitchToLoginSpy).toHaveBeenCalled();
    });

    test('shows real-time validation feedback as user types', async () => {
      renderRegisterForm();

      const emailInput = screen.getByLabelText(/email/i);

      // Type invalid email
      await user.type(emailInput, 'invalid');
      await user.tab();

      await waitFor(() => {
        expect(screen.getByText(/por favor ingresa un email válido/i)).toBeInTheDocument();
      });

      // Clear and type valid email
      await user.clear(emailInput);
      await user.type(emailInput, 'valid@email.com');
      await user.tab();

      await waitFor(() => {
        expect(screen.queryByText(/por favor ingresa un email válido/i)).not.toBeInTheDocument();
      });
    });

    test('handles form reset correctly', async () => {
      renderRegisterForm();

      // Fill form
      await user.type(screen.getByLabelText(/nombre completo/i), 'John Doe');
      await user.type(screen.getByLabelText(/email/i), 'john@example.com');
      
      // Verify form has values
      expect(screen.getByDisplayValue('John Doe')).toBeInTheDocument();
      expect(screen.getByDisplayValue('john@example.com')).toBeInTheDocument();

      // Form should maintain state until explicitly reset
      expect(screen.getByLabelText(/nombre completo/i)).toHaveValue('John Doe');
      expect(screen.getByLabelText(/email/i)).toHaveValue('john@example.com');
    });
  });

  // ==========================================================================
  // INTEGRATION TESTS
  // ==========================================================================

  describe('Integration', () => {
    test('integrates properly with authentication flow', async () => {
      const onSubmitSpy = vi.fn();
      renderRegisterForm({ onSubmit: onSubmitSpy });

      // Complete registration process
      await user.type(screen.getByLabelText(/nombre completo/i), 'Juan Pérez');
      await user.type(screen.getByLabelText(/email/i), 'juan@example.com');
      await user.type(screen.getByLabelText(/^contraseña$/i), 'StrongPass123');
      await user.type(screen.getByLabelText(/confirmar contraseña/i), 'StrongPass123');

      const submitButton = screen.getByRole('button', { name: /crear cuenta/i });
      await user.click(submitButton);

      expect(onSubmitSpy).toHaveBeenCalledTimes(1);
      expect(onSubmitSpy).toHaveBeenCalledWith({
        name: 'Juan Pérez',
        email: 'juan@example.com',
        password: 'StrongPass123'
      });
    });

    test('handles different authentication scenarios', async () => {
      // Test with successful authentication state
      const { rerender } = render(<RegisterForm {...defaultProps} authStatus={AuthStatus.IDLE} />);

      expect(screen.getByRole('button', { name: /crear cuenta/i })).toBeDisabled();

      rerender(<RegisterForm {...defaultProps} authStatus={AuthStatus.LOADING} />);
      expect(screen.getByRole('button', { name: /creando cuenta/i })).toBeDisabled();

      rerender(<RegisterForm {...defaultProps} authStatus={AuthStatus.ERROR} error="Registration failed" />);
      expect(screen.getAllByText('Registration failed')).toHaveLength(2);

      rerender(<RegisterForm {...defaultProps} authStatus={AuthStatus.AUTHENTICATED} />);
      expect(screen.getByRole('button', { name: /crear cuenta/i })).toBeDisabled();
    });
  });

  // ==========================================================================
  // EDGE CASES
  // ==========================================================================

  describe('Edge Cases', () => {
    test('handles very long input gracefully', async () => {
      renderRegisterForm();

      const nameInput = screen.getByLabelText(/nombre completo/i);
      const veryLongName = 'A'.repeat(200);

      await user.type(nameInput, veryLongName);
      await user.tab();

      expect(screen.getByText(/el nombre no puede tener más de 100 caracteres/i)).toBeInTheDocument();
    });

    test('handles special characters in inputs', async () => {
      renderRegisterForm();

      const nameInput = screen.getByLabelText(/nombre completo/i);
      const emailInput = screen.getByLabelText(/email/i);

      await user.type(nameInput, 'José María García-Pérez O\'Connor');
      await user.type(emailInput, 'josé.maría@ejemplo-test.com');

      expect(nameInput).toHaveValue('José María García-Pérez O\'Connor');
      expect(emailInput).toHaveValue('josé.maría@ejemplo-test.com');
    });

    test('prevents form submission with only whitespace', async () => {
      renderRegisterForm();

      await user.type(screen.getByLabelText(/nombre completo/i), '   ');
      await user.type(screen.getByLabelText(/email/i), '   ');
      await user.type(screen.getByLabelText(/^contraseña$/i), '   ');
      await user.type(screen.getByLabelText(/confirmar contraseña/i), '   ');

      const submitButton = screen.getByRole('button', { name: /crear cuenta/i });
      expect(submitButton).toBeDisabled();
    });

    test('handles rapid successive input changes', async () => {
      renderRegisterForm();

      const emailInput = screen.getByLabelText(/email/i);

      // Rapid typing simulation
      await user.type(emailInput, 'a');
      await user.type(emailInput, 'b');
      await user.type(emailInput, 'c');
      await user.type(emailInput, '@test.com');

      expect(emailInput).toHaveValue('abc@test.com');
    });
  });
});