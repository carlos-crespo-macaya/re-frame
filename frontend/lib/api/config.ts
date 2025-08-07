/**
 * Central API configuration for the frontend application.
 * All API endpoints and settings should be defined here.
 */

export const API_CONFIG = {
  // Use relative paths to go through our proxy route
  baseUrl: '/api/proxy',
  endpoints: {
    send: (sessionId: string) => `/api/proxy/api/send/${sessionId}`,
    events: (sessionId: string) => `/api/proxy/api/events/${sessionId}`,
    pdf: (sessionId: string) => `/api/proxy/pdf/${sessionId}`,
    health: '/api/proxy/api/health',
    // Voice endpoints
    createVoiceSession: '/api/proxy/api/voice/sessions',
    voiceStream: (sessionId: string) => `/api/proxy/api/voice/sessions/${sessionId}/stream`,
    sendVoiceAudio: (sessionId: string) => `/api/proxy/api/voice/sessions/${sessionId}/audio`
  },
  defaultHeaders: {
    'Content-Type': 'application/json'
  },
  timeouts: {
    default: 30000, // 30 seconds
    upload: 60000   // 60 seconds for file uploads
  }
} as const

export type ApiEndpoints = typeof API_CONFIG.endpoints
