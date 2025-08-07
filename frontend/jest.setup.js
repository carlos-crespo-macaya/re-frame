// Learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom'

// Mock Next.js navigation
const mockPush = jest.fn()
const mockReplace = jest.fn()
const mockRefresh = jest.fn()
const mockBack = jest.fn()
const mockForward = jest.fn()
const mockPrefetch = jest.fn()

jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
    replace: mockReplace,
    refresh: mockRefresh,
    back: mockBack,
    forward: mockForward,
    prefetch: mockPrefetch,
    pathname: '/',
    route: '/',
    query: {},
    asPath: '/',
  }),
  usePathname: () => '/en/about',
  useSearchParams: () => new URLSearchParams(),
  useParams: () => ({ locale: 'en' }),
  notFound: jest.fn(),
  redirect: jest.fn(),
}))

// Mock next/link
jest.mock('next/link', () => {
  const React = require('react')
  return React.forwardRef(({ children, href, ...props }, ref) => {
    return React.createElement('a', { href, ref, ...props }, children)
  })
})

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
})

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
  takeRecords() {
    return []
  }
}

// Mock Next.js server components for API route testing
global.Request = class Request {
  constructor(input, init) {
    this.url = typeof input === 'string' ? input : input.url;
    this.method = init?.method || 'GET';
    this.headers = new Map(Object.entries(init?.headers || {}));
    this.body = init?.body;
  }

  text() {
    return Promise.resolve(this.body || '');
  }

  json() {
    return Promise.resolve(JSON.parse(this.body || '{}'));
  }

  arrayBuffer() {
    return Promise.resolve(new ArrayBuffer(0));
  }
}

global.Response = class Response {
  constructor(body, init) {
    this.body = body;
    this.status = init?.status || 200;
    this.headers = new Map(Object.entries(init?.headers || {}));
  }

  text() {
    if (this.body instanceof ReadableStream) {
      return Promise.resolve('');
    }
    return Promise.resolve(this.body || '');
  }

  json() {
    return Promise.resolve(JSON.parse(this.body || '{}'));
  }
}

global.Headers = class Headers {
  constructor(init = {}) {
    this.map = new Map(Object.entries(init));
  }

  get(name) {
    return this.map.get(name.toLowerCase());
  }

  set(name, value) {
    this.map.set(name.toLowerCase(), value);
  }

  has(name) {
    return this.map.has(name.toLowerCase());
  }

  entries() {
    return this.map.entries();
  }

  forEach(callback) {
    this.map.forEach(callback);
  }
}

global.ReadableStream = class ReadableStream {
  constructor(underlyingSource) {
    this.underlyingSource = underlyingSource;
  }
}

// Mock Next.js NextResponse for API route testing
jest.mock('next/server', () => ({
  NextRequest: class NextRequest {
    constructor(input, init) {
      this.url = typeof input === 'string' ? input : input.url;
      this.method = init?.method || 'GET';
      this.headers = new Map(Object.entries(init?.headers || {}));
      this.body = init?.body;
      this.nextUrl = { search: '' };
    }

    text() {
      return Promise.resolve(this.body || '');
    }

    json() {
      return Promise.resolve(JSON.parse(this.body || '{}'));
    }

    arrayBuffer() {
      return Promise.resolve(new ArrayBuffer(0));
    }
  },
  NextResponse: class NextResponse extends Response {
    constructor(body, init) {
      super(body, init);
    }

    static json(data, init) {
      return new NextResponse(JSON.stringify(data), {
        status: init?.status || 200,
        headers: {
          'Content-Type': 'application/json',
          ...init?.headers
        }
      });
    }
  }
}))
