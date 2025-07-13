'use client'

import { useState } from 'react'
import { ConversationView, SessionEndView, useConversation } from '.'

/**
 * Demo component showing how to integrate conversation mode with audio recording
 */
export function ConversationDemo() {
  const [sessionEnded, setSessionEnded] = useState(false)
  const conversation = useConversation()
  
  // Simulated audio recording functions
  const handleStartRecording = () => {
    conversation.setRecording(true)
    
    // Simulate transcription updates
    const simulateTranscription = () => {
      const phrases = [
        'I feel anxious about',
        'I feel anxious about the meeting',
        'I feel anxious about the meeting tomorrow'
      ]
      
      phrases.forEach((phrase, index) => {
        setTimeout(() => {
          if (conversation.isRecording) {
            conversation.setCurrentTranscription(phrase)
          }
        }, (index + 1) * 500)
      })
    }
    
    simulateTranscription()
  }
  
  const handleStopRecording = () => {
    conversation.setRecording(false)
    
    if (conversation.currentTranscription) {
      // Add user message
      conversation.addMessage('user', conversation.currentTranscription)
      
      // Simulate AI response
      conversation.setAISpeaking(true)
      
      setTimeout(() => {
        conversation.addMessage(
          'ai',
          'I understand that you\'re feeling anxious about tomorrow\'s meeting. It\'s completely normal to feel this way before important events. Would you like to talk about what specifically concerns you?'
        )
        conversation.setAISpeaking(false)
      }, 1500)
    }
  }
  
  const handleEndSession = () => {
    setSessionEnded(true)
  }
  
  const handleNewSession = () => {
    setSessionEnded(false)
    conversation.clearConversation()
  }
  
  if (sessionEnded) {
    return (
      <SessionEndView
        onNewSession={handleNewSession}
        sessionSummary={conversation.getSessionSummary() || undefined}
      />
    )
  }
  
  return (
    <ConversationView
      messages={conversation.messages}
      isRecording={conversation.isRecording}
      isAISpeaking={conversation.isAISpeaking}
      currentTranscription={conversation.currentTranscription}
      onStartRecording={handleStartRecording}
      onStopRecording={handleStopRecording}
      onEndSession={handleEndSession}
    />
  )
}