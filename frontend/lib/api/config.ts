/**
 * Central API configuration for the frontend application.
 * All API endpoints and settings should be defined here.
 */

export const API_CONFIG = {
  baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  endpoints: {
    send: (sessionId: string) => `/api/send/${sessionId}`,
    events: (sessionId: string) => `/api/events/${sessionId}`,
    pdf: (sessionId: string) => `/pdf/${sessionId}`,
    health: '/api/health',
    // Voice endpoints
    createVoiceSession: '/api/voice/sessions',
    voiceStream: (sessionId: string) => `/api/voice/sessions/${sessionId}/stream`,
    sendVoiceAudio: (sessionId: string) => `/api/voice/sessions/${sessionId}/audio`
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