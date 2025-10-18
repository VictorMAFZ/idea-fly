/**
 * HTTP Client for IdeaFly Authentication System.
 * 
 * Provides a configured axios instance with JWT token management,
 * automatic token injection, error handling, and retry logic.
 */

'use client';

import axios, {
  AxiosInstance,
  AxiosRequestConfig,
  AxiosResponse,
  AxiosError,
  InternalAxiosRequestConfig,
} from 'axios';

import {
  ApiResponse,
  ErrorResponse,
  HttpClientConfig,
} from '../types/auth';

// ============================================================================
// CONFIGURATION
// ============================================================================

/** Default HTTP client configuration */
const defaultConfig: HttpClientConfig = {
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
};

/** Local storage keys (matching AuthContext) */
const AUTH_TOKEN_KEY = 'ideafly_auth_token';
const AUTH_EXPIRY_KEY = 'ideafly_auth_expiry';

// ============================================================================
// TOKEN MANAGEMENT UTILITIES
// ============================================================================

/**
 * Get auth token from localStorage.
 */
function getStoredToken(): string | null {
  try {
    return localStorage.getItem(AUTH_TOKEN_KEY);
  } catch (error) {
    console.error('Failed to get token from localStorage:', error);
    return null;
  }
}

/**
 * Check if stored token is expired.
 */
function isStoredTokenExpired(): boolean {
  try {
    const expiryStr = localStorage.getItem(AUTH_EXPIRY_KEY);
    if (!expiryStr) return true;
    
    const expiry = parseInt(expiryStr, 10);
    return Date.now() >= expiry;
  } catch (error) {
    console.error('Failed to check token expiry:', error);
    return true;
  }
}

/**
 * Clear auth data from localStorage.
 */
function clearStoredAuth(): void {
  try {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(AUTH_EXPIRY_KEY);
    localStorage.removeItem('ideafly_auth_user');
  } catch (error) {
    console.error('Failed to clear auth from localStorage:', error);
  }
}

// ============================================================================
// ERROR HANDLING
// ============================================================================

/**
 * Transform axios error to standardized API response.
 */
function handleApiError(error: AxiosError): ApiResponse {
  const status = error.response?.status || 500;
  
  // Handle network errors
  if (!error.response) {
    return {
      data: null,
      error: {
        error_code: 'NETWORK_ERROR',
        message: 'Network error. Please check your connection.',
      },
      status: 0,
      success: false,
    };
  }

  // Handle timeout errors
  if (error.code === 'ECONNABORTED') {
    return {
      data: null,
      error: {
        error_code: 'TIMEOUT_ERROR', 
        message: 'Request timeout. Please try again.',
      },
      status: 408,
      success: false,
    };
  }

  // Handle structured error responses from backend
  const errorData = error.response.data as any;
  
  if (errorData && typeof errorData === 'object') {
    // FastAPI validation errors
    if (errorData.detail && Array.isArray(errorData.detail)) {
      return {
        data: null,
        error: {
          error_code: 'VALIDATION_ERROR',
          message: 'Validation failed',
          details: errorData.detail,
        },
        status,
        success: false,
      };
    }
    
    // Custom error responses from backend
    if (errorData.error_code || errorData.message) {
      return {
        data: null,
        error: {
          error_code: errorData.error_code || 'UNKNOWN_ERROR',
          message: errorData.message || 'An unknown error occurred',
          details: errorData.details,
        },
        status,
        success: false,
      };
    }
  }

  // Default error mapping by status code
  const defaultErrors: Record<number, { error_code: string; message: string }> = {
    400: { error_code: 'BAD_REQUEST', message: 'Invalid request data' },
    401: { error_code: 'UNAUTHORIZED', message: 'Authentication required' },
    403: { error_code: 'FORBIDDEN', message: 'Access denied' },
    404: { error_code: 'NOT_FOUND', message: 'Resource not found' },
    409: { error_code: 'CONFLICT', message: 'Resource conflict' },
    422: { error_code: 'VALIDATION_ERROR', message: 'Validation failed' },
    429: { error_code: 'RATE_LIMIT', message: 'Too many requests' },
    500: { error_code: 'INTERNAL_ERROR', message: 'Internal server error' },
    502: { error_code: 'BAD_GATEWAY', message: 'Service unavailable' },
    503: { error_code: 'SERVICE_UNAVAILABLE', message: 'Service temporarily unavailable' },
  };

  const defaultError = defaultErrors[status] || {
    error_code: 'UNKNOWN_ERROR',
    message: `HTTP ${status}: ${error.message}`,
  };

  return {
    data: null,
    error: defaultError,
    status,
    success: false,
  };
}

// ============================================================================
// HTTP CLIENT CLASS
// ============================================================================

class HttpClient {
  private axiosInstance: AxiosInstance;
  private isRefreshing: boolean = false;
  private failedQueue: Array<{
    resolve: (value: any) => void;
    reject: (reason: any) => void;
  }> = [];

  constructor(config: Partial<HttpClientConfig> = {}) {
    const finalConfig = { ...defaultConfig, ...config };
    
    this.axiosInstance = axios.create({
      baseURL: finalConfig.baseURL,
      timeout: finalConfig.timeout,
      headers: finalConfig.headers,
    });

    this.setupInterceptors();
  }

