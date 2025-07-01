import { ErrorInfo } from 'react'

interface ErrorLog {
  message: string
  stack?: string
  componentStack?: string
  timestamp: string
  url: string
  userAgent: string
  digest?: string
}

class ErrorLogger {
  private isDevelopment = process.env.NODE_ENV === 'development'

  logError(error: Error & { digest?: string }, errorInfo?: ErrorInfo) {
    const errorLog: ErrorLog = {
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo?.componentStack || undefined,
      timestamp: new Date().toISOString(),
      url: typeof window !== 'undefined' ? window.location.href : '',
      userAgent: typeof navigator !== 'undefined' ? navigator.userAgent : '',
      digest: error.digest,
    }

    // Always log to console in development
    if (this.isDevelopment) {
      console.group('🚨 Error logged')
      console.error('Error:', error)
      console.error('Error Info:', errorInfo)
      console.table(errorLog)
      console.groupEnd()
    }

    // In production, send to error reporting service
    if (!this.isDevelopment) {
      this.sendToErrorService(errorLog)
    }

    // Store in session storage for debugging
    this.storeErrorLocally(errorLog)
  }

  private sendToErrorService(errorLog: ErrorLog) {
    // TODO: Integrate with error reporting service like Sentry
    // For now, just log that we would send it
    console.log('Would send error to reporting service:', errorLog)
  }

  private storeErrorLocally(errorLog: ErrorLog) {
    if (typeof window === 'undefined') return

    try {
      const errors = this.getStoredErrors()
      errors.push(errorLog)
      
      // Keep only last 10 errors
      const recentErrors = errors.slice(-10)
      
      sessionStorage.setItem('re-frame-errors', JSON.stringify(recentErrors))
    } catch (e) {
      // Fail silently if storage is full or unavailable
      console.warn('Failed to store error locally:', e)
    }
  }

  getStoredErrors(): ErrorLog[] {
    if (typeof window === 'undefined') return []

    try {
      const stored = sessionStorage.getItem('re-frame-errors')
      return stored ? JSON.parse(stored) : []
    } catch {
      return []
    }
  }

  clearStoredErrors() {
    if (typeof window !== 'undefined') {
      sessionStorage.removeItem('re-frame-errors')
    }
  }
}

export const errorLogger = new ErrorLogger()
export type { ErrorLog }