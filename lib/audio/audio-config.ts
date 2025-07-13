/**
 * Audio configuration for re-frame.social
 * Defines all audio-related settings and constraints
 */

export interface RecordingConfig {
  sampleRate: number;
  channels: number;
  bitDepth: number;
  bufferInterval: number;
}

export interface PlaybackConfig {
  sampleRate: number;
  channels: number;
  bufferSize: number;
}

export interface WorkletConfig {
  recorderPath: string;
  playerPath: string;
  processorPath: string;
}

export interface ConstraintsConfig {
  maxRecordingDuration: number;
  minBufferSize: number;
  maxBufferSize: number;
}

export interface AudioConfiguration {
  recording: RecordingConfig;
  playback: PlaybackConfig;
  worklets: WorkletConfig;
  constraints: ConstraintsConfig;
}

export const AUDIO_CONFIG: AudioConfiguration = {
  recording: {
    sampleRate: 16000,    // 16kHz for recording
    channels: 1,          // Mono
    bitDepth: 16,         // 16-bit PCM
    bufferInterval: 200   // 200ms buffer chunks
  },
  playback: {
    sampleRate: 24000,    // 24kHz for playback
    channels: 1,          // Mono
    bufferSize: 180       // 180 seconds ring buffer
  },
  worklets: {
    recorderPath: '/worklets/audio-recorder-processor.js',
    playerPath: '/worklets/noise-gate-processor.js',
    processorPath: '/worklets/noise-gate-processor.js'
  },
  constraints: {
    maxRecordingDuration: 300000,  // 5 minutes max recording
    minBufferSize: 128,
    maxBufferSize: 4096
  }
};

/**
 * Get a copy of the recording configuration
 */
export function getRecordingConfig(): RecordingConfig {
  return { ...AUDIO_CONFIG.recording };
}

/**
 * Get a copy of the playback configuration
 */
export function getPlaybackConfig(): PlaybackConfig {
  return { ...AUDIO_CONFIG.playback };
}

/**
 * Validate audio configuration
 * @throws Error if configuration is invalid
 */
export function validateAudioConfig(
  type: 'recording' | 'playback',
  config: Partial<RecordingConfig | PlaybackConfig>
): void {
  if (type === 'recording') {
    const recordingConfig = config as Partial<RecordingConfig>;
    
    if (recordingConfig.sampleRate !== undefined && recordingConfig.sampleRate <= 0) {
      throw new Error(`Invalid sample rate: ${recordingConfig.sampleRate}`);
    }
    
    if (recordingConfig.channels !== undefined && recordingConfig.channels <= 0) {
      throw new Error(`Invalid channel count: ${recordingConfig.channels}`);
    }
    
    if (recordingConfig.bitDepth !== undefined && 
        ![8, 16, 24, 32].includes(recordingConfig.bitDepth)) {
      throw new Error(`Invalid bit depth: ${recordingConfig.bitDepth}`);
    }
    
    // Check required fields for full config
    if ('sampleRate' in config && 'channels' in config && 
        'bitDepth' in config && 'bufferInterval' in config) {
      const fullConfig = config as RecordingConfig;
      if (!fullConfig.bitDepth) {
        throw new Error('Missing required field: bitDepth');
      }
      if (!fullConfig.bufferInterval) {
        throw new Error('Missing required field: bufferInterval');
      }
    } else if (type === 'recording') {
      // Check if any required field is missing when validating a partial config
      const requiredFields = ['sampleRate', 'channels', 'bitDepth', 'bufferInterval'];
      for (const field of requiredFields) {
        if (!(field in config)) {
          throw new Error(`Missing required field: ${field}`);
        }
      }
    }
  } else {
    const playbackConfig = config as Partial<PlaybackConfig>;
    
    if (playbackConfig.sampleRate !== undefined && playbackConfig.sampleRate <= 0) {
      throw new Error(`Invalid sample rate: ${playbackConfig.sampleRate}`);
    }
    
    if (playbackConfig.channels !== undefined && playbackConfig.channels <= 0) {
      throw new Error(`Invalid channel count: ${playbackConfig.channels}`);
    }
    
    if (playbackConfig.bufferSize !== undefined && playbackConfig.bufferSize <= 0) {
      throw new Error(`Invalid buffer size: ${playbackConfig.bufferSize}`);
    }
  }
}