import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import FeedbackPage from '../page'
import { postFeedbackApiFeedbackPost } from '@/lib/api/generated/sdk.gen'
import { useRecaptcha } from '@/lib/recaptcha/useRecaptcha'

// Mock dependencies
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
  usePathname: () => '/en/feedback',
}))

jest.mock('@/lib/api/generated/sdk.gen', () => ({
  postFeedbackApiFeedbackPost: jest.fn(),
}))

jest.mock('@/lib/recaptcha/useRecaptcha', () => ({
  useRecaptcha: jest.fn(),
}))

jest.mock('@/components/layout/AppLayout', () => ({
  AppLayout: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}))

jest.mock('@/components/layout/GlassCard', () => ({
  GlassCard: ({ children, className }: { children: React.ReactNode; className?: string }) => (
    <div className={className}>{children}</div>
  ),
}))

jest.mock('@/components/icons', () => ({
  ThumbsUpIcon: () => <div>ThumbsUp</div>,
  ThumbsDownIcon: () => <div>ThumbsDown</div>,
}))

describe('FeedbackPage', () => {
  const mockExecute = jest.fn()
  const mockPostFeedback = postFeedbackApiFeedbackPost as jest.Mock

  beforeEach(() => {
    jest.clearAllMocks()
    ;(useRecaptcha as jest.Mock).mockReturnValue({
      ready: true,
      execute: mockExecute,
      error: null,
    })
    mockExecute.mockResolvedValue('test-token')
    mockPostFeedback.mockResolvedValue({})
  })

  it('clears form after successful submission', async () => {
    render(<FeedbackPage params={{ locale: 'en' }} />)

    // Find and fill the comment textarea
    const textarea = screen.getByPlaceholderText('Add a note… (optional)')
    fireEvent.change(textarea, { target: { value: 'Great app!' } })
    expect(textarea).toHaveValue('Great app!')

    // Click thumbs up button
    const thumbsUpButton = screen.getByTitle('Thumbs up')
    fireEvent.click(thumbsUpButton)

    // Wait for success message
    await waitFor(() => {
      expect(screen.getByText('Thanks for the feedback!')).toBeInTheDocument()
    })

    // Verify form is cleared
    expect(textarea).toHaveValue('')
    
    // Verify button selection is cleared (by checking it's not in the selected state)
    // Selected button has specific classes including 'scale-110'
    expect(thumbsUpButton).not.toHaveClass('scale-110')
  })

  it('retains form state on submission error', async () => {
    mockPostFeedback.mockRejectedValueOnce(new Error('Network error'))
    
    render(<FeedbackPage params={{ locale: 'en' }} />)

    // Fill the comment
    const textarea = screen.getByPlaceholderText('Add a note… (optional)')
    fireEvent.change(textarea, { target: { value: 'Test comment' } })

    // Click thumbs down button
    const thumbsDownButton = screen.getByTitle('Thumbs down')
    fireEvent.click(thumbsDownButton)

    // Wait for error message
    await waitFor(() => {
      expect(screen.getByText('Could not submit feedback. Please try later.')).toBeInTheDocument()
    })

    // Verify form state is retained on error
    expect(textarea).toHaveValue('Test comment')
  })

  it('handles Spanish locale correctly', async () => {
    render(<FeedbackPage params={{ locale: 'es' }} />)

    // Find Spanish UI elements
    expect(screen.getByText('Opinión')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Añade una nota… (opcional)')).toBeInTheDocument()

    // Submit feedback
    const thumbsUpButton = screen.getByTitle('Pulgar arriba')
    fireEvent.click(thumbsUpButton)

    // Wait for Spanish success message
    await waitFor(() => {
      expect(screen.getByText('¡Gracias por tu opinión!')).toBeInTheDocument()
    })

    // Verify form is cleared
    const textarea = screen.getByPlaceholderText('Añade una nota… (opcional)')
    expect(textarea).toHaveValue('')
  })

  it('disables buttons when reCAPTCHA is not ready', () => {
    ;(useRecaptcha as jest.Mock).mockReturnValue({
      ready: false,
      execute: mockExecute,
      error: null,
    })

    render(<FeedbackPage params={{ locale: 'en' }} />)

    const thumbsUpButton = screen.getByTitle('Thumbs up')
    const thumbsDownButton = screen.getByTitle('Thumbs down')

    expect(thumbsUpButton).toBeDisabled()
    expect(thumbsDownButton).toBeDisabled()
  })

  it('sends feedback with correct payload', async () => {
    render(<FeedbackPage params={{ locale: 'en' }} />)

    const textarea = screen.getByPlaceholderText('Add a note… (optional)')
    fireEvent.change(textarea, { target: { value: 'Test feedback' } })

    const thumbsUpButton = screen.getByTitle('Thumbs up')
    fireEvent.click(thumbsUpButton)

    await waitFor(() => {
      expect(mockPostFeedback).toHaveBeenCalledWith({
        requestBody: expect.objectContaining({
          helpful: true,
          comment: 'Test feedback',
          lang: 'en',
          platform: 'web',
          source: 'feedback_page',
          recaptcha_token: 'test-token',
          recaptcha_action: 'feedback_up',
        }),
      })
    })
  })
})