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
  createVoiceSessionApiVoiceSessionsPost,
  sendAudioChunkApiVoiceSessionsSessionIdAudioPost,
  voiceControlApiVoiceSessionsSessionIdControlPost,
  endVoiceSessionApiVoiceSessionsSessionIdDelete,
} from './generated/sdk.gen'
import type {
  MessageRequest,
  MessageResponse,
  SessionInfo,
  SessionListResponse,
  HealthCheckResponse,
  LanguageDetectionRequest,
  LanguageDetectionResponse,
  CreateVoiceSessionRequest,
  VoiceSessionResponse,
  AudioChunkRequest,
  VoiceControlRequest,
} from './generated/types.gen'

// Configure the generated client with our API settings
// Use relative path to go through our proxy route
OpenAPI.BASE = '/api/proxy'
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
   * Voice endpoints
   */
  voice: {
    createSession: (requestBody: CreateVoiceSessionRequest) =>
      createVoiceSessionApiVoiceSessionsPost({ requestBody }),
    sendAudio: (sessionId: string, requestBody: AudioChunkRequest) =>
      sendAudioChunkApiVoiceSessionsSessionIdAudioPost({ sessionId, requestBody }),
    sendControl: (sessionId: string, requestBody: VoiceControlRequest) =>
      voiceControlApiVoiceSessionsSessionIdControlPost({ sessionId, requestBody }),
    endSession: (sessionId: string) =>
      endVoiceSessionApiVoiceSessionsSessionIdDelete({ sessionId }),
    // Voice SSE stream endpoint (EventSource handled separately)
    getStreamEndpoint: (sessionId: string) =>
      `/api/voice/sessions/${sessionId}/stream`,
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
  CreateVoiceSessionRequest,
  VoiceSessionResponse,
  AudioChunkRequest,
  VoiceControlRequest,
}

// Direct exports of SDK functions (getHealthCheck, sendMessage, etc.) were removed
// because they can break when the OpenAPI generator changes function names or signatures.
// The `generatedApi` wrapper pattern provides a stable API surface that won't break
// when the underlying generated code changes, ensuring better maintainability.
