/**
 * TypeScript interfaces for IdeaFly Authentication System.
 * 
 * These interfaces define the shape of data exchanged between frontend and backend,
 * ensuring type safety and consistency across API requests and responses.
 */



// ============================================================================
// ENUMS
// ============================================================================

/**
 * Authentication provider options.
 * Must match backend AuthProvider enum.
 */
export enum AuthProvider {
  EMAIL = "email",
  GOOGLE = "google", 
  MIXED = "mixed"
}

/**
 * JWT token type.
 * Must match backend TokenType enum.
 */
export enum TokenType {
  BEARER = "bearer"
}

/**
 * Authentication status for UI state management.
 */
export enum AuthStatus {
  IDLE = "idle",
  LOADING = "loading", 
  AUTHENTICATED = "authenticated",
  UNAUTHENTICATED = "unauthenticated",
  ERROR = "error"
}

// ============================================================================
// REQUEST INTERFACES (Input DTOs)
// ============================================================================

/**
 * User registration request payload.
 * Must match backend UserRegistrationRequest schema.
 */
export interface RegisterRequest {
  /** Full name of the user (2-100 characters) */
  name: string;
  /** Valid email address for login and communication */
  email: string;
  /** Strong password (minimum 8 characters) */
  password: string;
}

/**
 * User login request payload.
 * Must match backend UserLoginRequest schema.
 */
export interface LoginRequest {
  /** User email address */
  email: string;
  /** User password */
  password: string;
}

/**
 * Google OAuth callback request payload.
 * Must match backend GoogleOAuthRequest schema.
 */
export interface GoogleOAuthRequest {
  /** Authorization code from Google OAuth flow */
  code: string;
  /** State parameter for CSRF protection (optional) */
  state?: string;
}

/**
 * Google OAuth access token request payload.
 * For direct token authentication (frontend flow).
 */
export interface GoogleTokenRequest {
  /** Google OAuth access token */
  access_token: string;
}

// ============================================================================
// RESPONSE INTERFACES (Output DTOs)  
// ============================================================================

/**
 * JWT authentication response.
 * Must match backend Token/AuthResponse schema.
 */
export interface AuthResponse {
  /** JWT access token */
  access_token: string;
  /** Token type (always 'bearer') */
  token_type: TokenType;
  /** Token expiration time in seconds */
  expires_in: number;
}

/**
 * User profile response from API.
 * Must match backend UserResponse schema.
 */
export interface User {
  /** Unique user identifier (UUID) */
  id: string;
  /** Full name of the user */
  name: string;
  /** User email address */
  email: string;
  /** Primary authentication method */
  auth_provider: AuthProvider;
  /** Whether the user account is active */
  is_active: boolean;
  /** Account creation timestamp (ISO string) */
  created_at: string;
}

/**
 * API error response structure.
 * Must match backend ErrorResponse schema.
 */
export interface ErrorResponse {
  /** Specific error code for programmatic handling */
  error_code: string;
  /** Human-readable error message */
  message: string;
  /** Additional error details (optional) */
  details?: Record<string, any>;
}

/**
 * Validation error response with field details.
 * Must match backend ValidationErrorResponse schema.
 */
export interface ValidationErrorResponse {
  /** Error code for validation failures */
  error_code: string;
  /** General validation error message */
  message: string;
  /** List of field validation errors */
  details: Array<{
    field: string;
    message: string;
    type: string;
  }>;
}

/**
 * Logout success response.
 * Must match backend LogoutResponse schema.
 */
export interface LogoutResponse {
  /** Logout confirmation message */
  message: string;
}

// ============================================================================
// AUTHENTICATION STATE MANAGEMENT
// ============================================================================

/**
 * Complete authentication state for React context.
 * Used by AuthContext to manage authentication state across the app.
 */
export interface AuthState {
  /** Current authentication status */
  status: AuthStatus;
  /** Currently authenticated user (null if not authenticated) */
  user: User | null;
  /** JWT access token (null if not authenticated) */
  token: string | null;
  /** Token expiration timestamp (null if not authenticated) */
  tokenExpiry: number | null;
  /** Current error message (null if no error) */
  error: string | null;
  /** Whether an authentication operation is in progress */
  loading: boolean;
}

/**
 * Authentication context actions for state management.
 * Used by AuthContext to update authentication state.
 */
