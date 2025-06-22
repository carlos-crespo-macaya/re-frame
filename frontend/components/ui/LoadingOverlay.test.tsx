import { render, screen } from '@testing-library/react'
import LoadingOverlay from './LoadingOverlay'

describe('LoadingOverlay', () => {
  it('renders when isLoading is true', () => {
    render(<LoadingOverlay isLoading={true} />)
    
    expect(screen.getByRole('status')).toBeInTheDocument()
  })

  it('does not render when isLoading is false', () => {
    render(<LoadingOverlay isLoading={false} />)
    
    expect(screen.queryByRole('status')).not.toBeInTheDocument()
  })

  it('renders with custom label', () => {
    render(<LoadingOverlay isLoading={true} label="Processing data..." />)
    
    expect(screen.getByText('Processing data...')).toBeInTheDocument()
  })

  it('renders with spinner size', () => {
    render(<LoadingOverlay isLoading={true} spinnerSize="lg" />)
    
    const spinner = screen.getByRole('status').querySelector('svg')
    expect(spinner).toHaveClass('w-8', 'h-8')
  })

  it('renders with fullscreen variant', () => {
    render(<LoadingOverlay isLoading={true} variant="fullscreen" />)
    
    const overlay = screen.getByRole('status').parentElement?.parentElement
    expect(overlay).toHaveClass('fixed', 'inset-0')
  })

  it('renders with contained variant', () => {
    render(<LoadingOverlay isLoading={true} variant="contained" />)
    
    const overlay = screen.getByRole('status').parentElement?.parentElement
    expect(overlay).toHaveClass('absolute', 'inset-0')
  })

  it('renders with inline variant', () => {
    render(<LoadingOverlay isLoading={true} variant="inline" />)
    
    const overlay = screen.getByRole('status').parentElement?.parentElement
    expect(overlay).toHaveClass('relative')
  })

  it('has proper backdrop blur', () => {
    render(<LoadingOverlay isLoading={true} blur={true} />)
    
    const overlay = screen.getByRole('status').parentElement
    expect(overlay).toHaveClass('backdrop-blur-sm')
  })

  it('renders without backdrop blur', () => {
    render(<LoadingOverlay isLoading={true} blur={false} />)
    
    const overlay = screen.getByRole('status').parentElement
    expect(overlay).not.toHaveClass('backdrop-blur-sm')
  })

  it('applies custom className', () => {
    render(<LoadingOverlay isLoading={true} className="custom-overlay" />)
    
    const overlay = screen.getByRole('status').parentElement?.parentElement
    expect(overlay).toHaveClass('custom-overlay')
  })

  it('has proper z-index for layering', () => {
    render(<LoadingOverlay isLoading={true} zIndex="z-50" />)
    
    const overlay = screen.getByRole('status').parentElement?.parentElement
    expect(overlay).toHaveClass('z-50')
  })

  it('supports custom background opacity', () => {
    render(<LoadingOverlay isLoading={true} opacity="bg-opacity-75" />)
    
    const overlay = screen.getByRole('status').parentElement
    expect(overlay).toHaveClass('bg-opacity-75')
  })

  it('renders children when provided', () => {
    render(
      <LoadingOverlay isLoading={true}>
        <div data-testid="child">Child content</div>
      </LoadingOverlay>
    )
    
    expect(screen.getByTestId('child')).toBeInTheDocument()
  })

  it('prevents interaction with content underneath', () => {
    render(<LoadingOverlay isLoading={true} />)
    
    const overlay = screen.getByRole('status').parentElement?.parentElement
    expect(overlay).toHaveClass('pointer-events-none')
    const backdrop = screen.getByRole('status').parentElement
    expect(backdrop).toHaveClass('pointer-events-auto')
  })
})