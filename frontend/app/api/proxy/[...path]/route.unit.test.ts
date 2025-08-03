/**
 * Unit tests for the internal access proxy route
 * Focused on testing core functionality without Next.js dependencies
 */

// Mock google-auth-library before importing
const mockGetRequestHeaders = jest.fn();
const mockGetIdTokenClient = jest.fn();
jest.mock('google-auth-library', () => ({
  GoogleAuth: jest.fn().mockImplementation(() => ({
    getIdTokenClient: mockGetIdTokenClient
  }))
}));

// Mock global fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

// Mock environment variables
const originalEnv = process.env;

describe('Proxy Route Core Logic', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    process.env = { ...originalEnv };

    // Default mock for successful IAM token fetch
    mockGetRequestHeaders.mockResolvedValue({
      authorization: 'Bearer mock-id-token-123'
    });
    mockGetIdTokenClient.mockResolvedValue({
      getRequestHeaders: mockGetRequestHeaders
    });

    // Default mock for fetch response
    const mockReadableStream = {
      getReader: () => ({
        read: () => Promise.resolve({ done: true, value: undefined })
      })
    };

    mockFetch.mockResolvedValue({
      status: 200,
      headers: new Map([['Content-Type', 'application/json']]),
      body: mockReadableStream
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

      const mockRequest = {
        method: 'GET',
        headers: new Map(),
        nextUrl: { search: '' },
        arrayBuffer: () => Promise.resolve(new ArrayBuffer(0))
      };

      const response = await GET(mockRequest as any, { params: { path: ['api', 'health'] } });

      expect(response.status).toBe(502);
    });

    test('processes request when BACKEND_INTERNAL_HOST is set', async () => {
      process.env.BACKEND_INTERNAL_HOST = 're-frame-backend.europe-west1.internal';

      // Re-import to get updated environment
      jest.resetModules();
      const { GET } = await import('./route');

      const mockRequest = {
        method: 'GET',
        headers: new Map([['content-length', '100']]),
        nextUrl: { search: '?test=123' },
        arrayBuffer: () => Promise.resolve(new ArrayBuffer(0))
      };

      const response = await GET(mockRequest as any, { params: { path: ['api', 'health'] } });

      expect(mockFetch).toHaveBeenCalledWith(
        'https://re-frame-backend.europe-west1.internal/api/health?test=123',
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            authorization: 'Bearer mock-id-token-123',
            host: 're-frame-backend.europe-west1.internal'
          })
        })
      );
    });
  });

  describe('Request Size Limits', () => {
    beforeEach(() => {
      process.env.BACKEND_INTERNAL_HOST = 're-frame-backend.europe-west1.internal';
    });

    test('accepts requests up to 50MB', async () => {
      const { POST } = await import('./route');

      const mockRequest = {
        method: 'POST',
        headers: new Map([['content-length', '52428800']]), // 50MB
        nextUrl: { search: '' },
        arrayBuffer: () => Promise.resolve(new ArrayBuffer(0))
      };

      await POST(mockRequest as any, { params: { path: ['api', 'upload'] } });

      expect(mockFetch).toHaveBeenCalled();
    });

    test('returns 413 for requests over 50MB', async () => {
      jest.resetModules();
      const { POST } = await import('./route');

      const mockRequest = {
        method: 'POST',
        headers: new Map([['content-length', '52428801']]), // 50MB + 1 byte
        nextUrl: { search: '' },
        arrayBuffer: () => Promise.resolve(new ArrayBuffer(0))
      };

      const response = await POST(mockRequest as any, { params: { path: ['api', 'upload'] } });

      expect(response.status).toBe(413);
      expect(mockFetch).not.toHaveBeenCalled();
    });
  });

  describe('HTTP Methods', () => {
    beforeEach(() => {
      process.env.BACKEND_INTERNAL_HOST = 're-frame-backend.europe-west1.internal';
    });

    test.each(['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'])(
      'handles %s method correctly', async (method) => {
        jest.resetModules();
        const handlers = await import('./route');
        const handler = handlers[method as keyof typeof handlers];

        const mockRequest = {
          method,
          headers: new Map([['content-length', '100']]),
          nextUrl: { search: '' },
          arrayBuffer: () => Promise.resolve(new ArrayBuffer(0))
        };

        await handler(mockRequest as any, { params: { path: ['api', 'test'] } });

        expect(mockFetch).toHaveBeenCalledWith(
          'https://re-frame-backend.europe-west1.internal/api/test',
          expect.objectContaining({
            method,
            headers: expect.objectContaining({
              authorization: 'Bearer mock-id-token-123',
              host: 're-frame-backend.europe-west1.internal'
            })
          })
        );
      }
    );
  });

  describe('Security Requirements', () => {
    beforeEach(() => {
      process.env.BACKEND_INTERNAL_HOST = 're-frame-backend.europe-west1.internal';
    });

    test('always includes valid IAM ID token', async () => {
      jest.resetModules();
      const { GET } = await import('./route');

      const mockRequest = {
        method: 'GET',
        headers: new Map(),
        nextUrl: { search: '' },
        arrayBuffer: () => Promise.resolve(new ArrayBuffer(0))
      };

      await GET(mockRequest as any, { params: { path: ['api', 'health'] } });

      expect(mockGetIdTokenClient).toHaveBeenCalledWith('https://re-frame-backend.europe-west1.internal');

      const fetchCall = mockFetch.mock.calls[0];
      const headers = fetchCall[1].headers;
      expect(headers.authorization).toBe('Bearer mock-id-token-123');
    });

    test('uses correct audience for ID token (backend host)', async () => {
      jest.resetModules();
      const { GET } = await import('./route');

      const mockRequest = {
        method: 'GET',
        headers: new Map(),
        nextUrl: { search: '' },
        arrayBuffer: () => Promise.resolve(new ArrayBuffer(0))
      };

      await GET(mockRequest as any, { params: { path: ['api', 'health'] } });

      expect(mockGetIdTokenClient).toHaveBeenCalledWith('https://re-frame-backend.europe-west1.internal');
    });
  });

  describe('SSE and WebSocket Support', () => {
    beforeEach(() => {
      process.env.BACKEND_INTERNAL_HOST = 're-frame-backend.europe-west1.internal';
    });

    test('includes duplex: half flag in fetch options', async () => {
      jest.resetModules();
      const { GET } = await import('./route');

      const mockRequest = {
        method: 'GET',
        headers: new Map(),
        nextUrl: { search: '' },
        arrayBuffer: () => Promise.resolve(new ArrayBuffer(0))
      };

      await GET(mockRequest as any, { params: { path: ['api', 'events', 'session123'] } });

      const fetchCall = mockFetch.mock.calls[0];
      const options = fetchCall[1];
      expect(options.duplex).toBe('half');
    });

    test('sets cache to no-store', async () => {
      jest.resetModules();
      const { GET } = await import('./route');

      const mockRequest = {
        method: 'GET',
        headers: new Map(),
        nextUrl: { search: '' },
        arrayBuffer: () => Promise.resolve(new ArrayBuffer(0))
      };

      await GET(mockRequest as any, { params: { path: ['api', 'health'] } });

      const fetchCall = mockFetch.mock.calls[0];
      const options = fetchCall[1];
      expect(options.cache).toBe('no-store');
    });
  });

  describe('Request Transformation', () => {
    beforeEach(() => {
      process.env.BACKEND_INTERNAL_HOST = 're-frame-backend.europe-west1.internal';
    });

    test('constructs correct backend URL with path segments', async () => {
      jest.resetModules();
      const { GET } = await import('./route');

      const mockRequest = {
        method: 'GET',
        headers: new Map(),
        nextUrl: { search: '' },
        arrayBuffer: () => Promise.resolve(new ArrayBuffer(0))
      };

      await GET(mockRequest as any, { params: { path: ['api', 'voice', 'sessions', 'abc123', 'stream'] } });

      expect(mockFetch).toHaveBeenCalledWith(
        'https://re-frame-backend.europe-west1.internal/api/voice/sessions/abc123/stream',
        expect.any(Object)
      );
    });

    test('preserves query parameters', async () => {
      jest.resetModules();
      const { GET } = await import('./route');

      const mockRequest = {
        method: 'GET',
        headers: new Map(),
        nextUrl: { search: '?version=1&lang=en' },
        arrayBuffer: () => Promise.resolve(new ArrayBuffer(0))
      };

      await GET(mockRequest as any, { params: { path: ['api', 'health'] } });

      expect(mockFetch).toHaveBeenCalledWith(
        'https://re-frame-backend.europe-west1.internal/api/health?version=1&lang=en',
        expect.any(Object)
      );
    });

    test('sets host header to backend host', async () => {
      jest.resetModules();
      const { GET } = await import('./route');

      const mockRequest = {
        method: 'GET',
        headers: new Map(),
        nextUrl: { search: '' },
        arrayBuffer: () => Promise.resolve(new ArrayBuffer(0))
      };

      await GET(mockRequest as any, { params: { path: ['api', 'health'] } });

      const fetchCall = mockFetch.mock.calls[0];
      const headers = fetchCall[1].headers;
      expect(headers.host).toBe('re-frame-backend.europe-west1.internal');
    });
  });
});
