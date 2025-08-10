import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import { ChatClient } from '../chat-client'
import { postFeedbackApiFeedbackPost } from '@/lib/api/generated/sdk.gen'
import { useRecaptcha } from '@/lib/recaptcha/useRecaptcha'
import { useSSEClient } from '@/lib/streaming/use-sse-client'

// Mock dependencies
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}))

jest.mock('@/lib/api/generated/sdk.gen', () => ({
  postFeedbackApiFeedbackPost: jest.fn(),
}))

jest.mock('@/lib/recaptcha/useRecaptcha', () => ({
  useRecaptcha: jest.fn(),
}))

jest.mock('@/lib/streaming/use-sse-client', () => ({
  useSSEClient: jest.fn(),
}))

jest.mock('@/components/icons', () => ({
  ChevronLeftIcon: () => <div>ChevronLeft</div>,
  SendIcon: () => <div>Send</div>,
  ThumbsUpIcon: () => <div>ThumbsUp</div>,
  ThumbsDownIcon: () => <div>ThumbsDown</div>,
}))

jest.mock('react-markdown', () => ({
  __esModule: true,
  default: ({ children }: { children: string }) => <div>{children}</div>,
}))

describe('ChatClient - Inline Feedback', () => {
  const mockExecute = jest.fn()
  const mockPostFeedback = postFeedbackApiFeedbackPost as jest.Mock
  const mockConnect = jest.fn()
  const mockDisconnect = jest.fn()
  const mockSendText = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
    
    // Mock scrollIntoView which is not available in jsdom
    Element.prototype.scrollIntoView = jest.fn()
    
    ;(useRecaptcha as jest.Mock).mockReturnValue({
      ready: true,
      execute: mockExecute,
      error: null,
    })
    
    ;(useSSEClient as jest.Mock).mockReturnValue({
      connect: mockConnect,
      disconnect: mockDisconnect,
      sendText: mockSendText,
      messages: [],
      sessionId: 'test-session',
    })
    
    mockExecute.mockResolvedValue('test-token')
    mockPostFeedback.mockResolvedValue({})
  })

  it('shows input field when thumbs up is clicked', async () => {
    // Render with a message to test feedback on
    ;(useSSEClient as jest.Mock).mockReturnValue({
      connect: mockConnect,
      disconnect: mockDisconnect,
      sendText: mockSendText,
      messages: [
        { message_type: 'response', data: 'Hello, how can I help you?', turn_complete: true }
      ],
      sessionId: 'test-session',
    })

    const { rerender } = render(<ChatClient locale="en" />)

    // Trigger re-render to process messages
    rerender(<ChatClient locale="en" />)

    await waitFor(() => {
      expect(screen.getByText('Hello, how can I help you?')).toBeInTheDocument()
    })

    // Find and click thumbs up button
    const thumbsUpButtons = screen.getAllByLabelText('Thumbs up')
    const assistantThumbsUp = thumbsUpButtons[thumbsUpButtons.length - 1]
    fireEvent.click(assistantThumbsUp)

    // Verify input field appears and is not disabled
    const noteInput = await screen.findByPlaceholderText('Optional note…')
    expect(noteInput).toBeInTheDocument()
    expect(noteInput).not.toBeDisabled()

    // Verify single Send button is present (no separate Skip button)
    expect(screen.getAllByText('Send')[0]).toBeInTheDocument()
  })

  it('allows entering and sending feedback with note', async () => {
    ;(useSSEClient as jest.Mock).mockReturnValue({
      connect: mockConnect,
      disconnect: mockDisconnect,
      sendText: mockSendText,
      messages: [
        { message_type: 'response', data: 'Test response', turn_complete: true }
      ],
      sessionId: 'test-session',
    })

    const { rerender } = render(<ChatClient locale="en" />)
    rerender(<ChatClient locale="en" />)

    await waitFor(() => {
      expect(screen.getByText('Test response')).toBeInTheDocument()
    })

    // Click thumbs down
    const thumbsDownButtons = screen.getAllByLabelText('Thumbs down')
    fireEvent.click(thumbsDownButtons[thumbsDownButtons.length - 1])

    // Enter note
    const noteInput = await screen.findByPlaceholderText('Optional note…')
    fireEvent.change(noteInput, { target: { value: 'Could be better' } })

    // Click send - use getAllByText since there are multiple Send buttons
    const sendButtons = screen.getAllByText('Send')
    // The first Send button should be the one for the feedback note
    fireEvent.click(sendButtons[0])

    // Verify feedback was sent with note
    await waitFor(() => {
      expect(mockPostFeedback).toHaveBeenCalledWith({
        requestBody: expect.objectContaining({
          helpful: false,
          comment: 'Could be better',
          source: 'chat_inline',
          message_id: 'assistant-0',
        }),
        xObservabilityOptIn: undefined,
      })
    })

    // Verify thanks message appears
    await waitFor(() => {
      expect(screen.getByText('Thanks!')).toBeInTheDocument()
    })
  })

  it('allows skipping note and sending feedback without comment', async () => {
    ;(useSSEClient as jest.Mock).mockReturnValue({
      connect: mockConnect,
      disconnect: mockDisconnect,
      sendText: mockSendText,
      messages: [
        { message_type: 'response', data: 'Assistant message', turn_complete: true }
      ],
      sessionId: 'test-session',
    })

    const { rerender } = render(<ChatClient locale="en" />)
    rerender(<ChatClient locale="en" />)

    await waitFor(() => {
      expect(screen.getByText('Assistant message')).toBeInTheDocument()
    })

    // Click thumbs up
    const thumbsUpButtons = screen.getAllByLabelText('Thumbs up')
    fireEvent.click(thumbsUpButtons[thumbsUpButtons.length - 1])

    // Click Send without entering a note
    const sendButtons = await screen.findAllByText('Send')
    fireEvent.click(sendButtons[0])

    // Verify feedback was sent without note
    await waitFor(() => {
      expect(mockPostFeedback).toHaveBeenCalledWith({
        requestBody: expect.objectContaining({
          helpful: true,
          comment: undefined,
          source: 'chat_inline',
        }),
        xObservabilityOptIn: undefined,
      })
    })

    // Verify thanks message appears
    await waitFor(() => {
      expect(screen.getByText('Thanks!')).toBeInTheDocument()
    })
  })

  it('allows adding note after initial feedback', async () => {
    ;(useSSEClient as jest.Mock).mockReturnValue({
      connect: mockConnect,
      disconnect: mockDisconnect,
      sendText: mockSendText,
      messages: [
        { message_type: 'response', data: 'Response text', turn_complete: true }
      ],
      sessionId: 'test-session',
    })

    const { rerender } = render(<ChatClient locale="en" />)
    rerender(<ChatClient locale="en" />)

    await waitFor(() => {
      expect(screen.getByText('Response text')).toBeInTheDocument()
    })

    // Click thumbs up
    const thumbsUpButtons = screen.getAllByLabelText('Thumbs up')
    fireEvent.click(thumbsUpButtons[thumbsUpButtons.length - 1])

    // Send without note initially
    const sendButtons = await screen.findAllByText('Send')
    fireEvent.click(sendButtons[0])

    // Wait for thanks message
    await waitFor(() => {
      expect(screen.getByText('Thanks!')).toBeInTheDocument()
    })

    // Click "Add note" link
    const addNoteButton = screen.getByText('Add note')
    fireEvent.click(addNoteButton)

    // Verify input field reappears
    expect(screen.getByPlaceholderText('Optional note…')).toBeInTheDocument()
  })

  it('handles Spanish locale correctly', async () => {
    ;(useSSEClient as jest.Mock).mockReturnValue({
      connect: mockConnect,
      disconnect: mockDisconnect,
      sendText: mockSendText,
      messages: [
        { message_type: 'response', data: 'Hola', turn_complete: true }
      ],
      sessionId: 'test-session',
    })

    const { rerender } = render(<ChatClient locale="es" />)
    rerender(<ChatClient locale="es" />)

    await waitFor(() => {
      expect(screen.getByText('Hola')).toBeInTheDocument()
    })

    // Click thumbs up
    const thumbsUpButtons = screen.getAllByLabelText('Thumbs up')
    fireEvent.click(thumbsUpButtons[thumbsUpButtons.length - 1])

    // Verify Spanish UI elements (single Send button, optional note)
    expect(await screen.findByPlaceholderText('Nota opcional…')).toBeInTheDocument()
    expect(screen.getByText('Enviar')).toBeInTheDocument()
  })

  it('disables input while sending feedback', async () => {
    // Mock slow feedback submission
    mockPostFeedback.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)))

    ;(useSSEClient as jest.Mock).mockReturnValue({
      connect: mockConnect,
      disconnect: mockDisconnect,
      sendText: mockSendText,
      messages: [
        { message_type: 'response', data: 'Message', turn_complete: true }
      ],
      sessionId: 'test-session',
    })

    const { rerender } = render(<ChatClient locale="en" />)
    rerender(<ChatClient locale="en" />)

    await waitFor(() => {
      expect(screen.getByText('Message')).toBeInTheDocument()
    })

    // Click thumbs up
    const thumbsUpButtons = screen.getAllByLabelText('Thumbs up')
    fireEvent.click(thumbsUpButtons[thumbsUpButtons.length - 1])

    // Enter note and send
    const noteInput = await screen.findByPlaceholderText('Optional note…')
    fireEvent.change(noteInput, { target: { value: 'Great!' } })
    
    const sendButtons = screen.getAllByText('Send')
    fireEvent.click(sendButtons[0])

    // Verify button shows "Sending..." and input is disabled
    expect(screen.getByText('Sending…')).toBeInTheDocument()
    expect(noteInput).toBeDisabled()

    // Wait for completion
    await waitFor(() => {
      expect(screen.getByText('Thanks!')).toBeInTheDocument()
    })
  })

  it('handles feedback submission errors gracefully', async () => {
    mockPostFeedback.mockRejectedValueOnce(new Error('Network error'))

    ;(useSSEClient as jest.Mock).mockReturnValue({
      connect: mockConnect,
      disconnect: mockDisconnect,
      sendText: mockSendText,
      messages: [
        { message_type: 'response', data: 'Message', turn_complete: true }
      ],
      sessionId: 'test-session',
    })

    const { rerender } = render(<ChatClient locale="en" />)
    rerender(<ChatClient locale="en" />)

    await waitFor(() => {
      expect(screen.getByText('Message')).toBeInTheDocument()
    })

    // Click thumbs down and skip note
    const thumbsDownButtons = screen.getAllByLabelText('Thumbs down')
    fireEvent.click(thumbsDownButtons[thumbsDownButtons.length - 1])

    // Click Send without entering a note to trigger error path
    const sendButtons = await screen.findAllByText('Send')
    fireEvent.click(sendButtons[0])

    // Verify error message appears
    await waitFor(() => {
      expect(screen.getByText('Could not send feedback')).toBeInTheDocument()
    })
  })
})