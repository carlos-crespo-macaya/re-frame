'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'

export function ChatClient({ locale }: { locale: string }) {
  const router = useRouter()
  const [messages, setMessages] = useState<Array<{ role: 'user' | 'assistant', content: string }>>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleBack = () => {
    router.push(`/${locale}`)
  }

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return

    const userMessage = { role: 'user' as const, content: input }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      setTimeout(() => {
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: 'Hello! I\'m your CBT assistant. How are you feeling today?'
        }])
        setIsLoading(false)
      }, 1000)
    } catch (error) {
      console.error('Error sending message:', error)
      setIsLoading(false)
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
        
        {isLoading && (
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
