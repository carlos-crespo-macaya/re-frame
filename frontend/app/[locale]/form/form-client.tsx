'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { useSSEClient } from '@/lib/streaming/use-sse-client'
import ReactMarkdown from 'react-markdown'
import { FrameworkBadge, LanguageSelector } from '@/components/ui'
import { ThoughtInputForm } from '@/components/forms'
import { Framework } from '@/types/api'

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
    baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
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
    const newPath = `/${newLocale}/form`
    router.push(newPath)
  }


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
    <div className="min-h-screen bg-dark-charcoal text-[#EDEDED]">
      {/* Header */}
      <header className="relative bg-gradient-to-b from-[#1D1F1E] to-transparent">
        <div className="container-safe py-8 px-4 sm:px-6 lg:px-8">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-2xl font-heading font-semibold text-brand-green-400 mb-2">
                re-frame
              </h1>
              <button
                type="button"
                onClick={handleBack}
                className="text-brand-green-400 hover:text-brand-green-300 transition-colors"
              >
                {t.back}
              </button>
            </div>
            <div className="w-48">
              <LanguageSelector 
                value={selectedLanguage}
                onChange={handleLanguageChange}
              />
            </div>
          </div>
        </div>
      </header>


      {/* Main content */}
      <main className="container-safe py-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Input form */}
            <div className="bg-[#2a2a2a] rounded-2xl shadow-lg border border-[#3a3a3a] p-6">
              <h2 className="text-xl font-heading font-medium text-[#EDEDED] mb-6">
                Share Your Thoughts
              </h2>
              <ThoughtInputForm
                onSubmit={handleSubmit}
                onClear={handleClear}
                isLoading={isLoading}
                language={selectedLanguage}
              />
            </div>

            {/* Messages area */}
            <div className="bg-[#2a2a2a] rounded-2xl shadow-lg border border-[#3a3a3a] p-6">
              <h2 className="text-xl font-heading font-medium text-[#EDEDED] mb-6">
                Conversation
              </h2>
              <div className="h-[500px] overflow-y-auto space-y-4">
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[85%] p-4 rounded-lg ${
                        message.role === 'user'
                          ? 'bg-brand-green-600 text-white'
                          : 'bg-[#3a3a3a] text-[#EDEDED]'
                      }`}
                    >
                      {message.role === 'assistant' && message.frameworks && (
                        <div className="flex gap-2 mb-2">
                          {message.frameworks.map((fw, i) => (
                            <FrameworkBadge key={i} framework={fw as Framework} />
                          ))}
                        </div>
                      )}
                      <div className="prose prose-sm prose-invert max-w-none">
                        <ReactMarkdown>{message.content}</ReactMarkdown>
                      </div>
                    </div>
                  </div>
                ))}
                
                {/* Show buffer while streaming */}
                {assistantBuffer && (
                  <div className="flex justify-start">
                    <div className="max-w-[85%] p-4 rounded-lg bg-[#3a3a3a] text-[#EDEDED]">
                      <div className="flex gap-2 mb-2">
                        <FrameworkBadge framework="CBT" />
                      </div>
                      <div className="prose prose-sm prose-invert max-w-none">
                        <ReactMarkdown>{assistantBuffer}</ReactMarkdown>
                      </div>
                    </div>
                  </div>
                )}
                
                {/* Loading indicator */}
                {isLoading && !assistantBuffer && (
                  <div className="flex justify-start">
                    <div className="p-4 rounded-lg bg-[#3a3a3a] text-[#999999]">
                      {t.thinking}
                    </div>
                  </div>
                )}
                
                <div ref={messagesEndRef} />
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}