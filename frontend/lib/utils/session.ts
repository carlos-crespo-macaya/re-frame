/**
 * Centralized session management utilities
 */

import { v4 as uuidv4 } from 'uuid'

/**
 * Generate a unique session ID with optional prefix
 */
export function generateSessionId(prefix?: string): string {
  const id = uuidv4()
  return prefix ? `${prefix}-${id}` : id
}

/**
 * Generate a session ID for audio conversations
 */
export function generateAudioSessionId(): string {
  return generateSessionId('audio')
}

/**
 * Generate a session ID for text conversations
 */
export function generateTextSessionId(): string {
  return generateSessionId('text')
}

/**
 * Extract session type from session ID
 */
export function getSessionType(sessionId: string): 'audio' | 'text' | 'unknown' {
  if (sessionId.startsWith('audio-')) return 'audio'
  if (sessionId.startsWith('text-')) return 'text'
  return 'unknown'
}

/**
 * Validate session ID format
 */
export function isValidSessionId(sessionId: string): boolean {
  // UUID v4 format with optional prefix
  const uuidRegex = /^(?:[\w-]+-)?[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i
  return uuidRegex.test(sessionId)
}