'use client'

import { useState, useCallback, useEffect, useRef } from 'react'
import { ConversationView, SessionEndView, useConversation } from '.'
import { useSSEClient } from '@/lib/streaming/use-sse-client'
import { useAudioRecorder } from '@/lib/audio'
import { arrayBufferToBase64, float32ToPcm16 } from '@/lib/audio/audio-utils'

interface ConversationIntegratedProps {
  language?: string
}

/**
 * Integrated conversation component that connects to real backend
 */
export function ConversationIntegrated({ language = 'en-US' }: ConversationIntegratedProps) {
  const [sessionEnded, setSessionEnded] = useState(false)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const conversation = useConversation()
  const audioBufferRef = useRef<Float32Array[]>([])
  const bufferTimeoutRef = useRef<NodeJS.Timeout>()
  
  // Initialize SSE client
  const sseClient = useSSEClient({
    baseUrl: process.env.NEXT_PUBLIC_API_URL || '/api',
    autoConnect: false,
  })
  
  // Initialize audio recorder
  const audioRecorder = useAudioRecorder({
    onTranscription: (text) => {
      conversation.setCurrentTranscription(text)
    },
    onDataAvailable: (data: Float32Array) => {
      // Buffer audio data
      audioBufferRef.current.push(data)
      
      // Reset buffer timeout
      if (bufferTimeoutRef.current) {
        clearTimeout(bufferTimeoutRef.current)
      }
      
      // Send buffered audio after 100ms of silence
      bufferTimeoutRef.current = setTimeout(() => {
        sendBufferedAudio()
      }, 100)
    },
    onError: (error) => {
      console.error('Audio recording error:', error)
    }
  })
  
  // Send buffered audio data
  const sendBufferedAudio = useCallback(async () => {
    if (audioBufferRef.current.length === 0 || !sseClient.isConnected) return
    
    try {
      // Merge all audio chunks
      const totalLength = audioBufferRef.current.reduce((acc, chunk) => acc + chunk.length, 0)
      const mergedAudio = new Float32Array(totalLength)
      let offset = 0
      
      for (const chunk of audioBufferRef.current) {
        mergedAudio.set(chunk, offset)
        offset += chunk.length
      }
      
      // Convert to 16-bit PCM and base64
      const pcm16 = float32ToPcm16(mergedAudio)
      const arrayBuffer = pcm16.buffer.slice(pcm16.byteOffset, pcm16.byteOffset + pcm16.byteLength) as ArrayBuffer
      const base64Audio = await arrayBufferToBase64(arrayBuffer)
      
      // Send audio data
      await sseClient.sendAudio(base64Audio, false)
      
      // Clear buffer
      audioBufferRef.current = []
    } catch (error) {
      console.error('Failed to send audio:', error)
    }
  }, [sseClient])
  
  // Process SSE messages
  useEffect(() => {
    if (!sseClient.isConnected) return
    
    // Get the latest messages
    const textMessages = sseClient.getMessagesByType('response')
    const audioMessages = sseClient.getMessagesByType('audio')
    const transcriptionMessages = sseClient.getMessagesByType('transcription')
    
    // Process text responses
    const latestText = textMessages[textMessages.length - 1]
    if (latestText) {
      conversation.addMessage('ai', latestText.data)
      conversation.setAISpeaking(false)
    }
    
    // Process transcriptions
    const latestTranscription = transcriptionMessages[transcriptionMessages.length - 1]
    if (latestTranscription) {
      conversation.setCurrentTranscription(latestTranscription.data)
    }
  }, [sseClient.messages, sseClient.isConnected, conversation])
  
  // Connect to backend when component mounts
  useEffect(() => {
    const connect = async () => {
      try {
        await sseClient.connect(undefined, language)
        setSessionId(sseClient.sessionId)
      } catch (error) {
        console.error('Failed to connect:', error)
      }
    }
    
    connect()
    
    return () => {
      sseClient.disconnect()
      audioRecorder.cleanup()
    }
  }, [language])
  
  const handleStartRecording = useCallback(async () => {
    try {
      conversation.setRecording(true)
      conversation.setCurrentTranscription('')
      await audioRecorder.startRecording()
    } catch (error) {
      console.error('Failed to start recording:', error)
      conversation.setRecording(false)
    }
  }, [audioRecorder, conversation])
  
  const handleStopRecording = useCallback(async () => {
    try {
      await audioRecorder.stopRecording()
      conversation.setRecording(false)
      
      // Send any remaining buffered audio
      await sendBufferedAudio()
      
      if (conversation.currentTranscription) {
        // Add user message
        conversation.addMessage('user', conversation.currentTranscription)
        conversation.setAISpeaking(true)
        
        // Send text message to backend
        await sseClient.sendText(conversation.currentTranscription)
      }
    } catch (error) {
      console.error('Failed to stop recording:', error)
    }
  }, [audioRecorder, conversation, sendBufferedAudio, sseClient])
  
  const handleEndSession = () => {
    setSessionEnded(true)
  }
  
  const handleNewSession = async () => {
    setSessionEnded(false)
    conversation.clearConversation()
    
    // Reconnect with new session
    sseClient.disconnect()
    await sseClient.connect(undefined, language)
    setSessionId(sseClient.sessionId)
  }
  
  if (sessionEnded) {
    return (
      <SessionEndView
        onNewSession={handleNewSession}
        sessionSummary={conversation.getSessionSummary() || undefined}
        sessionId={sessionId || 'unknown'}
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