/**
 * Tests for message protocol
 */

import {
  createClientMessage,
  isServerMessage,
  isErrorMessage,
  isStatusMessage,
  type ServerMessage,
  type ErrorMessage,
  type StatusMessage
} from '../message-protocol';

describe('Message Protocol', () => {
  describe('createClientMessage', () => {
    it('should create a valid client message', () => {
      const message = createClientMessage({
        mimeType: 'text/plain',
        data: 'Hello world',
        messageType: 'thought',
        sessionId: 'test-session',
        turnComplete: true
      });
      
      expect(message).toMatchObject({
        mime_type: 'text/plain',
        data: 'Hello world',
        message_type: 'thought',
        session_id: 'test-session',
        turn_complete: true
      });
      expect(message.timestamp).toBeDefined();
    });
  });
  
  describe('Type Guards', () => {
    it('should identify server messages', () => {
      const validMessage: ServerMessage = {
        mime_type: 'text/plain',
        data: 'Response',
        message_type: 'response',
        session_id: 'test',
        is_final: true
      };
      
      expect(isServerMessage(validMessage)).toBe(true);
      expect(isServerMessage({})).toBe(false);
      expect(isServerMessage(null)).toBe(false);
    });
    
    it('should identify error messages', () => {
      const errorMessage: ErrorMessage = {
        message_type: 'error',
        error_code: 'CONN_FAILED',
        error_message: 'Connection failed',
        session_id: 'test',
        timestamp: Date.now()
      };
      
      expect(isErrorMessage(errorMessage)).toBe(true);
      expect(isErrorMessage({ message_type: 'status' })).toBe(false);
    });
    
    it('should identify status messages', () => {
      const statusMessage: StatusMessage = {
        message_type: 'status',
        status: 'connected',
        session_id: 'test',
        timestamp: Date.now()
      };
      
      expect(isStatusMessage(statusMessage)).toBe(true);
      expect(isStatusMessage({ message_type: 'error' })).toBe(false);
    });
  });
});