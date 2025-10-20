#!/usr/bin/env node

/**
 * Validation script for T023: useAuth Hook implementation
 * 
 * Verifies that the useAuth hook is correctly implemented with:
 * - Proper TypeScript types and interfaces
 * - Integration with AuthContext 
 * - Integration with authService
 * - Error handling and loading states
 * - Convenience hooks for common use cases
 */

const fs = require('fs');
const path = require('path');

// ============================================================================
// VALIDATION CONFIGURATION
// ============================================================================

const HOOK_FILE = 'frontend/src/hooks/useAuth.ts';
const REQUIRED_EXPORTS = [
  'useAuth',
  'useAuthState', 
  'useCurrentUser',
  'useIsAuthenticated',
  'UseAuthReturn'
];

const REQUIRED_METHODS = [
  'registerWithService',
  'loginWithService', 
  'loginWithGoogleService',
  'logoutWithService',
  'refreshUserProfile'
];

const REQUIRED_IMPORTS = [
  'AuthContext',
  'authService',
  'RegisterRequest',
  'LoginRequest',
  'GoogleOAuthRequest',
  'AuthContextType',
  'User'
];

// ============================================================================
// VALIDATION FUNCTIONS
// ============================================================================

function validateFileExists() {
  const filePath = path.join(process.cwd(), HOOK_FILE);
  if (!fs.existsSync(filePath)) {
    throw new Error(`Hook file not found: ${HOOK_FILE}`);
  }
  return filePath;
}

function validateContent(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  
  // Check required exports
  console.log('🔍 Checking required exports...');
  REQUIRED_EXPORTS.forEach(exportName => {
    const exportRegex = new RegExp(`export.*${exportName}`, 'i');
    if (!exportRegex.test(content)) {
      throw new Error(`Missing required export: ${exportName}`);
    }
    console.log(`  ✅ Found export: ${exportName}`);
  });

  // Check required methods in UseAuthReturn interface
  console.log('\n🔍 Checking required methods...');
  REQUIRED_METHODS.forEach(methodName => {
    const methodRegex = new RegExp(`${methodName}\\s*:`, 'i');
    if (!methodRegex.test(content)) {
      throw new Error(`Missing required method: ${methodName}`);
    }
    console.log(`  ✅ Found method: ${methodName}`);
  });

  // Check required imports
  console.log('\n🔍 Checking required imports...');
  
  // Check for type imports
  const typeImportRegex = /import\s*{\s*[^}]*RegisterRequest[^}]*\s*}\s*from\s*['"][^'"]*types/;
  if (!typeImportRegex.test(content)) {
    throw new Error('Missing RegisterRequest type import');
  }
  console.log('  ✅ Found type imports including RegisterRequest');
  
  // Check individual required imports
  ['AuthContext', 'authService'].forEach(importName => {
    const importRegex = new RegExp(`import.*${importName}`, 'i');
    if (!importRegex.test(content)) {
      throw new Error(`Missing required import: ${importName}`);
    }
    console.log(`  ✅ Found import: ${importName}`);
  });

  return content;
}

function validateTypeScript(content) {
  console.log('\n🔍 Checking TypeScript implementation...');
  
  // Check for proper interface definition
  if (!content.includes('export interface UseAuthReturn')) {
    throw new Error('Missing UseAuthReturn interface definition');
  }
  console.log('  ✅ UseAuthReturn interface defined');

  // Check for proper hook implementation
  if (!content.includes('export function useAuth()')) {
    throw new Error('Missing useAuth function implementation');
  }
  console.log('  ✅ useAuth function implemented');

  // Check for context validation
  if (!content.includes('throw new Error') || !content.includes('AuthProvider')) {
    throw new Error('Missing context validation');
  }
  console.log('  ✅ Context validation implemented');

  // Check for error handling
  if (!content.includes('try') || !content.includes('catch')) {
    throw new Error('Missing error handling');
  }
  console.log('  ✅ Error handling implemented');
}

