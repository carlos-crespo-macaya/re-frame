import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { useRouter } from 'next/navigation'
import { InterfaceSelector } from '../InterfaceSelector'

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}))

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
})

describe('InterfaceSelector', () => {
  it('renders all interface options for English locale', () => {
    render(<InterfaceSelector locale="en" />)
    
    expect(screen.getByText('Choose Your Interface')).toBeInTheDocument()
    expect(screen.getByText('Text Chat')).toBeInTheDocument()
    expect(screen.getByText('Voice Conversation')).toBeInTheDocument()
    expect(screen.getByText('Structured Form')).toBeInTheDocument()
  })

  it('renders all interface options for Spanish locale', () => {
    render(<InterfaceSelector locale="es" />)
    
    expect(screen.getByText('Elige Tu Interfaz')).toBeInTheDocument()
    expect(screen.getByText('Chat de Texto')).toBeInTheDocument()
    expect(screen.getByText('Conversación por Voz')).toBeInTheDocument()
    expect(screen.getByText('Formulario Estructurado')).toBeInTheDocument()
  })

  it('highlights current interface when specified', () => {
    render(<InterfaceSelector locale="en" currentInterface="chat" />)
    
    // Find the interface card by its button text "Current"
    const currentButton = screen.getByText('Current')
    expect(currentButton).toBeInTheDocument()
    
    // Check that the chat interface card has the proper ring classes
    const chatCard = screen.getByText('Text Chat').closest('[class*="ring-2"]')
    expect(chatCard).toBeInTheDocument()
  })

  it('navigates to correct interface when clicked', () => {
    render(<InterfaceSelector locale="en" />)
    
    const voiceInterface = screen.getByText('Voice Conversation').closest('div')
    fireEvent.click(voiceInterface!)
    
    expect(mockPush).toHaveBeenCalledWith('/en/voice')
  })

  it('navigates to correct Spanish interface when clicked', () => {
    render(<InterfaceSelector locale="es" />)
    
    const formInterface = screen.getByText('Formulario Estructurado').closest('div')
    fireEvent.click(formInterface!)
    
    expect(mockPush).toHaveBeenCalledWith('/es/form')
  })

  it('shows "Current" button for active interface', () => {
    render(<InterfaceSelector locale="en" currentInterface="voice" />)
    
    // Find the voice interface card and check if it has "Current" button
    const voiceCard = screen.getByText('Voice Conversation').closest('div')?.closest('div')?.closest('div')
    expect(voiceCard?.querySelector('button')).toHaveTextContent('Current')
  })

  it('shows "Select" button for inactive interfaces', () => {
    render(<InterfaceSelector locale="en" currentInterface="chat" />)
    
    // Find the voice interface card and check if it has "Select" button
    const voiceCard = screen.getByText('Voice Conversation').closest('div')?.closest('div')?.closest('div')
    expect(voiceCard?.querySelector('button')).toHaveTextContent('Select')
  })

  it('applies custom className when provided', () => {
    const { container } = render(
      <InterfaceSelector locale="en" className="custom-class" />
    )
    
    expect(container.firstChild).toHaveClass('custom-class')
  })
})