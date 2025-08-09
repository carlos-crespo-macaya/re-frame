'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { useSSEClient } from '@/lib/streaming/use-sse-client'
import ReactMarkdown from 'react-markdown'
import { useEffect as useReactEffect } from 'react'
import { useRecaptcha } from '@/lib/recaptcha/useRecaptcha'
// Chat screen does not display a language selector; language follows route locale

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

  // Prepare reCAPTCHA for chat session
  const siteKey = process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY
  const provider = process.env.NEXT_PUBLIC_RECAPTCHA_PROVIDER === 'enterprise' ? 'enterprise' : 'classic'
  const { ready, execute } = useRecaptcha(siteKey, provider)

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

  // Prefetch a token when chat session starts
  useReactEffect(() => {
    (async () => {
      try {
        if (ready) {
          await execute('chat_start')
        }
      } catch (err) {
        if (process.env.NODE_ENV !== 'production') {
          console.debug('reCAPTCHA chat_start prefetch failed', err)
        }
      }
    })()
  }, [ready, execute])

  // Handle incoming SSE messages
  useEffect(() => {
    const msgs = sseClient.messages || []
    let localBuffer = bufferRef.current
    let didTurnComplete = false

    for (let i = processedIndexRef.current; i < msgs.length; i++) {
      const msg = msgs[i] as { [key: string]: unknown }

      if (msg) {
        const data = msg['data']
        if (msg['message_type'] === 'response' && typeof data === 'string') {
          localBuffer += data
        } else if (msg['type'] === 'content' && typeof data === 'string') {
          localBuffer += data
        } else if (msg['mime_type'] === 'text/plain' && typeof data === 'string') {
          localBuffer += data
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

  // No language selector in chat; language is derived from route


  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return

    const userMessage = { role: 'user' as const, content: input }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    // Reset textarea height
    const textarea = document.querySelector('textarea')
    if (textarea) {
      textarea.style.height = '56px'
    }

    try {
      // Optionally include a recaptcha token on first message
      try {
        if (ready) {
          await execute('chat_message')
        }
      } catch (err) {
        if (process.env.NODE_ENV !== 'production') {
          // best-effort prefetch; ignore failures
          console.debug('reCAPTCHA prefetch failed', err)
        }
      }
      await sseClient.sendText(input)
    } catch (error) {
      console.error('Failed to send message:', error)
      setIsLoading(false)
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value)

    // Auto-resize textarea
    e.target.style.height = '56px'
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
      className="flex flex-col min-h-0 text-white relative overflow-hidden bg-chat-gradient min-h-[100svh]"
    >
      {/* Header */}
      <header className="flex-shrink-0 relative z-10">
        <div className="px-4 py-4 sm:px-16 sm:py-6 pt-[env(safe-area-inset-top)]">
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
            {/* Language selector intentionally removed on chat screen */}
          </div>
        </div>
      </header>

      {/* Main chat area with safe-area padding on mobile */}
      <main className="flex-1 min-h-0 flex flex-col overflow-hidden px-4 sm:px-16 sm:pb-8 pt-4">
        <div className="flex-1 min-h-0 flex flex-col max-w-[1312px] w-full mx-auto">
          {/* Messages container - Enhanced glassmorphic card with visible borders */}
          <div
            className="flex-1 min-h-0 overflow-y-auto rounded-[16px] sm:rounded-[24px] backdrop-blur-md relative ring-1 ring-white/20 shadow-glass bg-card-glass"
          >
            <div className="px-4 sm:px-8 pt-8 pb-6">
              {messages.length === 0 && !isLoading && (
                <div className="flex flex-col items-center justify-center text-center">
                  <p className="text-[18px] font-bold mb-2 text-white">{t.subtitle}</p>
                  <p className="text-[14px] leading-[22px] text-white/45">{t.placeholder}</p>
                </div>
              )}

              <div className="space-y-4">
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[90%] sm:max-w-[75%] break-words ${
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
                    <div className="max-w-[90%] sm:max-w-[75%] break-words bg-[#131e24] text-white/90 ring-1 ring-white/5 rounded-2xl px-5 py-3">
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
                          <div className="w-2 h-2 bg-[#9BF7EB] rounded-full animate-pulse delay-150" />
                          <div className="w-2 h-2 bg-[#9BF7EB] rounded-full animate-pulse delay-300" />
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

          {/* Input dock - sticky on mobile, static on larger screens */}
          <div className="mt-2 sm:mt-4 sticky bottom-0 sm:static z-10 flex items-center h-[56px] rounded-full backdrop-blur-md relative overflow-hidden ring-1 ring-white/20 bg-card-glass shadow-glass pb-[env(safe-area-inset-bottom)]">
            <textarea
              value={input}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              placeholder={t.placeholder}
              className="flex-1 px-4 sm:px-6 bg-transparent text-white text-[14px] leading-[22px] focus:outline-none resize-none overflow-hidden placeholder:text-white/[0.45] h-[56px] py-[17px] placeholder-shown:py-0 placeholder-shown:leading-[56px]"
              rows={1}
              disabled={isLoading}
            />
            <button
              type="button"
              onClick={handleSendMessage}
              disabled={isLoading || !input.trim()}
              aria-label={t.send}
              className={`w-[56px] h-[56px] flex items-center justify-center rounded-full transition-all disabled:opacity-50 disabled:cursor-not-allowed ${
                !isLoading && input.trim() ? 'hover:bg-[#7EEBD9] active:bg-[#65D9C6]' : ''
              }`}
              data-btn-bg={isLoading || !input.trim() ? 'muted' : 'accent'}
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
