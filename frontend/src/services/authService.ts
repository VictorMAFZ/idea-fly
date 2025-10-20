/**
 * Authentication Service for IdeaFly Authentication System.
 * 
 * Provides high-level authentication functions that use the HTTP client
 * to interact with backend authentication endpoints.
 */

'use client';

import { httpClient } from './httpClient';
import {
  RegisterRequest,
  LoginRequest,
  GoogleOAuthRequest,
  GoogleTokenRequest,
  AuthResponse,
  User,
  LogoutResponse,
  ApiResponse,
} from '../types/auth';

// ============================================================================
// AUTHENTICATION ENDPOINTS
// ============================================================================

/** API endpoint paths */
const ENDPOINTS = {
  REGISTER: '/auth/register',
  LOGIN: '/auth/login',
  LOGOUT: '/auth/logout',
  GOOGLE_OAUTH: '/auth/google',
  GOOGLE_CALLBACK: '/auth/google/callback',
  USER_PROFILE: '/users/me',
  REFRESH_TOKEN: '/auth/refresh',
} as const;

// ============================================================================
// AUTHENTICATION SERVICE CLASS
// ============================================================================

class AuthService {
  /**
   * Register a new user account.
   * 
   * @param request - User registration data
   * @returns Promise resolving to authentication response
   * 
   * @example
   * ```typescript
   * const result = await authService.register({
   *   name: "John Doe",
   *   email: "john@example.com", 
   *   password: "SecurePass123!"
   * });
   * 
   * if (result.success) {
   *   const { access_token } = result.data;
   *   // Handle successful registration
   * } else {
   *   console.error(result.error.message);
   * }
   * ```
   */
  async register(request: RegisterRequest): Promise<ApiResponse<AuthResponse>> {
    const response = await httpClient.post<AuthResponse>(
      ENDPOINTS.REGISTER,
      request
    );

    if (response.success && response.data) {
      // Registration successful - token is in the response
      console.log('User registration successful');
    }

    return response;
  }

  /**
   * Login with email and password.
   * 
   * @param request - User login credentials
   * @returns Promise resolving to authentication response
   * 
   * @example
   * ```typescript
   * const result = await authService.login({
   *   email: "john@example.com",
   *   password: "SecurePass123!"
   * });
   * 
   * if (result.success) {
   *   const { access_token } = result.data;
   *   // Handle successful login
   * } else {
   *   console.error(result.error.message);
   * }
   * ```
   */
  async login(request: LoginRequest): Promise<ApiResponse<AuthResponse>> {
    const response = await httpClient.post<AuthResponse>(
      ENDPOINTS.LOGIN,
      request
    );

    if (response.success && response.data) {
      console.log('User login successful');
    }

    return response;
  }

  /**
   * Complete Google OAuth authentication.
   * 
   * @param request - Google OAuth callback data
   * @returns Promise resolving to authentication response
   * 
   * @example
   * ```typescript
   * const result = await authService.googleCallback({
   *   code: "google_auth_code",
   *   state: "csrf_protection_state"
   * });
   * 
   * if (result.success) {
   *   const { access_token } = result.data;
   *   // Handle successful Google login
   * }
   * ```
   */
  async googleCallback(request: GoogleOAuthRequest): Promise<ApiResponse<AuthResponse>> {
    const response = await httpClient.post<AuthResponse>(
      ENDPOINTS.GOOGLE_CALLBACK,
      request
    );

    if (response.success && response.data) {
      console.log('Google OAuth authentication successful');
    }

    return response;
  }

  /**
   * Logout current user.
   * 
   * @returns Promise resolving to logout response
   * 
   * @example
   * ```typescript
   * const result = await authService.logout();
   * 
   * if (result.success) {
   *   // Handle successful logout
   *   console.log('User logged out successfully');
   * }
   * ```
   */
  async logout(): Promise<ApiResponse<LogoutResponse>> {
    const response = await httpClient.post<LogoutResponse>(ENDPOINTS.LOGOUT);

    if (response.success) {
      console.log('User logout successful');
    }

    return response;
  }

  /**
   * Get current user profile.
   * 
   * @returns Promise resolving to user profile data
   * 
   * @example
   * ```typescript
   * const result = await authService.getUserProfile();
   * 
   * if (result.success) {
   *   const user = result.data;
   *   console.log(`Welcome, ${user.name}!`);
   * } else {
   *   // Handle error - user might not be authenticated
   *   console.error(result.error.message);
   * }
   * ```
   */
  async getUserProfile(): Promise<ApiResponse<User>> {
    const response = await httpClient.get<User>(ENDPOINTS.USER_PROFILE);

    if (response.success && response.data) {
      console.log('User profile retrieved successfully');
    }

    return response;
  }

  /**
   * Refresh authentication token.
   * 
   * @returns Promise resolving to new authentication response
   * 
   * @example
   * ```typescript
   * const result = await authService.refreshToken();
   * 
   * if (result.success) {
   *   const { access_token } = result.data;
   *   // Handle successful token refresh
   * } else {
   *   // Token refresh failed - user needs to login again
   *   console.error('Token refresh failed:', result.error.message);
   * }
   * ```
   */
  async refreshToken(): Promise<ApiResponse<AuthResponse>> {
    const response = await httpClient.post<AuthResponse>(ENDPOINTS.REFRESH_TOKEN);

    if (response.success && response.data) {
      console.log('Token refresh successful');
    }

    return response;
  }

