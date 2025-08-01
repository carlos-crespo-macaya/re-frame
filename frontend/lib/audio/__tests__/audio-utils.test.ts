import {
  base64ToArrayBuffer,
  arrayBufferToBase64,
  float32ToPcm16,
  pcm16ToFloat32,
  generateSessionId,
  calculateAudioLevel,
  formatDuration,
  debounce,
  throttle,
  isAudioSupported,
  getAudioConstraints
} from '../audio-utils';

// Setup browser-like environment for tests
beforeEach(() => {
  // @ts-expect-error - mocking window object for tests
  global.window = {
    btoa: (str: string) => Buffer.from(str, 'binary').toString('base64'),
    atob: (str: string) => Buffer.from(str, 'base64').toString('binary')
  };
});

afterEach(() => {
  // Clean up any global mocks
  delete (global as any).window;
  delete (global as any).navigator;
});

describe('Audio Utilities', () => {
  describe('Base64 Conversion', () => {
    describe('arrayBufferToBase64', () => {
      it('should convert ArrayBuffer to base64', () => {
        const buffer = new ArrayBuffer(4);
        const view = new Uint8Array(buffer);
        view[0] = 72; // H
        view[1] = 101; // e
        view[2] = 108; // l
        view[3] = 108; // l

        const result = arrayBufferToBase64(buffer);
        expect(result).toBe('SGVsbA==');
      });

      it('should handle empty buffer', () => {
        const buffer = new ArrayBuffer(0);
        const result = arrayBufferToBase64(buffer);
        expect(result).toBe('');
      });

      it('should handle large buffer', () => {
        const buffer = new ArrayBuffer(1024);
        const view = new Uint8Array(buffer);
        for (let i = 0; i < 1024; i++) {
          view[i] = i % 256;
        }

        const result = arrayBufferToBase64(buffer);
        expect(result).toBeTruthy();
        expect(result.length).toBeGreaterThan(1024);
      });
    });

    describe('base64ToArrayBuffer', () => {
      it('should convert base64 to ArrayBuffer', () => {
        const base64 = 'SGVsbA==';
        const buffer = base64ToArrayBuffer(base64);
        const view = new Uint8Array(buffer);

        expect(view.length).toBe(4);
        expect(view[0]).toBe(72); // H
        expect(view[1]).toBe(101); // e
        expect(view[2]).toBe(108); // l
        expect(view[3]).toBe(108); // l
      });

      it('should handle empty string', () => {
        const buffer = base64ToArrayBuffer('');
        expect(buffer.byteLength).toBe(0);
      });

      it('should throw on invalid base64', () => {
        expect(() => base64ToArrayBuffer('invalid!@#$'))
          .toThrow();
      });
    });

    it('should be reversible', () => {
      const original = new ArrayBuffer(100);
      const view = new Uint8Array(original);
      for (let i = 0; i < 100; i++) {
        view[i] = Math.floor(Math.random() * 256);
      }

      const base64 = arrayBufferToBase64(original);
      const decoded = base64ToArrayBuffer(base64);
      const decodedView = new Uint8Array(decoded);

      expect(decodedView.length).toBe(view.length);
      for (let i = 0; i < view.length; i++) {
        expect(decodedView[i]).toBe(view[i]);
      }
    });
  });

  describe('Audio Format Conversion', () => {
    describe('float32ToPcm16', () => {
      it('should convert Float32 to 16-bit PCM', () => {
        const float32 = new Float32Array([0, 0.5, 1, -0.5, -1]);
        const pcm16 = float32ToPcm16(float32);

        expect(pcm16).toBeInstanceOf(Int16Array);
        expect(pcm16.length).toBe(5);
        expect(pcm16[0]).toBe(0);
        expect(pcm16[1]).toBeCloseTo(16383, -1);
        expect(pcm16[2]).toBe(32767);
        expect(pcm16[3]).toBeCloseTo(-16384, -1);
        expect(pcm16[4]).toBe(-32768);
      });

      it('should clamp values outside range', () => {
        const float32 = new Float32Array([2, -2, 1.5, -1.5]);
        const pcm16 = float32ToPcm16(float32);

        expect(pcm16[0]).toBe(32767); // Clamped to max
        expect(pcm16[1]).toBe(-32768); // Clamped to min
        expect(pcm16[2]).toBe(32767); // Clamped to max
        expect(pcm16[3]).toBe(-32768); // Clamped to min
      });

      it('should handle empty array', () => {
        const float32 = new Float32Array(0);
        const pcm16 = float32ToPcm16(float32);

        expect(pcm16.length).toBe(0);
      });
    });

    describe('pcm16ToFloat32', () => {
      it('should convert 16-bit PCM to Float32', () => {
        const pcm16 = new Int16Array([0, 16383, 32767, -16384, -32768]);
        const float32 = pcm16ToFloat32(pcm16);

        expect(float32).toBeInstanceOf(Float32Array);
        expect(float32.length).toBe(5);
        expect(float32[0]).toBe(0);
        expect(float32[1]).toBeCloseTo(0.5, 2);
        expect(float32[2]).toBeCloseTo(1, 2);
        expect(float32[3]).toBeCloseTo(-0.5, 2);
        expect(float32[4]).toBe(-1);
      });

      it('should handle empty array', () => {
        const pcm16 = new Int16Array(0);
        const float32 = pcm16ToFloat32(pcm16);

        expect(float32.length).toBe(0);
      });
    });

    it('should be reversible within precision limits', () => {
      const original = new Float32Array(100);
      for (let i = 0; i < 100; i++) {
        original[i] = (Math.random() * 2) - 1; // Range -1 to 1
      }

      const pcm16 = float32ToPcm16(original);
      const converted = pcm16ToFloat32(pcm16);

      expect(converted.length).toBe(original.length);
      for (let i = 0; i < original.length; i++) {
        expect(converted[i]).toBeCloseTo(original[i], 2);
      }
    });
  });

  describe('Session Management', () => {
    describe('generateSessionId', () => {
      it('should generate unique session IDs', () => {
        const id1 = generateSessionId();
        const id2 = generateSessionId();

        expect(id1).toBeTruthy();
        expect(id2).toBeTruthy();
        expect(id1).not.toBe(id2);
      });

      it('should generate IDs with correct format', () => {
        const id = generateSessionId();
        
        expect(id).toMatch(/^[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}$/);
      });

      it('should generate many unique IDs', () => {
        const ids = new Set<string>();
        for (let i = 0; i < 1000; i++) {
          ids.add(generateSessionId());
        }

        expect(ids.size).toBe(1000);
      });
    });
  });

  describe('Audio Analysis', () => {
    describe('calculateAudioLevel', () => {
      it('should calculate RMS level for audio samples', () => {
        const silence = new Float32Array(100).fill(0);
        const level = calculateAudioLevel(silence);
        expect(level).toBe(0);
      });

      it('should calculate level for sine wave', () => {
        const samples = new Float32Array(100);
        for (let i = 0; i < 100; i++) {
          samples[i] = Math.sin((i / 100) * Math.PI * 2);
        }
        const level = calculateAudioLevel(samples);
        expect(level).toBeGreaterThan(0);
        expect(level).toBeLessThanOrEqual(1);
      });

      it('should calculate level for full scale signal', () => {
        const samples = new Float32Array(100).fill(1);
        const level = calculateAudioLevel(samples);
        expect(level).toBe(1);
      });

      it('should handle empty array', () => {
        const samples = new Float32Array(0);
        const level = calculateAudioLevel(samples);
        expect(level).toBe(0);
      });
    });
  });

  describe('Formatting Utilities', () => {
    describe('formatDuration', () => {
      it('should format milliseconds to mm:ss', () => {
        expect(formatDuration(0)).toBe('0:00');
        expect(formatDuration(1000)).toBe('0:01');
        expect(formatDuration(60000)).toBe('1:00');
        expect(formatDuration(65000)).toBe('1:05');
        expect(formatDuration(125000)).toBe('2:05');
      });

      it('should handle hours', () => {
        expect(formatDuration(3600000)).toBe('60:00');
        expect(formatDuration(3665000)).toBe('61:05');
      });

      it('should handle negative values', () => {
        expect(formatDuration(-1000)).toBe('0:00');
      });
    });
  });

  describe('Function Utilities', () => {
    describe('debounce', () => {
      jest.useFakeTimers();

      it('should debounce function calls', () => {
        const fn = jest.fn();
        const debounced = debounce(fn, 100);

        debounced();
        debounced();
        debounced();

        expect(fn).not.toHaveBeenCalled();

        jest.advanceTimersByTime(100);
        expect(fn).toHaveBeenCalledTimes(1);
      });

      it('should pass latest arguments', () => {
        const fn = jest.fn();
        const debounced = debounce(fn, 100);

        debounced('first');
        debounced('second');
        debounced('third');

        jest.advanceTimersByTime(100);
        expect(fn).toHaveBeenCalledWith('third');
      });

      it('should reset timer on new calls', () => {
        const fn = jest.fn();
        const debounced = debounce(fn, 100);

        debounced();
        jest.advanceTimersByTime(50);
        debounced();
        jest.advanceTimersByTime(50);
        
        expect(fn).not.toHaveBeenCalled();
        
        jest.advanceTimersByTime(50);
        expect(fn).toHaveBeenCalledTimes(1);
      });
    });

    describe('throttle', () => {
      jest.useFakeTimers();

      it('should throttle function calls', () => {
        const fn = jest.fn();
        const throttled = throttle(fn, 100);

        throttled();
        throttled();
        throttled();

        expect(fn).toHaveBeenCalledTimes(1);

        jest.advanceTimersByTime(100);
        
        throttled();
        expect(fn).toHaveBeenCalledTimes(2);
      });

      it('should pass correct arguments', () => {
        const fn = jest.fn();
        const throttled = throttle(fn, 100);

        throttled('first');
        throttled('second'); // This will be ignored
        
        expect(fn).toHaveBeenCalledWith('first');

        jest.advanceTimersByTime(100);
        
        throttled('third');
        expect(fn).toHaveBeenCalledWith('third');
      });
    });
  });

  describe('Browser Compatibility', () => {
    describe('isAudioSupported', () => {
      it('should return false in test environment', () => {
        // In a Node.js test environment, window is undefined
        // so isAudioSupported should return false
        expect(isAudioSupported()).toBe(false);
      });

      // Note: Testing browser-specific functionality in Node.js environment
      // is challenging. The isAudioSupported function checks for window
      // which is undefined in Node.js. In a real browser environment,
      // it would properly detect AudioContext and getUserMedia support.
    });

    describe('getAudioConstraints', () => {
      it('should return audio constraints for mono recording', () => {
        const constraints = getAudioConstraints();
        
        expect(constraints.audio).toEqual({
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        });
        expect(constraints.video).toBe(false);
      });

      it('should allow custom sample rate', () => {
        const constraints = getAudioConstraints(48000);
        
        expect(constraints.audio).toMatchObject({
          sampleRate: 48000
        });
      });
    });
  });
});