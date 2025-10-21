/**
 * Responsive Design Utilities and Components for IdeaFly Application.
 * 
 * Provides mobile-first responsive design patterns, touch-friendly interactions,
 * breakpoint management, and adaptive components optimized for all devices.
 */

'use client';

import React, { 
  createContext, 
  useContext, 
  useState, 
  useEffect, 
  useCallback
} from 'react';

// ============================================================================
// TYPES AND INTERFACES
// ============================================================================

/**
 * Breakpoint definitions following mobile-first approach
 */
export const Breakpoints = {
  xs: 0,      // 0px and up (mobile)
  sm: 640,    // 640px and up (large mobile/small tablet)
  md: 768,    // 768px and up (tablet)
  lg: 1024,   // 1024px and up (desktop)
  xl: 1280,   // 1280px and up (large desktop)
  '2xl': 1536 // 1536px and up (extra large desktop)
} as const;

export type BreakpointKey = keyof typeof Breakpoints;

/**
 * Current viewport information
 */
interface ViewportInfo {
  width: number;
  height: number;
  currentBreakpoint: BreakpointKey;
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  orientation: 'portrait' | 'landscape';
  isTouch: boolean;
}

/**
 * Responsive context type
 */
interface ResponsiveContextType extends ViewportInfo {
  /** Get responsive value based on current breakpoint */
  getResponsiveValue: <T>(values: Partial<Record<BreakpointKey, T>>) => T | undefined;
  /** Check if current viewport matches breakpoint */
  matchesBreakpoint: (breakpoint: BreakpointKey, direction?: 'up' | 'down') => boolean;
}

// ============================================================================
// RESPONSIVE CONTEXT AND PROVIDER
// ============================================================================

const ResponsiveContext = createContext<ResponsiveContextType | undefined>(undefined);

/**
 * Responsive Provider Component
 */
export const ResponsiveProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [viewportInfo, setViewportInfo] = useState<ViewportInfo>({
    width: 0,
    height: 0,
    currentBreakpoint: 'xs',
    isMobile: false,
    isTablet: false,
    isDesktop: false,
    orientation: 'portrait',
    isTouch: false
  });

  /**
   * Determine current breakpoint based on width
   */
  const getCurrentBreakpoint = useCallback((width: number): BreakpointKey => {
    if (width >= Breakpoints['2xl']) return '2xl';
    if (width >= Breakpoints.xl) return 'xl';
    if (width >= Breakpoints.lg) return 'lg';
    if (width >= Breakpoints.md) return 'md';
    if (width >= Breakpoints.sm) return 'sm';
    return 'xs';
  }, []);

  /**
   * Detect device type based on viewport
   */
  const getDeviceType = useCallback((width: number, isTouch: boolean) => {
    return {
      isMobile: width < Breakpoints.md || (isTouch && width < Breakpoints.lg),
      isTablet: width >= Breakpoints.md && width < Breakpoints.lg && isTouch,
      isDesktop: width >= Breakpoints.lg && !isTouch
    };
  }, []);

  /**
   * Update viewport information
   */
  const updateViewportInfo = useCallback(() => {
    if (typeof window === 'undefined') return;

    const width = window.innerWidth;
    const height = window.innerHeight;
    const currentBreakpoint = getCurrentBreakpoint(width);
    const orientation = width > height ? 'landscape' : 'portrait';
    const isTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    const deviceTypes = getDeviceType(width, isTouch);

    setViewportInfo({
      width,
      height,
      currentBreakpoint,
      orientation,
      isTouch,
      ...deviceTypes
    });
  }, [getCurrentBreakpoint, getDeviceType]);

  // Initialize and listen for viewport changes
  useEffect(() => {
    updateViewportInfo();

    let timeoutId: NodeJS.Timeout;
    const handleResize = () => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(updateViewportInfo, 100); // Debounce resize events
    };

    window.addEventListener('resize', handleResize);
    window.addEventListener('orientationchange', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('orientationchange', handleResize);
      clearTimeout(timeoutId);
    };
  }, [updateViewportInfo]);

  /**
   * Get responsive value based on current breakpoint
   */
  const getResponsiveValue = useCallback(<T extends unknown>(values: Partial<Record<BreakpointKey, T>>): T | undefined => {
    const breakpointOrder: BreakpointKey[] = ['2xl', 'xl', 'lg', 'md', 'sm', 'xs'];
    const currentIndex = breakpointOrder.indexOf(viewportInfo.currentBreakpoint);
    
    // Look for value at current breakpoint or smaller
    for (let i = currentIndex; i < breakpointOrder.length; i++) {
      const breakpoint = breakpointOrder[i];
      if (values[breakpoint] !== undefined) {
        return values[breakpoint];
      }
    }
    
    return undefined;
  }, [viewportInfo.currentBreakpoint]);

  /**
   * Check if current viewport matches breakpoint
   */
  const matchesBreakpoint = useCallback((breakpoint: BreakpointKey, direction: 'up' | 'down' = 'up'): boolean => {
    const breakpointWidth = Breakpoints[breakpoint];
    
    if (direction === 'up') {
      return viewportInfo.width >= breakpointWidth;
    } else {
      return viewportInfo.width < breakpointWidth;
    }
  }, [viewportInfo.width]);

  const value: ResponsiveContextType = {
    ...viewportInfo,
    getResponsiveValue,
    matchesBreakpoint
  };

  return (
    <ResponsiveContext.Provider value={value}>
      {children}
    </ResponsiveContext.Provider>
  );
};

