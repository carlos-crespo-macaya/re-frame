'use client'

import { useState } from 'react'
import { Button } from '@/components/ui'
import type { MessageBubbleProps } from './types'

export function MessageBubble({ message, isLast = false }: MessageBubbleProps) {
  const [isPlaying, setIsPlaying] = useState(false)
  
  const formatTime = (timestamp: number) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }
  
  const handlePlayAudio = () => {
    // TODO: Implement actual audio playback
    setIsPlaying(!isPlaying)
  }
  
  const isUser = message.role === 'user'
  
  return (
    <div
      data-role={message.role}
      data-last-message={isLast}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      <div
        className={`
          max-w-[70%] rounded-lg px-4 py-2 
          ${isUser 
            ? 'bg-primary-500 text-white' 
            : 'bg-neutral-100 text-neutral-900'
          }
        `}
      >
        {/* Role label */}
        <div className={`text-xs font-medium mb-1 ${isUser ? 'text-primary-100' : 'text-neutral-500'}`}>
          {isUser ? 'You' : 'AI'}:
        </div>
        
        {/* Message content */}
        <div className="text-sm">
          {message.content}
        </div>
        
        {/* Audio playback button if available */}
        {message.audioUrl && (
          <div className="mt-2">
            <Button
              size="small"
              variant="secondary"
              onClick={handlePlayAudio}
              aria-label={isPlaying ? 'Pause audio' : 'Play audio'}
              className="text-xs"
            >
              {isPlaying ? '⏸️ Pause' : '▶️ Play'} Audio
            </Button>
          </div>
        )}
        
        {/* Timestamp */}
        <time
          role="time"
          className={`text-xs mt-1 block ${isUser ? 'text-primary-100' : 'text-neutral-400'}`}
          dateTime={new Date(message.timestamp).toISOString()}
        >
          {formatTime(message.timestamp)}
        </time>
      </div>
    </div>
  )
}