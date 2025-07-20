import { render, screen } from '@testing-library/react'
import LoadingSkeleton from '../LoadingSkeleton'

describe('LoadingSkeleton', () => {
  it('renders with default props', () => {
    render(<LoadingSkeleton />)
    
    const skeleton = screen.getByRole('status')
    expect(skeleton).toBeInTheDocument()
    expect(skeleton).toHaveAttribute('aria-busy', 'true')
    expect(skeleton).toHaveAttribute('aria-label', 'Loading content')
  })

  it('renders with custom className', () => {
    render(<LoadingSkeleton className="custom-class" />)
    
    const skeleton = screen.getByRole('status')
    expect(skeleton).toHaveClass('custom-class')
  })

  it('renders with text variant', () => {
    render(<LoadingSkeleton variant="text" />)
    
    const skeleton = screen.getByRole('status')
    expect(skeleton).toHaveClass('h-4', 'rounded')
  })

  it('renders with title variant', () => {
    render(<LoadingSkeleton variant="title" />)
    
    const skeleton = screen.getByRole('status')
    expect(skeleton).toHaveClass('h-8', 'rounded')
  })

  it('renders with paragraph variant', () => {
    render(<LoadingSkeleton variant="paragraph" />)
    
    const skeleton = screen.getByRole('status')
    const lines = skeleton.querySelectorAll('.motion-safe\\:animate-pulse')
    expect(lines.length).toBeGreaterThan(1)
  })

  it('renders with avatar variant', () => {
    render(<LoadingSkeleton variant="avatar" />)
    
    const skeleton = screen.getByRole('status')
    expect(skeleton).toHaveClass('rounded-full')
  })

  it('renders with card variant', () => {
    render(<LoadingSkeleton variant="card" />)
    
    const skeleton = screen.getByRole('status')
    expect(skeleton).toHaveClass('rounded-lg', 'p-4')
  })

  it('renders with custom width', () => {
    render(<LoadingSkeleton width="200px" />)
    
    const skeleton = screen.getByRole('status')
    expect(skeleton).toHaveStyle({ width: '200px' })
  })

  it('renders with custom height', () => {
    render(<LoadingSkeleton height="100px" />)
    
    const skeleton = screen.getByRole('status')
    expect(skeleton).toHaveStyle({ height: '100px' })
  })

  it('renders with custom lines for paragraph variant', () => {
    render(<LoadingSkeleton variant="paragraph" lines={5} />)
    
    const skeleton = screen.getByRole('status')
    const lines = skeleton.querySelectorAll('.motion-safe\\:animate-pulse')
    expect(lines).toHaveLength(5)
  })

  it('has proper animation class', () => {
    render(<LoadingSkeleton />)
    
    const skeleton = screen.getByRole('status')
    expect(skeleton.firstChild).toHaveClass('motion-safe:animate-pulse')
  })

  it('respects reduced motion preference', () => {
    window.matchMedia = jest.fn().mockImplementation(query => ({
      matches: query === '(prefers-reduced-motion: reduce)',
      media: query,
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
    }))

    render(<LoadingSkeleton />)
    
    const skeleton = screen.getByRole('status')
    expect(skeleton.firstChild).toHaveClass('motion-safe:animate-pulse')
  })

  it('renders multiple skeletons with count prop', () => {
    render(<LoadingSkeleton count={3} />)
    
    const skeletons = screen.getAllByRole('status')
    expect(skeletons).toHaveLength(3)
  })

  it('applies gap between multiple skeletons', () => {
    const { container } = render(<LoadingSkeleton count={2} gap="md" />)
    
    const wrapper = container.firstChild
    expect(wrapper).toHaveClass('gap-4')
  })
})