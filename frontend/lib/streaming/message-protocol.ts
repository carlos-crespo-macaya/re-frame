/**
 * Message protocol types for SSE streaming communication
 */

export type MimeType = 'text/plain' | 'audio/pcm';
export type MessageType = 'thought' | 'response' | 'transcription' | 'error' | 'status';
export type ConnectionState = 'connecting' | 'connected' | 'disconnected' | 'error';

/**
 * Base message structure for client-server communication
 */
export interface BaseMessage {
  mime_type: MimeType;
  data: string;
  message_type: MessageType;
  session_id: string;
  timestamp?: number;
}

/**
 * Message sent from client to server
 */
export interface ClientMessage extends BaseMessage {
  turn_complete?: boolean;
  interrupted?: boolean;
}

/**
 * Message received from server via SSE
 */
export interface ServerMessage extends BaseMessage {
  chunk_id?: string;
  is_final?: boolean;
}

/**
 * Error message structure
 */
export interface ErrorMessage {
  message_type: 'error';
  error_code: string;
  error_message: string;
  session_id: string;
  timestamp: number;
}

/**
 * Status message for connection state
 */
export interface StatusMessage {
  message_type: 'status';
  status: ConnectionState;
  session_id: string;
  timestamp: number;
}

/**
 * Audio configuration for streaming
 */
export interface AudioStreamConfig {
  sampleRate: number;
  channels: number;
  bitDepth: number;
  bufferInterval: number;
}

/**
 * SSE event data wrapper
 */
export interface SSEEventData {
  type: 'message' | 'error' | 'status' | 'ping';
  data: ServerMessage | ErrorMessage | StatusMessage;
}

/**
 * Type guards
 */
export function isServerMessage(data: any): data is ServerMessage {
  if (!data || typeof data !== 'object') {
    return false;
  }
  
  return (
    'mime_type' in data &&
    'data' in data &&
    'message_type' in data &&
    'session_id' in data
  );
}

export function isErrorMessage(data: any): data is ErrorMessage {
  return (
    data &&
    typeof data === 'object' &&
    data.message_type === 'error' &&
    'error_code' in data &&
    'error_message' in data
  );
}

export function isStatusMessage(data: any): data is StatusMessage {
  return (
    data &&
    typeof data === 'object' &&
    data.message_type === 'status' &&
    'status' in data &&
    'session_id' in data
  );
}

/**
 * Create a client message
 */
export function createClientMessage(params: {
  mimeType: MimeType;
  data: string;
  messageType: MessageType;
  sessionId: string;
  turnComplete?: boolean;
  interrupted?: boolean;
}): ClientMessage {
  return {
    mime_type: params.mimeType,
    data: params.data,
    message_type: params.messageType,
    session_id: params.sessionId,
    timestamp: Date.now(),
    turn_complete: params.turnComplete,
    interrupted: params.interrupted
  };
}

/**
 * Default audio configuration
 */
export const DEFAULT_AUDIO_CONFIG: AudioStreamConfig = {
  sampleRate: 16000,
  channels: 1,
  bitDepth: 16,
  bufferInterval: 200
};