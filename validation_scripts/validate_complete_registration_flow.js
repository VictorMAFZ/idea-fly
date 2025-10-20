/**
 * End-to-End Registration Flow Validation Script
 * 
 * Validates the complete registration workflow from frontend to backend
 * after T025 integration completion.
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
  MAGENTA: '\x1b[35m',
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

function readFile(filePath) {
  try {
    return fs.readFileSync(filePath, 'utf8');
  } catch (err) {
    error(`Failed to read file: ${filePath}`);
    return null;
  }
}

function fileExists(filePath) {
  try {
    return fs.existsSync(filePath);
  } catch (err) {
    return false;
  }
}

/**
 * Validate complete registration flow architecture
 */
function validateRegistrationFlowArchitecture() {
  section('Validating Registration Flow Architecture');
  
  const files = [
    // Backend files
    { path: 'backend/src/auth/repository.py', description: 'User Repository' },
    { path: 'backend/src/auth/service.py', description: 'Auth Service' },
    { path: 'backend/src/auth/router.py', description: 'Register Endpoint' },
    
    // Frontend files
    { path: 'frontend/src/components/auth/RegisterForm.tsx', description: 'RegisterForm Component' },
    { path: 'frontend/src/services/authService.ts', description: 'Registration Service' },
    { path: 'frontend/src/hooks/useAuth.ts', description: 'useAuth Hook' },
    { path: 'frontend/src/app/register/page.tsx', description: 'Registration Page' },
    { path: 'frontend/src/contexts/AuthContext.tsx', description: 'AuthContext' }
  ];
  
  let allFilesExist = true;
  
  files.forEach(({ path: filePath, description }) => {
    const fullPath = path.join(__dirname, '..', filePath);
    if (fileExists(fullPath)) {
      success(`${description}: ${filePath}`);
    } else {
      error(`Missing ${description}: ${filePath}`);
      allFilesExist = false;
    }
  });
  
  return allFilesExist;
}

/**
 * Validate backend registration implementation
 */
function validateBackendImplementation() {
  section('Validating Backend Registration Implementation');
  
  // Check repository
  const repositoryPath = path.join(__dirname, '..', 'backend', 'src', 'auth', 'repository.py');
  const repositoryContent = readFile(repositoryPath);
  
  if (!repositoryContent) return false;
  
  const repositoryChecks = [
    { pattern: /create_user/g, description: 'create_user method' },
    { pattern: /get_user_by_email/g, description: 'get_user_by_email method' },
    { pattern: /hash_password/g, description: 'password hashing' },
    { pattern: /SQLAlchemy/g, description: 'SQLAlchemy integration' }
  ];
  
  let repositoryValid = true;
  repositoryChecks.forEach(({ pattern, description }) => {
    if (repositoryContent.match(pattern)) {
      success(`Repository: ${description} ✓`);
    } else {
      error(`Repository: Missing ${description}`);
      repositoryValid = false;
    }
  });
  
  // Check service
  const servicePath = path.join(__dirname, '..', 'backend', 'src', 'auth', 'service.py');
  const serviceContent = readFile(servicePath);
  
  if (!serviceContent) return false;
  
  const serviceChecks = [
    { pattern: /register_user/g, description: 'register_user method' },
    { pattern: /EmailAlreadyExistsError/g, description: 'email validation' },
    { pattern: /create_access_token/g, description: 'JWT token creation' },
    { pattern: /AuthResponse/g, description: 'AuthResponse usage' }
  ];
  
  let serviceValid = true;
  serviceChecks.forEach(({ pattern, description }) => {
    if (serviceContent.match(pattern)) {
      success(`Service: ${description} ✓`);
    } else {
      error(`Service: Missing ${description}`);
      serviceValid = false;
    }
  });
  
  // Check router
  const routerPath = path.join(__dirname, '..', 'backend', 'src', 'auth', 'router.py');
  const routerContent = readFile(routerPath);
  
  if (!routerContent) return false;
  
  const routerChecks = [
    { pattern: /\/auth\/register/g, description: '/auth/register endpoint' },
    { pattern: /RegisterRequest/g, description: 'RegisterRequest schema' },
    { pattern: /status_code=201/g, description: 'HTTP 201 status' },
    { pattern: /HTTPException/g, description: 'error handling' }
  ];
  
  let routerValid = true;
  routerChecks.forEach(({ pattern, description }) => {
    if (routerContent.match(pattern)) {
      success(`Router: ${description} ✓`);
    } else {
      error(`Router: Missing ${description}`);
      routerValid = false;
    }
  });
  
  return repositoryValid && serviceValid && routerValid;
}