  /**
   * Setup request and response interceptors.
   */
  private setupInterceptors(): void {
    // Request interceptor - inject JWT token
    this.axiosInstance.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        const token = getStoredToken();
        
        if (token && !isStoredTokenExpired()) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor - handle token expiration and errors
    this.axiosInstance.interceptors.response.use(
      (response: AxiosResponse) => {
        // Success response - return as-is
        return response;
      },
      async (error: AxiosError) => {
        const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

        // Handle 401 errors - token expired or invalid
        if (error.response?.status === 401 && !originalRequest._retry) {
          // Clear expired token
          clearStoredAuth();
          
          // Emit token expired event for AuthContext to handle
          window.dispatchEvent(new CustomEvent('auth:token-expired'));
          
          // Don't retry, let the app handle redirect to login
          return Promise.reject(error);
        }

        return Promise.reject(error);
      }
    );
  }

  /**
   * Process failed requests queue when token is refreshed.
   */
  private processFailedQueue(error: any, token?: string): void {
    this.failedQueue.forEach(({ resolve, reject }) => {
      if (error) {
        reject(error);
      } else {
        resolve(token);
      }
    });
    
    this.failedQueue = [];
  }

  /**
   * Make GET request.
   */
  async get<T = any>(
    url: string, 
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> {
    try {
      const response = await this.axiosInstance.get<T>(url, config);
      return {
        data: response.data,
        error: null,
        status: response.status,
        success: true,
      };
    } catch (error) {
      return handleApiError(error as AxiosError);
    }
  }

  /**
   * Make POST request.
   */
  async post<T = any>(
    url: string, 
    data?: any, 
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> {
    try {
      const response = await this.axiosInstance.post<T>(url, data, config);
      return {
        data: response.data,
        error: null,
        status: response.status,
        success: true,
      };
    } catch (error) {
      return handleApiError(error as AxiosError);
    }
  }

  /**
   * Make PUT request.
   */
  async put<T = any>(
    url: string, 
    data?: any, 
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> {
    try {
      const response = await this.axiosInstance.put<T>(url, data, config);
      return {
        data: response.data,
        error: null,
        status: response.status,
        success: true,
      };
    } catch (error) {
      return handleApiError(error as AxiosError);
    }
  }

  /**
   * Make PATCH request.
   */
  async patch<T = any>(
    url: string, 
    data?: any, 
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> {
    try {
      const response = await this.axiosInstance.patch<T>(url, data, config);
      return {
        data: response.data,
        error: null,
        status: response.status,
        success: true,
      };
    } catch (error) {
      return handleApiError(error as AxiosError);
    }
  }

  /**
   * Make DELETE request.
   */
  async delete<T = any>(
    url: string, 
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> {
    try {
      const response = await this.axiosInstance.delete<T>(url, config);
      return {
        data: response.data,
        error: null,
        status: response.status,
        success: true,
      };
    } catch (error) {
      return handleApiError(error as AxiosError);
    }
  }

  /**
   * Upload file with progress tracking.
   */
  async upload<T = any>(
    url: string,
    file: File | FormData,
    options?: {
      onUploadProgress?: (progressEvent: any) => void;
      additionalData?: Record<string, any>;
    }
  ): Promise<ApiResponse<T>> {
    try {
      let formData: FormData;
      
      if (file instanceof FormData) {
        formData = file;
      } else {
        formData = new FormData();
        formData.append('file', file);
      }
      
      // Add additional data if provided
      if (options?.additionalData) {
        Object.entries(options.additionalData).forEach(([key, value]) => {
          formData.append(key, value);
        });
      }

      const response = await this.axiosInstance.post<T>(url, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: options?.onUploadProgress,
      });

      return {
        data: response.data,
        error: null,
        status: response.status,
        success: true,
      };
    } catch (error) {
      return handleApiError(error as AxiosError);
    }
  }

  /**
   * Get the underlying axios instance for advanced usage.
   */
  getAxiosInstance(): AxiosInstance {
    return this.axiosInstance;
  }

  /**
   * Update base URL for the client.
   */
  setBaseURL(baseURL: string): void {
    this.axiosInstance.defaults.baseURL = baseURL;
  }

  /**
   * Set default timeout for requests.
   */
  setTimeout(timeout: number): void {
    this.axiosInstance.defaults.timeout = timeout;
  }

  /**
   * Add or update default headers.
   */
  setHeaders(headers: Record<string, string>): void {
    Object.assign(this.axiosInstance.defaults.headers.common, headers);
  }
}

// ============================================================================
// SINGLETON INSTANCE
// ============================================================================

/** Global HTTP client instance */
export const httpClient = new HttpClient();

// ============================================================================
// CONVENIENCE FUNCTIONS
// ============================================================================

/**
 * Create a new HTTP client with custom configuration.
 */
export function createHttpClient(config: Partial<HttpClientConfig>): HttpClient {
  return new HttpClient(config);
}

/**
 * Set authorization token for future requests.
 * This is called by AuthContext when user logs in.
 */
export function setAuthToken(token: string): void {
  httpClient.setHeaders({
    'Authorization': `Bearer ${token}`,
  });
}

/**
 * Clear authorization token from future requests.
 * This is called by AuthContext when user logs out.
 */
export function clearAuthToken(): void {
  const instance = httpClient.getAxiosInstance();
  delete instance.defaults.headers.common['Authorization'];
}

/**
 * Check if client is configured with authentication.
 */
export function hasAuthToken(): boolean {
  const token = getStoredToken();
  return !!(token && !isStoredTokenExpired());
}

// ============================================================================
// EVENT HANDLERS
// ============================================================================

// Listen for token expiration events from interceptors
if (typeof window !== 'undefined') {
  window.addEventListener('auth:token-expired', () => {
    clearAuthToken();
    clearStoredAuth();
  });
}

// ============================================================================
// EXPORTS
// ============================================================================

export default httpClient;
export { HttpClient };
export type { ApiResponse, ErrorResponse, HttpClientConfig };