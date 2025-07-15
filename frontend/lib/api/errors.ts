/**
 * Custom error classes and error handling utilities for API operations
 */

export class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public details?: unknown
  ) {
    super(`API Error: ${status} - ${statusText}`)
    this.name = 'ApiError'
  }

  /**
   * Check if the error is a specific HTTP status code
   */
  isStatus(status: number): boolean {
    return this.status === status
  }

  /**
   * Check if the error is a client error (4xx)
   */
  isClientError(): boolean {
    return this.status >= 400 && this.status < 500
  }

  /**
   * Check if the error is a server error (5xx)
   */
  isServerError(): boolean {
    return this.status >= 500 && this.status < 600
  }
}

/**
 * Convert an API error to a user-friendly message
 */
export function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    switch (error.status) {
      case 400:
        return 'Invalid request. Please check your input.'
      case 401:
        return 'Authentication required.'
      case 403:
        return 'You do not have permission to perform this action.'
      case 404:
        return 'The requested resource was not found.'
      case 408:
        return 'Request timeout. Please try again.'
      case 429:
        return 'Too many requests. Please slow down.'
      case 500:
        return 'Server error. Please try again later.'
      case 502:
        return 'Bad gateway. Please try again later.'
      case 503:
        return 'Service unavailable. Please try again later.'
      default:
        return error.message
    }
  }

  if (error instanceof Error) {
    // Network errors
    if (error.message.includes('fetch')) {
      return 'Network error. Please check your connection.'
    }
    return error.message
  }

  return 'An unexpected error occurred.'
}

/**
 * Log API errors in development mode
 */
export function logApiError(error: unknown, context?: string): void {
  if (process.env.NODE_ENV === 'development') {
    console.error(`[API Error${context ? ` - ${context}` : ''}]:`, error)
  }
}