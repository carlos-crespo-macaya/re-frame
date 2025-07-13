import { 
  AUDIO_CONFIG, 
  getRecordingConfig, 
  getPlaybackConfig,
  validateAudioConfig 
} from '../audio-config';

describe('Audio Configuration', () => {
  describe('AUDIO_CONFIG', () => {
    it('should have valid recording configuration', () => {
      expect(AUDIO_CONFIG.recording).toBeDefined();
      expect(AUDIO_CONFIG.recording.sampleRate).toBe(16000);
      expect(AUDIO_CONFIG.recording.channels).toBe(1);
      expect(AUDIO_CONFIG.recording.bitDepth).toBe(16);
      expect(AUDIO_CONFIG.recording.bufferInterval).toBe(200);
    });

    it('should have valid playback configuration', () => {
      expect(AUDIO_CONFIG.playback).toBeDefined();
      expect(AUDIO_CONFIG.playback.sampleRate).toBe(24000);
      expect(AUDIO_CONFIG.playback.channels).toBe(1);
      expect(AUDIO_CONFIG.playback.bufferSize).toBe(180);
    });

    it('should have valid worklet configuration', () => {
      expect(AUDIO_CONFIG.worklets).toBeDefined();
      expect(AUDIO_CONFIG.worklets.recorderPath).toBe('/worklets/audio-recorder-processor.js');
      expect(AUDIO_CONFIG.worklets.playerPath).toBe('/worklets/noise-gate-processor.js');
      expect(AUDIO_CONFIG.worklets.processorPath).toBe('/worklets/noise-gate-processor.js');
    });

    it('should have valid constraints configuration', () => {
      expect(AUDIO_CONFIG.constraints).toBeDefined();
      expect(AUDIO_CONFIG.constraints.maxRecordingDuration).toBe(300000); // 5 minutes
      expect(AUDIO_CONFIG.constraints.minBufferSize).toBe(128);
      expect(AUDIO_CONFIG.constraints.maxBufferSize).toBe(4096);
    });
  });

  describe('getRecordingConfig', () => {
    it('should return recording configuration', () => {
      const config = getRecordingConfig();
      expect(config).toEqual(AUDIO_CONFIG.recording);
    });

    it('should return a copy, not a reference', () => {
      const config1 = getRecordingConfig();
      const config2 = getRecordingConfig();
      expect(config1).not.toBe(config2);
      expect(config1).toEqual(config2);
    });
  });

  describe('getPlaybackConfig', () => {
    it('should return playback configuration', () => {
      const config = getPlaybackConfig();
      expect(config).toEqual(AUDIO_CONFIG.playback);
    });

    it('should return a copy, not a reference', () => {
      const config1 = getPlaybackConfig();
      const config2 = getPlaybackConfig();
      expect(config1).not.toBe(config2);
      expect(config1).toEqual(config2);
    });
  });

  describe('validateAudioConfig', () => {
    it('should validate valid recording config', () => {
      const validConfig = {
        sampleRate: 16000,
        channels: 1,
        bitDepth: 16,
        bufferInterval: 200
      };
      expect(() => validateAudioConfig('recording', validConfig)).not.toThrow();
    });

    it('should validate valid playback config', () => {
      const validConfig = {
        sampleRate: 24000,
        channels: 1,
        bufferSize: 180
      };
      expect(() => validateAudioConfig('playback', validConfig)).not.toThrow();
    });

    it('should throw on invalid sample rate', () => {
      const invalidConfig = {
        sampleRate: -1,
        channels: 1,
        bitDepth: 16,
        bufferInterval: 200
      };
      expect(() => validateAudioConfig('recording', invalidConfig))
        .toThrow('Invalid sample rate: -1');
    });

    it('should throw on invalid channel count', () => {
      const invalidConfig = {
        sampleRate: 16000,
        channels: 0,
        bitDepth: 16,
        bufferInterval: 200
      };
      expect(() => validateAudioConfig('recording', invalidConfig))
        .toThrow('Invalid channel count: 0');
    });

    it('should throw on invalid bit depth', () => {
      const invalidConfig = {
        sampleRate: 16000,
        channels: 1,
        bitDepth: 7,
        bufferInterval: 200
      };
      expect(() => validateAudioConfig('recording', invalidConfig))
        .toThrow('Invalid bit depth: 7');
    });

    it('should throw on missing required fields', () => {
      const invalidConfig = {
        sampleRate: 16000,
        channels: 1
      };
      expect(() => validateAudioConfig('recording', invalidConfig as any))
        .toThrow('Missing required field: bitDepth');
    });
  });
});