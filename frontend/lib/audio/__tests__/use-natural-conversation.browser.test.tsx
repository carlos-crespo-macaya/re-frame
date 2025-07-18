import { renderHook, act } from '@testing-library/react-hooks';
import { useNaturalConversation } from '../use-natural-conversation';

// Polyfill for Safari/WebKit
if (typeof OfflineAudioContext === 'undefined') {
  (window as any).OfflineAudioContext = (window as any).webkitOfflineAudioContext;
}

describe('Browser Compatibility', () => {
  const browserConfigs = [
    { name: 'chrome', userAgent: 'Chrome/120.0', needsGesture: false },
    { name: 'firefox', userAgent: 'Firefox/120.0', needsGesture: false },
    { name: 'safari', userAgent: 'Safari/17.0', needsGesture: true },
    { name: 'edge', userAgent: 'Edg/120.0', needsGesture: false },
  ];
  
  beforeEach(() => {
    // Mock AudioContext for all browsers
    const MockAudioContext = jest.fn().mockImplementation(() => ({
      sampleRate: 16000,
      createMediaStreamSource: jest.fn(),
      audioWorklet: {
        addModule: jest.fn().mockResolvedValue(undefined),
      },
      close: jest.fn(),
    }));
    
    (window as any).AudioContext = MockAudioContext;
    (window as any).webkitAudioContext = MockAudioContext;
    
    // Mock MediaDevices
    const mockMediaStream = {
      getTracks: jest.fn().mockReturnValue([
        { stop: jest.fn() }
      ])
    };
    
    navigator.mediaDevices = {
      getUserMedia: jest.fn().mockResolvedValue(mockMediaStream),
    } as any;
  });
  
  afterEach(() => {
    jest.clearAllMocks();
  });
  
  browserConfigs.forEach(({ name, userAgent, needsGesture }) => {
    it(`should handle audio recording in ${name}`, async () => {
      // Set user agent
      Object.defineProperty(navigator, 'userAgent', {
        value: userAgent,
        writable: true,
        configurable: true,
      });
      
      const { result } = renderHook(() => useNaturalConversation());
      
      // Check initial state
      expect(result.current.isActive).toBe(false);
      expect(result.current.error).toBeNull();
      
      // Start voice mode
      await act(async () => {
        await result.current.startListening();
      });
      
      // Verify getUserMedia was called with correct constraints
      expect(navigator.mediaDevices.getUserMedia).toHaveBeenCalledWith({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 16000
        }
      });
      
      expect(result.current.isActive).toBe(true);
      expect(result.current.error).toBeNull();
    });
    
    it(`should handle getUserMedia rejection in ${name}`, async () => {
      Object.defineProperty(navigator, 'userAgent', {
        value: userAgent,
        writable: true,
        configurable: true,
      });
      
      // Mock getUserMedia rejection
      navigator.mediaDevices.getUserMedia = jest.fn().mockRejectedValue(
        new Error('Permission denied')
      );
      
      const { result } = renderHook(() => useNaturalConversation());
      
      await act(async () => {
        await result.current.startListening();
      });
      
      expect(result.current.isActive).toBe(false);
      expect(result.current.error).toContain('microphone');
    });
    
    it(`should handle AudioContext creation failure in ${name}`, async () => {
      Object.defineProperty(navigator, 'userAgent', {
        value: userAgent,
        writable: true,
        configurable: true,
      });
      
      // Mock AudioContext to throw
      (window as any).AudioContext = jest.fn().mockImplementation(() => {
        throw new Error('AudioContext not supported');
      });
      
      const { result } = renderHook(() => useNaturalConversation());
      
      await act(async () => {
        await result.current.startListening();
      });
      
      expect(result.current.isActive).toBe(false);
      expect(result.current.error).toBeTruthy();
    });
  });
  
  describe('Safari-specific handling', () => {
    beforeEach(() => {
      Object.defineProperty(navigator, 'userAgent', {
        value: 'Safari/17.0',
        writable: true,
        configurable: true,
      });
    });
    
    it('should handle webkit prefixed APIs', async () => {
      // Remove standard AudioContext, only webkit available
      delete (window as any).AudioContext;
      
      const { result } = renderHook(() => useNaturalConversation());
      
      await act(async () => {
        await result.current.startListening();
      });
      
      // Should still work with webkit prefix
      expect(result.current.isActive).toBe(true);
    });
    
    it('should handle AudioWorklet polyfill', async () => {
      // Mock AudioContext without audioWorklet
      const MockAudioContextNoWorklet = jest.fn().mockImplementation(() => ({
        sampleRate: 16000,
        createMediaStreamSource: jest.fn(),
        createScriptProcessor: jest.fn().mockReturnValue({
          connect: jest.fn(),
          disconnect: jest.fn(),
          addEventListener: jest.fn(),
        }),
        close: jest.fn(),
      }));
      
      (window as any).webkitAudioContext = MockAudioContextNoWorklet;
      delete (window as any).AudioContext;
      
      const { result } = renderHook(() => useNaturalConversation());
      
      await act(async () => {
        await result.current.startListening();
      });
      
      // Should fall back to ScriptProcessor
      const audioContext = MockAudioContextNoWorklet.mock.results[0].value;
      expect(audioContext.createScriptProcessor).toHaveBeenCalled();
    });
  });
  
  describe('Network resilience', () => {
    it('should handle network disconnection gracefully', async () => {
      const { result } = renderHook(() => useNaturalConversation());
      
      await act(async () => {
        await result.current.startListening();
      });
      
      // Simulate network offline
      await act(async () => {
        window.dispatchEvent(new Event('offline'));
      });
      
      // Should show connection error
      expect(result.current.status).toContain('connection');
      
      // Simulate network back online
      await act(async () => {
        window.dispatchEvent(new Event('online'));
      });
      
      // Should recover
      expect(result.current.isActive).toBe(true);
    });
  });
});