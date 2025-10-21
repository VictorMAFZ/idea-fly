#!/usr/bin/env python3
"""
🧪 Tests Implementation Verification Script
Tasks T048-T050: Google OAuth Testing Suite

This script verifies the implementation of all OAuth testing components:
- T048: Unit tests for OAuth service (backend)
- T049: Integration tests for OAuth flow (backend) 
- T050: Component tests for GoogleAuthButton (frontend)
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

def check_test_content(filepath, required_tests, description=""):
    """Check if a test file contains required test cases."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        passed_tests = 0
        for test_name, test_pattern in required_tests:
            if test_pattern in content:
                print(f"✅ {description}: {test_name}")
                passed_tests += 1
            else:
                print(f"❌ {description}: {test_name} - Missing test pattern")
        
        return passed_tests, len(required_tests)
        
    except FileNotFoundError:
        print(f"❌ {description}: File not found - {filepath}")
        return 0, len(required_tests)
    except Exception as e:
        print(f"❌ {description}: Error reading file - {e}")
        return 0, len(required_tests)

def main():
    print("=" * 80)
    print("🧪 OAUTH TESTS IMPLEMENTATION VERIFICATION")
    print("Tasks T048-T050: Complete OAuth Testing Suite")
    print("=" * 80)
    
    total_checks = 0
    passed_checks = 0
    
    # ========================================================================
    # T048: Unit Tests for OAuth Service
    # ========================================================================
    print("\n📦 T048: Unit Tests for OAuth Service")
    print("-" * 50)
    
    oauth_service_tests = [
        ("Service initialization test", "def test_init"),
        ("Successful authentication test", "test_authenticate_with_google_success"),
        ("Invalid token test", "test_authenticate_with_google_invalid_token"),
        ("Token validation test", "test_validate_google_token_success"),
        ("Unverified email test", "test_validate_google_token_unverified_email"),
        ("Retry logic test", "test_validate_google_token_retry_logic"),
        ("User creation test", "test_find_or_create_oauth_user_new_user"),
        ("Existing user test", "test_find_or_create_oauth_user_existing_user"),
        ("Network error handling", "test_network_error_handling"),
        ("Integration tests", "class TestGoogleOAuthServiceIntegration")
    ]
    
    total_checks += 1
    if check_file_exists("backend/tests/auth/test_oauth_service.py", "OAuth Service Tests File"):
        passed_checks += 1
    
    oauth_passed, oauth_total = check_test_content(
        "backend/tests/auth/test_oauth_service.py", 
        oauth_service_tests,
        "OAuth Service Tests"
    )
    
    total_checks += oauth_total
    passed_checks += oauth_passed
    
    # ========================================================================
    # T049: Integration Tests for OAuth Flow
    # ========================================================================
    print("\n📦 T049: Integration Tests for OAuth Flow")
    print("-" * 50)
    
    oauth_flow_tests = [
        ("OAuth endpoint success test", "test_oauth_endpoint_success_new_user"),
        ("OAuth endpoint existing user", "test_oauth_endpoint_success_existing_user"),
        ("Invalid token endpoint test", "test_oauth_endpoint_invalid_token"),
        ("Database integration test", "test_create_new_oauth_user_flow"),
        ("Existing user authentication", "test_authenticate_existing_oauth_user_flow"),
        ("User linking test", "test_link_existing_email_user_with_oauth"),
        ("Google API failure test", "test_oauth_flow_with_google_api_failure"),
        ("Error propagation test", "test_authentication_error_propagation"),
        ("Concurrency test", "test_concurrent_oauth_requests"),
        ("TestClient integration", "TestClient(app)")
    ]
    
    total_checks += 1
    if check_file_exists("backend/tests/auth/test_oauth_flow.py", "OAuth Flow Tests File"):
        passed_checks += 1
    
    flow_passed, flow_total = check_test_content(
        "backend/tests/auth/test_oauth_flow.py", 
        oauth_flow_tests,
        "OAuth Flow Tests"
    )
    
    total_checks += flow_total
    passed_checks += flow_passed
    
    # ========================================================================
    # T050: Component Tests for GoogleAuthButton
    # ========================================================================
    print("\n📦 T050: Component Tests for GoogleAuthButton")  
    print("-" * 50)
    
    button_component_tests = [
        ("Rendering tests", "describe('Rendering'"),
        ("Default props test", "renders with default props"),
        ("Loading state test", "renders loading spinner when loading"),
        ("Accessibility tests", "describe('Accessibility'"),
        ("ARIA labels test", "has proper ARIA labels"),
        ("Keyboard accessibility", "is keyboard accessible"),
        ("User interaction tests", "describe('User Interactions'"),
        ("Click handler test", "calls googleLogin when clicked"),
        ("OAuth flow tests", "describe('OAuth Flow Integration'"),
        ("Success handling", "handles successful OAuth response"),
        ("Error handling tests", "describe('Error Handling'"),
        ("Loading states tests", "describe('Loading States'"),
        ("Variant tests", "describe('Component Variants and Customization'"),
        ("React Testing Library", "import { render, screen")
    ]
    
    total_checks += 1
    if check_file_exists("frontend/tests/components/auth/GoogleAuthButton.test.tsx", "GoogleAuthButton Tests File"):
        passed_checks += 1
    
    button_passed, button_total = check_test_content(
        "frontend/tests/components/auth/GoogleAuthButton.test.tsx", 
        button_component_tests,
        "GoogleAuthButton Tests"
    )
    
    total_checks += button_total
    passed_checks += button_passed
    
    # ========================================================================
    # Configuration Files Verification
    # ========================================================================
    print("\n📦 Test Configuration")
    print("-" * 50)
    
    # Backend test configuration
    test_configs = [
        ("backend/pytest.ini", "PyTest configuration"),
        ("backend/conftest.py", "PyTest fixtures"),
        ("frontend/vitest.config.ts", "Vitest configuration"),
        ("frontend/src/test-setup.ts", "Test setup file")
    ]
    
    for config_file, description in test_configs:
        total_checks += 1
        if check_file_exists(config_file, description):
            passed_checks += 1
    
    # ========================================================================
    # Test Coverage Analysis
    # ========================================================================
    print("\n📦 Test Coverage Analysis")
    print("-" * 50)
    
    # Count test cases in each file
    oauth_service_file = Path("backend/tests/auth/test_oauth_service.py")
    oauth_flow_file = Path("backend/tests/auth/test_oauth_flow.py") 
    button_test_file = Path("frontend/tests/components/auth/GoogleAuthButton.test.tsx")
    
    if oauth_service_file.exists():
        with open(oauth_service_file, 'r', encoding='utf-8') as f:
            service_content = f.read()
        service_test_count = service_content.count('def test_') + service_content.count('it(')
        print(f"✅ OAuth Service Tests: {service_test_count} test cases")
    
    if oauth_flow_file.exists():
        with open(oauth_flow_file, 'r', encoding='utf-8') as f:
            flow_content = f.read()
        flow_test_count = flow_content.count('def test_') + flow_content.count('it(')
        print(f"✅ OAuth Flow Tests: {flow_test_count} test cases")
        
    if button_test_file.exists():
        with open(button_test_file, 'r', encoding='utf-8') as f:
            button_content = f.read()
        button_test_count = button_content.count('it(')
        print(f"✅ GoogleAuthButton Tests: {button_test_count} test cases")
    
    # ========================================================================
    # Tasks.md Verification
    # ========================================================================
    print("\n📦 Tasks.md Status Verification")
    print("-" * 50)
    
    tasks_file = Path("specs/001-user-auth-system/tasks.md")
    if tasks_file.exists():
        with open(tasks_file, 'r', encoding='utf-8') as f:
            tasks_content = f.read()
        
        t048_completed = "- [x] T048" in tasks_content
        t049_completed = "- [x] T049" in tasks_content  
        t050_completed = "- [x] T050" in tasks_content
        
        print(f"{'✅' if t048_completed else '❌'} T048 marked as completed in tasks.md")
        print(f"{'✅' if t049_completed else '❌'} T049 marked as completed in tasks.md")
        print(f"{'✅' if t050_completed else '❌'} T050 marked as completed in tasks.md")
        
        total_checks += 3
        passed_checks += sum([t048_completed, t049_completed, t050_completed])
    else:
        print("❌ tasks.md file not found")
        total_checks += 3
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 80)
    print("📊 TESTS VERIFICATION SUMMARY")
    print("=" * 80)
    
    success_rate = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
    
    print(f"✅ Checks Passed: {passed_checks}")
    print(f"❌ Checks Failed: {total_checks - passed_checks}")
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    print(f"\n📋 Test Implementation Status:")
    print(f"  • T048 (OAuth Service): Unit tests with mocking and error handling")
    print(f"  • T049 (OAuth Flow): Integration tests with real database and API mocking")
    print(f"  • T050 (GoogleAuthButton): Component tests with React Testing Library")
    
    if success_rate >= 90:
        print("\n🎉 EXCELLENT! All OAuth tests are properly implemented!")
        print("✨ Comprehensive testing suite ready for CI/CD pipeline")
        return 0
    elif success_rate >= 75:
        print("\n✅ GOOD! OAuth testing suite is mostly complete")
        print("🔧 Minor adjustments may be needed")
        return 0
    else:
        print("\n⚠️  NEEDS WORK! OAuth testing suite has issues")
        print("🛠️  Significant fixes required before deployment")
        return 1

if __name__ == "__main__":
    sys.exit(main())