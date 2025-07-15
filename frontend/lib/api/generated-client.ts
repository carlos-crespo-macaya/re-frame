/**
 * Wrapper around the generated API client
 * This provides a bridge between the generated code and our existing API patterns
 */

import { OpenAPI } from './generated/core/OpenAPI'
import { API_CONFIG } from './config'
import * as sdk from './generated/sdk.gen'
import type {
  MessageRequest,
  MessageResponse,
  SessionInfo,
  SessionListResponse,
  HealthCheckResponse,
  LanguageDetectionRequest,
  LanguageDetectionResponse,
} from './generated/types.gen'

// Configure the generated client with our API settings
OpenAPI.BASE = API_CONFIG.baseUrl
OpenAPI.HEADERS = API_CONFIG.defaultHeaders

/**
 * Type-safe API client using generated SDK
 */
export const generatedApi = {
  /**
   * Health check
   */
  health: {
    check: () => sdk.getHealthCheck(),
  },

  /**
   * Session management
   */
  sessions: {
    get: (sessionId: string) => sdk.getSessionInfo({ sessionId }),
    list: () => sdk.listSessions(),
    downloadPdf: (sessionId: string) => sdk.downloadPdf({ sessionId }),
  },

  /**
   * Messaging
   */
  messages: {
    send: (sessionId: string, requestBody: MessageRequest) =>
      sdk.sendMessage({ sessionId, requestBody }),
  },

  /**
   * Language detection
   */
  language: {
    detect: (requestBody: LanguageDetectionRequest) =>
      sdk.detectLanguage({ requestBody }),
  },

  /**
   * SSE Events (Note: EventSource is handled separately)
   */
  events: {
    // The generated client returns a promise, but SSE needs EventSource
    // This is just for type reference
    getEventStreamEndpoint: (sessionId: string, isAudio?: boolean, language?: string) =>
      `/api/events/${sessionId}?is_audio=${isAudio || false}&language=${language || 'en-US'}`,
  },
}

// Re-export types for convenience
export type {
  MessageRequest,
  MessageResponse,
  SessionInfo,
  SessionListResponse,
  HealthCheckResponse,
  LanguageDetectionRequest,
  LanguageDetectionResponse,
}

// Direct exports of SDK functions are removed to prevent fragility due to generator changes.
// Use the `generatedApi` wrapper for accessing SDK functionality instead.