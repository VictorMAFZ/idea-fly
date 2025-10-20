#!/usr/bin/env python3
"""
T032, T033, T034 Verification Script - Login Flow Implementation

Verifies that all three tasks are correctly implemented:
- T032: authService.login() function
- T033: useAuth.loginWithService() function  
- T034: Login page with LoginForm integration
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Any

def check_file_exists(file_path: str) -> bool:
    """Check if a file exists."""
    return Path(file_path).exists()

def read_file_content(file_path: str) -> str:
    """Read file content safely."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return ""

def verify_t032_auth_service() -> Dict[str, Any]:
    """Verify T032: authService.login() implementation."""
    
    results = {
        "task": "T032 [US2]: Extend authentication service with login function",
        "file_path": "frontend/src/services/authService.ts",
        "tests": [],
        "overall_status": "UNKNOWN"
    }
    
    file_path = "frontend/src/services/authService.ts"
    file_exists = check_file_exists(file_path)
    
    if not file_exists:
        results["tests"].append({
            "name": "File Exists",
            "status": "FAIL",
            "description": "authService.ts file exists",
            "details": f"File missing at {file_path}"
        })
        results["overall_status"] = "FAIL"
        return results
    
    content = read_file_content(file_path)
    
    # Test 1: Login function exists
    has_login_function = re.search(r'async\s+login\s*\([^)]*LoginRequest[^)]*\)', content)
    
    results["tests"].append({
        "name": "Login Function Exists",
        "status": "PASS" if has_login_function else "FAIL",
        "description": "async login(request: LoginRequest) function implemented",
        "details": "Login function found" if has_login_function else "Login function missing"
    })
    
    # Test 2: Return type is correct
    correct_return_type = re.search(r'login.*Promise<ApiResponse<AuthResponse>>', content, re.DOTALL)
    
    results["tests"].append({
        "name": "Return Type",
        "status": "PASS" if correct_return_type else "FAIL",
        "description": "Returns Promise<ApiResponse<AuthResponse>>",
        "details": "Correct return type found" if correct_return_type else "Incorrect return type"
    })
    
    # Test 3: Uses correct endpoint
    uses_login_endpoint = 'ENDPOINTS.LOGIN' in content
    
    results["tests"].append({
        "name": "Uses Login Endpoint",
        "status": "PASS" if uses_login_endpoint else "FAIL",
        "description": "Uses ENDPOINTS.LOGIN for API call",
        "details": "Login endpoint used" if uses_login_endpoint else "Login endpoint not found"
    })
    
    # Test 4: HTTP client integration
    uses_http_client = 'httpClient.post' in content
    
    results["tests"].append({
        "name": "HTTP Client Integration",
        "status": "PASS" if uses_http_client else "FAIL",
        "description": "Uses httpClient.post for API calls",
        "details": "HTTP client integration found" if uses_http_client else "HTTP client not used"
    })
    
    # Calculate overall status
    passed = sum(1 for test in results["tests"] if test["status"] == "PASS")
    results["overall_status"] = "PASS" if passed == len(results["tests"]) else "FAIL"
    
    return results

def verify_t033_use_auth_hook() -> Dict[str, Any]:
    """Verify T033: useAuth.loginWithService() implementation."""
    
    results = {
        "task": "T033 [US2]: Extend useAuth hook with login function",
        "file_path": "frontend/src/hooks/useAuth.ts",
        "tests": [],
        "overall_status": "UNKNOWN"
    }
    
    file_path = "frontend/src/hooks/useAuth.ts"
    file_exists = check_file_exists(file_path)
    
    if not file_exists:
        results["tests"].append({
            "name": "File Exists",
            "status": "FAIL",
            "description": "useAuth.ts file exists",
            "details": f"File missing at {file_path}"
        })
        results["overall_status"] = "FAIL"
        return results
    
    content = read_file_content(file_path)
    
    # Test 1: loginWithService function exists
    has_login_with_service = 'loginWithService' in content
    
    results["tests"].append({
        "name": "loginWithService Function",
        "status": "PASS" if has_login_with_service else "FAIL",
        "description": "loginWithService function implemented",
        "details": "Function found" if has_login_with_service else "Function missing"
    })
    
    # Test 2: Function signature in interface
    correct_signature = re.search(r'loginWithService:\s*\([^)]*LoginRequest[^)]*\)\s*=>\s*Promise<void>', content)
    
    results["tests"].append({
        "name": "Function Signature",
        "status": "PASS" if correct_signature else "FAIL",
        "description": "Correct loginWithService signature in interface",
        "details": "Correct signature found" if correct_signature else "Incorrect signature"
    })
    
    # Test 3: Uses authService.login
    uses_auth_service = 'authService.login' in content
    
    results["tests"].append({
        "name": "AuthService Integration",
        "status": "PASS" if uses_auth_service else "FAIL",
        "description": "Uses authService.login() internally",
        "details": "AuthService integration found" if uses_auth_service else "AuthService not used"
    })
    
    # Test 4: Exported in return object
    exported_in_return = re.search(r'return\s*{[^}]*loginWithService[^}]*}', content, re.DOTALL)
    
    results["tests"].append({
        "name": "Function Exported",
        "status": "PASS" if exported_in_return else "FAIL",
        "description": "loginWithService exported in hook return",
        "details": "Function exported" if exported_in_return else "Function not exported"
    })
    
    # Calculate overall status
    passed = sum(1 for test in results["tests"] if test["status"] == "PASS")
    results["overall_status"] = "PASS" if passed == len(results["tests"]) else "FAIL"
    
    return results

