'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { useSSEClient } from '@/lib/streaming/use-sse-client'
import ReactMarkdown from 'react-markdown'
import { AppLayout } from '@/components/layout/AppLayout'
import { GlassCard } from '@/components/layout/GlassCard'
// UI extras removed to reduce bundle and avoid unused warnings
import { ThoughtInputForm } from '@/components/forms'
// Types are local to this file; avoid importing unused API enums

interface Message {
  role: 'user' | 'assistant'
  content: string
  frameworks?: string[]
}

interface Translations {
  title: string
  subtitle: string
  back: string
  thinking: string
}

export function FormClient({ locale }: { locale: string }) {
  const router = useRouter()
  const pathname = usePathname()
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [assistantBuffer, setAssistantBuffer] = useState('')
  const [selectedLanguage, setSelectedLanguage] = useState(locale === 'es' ? 'es-ES' : 'en-US')
  const processedIndexRef = useRef(0)
  const bufferRef = useRef('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Translations
  const translations: Record<string, Translations> = {
    en: {
      title: 'Form Interface',
      subtitle: 'Share your thoughts with structured input',
      back: '← Back to home',
      thinking: 'Thinking...',
    },
    es: {
      title: 'Interfaz de Formulario',
      subtitle: 'Comparte tus pensamientos con entrada estructurada',
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



  const handleSubmit = async (thought: string) => {
    if (!thought.trim() || isLoading) return

    const userMessage = { role: 'user' as const, content: thought }
    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)

    try {
      await sseClient.sendText(thought)
    } catch (error) {
      console.error('Failed to send message:', error)
      setIsLoading(false)
    }
  }

  const handleClear = () => {
    setMessages([])
    setAssistantBuffer('')
    bufferRef.current = ''
    processedIndexRef.current = 0
  }

  return (
    <AppLayout
      locale={locale}
      showBackButton={true}
      currentLanguage={locale === 'es' ? 'ES' : 'EN'}
      onLanguageChange={(newLocale) => {
        const newPath = pathname.replace(`/${locale}`, `/${newLocale}`)
        router.push(newPath)
      }}
    >
      <div className="max-w-[1312px] mx-auto w-full">
        {/* Page title */}
        <div className="text-center mb-8">
          <h2 className="text-3xl md:text-4xl font-heading font-bold text-white mb-4">
            {t.title}
          </h2>
          <p className="text-lg text-white/70">
            {t.subtitle}
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Input form */}
          <GlassCard>
            <h3 className="text-xl font-heading font-semibold text-white mb-6">
              Share Your Thoughts
            </h3>
            <ThoughtInputForm
              onSubmit={handleSubmit}
              onClear={handleClear}
              isLoading={isLoading}
              language={selectedLanguage}
            />
          </GlassCard>

          {/* Messages area */}
          <GlassCard className="flex flex-col" padding="none">
            <div className="p-8 pb-4">
              <h3 className="text-xl font-heading font-semibold text-white">
                Conversation
              </h3>
            </div>
            <div className="flex-1 px-8 pb-8 overflow-y-auto max-h-[600px]">
              <div className="space-y-4">
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[85%] px-5 py-3 rounded-2xl ${
                        message.role === 'user'
                          ? 'bg-[#074d57] text-white'
                          : 'bg-white/5 text-white'
                      }`}
                    >
                      {message.role === 'assistant' && message.frameworks && (
                        <div className="flex flex-wrap gap-2 mb-3">
                          {message.frameworks.map((fw, i) => (
                            <span key={i} className="text-xs px-3 py-1 bg-white/10 rounded-lg text-[#aefcf5]">
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
                    <div className="max-w-[85%] bg-white/5 text-white rounded-2xl px-5 py-3">
                      <div className="flex flex-wrap gap-2 mb-3">
                        <span className="text-xs px-3 py-1 bg-white/10 rounded-lg text-[#aefcf5]">
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
                    <div className="bg-white/5 text-white rounded-2xl px-5 py-3">
                      <div className="flex items-center gap-3">
                        <div className="flex gap-1">
                          <div className="w-2 h-2 bg-[#aefcf5] rounded-full animate-pulse" />
                          <div className="w-2 h-2 bg-[#aefcf5] rounded-full animate-pulse" style={{ animationDelay: '150ms' }} />
                          <div className="w-2 h-2 bg-[#aefcf5] rounded-full animate-pulse" style={{ animationDelay: '300ms' }} />
                        </div>
                        <span className="text-[14px] leading-[22px]" style={{ color: 'rgba(255, 255, 255, 0.45)' }}>{t.thinking}</span>
                      </div>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>
            </div>
          </GlassCard>
        </div>
      </div>
    </AppLayout>
  )
}