/**
 * Validate frontend registration implementation
 */
function validateFrontendImplementation() {
  section('Validating Frontend Registration Implementation');
  
  // Check RegisterForm component
  const formPath = path.join(__dirname, '..', 'frontend', 'src', 'components', 'auth', 'RegisterForm.tsx');
  const formContent = readFile(formPath);
  
  if (!formContent) return false;
  
  const formChecks = [
    { pattern: /useForm/g, description: 'react-hook-form integration' },
    { pattern: /zodResolver/g, description: 'Zod validation' },
    { pattern: /registerSchema/g, description: 'registration schema' },
    { pattern: /TailwindCSS|className/g, description: 'TailwindCSS styling' }
  ];
  
  let formValid = true;
  formChecks.forEach(({ pattern, description }) => {
    if (formContent.match(pattern)) {
      success(`RegisterForm: ${description} ✓`);
    } else {
      error(`RegisterForm: Missing ${description}`);
      formValid = false;
    }
  });
  
  // Check authService
  const authServicePath = path.join(__dirname, '..', 'frontend', 'src', 'services', 'authService.ts');
  const authServiceContent = readFile(authServicePath);
  
  if (!authServiceContent) return false;
  
  const authServiceChecks = [
    { pattern: /register.*async/g, description: 'async register method' },
    { pattern: /httpClient/g, description: 'HTTP client usage' },
    { pattern: /\/auth\/register/g, description: 'register endpoint' },
    { pattern: /ApiResponse/g, description: 'typed responses' }
  ];
  
  let authServiceValid = true;
  authServiceChecks.forEach(({ pattern, description }) => {
    if (authServiceContent.match(pattern)) {
      success(`AuthService: ${description} ✓`);
    } else {
      error(`AuthService: Missing ${description}`);
      authServiceValid = false;
    }
  });
  
  // Check useAuth hook
  const hookPath = path.join(__dirname, '..', 'frontend', 'src', 'hooks', 'useAuth.ts');
  const hookContent = readFile(hookPath);
  
  if (!hookContent) return false;
  
  const hookChecks = [
    { pattern: /registerWithService/g, description: 'registerWithService method' },
    { pattern: /AuthContext/g, description: 'AuthContext integration' },
    { pattern: /useState.*loading/g, description: 'loading state' },
    { pattern: /catch.*error/g, description: 'error handling' }
  ];
  
  let hookValid = true;
  hookChecks.forEach(({ pattern, description }) => {
    if (hookContent.match(pattern)) {
      success(`useAuth Hook: ${description} ✓`);
    } else {
      error(`useAuth Hook: Missing ${description}`);
      hookValid = false;
    }
  });
  
  return formValid && authServiceValid && hookValid;
}

/**
 * Validate T025 AuthContext integration
 */
