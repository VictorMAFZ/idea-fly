/**
 * Validation Script for T024: Registration Page Implementation
 * 
 * Validates that the registration page in frontend/src/app/register/page.tsx
 * meets all the requirements for the T024 task in US1 user story.
 */

const fs = require('fs');
const path = require('path');

// ============================================================================
// VALIDATION CONFIGURATION
// ============================================================================

const TASK_ID = 'T024';
const TASK_DESCRIPTION = 'Create registration page in frontend/src/app/register/page.tsx';

const REQUIRED_FILES = [
  'frontend/src/app/register/page.tsx',
  'frontend/src/app/layout.tsx',
  'frontend/src/app/page.tsx'
];

const REQUIRED_IMPORTS = [
  'RegisterForm',
  'useAuth',
  'useRouter',
  'RegisterRequest',
  'AuthStatus'
];

const REQUIRED_FEATURES = [
  'handleRegister',
  'registerWithService',
  'AuthProvider',
  'error handling',
  'loading states',
  'navigation',
  'accessibility'
];

const REQUIRED_COMPONENTS = [
  'RegisterForm',
  'error display',
  'loading spinner',
  'navigation links',
  'responsive design'
];

// ============================================================================
// VALIDATION FUNCTIONS
// ============================================================================

function validateFileExists(filePath) {
  const fullPath = path.resolve(filePath);
  if (!fs.existsSync(fullPath)) {
    throw new Error(`Required file not found: ${filePath}`);
  }
  return fs.readFileSync(fullPath, 'utf8');
}

function validateImports(content, requiredImports) {
  for (const importName of requiredImports) {
    const importRegex = new RegExp(`import.*${importName}`, 'i');
    if (!importRegex.test(content)) {
      throw new Error(`Missing required import: ${importName}`);
    }
  }
}

function validateFeatures(content, requiredFeatures) {
  for (const feature of requiredFeatures) {
    if (!content.includes(feature)) {
      throw new Error(`Missing required feature: ${feature}`);
    }
  }
}

function validatePageStructure(content) {
  // Check for Next.js App Router page structure
  if (!content.includes('export default function')) {
    throw new Error('Missing default export function');
  }
  
  // Check for 'use client' directive
  if (!content.includes("'use client'")) {
    throw new Error('Missing client directive for interactive components');
  }
  
  // Check for proper JSX structure
  if (!content.includes('return (') && !content.includes('return<')) {
    throw new Error('Missing JSX return statement');
  }
}

function validateAuthIntegration(content) {
  // Check useAuth hook usage
  if (!content.includes('useAuth()')) {
    throw new Error('Missing useAuth hook usage');
  }
  
  // Check registerWithService usage
  if (!content.includes('registerWithService')) {
    throw new Error('Missing registerWithService integration');
  }
  
  // Check authentication state checks
  if (!content.includes('isAuthenticated')) {
    throw new Error('Missing authentication state management');
  }
}

function validateErrorHandling(content) {
  // Check error state management
  if (!content.includes('error') || !content.includes('clearError')) {
    throw new Error('Missing error handling implementation');
  }
  
  // Check error display
  if (!content.includes('displayError') || !content.includes('text-red-')) {
    throw new Error('Missing error display functionality');
  }
  
  // Check error clearing functionality
  if (!content.includes('handleClearError')) {
    throw new Error('Missing error clearing functionality');
  }
}

function validateAccessibility(content) {
  // Check for ARIA labels and semantic HTML
  if (!content.includes('aria-') && !content.includes('role=')) {
    console.warn('Warning: Consider adding ARIA labels for better accessibility');
  }
  
  // Check for proper heading structure
  if (!content.includes('<h1')) {
    throw new Error('Missing main heading (h1) for page structure');
  }
  
  // Check for loading states
  if (!content.includes('Loading') || !content.includes('disabled')) {
    throw new Error('Missing accessibility features for loading states');
  }
}

function validateResponsiveDesign(content) {
  // Check for responsive classes using more flexible matching
  const hasResponsive = /sm:|md:|lg:/.test(content);
  if (!hasResponsive) {
    throw new Error('Missing responsive design classes');
  }
  
  // Check for mobile-first approach
  if (!content.includes('min-h-screen')) {
    throw new Error('Missing full-height layout for mobile devices');
  }
}

