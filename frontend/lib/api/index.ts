/**
 * Central API module exports
 */

// Configuration
export { API_CONFIG } from './config'

// Main client and convenience functions
export { 
  ApiClient,
  sendMessage,
  createEventSource,
  downloadPdf
} from './client'

// Error handling
export { 
  ApiError,
  getErrorMessage,
  logApiError
} from './errors'

// Types
export type {
  ApiResponse,
  EventSourceParams,
  PdfDownloadResponse,
  MessageData,
  HealthCheckResponse,
  SessionType,
  ApiRequestConfig
} from './types'