export interface AuthActions {
  /** Register a new user account */
  register: (request: RegisterRequest) => Promise<void>;
  /** Login with email and password */
  login: (request: LoginRequest) => Promise<void>;
  /** Login/register with Google OAuth */
  loginWithGoogle: (request: GoogleOAuthRequest) => Promise<void>;
  /** Login/register with Google OAuth access token */
  loginWithGoogleToken: (accessToken: string) => Promise<void>;
  /** Logout current user */
  logout: () => Promise<void>;
  /** Refresh current user profile */
  refreshUser: () => Promise<void>;
  /** Clear error state */
  clearError: () => void;
  /** Check if user is authenticated */
  isAuthenticated: () => boolean;
  /** Check if token is expired */
  isTokenExpired: () => boolean;
}

/**
 * Combined authentication context interface.
 * Provides both state and actions to consuming components.
 */
export interface AuthContextType extends AuthState, AuthActions {}

// ============================================================================
// FORM STATE MANAGEMENT
// ============================================================================

/**
 * Form field state for validation and UI feedback.
 */
export interface FormField<T = string> {
  /** Current field value */
  value: T;
  /** Field validation error (null if valid) */
  error: string | null;
  /** Whether field has been touched by user */
  touched: boolean;
  /** Whether field is currently being validated */
  validating: boolean;
}

/**
 * Registration form state.
 */
export interface RegisterFormState {
  name: FormField;
  email: FormField;
  password: FormField;
  confirmPassword: FormField;
  isSubmitting: boolean;
  submitError: string | null;
}

/**
 * Login form state.
 */
export interface LoginFormState {
  email: FormField;
  password: FormField;
  rememberMe: FormField<boolean>;
  isSubmitting: boolean;
  submitError: string | null;
}

// ============================================================================
// API CLIENT TYPES
// ============================================================================

/**
 * HTTP client configuration options.
 */
export interface HttpClientConfig {
  /** Base API URL */
  baseURL: string;
  /** Default request timeout in milliseconds */
  timeout: number;
  /** Default headers to include with requests */
  headers: Record<string, string>;
}

/**
 * API response wrapper for consistent error handling.
 */
export interface ApiResponse<T = any> {
  /** Response data (null on error) */
  data: T | null;
  /** Error information (null on success) */
  error: ErrorResponse | null;
  /** HTTP status code */
  status: number;
  /** Whether the request was successful */
  success: boolean;
}

/**
 * API client interface for authentication endpoints.
 */
export interface AuthApiClient {
  /** Register a new user */
  register: (request: RegisterRequest) => Promise<ApiResponse<AuthResponse>>;
  /** Login with email and password */
  login: (request: LoginRequest) => Promise<ApiResponse<AuthResponse>>;
  /** Google OAuth callback */
  googleCallback: (request: GoogleOAuthRequest) => Promise<ApiResponse<AuthResponse>>;
  /** Logout current user */
  logout: () => Promise<ApiResponse<LogoutResponse>>;
  /** Get current user profile */
  getProfile: () => Promise<ApiResponse<User>>;
}

// ============================================================================
// UTILITY TYPES
// ============================================================================

/**
 * Extract keys from an object type that are of a specific type.
 */
export type KeysOfType<T, U> = {
  [K in keyof T]: T[K] extends U ? K : never;
}[keyof T];

/**
 * Make specific properties optional in an interface.
 */
export type PartialBy<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

/**
 * Make specific properties required in an interface.
 */
export type RequiredBy<T, K extends keyof T> = T & Required<Pick<T, K>>;

/**
 * Authentication hook return type for useAuth hook.
 */
export type UseAuthReturn = AuthContextType;

/**
 * Generic async operation state for UI components.
 */
export interface AsyncOperation<T = any> {
  data: T | null;
  loading: boolean;
  error: string | null;
  execute: (...args: any[]) => Promise<void>;
  reset: () => void;
}

// ============================================================================
// COMPONENT PROP TYPES
// ============================================================================

/**
 * Props for authentication form components.
 */
export interface AuthFormProps {
  /** Callback fired on successful authentication */
  onSuccess?: (user: User) => void;
  /** Callback fired on authentication error */
  onError?: (error: string) => void;
  /** Additional CSS classes */
  className?: string;
  /** Whether to redirect after successful auth */
  redirectAfterAuth?: boolean;
  /** Custom redirect path */
  redirectPath?: string;
}

/**
 * Props for protected route components.
 */
export interface ProtectedRouteProps {
  /** Child components to render if authenticated */
  children: any;
  /** Fallback component for unauthenticated users */
  fallback?: any;
  /** Redirect path for unauthenticated users */
  redirectTo?: string;
  /** Required authentication providers (optional) */
  requiredProviders?: AuthProvider[];
}

// ============================================================================
// EXPORTS
// ============================================================================

// All interfaces, types, and enums are already exported inline above
// No additional exports needed