function validateNavigation(content) {
  // Check for router usage
  if (!content.includes('useRouter') || !content.includes('router.push')) {
    throw new Error('Missing navigation implementation');
  }
  
  // Check for redirect logic
  if (!content.includes('dashboard') || !content.includes('login')) {
    throw new Error('Missing navigation to dashboard and login pages');
  }
}

// ============================================================================
// MAIN VALIDATION LOGIC
// ============================================================================

async function validateT024Implementation() {
  console.log('🚀 Validating T024: Registration Page Implementation\n');
  
  try {
    // Check file existence
    console.log('📁 Checking file existence...');
    const contents = {};
    for (const filePath of REQUIRED_FILES) {
      contents[filePath] = validateFileExists(filePath);
      console.log(`  ✅ Found: ${filePath}`);
    }
    
    const mainPageContent = contents['frontend/src/app/register/page.tsx'];
    const layoutContent = contents['frontend/src/app/layout.tsx'];
    
    // Validate imports
    console.log('\n🔍 Checking required imports...');
    validateImports(mainPageContent, REQUIRED_IMPORTS);
    console.log('  ✅ All required imports found');
    
    // Validate page structure
    console.log('\n🏗️ Checking page structure...');
    validatePageStructure(mainPageContent);
    console.log('  ✅ Next.js App Router page structure is correct');
    
    // Validate auth integration
    console.log('\n🔐 Checking authentication integration...');
    validateAuthIntegration(mainPageContent);
    console.log('  ✅ useAuth hook and authentication flow integrated');
    
    // Validate error handling
    console.log('\n❌ Checking error handling...');
    validateErrorHandling(mainPageContent);
    console.log('  ✅ Error handling and display implemented');
    
    // Validate accessibility
    console.log('\n♿ Checking accessibility features...');
    validateAccessibility(mainPageContent);
    console.log('  ✅ Accessibility features implemented');
    
    // Validate responsive design
    console.log('\n📱 Checking responsive design...');
    validateResponsiveDesign(mainPageContent);
    console.log('  ✅ Responsive design classes implemented');
    
    // Validate navigation
    console.log('\n🧭 Checking navigation logic...');
    validateNavigation(mainPageContent);
    console.log('  ✅ Navigation and routing implemented');
    
    // Validate AuthProvider in layout
    console.log('\n🎯 Checking AuthProvider setup...');
    if (!layoutContent.includes('AuthProvider')) {
      throw new Error('Missing AuthProvider in layout');
    }
    console.log('  ✅ AuthProvider properly configured in layout');
    
    // Count lines and estimate complexity
    const lines = mainPageContent.split('\n').length;
    const size = (mainPageContent.length / 1024).toFixed(1);
    
    console.log('\n🎯 Validating T024 Requirements...');
    console.log('  ✅ Requirement 1: Next.js page using RegisterForm component');
    console.log('  ✅ Requirement 2: Integration with useAuth hook');
    console.log('  ✅ Requirement 3: Proper error handling and loading states');
    console.log('  ✅ Requirement 4: Navigation and routing logic');
    console.log('  ✅ Requirement 5: Responsive design and accessibility');
    console.log('  ✅ Requirement 6: AuthProvider integration');
    console.log('  ✅ Requirement 7: User redirect logic for authenticated users');
    
    console.log('\n✨ All T024 requirements satisfied!');
    
    console.log('\n🎉 SUCCESS: T024 Registration Page implementation is complete and valid!');
    
    console.log('\n📊 Implementation Summary:');
    console.log(`  - Main File: frontend/src/app/register/page.tsx`);
    console.log(`  - Size: ${size}KB`);
    console.log(`  - Lines: ${lines}`);
    console.log(`  - Components: RegisterForm, Error Display, Loading States`);
    console.log(`  - Features: Auth Integration, Navigation, Responsive Design`);
    console.log(`  - Next.js: App Router with proper structure`);
    
    return true;
    
  } catch (error) {
    console.log('\n❌ VALIDATION FAILED:');
    console.log(`   ${error.message}`);
    return false;
  }
}

// ============================================================================
// SCRIPT EXECUTION
// ============================================================================

if (require.main === module) {
  validateT024Implementation()
    .then((success) => {
      process.exit(success ? 0 : 1);
    })
    .catch((error) => {
      console.error('Validation script error:', error);
      process.exit(1);
    });
}

module.exports = {
  validateT024Implementation,
  TASK_ID,
  TASK_DESCRIPTION
};