/**
 * Client-side Logger Utility for IdeaFly Frontend.
 * 
 * Provides structured logging with different levels, context,
 * and integration with Error Boundary and monitoring services.
 */

'use client';

// ============================================================================
// TYPES AND INTERFACES
// ============================================================================

export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3
}

interface LogContext {
  [key: string]: any;
}

interface LogEntry {
  level: LogLevel;
  message: string;
  context?: LogContext;
  timestamp: string;
  url?: string;
  userAgent?: string;
}

// ============================================================================
// LOGGER CONFIGURATION
// ============================================================================

class Logger {
  private minLevel: LogLevel;
  private isDevelopment: boolean;

  constructor() {
    this.isDevelopment = process.env.NODE_ENV === 'development';
    this.minLevel = this.isDevelopment ? LogLevel.DEBUG : LogLevel.INFO;
  }

  /**
   * Set minimum log level.
   */
  setLevel(level: LogLevel) {
    this.minLevel = level;
  }

  /**
   * Create a log entry with metadata.
   */
  private createLogEntry(level: LogLevel, message: string, context?: LogContext): LogEntry {
    return {
      level,
      message,
      context,
      timestamp: new Date().toISOString(),
      url: typeof window !== 'undefined' ? window.location.href : undefined,
      userAgent: typeof navigator !== 'undefined' ? navigator.userAgent : undefined
    };
  }

  /**
   * Format log message for console output.
   */
  private formatConsoleMessage(entry: LogEntry): string {
    const levelName = LogLevel[entry.level];
    const timestamp = new Date(entry.timestamp).toLocaleTimeString();
    return `[${timestamp}] ${levelName}: ${entry.message}`;
  }

  /**
   * Log message if level meets minimum threshold.
   */
  private log(level: LogLevel, message: string, context?: LogContext) {
    if (level < this.minLevel) return;

    const entry = this.createLogEntry(level, message, context);
    const formattedMessage = this.formatConsoleMessage(entry);

    // Console output based on level
    switch (level) {
      case LogLevel.DEBUG:
        console.debug(formattedMessage, context);
        break;
      case LogLevel.INFO:
        console.info(formattedMessage, context);
        break;
      case LogLevel.WARN:
        console.warn(formattedMessage, context);
        break;
      case LogLevel.ERROR:
        console.error(formattedMessage, context);
        break;
    }

    // In production, send to monitoring service
    if (!this.isDevelopment && level >= LogLevel.WARN) {
      this.sendToMonitoring(entry);
    }
  }

  /**
   * Send log entry to external monitoring service.
   */
  private sendToMonitoring(entry: LogEntry) {
    // TODO: Implement integration with monitoring service
    // Example: Sentry, LogRocket, DataDog, etc.
    console.info('Would send to monitoring:', entry);
  }

  /**
   * Debug level logging.
   */
  debug(message: string, context?: LogContext) {
    this.log(LogLevel.DEBUG, message, context);
  }

  /**
   * Info level logging.
   */
  info(message: string, context?: LogContext) {
    this.log(LogLevel.INFO, message, context);
  }

  /**
   * Warning level logging.
   */
  warn(message: string, context?: LogContext) {
    this.log(LogLevel.WARN, message, context);
  }

  /**
   * Error level logging.
   */
  error(message: string, context?: LogContext) {
    this.log(LogLevel.ERROR, message, context);
  }
}

// ============================================================================
// SINGLETON INSTANCE
// ============================================================================

export const logger = new Logger();

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Log authentication events.
 */
export function logAuthEvent(event: string, context?: LogContext) {
  logger.info(`Auth: ${event}`, { ...context, category: 'authentication' });
}

/**
 * Log API request events.
 */
export function logApiRequest(method: string, url: string, context?: LogContext) {
  logger.debug(`API ${method}: ${url}`, { ...context, category: 'api' });
}

/**
 * Log user interaction events.
 */
export function logUserAction(action: string, context?: LogContext) {
  logger.info(`User: ${action}`, { ...context, category: 'user_action' });
}

export default logger;