/**
 * Error Service
 * Centralized error handling with typed errors, retry logic, and structured logging
 */

import type { DomainError } from '../domain/types';

// Error Types
export enum ErrorCode {
  // Network Errors
  NETWORK_ERROR = 'NETWORK_ERROR',
  TIMEOUT_ERROR = 'TIMEOUT_ERROR',
  CONNECTION_REFUSED = 'CONNECTION_REFUSED',
  
  // Authentication Errors
  AUTH_TOKEN_EXPIRED = 'AUTH_TOKEN_EXPIRED',
  AUTH_INVALID_TOKEN = 'AUTH_INVALID_TOKEN',
  AUTH_INSUFFICIENT_PERMISSIONS = 'AUTH_INSUFFICIENT_PERMISSIONS',
  
  // Validation Errors
  VALIDATION_FAILED = 'VALIDATION_FAILED',
  INVALID_INPUT = 'INVALID_INPUT',
  REQUIRED_FIELD_MISSING = 'REQUIRED_FIELD_MISSING',
  
  // Business Logic Errors
  SALARY_CALCULATION_FAILED = 'SALARY_CALCULATION_FAILED',
  CPI_DATA_UNAVAILABLE = 'CPI_DATA_UNAVAILABLE',
  BENCHMARK_DATA_UNAVAILABLE = 'BENCHMARK_DATA_UNAVAILABLE',
  
  // API Errors
  API_ERROR = 'API_ERROR',
  RATE_LIMIT_EXCEEDED = 'RATE_LIMIT_EXCEEDED',
  SERVICE_UNAVAILABLE = 'SERVICE_UNAVAILABLE',
  
  // Unknown Errors
  UNKNOWN_ERROR = 'UNKNOWN_ERROR'
}

export class WageLiftError extends Error {
  public readonly code: ErrorCode;
  public readonly details?: Record<string, any>;
  public readonly timestamp: Date;
  public readonly retryable: boolean;

  constructor(
    code: ErrorCode,
    message: string,
    details?: Record<string, any>,
    retryable: boolean = false
  ) {
    super(message);
    this.name = 'WageLiftError';
    this.code = code;
    this.details = details;
    this.timestamp = new Date();
    this.retryable = retryable;
  }

  toDomainError(): DomainError {
    return {
      code: this.code,
      message: this.message,
      details: this.details || {},
      timestamp: this.timestamp
    };
  }
}

export interface RetryOptions {
  maxAttempts: number;
  baseDelay: number;
  maxDelay: number;
  backoffFactor: number;
  jitter: boolean;
}

export class ErrorService {
  private static instance: ErrorService;
  private errorListeners: Array<(error: WageLiftError) => void> = [];

  static getInstance(): ErrorService {
    if (!ErrorService.instance) {
      ErrorService.instance = new ErrorService();
    }
    return ErrorService.instance;
  }

  /**
   * Add error listener for global error handling
   */
  addErrorListener(listener: (error: WageLiftError) => void): void {
    this.errorListeners.push(listener);
  }

  /**
   * Remove error listener
   */
  removeErrorListener(listener: (error: WageLiftError) => void): void {
    const index = this.errorListeners.indexOf(listener);
    if (index > -1) {
      this.errorListeners.splice(index, 1);
    }
  }

  /**
   * Handle and classify errors
   */
  handleError(error: unknown, context?: string): WageLiftError {
    let wageLiftError: WageLiftError;

    if (error instanceof WageLiftError) {
      wageLiftError = error;
    } else if (error instanceof Error) {
      wageLiftError = this.classifyError(error, context);
    } else {
      wageLiftError = new WageLiftError(
        ErrorCode.UNKNOWN_ERROR,
        'An unknown error occurred',
        { originalError: error, context }
      );
    }

    // Log error
    this.logError(wageLiftError, context);

    // Notify listeners
    this.errorListeners.forEach(listener => {
      try {
        listener(wageLiftError);
      } catch (listenerError) {
        console.error('Error in error listener:', listenerError);
      }
    });

    return wageLiftError;
  }

