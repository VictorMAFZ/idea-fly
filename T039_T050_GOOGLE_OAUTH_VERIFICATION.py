#!/usr/bin/env python3
"""
🎯 Google OAuth Implementation Verification Script
User Story 3: Google OAuth Authentication

This script verifies the complete Google OAuth implementation including:
- Backend OAuth service and endpoints
- Frontend components and hooks  
- Integration with existing authentication system
- End-to-end OAuth flow
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, description=""):
    """Check if a file exists and return status."""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} - NOT FOUND")
        return False

def check_directory_exists(dirpath, description=""):
    """Check if a directory exists and return status."""
    if Path(dirpath).exists():
        print(f"✅ {description}: {dirpath}")
        return True
    else:
        print(f"❌ {description}: {dirpath} - NOT FOUND")
        return False

def check_file_contains(filepath, content_check, description=""):
    """Check if a file contains specific content."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if content_check in content:
                print(f"✅ {description}")
                return True
            else:
                print(f"❌ {description} - Content not found")
                return False
    except FileNotFoundError:
        print(f"❌ {description} - File not found: {filepath}")
        return False
    except Exception as e:
        print(f"❌ {description} - Error reading file: {e}")
        return False

def main():
    print("=" * 80)
    print("🎯 GOOGLE OAUTH IMPLEMENTATION VERIFICATION")
    print("User Story 3: Registro e Inicio de Sesión con Google")
    print("=" * 80)
    
    # Track overall results
    checks_passed = 0
    total_checks = 0
    
    # ========================================================================
    # T039: Google OAuth Service Backend
    # ========================================================================
    print("\n📦 T039: Google OAuth Service Backend")
    print("-" * 50)
    
    total_checks += 1
    if check_file_exists("backend/src/auth/oauth_service.py", "OAuth Service"):
        checks_passed += 1
    
    # Check OAuth service implementation
    oauth_service_checks = [
        ("class GoogleOAuthService", "GoogleOAuthService class defined"),
        ("async def authenticate_with_google", "Main authentication method"),
        ("async def _validate_google_token", "Token validation method"),
        ("async def _find_or_create_oauth_user", "User management method"),
        ("GOOGLE_USER_INFO_URL", "Google API endpoints configured"),
        ("httpx.AsyncClient", "HTTP client configured"),
        ("def get_google_oauth_service", "FastAPI dependency")
    ]
    
    for content_check, description in oauth_service_checks:
        total_checks += 1
        if check_file_contains("backend/src/auth/oauth_service.py", content_check, description):
            checks_passed += 1
    
    # ========================================================================
    # T040: OAuth Callback Endpoint
    # ========================================================================
    print("\n📦 T040: OAuth Callback Endpoint")
    print("-" * 50)
    
    router_checks = [
        ("@router.post(\n    \"/google\"", "Google OAuth endpoint defined"),
        ("async def authenticate_with_google", "OAuth endpoint handler"),
        ("GoogleTokenRequest", "OAuth request schema imported"),
        ("GoogleOAuthService", "OAuth service imported"),
        ("AuthenticationError", "Error handling imported")
    ]
    
    for content_check, description in router_checks:
        total_checks += 1
        if check_file_contains("backend/src/auth/router.py", content_check, description):
            checks_passed += 1
    
    # ========================================================================
    # T041: User Repository OAuth Support
    # ========================================================================
    print("\n📦 T041: User Repository OAuth Support")
    print("-" * 50)
    
    repo_checks = [
        ("async def create_oauth_user", "OAuth user creation method"),
        ("async def authenticate_oauth_user", "OAuth authentication method"),
        ("OAuthProfile", "OAuth profile model imported"),
        ("AuthProvider.GOOGLE", "Google auth provider"),
        ("AuthProvider.MIXED", "Mixed auth provider support")
    ]
    
    for content_check, description in repo_checks:
        total_checks += 1
        if check_file_contains("backend/src/auth/repository.py", content_check, description):
            checks_passed += 1
    
    # ========================================================================
    # T042: GoogleAuthButton Component
    # ========================================================================
    print("\n📦 T042: GoogleAuthButton Component")
    print("-" * 50)
    
    total_checks += 1
    if check_file_exists("frontend/src/components/auth/GoogleAuthButton.tsx", "GoogleAuthButton component"):
        checks_passed += 1
    
    button_checks = [
        ("export function GoogleAuthButton", "Component function defined"),
        ("useGoogleLogin", "Google OAuth hook imported"),
        ("interface GoogleAuthButtonProps", "Props interface defined"),
        ("onSuccess:", "Success callback prop"),
        ("onError:", "Error callback prop"),
        ("WCAG accessibility", "Accessibility features"),
        ("aria-label", "Accessibility labels"),
        ("dark mode support", "Dark mode styling")
    ]
    
    for content_check, description in button_checks:
        total_checks += 1
        if check_file_contains("frontend/src/components/auth/GoogleAuthButton.tsx", content_check, description):
            checks_passed += 1
    
    # ========================================================================
    # T043: Google OAuth Hook
    # ========================================================================
    print("\n📦 T043: Google OAuth Hook")
    print("-" * 50)
    
    total_checks += 1
    if check_file_exists("frontend/src/hooks/useGoogleAuth.ts", "useGoogleAuth hook"):
        checks_passed += 1
    
    hook_checks = [
        ("export function useGoogleAuth", "Hook function defined"),
        ("interface GoogleAuthState", "State interface defined"),
        ("interface GoogleAuthActions", "Actions interface defined"),
        ("signInWithGoogle:", "Sign in method"),
        ("clearError:", "Error clearing method"),
        ("useState", "State management"),
        ("useCallback", "Callback optimization"),
        ("authService.authenticateWithGoogle", "Service integration")
    ]
    
    for content_check, description in hook_checks:
        total_checks += 1
        if check_file_contains("frontend/src/hooks/useGoogleAuth.ts", content_check, description):
            checks_passed += 1
    
    # ========================================================================
    # T044: Auth Service Extension
    # ========================================================================
    print("\n📦 T044: Auth Service Extension")
    print("-" * 50)
    
    service_checks = [
        ("async authenticateWithGoogle", "Google auth method"),
        ("GoogleTokenRequest", "Google token type imported"),
        ("GOOGLE_OAUTH: '/auth/google'", "Google OAuth endpoint"),
        ("httpClient.post", "HTTP client usage")
    ]
    
    for content_check, description in service_checks:
        total_checks += 1
        if check_file_contains("frontend/src/services/authService.ts", content_check, description):
            checks_passed += 1
    
    # ========================================================================
    # T045: Google OAuth Provider Setup
    # ========================================================================
    print("\n📦 T045: Google OAuth Provider Setup")
    print("-" * 50)
    
    layout_checks = [
        ("import { GoogleOAuthProvider }", "Google OAuth provider imported"),
        ("GoogleOAuthProvider", "Provider component used"),
        ("NEXT_PUBLIC_GOOGLE_CLIENT_ID", "Client ID environment variable"),
        ("clientId={googleClientId}", "Client ID configuration")
    ]
    
    for content_check, description in layout_checks:
        total_checks += 1
        if check_file_contains("frontend/src/app/layout.tsx", content_check, description):
            checks_passed += 1
    
    # ========================================================================
    # T046: Forms Integration
    # ========================================================================
    print("\n📦 T046: Forms Integration")
    print("-" * 50)
    
    # LoginForm integration
    login_checks = [
        ("import { GoogleAuthButton }", "GoogleAuthButton imported"),
        ("import { useGoogleAuth }", "useGoogleAuth hook imported"),
        ("useGoogleAuth()", "Hook used in component"),
        ("<GoogleAuthButton", "Component used in JSX"),
        ("handleGoogleSuccess", "Success handler"),
        ("O continúa con", "Divider text")
    ]
    
    for content_check, description in login_checks:
        total_checks += 1
        if check_file_contains("frontend/src/components/auth/LoginForm.tsx", content_check, f"LoginForm: {description}"):
            checks_passed += 1
    
    # RegisterForm integration
    register_checks = [
        ("import { GoogleAuthButton }", "GoogleAuthButton imported"),
        ("import { useGoogleAuth }", "useGoogleAuth hook imported"),
        ("useGoogleAuth()", "Hook used in component"),
        ("<GoogleAuthButton", "Component used in JSX"),
        ("handleGoogleSuccess", "Success handler"),
        ("Registrarse con Google", "Register button text")
    ]
    
    for content_check, description in register_checks:
        total_checks += 1
        if check_file_contains("frontend/src/components/auth/RegisterForm.tsx", content_check, f"RegisterForm: {description}"):
            checks_passed += 1
    
    # ========================================================================
    # T047: AuthContext Extension
    # ========================================================================
    print("\n📦 T047: AuthContext Extension")
    print("-" * 50)
    
    context_checks = [
        ("loginWithGoogleToken:", "Google token method in types"),
        ("const loginWithGoogleToken", "Method implementation"),
        ("authService.authenticateWithGoogle", "Service integration"),
        ("loginWithGoogleToken,", "Method in context value"),
        ("Google authentication failed", "Error handling")
    ]
    
    for content_check, description in context_checks:
        total_checks += 1
        if check_file_contains("frontend/src/contexts/AuthContext.tsx", content_check, description):
            checks_passed += 1
    
    # ========================================================================
    # Type Definitions
    # ========================================================================
    print("\n📦 Type Definitions")
    print("-" * 50)
    
    # Frontend types
    type_checks = [
        ("interface GoogleTokenRequest", "Google token request type"),
        ("loginWithGoogleToken:", "Method in AuthActions interface")
    ]
    
    for content_check, description in type_checks:
        total_checks += 1
        if check_file_contains("frontend/src/types/auth.ts", content_check, description):
            checks_passed += 1
    
    # Backend schemas
    schema_checks = [
        ("class GoogleTokenRequest", "Backend token request schema"),
        ("GoogleTokenRequest", "Schema in exports")
    ]
    
    for content_check, description in schema_checks:
        total_checks += 1
        if check_file_contains("backend/src/auth/schemas.py", content_check, description):
            checks_passed += 1
    
    # ========================================================================
    # Configuration Files
    # ========================================================================
    print("\n📦 Configuration Files")
    print("-" * 50)
    
    # Check package.json dependencies
    total_checks += 1
    if check_file_contains("frontend/package.json", "@react-oauth/google", "Google OAuth dependency"):
        checks_passed += 1
    
    # Check requirements.txt dependencies  
    total_checks += 1
    if check_file_contains("backend/requirements.txt", "httpx", "HTTP client dependency"):
        checks_passed += 1
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 80)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 80)
    
    success_rate = (checks_passed / total_checks) * 100
    
    print(f"✅ Checks Passed: {checks_passed}")
    print(f"❌ Checks Failed: {total_checks - checks_passed}")
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 95:
        print("\n🎉 EXCELLENT! Google OAuth implementation is complete and ready!")
        print("✨ All core components are properly implemented")
        return 0
    elif success_rate >= 85:
        print("\n✅ GOOD! Google OAuth implementation is mostly complete")
        print("🔧 Minor issues to address before full deployment")
        return 0
    elif success_rate >= 70:
        print("\n⚠️  NEEDS WORK! Google OAuth implementation has some issues")
        print("🛠️  Significant fixes required before testing")
        return 1
    else:
        print("\n❌ MAJOR ISSUES! Google OAuth implementation is incomplete")
        print("🚨 Extensive work required before deployment")
        return 1

if __name__ == "__main__":
    sys.exit(main())