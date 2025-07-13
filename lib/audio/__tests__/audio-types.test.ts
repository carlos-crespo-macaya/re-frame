import {
  AudioMode,
  MicPermissionState,
  AudioState,
  AudioMessage,
  AudioSessionConfig,
  isValidAudioMode,
  isValidMimeType,
  createDefaultAudioState,
  createAudioMessage,
  validateAudioMessage
} from '../audio-types';

describe('Audio Types', () => {
  describe('Type Guards', () => {
    describe('isValidAudioMode', () => {
      it('should return true for valid audio modes', () => {
        expect(isValidAudioMode('review')).toBe(true);
        expect(isValidAudioMode('conversation')).toBe(true);
      });

      it('should return false for invalid audio modes', () => {
        expect(isValidAudioMode('invalid')).toBe(false);
        expect(isValidAudioMode('')).toBe(false);
        expect(isValidAudioMode(null as any)).toBe(false);
        expect(isValidAudioMode(undefined as any)).toBe(false);
      });
    });

    describe('isValidMimeType', () => {
      it('should return true for valid mime types', () => {
        expect(isValidMimeType('text/plain')).toBe(true);
        expect(isValidMimeType('audio/pcm')).toBe(true);
      });

      it('should return false for invalid mime types', () => {
        expect(isValidMimeType('audio/mp3')).toBe(false);
        expect(isValidMimeType('video/mp4')).toBe(false);
        expect(isValidMimeType('')).toBe(false);
      });
    });
  });

  describe('Factory Functions', () => {
    describe('createDefaultAudioState', () => {
      it('should create default audio state', () => {
        const state = createDefaultAudioState();
        
        expect(state.isRecording).toBe(false);
        expect(state.isPlaying).toBe(false);
        expect(state.audioEnabled).toBe(false);
        expect(state.micPermission).toBe('prompt');
        expect(state.transcription).toBe('');
        expect(state.audioLevel).toBe(0);
        expect(state.mode).toBe('review');
        expect(state.error).toBeNull();
      });
    });

    describe('createAudioMessage', () => {
      it('should create text message', () => {
        const message = createAudioMessage({
          mimeType: 'text/plain',
          data: 'Hello world',
          sessionId: 'test-session',
          messageType: 'thought'
        });

        expect(message.mime_type).toBe('text/plain');
        expect(message.data).toBe('Hello world');
        expect(message.session_id).toBe('test-session');
        expect(message.message_type).toBe('thought');
        expect(message.turn_complete).toBeUndefined();
        expect(message.interrupted).toBeUndefined();
      });

      it('should create audio message with optional fields', () => {
        const message = createAudioMessage({
          mimeType: 'audio/pcm',
          data: 'base64-audio-data',
          sessionId: 'test-session',
          messageType: 'response',
          turnComplete: true,
          interrupted: false
        });

        expect(message.mime_type).toBe('audio/pcm');
        expect(message.data).toBe('base64-audio-data');
        expect(message.session_id).toBe('test-session');
        expect(message.message_type).toBe('response');
        expect(message.turn_complete).toBe(true);
        expect(message.interrupted).toBe(false);
      });
    });
  });

  describe('Validation Functions', () => {
    describe('validateAudioMessage', () => {
      it('should validate valid text message', () => {
        const message: AudioMessage = {
          mime_type: 'text/plain',
          data: 'Hello',
          session_id: 'test-123',
          message_type: 'thought'
        };

        expect(() => validateAudioMessage(message)).not.toThrow();
      });

      it('should validate valid audio message', () => {
        const message: AudioMessage = {
          mime_type: 'audio/pcm',
          data: 'base64data',
          session_id: 'test-123',
          message_type: 'transcription',
          turn_complete: true
        };

        expect(() => validateAudioMessage(message)).not.toThrow();
      });

      it('should throw on invalid mime type', () => {
        const message = {
          mime_type: 'invalid/type',
          data: 'data',
          session_id: 'test',
          message_type: 'thought'
        } as any;

        expect(() => validateAudioMessage(message))
          .toThrow('Invalid mime type: invalid/type');
      });

      it('should throw on missing session ID', () => {
        const message = {
          mime_type: 'text/plain',
          data: 'data',
          message_type: 'thought'
        } as any;

        expect(() => validateAudioMessage(message))
          .toThrow('Session ID is required');
      });

      it('should throw on empty data', () => {
        const message = {
          mime_type: 'text/plain',
          data: '',
          session_id: 'test',
          message_type: 'thought'
        } as any;

        expect(() => validateAudioMessage(message))
          .toThrow('Message data cannot be empty');
      });

      it('should throw on invalid message type', () => {
        const message = {
          mime_type: 'text/plain',
          data: 'data',
          session_id: 'test',
          message_type: 'invalid'
        } as any;

        expect(() => validateAudioMessage(message))
          .toThrow('Invalid message type: invalid');
      });
    });
  });

  describe('Type Definitions', () => {
    it('should enforce AudioMode type', () => {
      const validMode: AudioMode = 'review';
      const validMode2: AudioMode = 'conversation';
      
      expect(validMode).toBe('review');
      expect(validMode2).toBe('conversation');
    });

    it('should enforce MicPermissionState type', () => {
      const granted: MicPermissionState = 'granted';
      const denied: MicPermissionState = 'denied';
      const prompt: MicPermissionState = 'prompt';
      
      expect(granted).toBe('granted');
      expect(denied).toBe('denied');
      expect(prompt).toBe('prompt');
    });

    it('should enforce AudioState structure', () => {
      const state: AudioState = {
        isRecording: true,
        isPlaying: false,
        audioEnabled: true,
        micPermission: 'granted',
        transcription: 'Test transcription',
        audioLevel: 0.5,
        mode: 'conversation',
        error: null
      };

      expect(state.isRecording).toBe(true);
      expect(state.mode).toBe('conversation');
    });

    it('should enforce AudioSessionConfig structure', () => {
      const config: AudioSessionConfig = {
        sessionId: 'session-123',
        mode: 'review',
        autoSend: false,
        enableTranscription: true,
        maxDuration: 300000
      };

      expect(config.sessionId).toBe('session-123');
      expect(config.mode).toBe('review');
    });
  });
});