  /**
   * Classify generic errors into typed errors
   */
  private classifyError(error: Error, context?: string): WageLiftError {
    const message = error.message.toLowerCase();

    // Network errors
    if (message.includes('fetch') || message.includes('network')) {
      return new WageLiftError(
        ErrorCode.NETWORK_ERROR,
        'Network connection failed',
        { originalError: error.message, context },
        true
      );
    }

    // Timeout errors
    if (message.includes('timeout')) {
      return new WageLiftError(
        ErrorCode.TIMEOUT_ERROR,
        'Request timed out',
        { originalError: error.message, context },
        true
      );
    }

    // Connection refused
    if (message.includes('refused') || message.includes('econnrefused')) {
      return new WageLiftError(
        ErrorCode.CONNECTION_REFUSED,
        'Connection refused by server',
        { originalError: error.message, context },
        true
      );
    }

    // Authentication errors
    if (message.includes('unauthorized') || message.includes('401')) {
      return new WageLiftError(
        ErrorCode.AUTH_INVALID_TOKEN,
        'Authentication failed',
        { originalError: error.message, context }
      );
    }

    // Validation errors
    if (message.includes('validation') || message.includes('invalid')) {
      return new WageLiftError(
        ErrorCode.VALIDATION_FAILED,
        'Validation failed',
        { originalError: error.message, context }
      );
    }

    // Default to API error
    return new WageLiftError(
      ErrorCode.API_ERROR,
      error.message,
      { originalError: error.message, context },
      false
    );
  }

  /**
   * Retry logic with exponential backoff and jitter
   */
  async withRetry<T>(
    operation: () => Promise<T>,
    options: Partial<RetryOptions> = {}
  ): Promise<T> {
    const config: RetryOptions = {
      maxAttempts: 3,
      baseDelay: 1000,
      maxDelay: 10000,
      backoffFactor: 2,
      jitter: true,
      ...options
    };

    let lastError: WageLiftError;

    for (let attempt = 1; attempt <= config.maxAttempts; attempt++) {
      try {
        return await operation();
      } catch (error) {
        lastError = this.handleError(error, `Retry attempt ${attempt}`);

        // Don't retry if error is not retryable or this is the last attempt
        if (!lastError.retryable || attempt === config.maxAttempts) {
          throw lastError;
        }

        // Calculate delay with exponential backoff and jitter
        let delay = Math.min(
          config.baseDelay * Math.pow(config.backoffFactor, attempt - 1),
          config.maxDelay
        );

        if (config.jitter) {
          delay = delay * (0.5 + Math.random() * 0.5);
        }

        await this.sleep(delay);
      }
    }

    throw lastError!;
  }

  /**
   * Log error with structured format
   */
  private logError(error: WageLiftError, context?: string): void {
    const logData = {
      timestamp: error.timestamp.toISOString(),
      code: error.code,
      message: error.message,
      context,
      details: error.details,
      retryable: error.retryable,
      stack: error.stack
    };

    console.error('WageLift Error:', logData);

    // In production, send to logging service
    if (process.env.NODE_ENV === 'production') {
      this.sendToLoggingService(logData);
    }
  }

  /**
   * Send error to external logging service
   */
  private async sendToLoggingService(logData: any): Promise<void> {
    try {
      // Implement your logging service integration here
      // e.g., Sentry, LogRocket, DataDog, etc.
    } catch (loggingError) {
      console.error('Failed to send error to logging service:', loggingError);
    }
  }

  /**
   * Sleep utility for retry delays
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Create user-friendly error messages
   */
  getUserFriendlyMessage(error: WageLiftError): string {
    switch (error.code) {
      case ErrorCode.NETWORK_ERROR:
        return 'Unable to connect to the server. Please check your internet connection and try again.';
      
      case ErrorCode.TIMEOUT_ERROR:
        return 'The request is taking longer than expected. Please try again.';
      
      case ErrorCode.AUTH_TOKEN_EXPIRED:
        return 'Your session has expired. Please log in again.';
      
      case ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS:
        return 'You do not have permission to perform this action.';
      
      case ErrorCode.VALIDATION_FAILED:
        return 'Please check your input and try again.';
      
      case ErrorCode.SALARY_CALCULATION_FAILED:
        return 'Unable to calculate salary data. Please verify your information and try again.';
      
      case ErrorCode.CPI_DATA_UNAVAILABLE:
        return 'Cost of living data is temporarily unavailable. Please try again later.';
      
      case ErrorCode.RATE_LIMIT_EXCEEDED:
        return 'Too many requests. Please wait a moment and try again.';
      
      case ErrorCode.SERVICE_UNAVAILABLE:
        return 'The service is temporarily unavailable. Please try again later.';
      
      default:
        return 'An unexpected error occurred. Please try again or contact support if the problem persists.';
    }
  }
}

// Export singleton instance
export const errorService = ErrorService.getInstance(); 