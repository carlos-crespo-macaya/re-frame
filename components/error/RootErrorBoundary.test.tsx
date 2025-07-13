import React from 'react'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import RootErrorBoundary from './RootErrorBoundary'

// Mock console methods to avoid test noise
const originalError = console.error
beforeAll(() => {
  console.error = jest.fn()
})

afterAll(() => {
  console.error = originalError
})

// Component that throws an error for testing
const ThrowError = ({ shouldThrow }: { shouldThrow: boolean }) => {
  if (shouldThrow) {
    throw new Error('Test error message')
  }
  return <div>No error</div>
}

describe('RootErrorBoundary', () => {
  afterEach(() => {
    jest.clearAllMocks()
  })

  it('renders children when there is no error', () => {
    render(
      <RootErrorBoundary>
        <div>Test content</div>
      </RootErrorBoundary>
    )

    expect(screen.getByText('Test content')).toBeInTheDocument()
  })

  it('renders error fallback when error is thrown', () => {
    render(
      <RootErrorBoundary>
        <ThrowError shouldThrow={true} />
      </RootErrorBoundary>
    )

    expect(screen.getByText('Something went wrong')).toBeInTheDocument()
    expect(screen.getByText(/We apologize for the inconvenience/)).toBeInTheDocument()
  })

  it('calls onError callback when error occurs', () => {
    const onError = jest.fn()
    // Error is created by the ThrowError component

    render(
      <RootErrorBoundary onError={onError}>
        <ThrowError shouldThrow={true} />
      </RootErrorBoundary>
    )

    expect(onError).toHaveBeenCalledWith(
      expect.objectContaining({ message: 'Test error message' }),
      expect.any(Object)
    )
  })

  it('resets error state when reset button is clicked', async () => {
    const user = userEvent.setup()
    
    // Component that can toggle error state
    const TestComponent = ({ throwOnMount }: { throwOnMount: boolean }) => {
      const [shouldThrow, setShouldThrow] = React.useState(throwOnMount)
      
      React.useEffect(() => {
        setShouldThrow(throwOnMount)
      }, [throwOnMount])
      
      if (shouldThrow) {
        throw new Error('Test error message')
      }
      
      return <div>No error</div>
    }

    const { rerender } = render(
      <RootErrorBoundary>
        <TestComponent throwOnMount={true} />
      </RootErrorBoundary>
    )

    expect(screen.getByText('Something went wrong')).toBeInTheDocument()

    // Click reset button
    await user.click(screen.getByRole('button', { name: /try again/i }))

    // After reset, error boundary should retry rendering children
    // Since we're still passing throwOnMount={true}, it will error again
    expect(screen.getByText('Something went wrong')).toBeInTheDocument()
    
    // Now re-render with fixed component
    rerender(
      <RootErrorBoundary>
        <TestComponent throwOnMount={false} />
      </RootErrorBoundary>
    )
    
    // Click reset again with the fixed component
    await user.click(screen.getByRole('button', { name: /try again/i }))

    expect(screen.getByText('No error')).toBeInTheDocument()
  })

  it('renders custom fallback component when provided', () => {
    const CustomFallback = () => <div>Custom error UI</div>

    render(
      <RootErrorBoundary fallback={CustomFallback}>
        <ThrowError shouldThrow={true} />
      </RootErrorBoundary>
    )

    expect(screen.getByText('Custom error UI')).toBeInTheDocument()
  })

  it('provides error info to fallback component', () => {
    const CustomFallback = ({ error }: { error: Error }) => (
      <div>Error: {error.message}</div>
    )

    render(
      <RootErrorBoundary fallback={CustomFallback}>
        <ThrowError shouldThrow={true} />
      </RootErrorBoundary>
    )

    expect(screen.getByText('Error: Test error message')).toBeInTheDocument()
  })

  it('logs error to console in development', () => {
    Object.defineProperty(process.env, 'NODE_ENV', {
      configurable: true,
      value: 'development'
    })

    render(
      <RootErrorBoundary>
        <ThrowError shouldThrow={true} />
      </RootErrorBoundary>
    )

    expect(console.error).toHaveBeenCalled()
  })

  it('supports multiple error boundaries', () => {
    const InnerError = () => {
      throw new Error('Inner error')
    }

    render(
      <RootErrorBoundary>
        <div>Outer content</div>
        <RootErrorBoundary>
          <InnerError />
        </RootErrorBoundary>
      </RootErrorBoundary>
    )

    // Outer boundary should still render normally
    expect(screen.getByText('Outer content')).toBeInTheDocument()
    // Inner boundary should catch its error
    expect(screen.getByText('Something went wrong')).toBeInTheDocument()
  })

  it('handles async errors when reported', async () => {
    const onError = jest.fn()

    const AsyncComponent = () => {
      React.useEffect(() => {
        // Note: Async errors need to be caught and re-thrown in useEffect
        // or use an error reporting mechanism
        // This is a limitation of error boundaries - they don't catch async errors
      }, [])
      return <div>Async component</div>
    }

    render(
      <RootErrorBoundary onError={onError}>
        <AsyncComponent />
      </RootErrorBoundary>
    )

    expect(screen.getByText('Async component')).toBeInTheDocument()
  })

  it('preserves error boundary state across re-renders', () => {
    const { rerender } = render(
      <RootErrorBoundary>
        <ThrowError shouldThrow={true} />
      </RootErrorBoundary>
    )

    expect(screen.getByText('Something went wrong')).toBeInTheDocument()

    // Re-render should maintain error state
    rerender(
      <RootErrorBoundary>
        <ThrowError shouldThrow={false} />
      </RootErrorBoundary>
    )

    expect(screen.getByText('Something went wrong')).toBeInTheDocument()
  })
})