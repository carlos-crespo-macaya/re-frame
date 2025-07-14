import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ThoughtInputForm from './ThoughtInputForm'

// Mock audio modules
jest.mock('@/lib/audio/use-audio-recorder', () => ({
  useAudioRecorder: () => ({
    isRecording: false,
    isProcessing: false,
    micPermission: 'prompt',
    error: null,
    isGateOpen: false,
    startRecording: jest.fn(),
    stopRecording: jest.fn(),
    cleanup: jest.fn()
  })
}))

jest.mock('@/lib/streaming/use-sse-client', () => ({
  useSSEClient: () => ({
    isConnected: false,
    connectionState: 'disconnected',
    error: null,
    messages: [],
    sessionId: null,
    connect: jest.fn(),
    disconnect: jest.fn(),
    sendMessage: jest.fn(),
    sendAudio: jest.fn(),
    clearMessages: jest.fn(),
    getLatestMessage: jest.fn(),
    getMessagesByType: jest.fn().mockReturnValue([])
  })
}))

jest.mock('@/lib/audio/audio-utils', () => ({
  checkAudioSupport: () => ({
    audioContext: false,
    audioWorklet: false,
    getUserMedia: false
  }),
  arrayBufferToBase64: jest.fn(),
  float32ToPcm16: jest.fn()
}))

