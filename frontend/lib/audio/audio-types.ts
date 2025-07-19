/**
 * Type definitions for audio functionality in re-frame.social
 */

export type AudioMode = 'instant' | 'manual';
export type MicPermissionState = 'granted' | 'denied' | 'prompt' | 'checking';
export type MessageType = 'thought' | 'response' | 'transcription';
export type MimeType = 'text/plain' | 'audio/pcm';

/**
 * Audio state management interface
 */
export interface AudioState {
  isRecording: boolean;
  isPlaying: boolean;
  isProcessing: boolean;
  audioEnabled: boolean;
  micPermission: MicPermissionState;
  audioLevel: number;
  mode: AudioMode;
  error: Error | null;
}

/**
 * Message protocol for SSE communication
 */
export interface AudioMessage {
  mime_type: MimeType;
  data: string;
  message_type: MessageType;
  session_id: string;
  turn_complete?: boolean;
  interrupted?: boolean;
}

/**
 * Audio session configuration
 */
export interface AudioSessionConfig {
  sessionId: string;
  mode: AudioMode;
  autoSend: boolean;
  enableTranscription: boolean;
  maxDuration: number;
}

/**
 * Audio event types
 */
export interface AudioEvents {
  onRecordingStart: () => void;
  onRecordingStop: () => void;
  onTranscription: (text: string) => void;
  onAudioLevel: (level: number) => void;
  onError: (error: Error) => void;
  onModeChange: (mode: AudioMode) => void;
  onPlaybackStart: () => void;
  onPlaybackEnd: () => void;
}

/**
 * Type guard for AudioMode
 */
export function isValidAudioMode(mode: unknown): mode is AudioMode {
  return mode === 'instant' || mode === 'manual';
}

/**
 * Type guard for MimeType
 */
export function isValidMimeType(type: unknown): type is MimeType {
  return type === 'text/plain' || type === 'audio/pcm';
}

/**
 * Create default audio state
 */
export function createDefaultAudioState(): AudioState {
  return {
    isRecording: false,
    isPlaying: false,
    isProcessing: false,
    audioEnabled: false,
    micPermission: 'prompt',
    audioLevel: 0,
    mode: 'instant',
    error: null
  };
}

/**
 * Create audio message
 */
export function createAudioMessage(params: {
  mimeType: MimeType;
  data: string;
  sessionId: string;
  messageType: MessageType;
  turnComplete?: boolean;
  interrupted?: boolean;
}): AudioMessage {
  return {
    mime_type: params.mimeType,
    data: params.data,
    session_id: params.sessionId,
    message_type: params.messageType,
    ...(params.turnComplete !== undefined && { turn_complete: params.turnComplete }),
    ...(params.interrupted !== undefined && { interrupted: params.interrupted })
  };
}

/**
 * Validate audio message
 * @throws Error if message is invalid
 */
export function validateAudioMessage(message: AudioMessage): void {
  if (!isValidMimeType(message.mime_type)) {
    throw new Error(`Invalid mime type: ${message.mime_type}`);
  }
  
  if (!message.session_id) {
    throw new Error('Session ID is required');
  }
  
  if (!message.data) {
    throw new Error('Message data cannot be empty');
  }
  
  const validMessageTypes: MessageType[] = ['thought', 'response', 'transcription'];
  if (!validMessageTypes.includes(message.message_type)) {
    throw new Error(`Invalid message type: ${message.message_type}`);
  }
}