/**
 * Tests for streaming utilities
 */

import {
  encodePCM,
  decodePCM,
  chunkMessage,
  MessageAssembler,
  RateLimiter
} from '../streaming-utils';
import { type ServerMessage } from '../message-protocol';

describe('Streaming Utilities', () => {
  describe('PCM Encoding/Decoding', () => {
    it('should encode and decode PCM data', () => {
      const original = new Int16Array([100, -200, 300, -400, 500]);
      const encoded = encodePCM(original);
      const decoded = decodePCM(encoded);
      
      expect(decoded).toEqual(original);
    });
  });
  
  describe('Message Chunking', () => {
    it('should chunk messages correctly', () => {
      const message = 'Hello, this is a long message that needs chunking';
      const chunks = Array.from(chunkMessage(message, 10));
      
      expect(chunks).toHaveLength(5);
      expect(chunks[0]).toBe('Hello, thi');
      expect(chunks[4]).toBe(' chunking');
      expect(chunks.join('')).toBe(message);
    });
  });
  
  describe('MessageAssembler', () => {
    it('should assemble chunked messages', () => {
      const assembler = new MessageAssembler();
      const baseMessage: Partial<ServerMessage> = {
        session_id: 'test',
        timestamp: 12345,
        mime_type: 'text/plain',
        message_type: 'response'
      };
      
      // Add chunks
      expect(assembler.addChunk({
        ...baseMessage,
        data: 'Hello ',
        is_final: false
      } as ServerMessage)).toBeNull();
      
      expect(assembler.addChunk({
        ...baseMessage,
        data: 'World!',
        is_final: true
      } as ServerMessage)).toBe('Hello World!');
    });
    
    it('should handle multiple concurrent messages', () => {
      const assembler = new MessageAssembler();
      
      // Message 1
      assembler.addChunk({
        session_id: 'session1',
        timestamp: 1000,
        data: 'Msg1-',
        mime_type: 'text/plain',
        message_type: 'response'
      } as ServerMessage);
      
      // Message 2
      assembler.addChunk({
        session_id: 'session2',
        timestamp: 2000,
        data: 'Msg2-',
        mime_type: 'text/plain',
        message_type: 'response'
      } as ServerMessage);
      
      // Complete message 1
      const msg1 = assembler.addChunk({
        session_id: 'session1',
        timestamp: 1000,
        data: 'Part2',
        is_final: true,
        mime_type: 'text/plain',
        message_type: 'response'
      } as ServerMessage);
      
      expect(msg1).toBe('Msg1-Part2');
    });
  });
  
  describe('RateLimiter', () => {
    jest.useFakeTimers();
    
    it('should rate limit messages', async () => {
      const sendFn = jest.fn().mockResolvedValue(undefined);
      const limiter = new RateLimiter(100);
      
      const message1 = {
        mime_type: 'text/plain',
        data: 'msg1',
        message_type: 'thought',
        session_id: 'test'
      } as any;
      
      const message2 = {
        mime_type: 'text/plain',
        data: 'msg2',
        message_type: 'thought',
        session_id: 'test'
      } as any;
      
      // Send two messages
      limiter.send(message1, sendFn);
      limiter.send(message2, sendFn);
      
      // First message should be sent immediately
      await Promise.resolve();
      expect(sendFn).toHaveBeenCalledTimes(1);
      expect(sendFn).toHaveBeenCalledWith(message1);
      
      // Advance time for rate limit
      jest.advanceTimersByTime(100);
      await Promise.resolve();
      
      // Second message should be sent
      expect(sendFn).toHaveBeenCalledTimes(2);
      expect(sendFn).toHaveBeenCalledWith(message2);
    });
    
    afterEach(() => {
      jest.useRealTimers();
    });
  });
});