/**
 * Hook to use responsive context
 */
export const useResponsive = (): ResponsiveContextType => {
  const context = useContext(ResponsiveContext);
  if (!context) {
    throw new Error('useResponsive must be used within a ResponsiveProvider');
  }
  return context;
};

// ============================================================================
// RESPONSIVE HOOKS
// ============================================================================

/**
 * Hook for media query matching
 */
export const useMediaQuery = (query: string): boolean => {
  const [matches, setMatches] = useState(false);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const mediaQuery = window.matchMedia(query);
    setMatches(mediaQuery.matches);

    const handleChange = (event: MediaQueryListEvent) => {
      setMatches(event.matches);
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [query]);

  return matches;
};

/**
 * Hook for breakpoint matching
 */
export const useBreakpoint = (breakpoint: BreakpointKey, direction: 'up' | 'down' = 'up'): boolean => {
  const breakpointPx = Breakpoints[breakpoint];
  const query = direction === 'up' 
    ? `(min-width: ${breakpointPx}px)`
    : `(max-width: ${breakpointPx - 1}px)`;
  
  return useMediaQuery(query);
};

/**
 * Hook for responsive values
 */
export const useResponsiveValue = <T>(values: Partial<Record<BreakpointKey, T>>): T | undefined => {
  const { getResponsiveValue } = useResponsive();
  return getResponsiveValue(values);
};

// ============================================================================
// RESPONSIVE COMPONENTS
// ============================================================================

/**
 * Responsive Container Component
 */
export const ResponsiveContainer: React.FC<{
  children: ReactNode;
  maxWidth?: BreakpointKey | 'none';
  padding?: boolean;
  className?: string;
}> = ({ 
  children, 
  maxWidth = 'lg', 
  padding = true, 
  className = '' 
}) => {
  const maxWidthClasses = {
    xs: 'max-w-none',
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
    '2xl': 'max-w-2xl',
    none: 'max-w-none'
  };

  const paddingClasses = padding ? 'px-4 sm:px-6 lg:px-8' : '';

  return (
    <div className={`mx-auto w-full ${maxWidthClasses[maxWidth]} ${paddingClasses} ${className}`}>
      {children}
    </div>
  );
};

/**
 * Responsive Grid Component
 */
