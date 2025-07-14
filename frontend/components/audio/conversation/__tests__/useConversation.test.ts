import { renderHook, act } from '@testing-library/react'
import { useConversation } from '../useConversation'

describe('useConversation', () => {
  it('should initialize with empty state', () => {
    const { result } = renderHook(() => useConversation())
    
    expect(result.current.messages).toEqual([])
    expect(result.current.isRecording).toBe(false)
    expect(result.current.isAISpeaking).toBe(false)
    expect(result.current.currentTranscription).toBe('')
  })
  
  it('should add messages', () => {
    const { result } = renderHook(() => useConversation())
    
    act(() => {
      result.current.addMessage('user', 'Hello')
    })
    
    expect(result.current.messages).toHaveLength(1)
    expect(result.current.messages[0]).toMatchObject({
      role: 'user',
      content: 'Hello',
      id: expect.any(String),
      timestamp: expect.any(Number)
    })
    
    act(() => {
      result.current.addMessage('ai', 'Hi there!', '/audio/response.mp3')
    })
    
    expect(result.current.messages).toHaveLength(2)
    expect(result.current.messages[1]).toMatchObject({
      role: 'ai',
      content: 'Hi there!',
      audioUrl: '/audio/response.mp3'
    })
  })
  
  it('should manage recording state', () => {
    const { result } = renderHook(() => useConversation())
    
    act(() => {
      result.current.setRecording(true)
    })
    
    expect(result.current.isRecording).toBe(true)
    
    act(() => {
      result.current.setCurrentTranscription('Testing...')
    })
    
    expect(result.current.currentTranscription).toBe('Testing...')
    
    act(() => {
      result.current.setRecording(false)
    })
    
    expect(result.current.isRecording).toBe(false)
    expect(result.current.currentTranscription).toBe('')
  })
  
  it('should manage AI speaking state', () => {
    const { result } = renderHook(() => useConversation())
    
    act(() => {
      result.current.setAISpeaking(true)
    })
    
    expect(result.current.isAISpeaking).toBe(true)
    
    act(() => {
      result.current.setAISpeaking(false)
    })
    
    expect(result.current.isAISpeaking).toBe(false)
  })
  
  it('should clear conversation', () => {
    const { result } = renderHook(() => useConversation())
    
    // Add some messages
    act(() => {
      result.current.addMessage('user', 'Message 1')
      result.current.addMessage('ai', 'Response 1')
      result.current.setRecording(true)
      result.current.setCurrentTranscription('Test')
    })
    
    expect(result.current.messages).toHaveLength(2)
    expect(result.current.isRecording).toBe(true)
    
    // Clear conversation
    act(() => {
      result.current.clearConversation()
    })
    
    expect(result.current.messages).toEqual([])
    expect(result.current.isRecording).toBe(false)
    expect(result.current.isAISpeaking).toBe(false)
    expect(result.current.currentTranscription).toBe('')
  })
  
  it('should generate unique message IDs', () => {
    const { result } = renderHook(() => useConversation())
    
    act(() => {
      result.current.addMessage('user', 'Message 1')
      result.current.addMessage('user', 'Message 2')
      result.current.addMessage('user', 'Message 3')
    })
    
    const ids = result.current.messages.map(m => m.id)
    const uniqueIds = new Set(ids)
    
    expect(uniqueIds.size).toBe(3)
  })
  
  it('should calculate session summary', () => {
    const { result } = renderHook(() => useConversation())
    
    // Add messages with time gaps
    act(() => {
      // Mock timestamps
      const now = Date.now()
      jest.spyOn(Date, 'now')
        .mockReturnValueOnce(now)
        .mockReturnValueOnce(now + 60000) // 1 minute later
        .mockReturnValueOnce(now + 120000) // 2 minutes later
      
      result.current.addMessage('user', 'Hello')
      result.current.addMessage('ai', 'Hi')
      result.current.addMessage('user', 'Bye')
    })
    
    const summary = result.current.getSessionSummary()
    
    expect(summary).toEqual({
      duration: 120, // 2 minutes in seconds
      messageCount: 3,
      insights: []
    })
    
    // Restore Date.now
    jest.restoreAllMocks()
  })
  
  it('should return null summary for empty conversation', () => {
    const { result } = renderHook(() => useConversation())
    
    const summary = result.current.getSessionSummary()
    expect(summary).toBeNull()
  })
})