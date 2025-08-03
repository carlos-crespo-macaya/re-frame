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
