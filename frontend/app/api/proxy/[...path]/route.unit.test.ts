/**
 * Unit tests for the internal access proxy route
 * Focused on testing core functionality without Next.js dependencies
 */

// Mock google-auth-library before importing
const mockRequest = jest.fn();
const mockGetIdTokenClient = jest.fn();
jest.mock('google-auth-library', () => ({
  GoogleAuth: jest.fn().mockImplementation(() => ({
    getIdTokenClient: mockGetIdTokenClient
  }))
}));

// Mock environment variables
const originalEnv = process.env;

describe('Proxy Route Core Logic', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    process.env = { ...originalEnv };

    // Default mock for successful GoogleAuth client
    mockGetIdTokenClient.mockResolvedValue({
      request: mockRequest
    });

    // Default mock for client.request response
    mockRequest.mockResolvedValue({
      status: 200,
      headers: { 'content-type': 'application/json' },
      data: 'mock response data'
    });
  });

  afterAll(() => {
    process.env = originalEnv;
  });

  describe('Environment Detection', () => {
    test('returns 502 when BACKEND_INTERNAL_HOST is not set', async () => {
      delete process.env.BACKEND_INTERNAL_HOST;

      // Import the proxy function after setting environment
      const { GET } = await import('./route');

      const testRequest = {
        method: 'GET',
        headers: new Map(),
        nextUrl: { search: '' },
        arrayBuffer: () => Promise.resolve(new ArrayBuffer(0))
      };

      const response = await GET(testRequest as any, { params: { path: ['api', 'health'] } });

      expect(response.status).toBe(502);
    });

    test('returns 500 error when BACKEND_PUBLIC_URL is not set', async () => {
      process.env.BACKEND_INTERNAL_HOST = 're-frame-backend.europe-west1.internal';
      delete process.env.BACKEND_PUBLIC_URL;

      // Re-import to get updated environment
      jest.resetModules();
      const { GET } = await import('./route');

      const testRequest = {
        method: 'GET',
        headers: new Map(),
        nextUrl: { search: '' },
        arrayBuffer: () => Promise.resolve(new ArrayBuffer(0))
      };

      const response = await GET(testRequest as any, { params: { path: ['api', 'health'] } });
      const json = await response.json();

      expect(response.status).toBe(500);
      expect(json.error).toBe('Service configuration error');
      expect(json.details).toBe('Backend URL not configured. Please check deployment configuration.');
    });

    test('processes request when BACKEND_INTERNAL_HOST is set', async () => {
      process.env.BACKEND_INTERNAL_HOST = 're-frame-backend.europe-west1.internal';
      process.env.BACKEND_PUBLIC_URL = 'https://re-frame-backend-test.a.run.app';

      // Re-import to get updated environment
      jest.resetModules();
      const { GET } = await import('./route');

      const testRequest = {
        method: 'GET',
        headers: new Map([['content-length', '100']]),
        nextUrl: { search: '?test=123' },
        arrayBuffer: () => Promise.resolve(new ArrayBuffer(0))
      };

      const response = await GET(testRequest as any, { params: { path: ['api', 'health'] } });

      expect(mockRequest).toHaveBeenCalledWith({
        url: 'https://re-frame-backend.europe-west1.internal/api/health?test=123',
        method: 'GET',
        headers: expect.any(Object),
        data: undefined,
        responseType: 'stream'
      });
    });
  });

  describe('Request Size Limits', () => {
    beforeEach(() => {
      process.env.BACKEND_INTERNAL_HOST = 're-frame-backend.europe-west1.internal';
      process.env.BACKEND_PUBLIC_URL = 'https://re-frame-backend-test.a.run.app';
    });

    test('accepts requests up to 50MB', async () => {
      const { POST } = await import('./route');

      const testRequest = {
        method: 'POST',
        headers: new Map([['content-length', '52428800']]), // 50MB
        nextUrl: { search: '' },
        arrayBuffer: () => Promise.resolve(new ArrayBuffer(0))
      };

      await POST(testRequest as any, { params: { path: ['api', 'upload'] } });

      expect(mockRequest).toHaveBeenCalled();
    });

    test('returns 413 for requests over 50MB', async () => {
      jest.resetModules();
      const { POST } = await import('./route');

      const testRequest = {
        method: 'POST',
        headers: new Map([['content-length', '52428801']]), // 50MB + 1 byte
        nextUrl: { search: '' },
        arrayBuffer: () => Promise.resolve(new ArrayBuffer(0))
      };

      const response = await POST(testRequest as any, { params: { path: ['api', 'upload'] } });

      expect(response.status).toBe(413);
      expect(mockRequest).not.toHaveBeenCalled();
    });
  });

  describe('HTTP Methods', () => {
    beforeEach(() => {
      process.env.BACKEND_INTERNAL_HOST = 're-frame-backend.europe-west1.internal';
      process.env.BACKEND_PUBLIC_URL = 'https://re-frame-backend-test.a.run.app';
    });

    test.each(['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'])(
      'handles %s method correctly', async (method) => {
        jest.resetModules();
        const handlers = await import('./route');
        const handler = handlers[method as keyof typeof handlers];

        const testRequest = {
          method,
          headers: new Map([['content-length', '100']]),
          nextUrl: { search: '' },
          arrayBuffer: () => Promise.resolve(new ArrayBuffer(0))
        };

        await handler(testRequest as any, { params: { path: ['api', 'test'] } });

        expect(mockRequest).toHaveBeenCalledWith({
          url: 'https://re-frame-backend.europe-west1.internal/api/test',
          method,
          headers: expect.any(Object),
          data: ['GET', 'HEAD'].includes(method) ? undefined : expect.any(ArrayBuffer),
          responseType: 'stream'
        });
      }
    );
  });

  describe('Security Requirements', () => {
    beforeEach(() => {
      process.env.BACKEND_INTERNAL_HOST = 're-frame-backend.europe-west1.internal';
      process.env.BACKEND_PUBLIC_URL = 'https://re-frame-backend-test.a.run.app';
    });

    test('always includes valid IAM ID token via Google Auth client', async () => {
      jest.resetModules();
      const { GET } = await import('./route');

      const testRequest = {
        method: 'GET',
        headers: new Map(),
        nextUrl: { search: '' },
        arrayBuffer: () => Promise.resolve(new ArrayBuffer(0))
      };

      await GET(testRequest as any, { params: { path: ['api', 'health'] } });

      // Step 1: Verify correct audience was used for ID token client (should be public URL)
      expect(mockGetIdTokenClient).toHaveBeenCalledWith('https://re-frame-backend-test.a.run.app');

      // Step 2: Verify the authenticated request was made via client.request
      // Note: The Google Auth library's client.request() automatically adds the Authorization header
      expect(mockRequest).toHaveBeenCalledTimes(1);
      expect(mockRequest).toHaveBeenCalledWith({
        url: 'https://re-frame-backend.europe-west1.internal/api/health',
        method: 'GET',
        headers: {}, // Empty headers object since we remove host and content-length
        data: undefined,
        responseType: 'stream'
      });
    });

    test('uses correct audience for ID token (backend host)', async () => {
      jest.resetModules();
      const { GET } = await import('./route');

      const testRequest = {
        method: 'GET',
        headers: new Map(),
        nextUrl: { search: '' },
        arrayBuffer: () => Promise.resolve(new ArrayBuffer(0))
      };

      await GET(testRequest as any, { params: { path: ['api', 'health'] } });

      // The audience should be the public URL, not the internal host
      expect(mockGetIdTokenClient).toHaveBeenCalledWith('https://re-frame-backend-test.a.run.app');
    });
  });

  describe('SSE and WebSocket Support', () => {
    beforeEach(() => {
      process.env.BACKEND_INTERNAL_HOST = 're-frame-backend.europe-west1.internal';
      process.env.BACKEND_PUBLIC_URL = 'https://re-frame-backend-test.a.run.app';
    });

    test('uses fetch for SSE with proper headers and duplex: half', async () => {
      jest.resetModules();

      // Mock GoogleAuth.getClient used for SSE auth headers
      const getClientMock = jest.fn().mockResolvedValue({
        getRequestHeaders: jest.fn().mockResolvedValue({ Authorization: 'Bearer test-token' })
      });
      (jest.requireMock('google-auth-library') as any).GoogleAuth.mockImplementation(() => ({
        getIdTokenClient: mockGetIdTokenClient,
        getClient: getClientMock
      }));

      // Ensure global fetch exists in this test environment (Node may not provide it)
      if (!(globalThis as any).fetch) {
        (globalThis as any).fetch = jest.fn();
      }

      // Spy on global fetch
      const fetchSpy = jest.spyOn(globalThis as any, 'fetch').mockResolvedValue({
        ok: true,
        status: 200,
        body: 'mock-stream-body'
      } as any);

      const { GET } = await import('./route');

      const testRequest = {
        method: 'GET',
        headers: new Map(),
        nextUrl: { search: '' },
        arrayBuffer: () => Promise.resolve(new ArrayBuffer(0))
      };

      await GET(testRequest as any, { params: { path: ['api', 'events', 'session123'] } });

      expect(fetchSpy).toHaveBeenCalledTimes(1);
      const [, options] = fetchSpy.mock.calls[0];
      expect((options as any).headers['Accept']).toBe('text/event-stream');
      expect((options as any).headers['Cache-Control']).toBe('no-cache');
      expect((options as any).duplex).toBe('half');

      fetchSpy.mockRestore();
    });

    test('sets cache to no-store', async () => {
      jest.resetModules();
      const { GET } = await import('./route');

      const testRequest = {
        method: 'GET',
        headers: new Map(),
        nextUrl: { search: '' },
        arrayBuffer: () => Promise.resolve(new ArrayBuffer(0))
      };

      const response = await GET(testRequest as any, { params: { path: ['api', 'health'] } });

      // Check that the response headers include cache-control: no-store
      expect(response.headers.get('cache-control')).toBe('no-store');
    });
  });

  describe('Request Transformation', () => {
    beforeEach(() => {
      process.env.BACKEND_INTERNAL_HOST = 're-frame-backend.europe-west1.internal';
      process.env.BACKEND_PUBLIC_URL = 'https://re-frame-backend-test.a.run.app';
    });

    test('constructs correct backend URL with path segments', async () => {
      jest.resetModules();
      const { GET } = await import('./route');

      const testRequest = {
        method: 'GET',
        headers: new Map(),
        nextUrl: { search: '' },
        arrayBuffer: () => Promise.resolve(new ArrayBuffer(0))
      };

      await GET(testRequest as any, { params: { path: ['api', 'voice', 'sessions', 'abc123', 'stream'] } });

      expect(mockRequest).toHaveBeenCalledWith(expect.objectContaining({
        url: 'https://re-frame-backend.europe-west1.internal/api/voice/sessions/abc123/stream'
      }));
    });

    test('preserves query parameters', async () => {
      jest.resetModules();
      const { GET } = await import('./route');

      const testRequest = {
        method: 'GET',
        headers: new Map(),
        nextUrl: { search: '?version=1&lang=en' },
        arrayBuffer: () => Promise.resolve(new ArrayBuffer(0))
      };

      await GET(testRequest as any, { params: { path: ['api', 'health'] } });

      expect(mockRequest).toHaveBeenCalledWith(expect.objectContaining({
        url: 'https://re-frame-backend.europe-west1.internal/api/health?version=1&lang=en'
      }));
    });

    test('removes host and content-length headers from request', async () => {
      jest.resetModules();
      const { GET } = await import('./route');

      const testRequest = {
        method: 'GET',
        headers: new Map([
          ['host', 'original-host.com'],
          ['content-length', '12345'],
          ['x-custom-header', 'should-be-preserved'],
          ['authorization', 'Bearer old-token'] // Should also be preserved (Google adds its own)
        ]),
        nextUrl: { search: '' },
        arrayBuffer: () => Promise.resolve(new ArrayBuffer(0))
      };

      await GET(testRequest as any, { params: { path: ['api', 'health'] } });

      expect(mockRequest).toHaveBeenCalledWith({
        url: 'https://re-frame-backend.europe-west1.internal/api/health',
        method: 'GET',
        headers: {
          'x-custom-header': 'should-be-preserved',
          'authorization': 'Bearer old-token'
          // host and content-length should be removed
        },
        data: undefined,
        responseType: 'stream'
      });

      // Explicitly verify problematic headers were removed
      const callHeaders = mockRequest.mock.calls[0][0].headers;
      expect(callHeaders).not.toHaveProperty('host');
      expect(callHeaders).not.toHaveProperty('content-length');

      // Verify other headers were preserved
      expect(callHeaders['x-custom-header']).toBe('should-be-preserved');
    });

    test('cleans response headers properly', async () => {
      jest.resetModules();

      // Mock response with problematic headers
      mockRequest.mockResolvedValue({
        status: 200,
        headers: {
          'content-type': 'application/json',
          'host': 'backend-host.internal',
          'content-encoding': 'gzip',
          'transfer-encoding': 'chunked',
          'x-custom-header': 'should-be-preserved',
          'cache-control': 'max-age=3600' // Should be overridden
        },
        data: '{"test": "data"}'
      });

      const { GET } = await import('./route');

      const testRequest = {
        method: 'GET',
        headers: new Map(),
        nextUrl: { search: '' },
        arrayBuffer: () => Promise.resolve(new ArrayBuffer(0))
      };

      const response = await GET(testRequest as any, { params: { path: ['api', 'health'] } });

      // Verify response headers are cleaned
      expect(response.headers.get('content-type')).toBe('application/json');
      expect(response.headers.get('cache-control')).toBe('no-store'); // Should be overridden
      expect(response.headers.get('x-custom-header')).toBe('should-be-preserved');

      // Verify problematic headers are removed (not present in response)
      expect(response.headers.get('host')).toBeFalsy();
      expect(response.headers.get('content-encoding')).toBeFalsy();
      expect(response.headers.get('transfer-encoding')).toBeFalsy();
    });

    test('sets default content-type when missing', async () => {
      jest.resetModules();

      // Mock response without content-type
      mockRequest.mockResolvedValue({
        status: 200,
        headers: {
          'x-custom-header': 'test'
        },
        data: 'raw data'
      });

      const { GET } = await import('./route');

      const testRequest = {
        method: 'GET',
        headers: new Map(),
        nextUrl: { search: '' },
        arrayBuffer: () => Promise.resolve(new ArrayBuffer(0))
      };

      const response = await GET(testRequest as any, { params: { path: ['api', 'data'] } });

      // Verify default content-type is set
      expect(response.headers.get('content-type')).toBe('application/octet-stream');
    });
  });
});
