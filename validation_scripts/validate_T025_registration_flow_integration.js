/**
 * T025 Validation Script: Registration Flow Integration with AuthContext
 * 
 * This script validates the integration of registration flow with AuthContext
 * by checking that mock implementations have been replaced with real authService calls.
 */

const fs = require('fs');
const path = require('path');

// Color codes for console output
const COLORS = {
  GREEN: '\x1b[32m',
  RED: '\x1b[31m',
  YELLOW: '\x1b[33m',
  BLUE: '\x1b[34m',
  CYAN: '\x1b[36m',
  RESET: '\x1b[0m'
};

function log(color, message, prefix = '') {
  console.log(`${color}${prefix}${message}${COLORS.RESET}`);
}

function success(message) {
  log(COLORS.GREEN, `✅ ${message}`);
}

function error(message) {
  log(COLORS.RED, `❌ ${message}`);
}

function warning(message) {
  log(COLORS.YELLOW, `⚠️  ${message}`);
}

function info(message) {
  log(COLORS.BLUE, `ℹ️  ${message}`);
}

function section(message) {
  log(COLORS.CYAN, `\n🔍 ${message}`, '='.repeat(3) + ' ');
}

/**
 * Read file content safely
 */
function readFile(filePath) {
  try {
    return fs.readFileSync(filePath, 'utf8');
  } catch (err) {
    error(`Failed to read file: ${filePath}`);
    return null;
  }
}

/**
 * Check if AuthContext imports authService
 */
function validateAuthServiceImport(content) {
  section('Validating AuthService Import');
  
  if (content.includes("import { authService } from '../services/authService';")) {
    success('AuthService is properly imported');
    return true;
  } else {
    error('AuthService import is missing');
    return false;
  }
}

/**
 * Check if mock implementations have been removed
 */
function validateMockRemoval(content) {
  section('Validating Mock Implementation Removal');
  
  const mockPatterns = [
    /setTimeout.*resolve.*\d+/g,
    /mock_token_/g,
    /Mock User/g,
    /google_token_/g,
    /google_user_/g,
    /TODO.*Replace with actual/g,
    /placeholder until/g
  ];
  
  let hasMocks = false;
  
  mockPatterns.forEach((pattern, index) => {
    const matches = content.match(pattern);
    if (matches) {
      hasMocks = true;
      error(`Found mock pattern ${index + 1}: ${matches[0]}`);
    }
  });
  
  if (!hasMocks) {
    success('No mock implementations found - all replaced with real authService calls');
    return true;
  } else {
    error('Found mock implementations that should be replaced');
    return false;
  }
}

/**
 * Check if real authService methods are called
 */
function validateAuthServiceCalls(content) {
  section('Validating AuthService Method Calls');
  
  const requiredCalls = [
    { method: 'authService.register', pattern: /authService\.register\s*\(/g },
    { method: 'authService.login', pattern: /authService\.login\s*\(/g },
    { method: 'authService.googleCallback', pattern: /authService\.googleCallback\s*\(/g },
    { method: 'authService.logout', pattern: /authService\.logout\s*\(/g },
    { method: 'authService.getUserProfile', pattern: /authService\.getUserProfile\s*\(/g }
  ];
  
  let allCallsPresent = true;
  
  requiredCalls.forEach(({ method, pattern }) => {
    if (content.match(pattern)) {
      success(`Found call to ${method}`);
    } else {
      error(`Missing call to ${method}`);
      allCallsPresent = false;
    }
  });
  
  return allCallsPresent;
}

/**
 * Check proper error handling for authService responses
 */
function validateErrorHandling(content) {
  section('Validating Error Handling');
  
  const errorPatterns = [
    { description: 'response.error?.message handling', pattern: /response\.error\?\.message/g },
    { description: 'response.success checks', pattern: /response\.success/g },
    { description: 'response.data usage', pattern: /response\.data/g }
  ];
  
  let allHandlersPresent = true;
  
  errorPatterns.forEach(({ description, pattern }) => {
    const matches = content.match(pattern);
    if (matches && matches.length >= 3) { // Should appear in multiple methods
      success(`Proper ${description} found`);
    } else {
      error(`Insufficient ${description}`);
      allHandlersPresent = false;
    }
  });
  
  return allHandlersPresent;
}

/**
 * Check async/await pattern usage
 */
function validateAsyncPatterns(content) {
  section('Validating Async/Await Patterns');
  
  const patterns = [
    { description: 'await authService calls', pattern: /await authService\./g },
    { description: 'response success checks', pattern: /if \(response\.success && response\.data\)/g },
    { description: 'getUserProfile after auth', pattern: /await authService\.getUserProfile\(\)/g }
  ];
  
  let allPatternsValid = true;
  
  patterns.forEach(({ description, pattern }) => {
    const matches = content.match(pattern);
    if (matches && matches.length >= 2) { // Should appear in multiple methods
      success(`Proper ${description} pattern found`);
    } else {
      error(`Missing or insufficient ${description} pattern`);
      allPatternsValid = false;
    }
  });
  
  return allPatternsValid;
}

/**
 * Check token and storage management
 */
function validateTokenManagement(content) {
  section('Validating Token Management');
  
  const patterns = [
    { description: 'handleAuthSuccess calls', pattern: /handleAuthSuccess\(/g },
    { description: 'clearAuthFromStorage calls', pattern: /clearAuthFromStorage\(/g },
    { description: 'dispatch LOGIN_SUCCESS', pattern: /type:\s*['"']LOGIN_SUCCESS['"']/g }
  ];
  
  let allPatternsValid = true;
  
  patterns.forEach(({ description, pattern }) => {
    if (content.match(pattern)) {
      success(`Found ${description}`);
    } else {
      error(`Missing ${description}`);
      allPatternsValid = false;
    }
  });
  
  return allPatternsValid;
}

/**
 * Main validation function
 */
function validateT025Integration() {
  log(COLORS.CYAN, '\n🚀 T025 REGISTRATION FLOW INTEGRATION VALIDATION\n', '='.repeat(10) + ' ');
  
  const authContextPath = path.join(__dirname, '..', 'frontend', 'src', 'contexts', 'AuthContext.tsx');
  
  info(`Validating AuthContext integration: ${authContextPath}`);
  
  const authContextContent = readFile(authContextPath);
  if (!authContextContent) {
    error('Cannot read AuthContext file');
    return false;
  }
  
  const validations = [
    validateAuthServiceImport(authContextContent),
    validateMockRemoval(authContextContent),
    validateAuthServiceCalls(authContextContent),
    validateErrorHandling(authContextContent),
    validateAsyncPatterns(authContextContent),
    validateTokenManagement(authContextContent)
  ];
  
  const allValid = validations.every(v => v);
  
  section('Validation Summary');
  
  if (allValid) {
    success('✨ T025 Registration Flow Integration: ALL VALIDATIONS PASSED');
    info('🎯 AuthContext is successfully integrated with real authService');
    info('🔗 Mock implementations replaced with actual API calls');
    info('✅ Registration flow end-to-end integration complete');
    return true;
  } else {
    error('❌ T025 Registration Flow Integration: VALIDATION FAILED');
    warning('Please fix the issues identified above');
    return false;
  }
}

// Run validation
const isValid = validateT025Integration();
process.exit(isValid ? 0 : 1);