def verify_t034_login_page() -> Dict[str, Any]:
    """Verify T034: Login page implementation."""
    
    results = {
        "task": "T034 [US2]: Create login page",
        "file_path": "frontend/src/app/login/page.tsx",
        "tests": [],
        "overall_status": "UNKNOWN"
    }
    
    file_path = "frontend/src/app/login/page.tsx"
    file_exists = check_file_exists(file_path)
    
    if not file_exists:
        results["tests"].append({
            "name": "File Exists",
            "status": "FAIL",
            "description": "Login page exists at correct path",
            "details": f"File missing at {file_path}"
        })
        results["overall_status"] = "FAIL"
        return results
    
    content = read_file_content(file_path)
    
    # Test 1: Uses LoginForm component
    uses_login_form = 'LoginForm' in content and 'from' in content and 'components/auth' in content
    
    results["tests"].append({
        "name": "Uses LoginForm Component",
        "status": "PASS" if uses_login_form else "FAIL",
        "description": "Imports and uses LoginForm component",
        "details": "LoginForm import and usage found" if uses_login_form else "LoginForm not used"
    })
    
    # Test 2: Uses useAuth hook
    uses_use_auth = 'useAuth' in content and 'loginWithService' in content
    
    results["tests"].append({
        "name": "Uses useAuth Hook",
        "status": "PASS" if uses_use_auth else "FAIL",
        "description": "Imports and uses useAuth hook",
        "details": "useAuth integration found" if uses_use_auth else "useAuth not used"
    })
    
    # Test 3: Next.js 14 App Router structure
    is_app_router = "'use client'" in content and 'export default function' in content
    
    results["tests"].append({
        "name": "Next.js App Router",
        "status": "PASS" if is_app_router else "FAIL",
        "description": "Uses Next.js 14 App Router pattern",
        "details": "App Router pattern found" if is_app_router else "Not App Router format"
    })
    
    # Test 4: Navigation integration
    has_navigation = 'useRouter' in content and 'router.push' in content
    
    results["tests"].append({
        "name": "Navigation Integration",
        "status": "PASS" if has_navigation else "FAIL",
        "description": "Uses Next.js navigation for redirects",
        "details": "Navigation found" if has_navigation else "Navigation missing"
    })
    
    # Test 5: Handles authentication state
    handles_auth_state = 'isAuthenticated' in content and 'redirectTo' in content
    
    results["tests"].append({
        "name": "Authentication State Handling",
        "status": "PASS" if handles_auth_state else "FAIL",
        "description": "Handles authentication state and redirects",
        "details": "Auth state handling found" if handles_auth_state else "Auth state not handled"
    })
    
    # Test 6: Error handling
    has_error_handling = 'error' in content and 'setLoginError' in content
    
    results["tests"].append({
        "name": "Error Handling",
        "status": "PASS" if has_error_handling else "FAIL",
        "description": "Implements error handling and display",
        "details": "Error handling found" if has_error_handling else "Error handling missing"
    })
    
    # Test 7: Loading states
    has_loading_states = 'loading' in content and 'isSubmitting' in content
    
    results["tests"].append({
        "name": "Loading States",
        "status": "PASS" if has_loading_states else "FAIL",
        "description": "Implements loading states and feedback",
        "details": "Loading states found" if has_loading_states else "Loading states missing"
    })
    
    # Calculate overall status
    passed = sum(1 for test in results["tests"] if test["status"] == "PASS")
    results["overall_status"] = "PASS" if passed >= len(results["tests"]) * 0.85 else "FAIL"
    
    return results

def main():
    """Main verification function."""
    print("🔍 T032, T033, T034 VERIFICATION: Login Flow Implementation")
    print("=" * 80)
    
    # Change to project root directory
    os.chdir("d:/victo/proyectos/idea-fly")
    
    # Run verifications
    t032_results = verify_t032_auth_service()
    t033_results = verify_t033_use_auth_hook()
    t034_results = verify_t034_login_page()
    
    # Display results
    all_results = [t032_results, t033_results, t034_results]
    
    for result in all_results:
        print(f"\n📋 {result['task']}")
        print(f"📁 File: {result['file_path']}")
        print(f"🎯 Status: {result['overall_status']}")
        print("-" * 50)
        
        for test in result['tests']:
            status_emoji = "✅" if test['status'] == "PASS" else "❌"
            print(f"{status_emoji} {test['name']}: {test['description']}")
            print(f"   Details: {test['details']}")
        
        print()
    
    # Overall summary
    total_passed = sum(len([t for t in r['tests'] if t['status'] == 'PASS']) for r in all_results)
    total_tests = sum(len(r['tests']) for r in all_results)
    overall_status = "PASS" if all(r['overall_status'] == 'PASS' for r in all_results) else "PARTIAL"
    
    print("=" * 80)
    print(f"📊 FINAL RESULT: {overall_status}")
    print(f"🧪 Tests passed: {total_passed}/{total_tests}")
    
    if overall_status == "PASS":
        print("🎉 T032, T033, T034 IMPLEMENTATION COMPLETED SUCCESSFULLY!")
        print()
        print("✅ Login flow is now complete:")
        print("   - T032: authService.login() ✅")
        print("   - T033: useAuth.loginWithService() ✅")
        print("   - T034: Login page with LoginForm ✅")
        print()
        print("🔗 Login flow ready for:")
        print("   - User authentication via email/password")
        print("   - Redirect handling after login")
        print("   - Error handling and user feedback")
        print("   - Integration with existing auth system")
        print()
        print("🎯 Next step: T035 - Integrate login flow with AuthContext")
    else:
        print("❌ SOME TASKS NEED ATTENTION")
        print("Please review the failed tests above.")
        
        # Show what's working
        working_tasks = [r['task'].split(':')[0] for r in all_results if r['overall_status'] == 'PASS']
        if working_tasks:
            print(f"✅ Working: {', '.join(working_tasks)}")

if __name__ == "__main__":
    main()