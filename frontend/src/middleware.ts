/**
 * Next.js Middleware for Route Protection in IdeaFly Application.
 * 
 * This middleware automatically protects routes based on authentication status.
 * It runs on Edge Runtime for optimal performance and handles:
 * - Route-based authentication checks
 * - Automatic redirects for unauthenticated users
 * - Token validation without full page loads
 * - Public route exceptions
 */

import { NextRequest, NextResponse } from 'next/server';

// ============================================================================
// CONFIGURATION
// ============================================================================

/** Routes that require authentication */
const PROTECTED_ROUTES = [
  '/dashboard',
  '/ideas',
  '/profile',
  '/settings',
  '/admin'
] as const;

/** Routes that should redirect authenticated users (auth pages) */
const AUTH_ROUTES = [
  '/login',
  '/register'
] as const;

/** Public routes that don't require authentication */
const PUBLIC_ROUTES = [
  '/',
  '/about',
  '/contact',
  '/privacy',
  '/terms'
] as const;

/** Default redirect paths */
const DEFAULT_LOGIN_REDIRECT = '/login';
const DEFAULT_AUTH_REDIRECT = '/dashboard';

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Check if the given path matches any of the provided route patterns.
 * Supports exact matches and wildcard patterns.
 */
function matchesRoutes(pathname: string, routes: readonly string[]): boolean {
  return routes.some(route => {
    // Exact match
    if (route === pathname) return true;
    
    // Wildcard match (route ends with *)
    if (route.endsWith('*')) {
      const baseRoute = route.slice(0, -1);
      return pathname.startsWith(baseRoute);
    }
    
    // Directory match (check if pathname starts with route)
    return pathname.startsWith(route + '/') || pathname === route;
  });
}

/**
 * Extract JWT token from request cookies or headers.
 */
function getTokenFromRequest(request: NextRequest): string | null {
  // Try cookies first (most secure for web apps)
  const tokenFromCookie = request.cookies.get('ideafly_auth_token')?.value;
  if (tokenFromCookie) return tokenFromCookie;
  
  // Fallback to Authorization header
  const authHeader = request.headers.get('authorization');
  if (authHeader?.startsWith('Bearer ')) {
    return authHeader.substring(7);
  }
  
  return null;
}

/**
 * Validate JWT token format (basic validation).
 * Note: Full validation should be done on the server side.
 */
function isValidTokenFormat(token: string): boolean {
  if (!token) return false;
  
  // JWT should have 3 parts separated by dots
  const parts = token.split('.');
  if (parts.length !== 3) return false;
  
  // Each part should be base64-encoded (basic check)
  try {
    parts.forEach(part => {
      if (!part) throw new Error('Empty part');
      // Basic base64 character check
      if (!/^[A-Za-z0-9_-]+$/.test(part)) throw new Error('Invalid base64');
    });
    return true;
  } catch {
    return false;
  }
}

/**
 * Check if token is expired (client-side check).
 * Note: This is just a basic check. Server should always validate.
 */
function isTokenExpired(token: string): boolean {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const currentTime = Math.floor(Date.now() / 1000);
    return payload.exp < currentTime;
  } catch {
    // If we can't decode, consider it expired
    return true;
  }
}

/**
 * Check if user is authenticated based on token.
 */
function isAuthenticated(request: NextRequest): boolean {
  const token = getTokenFromRequest(request);
  
  if (!token) return false;
  if (!isValidTokenFormat(token)) return false;
  if (isTokenExpired(token)) return false;
  
  return true;
}

/**
 * Create redirect response with proper URL handling.
 */
function createRedirect(request: NextRequest, path: string): NextResponse {
  const url = new URL(path, request.url);
  
  // Add return URL for login redirects
  if (path === DEFAULT_LOGIN_REDIRECT) {
    url.searchParams.set('returnTo', request.nextUrl.pathname);
  }
  
  return NextResponse.redirect(url);
}

// ============================================================================
// MIDDLEWARE FUNCTION
// ============================================================================

export function middleware(request: NextRequest): NextResponse {
  const { pathname } = request.nextUrl;
  const authenticated = isAuthenticated(request);
  
  // ============================================================================
  // PROTECTED ROUTES - Require Authentication
  // ============================================================================
  
  if (matchesRoutes(pathname, PROTECTED_ROUTES)) {
    if (!authenticated) {
      console.log(`🔒 Redirecting unauthenticated user from ${pathname} to login`);
      return createRedirect(request, DEFAULT_LOGIN_REDIRECT);
    }
    
    console.log(`✅ Allowing authenticated user access to ${pathname}`);
    return NextResponse.next();
  }
  
  // ============================================================================
  // AUTH ROUTES - Redirect if Already Authenticated
  // ============================================================================
  
  if (matchesRoutes(pathname, AUTH_ROUTES)) {
    if (authenticated) {
      console.log(`🔄 Redirecting authenticated user from ${pathname} to dashboard`);
      return createRedirect(request, DEFAULT_AUTH_REDIRECT);
    }
    
    console.log(`🔓 Allowing unauthenticated user access to ${pathname}`);
    return NextResponse.next();
  }
  
  // ============================================================================
  // PUBLIC ROUTES - Always Allow
  // ============================================================================
  
  if (matchesRoutes(pathname, PUBLIC_ROUTES)) {
    console.log(`🌐 Allowing access to public route ${pathname}`);
    return NextResponse.next();
  }
  
  // ============================================================================
  // DEFAULT BEHAVIOR - Allow but Log
  // ============================================================================
  
  console.log(`❓ Unknown route ${pathname}, allowing access`);
  return NextResponse.next();
}

// ============================================================================
// MIDDLEWARE CONFIGURATION
// ============================================================================

/**
 * Middleware configuration for Next.js.
 * Specifies which paths this middleware should run on.
 */
export const config = {
  /*
   * Match all request paths except:
   * - api routes (handled separately)
   * - _next/static (static files)
   * - _next/image (image optimization)
   * - favicon.ico (favicon)
   * - public folder files
   */
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};

// ============================================================================
// EXPORTS
// ============================================================================

export default middleware;

/**
 * Utility functions for testing and external use.
 */
export {
  matchesRoutes,
  getTokenFromRequest,
  isValidTokenFormat,
  isTokenExpired,
  isAuthenticated,
  PROTECTED_ROUTES,
  AUTH_ROUTES,
  PUBLIC_ROUTES
};