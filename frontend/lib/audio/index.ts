/**
 * Audio module exports for re-frame.social
 */

// Configuration exports
export {
  AUDIO_CONFIG,
  getRecordingConfig,
  getPlaybackConfig,
  validateAudioConfig,
  type RecordingConfig,
  type PlaybackConfig,
  type WorkletConfig,
  type ConstraintsConfig,
  type AudioConfiguration
} from './audio-config';

// Type exports
export {
  type AudioMode,
  type MicPermissionState,
  type MessageType,
  type MimeType,
  type AudioState,
  type AudioMessage,
  type AudioSessionConfig,
  type AudioEvents,
  isValidAudioMode,
  isValidMimeType,
  createDefaultAudioState,
  createAudioMessage,
  validateAudioMessage
} from './audio-types';

// Utility exports
export {
  arrayBufferToBase64,
  base64ToArrayBuffer,
  float32ToPcm16,
  pcm16ToFloat32,
  generateSessionId,
  calculateAudioLevel,
  formatDuration,
  debounce,
  throttle,
  isAudioSupported,
  getAudioConstraints
} from './audio-utils';

// Audio recorder exports
export {
  AudioRecorder,
  type AudioRecorderOptions,
  type AudioRecorderCallbacks
} from './audio-recorder';

// React hooks
export {
  useAudioRecorder,
  type UseAudioRecorderOptions,
  type AudioRecorderState
} from './use-audio-recorder';

// Debug utilities
export {
  AudioDebugger,
  audioDebugConsole,
  runAudioDiagnostics,
  type AudioDebugInfo,
  type AudioLevelInfo,
  type DeviceInfo
} from './audio-debug';