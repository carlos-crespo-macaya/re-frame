'use client'

import { useState, useCallback, useRef } from 'react'
import type { ConversationMessage, ConversationState } from './types'

export function useConversation() {
  const [state, setState] = useState<ConversationState>({
    messages: [],
    isRecording: false,
    isAISpeaking: false
  })
  
  const messageIdRef = useRef(0)
  
  const generateMessageId = () => {
    messageIdRef.current += 1
    return `msg-${messageIdRef.current}`
  }
  
  const addMessage = useCallback((role: 'user' | 'ai', content: string, audioUrl?: string) => {
    const newMessage: ConversationMessage = {
      id: generateMessageId(),
      role,
      content,
      timestamp: Date.now(),
      audioUrl
    }
    
    setState(prev => ({
      ...prev,
      messages: [...prev.messages, newMessage]
    }))
    
    return newMessage
  }, [])
  
  const setRecording = useCallback((isRecording: boolean) => {
    setState(prev => ({
      ...prev,
      isRecording
    }))
  }, [])
  
  const setAISpeaking = useCallback((isAISpeaking: boolean) => {
    setState(prev => ({
      ...prev,
      isAISpeaking
    }))
  }, [])
  
  
  const clearConversation = useCallback(() => {
    setState({
      messages: [],
      isRecording: false,
      isAISpeaking: false
    })
    messageIdRef.current = 0
  }, [])
  
  const getSessionSummary = useCallback(() => {
    const messages = state.messages
    if (messages.length === 0) return null
    
    const firstMessageTime = messages[0].timestamp
    const lastMessageTime = messages[messages.length - 1].timestamp
    const duration = Math.floor((lastMessageTime - firstMessageTime) / 1000)
    
    return {
      duration,
      messageCount: messages.length,
      insights: [] // Could be enhanced with actual analysis
    }
  }, [state.messages])
  
  return {
    ...state,
    addMessage,
    setRecording,
    setAISpeaking,
    clearConversation,
    getSessionSummary
  }
}