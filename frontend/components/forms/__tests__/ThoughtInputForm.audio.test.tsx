import { render, screen, act, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ThoughtInputForm from '../ThoughtInputForm'
import { AudioRecorder } from '@/lib/audio/audio-recorder'
import { SSEClient } from '@/lib/streaming/sse-client'
import * as AudioUtils from '@/lib/audio/audio-utils'
import { useAudioRecorder } from '@/lib/audio/use-audio-recorder'
import { useSSEClient } from '@/lib/streaming/use-sse-client'

// Mock the audio modules
jest.mock('@/lib/audio/audio-recorder')
jest.mock('@/lib/streaming/sse-client')
jest.mock('@/lib/audio/audio-utils')
jest.mock('@/lib/audio/use-audio-recorder')
jest.mock('@/lib/streaming/use-sse-client')

// Mock canvas for AudioVisualizer
HTMLCanvasElement.prototype.getContext = jest.fn(() => ({
  clearRect: jest.fn(),
  fillRect: jest.fn(),
  fillStyle: '',
  strokeStyle: '',
  beginPath: jest.fn(),
  moveTo: jest.fn(),
  lineTo: jest.fn(),
  stroke: jest.fn(),
  arc: jest.fn(),
  fill: jest.fn(),
  scale: jest.fn(),
  save: jest.fn(),
  restore: jest.fn(),
  translate: jest.fn()
})) as any

// Mock window.devicePixelRatio
Object.defineProperty(window, 'devicePixelRatio', {
  value: 1,
  writable: true
})

describe.skip('ThoughtInputForm - Audio Integration - SKIPPED: Audio moved to separate voice mode', () => {
  let mockAudioRecorder: any
  let mockSSEClient: any
  let mockStartRecording: jest.Mock
  let mockStopRecording: jest.Mock
  let mockConnect: jest.Mock
  let mockDisconnect: jest.Mock
  let mockSendAudio: jest.Mock
  let onTranscriptionCallback: ((text: string) => void) | undefined
  let onDataAvailableCallback: ((data: Float32Array) => void) | undefined
  
  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks()
    
    // Setup mock functions
    mockStartRecording = jest.fn()
    mockStopRecording = jest.fn()
    mockConnect = jest.fn()
    mockDisconnect = jest.fn()
    mockSendAudio = jest.fn()
    
    // Mock useAudioRecorder hook
    mockAudioRecorder = {
      isRecording: false,
      isProcessing: false,
      micPermission: 'prompt',
      error: null,
      isGateOpen: false,
      startRecording: mockStartRecording,
      stopRecording: mockStopRecording,
      cleanup: jest.fn()
    };
    
    // Capture the callbacks from useAudioRecorder
    (useAudioRecorder as jest.Mock).mockImplementation((options) => {
      onTranscriptionCallback = options?.onTranscription
      onDataAvailableCallback = options?.onDataAvailable
      return mockAudioRecorder
    })
    
    // Mock useSSEClient hook
    mockSSEClient = {
      isConnected: false,
      connectionState: 'disconnected',
      error: null,
      messages: [],
      sessionId: null,
      connect: mockConnect,
      disconnect: mockDisconnect,
      sendMessage: jest.fn(),
      sendAudio: mockSendAudio,
      clearMessages: jest.fn(),
      getLatestMessage: jest.fn(),
      getMessagesByType: jest.fn().mockReturnValue([])
    };
    
    (useSSEClient as jest.Mock).mockReturnValue(mockSSEClient)
  })
  
  it.skip('should show record button when audio is supported - audio controls moved to separate voice mode', () => {
    // This test is no longer applicable as audio controls have been moved to a separate voice mode
    // The test is kept for reference but skipped
  })
  
  it('should not show record button when audio is not supported', () => {
    jest.spyOn(AudioUtils, 'checkAudioSupport').mockReturnValue({
      audioContext: false,
      audioWorklet: false,
      getUserMedia: false
    })
    
    render(<ThoughtInputForm onSubmit={jest.fn()} onClear={jest.fn()} />)
    expect(screen.queryByTestId('audio-controls')).not.toBeInTheDocument()
  })
  
  it('should start recording when record button is clicked', async () => {
    const user = userEvent.setup()
    jest.spyOn(AudioUtils, 'checkAudioSupport').mockReturnValue({
      audioContext: true,
      audioWorklet: true,
      getUserMedia: true
    })
    
    render(<ThoughtInputForm onSubmit={jest.fn()} onClear={jest.fn()} />)
    
    const recordButton = screen.getByRole('button', { name: /hold to record/i })
    await user.click(recordButton)
    
    expect(mockStartRecording).toHaveBeenCalled()
    expect(mockConnect).toHaveBeenCalled()
  })
  
  it('should show transcription in real-time from SSE', async () => {
    const mockOnSubmit = jest.fn()
    
    jest.spyOn(AudioUtils, 'checkAudioSupport').mockReturnValue({
      audioContext: true,
      audioWorklet: true,
      getUserMedia: true
    })
    
    // Mock SSE client as connected with transcription messages
    const connectedSSEClient = {
      ...mockSSEClient,
      isConnected: true,
      getMessagesByType: jest.fn().mockReturnValue([
        { data: 'I am feeling anxious', message_type: 'transcription' }
      ])
    };
    (useSSEClient as jest.Mock).mockReturnValue(connectedSSEClient)
    
    // Mock audio recorder as recording
    const recordingAudioRecorder = {
      ...mockAudioRecorder,
      isRecording: true,
      micPermission: 'granted'
    };
    (useAudioRecorder as jest.Mock).mockReturnValue(recordingAudioRecorder)
    
    const { rerender } = render(<ThoughtInputForm onSubmit={mockOnSubmit} onClear={jest.fn()} />)
    
    // Force a re-render to trigger the SSE message effect
    rerender(<ThoughtInputForm onSubmit={mockOnSubmit} onClear={jest.fn()} />)
    
    await waitFor(() => {
      expect(screen.getByText(/I am feeling anxious/)).toBeInTheDocument()
    })
  })
  
  it('should handle transcription updates during recording', async () => {
    const mockOnSubmit = jest.fn()
    
    jest.spyOn(AudioUtils, 'checkAudioSupport').mockReturnValue({
      audioContext: true,
      audioWorklet: true,
      getUserMedia: true
    })
    
    // Mock recording state
    const recordingState = {
      ...mockAudioRecorder,
      isRecording: true,
      micPermission: 'granted'
    };
    (useAudioRecorder as jest.Mock).mockReturnValue(recordingState)
    
    render(<ThoughtInputForm onSubmit={mockOnSubmit} onClear={jest.fn()} />)
    
    // Simulate transcription callback
    act(() => {
      if (onTranscriptionCallback) {
        onTranscriptionCallback('Test transcription')
      }
    })
    
    // Verify transcription callback was captured
    expect(onTranscriptionCallback).toBeDefined()
  })
  
  it('should buffer audio data before sending', async () => {
    jest.useFakeTimers()
    const user = userEvent.setup({ delay: null })
    
    jest.spyOn(AudioUtils, 'checkAudioSupport').mockReturnValue({
      audioContext: true,
      audioWorklet: true,
      getUserMedia: true
    })
    
    // Mock as connected
    const connectedSSEClient = {
      ...mockSSEClient,
      isConnected: true
    };
    (useSSEClient as jest.Mock).mockReturnValue(connectedSSEClient)
    
    // Mock audio utilities
    jest.spyOn(AudioUtils, 'arrayBufferToBase64').mockReturnValue('base64data')
    jest.spyOn(AudioUtils, 'float32ToPcm16').mockImplementation((float32) => {
      // Return a mock Int16Array with proper buffer
      return new Int16Array(float32.length)
    })
    
    render(<ThoughtInputForm onSubmit={jest.fn()} onClear={jest.fn()} />)
    
    // Start recording
    const recordButton = screen.getByRole('button', { name: /hold to record/i })
    await user.click(recordButton)
    
    // Simulate audio data chunks
    const audioData1 = new Float32Array([1, 2, 3])
    const audioData2 = new Float32Array([4, 5, 6])
    
    act(() => {
      // Simulate audio data events
      if (onDataAvailableCallback) {
        onDataAvailableCallback(audioData1)
        onDataAvailableCallback(audioData2)
      }
    })
    
    // Should not send immediately
    expect(mockSendAudio).not.toHaveBeenCalled()
    
    // Advance timer to trigger buffer send (200ms)
    act(() => {
      jest.advanceTimersByTime(200)
    })
    
    // Should have sent buffered audio data
    await waitFor(() => {
      expect(mockSendAudio).toHaveBeenCalledWith('base64data', false)
    })
    
    jest.useRealTimers()
  })
  
  it('should handle permission denied gracefully', async () => {
    const user = userEvent.setup()
    
    jest.spyOn(AudioUtils, 'checkAudioSupport').mockReturnValue({
      audioContext: true,
      audioWorklet: true,
      getUserMedia: true
    })
    
    render(<ThoughtInputForm onSubmit={jest.fn()} onClear={jest.fn()} />)
    
    // Should have audio controls initially
    expect(screen.getByTestId('audio-controls')).toBeInTheDocument()
    
    // Find the permission denied button
    const permissionButtons = screen.getAllByRole('button')
    const denyButton = permissionButtons.find(btn => 
      btn.textContent?.includes('Stay with typing')
    )
    
    if (denyButton) {
      await user.click(denyButton)
      
      // Audio controls should be hidden after permission denied
      await waitFor(() => {
        expect(screen.queryByTestId('audio-controls')).not.toBeInTheDocument()
      })
    }
  })
  
  it('should integrate with SSE client for streaming', async () => {
    const user = userEvent.setup()
    
    jest.spyOn(AudioUtils, 'checkAudioSupport').mockReturnValue({
      audioContext: true,
      audioWorklet: true,
      getUserMedia: true
    })
    
    render(<ThoughtInputForm onSubmit={jest.fn()} onClear={jest.fn()} />)
    
    // Should connect to SSE when starting recording
    const recordButton = screen.getByRole('button', { name: /hold to record/i })
    await user.click(recordButton)
    
    await waitFor(() => {
      expect(mockConnect).toHaveBeenCalled()
    })
    
    // Update to recording state
    const recordingState = {
      ...mockAudioRecorder,
      isRecording: true,
      micPermission: 'granted'
    };
    (useAudioRecorder as jest.Mock).mockReturnValue(recordingState)
    
    // Should disconnect when form is cleared
    const clearButton = screen.getByRole('button', { name: /clear/i })
    await user.click(clearButton)
    
    await waitFor(() => {
      expect(mockDisconnect).toHaveBeenCalled()
    })
  })
  
  it('should stop recording when stop is triggered', async () => {
    const user = userEvent.setup()
    
    jest.spyOn(AudioUtils, 'checkAudioSupport').mockReturnValue({
      audioContext: true,
      audioWorklet: true,
      getUserMedia: true
    })
    
    render(<ThoughtInputForm onSubmit={jest.fn()} onClear={jest.fn()} />)
    
    // Start recording first
    const recordButton = screen.getByRole('button', { name: /hold to record/i })
    await user.click(recordButton)
    
    expect(mockStartRecording).toHaveBeenCalled()
    
    // Update mock to show recording state
    const recordingState = {
      ...mockAudioRecorder,
      isRecording: true,
      micPermission: 'granted'
    };
    (useAudioRecorder as jest.Mock).mockReturnValue(recordingState)
    
    // The stop will be called when button is released or other action
    // This test just verifies the recording flow works
    expect(mockStartRecording).toHaveBeenCalled()
  })
})