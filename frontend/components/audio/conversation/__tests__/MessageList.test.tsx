import { render, screen } from '@testing-library/react'
import { MessageList } from '../MessageList'
import type { ConversationMessage } from '../types'

// Mock scrollIntoView which is not available in jsdom
beforeAll(() => {
  Element.prototype.scrollIntoView = jest.fn()
})

describe('MessageList', () => {
  const mockMessages: ConversationMessage[] = [
    {
      id: '1',
      role: 'user',
      content: 'I feel anxious about the meeting tomorrow',
      timestamp: Date.now() - 60000
    },
    {
      id: '2',
      role: 'ai',
      content: 'It sounds like you\'re experiencing anticipatory anxiety. This is very common.',
      timestamp: Date.now() - 30000
    },
    {
      id: '3',
      role: 'user',
      content: 'Yes, I keep thinking about what could go wrong',
      timestamp: Date.now()
    }
  ]
  
  it('should render all messages', () => {
    render(<MessageList messages={mockMessages} />)
    
    expect(screen.getByText('I feel anxious about the meeting tomorrow')).toBeInTheDocument()
    expect(screen.getByText(/It sounds like you're experiencing anticipatory anxiety/)).toBeInTheDocument()
    expect(screen.getByText('Yes, I keep thinking about what could go wrong')).toBeInTheDocument()
  })
  
  it('should apply correct styling for user and AI messages', () => {
    const { container } = render(<MessageList messages={mockMessages} />)
    
    const userMessages = container.querySelectorAll('[data-role="user"]')
    const aiMessages = container.querySelectorAll('[data-role="ai"]')
    
    expect(userMessages).toHaveLength(2)
    expect(aiMessages).toHaveLength(1)
  })
  
  it('should show timestamps', () => {
    render(<MessageList messages={mockMessages} />)
    
    // Check that time elements exist
    const timeElements = screen.getAllByRole('time')
    expect(timeElements).toHaveLength(3)
  })
  
  it('should handle empty message list', () => {
    const { container } = render(<MessageList messages={[]} />)
    
    expect(container.querySelector('[data-testid="message-list"]')).toBeEmptyDOMElement()
  })
  
  it('should show audio playback button for messages with audio', () => {
    const messagesWithAudio: ConversationMessage[] = [
      {
        id: '1',
        role: 'ai',
        content: 'Let me help you with that',
        timestamp: Date.now(),
        audioUrl: '/audio/response.mp3'
      }
    ]
    
    render(<MessageList messages={messagesWithAudio} />)
    
    expect(screen.getByRole('button', { name: /play audio/i })).toBeInTheDocument()
  })
  
  it('should mark the last message for auto-scroll', () => {
    const { container } = render(<MessageList messages={mockMessages} />)
    
    const lastMessage = container.querySelector('[data-last-message="true"]')
    expect(lastMessage).toBeInTheDocument()
    expect(lastMessage).toHaveTextContent('Yes, I keep thinking about what could go wrong')
  })
})