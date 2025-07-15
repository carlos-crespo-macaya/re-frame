/**
 * Tests for the generated API client integration
 */

import { generatedApi } from '../generated-client'
import type { MessageRequest, HealthCheckResponse, LanguageDetectionRequest } from '../generated/types.gen'

describe('Generated API Client', () => {
  it('should have properly typed methods', () => {
    // This test verifies TypeScript compilation with the generated types
    expect(generatedApi.health.check).toBeDefined()
    expect(generatedApi.sessions.get).toBeDefined()
    expect(generatedApi.sessions.list).toBeDefined()
    expect(generatedApi.messages.send).toBeDefined()
    expect(generatedApi.language.detect).toBeDefined()
  })

  it('should enforce type safety for message requests', () => {
    // This will fail TypeScript compilation if types don't match
    const validRequest: MessageRequest = {
      mime_type: 'text/plain',
      data: 'SGVsbG8gd29ybGQ=', // Base64 encoded "Hello world"
    }

    // This would fail TypeScript compilation:
    // const invalidRequest: MessageRequest = {
    //   mimeType: 'text/plain', // Wrong property name
    //   data: 'test',
    // }

    expect(validRequest.mime_type).toBe('text/plain')
    expect(validRequest.data).toBe('SGVsbG8gd29ybGQ=')
  })

  it('should have proper health check response type', () => {
    // This verifies the response type structure
    const mockResponse: HealthCheckResponse = {
      status: 'healthy',
      service: 'CBT Reframing Assistant API',
      timestamp: new Date().toISOString(),
      version: '1.0.0',
    }

    // TypeScript ensures status can only be 'healthy' or 'unhealthy'
    expect(mockResponse.status).toBe('healthy')
    
    // This would fail TypeScript compilation:
    // mockResponse.status = 'invalid-status'
  })

  it('should generate proper SSE endpoint URLs', () => {
    const sessionId = 'test-session-123'
    const endpoint = generatedApi.events.getEventStreamEndpoint(sessionId, 'true', 'es-ES')
    
    expect(endpoint).toBe('/api/events/test-session-123?is_audio=true&language=es-ES')
  })

  it('should have sessions.downloadPdf method', () => {
    expect(generatedApi.sessions.downloadPdf).toBeDefined()
    expect(typeof generatedApi.sessions.downloadPdf).toBe('function')
    
    // Verify it accepts a session ID parameter
    const mockDownload = generatedApi.sessions.downloadPdf as jest.Mock
    if (mockDownload.mockImplementation) {
      mockDownload('test-session-123')
      expect(mockDownload).toHaveBeenCalledWith('test-session-123')
    }
  })

  it('should have language.detect method with proper typing', () => {
    expect(generatedApi.language.detect).toBeDefined()
    expect(typeof generatedApi.language.detect).toBe('function')
    
    // This verifies the type structure
    const mockRequest: LanguageDetectionRequest = {
      text: 'Hello, how are you?'
    }
    
    // TypeScript will ensure the request matches the expected type
    expect(mockRequest.text).toBe('Hello, how are you?')
  })
})