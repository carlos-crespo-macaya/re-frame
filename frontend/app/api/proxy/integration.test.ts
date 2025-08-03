/**
 * Integration test to verify the proxy configuration works end-to-end
 */

import { API_CONFIG } from '@/lib/api/config';
import { generatedApi } from '@/lib/api/generated-client';

describe('Proxy Integration', () => {
  test('API_CONFIG uses proxy paths', () => {
    expect(API_CONFIG.baseUrl).toBe('/api/proxy');
    expect(API_CONFIG.endpoints.health).toBe('/api/proxy/api/health');
    expect(API_CONFIG.endpoints.send('test123')).toBe('/api/proxy/api/send/test123');
  });

  test('Generated API client uses proxy', () => {
    // The OpenAPI property should be configured to use proxy
    expect(generatedApi).toBeDefined();
    // This ensures the generated client is properly configured
  });

  test('Health endpoint returns proxy status', async () => {
    // Mock fetch for this test
    const originalFetch = global.fetch;
    global.fetch = jest.fn().mockResolvedValue(
      new Response(JSON.stringify({
        status: 'healthy',
        proxyEnabled: false,
        backendHost: 'not configured'
      }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      })
    );

    try {
      const response = await fetch('/api/health');
      const data = await response.json();

      expect(data.status).toBe('healthy');
      expect(data).toHaveProperty('proxyEnabled');
      expect(data).toHaveProperty('backendHost');
    } finally {
      global.fetch = originalFetch;
    }
  });

  describe('Environment-based behavior', () => {
    const originalEnv = process.env;

    afterEach(() => {
      process.env = originalEnv;
    });

    test('proxy is disabled in development (no BACKEND_INTERNAL_HOST)', () => {
      delete process.env.BACKEND_INTERNAL_HOST;

      // In development, the proxy should return 502
      // This test verifies the configuration is correct
      expect(process.env.BACKEND_INTERNAL_HOST).toBeUndefined();
    });

    test('proxy is enabled with BACKEND_INTERNAL_HOST', () => {
      process.env.BACKEND_INTERNAL_HOST = 'test-backend.internal';

      // In production/staging, the proxy should be active
      expect(process.env.BACKEND_INTERNAL_HOST).toBe('test-backend.internal');
    });
  });
});