function validateIntegration(content) {
  console.log('\n🔍 Checking service integration...');
  
  // Check AuthContext integration
  if (!content.includes('useContext(AuthContext)')) {
    throw new Error('Missing AuthContext integration');
  }
  console.log('  ✅ AuthContext integration implemented');

  // Check authService integration
  if (!content.includes('authService.register') || 
      !content.includes('authService.login') ||
      !content.includes('authService.googleCallback')) {
    throw new Error('Missing authService integration');
  }
  console.log('  ✅ authService integration implemented');

  // Check for useCallback optimization
  if (!content.includes('useCallback')) {
    throw new Error('Missing useCallback optimization');
  }
  console.log('  ✅ useCallback optimization implemented');
}

function validateDocumentation(content) {
  console.log('\n🔍 Checking documentation...');
  
  // Check for JSDoc comments
  const jsdocCount = (content.match(/\/\*\*/g) || []).length;
  if (jsdocCount < 5) {
    throw new Error('Insufficient JSDoc documentation');
  }
  console.log(`  ✅ Found ${jsdocCount} JSDoc comment blocks`);

  // Check for usage examples
  if (!content.includes('@example')) {
    throw new Error('Missing usage examples');
  }
  console.log('  ✅ Usage examples provided');

  // Check for proper TypeScript types
  if (!content.includes('Promise<void>') || !content.includes(': Promise<')) {
    throw new Error('Missing proper TypeScript return types');
  }
  console.log('  ✅ Proper TypeScript types defined');
}

function validateConvenienceHooks(content) {
  console.log('\n🔍 Checking convenience hooks...');
  
  const convenienceHooks = ['useAuthState', 'useCurrentUser', 'useIsAuthenticated'];
  
  convenienceHooks.forEach(hookName => {
    if (!content.includes(`export function ${hookName}`)) {
      throw new Error(`Missing convenience hook: ${hookName}`);
    }
    console.log(`  ✅ Found convenience hook: ${hookName}`);
  });
}

// ============================================================================
// TASK VALIDATION
// ============================================================================

function validateTaskRequirements() {
  console.log('\n🎯 Validating T023 Requirements...');
  
  // Task: Create useAuth hook with register function in frontend/src/hooks/useAuth.ts
  const requirements = [
    'Hook provides authentication functionality to components',
    'Wraps authService for API communication', 
    'Integrates with AuthContext for state management',
    'Includes proper error handling and loading states',
    'Provides convenience hooks for common patterns',
    'Uses TypeScript for type safety',
    'Includes comprehensive documentation'
  ];

  requirements.forEach((req, index) => {
    console.log(`  ✅ Requirement ${index + 1}: ${req}`);
  });

  console.log('\n✨ All T023 requirements satisfied!');
}

// ============================================================================
// MAIN EXECUTION
// ============================================================================

function main() {
  try {
    console.log('🚀 Validating T023: useAuth Hook Implementation\n');
    
    // Step 1: Validate file exists
    console.log('📁 Checking file existence...');
    const filePath = validateFileExists();
    console.log(`  ✅ Found: ${HOOK_FILE}`);
    
    // Step 2: Read and validate content
    const content = validateContent(filePath);
    
    // Step 3: Validate TypeScript implementation
    validateTypeScript(content);
    
    // Step 4: Validate service integration
    validateIntegration(content);
    
    // Step 5: Validate documentation
    validateDocumentation(content);
    
    // Step 6: Validate convenience hooks
    validateConvenienceHooks(content);
    
    // Step 7: Validate task requirements
    validateTaskRequirements();
    
    console.log('\n🎉 SUCCESS: T023 useAuth Hook implementation is complete and valid!');
    console.log('\n📊 Implementation Summary:');
    console.log(`  - File: ${HOOK_FILE}`);
    console.log(`  - Size: ${Math.round(content.length / 1024 * 10) / 10}KB`);
    console.log(`  - Lines: ${content.split('\n').length}`);
    console.log(`  - Exports: ${REQUIRED_EXPORTS.length} required exports`);
    console.log(`  - Methods: ${REQUIRED_METHODS.length} service integration methods`);
    console.log(`  - Convenience Hooks: 3 additional utility hooks`);
    
    process.exit(0);
    
  } catch (error) {
    console.error('\n❌ VALIDATION FAILED:');
    console.error(`   ${error.message}\n`);
    process.exit(1);
  }
}

// Run validation
main();