'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { useSSEClient } from '@/lib/streaming/use-sse-client'
import ReactMarkdown from 'react-markdown'
import { FrameworkBadge, LanguageSelector } from '@/components/ui'
import { Framework } from '@/types/api'

interface Message {
  role: 'user' | 'assistant'
  content: string
  frameworks?: string[]
}

interface Translations {
  title: string
  subtitle: string
  placeholder: string
  send: string
  back: string
  thinking: string
}

export function ChatClient({ locale }: { locale: string }) {
  const router = useRouter()
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [assistantBuffer, setAssistantBuffer] = useState('')
  const [selectedLanguage, setSelectedLanguage] = useState(locale === 'es' ? 'es-ES' : 'en-US')
  const processedIndexRef = useRef(0)
  const bufferRef = useRef('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Translations
  const translations: Record<string, Translations> = {
    en: {
      title: 'Text Chat',
      subtitle: 'Chat with re-frame in real-time',
      placeholder: 'Share your thoughts...',
      send: 'Send',
      back: '← Back to home',
      thinking: 'Thinking...',
    },
    es: {
      title: 'Chat de Texto',
      subtitle: 'Chatea con re-frame en tiempo real',
      placeholder: 'Comparte tus pensamientos...',
      send: 'Enviar',
      back: '← Volver al inicio',
      thinking: 'Pensando...',
    },
  }

  const t: Translations = translations[locale] || translations.en

  // Initialize SSE client
  const sseClient = useSSEClient({
    baseUrl: '/api/proxy',
    autoConnect: false,
  })

  useEffect(() => {
    setSelectedLanguage(locale === 'es' ? 'es-ES' : 'en-US')
  }, [locale])

  // Connect to SSE on mount
  useEffect(() => {
    const connectToSSE = async () => {
      try {
        await sseClient.connect(undefined, selectedLanguage, false)
      } catch (error) {
        console.error('Failed to connect to SSE:', error)
      }
    }

    connectToSSE()

    return () => {
      sseClient.disconnect()
    }
  }, [selectedLanguage]) // eslint-disable-line react-hooks/exhaustive-deps

  // Handle incoming SSE messages
  useEffect(() => {
    const msgs = sseClient.messages || []
    let localBuffer = bufferRef.current
    let didTurnComplete = false

    for (let i = processedIndexRef.current; i < msgs.length; i++) {
      const msg = msgs[i] as any

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

    // If the turn completed, flush everything we've accumulated
    if (didTurnComplete) {
      const finalContent = localBuffer
      if (finalContent) {
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: finalContent,
          frameworks: ['CBT'] // Default framework
        }])
      }
      bufferRef.current = ''
      setAssistantBuffer('')
      setIsLoading(false)
    }

    processedIndexRef.current = msgs.length
  }, [sseClient.messages])

  // Keep a ref in sync with assistantBuffer
  useEffect(() => {
    bufferRef.current = assistantBuffer
  }, [assistantBuffer])

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, assistantBuffer])

  const handleBack = () => {
    router.push(`/${locale}`)
  }

  const handleLanguageChange = (language: string) => {
    setSelectedLanguage(language)
    const newLocale = language.startsWith('es') ? 'es' : 'en'
    const newPath = `/${newLocale}/chat`
    router.push(newPath)
  }


  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return

    const userMessage = { role: 'user' as const, content: input }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    // Reset textarea height
    const textarea = document.querySelector('textarea')
    if (textarea) {
      textarea.style.height = '44px'
    }

    try {
      await sseClient.sendText(input)
    } catch (error) {
      console.error('Failed to send message:', error)
      setIsLoading(false)
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value)

    // Auto-resize textarea
    e.target.style.height = '44px'
    e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px'
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div
      className="flex flex-col h-screen text-white relative overflow-hidden"
      style={{
        background: 'radial-gradient(ellipse at center, #0a2a3a 0%, #062633 25%, #03141d 50%, #020c12 100%)',
      }}
    >
      {/* Header */}
      <header className="flex-shrink-0 relative z-10">
        <div className="px-16 py-6">
          <div className="flex items-center justify-between max-w-[1312px] mx-auto">
            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={handleBack}
                className="text-[#9BF7EB] hover:text-white transition-colors"
                aria-label="Back to home"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              <div className="w-8 h-8 rounded-full bg-[#9BF7EB] flex items-center justify-center">
                <span className="text-[#002e34] font-bold text-sm">R</span>
              </div>
              <h1 className="text-[24px] font-semibold text-white">
                re-frame
              </h1>
            </div>
            <button
              className="flex items-center gap-1.5 px-3 h-[32px] rounded-full bg-white/5 hover:bg-white/10 transition-colors"
              style={{ minWidth: '80px' }}
              onClick={() => {
                const newLocale = locale === 'es' ? 'en' : 'es'
                const newLanguage = newLocale === 'es' ? 'es-ES' : 'en-US'
                setSelectedLanguage(newLanguage)
                router.push(`/${newLocale}/chat`)
              }}
            >
              <svg className="w-5 h-5 text-white/70" fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 21a9.004 9.004 0 008.716-6.747M12 21a9.004 9.004 0 01-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 017.843 4.582M12 3a8.997 8.997 0 00-7.843 4.582m15.686 0A11.953 11.953 0 0112 10.5c-2.998 0-5.74-1.1-7.843-2.918m15.686 0A8.959 8.959 0 0121 12c0 .778-.099 1.533-.284 2.253m0 0A17.919 17.919 0 0112 16.5c-3.162 0-6.133-.815-8.716-2.247m0 0A9.015 9.015 0 013 12c0-1.605.42-3.113 1.157-4.418" />
              </svg>
              <span className="text-xs text-white/70">{locale === 'es' ? 'ES' : 'EN'}</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main chat area with 32px gap from header */}
      <main className="flex-1 flex flex-col overflow-hidden px-16 pb-8" style={{ paddingTop: '32px' }}>
        <div className="flex-1 flex flex-col max-w-[1312px] w-full mx-auto">
          {/* Messages container - Enhanced glassmorphic card with visible borders */}
          <div
            className="flex-1 overflow-y-auto rounded-[24px] backdrop-blur-md relative ring-1 ring-white/20 shadow-lg"
            style={{
              background: 'rgba(8, 20, 28, 0.55)',
              boxShadow: '0 0 0 1px rgba(155, 247, 235, 0.25), 0 10px 40px rgba(0, 0, 0, 0.4)',
            }}
          >
            <div className="px-8" style={{ paddingTop: '48px', paddingBottom: '32px' }}>
              {messages.length === 0 && !isLoading && (
                <div className="flex flex-col items-center justify-center text-center">
                  <p className="text-[18px] font-bold mb-2 text-white">{t.subtitle}</p>
                  <p className="text-[14px] leading-[22px]" style={{ color: 'rgba(255, 255, 255, 0.45)' }}>{t.placeholder}</p>
                </div>
              )}

              <div className="space-y-4">
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[75%] ${
                        message.role === 'user'
                          ? 'bg-[#9BF7EB] text-[#002e34]'
                          : 'bg-[#131e24] text-white/90 ring-1 ring-white/5'
                      } rounded-2xl px-5 py-3`}
                    >
                      {message.role === 'assistant' && message.frameworks && (
                        <div className="flex flex-wrap gap-2 mb-3">
                          {message.frameworks.map((fw, i) => (
                            <span key={i} className="text-xs px-3 py-1 bg-[#9BF7EB]/10 rounded-lg text-[#9BF7EB] font-medium">
                              {fw}
                            </span>
                          ))}
                        </div>
                      )}
                      <div className="text-[14px] leading-[22px]">
                        <ReactMarkdown>{message.content}</ReactMarkdown>
                      </div>
                    </div>
                  </div>
                ))}

                {/* Show buffer while streaming */}
                {assistantBuffer && (
                  <div className="flex justify-start">
                    <div className="max-w-[75%] bg-[#131e24] text-white/90 ring-1 ring-white/5 rounded-2xl px-5 py-3">
                      <div className="flex flex-wrap gap-2 mb-3">
                        <span className="text-xs px-3 py-1 bg-[#9BF7EB]/10 rounded-lg text-[#9BF7EB]">
                          CBT
                        </span>
                      </div>
                      <div className="text-[14px] leading-[22px]">
                        <ReactMarkdown>{assistantBuffer}</ReactMarkdown>
                      </div>
                    </div>
                  </div>
                )}

                {/* Loading indicator */}
                {isLoading && !assistantBuffer && (
                  <div className="flex justify-start">
                    <div className="bg-[#131e24] text-white/90 ring-1 ring-white/5 rounded-2xl px-5 py-3">
                      <div className="flex items-center gap-3">
                        <div className="flex gap-1">
                          <div className="w-2 h-2 bg-[#9BF7EB] rounded-full animate-pulse" />
                          <div className="w-2 h-2 bg-[#9BF7EB] rounded-full animate-pulse" style={{ animationDelay: '150ms' }} />
                          <div className="w-2 h-2 bg-[#9BF7EB] rounded-full animate-pulse" style={{ animationDelay: '300ms' }} />
                        </div>
                        <span className="text-[14px] leading-[22px] text-white/45">{t.thinking}</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* Input dock - Enhanced glassmorphic pill with visible borders */}
          <div className="mt-4 flex items-center h-[56px] rounded-full backdrop-blur-md relative overflow-hidden ring-1 ring-white/20"
            style={{
              background: 'rgba(8, 20, 28, 0.55)',
              boxShadow: '0 0 0 1px rgba(155, 247, 235, 0.25), 0 4px 20px rgba(0, 0, 0, 0.3)',
            }}
          >
            <textarea
              value={input}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              placeholder={t.placeholder}
              className="flex-1 px-6 bg-transparent text-white text-[14px] leading-[22px] focus:outline-none resize-none overflow-hidden placeholder:text-white/[0.45]"
              style={{
                height: '56px',
                paddingTop: '17px',
                paddingBottom: '17px',
              }}
              rows={1}
              disabled={isLoading}
            />
            <button
              type="button"
              onClick={handleSendMessage}
              disabled={isLoading || !input.trim()}
              className={`w-[56px] h-[56px] flex items-center justify-center rounded-full transition-all disabled:opacity-50 disabled:cursor-not-allowed ${
                !isLoading && input.trim() ? 'hover:bg-[#7EEBD9] active:bg-[#65D9C6]' : ''
              }`}
              style={{
                background: isLoading || !input.trim()
                  ? 'rgba(155, 247, 235, 0.2)'
                  : '#9BF7EB',
              }}
            >
              <svg className={`w-5 h-5 ${isLoading || !input.trim() ? 'text-white/30' : 'text-[#002e34]'}`} fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
              </svg>
            </button>
          </div>
        </div>
      </main>
    </div>
  )
}
