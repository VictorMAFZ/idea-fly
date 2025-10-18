/**
 * Services Index for IdeaFly Authentication System.
 * 
 * Central export point for all service modules, including
 * HTTP client and authentication service.
 */

// ============================================================================
// HTTP CLIENT EXPORTS
// ============================================================================

export {
  httpClient,
  HttpClient,
  createHttpClient,
  setAuthToken,
  clearAuthToken,
  hasAuthToken,
} from './httpClient';

// ============================================================================
// AUTHENTICATION SERVICE EXPORTS
// ============================================================================

export {
  authService,
  AuthService,
} from './authService';

// ============================================================================
// TYPE EXPORTS
// ============================================================================

export type { 
  ApiResponse, 
  ErrorResponse, 
  HttpClientConfig 
} from './httpClient';

// Default exports
export { default as httpClientDefault } from './httpClient';
export { default as authServiceDefault } from './authService';