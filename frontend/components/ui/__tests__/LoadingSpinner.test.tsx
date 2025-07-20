import { render, screen } from '@testing-library/react'
import LoadingSpinner from '../LoadingSpinner'

describe('LoadingSpinner', () => {
  it('renders with default props', () => {
    render(<LoadingSpinner />)
    
    const spinner = screen.getByRole('status')
    expect(spinner).toBeInTheDocument()
    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('renders with custom label', () => {
    render(<LoadingSpinner label="Processing..." />)
    
    expect(screen.getByText('Processing...')).toBeInTheDocument()
  })

  it('renders without label when showLabel is false', () => {
    render(<LoadingSpinner showLabel={false} />)
    
    expect(screen.queryByText('Loading...')).toHaveClass('sr-only')
  })

  it('renders with small size', () => {
    render(<LoadingSpinner size="sm" />)
    
    const spinner = screen.getByRole('status')
    expect(spinner.firstChild).toHaveClass('w-4', 'h-4')
  })

  it('renders with medium size', () => {
    render(<LoadingSpinner size="md" />)
    
    const spinner = screen.getByRole('status')
    expect(spinner.firstChild).toHaveClass('w-6', 'h-6')
  })

  it('renders with large size', () => {
    render(<LoadingSpinner size="lg" />)
    
    const spinner = screen.getByRole('status')
    expect(spinner.firstChild).toHaveClass('w-8', 'h-8')
  })

  it('renders inline variant', () => {
    render(<LoadingSpinner variant="inline" />)
    
    const spinner = screen.getByRole('status')
    expect(spinner).toHaveClass('inline-flex')
  })

  it('renders centered variant', () => {
    render(<LoadingSpinner variant="centered" />)
    
    const spinner = screen.getByRole('status')
    expect(spinner).toHaveClass('flex', 'justify-center')
  })

  it('renders fullscreen variant', () => {
    render(<LoadingSpinner variant="fullscreen" />)
    
    const spinner = screen.getByRole('status')
    expect(spinner).toHaveClass('fixed', 'inset-0')
  })

  it('applies custom className', () => {
    render(<LoadingSpinner className="custom-class" />)
    
    const spinner = screen.getByRole('status')
    expect(spinner).toHaveClass('custom-class')
  })

  it('supports custom colors', () => {
    render(<LoadingSpinner color="primary" />)
    
    const spinner = screen.getByRole('status')
    const svg = spinner.querySelector('svg')
    expect(svg).toHaveClass('text-primary-600')
  })

  it('has proper ARIA attributes', () => {
    render(<LoadingSpinner label="Custom loading" />)
    
    const spinner = screen.getByRole('status')
    expect(spinner).toHaveAttribute('aria-busy', 'true')
    expect(spinner).toHaveAttribute('aria-label', 'Custom loading')
  })

  it('respects reduced motion preference', () => {
    // Mock matchMedia for reduced motion
    window.matchMedia = jest.fn().mockImplementation(query => ({
      matches: query === '(prefers-reduced-motion: reduce)',
      media: query,
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
    }))

    render(<LoadingSpinner />)
    
    const svg = screen.getByRole('status').querySelector('svg')
    expect(svg).toHaveClass('motion-safe:animate-spin')
  })
})