export const ResponsiveGrid: React.FC<{
  children: ReactNode;
  columns?: Partial<Record<BreakpointKey, number>>;
  gap?: Partial<Record<BreakpointKey, number>>;
  className?: string;
}> = ({ 
  children, 
  columns = { xs: 1, sm: 2, lg: 3 }, 
  gap = { xs: 4, sm: 6 },
  className = '' 
}) => {
  const { getResponsiveValue } = useResponsive();
  
  const currentColumns = getResponsiveValue(columns) || 1;
  const currentGap = getResponsiveValue(gap) || 4;

  const gridClasses = `grid grid-cols-${currentColumns} gap-${currentGap}`;

  return (
    <div className={`${gridClasses} ${className}`}>
      {children}
    </div>
  );
};

/**
 * Responsive Breakpoint Display Component (for development)
 */
export const BreakpointIndicator: React.FC<{ show?: boolean }> = ({ show = false }) => {
  const { currentBreakpoint, width, height } = useResponsive();

  if (!show || process.env.NODE_ENV === 'production') return null;

  return (
    <div className="fixed bottom-4 right-4 bg-black bg-opacity-75 text-white p-2 rounded text-xs font-mono z-50">
      <div>Breakpoint: {currentBreakpoint}</div>
      <div>Size: {width}x{height}</div>
    </div>
  );
};

/**
 * Touch-friendly Button Component
 */
