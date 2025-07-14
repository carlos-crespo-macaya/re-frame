import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { SessionEndView } from '../SessionEndView'

describe('SessionEndView', () => {
  it('should show thank you message', () => {
    render(<SessionEndView />)
    
    expect(screen.getByText(/thank you for sharing today/i)).toBeInTheDocument()
    expect(screen.getByText(/these perspectives are here to support you/i)).toBeInTheDocument()
  })
  
  it('should show start new session button', async () => {
    const user = userEvent.setup()
    const onNewSession = jest.fn()
    render(<SessionEndView onNewSession={onNewSession} />)
    
    const newSessionButton = screen.getByRole('button', { name: /start new session/i })
    await user.click(newSessionButton)
    
    expect(onNewSession).toHaveBeenCalled()
  })
  
  it('should show session summary if provided', () => {
    const sessionSummary = {
      duration: 300, // 5 minutes in seconds
      messageCount: 10,
      insights: [
        'You explored feelings of anxiety',
        'You identified helpful coping strategies'
      ]
    }
    
    render(<SessionEndView sessionSummary={sessionSummary} />)
    
    expect(screen.getByText(/5 minutes/i)).toBeInTheDocument()
    expect(screen.getByText(/10 messages/i)).toBeInTheDocument()
    expect(screen.getByText(/You explored feelings of anxiety/i)).toBeInTheDocument()
    expect(screen.getByText(/You identified helpful coping strategies/i)).toBeInTheDocument()
  })
})