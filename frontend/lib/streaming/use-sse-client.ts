/**
 * React hook for SSE client integration
 */

import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { 
  SSEClient, 
  type SSEClientOptions 
} from './sse-client';
import {
  type ServerMessage,
  type ClientMessage,
  type ConnectionState,
  type ErrorMessage,
  createClientMessage
} from './message-protocol';
import { MessageAssembler, RateLimiter } from './streaming-utils';

export interface UseSSEClientOptions extends Omit<SSEClientOptions, 'onMessage' | 'onError' | 'onStatusChange'> {
  autoConnect?: boolean;
  enableRateLimit?: boolean;
  rateLimitMs?: number;
}

export interface SSEClientState {
  isConnected: boolean;
  connectionState: ConnectionState;
  error: Error | null;
  messages: ServerMessage[];
  sessionId: string | null;
}

export function useSSEClient(options: UseSSEClientOptions = {}) {
  const {
    autoConnect = false,
    enableRateLimit = true,
    rateLimitMs = 100,
    ...sseOptions
  } = options;
  
  const [state, setState] = useState<SSEClientState>({
    isConnected: false,
    connectionState: 'disconnected',
    error: null,
    messages: [],
    sessionId: null
  });
  
  const clientRef = useRef<SSEClient | null>(null);
  const assemblerRef = useRef(new MessageAssembler());
  const rateLimiterRef = useRef(new RateLimiter(rateLimitMs));

  // Queue for messages attempted before the SSE connection is fully open.
  // Each entry stores the arguments passed to sendMessage so we can replay
  // them later in the exact same order.
  const pendingQueueRef = useRef<Array<[
    string,
    'text/plain' | 'audio/pcm',
    Partial<{ messageType: 'thought' | 'response' | 'transcription'; turnComplete?: boolean; interrupted?: boolean; }>
  ]>>([]);
  
  // Memoize SSE options to prevent unnecessary re-renders
  const memoizedSseOptions = useMemo(() => sseOptions, [
    sseOptions.baseUrl,
    sseOptions.reconnectInterval,
    sseOptions.maxReconnectAttempts,
    sseOptions.heartbeatInterval
  ]);
  
  // Initialize SSE client
  useEffect(() => {
    const client = new SSEClient({
      ...memoizedSseOptions,
      onMessage: (message: ServerMessage) => {
        // Try to assemble chunked messages
        const complete = assemblerRef.current.addChunk(message);
        
        if (complete) {
          // Process complete message
          const completeMessage = {
            ...message,
            data: complete
          };
          
          setState(prev => ({
            ...prev,
            messages: [...prev.messages, completeMessage]
          }));
        } else {
          // Add partial message
          setState(prev => ({
            ...prev,
            messages: [...prev.messages, message]
          }));
        }
      },
      onError: (error: ErrorMessage | Error) => {
        setState(prev => ({
          ...prev,
          error: error instanceof Error ? error : new Error(error.error_message)
        }));
      },
      onStatusChange: (status: ConnectionState) => {
        setState(prev => ({
          ...prev,
          connectionState: status,
          isConnected: status === 'connected'
        }));

        // When the connection transitions to "connected" we flush any queued
        // messages that were generated while waiting for the SSE handshake.
        if (status === 'connected' && pendingQueueRef.current.length > 0 && clientRef.current) {
          const flushQueue = async () => {
            for (const [queuedData, queuedMime, queuedOpts] of pendingQueueRef.current) {
              try {
                // eslint-disable-next-line no-await-in-loop
                await clientRef.current!.sendMessage(
                  createClientMessage({
                    data: queuedData,
                    mimeType: queuedMime,
                    messageType: queuedOpts.messageType || 'thought',
                    sessionId: clientRef.current!.getSession()!.id,
                    turnComplete: queuedOpts.turnComplete,
                    interrupted: queuedOpts.interrupted
                  })
                );
              } catch (err) {
                console.error('Failed to flush queued message:', err);
              }
            }
            pendingQueueRef.current = [];
          };

          // Fire and forget – we don't await inside the status handler.
          // eslint-disable-next-line @typescript-eslint/no-floating-promises
          flushQueue();
        }
      }
    });
    
    clientRef.current = client;
    
    if (autoConnect) {
      client.connect().catch(console.error);
    }
    
    return () => {
      client.disconnect();
    };
  }, [memoizedSseOptions, autoConnect]); // Re-create client when options change
  
  // Connect to SSE
  const connect = useCallback(async (sessionId?: string, language?: string, isAudio: boolean = false) => {
    if (!clientRef.current) return;
    
    try {
      setState(prev => ({ ...prev, error: null }));
      await clientRef.current.connect(sessionId, language, isAudio);
      
      const session = clientRef.current.getSession();
      setState(prev => ({
        ...prev,
        sessionId: session?.id || null
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        error: error as Error
      }));
    }
  }, []);
  
  // Disconnect from SSE
  const disconnect = useCallback(() => {
    if (!clientRef.current) return;
    
    clientRef.current.disconnect();
    assemblerRef.current.clear();
    rateLimiterRef.current.clear();
    
    setState(prev => ({
      ...prev,
      isConnected: false,
      connectionState: 'disconnected',
      sessionId: null,
      messages: []
    }));

    pendingQueueRef.current = [];
  }, []);
  
  // Send a message
  const sendMessage = useCallback(async (
    data: string,
    mimeType: 'text/plain' | 'audio/pcm' = 'text/plain',
    options: Partial<{
      messageType: 'thought' | 'response' | 'transcription';
      turnComplete?: boolean;
      interrupted?: boolean;
    }> = {}
  ) => {
    const client = clientRef.current;

    // If the SSE connection hasn't been fully established yet we enqueue the
    // message. It will be flushed as soon as we receive the "connected" status
    // from the EventSource. This prevents race conditions where the first
    // message arrives at the backend before the session is created, which
    // results in 404 errors.
    if (!client || !state.sessionId || client.getConnectionState() !== 'connected') {
      pendingQueueRef.current.push([data, mimeType, options]);
      return;
    }
    
    const message = createClientMessage({
      data,
      mimeType,
      messageType: options.messageType || 'thought',
      sessionId: state.sessionId,
      turnComplete: options.turnComplete,
      interrupted: options.interrupted
    });
    
    // Always emit a debug log for audio payloads so that issues can be
    // diagnosed on production systems without having to rebuild the frontend
    // in development mode.
    if (message.mime_type === 'audio/pcm') {
      console.log('Audio message payload:', {
        mime_type: message.mime_type,
        data_length: message.data.length,
        turn_complete: message.turn_complete,
        session_id: message.session_id
      })
    }
    
    if (enableRateLimit) {
      await rateLimiterRef.current.send(
        message,
        (msg) => clientRef.current!.sendMessage(msg)
      );
    } else {
      await clientRef.current.sendMessage(message);
    }
  }, [state.sessionId, enableRateLimit]);
  
  // Send text message
  const sendText = useCallback((text: string, turnComplete = true) => {
    return sendMessage(text, 'text/plain', {
      messageType: 'thought',
      turnComplete: turnComplete
    });
  }, [sendMessage]);
  
  // Send audio message
  const sendAudio = useCallback((audioData: string, turnComplete = false) => {
    console.log(`Sending audio/pcm data: ${audioData.length} chars, turnComplete: ${turnComplete}`)
    return sendMessage(audioData, 'audio/pcm', {
      messageType: 'thought',
      turnComplete: turnComplete
    });
  }, [sendMessage]);
  
  // Clear messages
  const clearMessages = useCallback(() => {
    setState(prev => ({
      ...prev,
      messages: []
    }));
    
    if (clientRef.current) {
      clientRef.current.clearMessageBuffer();
    }
  }, []);
  
  // Get latest message of a specific type
  const getLatestMessage = useCallback((type: string) => {
    return state.messages
      .filter(msg => msg.message_type === type)
      .pop();
  }, [state.messages]);
  
  // Get all messages of a specific type
  const getMessagesByType = useCallback((type: string) => {
    return state.messages.filter(msg => msg.message_type === type);
  }, [state.messages]);
  
  return {
    // State
    ...state,
    
    // Actions
    connect,
    disconnect,
    sendMessage,
    sendText,
    sendAudio,
    clearMessages,
    
    // Utilities
    getLatestMessage,
    getMessagesByType,
    
    // Client reference (for advanced usage)
    client: clientRef.current
  };
}