describe('ThoughtInputForm', () => {
  const mockOnSubmit = jest.fn()
  const mockOnClear = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders form with all required elements', () => {
    render(<ThoughtInputForm onSubmit={mockOnSubmit} onClear={mockOnClear} />)
    
    expect(screen.getByPlaceholderText(/what happened\? how did it feel\?/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /generate perspective/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /clear/i })).toBeInTheDocument()
  })

  it('allows typing in textarea', async () => {
    const user = userEvent.setup()
    render(<ThoughtInputForm onSubmit={mockOnSubmit} onClear={mockOnClear} />)
    
    const textarea = screen.getByPlaceholderText(/what happened\? how did it feel\?/i)
    await user.type(textarea, 'I feel anxious about the meeting')
    
    expect(textarea).toHaveValue('I feel anxious about the meeting')
  })

  it('submits form with entered text', async () => {
    const user = userEvent.setup()
    render(<ThoughtInputForm onSubmit={mockOnSubmit} onClear={mockOnClear} />)
    
    const textarea = screen.getByPlaceholderText(/what happened\? how did it feel\?/i)
    const submitButton = screen.getByRole('button', { name: /generate perspective/i })
    
    await user.type(textarea, 'I feel anxious about the meeting')
    await user.click(submitButton)
    
    expect(mockOnSubmit).toHaveBeenCalledWith('I feel anxious about the meeting')
    expect(mockOnSubmit).toHaveBeenCalledTimes(1)
  })

  it('clears form when clear button is clicked', async () => {
    const user = userEvent.setup()
    render(<ThoughtInputForm onSubmit={mockOnSubmit} onClear={mockOnClear} />)
    
    const textarea = screen.getByPlaceholderText(/what happened\? how did it feel\?/i)
    const clearButton = screen.getByRole('button', { name: /clear/i })
    
    await user.type(textarea, 'Some text')
    await user.click(clearButton)
    
    expect(textarea).toHaveValue('')
    expect(mockOnClear).toHaveBeenCalledTimes(1)
  })

  it('disables submit button when textarea is empty', () => {
    render(<ThoughtInputForm onSubmit={mockOnSubmit} onClear={mockOnClear} />)
    
    const submitButton = screen.getByRole('button', { name: /generate perspective/i })
    expect(submitButton).toBeDisabled()
  })

  it('enables submit button when textarea has content', async () => {
    const user = userEvent.setup()
    render(<ThoughtInputForm onSubmit={mockOnSubmit} onClear={mockOnClear} />)
    
    const textarea = screen.getByPlaceholderText(/what happened\? how did it feel\?/i)
    const submitButton = screen.getByRole('button', { name: /generate perspective/i })
    
    await user.type(textarea, 'Some thought')
    expect(submitButton).toBeEnabled()
  })

  it('shows character count', () => {
    render(<ThoughtInputForm onSubmit={mockOnSubmit} onClear={mockOnClear} />)
    
    expect(screen.getByText(/0 \/ 1000/i)).toBeInTheDocument()
  })

  it('updates character count as user types', async () => {
    const user = userEvent.setup()
    render(<ThoughtInputForm onSubmit={mockOnSubmit} onClear={mockOnClear} />)
    
    const textarea = screen.getByPlaceholderText(/what happened\? how did it feel\?/i)
    await user.type(textarea, 'Hello')
    
    expect(screen.getByText(/5 \/ 1000/i)).toBeInTheDocument()
  })

  it('enforces maximum character limit', async () => {
    const user = userEvent.setup()
    render(<ThoughtInputForm onSubmit={mockOnSubmit} onClear={mockOnClear} />)
    
    const textarea = screen.getByPlaceholderText(/what happened\? how did it feel\?/i) as HTMLTextAreaElement
    const longText = 'a'.repeat(1001)
    
    // Use paste instead of type for better performance with long text
    await user.click(textarea)
    await user.paste(longText)
    
    expect(textarea.value.length).toBe(1000)
  })

  it('clears form after successful submission', async () => {
    const user = userEvent.setup()
    render(<ThoughtInputForm onSubmit={mockOnSubmit} onClear={mockOnClear} />)
    
    const textarea = screen.getByPlaceholderText(/what happened\? how did it feel\?/i)
    const submitButton = screen.getByRole('button', { name: /generate perspective/i })
    
    await user.type(textarea, 'My thought')
    await user.click(submitButton)
    
    expect(textarea).toHaveValue('')
  })

  it('handles loading state', () => {
    render(<ThoughtInputForm onSubmit={mockOnSubmit} onClear={mockOnClear} isLoading />)
    
    const submitButton = screen.getByRole('button', { name: /processing/i })
    const textarea = screen.getByPlaceholderText(/what happened\? how did it feel\?/i)
    
    expect(submitButton).toBeDisabled()
    expect(textarea).toBeDisabled()
    expect(screen.getByText(/analyzing your input/i)).toBeInTheDocument()
  })

  it('is keyboard accessible', async () => {
    const user = userEvent.setup()
    render(<ThoughtInputForm onSubmit={mockOnSubmit} onClear={mockOnClear} />)
    
    await user.tab()
    expect(screen.getByPlaceholderText(/what happened\? how did it feel\?/i)).toHaveFocus()
    
    await user.type(screen.getByPlaceholderText(/what happened\? how did it feel\?/i), 'Test')
    
    await user.tab()
    expect(screen.getByRole('button', { name: /generate perspective/i })).toHaveFocus()
    
    await user.tab()
    expect(screen.getByRole('button', { name: /clear/i })).toHaveFocus()
  })

  it('submits form on Enter key with Ctrl/Cmd', async () => {
    const user = userEvent.setup()
    render(<ThoughtInputForm onSubmit={mockOnSubmit} onClear={mockOnClear} />)
    
    const textarea = screen.getByPlaceholderText(/what happened\? how did it feel\?/i)
    await user.type(textarea, 'My thought')
    await user.keyboard('{Control>}{Enter}{/Control}')
    
    expect(mockOnSubmit).toHaveBeenCalledWith('My thought')
  })
  
  it('shows status messages based on input length', async () => {
    const user = userEvent.setup()
    render(<ThoughtInputForm onSubmit={mockOnSubmit} onClear={mockOnClear} />)
    
    // Initial state - empty message
    const textarea = screen.getByPlaceholderText(/what happened\? how did it feel\?/i)
    
    // Short input
    await user.type(textarea, 'Hello')
    expect(screen.getByText(/continue if you'd like to add more context/i)).toBeInTheDocument()
    
    // Medium input
    await user.clear(textarea)
    await user.type(textarea, 'a'.repeat(100))
    expect(screen.getByText(/good amount of detail/i)).toBeInTheDocument()
  })
})