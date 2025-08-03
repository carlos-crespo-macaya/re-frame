import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { useRouter } from 'next/navigation'
import { InterfaceSelector } from '../InterfaceSelector'

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}))

// Mock the feature flags API
jest.mock('@/lib/api/featureFlags', () => ({
  fetchUiFeatureFlags: jest.fn(),
}))

import { fetchUiFeatureFlags } from '@/lib/api/featureFlags'

const mockFetchUiFeatureFlags = fetchUiFeatureFlags as jest.MockedFunction<typeof fetchUiFeatureFlags>
const mockPush = jest.fn()
const mockRouter = {
  push: mockPush,
  back: jest.fn(),
  forward: jest.fn(),
  refresh: jest.fn(),
  replace: jest.fn(),
  prefetch: jest.fn(),
}

beforeEach(() => {
  (useRouter as jest.Mock).mockReturnValue(mockRouter)
  mockPush.mockClear()

  // Mock feature flags to return all interfaces enabled by default
  mockFetchUiFeatureFlags.mockResolvedValue({
    chat_mode_enabled: true,
    voice_mode_enabled: true,
    notepad_mode_enabled: true,
  })
})

describe('InterfaceSelector', () => {
  it('renders all interface options for English locale', async () => {
    render(<InterfaceSelector locale="en" />)

    expect(screen.queryByText('Choose Your Interface')).not.toBeInTheDocument()

    // Wait for feature flags to load and interfaces to appear
    await waitFor(() => {
      expect(screen.getByText('Text Chat')).toBeInTheDocument()
      expect(screen.getByText('Voice Conversation')).toBeInTheDocument()
      expect(screen.getByText('Structured Form')).toBeInTheDocument()
    })
  })

  it('renders all interface options for Spanish locale', async () => {
    render(<InterfaceSelector locale="es" />)

    expect(screen.queryByText('Elige Tu Interfaz')).not.toBeInTheDocument()

    // Wait for feature flags to load and interfaces to appear
    await waitFor(() => {
      expect(screen.getByText('Chat de Texto')).toBeInTheDocument()
      expect(screen.getByText('Conversación por Voz')).toBeInTheDocument()
      expect(screen.getByText('Formulario Estructurado')).toBeInTheDocument()
    })
  })

  it('highlights current interface when specified', async () => {
    render(<InterfaceSelector locale="en" currentInterface="chat" />)

    // Wait for feature flags to load and interfaces to appear
    await waitFor(() => {
      expect(screen.getByText('Text Chat')).toBeInTheDocument()
    })

    // Find the interface card by its button text "Current"
    const currentButton = screen.getByText('Current')
    expect(currentButton).toBeInTheDocument()

    // Check that the chat interface card has the proper ring classes
    const chatCard = screen.getByText('Text Chat').closest('[class*="ring-2"]')
    expect(chatCard).toBeInTheDocument()
  })

  it('navigates to correct interface when clicked', async () => {
    render(<InterfaceSelector locale="en" />)

    // Wait for feature flags to load and interfaces to appear
    await waitFor(() => {
      expect(screen.getByText('Voice Conversation')).toBeInTheDocument()
    })

    const voiceInterface = screen.getByText('Voice Conversation').closest('div')
    fireEvent.click(voiceInterface!)

    expect(mockPush).toHaveBeenCalledWith('/en/voice')
  })

  it('navigates to correct Spanish interface when clicked', async () => {
    render(<InterfaceSelector locale="es" />)

    // Wait for feature flags to load and interfaces to appear
    await waitFor(() => {
      expect(screen.getByText('Formulario Estructurado')).toBeInTheDocument()
    })

    const formInterface = screen.getByText('Formulario Estructurado').closest('div')
    fireEvent.click(formInterface!)

    expect(mockPush).toHaveBeenCalledWith('/es/form')
  })

  it('shows "Current" button for active interface', async () => {
    render(<InterfaceSelector locale="en" currentInterface="voice" />)

    // Wait for feature flags to load and interfaces to appear
    await waitFor(() => {
      expect(screen.getByText('Voice Conversation')).toBeInTheDocument()
    })

    // Find the voice interface card and check if it has "Current" button
    const voiceCard = screen.getByText('Voice Conversation').closest('div')?.closest('div')?.closest('div')
    expect(voiceCard?.querySelector('button')).toHaveTextContent('Current')
  })

  it('shows "Select" button for inactive interfaces', async () => {
    render(<InterfaceSelector locale="en" currentInterface="chat" />)

    // Wait for feature flags to load and interfaces to appear
    await waitFor(() => {
      expect(screen.getByText('Voice Conversation')).toBeInTheDocument()
    })

    // Find the voice interface card and check if it has "Select" button
    const voiceCard = screen.getByText('Voice Conversation').closest('div')?.closest('div')?.closest('div')
    expect(voiceCard?.querySelector('button')).toHaveTextContent('Select')
  })

  it('applies custom className when provided', async () => {
    const { container } = render(
      <InterfaceSelector locale="en" className="custom-class" />
    )

    // Wait for feature flags to load
    await waitFor(() => {
      expect(screen.getByText('Text Chat')).toBeInTheDocument()
    })

    expect(container.firstChild).toHaveClass('custom-class')
  })

  it('only shows enabled interfaces based on feature flags', async () => {
    // Mock feature flags with only chat enabled
    mockFetchUiFeatureFlags.mockResolvedValue({
      chat_mode_enabled: true,
      voice_mode_enabled: false,
      notepad_mode_enabled: false,
    })

    render(<InterfaceSelector locale="en" />)

    // Wait for feature flags to load
    await waitFor(() => {
      expect(screen.getByText('Text Chat')).toBeInTheDocument()
    })

    // Only chat should be visible
    expect(screen.getByText('Text Chat')).toBeInTheDocument()
    expect(screen.queryByText('Voice Conversation')).not.toBeInTheDocument()
    expect(screen.queryByText('Structured Form')).not.toBeInTheDocument()
  })
})