/**
 * Component tests for GoogleAuthButton.
 * 
 * Tests the GoogleAuthButton component including:
 * - Rendering with different props
 * - User interactions
 * - Loading states
 * - Error handling
 * - Accessibility features
 * - OAuth flow integration
 */

import React from 'react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { GoogleOAuthProvider } from '@react-oauth/google';
import GoogleAuthButton from '../../../src/components/auth/GoogleAuthButton';

// Mock @react-oauth/google
const mockGoogleLogin = vi.fn();
vi.mock('@react-oauth/google', async () => {
  const actual = await vi.importActual('@react-oauth/google');
  return {
    ...actual,
    useGoogleLogin: () => mockGoogleLogin,
  };
});

// Mock environment variable for Google Client ID
const MOCK_GOOGLE_CLIENT_ID = 'mock_google_client_id';

// Test wrapper component with Google OAuth Provider
function GoogleAuthTestWrapper({ children }: { children: React.ReactNode }) {
  return (
    <GoogleOAuthProvider clientId={MOCK_GOOGLE_CLIENT_ID}>
      {children}
    </GoogleOAuthProvider>
  );
}

// Helper function to render GoogleAuthButton with provider
function renderGoogleAuthButton(props: any = {}) {
  const defaultProps = {
    onSuccess: vi.fn(),
    onError: vi.fn(),
    ...props,
  };

  return {
    ...render(
      <GoogleAuthTestWrapper>
        <GoogleAuthButton {...defaultProps} />
      </GoogleAuthTestWrapper>
    ),
    props: defaultProps,
  };
}