export const TouchButton: React.FC<{
  children: ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg' | 'touch';
  fullWidth?: boolean;
  className?: string;
  type?: 'button' | 'submit' | 'reset';
}> = ({
  children,
  onClick,
  disabled = false,
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  className = '',
  type = 'button'
}) => {
  const { isTouch } = useResponsive();

  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed select-none';
  
  const variantClasses = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500 active:bg-blue-800',
    secondary: 'bg-gray-600 text-white hover:bg-gray-700 focus:ring-gray-500 active:bg-gray-800',
    ghost: 'text-gray-700 hover:bg-gray-50 focus:ring-gray-500 active:bg-gray-100'
  };

  // Touch-optimized sizing
  const sizeClasses = {
    sm: isTouch ? 'px-4 py-3 text-sm min-h-[44px]' : 'px-3 py-2 text-sm',
    md: isTouch ? 'px-5 py-3 text-base min-h-[48px]' : 'px-4 py-2 text-base',
    lg: isTouch ? 'px-6 py-4 text-lg min-h-[52px]' : 'px-6 py-3 text-lg',
    touch: 'px-6 py-4 text-base min-h-[48px]'
  };

  const widthClass = fullWidth ? 'w-full' : '';

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${widthClass} ${className}`}
    >
      {children}
    </button>
  );
};

/**
 * Responsive Input Component
 */
export const ResponsiveInput: React.FC<{
  id?: string;
  name?: string;
  type?: string;
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onBlur?: (e: React.FocusEvent<HTMLInputElement>) => void;
  placeholder?: string;
  disabled?: boolean;
  required?: boolean;
  autoComplete?: string;
  className?: string;
  error?: boolean;
}> = ({
  id,
  name,
  type = 'text',
  value,
  onChange,
  onBlur,
  placeholder,
  disabled = false,
  required = false,
  autoComplete,
  className = '',
  error = false
}) => {
  const { isTouch } = useResponsive();

  // Touch-optimized input sizing
  const baseClasses = `block w-full border rounded-md shadow-sm placeholder-gray-400 
    focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 
    disabled:bg-gray-100 disabled:cursor-not-allowed transition-colors duration-200
    ${isTouch ? 'px-4 py-3 text-base min-h-[48px]' : 'px-3 py-2 text-sm'}`;

  const stateClasses = error 
    ? 'border-red-300 focus:ring-red-500 focus:border-red-500'
    : 'border-gray-300 focus:border-blue-500';

  return (
    <input
      id={id}
      name={name}
      type={type}
      value={value}
      onChange={onChange}
      onBlur={onBlur}
      placeholder={placeholder}
      disabled={disabled}
      required={required}
      autoComplete={autoComplete}
      className={`${baseClasses} ${stateClasses} ${className}`}
    />
  );
};

/**
 * Responsive Layout Component
 */
export const ResponsiveLayout: React.FC<{
  children: ReactNode;
  sidebar?: ReactNode;
  header?: ReactNode;
  footer?: ReactNode;
  sidebarPosition?: 'left' | 'right';
  className?: string;
}> = ({
  children,
  sidebar,
  header,
  footer,
  sidebarPosition = 'left',
  className = ''
}) => {
  const { isMobile } = useResponsive();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const toggleSidebar = () => setSidebarOpen(!sidebarOpen);

  return (
    <div className={`min-h-screen flex flex-col ${className}`}>
      {/* Header */}
      {header && (
        <header className="flex-shrink-0">
          {header}
        </header>
      )}

      {/* Main Content Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar for desktop, drawer for mobile */}
        {sidebar && (
          <>
            {isMobile ? (
              /* Mobile Drawer */
              <>
                {sidebarOpen && (
                  <div 
                    className="fixed inset-0 bg-gray-600 bg-opacity-75 z-40"
                    onClick={() => setSidebarOpen(false)}
                  />
                )}
                <div className={`fixed inset-y-0 ${sidebarPosition}-0 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out z-50 ${
                  sidebarOpen ? 'translate-x-0' : sidebarPosition === 'left' ? '-translate-x-full' : 'translate-x-full'
                }`}>
                  {sidebar}
                </div>
              </>
            ) : (
              /* Desktop Sidebar */
              <aside className={`flex-shrink-0 w-64 bg-white border-r border-gray-200 ${
                sidebarPosition === 'right' ? 'order-2' : ''
              }`}>
                {sidebar}
              </aside>
            )}
          </>
        )}

        {/* Main Content */}
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>

      {/* Footer */}
      {footer && (
        <footer className="flex-shrink-0">
          {footer}
        </footer>
      )}

      {/* Mobile Sidebar Toggle Button */}
      {sidebar && isMobile && (
        <button
          onClick={toggleSidebar}
          className="fixed bottom-4 right-4 bg-blue-600 text-white p-3 rounded-full shadow-lg z-30"
          aria-label="Toggle navigation menu"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      )}
    </div>
  );
};

// ============================================================================
// RESPONSIVE UTILITIES
// ============================================================================

/**
 * Generate responsive classes helper
 */
export const generateResponsiveClasses = (
  baseClass: string,
  values: Partial<Record<BreakpointKey, string>>
): string => {
  const classes: string[] = [];

  Object.entries(values).forEach(([breakpoint, value]) => {
    if (breakpoint === 'xs') {
      classes.push(`${baseClass}-${value}`);
    } else {
      classes.push(`${breakpoint}:${baseClass}-${value}`);
    }
  });

  return classes.join(' ');
};

/**
 * Responsive spacing utility
 */
export const responsiveSpacing = (
  property: 'p' | 'm' | 'px' | 'py' | 'pl' | 'pr' | 'pt' | 'pb' | 'mx' | 'my' | 'ml' | 'mr' | 'mt' | 'mb',
  values: Partial<Record<BreakpointKey, number>>
): string => {
  return generateResponsiveClasses(property, values as Partial<Record<BreakpointKey, string>>);
};

export default {
  ResponsiveProvider,
  useResponsive,
  useMediaQuery,
  useBreakpoint,
  useResponsiveValue,
  ResponsiveContainer,
  ResponsiveGrid,
  BreakpointIndicator,
  TouchButton,
  ResponsiveInput,
  ResponsiveLayout,
  generateResponsiveClasses,
  responsiveSpacing,
  Breakpoints
};