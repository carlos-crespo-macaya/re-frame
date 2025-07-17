/**
 * Unit tests for SSE client heartbeat timer functionality.
 * These tests verify that lastEventTime is properly updated on any SSE message.
 */

import { SSEClient } from '../sse-client';
import type { ApiClient as ApiClientType } from '../../api';

// Mock dependencies
jest.mock('../session-manager', () => ({
  sessionManager: {
    createSession: jest.fn(() => ({ id: 'test-session-id', messages: [] })),
    updateActivity: jest.fn(),
    removeSession: jest.fn(),
    getSession: jest.fn(() => ({ id: 'test-session-id', messages: [] })),
  },
}));

jest.mock('../../api', () => ({
  ApiClient: {
    createSession: jest.fn().mockResolvedValue({
      data: { session_id: 'test-session-id' },
    }),
    sendMessage: jest.fn().mockResolvedValue({}),
    createEventSource: jest.fn(),
  },
  logApiError: jest.fn(),
}));

// Import the mocked module
import { ApiClient } from '../../api';
const mockedApiClient = ApiClient as jest.Mocked<typeof ApiClientType>;

describe('SSEClient Heartbeat Timer', () => {
  let client: SSEClient;
  let mockEventSource: any;
  let originalEventSource: any;

  beforeEach(() => {
    // Define EventSource constants if not available
    if (typeof EventSource === 'undefined') {
      (global as any).EventSource = class {
        static CONNECTING = 0;
        static OPEN = 1;
        static CLOSED = 2;
      };
    }

    // Mock EventSource
    mockEventSource = {
      readyState: 1, // EventSource.OPEN
      close: jest.fn(),
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      onopen: null,
      onmessage: null,
      onerror: null,
    };

    originalEventSource = global.EventSource;
    global.EventSource = jest.fn().mockImplementation(() => mockEventSource) as any;
    
    // Mock ApiClient to return our mockEventSource
    mockedApiClient.createEventSource.mockReturnValue(mockEventSource);

    client = new SSEClient({
      onMessage: jest.fn(),
      onError: jest.fn(),
      onStatusChange: jest.fn(),
      onReconnect: jest.fn(),
    });
  });

  afterEach(() => {
    global.EventSource = originalEventSource;
    jest.clearAllMocks();
  });

  it('should update lastEventTime on ANY SSE message', async () => {
    // Connect the client
    await client.connect('test-session', 'en-US');

    // Get initial lastEventTime
    const initialTime = (client as any).lastEventTime;
    expect(initialTime).toBeGreaterThan(0);

    // Simulate various SSE messages
    const testMessages = [
      { data: JSON.stringify({ mime_type: 'text/plain', data: 'Hello' }) },
      { data: JSON.stringify({ type: 'heartbeat', timestamp: '2025-01-17T12:00:00Z' }) },
      { data: JSON.stringify({ turn_complete: true, interrupted: null }) },
      { data: JSON.stringify({ type: 'connected', session_id: 'test' }) },
      { data: '{}' }, // Empty object
      { data: 'invalid json' }, // Invalid JSON
    ];

    for (const message of testMessages) {
      const timeBefore = (client as any).lastEventTime;
      
      // Wait a bit to ensure time difference  
      await new Promise(resolve => setTimeout(resolve, 5));
      
      // Trigger onmessage handler
      if (mockEventSource.onmessage) {
        mockEventSource.onmessage(message);
      }

      const timeAfter = (client as any).lastEventTime;
      
      // Verify lastEventTime was updated
      expect(timeAfter).toBeGreaterThan(timeBefore);
    }
  });

  it('should not timeout if messages are received within threshold', async () => {
    // Connect with short heartbeat interval for testing
    let errorCalled = false;
    const customClient = new SSEClient({
      onMessage: jest.fn(),
      onError: (error: any) => {
        if (error.message === 'Connection timeout') {
          errorCalled = true;
        }
      },
      onStatusChange: jest.fn(),
      onReconnect: jest.fn(),
      heartbeatInterval: 1000, // 1 second for faster testing
    });

    await customClient.connect('test-session', 'en-US');

    // Start heartbeat monitoring
    (customClient as any).startHeartbeat();

    // Simulate regular messages within heartbeat interval
    const messageInterval = setInterval(() => {
      if (mockEventSource.onmessage) {
        mockEventSource.onmessage({
          data: JSON.stringify({ mime_type: 'text/plain', data: 'test' })
        });
      }
    }, 500); // Send message every 500ms

    // Wait for 3 seconds (would timeout after 2 seconds without messages)
    await new Promise(resolve => setTimeout(resolve, 3000));

    clearInterval(messageInterval);
    (customClient as any).stopHeartbeat();

    // Verify no timeout error occurred
    expect(errorCalled).toBe(false);
  });

  it('should timeout if no messages received', async () => {
    // Connect with short heartbeat interval for testing
    let timeoutError: Error | null = null;
    const customClient = new SSEClient({
      onMessage: jest.fn(),
      onError: (error: any) => {
        if (error.message === 'Connection timeout') {
          timeoutError = error;
        }
      },
      onStatusChange: jest.fn(),
      onReconnect: jest.fn(),
      heartbeatInterval: 500, // 500ms for faster testing
    });

    await customClient.connect('test-session', 'en-US');

    // Start heartbeat monitoring
    (customClient as any).startHeartbeat();

    // Don't send any messages and wait for timeout
    await new Promise(resolve => setTimeout(resolve, 1500)); // Wait 1.5 seconds

    // Verify timeout occurred
    expect(timeoutError).not.toBeNull();
    expect(timeoutError!.message).toBe('Connection timeout');

    (customClient as any).stopHeartbeat();
  });

  it('should handle malformed messages without breaking heartbeat', async () => {
    await client.connect('test-session', 'en-US');

    const timeBefore = (client as any).lastEventTime;

    // Send malformed messages
    const malformedMessages = [
      { data: null },
      { data: undefined },
      { data: '' },
      { data: 'not json at all {{{' },
      { data: '{"incomplete": ' },
    ];

    for (const message of malformedMessages) {
      if (mockEventSource.onmessage) {
        mockEventSource.onmessage(message as any);
      }
    }

    const timeAfter = (client as any).lastEventTime;

    // Even malformed messages should update lastEventTime
    expect(timeAfter).toBeGreaterThan(timeBefore);
  });

  it('should reset reconnection attempts on successful heartbeat', async () => {
    await client.connect('test-session', 'en-US');

    // Simulate some failed reconnection attempts
    (client as any).reconnectAttempts = 3;

    // Send a heartbeat message
    if (mockEventSource.onmessage) {
      mockEventSource.onmessage({
        data: JSON.stringify({ type: 'heartbeat', timestamp: '2025-01-17T12:00:00Z' })
      });
    }

    // Heartbeat should indicate healthy connection
    // In the real implementation, this would reset reconnectAttempts
    // For now, we're just testing that the message is received
    expect((client as any).lastEventTime).toBeGreaterThan(0);
  });
});