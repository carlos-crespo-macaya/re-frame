import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ErrorFallback from '../ErrorFallback'

describe('ErrorFallback', () => {
  const mockReset = jest.fn()
  const mockError = new Error('Test error message')

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders error message', () => {
    render(<ErrorFallback error={mockError} reset={mockReset} />)
    
    expect(screen.getByText('Something went wrong')).toBeInTheDocument()
    expect(screen.getByText(/We apologize for the inconvenience/)).toBeInTheDocument()
  })

  it('renders try again button', () => {
    render(<ErrorFallback error={mockError} reset={mockReset} />)
    
    const tryAgainButton = screen.getByRole('button', { name: /try again/i })
    expect(tryAgainButton).toBeInTheDocument()
  })

  it('renders home link', () => {
    render(<ErrorFallback error={mockError} reset={mockReset} />)
    
    const homeLink = screen.getByRole('link', { name: /return to home/i })
    expect(homeLink).toBeInTheDocument()
    expect(homeLink).toHaveAttribute('href', '/')
  })

  it('calls reset function when try again is clicked', async () => {
    const user = userEvent.setup()
    render(<ErrorFallback error={mockError} reset={mockReset} />)
    
    await user.click(screen.getByRole('button', { name: /try again/i }))
    
    expect(mockReset).toHaveBeenCalledTimes(1)
  })

  it('shows error details in development mode', () => {
    const originalEnv = process.env.NODE_ENV
    Object.defineProperty(process.env, 'NODE_ENV', {
      configurable: true,
      value: 'development'
    })
    
    render(<ErrorFallback error={mockError} reset={mockReset} />)
    
    const detailsElement = screen.getByText(/error details/i)
    expect(detailsElement).toBeInTheDocument()
    
    // Error message should be visible in the pre element
    const preElement = screen.getByText((content, element) => {
      return element?.tagName === 'PRE' && content.includes(mockError.message)
    })
    expect(preElement).toBeInTheDocument()
    
    Object.defineProperty(process.env, 'NODE_ENV', {
      configurable: true,
      value: originalEnv
    })
  })

  it('hides error details in production mode', () => {
    const originalEnv = process.env.NODE_ENV
    Object.defineProperty(process.env, 'NODE_ENV', {
      configurable: true,
      value: 'production'
    })
    
    render(<ErrorFallback error={mockError} reset={mockReset} />)
    
    expect(screen.queryByText(/error details/i)).not.toBeInTheDocument()
    
    Object.defineProperty(process.env, 'NODE_ENV', {
      configurable: true,
      value: originalEnv
    })
  })

  it('handles errors with stack traces', () => {
    const originalEnv = process.env.NODE_ENV
    Object.defineProperty(process.env, 'NODE_ENV', {
      configurable: true,
      value: 'development'
    })
    
    const errorWithStack = new Error('Test error')
    errorWithStack.stack = 'Error: Test error\n    at TestComponent'
    
    render(<ErrorFallback error={errorWithStack} reset={mockReset} />)
    
    expect(screen.getByText(/at TestComponent/)).toBeInTheDocument()
    
    Object.defineProperty(process.env, 'NODE_ENV', {
      configurable: true,
      value: originalEnv
    })
  })

  it('is accessible with proper ARIA attributes', () => {
    render(<ErrorFallback error={mockError} reset={mockReset} />)
    
    // Main content should be in a main landmark
    const mainContent = screen.getByRole('main')
    expect(mainContent).toBeInTheDocument()
    
    // Error alert should have proper role
    const errorAlert = screen.getByRole('alert')
    expect(errorAlert).toBeInTheDocument()
  })

  it('supports keyboard navigation', async () => {
    const user = userEvent.setup()
    render(<ErrorFallback error={mockError} reset={mockReset} />)
    
    // Tab to try again button
    await user.tab()
    expect(screen.getByRole('button', { name: /try again/i })).toHaveFocus()
    
    // Tab to home link
    await user.tab()
    expect(screen.getByRole('link', { name: /return to home/i })).toHaveFocus()
  })

  it('has proper styling for dark mode', () => {
    render(<ErrorFallback error={mockError} reset={mockReset} />)
    
    const heading = screen.getByText('Something went wrong')
    expect(heading).toHaveClass('dark:text-neutral-100')
    
    const description = screen.getByText(/We apologize for the inconvenience/)
    expect(description).toHaveClass('dark:text-neutral-400')
  })
})