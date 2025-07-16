/**
 * Wrapper around the generated API client
 * This provides a bridge between the generated code and our existing API patterns
 */

import { OpenAPI } from './generated/core/OpenAPI'
import { API_CONFIG } from './config'
import {
  getHealthCheck,
  getSessionInfo,
  listSessions,
  downloadPdf,
  sendMessage,
  detectLanguage,
  getEventStream,
} from './generated/sdk.gen.js'
import type {
  MessageRequest,
  MessageResponse,
  SessionInfo,
  SessionListResponse,
  HealthCheckResponse,
  LanguageDetectionRequest,
  LanguageDetectionResponse,
} from './generated/types.gen.js'

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
    check: () => getHealthCheck(),
  },

  /**
   * Session management
   */
  sessions: {
    get: (sessionId: string) => getSessionInfo({ sessionId }),
    list: () => listSessions(),
    downloadPdf: (sessionId: string) => downloadPdf({ sessionId }),
  },

  /**
   * Messaging
   */
  messages: {
    send: (sessionId: string, requestBody: MessageRequest) =>
      sendMessage({ sessionId, requestBody }),
  },

  /**
   * Language detection
   */
  language: {
    detect: (requestBody: LanguageDetectionRequest) =>
      detectLanguage({ requestBody }),
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

// Direct exports of SDK functions (getHealthCheck, sendMessage, etc.) were removed
// because they can break when the OpenAPI generator changes function names or signatures.
// The `generatedApi` wrapper pattern provides a stable API surface that won't break
// when the underlying generated code changes, ensuring better maintainability.