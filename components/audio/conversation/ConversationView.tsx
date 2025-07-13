'use client'

import { useEffect, useRef } from 'react'
import { Button } from '@/components/ui'
import { AudioVisualizer } from '@/components/ui/AudioVisualizer'
import { MessageList } from './MessageList'
import type { ConversationViewProps } from './types'

export function ConversationView({
  messages = [],
  isRecording = false,
  isAISpeaking = false,
  currentTranscription = '',
  onStartRecording,
  onStopRecording,
  onEndSession
}: ConversationViewProps) {
  const isHoldingRef = useRef(false)
  
  // Handle keyboard push-to-talk
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === ' ' && !isHoldingRef.current) {
        e.preventDefault()
        isHoldingRef.current = true
        onStartRecording?.()
      }
    }
    
    const handleKeyUp = (e: KeyboardEvent) => {
      if (e.key === ' ' && isHoldingRef.current) {
        e.preventDefault()
        isHoldingRef.current = false
        onStopRecording?.()
      }
    }
    
    document.addEventListener('keydown', handleKeyDown)
    document.addEventListener('keyup', handleKeyUp)
    
    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      document.removeEventListener('keyup', handleKeyUp)
    }
  }, [onStartRecording, onStopRecording])
  
  const handleMouseDown = () => {
    isHoldingRef.current = true
    onStartRecording?.()
  }
  
  const handleMouseUp = () => {
    isHoldingRef.current = false
    onStopRecording?.()
  }
  
  const handleTouchStart = (e: React.TouchEvent) => {
    e.preventDefault()
    isHoldingRef.current = true
    onStartRecording?.()
  }
  
  const handleTouchEnd = (e: React.TouchEvent) => {
    e.preventDefault()
    isHoldingRef.current = false
    onStopRecording?.()
  }
  
  return (
    <div className="flex flex-col h-full max-h-[600px] bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-neutral-200">
        <h2 className="text-lg font-semibold text-neutral-900">Conversation Mode</h2>
        <Button
          variant="secondary"
          size="small"
          onClick={onEndSession}
          aria-label="End session"
        >
          End Session
        </Button>
      </div>
      
      {/* Status indicators */}
      <div className="px-4 py-2 bg-neutral-50 border-b border-neutral-100">
        {isRecording && (
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-red-600">🔴 Listening...</span>
            <AudioVisualizer audioLevel={0.5} isActive={true} />
          </div>
        )}
        {isAISpeaking && (
          <div className="text-sm font-medium text-primary-600">[🔊 Speaking...]</div>
        )}
        {isRecording && currentTranscription && (
          <div className="mt-2 text-sm text-neutral-600 italic">{currentTranscription}</div>
        )}
      </div>
      
      {/* Message history */}
      <div className="flex-1 overflow-y-auto">
        <MessageList messages={messages} />
      </div>
      
      {/* Controls */}
      <div className="p-4 border-t border-neutral-200">
        <div className="flex flex-col items-center gap-2">
          <button
            className="px-6 py-3 bg-primary-500 text-white rounded-full hover:bg-primary-600 active:bg-primary-700 transition-colors touch-none select-none"
            onMouseDown={handleMouseDown}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
            onTouchStart={handleTouchStart}
            onTouchEnd={handleTouchEnd}
            aria-label="Hold to talk"
            role="button"
          >
            Hold to Talk
          </button>
          <p className="text-xs text-neutral-500">Hold the button or press Space to speak</p>
        </div>
      </div>
    </div>
  )
}