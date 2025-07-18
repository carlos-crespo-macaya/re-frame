import { renderHook, act } from '@testing-library/react';
import { useNaturalConversation } from '../use-natural-conversation';
import { ApiClient } from '../../api';

// Mock the session utilities
jest.mock('../../utils/session', () => ({
  generateAudioSessionId: jest.fn(() => 'test-audio-session-123')
}));

// Mock the API client
jest.mock('../../api', () => ({
  ApiClient: {
    sendMessage: jest.fn().mockResolvedValue(undefined),
    createEventSource: jest.fn().mockImplementation(() => {
      const mockEventSource = {
        close: jest.fn(),
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
        readyState: 1,
        url: '',
        withCredentials: false,
        CONNECTING: 0,
        OPEN: 1,
        CLOSED: 2,
        onerror: null,
        onmessage: null,
        onopen: null,
      };
      
      // Simulate successful connection
      setTimeout(() => {
        if (mockEventSource.onopen) {
          mockEventSource.onopen(new Event('open'));
        }
      }, 0);
      
      return mockEventSource;
    })
  },
  logApiError: jest.fn()
}));

// Mock the streaming message protocol
jest.mock('../../streaming/message-protocol', () => ({
  createClientMessage: jest.fn((data) => data)
}));

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
    
    // Mock URL.createObjectURL and URL.revokeObjectURL for AudioWorklet
    (global as any).URL = {
      ...URL,
      createObjectURL: jest.fn().mockReturnValue('blob:mock-url'),
      revokeObjectURL: jest.fn(),
    };
    
    // Mock AudioContext for all browsers
    const MockAudioContext = jest.fn().mockImplementation(() => ({
      sampleRate: 16000,
      createMediaStreamSource: jest.fn().mockReturnValue({
        connect: jest.fn(),
        disconnect: jest.fn(),
      }),
      audioWorklet: {
        addModule: jest.fn().mockResolvedValue(undefined),
      },
      destination: {},
      close: jest.fn(),
    }));
    
    (window as any).AudioContext = MockAudioContext;
    (window as any).webkitAudioContext = MockAudioContext;
    
    // Mock AudioWorkletNode
    (window as any).AudioWorkletNode = jest.fn().mockImplementation(() => ({
      connect: jest.fn(),
      disconnect: jest.fn(),
      port: {
        onmessage: null,
        postMessage: jest.fn(),
      },
    }));
    
    // Mock MediaDevices
    const mockMediaStream = {
      getTracks: jest.fn().mockReturnValue([
        { stop: jest.fn() }
      ])
    };
    
    // Use Object.defineProperty to override readonly property
    Object.defineProperty(navigator, 'mediaDevices', {
      value: {
        getUserMedia: jest.fn().mockResolvedValue(mockMediaStream),
      },
      writable: true,
      configurable: true,
    });
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
        await result.current.startConversation();
      });
      
      // Verify getUserMedia was called (hook uses simple constraints for permission test)
      expect(navigator.mediaDevices.getUserMedia).toHaveBeenCalledWith({
        audio: true
      });
      
      // Debug info if test fails
      if (!result.current.isActive) {
        console.log('Failed to activate:', {
          status: result.current.status,
          error: result.current.error?.message
        });
      }
      
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
        await result.current.startConversation();
      });
      
      expect(result.current.isActive).toBe(false);
      expect(result.current.error).toBeTruthy();
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
        await result.current.startConversation();
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
      // The hook doesn't actually have webkit prefix support
      // If standard AudioContext is not available, it should fail
      const originalAudioContext = (window as any).AudioContext;
      
      // Remove standard AudioContext, only webkit available
      delete (window as any).AudioContext;
      
      try {
        const { result } = renderHook(() => useNaturalConversation());
        
        await act(async () => {
          await result.current.startConversation();
        });
        
        // Should fail when AudioContext is not available
        expect(result.current.isActive).toBe(false);
        expect(result.current.error).toBeTruthy();
      } finally {
        // Restore AudioContext
        (window as any).AudioContext = originalAudioContext;
      }
    });
    
    it('should handle AudioWorklet polyfill', async () => {
      // Store originals
      const originalAudioContext = (window as any).AudioContext;
      const originalAudioWorkletNode = (window as any).AudioWorkletNode;
      
      // Mock AudioContext without audioWorklet
      const MockAudioContextNoWorklet = jest.fn().mockImplementation(() => ({
        sampleRate: 16000,
        createMediaStreamSource: jest.fn().mockReturnValue({
          connect: jest.fn(),
          disconnect: jest.fn(),
        }),
        // No audioWorklet property
        destination: {},
        close: jest.fn(),
      }));
      
      (window as any).webkitAudioContext = MockAudioContextNoWorklet;
      delete (window as any).AudioContext;
      delete (window as any).AudioWorkletNode;
      
      try {
        const { result } = renderHook(() => useNaturalConversation());
        
        await act(async () => {
          await result.current.startConversation();
        });
        
        // Should fail when AudioWorklet is not available
        expect(result.current.isActive).toBe(false);
        expect(result.current.error).toBeTruthy();
      } finally {
        // Restore
        (window as any).AudioContext = originalAudioContext;
        (window as any).AudioWorkletNode = originalAudioWorkletNode;
      }
    });
  });
  
  describe('Network resilience', () => {
    it('should handle network disconnection gracefully', async () => {
      // Get access to the mock EventSource
      const mockEventSource = (ApiClient.createEventSource as jest.Mock).mockImplementation(() => {
        const eventSource = {
          close: jest.fn(),
          addEventListener: jest.fn(),
          removeEventListener: jest.fn(),
          readyState: 1,
          url: '',
          withCredentials: false,
          CONNECTING: 0,
          OPEN: 1,
          CLOSED: 2,
          onerror: null,
          onmessage: null,
          onopen: null,
        };
        
        // Simulate successful connection initially
        setTimeout(() => {
          if (eventSource.onopen) {
            eventSource.onopen(new Event('open'));
          }
        }, 0);
        
        return eventSource;
      });
      
      const { result } = renderHook(() => useNaturalConversation());
      
      await act(async () => {
        await result.current.startConversation();
      });
      
      expect(result.current.isActive).toBe(true);
      
      // Get the created EventSource instance
      const eventSourceInstance = mockEventSource.mock.results[0].value;
      
      // Simulate SSE error
      await act(async () => {
        if (eventSourceInstance.onerror) {
          eventSourceInstance.onerror(new Event('error'));
        }
      });
      
      // Should show connection error
      expect(result.current.status.toLowerCase()).toContain('connection error');
    });
  });
});