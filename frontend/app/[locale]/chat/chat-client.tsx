'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { useSSEClient } from '@/lib/streaming/use-sse-client'

export function ChatClient({ locale }: { locale: string }) {
  const router = useRouter()
  const [messages, setMessages] = useState<Array<{ role: 'user' | 'assistant', content: string }>>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [assistantBuffer, setAssistantBuffer] = useState('')
  const processedIndexRef = useRef(0)
  const bufferRef = useRef('')
  
  // Initialize SSE client
  const sseClient = useSSEClient({
    baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    autoConnect: false,
  })

  // Connect to SSE on mount
  useEffect(() => {
    const connectToSSE = async () => {
      try {
        await sseClient.connect(undefined, locale, false)
      } catch (error) {
        console.error('Failed to connect to SSE:', error)
      }
    }
    
    connectToSSE()
    
    return () => {
      sseClient.disconnect()
    }
  }, [locale]) // eslint-disable-line react-hooks/exhaustive-deps
  
  // Handle incoming SSE messages: accumulate 'response' chunks and flush on turn_complete
  // Fix: ensure chunks received in the same tick as turn_complete are flushed by using a local buffer
  useEffect(() => {
    const msgs = sseClient.messages || []
    let localBuffer = bufferRef.current
    let didTurnComplete = false

    for (let i = processedIndexRef.current; i < msgs.length; i++) {
      const msg = msgs[i] as any

      // Accept multiple possible shapes to be robust to transport differences
      // 1) Normalized ServerMessage: { message_type: 'response', data: string }
      // 2) Raw SSE payload (if it ever leaks through): { type: 'content', data: string }
      // 3) Fallback: any object with text/plain and data
      if (msg) {
        if (msg.message_type === 'response' && typeof msg.data === 'string') {
          localBuffer += msg.data
        } else if (msg.type === 'content' && typeof msg.data === 'string') {
          localBuffer += msg.data
        } else if (msg.mime_type === 'text/plain' && typeof msg.data === 'string') {
          localBuffer += msg.data
        }
      }

      if (msg && 'turn_complete' in msg && msg.turn_complete) {
        didTurnComplete = true
      }
    }

    // Reflect any new chunks in UI
    if (localBuffer !== bufferRef.current) {
      setAssistantBuffer(localBuffer)
    }

    // If the turn completed, flush everything we've accumulated (including chunks from this loop)
    if (didTurnComplete) {
      const finalContent = localBuffer
      if (finalContent) {
        setMessages(prev => [...prev, { role: 'assistant', content: finalContent }])
      }
      bufferRef.current = ''
      setAssistantBuffer('')
      setIsLoading(false)
    }

    processedIndexRef.current = msgs.length
  }, [sseClient.messages])

  // Keep a ref in sync with assistantBuffer to avoid stale closures during flush
  useEffect(() => {
    bufferRef.current = assistantBuffer
  }, [assistantBuffer])

  const handleBack = () => {
    router.push(`/${locale}`)
  }

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return

    const userMessage = { role: 'user' as const, content: input }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)
    setAssistantBuffer('')

    try {
      // Send message via SSE
      await sseClient.sendText(input)
    } catch (error) {
      console.error('Error sending message:', error)
      setIsLoading(false)
      // Add error message to chat
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      }])
    }
  }

  return (
    <div className="flex flex-col h-screen bg-[#161616] text-[#EDEDED]">
      {/* Header */}
      <div className="border-b border-[#404040] p-4">
        <div className="flex items-center justify-between">
          <button
            onClick={handleBack}
            className="text-primary-400 hover:text-primary-300"
          >
            ← Back
          </button>
          <h1 className="text-xl font-semibold text-[#EDEDED]">
            CBT Session
          </h1>
          <div></div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-[#B0B0B0] mt-8">
            <p>Welcome to your CBT session. How can I help you today?</p>
          </div>
        )}
        
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                message.role === 'user'
                  ? 'bg-primary-500 text-white'
                  : 'bg-[#2a2a2a] text-[#EDEDED]'
              }`}
            >
              {message.content}
            </div>
          </div>
        ))}
        
        {/* Show streaming message buffer */}
        {assistantBuffer && (
          <div className="flex justify-start">
            <div className="max-w-xs lg:max-w-md px-4 py-2 rounded-lg bg-[#2a2a2a] text-[#EDEDED]">
              {assistantBuffer}
            </div>
          </div>
        )}
        
        {isLoading && !assistantBuffer && (
          <div className="flex justify-start">
            <div className="bg-[#2a2a2a] px-4 py-2 rounded-lg">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-[#B0B0B0] rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-[#B0B0B0] rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-[#B0B0B0] rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="border-t border-[#404040] p-4">
        <div className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder="Type your message..."
            className="flex-1 border border-[#404040] rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 bg-[#2a2a2a] text-[#EDEDED] placeholder-[#B0B0B0]"
            disabled={isLoading}
          />
          <button
            onClick={handleSendMessage}
            disabled={!input.trim() || isLoading}
            className="bg-primary-500 text-white px-6 py-2 rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  )
}
