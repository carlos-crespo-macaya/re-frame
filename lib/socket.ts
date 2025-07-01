// WebSocket connection handler for Reframe-APD
import { EventEmitter } from 'events';

export interface SocketMessage {
  type: 'init' | 'user_msg' | 'assistant_stream' | 'phase_change' | 'pdf_ready' | 'complete';
  data?: any;
  session_id?: string;
}

export class ReframeSocket extends EventEmitter {
  private ws: WebSocket | null = null;
  private url: string;
  private sessionId: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;

  constructor(url: string, sessionId: string) {
    super();
    this.url = url;
    this.sessionId = sessionId;
  }

  connect(): void {
    try {
      this.ws = new WebSocket(`${this.url}/chat/${this.sessionId}`);
      
      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
        this.emit('connected');
        
        // Send init message
        this.send('init', { session_id: this.sessionId });
      };

      this.ws.onmessage = (event) => {
        try {
          const message: SocketMessage = JSON.parse(event.data);
          this.handleMessage(message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.emit('error', error);
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.emit('disconnected');
        this.handleReconnect();
      };
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      this.emit('error', error);
    }
  }

  private handleMessage(message: SocketMessage): void {
    switch (message.type) {
      case 'assistant_stream':
        this.emit('assistant_stream', message.data);
        break;
      case 'phase_change':
        this.emit('phase_change', message.data);
        break;
      case 'pdf_ready':
        this.emit('pdf_ready', message.data);
        break;
      case 'complete':
        this.emit('complete', message.data);
        break;
      default:
        console.warn('Unknown message type:', message.type);
    }
  }

  send(type: string, data?: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const message: SocketMessage = { type: type as any, data, session_id: this.sessionId };
      this.ws.send(JSON.stringify(message));
    } else {
      console.error('WebSocket is not connected');
    }
  }

  sendUserMessage(message: string): void {
    this.send('user_msg', { message });
  }

  private handleReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Reconnecting... Attempt ${this.reconnectAttempts}`);
      setTimeout(() => {
        this.connect();
      }, this.reconnectDelay * this.reconnectAttempts);
    } else {
      console.error('Max reconnection attempts reached');
      this.emit('reconnect_failed');
    }
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

// Factory function to create socket connection
export function createReframeSocket(sessionId: string): ReframeSocket {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'ws://localhost:8000';
  const wsUrl = apiUrl.replace(/^http/, 'ws');
  return new ReframeSocket(wsUrl, sessionId);
}