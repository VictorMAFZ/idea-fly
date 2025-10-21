/**
 * Accessibility Utilities and Components for IdeaFly Application.
 * 
 * Provides WCAG 2.1 AA compliant accessibility features including
 * focus management, keyboard navigation, screen reader support,
 * and ARIA enhancements.
 */

'use client';

import React, { 
  createContext, 
  useContext, 
  useCallback, 
  useEffect, 
  useRef, 
  useState,
  ReactNode,
  KeyboardEvent,
  FocusEvent
} from 'react';

// ============================================================================
// TYPES AND INTERFACES
// ============================================================================

/**
 * Focus management context interface
 */
interface FocusManagerContextType {
  /** Focus trap active state */
  isTrapActive: boolean;
  /** Activate focus trap */
  activateTrap: (element: HTMLElement) => void;
  /** Deactivate focus trap */
  deactivateTrap: () => void;
  /** Set focus to element by selector or ref */
  focusElement: (selector: string | HTMLElement) => void;
  /** Announce message to screen readers */
  announce: (message: string, priority?: 'polite' | 'assertive') => void;
}

/**
 * Accessibility preferences interface
 */
interface AccessibilityPreferences {
  /** Reduced motion preference */
  prefersReducedMotion: boolean;
  /** High contrast preference */
  prefersHighContrast: boolean;
  /** Focus visible preference */
  prefersFocusVisible: boolean;
}

/**
 * Keyboard navigation handler type
 */
type KeyboardHandler = (event: KeyboardEvent) => void;

// ============================================================================
// CONSTANTS
// ============================================================================

/**
 * Focusable element selectors for focus trapping
 */
const FOCUSABLE_SELECTORS = [
  'a[href]',
  'button:not([disabled])',
  'textarea:not([disabled])',
  'input:not([disabled])',
  'select:not([disabled])',
  '[tabindex]:not([tabindex="-1"])',
  '[contenteditable="true"]'
].join(',');

/**
 * Common keyboard codes for navigation
 */
export const KeyCodes = {
  ENTER: 'Enter',
  SPACE: ' ',
  ESCAPE: 'Escape',
  TAB: 'Tab',
  ARROW_UP: 'ArrowUp',
  ARROW_DOWN: 'ArrowDown',
  ARROW_LEFT: 'ArrowLeft',
  ARROW_RIGHT: 'ArrowRight',
  HOME: 'Home',
  END: 'End'
} as const;

// ============================================================================
// CONTEXT AND PROVIDER
// ============================================================================

/**
 * Focus manager context
 */
const FocusManagerContext = createContext<FocusManagerContextType | undefined>(undefined);

/**
 * Focus Manager Provider Component
 */
