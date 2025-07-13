'use client'

import { useEffect, useRef } from 'react'
import { MessageBubble } from './MessageBubble'
import type { MessageListProps } from './types'

export function MessageList({ messages }: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)
  
  // Auto-scroll to latest message
  useEffect(() => {
    if (messages.length > 0) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
    }
  }, [messages])
  
  if (messages.length === 0) {
    return <div data-testid="message-list" className="p-4" />
  }
  
  return (
    <div data-testid="message-list" className="p-4 space-y-4">
      {messages.map((message, index) => (
        <MessageBubble
          key={message.id}
          message={message}
          isLast={index === messages.length - 1}
        />
      ))}
      <div ref={messagesEndRef} />
    </div>
  )
}