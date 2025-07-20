import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MessageBubble } from '../MessageBubble'
import type { ConversationMessage } from '../types'

describe('MessageBubble', () => {
  const mockUserMessage: ConversationMessage = {
    id: '1',
    role: 'user',
    content: 'I feel anxious about social situations',
    timestamp: new Date('2024-01-15T10:30:00').getTime()
  }

  const mockAIMessage: ConversationMessage = {
    id: '2',
    role: 'ai',
    content: 'I understand that social situations can be challenging. Can you tell me more about what specifically makes you anxious?',
    timestamp: new Date('2024-01-15T10:31:00').getTime()
  }

  const mockMessageWithAudio: ConversationMessage = {
    id: '3',
    role: 'ai',
    content: 'Let me guide you through a breathing exercise',
    timestamp: new Date('2024-01-15T10:32:00').getTime(),
    audioUrl: '/audio/breathing-exercise.mp3'
  }

  it('should render user message with correct styling', () => {
    const { container } = render(<MessageBubble message={mockUserMessage} />)

    // Check the message bubble container has correct background
    const messageBubble = container.querySelector('.bg-primary-500')
    expect(messageBubble).toBeInTheDocument()
    expect(messageBubble).toHaveClass('text-white')
    
    // Check role label
    expect(screen.getByText('You:')).toBeInTheDocument()
    expect(screen.getByText('You:')).toHaveClass('text-primary-100')
    
    // Check alignment
    const alignmentContainer = container.querySelector('[data-role="user"]')
    expect(alignmentContainer).toBeInTheDocument()
    expect(alignmentContainer).toHaveClass('justify-end')
  })

  it('should render AI message with correct styling', () => {
    const { container } = render(<MessageBubble message={mockAIMessage} />)

    // Check the message bubble container has correct background
    const messageBubble = container.querySelector('.bg-neutral-100')
    expect(messageBubble).toBeInTheDocument()
    expect(messageBubble).toHaveClass('text-neutral-900')
    
    // Check role label
    expect(screen.getByText('AI:')).toBeInTheDocument()
    expect(screen.getByText('AI:')).toHaveClass('text-neutral-500')
    
    // Check alignment
    const alignmentContainer = container.querySelector('[data-role="ai"]')
    expect(alignmentContainer).toBeInTheDocument()
    expect(alignmentContainer).toHaveClass('justify-start')
  })

  it('should display formatted timestamp', () => {
    render(<MessageBubble message={mockUserMessage} />)

    const timeElement = screen.getByRole('time')
    expect(timeElement).toBeInTheDocument()
    // The time will be formatted based on the local timezone
    // Check that it contains hour and minute separated by colon
    expect(timeElement.textContent).toMatch(/\d{1,2}:\d{2}/)
    expect(timeElement).toHaveAttribute('dateTime')
  })

  it('should show audio playback button when audioUrl is provided', () => {
    render(<MessageBubble message={mockMessageWithAudio} />)

    const playButton = screen.getByRole('button', { name: /play audio/i })
    expect(playButton).toBeInTheDocument()
    expect(playButton).toHaveTextContent('▶️ Play Audio')
  })

  it('should toggle play/pause state when audio button is clicked', async () => {
    const user = userEvent.setup()
    render(<MessageBubble message={mockMessageWithAudio} />)

    const playButton = screen.getByRole('button', { name: /play audio/i })
    
    // Initial state - should show play
    expect(playButton).toHaveTextContent('▶️ Play Audio')
    expect(playButton).toHaveAttribute('aria-label', 'Play audio')

    // Click to play
    await user.click(playButton)
    expect(playButton).toHaveTextContent('⏸️ Pause Audio')
    expect(playButton).toHaveAttribute('aria-label', 'Pause audio')

    // Click to pause
    await user.click(playButton)
    expect(playButton).toHaveTextContent('▶️ Play Audio')
    expect(playButton).toHaveAttribute('aria-label', 'Play audio')
  })

  it('should not show audio button when audioUrl is not provided', () => {
    render(<MessageBubble message={mockUserMessage} />)

    expect(screen.queryByRole('button', { name: /audio/i })).not.toBeInTheDocument()
  })

  it('should mark last message with data attribute', () => {
    const { container } = render(<MessageBubble message={mockUserMessage} isLast={true} />)

    const messageContainer = container.querySelector('[data-last-message="true"]')
    expect(messageContainer).toBeInTheDocument()
  })

  it('should not mark non-last message with data attribute', () => {
    const { container } = render(<MessageBubble message={mockUserMessage} isLast={false} />)

    const messageContainer = container.querySelector('[data-last-message="false"]')
    expect(messageContainer).toBeInTheDocument()
  })

  it('should handle long content gracefully', () => {
    const longMessage: ConversationMessage = {
      id: '4',
      role: 'user',
      content: 'This is a very long message that might wrap to multiple lines. It contains a lot of text to test how the component handles longer content that would naturally break across multiple lines in the UI.',
      timestamp: Date.now()
    }

    const { container } = render(<MessageBubble message={longMessage} />)

    // Check that the message bubble has max-width constraint
    const messageBubble = container.querySelector('.bg-primary-500') // user message
    expect(messageBubble).toBeInTheDocument()
    expect(messageBubble).toHaveClass('max-w-[70%]')
  })

  it('should handle special characters in content', () => {
    const specialMessage: ConversationMessage = {
      id: '5',
      role: 'ai',
      content: 'Here\'s some content with "quotes" and <special> characters & symbols!',
      timestamp: Date.now()
    }

    render(<MessageBubble message={specialMessage} />)

    expect(screen.getByText(/Here's some content with "quotes" and <special> characters & symbols!/)).toBeInTheDocument()
  })

  it('should maintain consistent structure for all message types', () => {
    const { container } = render(<MessageBubble message={mockUserMessage} />)

    // Check structure
    const roleLabel = container.querySelector('.text-xs.font-medium.mb-1')
    const content = container.querySelector('.text-sm')
    const timestamp = container.querySelector('time')

    expect(roleLabel).toBeInTheDocument()
    expect(content).toBeInTheDocument()
    expect(timestamp).toBeInTheDocument()
  })
})