describe('GoogleAuthButton', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  describe('Rendering', () => {
    it('renders with default props', () => {
      renderGoogleAuthButton();
      
      const button = screen.getByRole('button', { name: /continue with google/i });
      expect(button).toBeInTheDocument();
      expect(button).not.toBeDisabled();
    });

    it('renders with custom text', () => {
      renderGoogleAuthButton({ text: 'Sign in with Google' });
      
      const button = screen.getByRole('button', { name: /sign in with google/i });
      expect(button).toBeInTheDocument();
    });

    it('renders Google icon when not loading', () => {
      renderGoogleAuthButton();
      
      const icon = screen.getByRole('button').querySelector('svg');
      expect(icon).toBeInTheDocument();
      expect(icon).toHaveAttribute('aria-hidden', 'true');
    });

    it('renders loading spinner when loading', () => {
      renderGoogleAuthButton({ loading: true });
      
      const button = screen.getByRole('button', { name: /signing in with google/i });
      expect(button).toBeInTheDocument();
      
      // Should show loading spinner instead of icon
      const spinner = button.querySelector('.animate-spin');
      expect(spinner).toBeInTheDocument();
      
      const icon = button.querySelector('svg');
      expect(icon).not.toBeInTheDocument();
      
      expect(button).toHaveTextContent('Signing in...');
    });

    it('renders as disabled when disabled prop is true', () => {
      renderGoogleAuthButton({ disabled: true });
      
      const button = screen.getByRole('button');
      expect(button).toBeDisabled();
    });

    it('applies correct size classes', () => {
      const { rerender } = render(
        <GoogleAuthTestWrapper>
          <GoogleAuthButton onSuccess={vi.fn()} onError={vi.fn()} size="sm" />
        </GoogleAuthTestWrapper>
      );
      
      let button = screen.getByRole('button');
      expect(button).toHaveClass('px-4', 'py-2', 'text-sm');
      
      rerender(
        <GoogleAuthTestWrapper>
          <GoogleAuthButton onSuccess={vi.fn()} onError={vi.fn()} size="lg" />
        </GoogleAuthTestWrapper>
      );
      
      button = screen.getByRole('button');
      expect(button).toHaveClass('px-8', 'py-4', 'text-lg');
    });

    it('applies correct variant classes', () => {
      const { rerender } = render(
        <GoogleAuthTestWrapper>
          <GoogleAuthButton onSuccess={vi.fn()} onError={vi.fn()} variant="filled" />
        </GoogleAuthTestWrapper>
      );
      
      let button = screen.getByRole('button');
      expect(button).toHaveClass('bg-white', 'text-gray-700');
      
      rerender(
        <GoogleAuthTestWrapper>
          <GoogleAuthButton onSuccess={vi.fn()} onError={vi.fn()} variant="outlined" />
        </GoogleAuthTestWrapper>
      );
      
      button = screen.getByRole('button');
      expect(button).toHaveClass('bg-transparent', 'border-2');
    });

    it('applies custom className', () => {
      renderGoogleAuthButton({ className: 'custom-class' });
      
      const button = screen.getByRole('button');
      expect(button).toHaveClass('custom-class');
    });
  });

  describe('Accessibility', () => {
    it('has proper ARIA labels', () => {
      renderGoogleAuthButton();
      
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-label', 'Continue with Google');
      expect(button).toHaveAttribute('aria-describedby', 'google-auth-description');
    });

    it('has proper ARIA label when loading', () => {
      renderGoogleAuthButton({ loading: true });
      
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-label', 'Signing in with Google...');
    });

    it('has screen reader description', () => {
      renderGoogleAuthButton();
      
      const description = document.getElementById('google-auth-description');
      expect(description).toBeInTheDocument();
      expect(description).toHaveClass('sr-only');
      expect(description).toHaveTextContent(
        "Sign in with your Google account. This will open Google's secure authentication page."
      );
    });

    it('is keyboard accessible', async () => {
      const user = userEvent.setup();
      renderGoogleAuthButton();
      
      const button = screen.getByRole('button');
      
      // Should be focusable
      await user.tab();
      expect(button).toHaveFocus();
      
      // Should be activatable with Enter
      await user.keyboard('{Enter}');
      expect(mockGoogleLogin).toHaveBeenCalledTimes(1);
      
      // Should be activatable with Space
      await user.keyboard(' ');
      expect(mockGoogleLogin).toHaveBeenCalledTimes(2);
    });

    it('has proper focus styles', () => {
      renderGoogleAuthButton();
      
      const button = screen.getByRole('button');
      expect(button).toHaveClass('focus:outline-none', 'focus:ring-2', 'focus:ring-blue-500');
    });
  });

  describe('User Interactions', () => {
    it('calls googleLogin when clicked', async () => {
      const user = userEvent.setup();
      renderGoogleAuthButton();
      
      const button = screen.getByRole('button');
      await user.click(button);
      
      expect(mockGoogleLogin).toHaveBeenCalledTimes(1);
    });

    it('does not call googleLogin when disabled', async () => {
      const user = userEvent.setup();
      renderGoogleAuthButton({ disabled: true });
      
      const button = screen.getByRole('button');
      await user.click(button);
      
      expect(mockGoogleLogin).not.toHaveBeenCalled();
    });

    it('does not call googleLogin when loading', async () => {
      const user = userEvent.setup();
      renderGoogleAuthButton({ loading: true });
      
      const button = screen.getByRole('button');
      await user.click(button);
      
      expect(mockGoogleLogin).not.toHaveBeenCalled();
    });

    it('handles hover effects', async () => {
      const user = userEvent.setup();
      renderGoogleAuthButton();
      
      const button = screen.getByRole('button');
      
      await user.hover(button);
      expect(button).toHaveClass('hover:scale-105');
      
      await user.unhover(button);
      // Button should still have hover classes defined in CSS
    });

    it('handles active state', () => {
      renderGoogleAuthButton();
      
      const button = screen.getByRole('button');
      expect(button).toHaveClass('active:scale-95');
    });
  });

  describe('OAuth Flow Integration', () => {
    it('configures useGoogleLogin with correct options', () => {
      // Mock the useGoogleLogin hook to capture its configuration
      const mockUseGoogleLogin = vi.fn().mockReturnValue(mockGoogleLogin);
      
      vi.doMock('@react-oauth/google', () => ({
        useGoogleLogin: mockUseGoogleLogin,
        GoogleOAuthProvider: ({ children }: any) => children,
      }));
      
      const { props } = renderGoogleAuthButton();
      
      // The hook should be called with correct configuration
      expect(mockUseGoogleLogin).toHaveBeenCalledWith(
        expect.objectContaining({
          scope: 'email profile',
          flow: 'implicit',
          onSuccess: expect.any(Function),
          onError: expect.any(Function),
        })
      );
    });

    it('handles successful OAuth response', async () => {
      const onSuccess = vi.fn();
      const mockTokenResponse = { access_token: 'mock_access_token' };
      
      // Mock successful OAuth response
      const mockUseGoogleLogin = vi.fn().mockImplementation(({ onSuccess: handleSuccess }) => {
        return () => handleSuccess(mockTokenResponse);
      });
      
      vi.doMock('@react-oauth/google', () => ({
        useGoogleLogin: mockUseGoogleLogin,
        GoogleOAuthProvider: ({ children }: any) => children,
      }));
      
      const user = userEvent.setup();
      renderGoogleAuthButton({ onSuccess });
      
      const button = screen.getByRole('button');
      await user.click(button);
      
      await waitFor(() => {
        expect(onSuccess).toHaveBeenCalledWith('mock_access_token');
      });
    });

    it('handles OAuth response without access_token', async () => {
      const onError = vi.fn();
      const mockTokenResponse = {}; // No access_token
      
      const mockUseGoogleLogin = vi.fn().mockImplementation(({ onSuccess: handleSuccess }) => {
        return () => handleSuccess(mockTokenResponse);
      });
      
      vi.doMock('@react-oauth/google', () => ({
        useGoogleLogin: mockUseGoogleLogin,
        GoogleOAuthProvider: ({ children }: any) => children,
      }));
      
      const user = userEvent.setup();
      renderGoogleAuthButton({ onError });
      
      const button = screen.getByRole('button');
      await user.click(button);
      
      await waitFor(() => {
        expect(onError).toHaveBeenCalledWith('No access token received from Google');
      });
    });

    it('handles OAuth error response', async () => {
      const onError = vi.fn();
      const mockError = { error: 'access_denied' };
      
      const mockUseGoogleLogin = vi.fn().mockImplementation(({ onError: handleError }) => {
        return () => handleError(mockError);
      });
      
      vi.doMock('@react-oauth/google', () => ({
        useGoogleLogin: mockUseGoogleLogin,
        GoogleOAuthProvider: ({ children }: any) => children,
      }));
      
      const user = userEvent.setup();
      renderGoogleAuthButton({ onError });
      
      const button = screen.getByRole('button');
      await user.click(button);
      
      await waitFor(() => {
        expect(onError).toHaveBeenCalledWith('Google authentication failed. Please try again.');
      });
    });
  });

  describe('Loading States', () => {
    it('manages internal loading state during OAuth flow', async () => {
      const onSuccess = vi.fn();
      
      let resolveOAuth: (value: any) => void;
      const oauthPromise = new Promise(resolve => {
        resolveOAuth = resolve;
      });
      
      const mockUseGoogleLogin = vi.fn().mockImplementation(({ onSuccess: handleSuccess }) => {
        return async () => {
          const result = await oauthPromise;
          handleSuccess(result);
        };
      });
      
      vi.doMock('@react-oauth/google', () => ({
        useGoogleLogin: mockUseGoogleLogin,
        GoogleOAuthProvider: ({ children }: any) => children,
      }));
      
      const user = userEvent.setup();
      renderGoogleAuthButton({ onSuccess });
      
      const button = screen.getByRole('button');
      await user.click(button);
      
      // Button should be in loading state
      await waitFor(() => {
        expect(button).toHaveTextContent('Signing in...');
        expect(button).toBeDisabled();
      });
      
      // Resolve the OAuth flow
      resolveOAuth!({ access_token: 'test_token' });
      
      // Button should return to normal state
      await waitFor(() => {
        expect(button).toHaveTextContent('Continue with Google');
        expect(button).not.toBeDisabled();
      });
      
      expect(onSuccess).toHaveBeenCalledWith('test_token');
    });

    it('clears loading state on error', async () => {
      const onError = vi.fn();
      
      const mockUseGoogleLogin = vi.fn().mockImplementation(({ onSuccess: handleSuccess }) => {
        return () => {
          handleSuccess({}); // Invalid response without access_token
        };
      });
      
      vi.doMock('@react-oauth/google', () => ({
        useGoogleLogin: mockUseGoogleLogin,
        GoogleOAuthProvider: ({ children }: any) => children,
      }));
      
      const user = userEvent.setup();
      renderGoogleAuthButton({ onError });
      
      const button = screen.getByRole('button');
      await user.click(button);
      
      // Button should return to normal state after error
      await waitFor(() => {
        expect(button).toHaveTextContent('Continue with Google');
        expect(button).not.toBeDisabled();
      });
      
      expect(onError).toHaveBeenCalled();
    });

    it('respects external loading prop', () => {
      renderGoogleAuthButton({ loading: true });
      
      const button = screen.getByRole('button');
      expect(button).toBeDisabled();
      expect(button).toHaveTextContent('Signing in...');
    });
  });

  describe('Error Handling', () => {
    it('handles exceptions during OAuth success processing', async () => {
      const onError = vi.fn();
      const onSuccess = vi.fn().mockImplementation(() => {
        throw new Error('Processing failed');
      });
      
      const mockUseGoogleLogin = vi.fn().mockImplementation(({ onSuccess: handleSuccess }) => {
        return () => handleSuccess({ access_token: 'test_token' });
      });
      
      vi.doMock('@react-oauth/google', () => ({
        useGoogleLogin: mockUseGoogleLogin,
        GoogleOAuthProvider: ({ children }: any) => children,
      }));
      
      const user = userEvent.setup();
      renderGoogleAuthButton({ onSuccess, onError });
      
      const button = screen.getByRole('button');
      await user.click(button);
      
      await waitFor(() => {
        expect(onError).toHaveBeenCalledWith('Processing failed');
      });
    });

    it('handles non-Error exceptions', async () => {
      const onError = vi.fn();
      const onSuccess = vi.fn().mockImplementation(() => {
        throw 'String error';
      });
      
      const mockUseGoogleLogin = vi.fn().mockImplementation(({ onSuccess: handleSuccess }) => {
        return () => handleSuccess({ access_token: 'test_token' });
      });
      
      vi.doMock('@react-oauth/google', () => ({
        useGoogleLogin: mockUseGoogleLogin,
        GoogleOAuthProvider: ({ children }: any) => children,
      }));
      
      const user = userEvent.setup();
      renderGoogleAuthButton({ onSuccess, onError });
      
      const button = screen.getByRole('button');
      await user.click(button);
      
      await waitFor(() => {
        expect(onError).toHaveBeenCalledWith('Google authentication failed');
      });
    });
  });

  describe('Component Variants and Customization', () => {
    it('supports all size variants', () => {
      const sizes: Array<'sm' | 'md' | 'lg'> = ['sm', 'md', 'lg'];
      
      sizes.forEach(size => {
        const { unmount } = renderGoogleAuthButton({ size });
        const button = screen.getByRole('button');
        
        switch (size) {
          case 'sm':
            expect(button).toHaveClass('px-4', 'py-2', 'text-sm');
            break;
          case 'md':
            expect(button).toHaveClass('px-6', 'py-3', 'text-base');
            break;
          case 'lg':
            expect(button).toHaveClass('px-8', 'py-4', 'text-lg');
            break;
        }
        
        unmount();
      });
    });

    it('supports all variant styles', () => {
      const variants: Array<'filled' | 'outlined'> = ['filled', 'outlined'];
      
      variants.forEach(variant => {
        const { unmount } = renderGoogleAuthButton({ variant });
        const button = screen.getByRole('button');
        
        switch (variant) {
          case 'filled':
            expect(button).toHaveClass('bg-white', 'text-gray-700');
            break;
          case 'outlined':
            expect(button).toHaveClass('bg-transparent', 'border-2');
            break;
        }
        
        unmount();
      });
    });

    it('combines multiple customization props', () => {
      renderGoogleAuthButton({
        text: 'Register with Google',
        size: 'lg',
        variant: 'filled',
        className: 'custom-style'
      });
      
      const button = screen.getByRole('button', { name: /register with google/i });
      expect(button).toHaveClass('px-8', 'py-4', 'text-lg', 'bg-white', 'custom-style');
    });
  });

  describe('Console Error Handling', () => {
    let consoleSpy: any;
    
    beforeEach(() => {
      consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    });
    
    afterEach(() => {
      consoleSpy.mockRestore();
    });
    
    it('logs OAuth errors to console', async () => {
      const onError = vi.fn();
      const mockError = { error: 'popup_blocked' };
      
      const mockUseGoogleLogin = vi.fn().mockImplementation(({ onError: handleError }) => {
        return () => handleError(mockError);
      });
      
      vi.doMock('@react-oauth/google', () => ({
        useGoogleLogin: mockUseGoogleLogin,
        GoogleOAuthProvider: ({ children }: any) => children,
      }));
      
      const user = userEvent.setup();
      renderGoogleAuthButton({ onError });
      
      const button = screen.getByRole('button');
      await user.click(button);
      
      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith('Google OAuth Error:', mockError);
        expect(onError).toHaveBeenCalled();
      });
    });
  });
});