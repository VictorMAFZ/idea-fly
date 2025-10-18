/**
 * Environment configuration for IdeaFly Frontend.
 * 
 * This module handles loading and validating Next.js environment variables.
 * All variables must have NEXT_PUBLIC_ prefix to be available in the browser.
 */

interface AppConfig {
  // API Configuration
  apiUrl: string;
  apiVersion: string;
  
  // Google OAuth
  googleClientId: string;
  
  // Application Info
  appName: string;
  appVersion: string;
  appDescription: string;
  
  // Authentication
  jwtStorageKey: string;
  userStorageKey: string;
  sessionTimeout: number;
  
  // Development
  debugMode: boolean;
  logLevel: string;
  
  // Feature Flags
  enableGoogleAuth: boolean;
  enableEmailAuth: boolean;
  enableRegistration: boolean;
  
  // UI
  theme: string;
  defaultLocale: string;
}

/**
 * Get environment variable with validation
 */
function getEnvVar(key: string, defaultValue?: string): string {
  const value = process.env[key] || defaultValue;
  if (!value) {
    throw new Error(`Missing required environment variable: ${key}`);
  }
  return value;
}

/**
 * Get boolean environment variable
 */
function getBoolEnvVar(key: string, defaultValue = false): boolean {
  const value = process.env[key];
  if (!value) return defaultValue;
  return value.toLowerCase() === 'true';
}

/**
 * Get numeric environment variable
 */
function getNumericEnvVar(key: string, defaultValue: number): number {
  const value = process.env[key];
  if (!value) return defaultValue;
  const parsed = parseInt(value, 10);
  if (isNaN(parsed)) {
    throw new Error(`Invalid numeric environment variable: ${key}=${value}`);
  }
  return parsed;
}

/**
 * Application configuration loaded from environment variables
 */
export const config: AppConfig = {
  // API Configuration
  apiUrl: getEnvVar('NEXT_PUBLIC_API_URL', 'http://localhost:8000'),
  apiVersion: getEnvVar('NEXT_PUBLIC_API_VERSION', 'v1'),
  
  // Google OAuth (required for OAuth functionality)
  googleClientId: getEnvVar('NEXT_PUBLIC_GOOGLE_CLIENT_ID'),
  
  // Application Info
  appName: getEnvVar('NEXT_PUBLIC_APP_NAME', 'IdeaFly'),
  appVersion: getEnvVar('NEXT_PUBLIC_APP_VERSION', '0.1.0'),
  appDescription: getEnvVar('NEXT_PUBLIC_APP_DESCRIPTION', 'Sistema de Autenticación IdeaFly'),
  
  // Authentication
  jwtStorageKey: getEnvVar('NEXT_PUBLIC_JWT_STORAGE_KEY', 'ideafly_auth_token'),
  userStorageKey: getEnvVar('NEXT_PUBLIC_USER_STORAGE_KEY', 'ideafly_user_data'),
  sessionTimeout: getNumericEnvVar('NEXT_PUBLIC_SESSION_TIMEOUT', 1800000), // 30 minutes
  
  // Development
  debugMode: getBoolEnvVar('NEXT_PUBLIC_DEBUG_MODE', false),
  logLevel: getEnvVar('NEXT_PUBLIC_LOG_LEVEL', 'info'),
  
  // Feature Flags
  enableGoogleAuth: getBoolEnvVar('NEXT_PUBLIC_ENABLE_GOOGLE_AUTH', true),
  enableEmailAuth: getBoolEnvVar('NEXT_PUBLIC_ENABLE_EMAIL_AUTH', true),
  enableRegistration: getBoolEnvVar('NEXT_PUBLIC_ENABLE_REGISTRATION', true),
  
  // UI
  theme: getEnvVar('NEXT_PUBLIC_THEME', 'light'),
  defaultLocale: getEnvVar('NEXT_PUBLIC_DEFAULT_LOCALE', 'es-ES'),
};

/**
 * Validate configuration on module load
 */
function validateConfig(): void {
  // Validate API URL format
  try {
    new URL(config.apiUrl);
  } catch {
    throw new Error(`Invalid API URL: ${config.apiUrl}`);
  }
  
  // Validate Google Client ID format (if Google Auth is enabled)
  if (config.enableGoogleAuth && !config.googleClientId.endsWith('.apps.googleusercontent.com')) {
    throw new Error(`Invalid Google Client ID format: ${config.googleClientId}`);
  }
  
  // Validate session timeout
  if (config.sessionTimeout < 60000) { // Minimum 1 minute
    throw new Error(`Session timeout too short: ${config.sessionTimeout}ms`);
  }
  
  console.log('✅ Frontend configuration validated successfully');
  
  if (config.debugMode) {
    console.log('🔧 Debug mode enabled - Configuration:', {
      apiUrl: config.apiUrl,
      googleAuthEnabled: config.enableGoogleAuth,
      emailAuthEnabled: config.enableEmailAuth,
      registrationEnabled: config.enableRegistration,
    });
  }
}

// Validate on module load (only in development)
if (process.env.NODE_ENV === 'development') {
  validateConfig();
}

export default config;