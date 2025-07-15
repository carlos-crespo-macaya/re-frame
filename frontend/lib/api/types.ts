/**
 * Type definitions for API operations
 */

import { ClientMessage, ServerMessage } from '../streaming/message-protocol'

/**
 * Generic API response wrapper
 */
export interface ApiResponse<T> {
  data: T
  status: number
  headers: Headers
}

/**
 * Parameters for creating EventSource connections
 */
export interface EventSourceParams {
  is_audio?: boolean
  language?: string
  [key: string]: string | boolean | number | undefined
}

/**
 * PDF download response
 */
export interface PdfDownloadResponse {
  blob: Blob
  filename: string
}

/**
 * Health check response
 */
export interface HealthCheckResponse {
  status: 'healthy' | 'unhealthy'
  service: string
  timestamp: string
  environment: string
  apiUrl: string
}

/**
 * Re-export message types for convenience
 */
export type { ClientMessage, ServerMessage }

/**
 * Type alias for message data sent to the API
 */
export type MessageData = ClientMessage

/**
 * Session types
 */
export type SessionType = 'text' | 'audio'

/**
 * API request configuration
 */
export interface ApiRequestConfig extends RequestInit {
  timeout?: number
  retries?: number
  retryDelay?: number
}