  /**
   * Update user profile.
   * 
   * @param updates - Partial user data to update
   * @returns Promise resolving to updated user data
   * 
   * @example
   * ```typescript
   * const result = await authService.updateProfile({
   *   name: "John Updated"
   * });
   * 
   * if (result.success) {
   *   console.log('Profile updated successfully');
   * }
   * ```
   */
  async updateProfile(updates: Partial<Pick<User, 'name' | 'email'>>): Promise<ApiResponse<User>> {
    const response = await httpClient.patch<User>(
      ENDPOINTS.USER_PROFILE,
      updates
    );

    if (response.success && response.data) {
      console.log('User profile updated successfully');
    }

    return response;
  }

  /**
   * Change user password.
   * 
   * @param data - Password change data
   * @returns Promise resolving to success response
   * 
   * @example
   * ```typescript
   * const result = await authService.changePassword({
   *   current_password: "OldPass123!",
   *   new_password: "NewPass123!",
   *   confirm_password: "NewPass123!"
   * });
   * 
   * if (result.success) {
   *   console.log('Password changed successfully');
   * }
   * ```
   */
  async changePassword(data: {
    current_password: string;
    new_password: string;
    confirm_password: string;
  }): Promise<ApiResponse<{ message: string }>> {
    const response = await httpClient.post<{ message: string }>(
      '/auth/change-password',
      data
    );

    if (response.success) {
      console.log('Password changed successfully');
    }

    return response;
  }

  /**
   * Request password reset email.
   * 
   * @param email - Email address to send reset link to
   * @returns Promise resolving to success response
   * 
   * @example
   * ```typescript
   * const result = await authService.requestPasswordReset("john@example.com");
   * 
   * if (result.success) {
   *   console.log('Password reset email sent');
   * }
   * ```
   */
  async requestPasswordReset(email: string): Promise<ApiResponse<{ message: string }>> {
    const response = await httpClient.post<{ message: string }>(
      '/auth/password-reset/request',
      { email }
    );

    if (response.success) {
      console.log('Password reset email sent');
    }

    return response;
  }

  /**
   * Reset password using reset token.
   * 
   * @param data - Password reset data
   * @returns Promise resolving to success response
   * 
   * @example
   * ```typescript
   * const result = await authService.resetPassword({
   *   token: "reset_token_from_email",
   *   new_password: "NewPass123!",
   *   confirm_password: "NewPass123!"
   * });
   * 
   * if (result.success) {
   *   console.log('Password reset successfully');
   * }
   * ```
   */
  async resetPassword(data: {
    token: string;
    new_password: string;
    confirm_password: string;
  }): Promise<ApiResponse<{ message: string }>> {
    const response = await httpClient.post<{ message: string }>(
      '/auth/password-reset/confirm',
      data
    );

    if (response.success) {
      console.log('Password reset successfully');
    }

    return response;
  }

  /**
   * Verify email address.
   * 
   * @param token - Email verification token
   * @returns Promise resolving to success response
   * 
   * @example
   * ```typescript
   * const result = await authService.verifyEmail("verification_token");
   * 
   * if (result.success) {
   *   console.log('Email verified successfully');
   * }
   * ```
   */
  async verifyEmail(token: string): Promise<ApiResponse<{ message: string }>> {
    const response = await httpClient.post<{ message: string }>(
      `/auth/verify-email/${token}`
    );

    if (response.success) {
      console.log('Email verified successfully');
    }

    return response;
  }

  /**
   * Authenticate with Google OAuth using access token.
   * 
   * This method sends a Google OAuth access token to the backend
   * for validation and user authentication/creation.
   * 
   * @param accessToken - Google OAuth access token
   * @returns Promise resolving to authentication response
   * 
   * @example
   * ```typescript
   * const result = await authService.authenticateWithGoogle("ya29.a0ARrd...");
   * 
   * if (result.success) {
   *   const { access_token, user } = result.data;
   *   // Handle successful Google authentication
   * }
   * ```
   */
  async authenticateWithGoogle(accessToken: string): Promise<ApiResponse<AuthResponse>> {
    if (!accessToken) {
      throw new Error('Google access token is required');
    }

    const response = await httpClient.post<AuthResponse>(
      ENDPOINTS.GOOGLE_OAUTH,
      { access_token: accessToken } as GoogleTokenRequest
    );

    if (response.success && response.data) {
      console.log('Google OAuth authentication successful via access token');
    }

    return response;
  }

  /**
   * Resend email verification.
   * 
   * @returns Promise resolving to success response
   * 
   * @example
   * ```typescript
   * const result = await authService.resendVerificationEmail();
   * 
   * if (result.success) {
   *   console.log('Verification email sent');
   * }
   * ```
   */
  async resendVerificationEmail(): Promise<ApiResponse<{ message: string }>> {
    const response = await httpClient.post<{ message: string }>(
      '/auth/resend-verification'
    );

    if (response.success) {
      console.log('Verification email sent');
    }

    return response;
  }
}

// ============================================================================
// SINGLETON INSTANCE
// ============================================================================

/** Global authentication service instance */
export const authService = new AuthService();

// ============================================================================
// EXPORTS
// ============================================================================

export default authService;
export { AuthService };