export const FocusManagerProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isTrapActive, setIsTrapActive] = useState(false);
  const trapRef = useRef<HTMLElement | null>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);
  const announcerRef = useRef<HTMLDivElement | null>(null);

  // Initialize live region announcer
  useEffect(() => {
    // Create announcer element for screen readers
    const announcer = document.createElement('div');
    announcer.setAttribute('aria-live', 'polite');
    announcer.setAttribute('aria-atomic', 'true');
    announcer.setAttribute('role', 'status');
    announcer.style.position = 'absolute';
    announcer.style.left = '-10000px';
    announcer.style.width = '1px';
    announcer.style.height = '1px';
    announcer.style.overflow = 'hidden';
    
    document.body.appendChild(announcer);
    announcerRef.current = announcer;

    return () => {
      if (announcerRef.current && document.body.contains(announcerRef.current)) {
        document.body.removeChild(announcerRef.current);
      }
    };
  }, []);

  /**
   * Get all focusable elements within a container
   */
  const getFocusableElements = useCallback((container: HTMLElement): HTMLElement[] => {
    return Array.from(container.querySelectorAll(FOCUSABLE_SELECTORS))
      .filter(element => {
        const style = window.getComputedStyle(element);
        return style.display !== 'none' && style.visibility !== 'hidden';
      }) as HTMLElement[];
  }, []);

  /**
   * Handle focus trap keydown events
   */
  const handleTrapKeydown = useCallback((event: Event) => {
    const keyboardEvent = event as unknown as KeyboardEvent;
    
    if (!isTrapActive || !trapRef.current || keyboardEvent.key !== KeyCodes.TAB) {
      return;
    }

    const focusableElements = getFocusableElements(trapRef.current);
    
    if (focusableElements.length === 0) {
      keyboardEvent.preventDefault();
      return;
    }

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];
    
    if (keyboardEvent.shiftKey) {
      // Shift + Tab - move to previous element
      if (document.activeElement === firstElement) {
        keyboardEvent.preventDefault();
        lastElement.focus();
      }
    } else {
      // Tab - move to next element
      if (document.activeElement === lastElement) {
        keyboardEvent.preventDefault();
        firstElement.focus();
      }
    }
  }, [isTrapActive, getFocusableElements]);

  /**
   * Activate focus trap
   */
  const activateTrap = useCallback((element: HTMLElement) => {
    // Store current focus to restore later
    previousFocusRef.current = document.activeElement as HTMLElement;
    
    trapRef.current = element;
    setIsTrapActive(true);
    
    // Add event listener for keydown
    document.addEventListener('keydown', handleTrapKeydown);
    
    // Focus first focusable element
    const focusableElements = getFocusableElements(element);
    if (focusableElements.length > 0) {
      focusableElements[0].focus();
    }
  }, [getFocusableElements, handleTrapKeydown]);

  /**
   * Deactivate focus trap
   */
  const deactivateTrap = useCallback(() => {
    setIsTrapActive(false);
    trapRef.current = null;
    
    // Remove event listener
    document.removeEventListener('keydown', handleTrapKeydown);
    
    // Restore previous focus
    if (previousFocusRef.current) {
      previousFocusRef.current.focus();
      previousFocusRef.current = null;
    }
  }, [handleTrapKeydown]);

  /**
   * Focus specific element
   */
  const focusElement = useCallback((selector: string | HTMLElement) => {
    let element: HTMLElement | null = null;
    
    if (typeof selector === 'string') {
      element = document.querySelector(selector);
    } else {
      element = selector;
    }
    
    if (element && typeof element.focus === 'function') {
      element.focus();
    }
  }, []);

  /**
   * Announce message to screen readers
   */
  const announce = useCallback((message: string, priority: 'polite' | 'assertive' = 'polite') => {
    if (announcerRef.current) {
      announcerRef.current.setAttribute('aria-live', priority);
      announcerRef.current.textContent = message;
      
      // Clear message after announcement
      setTimeout(() => {
        if (announcerRef.current) {
          announcerRef.current.textContent = '';
        }
      }, 1000);
    }
  }, []);

  const value: FocusManagerContextType = {
    isTrapActive,
    activateTrap,
    deactivateTrap,
    focusElement,
    announce
  };

  return (
    <FocusManagerContext.Provider value={value}>
      {children}
    </FocusManagerContext.Provider>
  );
};

/**
 * Hook to use focus manager
 */
export const useFocusManager = (): FocusManagerContextType => {
  const context = useContext(FocusManagerContext);
  if (!context) {
    throw new Error('useFocusManager must be used within a FocusManagerProvider');
  }
  return context;
};

// ============================================================================
// ACCESSIBILITY HOOKS
// ============================================================================

/**
 * Hook to detect accessibility preferences
 */
export const useAccessibilityPreferences = (): AccessibilityPreferences => {
  const [preferences, setPreferences] = useState<AccessibilityPreferences>({
    prefersReducedMotion: false,
    prefersHighContrast: false,
    prefersFocusVisible: false
  });

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const checkPreferences = () => {
        setPreferences({
          prefersReducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
          prefersHighContrast: window.matchMedia('(prefers-contrast: high)').matches,
          prefersFocusVisible: window.matchMedia('(prefers-reduced-motion: no-preference)').matches
        });
      };

      checkPreferences();

      // Listen for changes
      const mediaQueries = [
        window.matchMedia('(prefers-reduced-motion: reduce)'),
        window.matchMedia('(prefers-contrast: high)'),
        window.matchMedia('(prefers-reduced-motion: no-preference)')
      ];

      mediaQueries.forEach(mq => mq.addEventListener('change', checkPreferences));

      return () => {
        mediaQueries.forEach(mq => mq.removeEventListener('change', checkPreferences));
      };
    }
  }, []);

  return preferences;
};

/**
 * Hook for keyboard navigation handling
 */
export const useKeyboardNavigation = (handlers: Record<string, KeyboardHandler>) => {
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    const handler = handlers[event.key];
    if (handler) {
      handler(event);
    }
  }, [handlers]);

  return { onKeyDown: handleKeyDown };
};

/**
 * Hook for managing focus on mount/unmount
 */
export const useFocusOnMount = (shouldFocus = true, selector?: string) => {
  const elementRef = useRef<HTMLElement>(null);

  useEffect(() => {
    if (shouldFocus) {
      if (selector) {
        const element = document.querySelector(selector) as HTMLElement;
        if (element) {
          element.focus();
        }
      } else if (elementRef.current) {
        elementRef.current.focus();
      }
    }
  }, [shouldFocus, selector]);

  return elementRef;
};

