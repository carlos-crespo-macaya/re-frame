import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { PlaybackControls } from '../PlaybackControls'

// Mock formatDuration function
jest.mock('@/lib/audio', () => ({
  formatDuration: (ms: number) => {
    const totalSeconds = Math.floor(ms / 1000)
    const minutes = Math.floor(totalSeconds / 60)
    const seconds = totalSeconds % 60
    return `${minutes}:${seconds.toString().padStart(2, '0')}`
  }
}))

describe('PlaybackControls', () => {
  const defaultProps = {
    isPlaying: false,
    currentTime: 0,
    duration: 120000, // 2 minutes in milliseconds
    onPlayPause: jest.fn()
  }

  afterEach(() => {
    jest.clearAllMocks()
  })

  it('should render play button when not playing', () => {
    render(<PlaybackControls {...defaultProps} />)
    
    const playButton = screen.getByRole('button', { name: 'Play' })
    expect(playButton).toBeInTheDocument()
    
    // Check for play icon SVG
    const svg = playButton.querySelector('svg')
    expect(svg).toBeInTheDocument()
    expect(svg?.querySelector('path')?.getAttribute('d')).toContain('M8 5v14l11-7L8 5z')
  })

  it('should render pause button when playing', () => {
    render(<PlaybackControls {...defaultProps} isPlaying={true} />)
    
    const pauseButton = screen.getByRole('button', { name: 'Pause' })
    expect(pauseButton).toBeInTheDocument()
    
    // Check for pause icon SVG
    const svg = pauseButton.querySelector('svg')
    expect(svg).toBeInTheDocument()
    expect(svg?.querySelector('path')?.getAttribute('d')).toContain('M6 4h4v16H6V4zm8 0h4v16h-4V4z')
  })

  it('should call onPlayPause when play/pause button is clicked', async () => {
    const user = userEvent.setup()
    const onPlayPause = jest.fn()
    render(<PlaybackControls {...defaultProps} onPlayPause={onPlayPause} />)
    
    const playButton = screen.getByRole('button', { name: 'Play' })
    await user.click(playButton)
    
    expect(onPlayPause).toHaveBeenCalledTimes(1)
  })

  it('should render skip buttons by default', () => {
    render(<PlaybackControls {...defaultProps} onSkip={jest.fn()} />)
    
    expect(screen.getByRole('button', { name: 'Skip back 10 seconds' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Skip forward 10 seconds' })).toBeInTheDocument()
  })

  it('should not render skip buttons when showSkipButtons is false', () => {
    render(<PlaybackControls {...defaultProps} showSkipButtons={false} />)
    
    expect(screen.queryByRole('button', { name: 'Skip back 10 seconds' })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Skip forward 10 seconds' })).not.toBeInTheDocument()
  })

  it('should call onSkip with correct values when skip buttons are clicked', async () => {
    const user = userEvent.setup()
    const onSkip = jest.fn()
    render(<PlaybackControls {...defaultProps} onSkip={onSkip} />)
    
    // Click skip back
    await user.click(screen.getByRole('button', { name: 'Skip back 10 seconds' }))
    expect(onSkip).toHaveBeenCalledWith(-10)
    
    // Click skip forward
    await user.click(screen.getByRole('button', { name: 'Skip forward 10 seconds' }))
    expect(onSkip).toHaveBeenCalledWith(10)
  })

  it('should render stop button when onStop is provided', () => {
    const onStop = jest.fn()
    render(<PlaybackControls {...defaultProps} onStop={onStop} />)
    
    expect(screen.getByRole('button', { name: 'Stop' })).toBeInTheDocument()
  })

  it('should call onStop when stop button is clicked', async () => {
    const user = userEvent.setup()
    const onStop = jest.fn()
    render(<PlaybackControls {...defaultProps} onStop={onStop} />)
    
    await user.click(screen.getByRole('button', { name: 'Stop' }))
    expect(onStop).toHaveBeenCalledTimes(1)
  })

  it('should display time information correctly', () => {
    render(<PlaybackControls {...defaultProps} currentTime={30000} onSeek={jest.fn()} />)
    
    // Should show current time and duration
    expect(screen.getByText('0:30')).toBeInTheDocument() // 30 seconds
    expect(screen.getByText('2:00')).toBeInTheDocument() // 2 minutes
  })

  it('should render progress slider when onSeek is provided', () => {
    render(<PlaybackControls {...defaultProps} onSeek={jest.fn()} />)
    
    const slider = screen.getByRole('slider', { name: 'Seek' })
    expect(slider).toBeInTheDocument()
    expect(slider).toHaveAttribute('min', '0')
    expect(slider).toHaveAttribute('max', '100')
    expect(slider).toHaveAttribute('value', '0')
  })

  it('should not render progress slider when onSeek is not provided', () => {
    render(<PlaybackControls {...defaultProps} />)
    
    expect(screen.queryByRole('slider')).not.toBeInTheDocument()
  })

  it('should calculate progress correctly', () => {
    const { container } = render(
      <PlaybackControls 
        {...defaultProps} 
        currentTime={60000} // 1 minute
        duration={120000} // 2 minutes
        onSeek={jest.fn()} 
      />
    )
    
    const slider = screen.getByRole('slider')
    expect(slider).toHaveAttribute('value', '50') // 50% progress
    
    const progressBar = container.querySelector('.playback-controls__progress-bar')
    expect(progressBar).toHaveStyle({ width: '50%' })
  })

  it('should handle seek interaction', () => {
    const onSeek = jest.fn()
    render(<PlaybackControls {...defaultProps} onSeek={onSeek} />)
    
    const slider = screen.getByRole('slider')
    
    // Simulate dragging to 75% position
    fireEvent.change(slider, { target: { value: '75' } })
    
    // Should seek to 75% of duration (90 seconds = 90000ms)
    expect(onSeek).toHaveBeenCalledWith(90000)
  })

  it('should handle zero duration gracefully', () => {
    const { container } = render(
      <PlaybackControls 
        {...defaultProps} 
        currentTime={0}
        duration={0}
        onSeek={jest.fn()} 
      />
    )
    
    const slider = screen.getByRole('slider')
    expect(slider).toHaveAttribute('value', '0')
    
    const progressBar = container.querySelector('.playback-controls__progress-bar')
    expect(progressBar).toHaveStyle({ width: '0%' })
  })

  it('should apply custom className', () => {
    const { container } = render(
      <PlaybackControls {...defaultProps} className="custom-controls" />
    )
    
    expect(container.firstChild).toHaveClass('playback-controls', 'custom-controls')
  })

  it('should have proper accessibility attributes on slider', () => {
    render(
      <PlaybackControls 
        {...defaultProps} 
        currentTime={30000}
        duration={120000}
        onSeek={jest.fn()} 
      />
    )
    
    const slider = screen.getByRole('slider')
    expect(slider).toHaveAttribute('aria-label', 'Seek')
    expect(slider).toHaveAttribute('aria-valuetext', '0:30 of 2:00')
  })

  it('should render all controls when all callbacks are provided', () => {
    render(
      <PlaybackControls 
        {...defaultProps}
        onSeek={jest.fn()}
        onSkip={jest.fn()}
        onStop={jest.fn()}
      />
    )
    
    // Should have all buttons
    expect(screen.getByRole('button', { name: 'Skip back 10 seconds' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Play' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Skip forward 10 seconds' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Stop' })).toBeInTheDocument()
    
    // Should have slider
    expect(screen.getByRole('slider')).toBeInTheDocument()
    
    // Should have time displays
    expect(screen.getByText('0:00')).toBeInTheDocument()
    expect(screen.getByText('2:00')).toBeInTheDocument()
  })
})