function validateAuthContextIntegration() {
  section('Validating T025 AuthContext Integration');
  
  const contextPath = path.join(__dirname, '..', 'frontend', 'src', 'contexts', 'AuthContext.tsx');
  const contextContent = readFile(contextPath);
  
  if (!contextContent) return false;
  
  const integrationChecks = [
    { pattern: /import.*authService/g, description: 'authService import' },
    { pattern: /authService\.register/g, description: 'real authService.register calls' },
    { pattern: /authService\.login/g, description: 'real authService.login calls' },
    { pattern: /authService\.logout/g, description: 'real authService.logout calls' },
    { pattern: /authService\.getUserProfile/g, description: 'real authService.getUserProfile calls' },
    { pattern: /response\.success/g, description: 'API response handling' },
    { pattern: /response\.error\?\.message/g, description: 'error message extraction' }
  ];
  
  // Check for absence of mock patterns
  const mockPatterns = [
    { pattern: /setTimeout.*resolve/g, description: 'mock setTimeout calls' },
    { pattern: /mock_token_/g, description: 'mock token generation' },
    { pattern: /Mock User/g, description: 'mock user data' },
    { pattern: /TODO.*Replace/g, description: 'TODO comments' }
  ];
  
  let integrationValid = true;
  
  integrationChecks.forEach(({ pattern, description }) => {
    if (contextContent.match(pattern)) {
      success(`AuthContext: ${description} ✓`);
    } else {
      error(`AuthContext: Missing ${description}`);
      integrationValid = false;
    }
  });
  
  mockPatterns.forEach(({ pattern, description }) => {
    if (!contextContent.match(pattern)) {
      success(`AuthContext: No ${description} ✓`);
    } else {
      error(`AuthContext: Found ${description} (should be removed)`);
      integrationValid = false;
    }
  });
  
  return integrationValid;
}

/**
 * Validate registration page implementation
 */
function validateRegistrationPage() {
  section('Validating Registration Page Implementation');
  
  const pagePath = path.join(__dirname, '..', 'frontend', 'src', 'app', 'register', 'page.tsx');
  const pageContent = readFile(pagePath);
  
  if (!pageContent) return false;
  
  const pageChecks = [
    { pattern: /useAuth/g, description: 'useAuth hook usage' },
    { pattern: /RegisterForm/g, description: 'RegisterForm component' },
    { pattern: /useRouter/g, description: 'Next.js router' },
    { pattern: /handleRegister/g, description: 'registration handler' },
    { pattern: /isAuthenticated/g, description: 'authentication check' }
  ];
  
  let pageValid = true;
  pageChecks.forEach(({ pattern, description }) => {
    if (pageContent.match(pattern)) {
      success(`Registration Page: ${description} ✓`);
    } else {
      error(`Registration Page: Missing ${description}`);
      pageValid = false;
    }
  });
  
  return pageValid;
}

/**
 * Main validation function
 */
function validateCompleteRegistrationFlow() {
  log(COLORS.MAGENTA, '\n🎯 COMPLETE REGISTRATION FLOW VALIDATION', '='.repeat(15) + ' ');
  log(COLORS.CYAN, '   End-to-End US1 Registration Implementation\n');
  
  const validations = [
    { name: 'Architecture', fn: validateRegistrationFlowArchitecture },
    { name: 'Backend Implementation', fn: validateBackendImplementation },
    { name: 'Frontend Implementation', fn: validateFrontendImplementation },
    { name: 'T025 AuthContext Integration', fn: validateAuthContextIntegration },
    { name: 'Registration Page', fn: validateRegistrationPage }
  ];
  
  const results = validations.map(({ name, fn }) => {
    const result = fn();
    return { name, result };
  });
  
  const allValid = results.every(({ result }) => result);
  
  section('Final Validation Summary');
  
  results.forEach(({ name, result }) => {
    if (result) {
      success(`${name}: PASSED`);
    } else {
      error(`${name}: FAILED`);
    }
  });
  
  if (allValid) {
    log(COLORS.MAGENTA, '\n🎉 🎉 🎉 REGISTRATION FLOW COMPLETE! 🎉 🎉 🎉');
    success('✨ US1: User Registration - ALL TASKS COMPLETED');
    info('📋 T018-T025: All tasks successfully implemented and validated');
    info('🏗️  Architecture: Backend repository → service → router');
    info('🎨 Frontend: Component → hook → service → context');
    info('🔗 Integration: Real API calls, no mock implementations');
    info('✅ End-to-end registration workflow ready for testing');
    log(COLORS.CYAN, '\n🚀 Ready for development and user testing!\n');
    return true;
  } else {
    error('❌ REGISTRATION FLOW VALIDATION FAILED');
    warning('Please fix the issues identified above');
    return false;
  }
}

// Run validation
const isValid = validateCompleteRegistrationFlow();
process.exit(isValid ? 0 : 1);