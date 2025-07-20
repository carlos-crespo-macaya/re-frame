import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ConversationView } from '../ConversationView'

// Mock AudioVisualizer component
jest.mock('@/components/ui/AudioVisualizer', () => ({
  AudioVisualizer: () => (
    <div data-testid="audio-visualizer">Audio Visualizer</div>
  )
}))

// Mock scrollIntoView which is not available in jsdom
beforeAll(() => {
  Element.prototype.scrollIntoView = jest.fn()
})

describe('ConversationView', () => {
  it('should display message history', () => {
    const messages = [
      { id: '1', role: 'user' as const, content: 'I feel anxious', timestamp: Date.now() },
      { id: '2', role: 'ai' as const, content: 'I understand...', timestamp: Date.now() }
    ]
    
    render(<ConversationView messages={messages} />)
    
    // Check for message content separately since labels are in different elements
    expect(screen.getByText('I feel anxious')).toBeInTheDocument()
    expect(screen.getByText('I understand...')).toBeInTheDocument()
    
    // Check for role labels
    expect(screen.getByText('You:')).toBeInTheDocument()
    expect(screen.getByText('AI:')).toBeInTheDocument()
  })
  
  it('should show active recording state', () => {
    render(<ConversationView isRecording={true} />)
    
    expect(screen.getByText('🔴 Listening...')).toBeInTheDocument()
    expect(screen.getByTestId('audio-visualizer')).toBeInTheDocument()
  })
  
  it('should show AI speaking indicator', () => {
    render(<ConversationView isAISpeaking={true} />)
    
    expect(screen.getByText('[🔊 Speaking...]')).toBeInTheDocument()
  })
  
  it('should handle push-to-talk', async () => {
    const onStartRecording = jest.fn()
    const onStopRecording = jest.fn()
    
    render(
      <ConversationView 
        onStartRecording={onStartRecording}
        onStopRecording={onStopRecording}
      />
    )
    
    const talkButton = screen.getByRole('button', { name: /hold to talk/i })
    
    // Mouse down
    fireEvent.mouseDown(talkButton)
    expect(onStartRecording).toHaveBeenCalled()
    
    // Mouse up
    fireEvent.mouseUp(talkButton)
    expect(onStopRecording).toHaveBeenCalled()
  })
  
  it('should handle space key for push-to-talk', () => {
    const onStartRecording = jest.fn()
    const onStopRecording = jest.fn()
    
    render(
      <ConversationView 
        onStartRecording={onStartRecording}
        onStopRecording={onStopRecording}
      />
    )
    
    // Space key down
    fireEvent.keyDown(document, { key: ' ', code: 'Space' })
    expect(onStartRecording).toHaveBeenCalled()
    
    // Space key up
    fireEvent.keyUp(document, { key: ' ', code: 'Space' })
    expect(onStopRecording).toHaveBeenCalled()
  })
  
  it('should show end session button', async () => {
    const user = userEvent.setup()
    const onEndSession = jest.fn()
    render(<ConversationView onEndSession={onEndSession} />)
    
    const endButton = screen.getByRole('button', { name: /end session/i })
    await user.click(endButton)
    
    expect(onEndSession).toHaveBeenCalled()
  })
  
  it('should auto-scroll to latest message', () => {
    const { rerender } = render(<ConversationView messages={[]} />)
    
    const scrollIntoViewMock = jest.fn()
    Element.prototype.scrollIntoView = scrollIntoViewMock
    
    const newMessages = [
      { id: '1', role: 'user' as const, content: 'New message', timestamp: Date.now() }
    ]
    
    rerender(<ConversationView messages={newMessages} />)
    
    expect(scrollIntoViewMock).toHaveBeenCalledWith({
      behavior: 'smooth',
      block: 'end'
    })
  })
  
  it('should show current transcription when recording', () => {
    render(
      <ConversationView 
        isRecording={true}
        currentTranscription="Hello, I am speaking..."
      />
    )
    
    expect(screen.getByText('Hello, I am speaking...')).toBeInTheDocument()
  })
  
  it('should handle touch events for mobile push-to-talk', () => {
    const onStartRecording = jest.fn()
    const onStopRecording = jest.fn()
    
    render(
      <ConversationView 
        onStartRecording={onStartRecording}
        onStopRecording={onStopRecording}
      />
    )
    
    const talkButton = screen.getByRole('button', { name: /hold to talk/i })
    
    // Touch start
    fireEvent.touchStart(talkButton)
    expect(onStartRecording).toHaveBeenCalled()
    
    // Touch end
    fireEvent.touchEnd(talkButton)
    expect(onStopRecording).toHaveBeenCalled()
  })
})