/**
 * SSE (Server-Sent Events) client for real-time streaming
 */

import {
  ServerMessage,
  ErrorMessage,
  ClientMessage,
  ConnectionState,
  isServerMessage,
  isErrorMessage,
  isStatusMessage
} from './message-protocol';
import { sessionManager, Session } from './session-manager';
import { ApiClient, logApiError, EventSourceParams } from '../api';

export interface SSEClientOptions {
  baseUrl?: string;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  heartbeatInterval?: number;
  onMessage?: (message: ServerMessage) => void;
  onError?: (error: ErrorMessage | Error) => void;
  onStatusChange?: (status: ConnectionState) => void;
  onReconnect?: (attempt: number) => void;
}

export class SSEClient {
  private eventSource: EventSource | null = null;
  private session: Session | null = null;
  private options: Required<SSEClientOptions>;
  private reconnectAttempts = 0;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private heartbeatTimer: NodeJS.Timeout | null = null;
  private messageBuffer: ServerMessage[] = [];
  private isConnecting = false;
  private lastEventTime = Date.now();
  private currentLanguage?: string;
  
  constructor(options: SSEClientOptions = {}) {
    this.options = {
      baseUrl: '',
      reconnectInterval: 5000,
      maxReconnectAttempts: 5,
      heartbeatInterval: 30000,
      onMessage: () => {},
      onError: () => {},
      onStatusChange: () => {},
      onReconnect: () => {},
      ...options
    };
  }
  
  /**
   * Connect to SSE endpoint
   */
  async connect(sessionId?: string, language?: string, isAudio: boolean = false): Promise<void> {
    if (this.isConnecting || this.eventSource) {
      console.warn('SSE client is already connected or connecting');
      return;
    }
    
    this.isConnecting = true;
    this.currentLanguage = language;
    
    try {
      // Use provided session or create new one with specified ID
      if (sessionId) {
        this.session = sessionManager.getSession(sessionId) || sessionManager.createSession(sessionId);
      } else {
        this.session = sessionManager.createSession();
      }
      
      const params: EventSourceParams = {};
      if (language) {
        params.language = language;
      }
      if (isAudio) {
        params.is_audio = true;
      }
      
      console.log('Connecting to SSE for session:', this.session.id);
      this.updateStatus('connecting');
      
      this.eventSource = ApiClient.createEventSource(this.session.id, params);
      
      this.eventSource.onopen = () => {
        console.log('SSE connection opened');
        this.isConnecting = false;
        this.reconnectAttempts = 0;
        this.updateStatus('connected');
        this.startHeartbeat();
      };
      
      this.eventSource.onmessage = (event) => {
        console.log('SSE message received:', event.data);
        this.handleMessage(event);
      };
      
      this.eventSource.onerror = (error) => {
        this.isConnecting = false;
        this.handleError(error);
      };
      
      // Custom event listeners
      this.eventSource.addEventListener('audio', (event) => {
        this.handleMessage(event);
      });
      
      this.eventSource.addEventListener('transcription', (event) => {
        this.handleMessage(event);
      });
      
      this.eventSource.addEventListener('status', (event) => {
        this.handleMessage(event);
      });
      
    } catch (error) {
      this.isConnecting = false;
      this.handleError(error as Error);
      throw error;
    }
  }
  
  /**
   * Disconnect from SSE
   */
  disconnect(): void {
    this.stopHeartbeat();
    this.clearReconnectTimer();
    
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
    
    if (this.session) {
      sessionManager.deactivateSession(this.session.id);
      this.session = null;
    }
    
    this.updateStatus('disconnected');
    this.messageBuffer = [];
  }
  
  /**
   * Send a message to the server
   */
  async sendMessage(message: ClientMessage): Promise<void> {
    if (!this.session) {
      throw new Error('No active session');
    }
    
    try {
      await ApiClient.sendMessage(this.session.id, message);
      sessionManager.updateActivity(this.session.id);
    } catch (error) {
      logApiError(error, `SSE sendMessage(${this.session.id})`);
      this.options.onError(error as Error);
      throw error;
    }
  }
  
