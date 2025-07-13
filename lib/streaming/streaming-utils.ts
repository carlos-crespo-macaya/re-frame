/**
 * Utilities for streaming data processing
 */

import { ClientMessage, ServerMessage } from './message-protocol';

/**
 * Convert text to base64-encoded PCM audio data
 * This is a placeholder - real implementation would use text-to-speech
 */
export function textToPCM(text: string, sampleRate: number = 16000): string {
  // Placeholder implementation
  console.warn('textToPCM is not yet implemented');
  return '';
}

/**
 * Convert base64-encoded PCM audio data to text
 * This is a placeholder - real implementation would use speech-to-text
 */
export function pcmToText(pcmData: string): Promise<string> {
  // Placeholder implementation
  console.warn('pcmToText is not yet implemented');
  return Promise.resolve('');
}

/**
 * Encode Int16 PCM audio buffer to base64
 */
export function encodePCM16(buffer: Int16Array): string {
  const bytes = new Uint8Array(buffer.buffer, buffer.byteOffset, buffer.byteLength);
  let binary = '';
  
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  
  return btoa(binary);
}

/**
 * Encode Float32 PCM audio buffer to base64 (converts to Int16 first)
 */
export function encodePCM32(buffer: Float32Array): string {
  // Convert Float32 to Int16 first
  const int16Buffer = new Int16Array(buffer.length);
  for (let i = 0; i < buffer.length; i++) {
    const clamped = Math.max(-1, Math.min(1, buffer[i]));
    int16Buffer[i] = Math.round(clamped * 32767);
  }
  return encodePCM16(int16Buffer);
}

/**
 * Decode base64 to Int16 PCM audio buffer
 */
export function decodePCM16(base64: string): Int16Array {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  
  return new Int16Array(bytes.buffer);
}

/**
 * Legacy function for backward compatibility
 * @deprecated Use encodePCM16 or encodePCM32 instead
 */
export function encodePCM(buffer: Float32Array | Int16Array): string {
  if (buffer instanceof Float32Array) {
    return encodePCM32(buffer);
  } else {
    return encodePCM16(buffer);
  }
}

/**
 * Legacy function for backward compatibility
 * @deprecated Use decodePCM16 instead
 */
export function decodePCM(base64: string): Int16Array {
  return decodePCM16(base64);
}

/**
 * Chunk large messages for streaming
 */
export function* chunkMessage(
  message: string,
  chunkSize: number = 1024
): Generator<string> {
  for (let i = 0; i < message.length; i += chunkSize) {
    yield message.slice(i, i + chunkSize);
  }
}

/**
 * Reassemble chunked messages
 */
export class MessageAssembler {
  private chunks: Map<string, string[]> = new Map();
  private messageCounter = 0;
  
  addChunk(message: ServerMessage): string | null {
    // Use timestamp if available, otherwise use chunk_id or a counter
    const timestamp = message.timestamp || message.chunk_id || `msg-${this.messageCounter++}`;
    const key = `${message.session_id}-${timestamp}`;
    
    if (!this.chunks.has(key)) {
      this.chunks.set(key, []);
    }
    
    const chunks = this.chunks.get(key)!;
    chunks.push(message.data);
    
    if (message.is_final) {
      const complete = chunks.join('');
      this.chunks.delete(key);
      return complete;
    }
    
    return null;
  }
  
  clear(): void {
    this.chunks.clear();
    this.messageCounter = 0;
  }
}

/**
 * Rate limiter for outgoing messages
 */
export class RateLimiter {
  private queue: ClientMessage[] = [];
  private processing = false;
  private retryAttempts = new Map<ClientMessage, number>();
  private maxRetries = 3;
  
  constructor(
    private rateMs: number = 100,
    private maxQueueSize: number = 100
  ) {}
  
  async send(
    message: ClientMessage,
    sendFn: (msg: ClientMessage) => Promise<void>
  ): Promise<void> {
    if (this.queue.length >= this.maxQueueSize) {
      throw new Error('Rate limiter queue is full');
    }
    
    this.queue.push(message);
    
    if (!this.processing) {
      this.processQueue(sendFn);
    }
  }
  
  private async processQueue(
    sendFn: (msg: ClientMessage) => Promise<void>
  ): Promise<void> {
    this.processing = true;
    
    while (this.queue.length > 0) {
      const message = this.queue.shift()!;
      
      try {
        await sendFn(message);
        // Clean up retry count on success
        this.retryAttempts.delete(message);
        await this.delay(this.rateMs);
      } catch (error) {
        const retries = this.retryAttempts.get(message) || 0;
        
        if (retries < this.maxRetries) {
          console.warn(`Failed to send rate-limited message (attempt ${retries + 1}/${this.maxRetries}):`, error);
          // Increment retry count and re-queue
          this.retryAttempts.set(message, retries + 1);
          this.queue.unshift(message);
          await this.delay(this.rateMs * Math.pow(2, retries + 1)); // Exponential backoff
        } else {
          console.error(`Failed to send rate-limited message after ${this.maxRetries} attempts:`, error);
          // Clean up and drop the message
          this.retryAttempts.delete(message);
        }
      }
    }
    
    this.processing = false;
  }
  
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
  
  clear(): void {
    this.queue = [];
    this.retryAttempts.clear();
  }
}

/**
 * Create a reconnecting SSE client wrapper
 */
export function createReconnectingClient(
  clientFactory: () => any,
  options: {
    maxAttempts?: number;
    backoffMs?: number;
    onReconnect?: (attempt: number) => void;
  } = {}
): any {
  const {
    maxAttempts = 5,
    backoffMs = 1000,
    onReconnect = () => {}
  } = options;
  
  let client = clientFactory();
  let attempts = 0;
  
  const reconnect = async () => {
    if (attempts >= maxAttempts) {
      throw new Error('Max reconnection attempts reached');
    }
    
    attempts++;
    onReconnect(attempts);
    
    await new Promise(resolve => 
      setTimeout(resolve, backoffMs * Math.pow(2, attempts - 1))
    );
    
    client = clientFactory();
    return client;
  };
  
  // Proxy all client methods and add reconnection logic
  return new Proxy(client, {
    get(target, prop) {
      const value = target[prop];
      
      if (typeof value === 'function') {
        return async (...args: any[]) => {
          try {
            return await value.apply(target, args);
          } catch (error) {
            console.error(`Error calling ${String(prop)}:`, error);
            const newClient = await reconnect();
            return newClient[prop](...args);
          }
        };
      }
      
      return value;
    }
  });
}