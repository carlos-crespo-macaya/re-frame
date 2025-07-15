/**
 * Tests for the generated API client integration
 */

import { generatedApi } from '../generated-client'
import type { MessageRequest, HealthCheckResponse } from '../generated/types.gen'

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
    const endpoint = generatedApi.events.getEndpoint(sessionId, 'true', 'es-ES')
    
    expect(endpoint).toBe('/api/events/test-session-123?is_audio=true&language=es-ES')
  })
})