  /**
   * Handle incoming messages
   */
  private handleMessage(event: MessageEvent): void {
    this.lastEventTime = Date.now();
    
    try {
      const data = JSON.parse(event.data);
      
      // Handle different SSE message types from backend
      if (data.type === 'heartbeat') {
        // Just update last event time, no need to process further
        return;
      }
      
      if (data.type === 'connected') {
        // Connection confirmation from backend
        console.log('SSE connection confirmed:', data.session_id);
        return;
      }
      
      if (data.type === 'content') {
        // Transform SSEMessage to ServerMessage format
        const serverMessage: ServerMessage = {
          mime_type: data.content_type || 'text/plain',
          data: data.data || '',
          message_type: 'response',
          session_id: this.session?.id
        };
        
        this.messageBuffer.push(serverMessage);
        this.options.onMessage(serverMessage);
        
        if (this.session) {
          sessionManager.updateActivity(this.session.id);
        }
      } else if (data.type === 'turn_complete') {
        // Handle turn complete message
        console.log('🎯 SSE received turn_complete:', data);
        const serverMessage: ServerMessage = {
          turn_complete: data.turn_complete,
          interrupted: data.interrupted
        };
        
        this.messageBuffer.push(serverMessage);
        this.options.onMessage(serverMessage);
        console.log('🎯 Turn complete message sent to onMessage callback');
      } else if (data.type === 'error') {
        // Handle error message
        const errorMessage: ErrorMessage = {
          message_type: 'error',
          error_code: 'SSE_ERROR',
          error_message: data.message || 'Unknown error',
          session_id: this.session?.id || '',
          timestamp: Date.now()
        };
        this.options.onError(errorMessage);
      } else if (isServerMessage(data)) {
        // Legacy format support
        this.messageBuffer.push(data);
        this.options.onMessage(data);
        
        if (this.session) {
          sessionManager.updateActivity(this.session.id);
        }
      } else if (isErrorMessage(data)) {
        this.options.onError(data);
      } else if (isStatusMessage(data)) {
        this.updateStatus(data.status);
      }
      
    } catch (error) {
      console.error('Failed to parse SSE message:', error as Error);
      this.options.onError(error as Error);
    }
  }
  
  /**
   * Handle connection errors
   */
  private handleError(error: Error | Event): void {
    console.error('SSE connection error:', error);
    
    this.stopHeartbeat();
    if (this.eventSource?.readyState === EventSource.CLOSED) {
      this.updateStatus('disconnected');
      this.attemptReconnect();
    } else {
      this.updateStatus('error');
      this.options.onError(error as Error);
    }
  }
  
  /**
   * Attempt to reconnect
   */
  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.options.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      this.disconnect();
      return;
    }
    
    this.clearReconnectTimer();
    
    this.reconnectAttempts++;
    this.options.onReconnect(this.reconnectAttempts);
    
    this.reconnectTimer = setTimeout(() => {
      // Ensure any stale EventSource is cleared before reconnect
      if (this.eventSource && this.eventSource.readyState !== EventSource.OPEN) {
        try { this.eventSource.close(); } catch {
          // ignore close errors
        }
        this.eventSource = null;
      }
      if (this.session) {
        this.connect(this.session.id, this.currentLanguage)
          .catch((err) => {
            console.error('Reconnect failed:', err);
            this.options.onError(err as Error);
          });
      }
    }, this.options.reconnectInterval);
  }
  
  /**
   * Start heartbeat monitoring
   */
  private startHeartbeat(): void {
    this.stopHeartbeat();
    
    this.heartbeatTimer = setInterval(() => {
      const timeSinceLastEvent = Date.now() - this.lastEventTime;
      
      if (timeSinceLastEvent > this.options.heartbeatInterval * 2) {
        console.warn('No events received, reconnecting...');
        this.handleError(new Error('Connection timeout'));
      }
    }, this.options.heartbeatInterval);
  }
  
  /**
   * Stop heartbeat monitoring
   */
  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }
  
  /**
   * Clear reconnect timer
   */
  private clearReconnectTimer(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }
  
  /**
   * Update connection status
   */
  private updateStatus(status: ConnectionState): void {
    this.options.onStatusChange(status);
  }
  
  /**
   * Get buffered messages
   */
  getMessageBuffer(): ServerMessage[] {
    return [...this.messageBuffer];
  }
  
  /**
   * Clear message buffer
   */
  clearMessageBuffer(): void {
    this.messageBuffer = [];
  }
  
  /**
   * Get connection state
   */
  getConnectionState(): ConnectionState {
    if (!this.eventSource) return 'disconnected';
    
    switch (this.eventSource.readyState) {
      case EventSource.CONNECTING:
        return 'connecting';
      case EventSource.OPEN:
        return 'connected';
      case EventSource.CLOSED:
        return 'disconnected';
      default:
        return 'error';
    }
  }
  
  /**
   * Get current session
   */
  getSession(): Session | null {
    return this.session;
  }
  
  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.eventSource?.readyState === EventSource.OPEN;
  }
}