// ============================================================================
// ACCESSIBILITY COMPONENTS
// ============================================================================

/**
 * Skip Link Component for keyboard navigation
 */
export const SkipLink: React.FC<{
  href: string;
  children: ReactNode;
  className?: string;
}> = ({ href, children, className = '' }) => {
  return (
    <a
      href={href}
      className={`sr-only focus:not-sr-only focus:absolute focus:top-0 focus:left-0 bg-blue-600 text-white p-2 z-50 ${className}`}
      onFocus={(e) => {
        e.target.scrollIntoView();
      }}
    >
      {children}
    </a>
  );
};

/**
 * Screen Reader Only Text Component
 */
export const ScreenReaderOnly: React.FC<{ 
  children: ReactNode;
  className?: string;
}> = ({ children, className = '' }) => {
  return (
    <span className={`sr-only ${className}`}>
      {children}
    </span>
  );
};

/**
 * Focus Trap Component
 */
export const FocusTrap: React.FC<{
  active: boolean;
  children: ReactNode;
  className?: string;
}> = ({ active, children, className = '' }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const { activateTrap, deactivateTrap } = useFocusManager();

  useEffect(() => {
    if (active && containerRef.current) {
      activateTrap(containerRef.current);
    } else {
      deactivateTrap();
    }

    return () => {
      deactivateTrap();
    };
  }, [active, activateTrap, deactivateTrap]);

  return (
    <div ref={containerRef} className={className}>
      {children}
    </div>
  );
};

/**
 * Accessible Button Component with enhanced features
 */
export const AccessibleButton: React.FC<{
  children: ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  loading?: boolean;
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  ariaLabel?: string;
  ariaDescribedby?: string;
  className?: string;
  type?: 'button' | 'submit' | 'reset';
}> = ({
  children,
  onClick,
  disabled = false,
  loading = false,
  variant = 'primary',
  size = 'md',
  ariaLabel,
  ariaDescribedby,
  className = '',
  type = 'button'
}) => {
  const { announce } = useFocusManager();

  const handleClick = useCallback(() => {
    if (!disabled && !loading && onClick) {
      onClick();
      if (ariaLabel) {
        announce(`${ariaLabel} activated`);
      }
    }
  }, [disabled, loading, onClick, ariaLabel, announce]);

  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed';
  
  const variantClasses = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500',
    secondary: 'bg-gray-600 text-white hover:bg-gray-700 focus:ring-gray-500',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500'
  };

  const sizeClasses = {
    sm: 'px-3 py-2 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg'
  };

  return (
    <button
      type={type}
      onClick={handleClick}
      disabled={disabled || loading}
      aria-label={ariaLabel}
      aria-describedby={ariaDescribedby}
      aria-busy={loading}
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
    >
      {loading && (
        <svg
          className="animate-spin -ml-1 mr-2 h-4 w-4"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      )}
      {children}
    </button>
  );
};

/**
 * Accessible Form Field Component
 */
export const AccessibleFormField: React.FC<{
  id: string;
  label: string;
  children: ReactNode;
  error?: string | null;
  helpText?: string;
  required?: boolean;
  className?: string;
}> = ({ id, label, children, error, helpText, required = false, className = '' }) => {
  const errorId = `${id}-error`;
  const helpId = `${id}-help`;

  return (
    <div className={`space-y-1 ${className}`}>
      <label 
        htmlFor={id}
        className="block text-sm font-medium text-gray-700 dark:text-gray-300"
      >
        {label}
        {required && (
          <span className="text-red-500 ml-1" aria-label="required">
            *
          </span>
        )}
      </label>
      
      {React.cloneElement(children as React.ReactElement, {
        id,
        'aria-describedby': [
          error ? errorId : null,
          helpText ? helpId : null
        ].filter(Boolean).join(' ') || undefined,
        'aria-invalid': !!error,
        required
      })}
      
      {helpText && (
        <p id={helpId} className="text-sm text-gray-500 dark:text-gray-400">
          {helpText}
        </p>
      )}
      
      {error && (
        <p id={errorId} className="text-sm text-red-600 dark:text-red-400" role="alert">
          {error}
        </p>
      )}
    </div>
  );
};

export default {
  FocusManagerProvider,
  useFocusManager,
  useAccessibilityPreferences,
  useKeyboardNavigation,
  useFocusOnMount,
  SkipLink,
  ScreenReaderOnly,
  FocusTrap,
  AccessibleButton,
  AccessibleFormField,
  KeyCodes
};