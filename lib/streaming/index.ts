/**
 * Streaming module exports for real-time communication
 */

// SSE Client
export { SSEClient, type SSEClientOptions } from './sse-client';

// Session Management
export { 
  SessionManager, 
  sessionManager,
  type Session 
} from './session-manager';

// Message Protocol
export {
  type MimeType,
  type MessageType,
  type ConnectionState,
  type BaseMessage,
  type ClientMessage,
  type ServerMessage,
  type ErrorMessage,
  type StatusMessage,
  type AudioStreamConfig,
  type SSEEventData,
  isServerMessage,
  isErrorMessage,
  isStatusMessage,
  createClientMessage,
  DEFAULT_AUDIO_CONFIG
} from './message-protocol';

// Streaming Utilities
export {
  textToPCM,
  pcmToText,
  encodePCM,
  decodePCM,
  chunkMessage,
  MessageAssembler,
  RateLimiter,
  createReconnectingClient
} from './streaming-utils';