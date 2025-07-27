'use client'

import { useState, useEffect, useRef, useMemo } from 'react'
import Link from 'next/link'
import ThoughtInputForm from '@/components/forms/ThoughtInputForm'
import { FrameworkBadge, LanguageSelector } from '@/components/ui'
import { ReframeResponse, Framework } from '@/types/api'
import { useSSEClient } from '@/lib/streaming/use-sse-client'
import ReactMarkdown from 'react-markdown'
import { NaturalConversation } from '@/components/audio/NaturalConversation'
import { appLogger } from '@/lib/logger'

export default function Home() {
  const [isLoading, setIsLoading] = useState(false)
  const [responses, setResponses] = useState<ReframeResponse[]>([])
  const [selectedLanguage, setSelectedLanguage] = useState('en-US')
  const [useAudioMode, setUseAudioMode] = useState(false)
  const [isConnecting, setIsConnecting] = useState(false)
  const hasConnectedRef = useRef(false)
  const previousLanguageRef = useRef(selectedLanguage)
  const previousAudioModeRef = useRef(useAudioMode)
  const connectionAttemptRef = useRef<number>(0)
  
  // Memoize SSE client options to prevent recreating the client on every render
  const sseOptions = useMemo(() => ({
    baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    autoConnect: false,
  }), [])
  
  // Initialize SSE client (text mode only)
  const sseClient = useSSEClient(sseOptions)
  
  // Extract specific values to avoid object identity issues in useEffect
  const { isConnected, messages, connect, disconnect, sendText, error } = sseClient
  
  
  // Connect on mount and when language/mode changes
  useEffect(() => {
    let mounted = true
    const currentAttempt = ++connectionAttemptRef.current
    
    // Debounce connection attempts in development to handle React StrictMode
    const debounceDelay = process.env.NODE_ENV === 'development' ? 100 : 0
    
    const performConnect = async () => {
      try {
        if (mounted && !useAudioMode) {
          // Only reconnect if language changed or first connection
          const shouldConnect = !hasConnectedRef.current || 
                               previousLanguageRef.current !== selectedLanguage ||
                               previousAudioModeRef.current !== useAudioMode
          
          if (shouldConnect) {
            setIsConnecting(true)
            appLogger.info('Connection attempt', {
              attempt: currentAttempt,
              language: selectedLanguage,
              audioMode: useAudioMode,
              shouldConnect
            })
            
            // Only proceed if this is still the latest connection attempt
            if (currentAttempt === connectionAttemptRef.current && mounted) {
              appLogger.info('Connecting with settings', {
                language: selectedLanguage,
                audioMode: false
              })
              await connect(undefined, selectedLanguage, false)
              hasConnectedRef.current = true
              previousLanguageRef.current = selectedLanguage
              previousAudioModeRef.current = useAudioMode
              appLogger.info('Connection successful')
            }
            
            setIsConnecting(false)
          }
        }
      } catch (error) {
        appLogger.error('Failed to connect', {
          attempt: currentAttempt,
          language: selectedLanguage
        }, error as Error)
        setIsConnecting(false)
        
        // Retry connection after delay if still mounted
        if (mounted && currentAttempt === connectionAttemptRef.current) {
          setTimeout(() => {
            if (mounted && !useAudioMode) {
              performConnect()
            }
          }, 2000)
        }
      }
    }
    
    // Handle mode switching with debounce
    if (!useAudioMode) {
      if (debounceDelay > 0) {
        const timer = setTimeout(() => {
          if (mounted) performConnect()
        }, debounceDelay)
        return () => clearTimeout(timer)
      } else {
        performConnect()
      }
    } else if (useAudioMode) {
      // Disconnect text mode when switching to audio
      appLogger.info('Disconnecting text mode for audio mode switch')
      disconnect()
      hasConnectedRef.current = false
      previousAudioModeRef.current = useAudioMode
    }
    
    return () => {
      mounted = false
      // Always try to disconnect on unmount
      disconnect()
    }
  }, [selectedLanguage, useAudioMode, connect, disconnect])
  
  // Track the start of current response
  const [responseStartIndex, setResponseStartIndex] = useState(0)
  
  // Get the latest response from messages
  const latestResponse = useMemo(() => {
    if (!isConnected || messages.length === 0) return null
    
    // Only process messages from the current response
    const currentMessages = messages.slice(responseStartIndex)
    
    // Debug logging for messages
    if (currentMessages.length > 0 && process.env.NODE_ENV === 'development') {
      console.log('Current messages:', currentMessages.map(msg => ({
        mime_type: msg.mime_type,
        has_data: !!msg.data,
        turn_complete: msg.turn_complete,
        interrupted: msg.interrupted
      })))
    }
    
    const textMessages = currentMessages.filter(msg => 
      msg.mime_type === 'text/plain' && msg.data
    )
    
    // Check for turn completion in current messages
    const turnComplete = currentMessages.some(msg => msg.turn_complete === true)
    
    if (process.env.NODE_ENV === 'development' && turnComplete) {
      console.log('🎯 Turn complete found in messages!')
    }
    
    if (textMessages.length > 0 || turnComplete) {
      // Combine text messages from current response only
      const fullResponse = textMessages.map(msg => msg.data).join('')
      
      return {
        success: true,
        response: fullResponse,
        frameworks_used: ['CBT'],
        transparency: {
          agents_used: ['cbt_assistant'],
          techniques_applied: ['Cognitive restructuring'],
          framework_details: {
            CBT: {
              techniques: ['Cognitive restructuring'],
              confidence: 0.85,
              patterns_addressed: []
            }
          },
          selection_rationale: 'CBT framework applied based on the thought pattern.'
        },
        turnComplete
      }
    }
    
    return null
  }, [messages, responseStartIndex, isConnected])
  
  // Update response state when latest response changes
  useEffect(() => {
    if (latestResponse) {
      console.log('Latest response:', latestResponse);
      // Append new response to the array (idempotent to handle StrictMode)
      setResponses(prev => {
        // Check if this exact response already exists (handles StrictMode double-render)
        const isDuplicate = prev.some(r => 
          r.response === latestResponse.response && 
          r.frameworks_used.join(',') === latestResponse.frameworks_used.join(',')
        );
        
        if (!isDuplicate) {
          return [...prev, latestResponse];
        }
        return prev;
      })
      
      // Clear loading state when turn is complete
      if (latestResponse.turnComplete) {
        console.log('🚀 Turn complete detected, clearing loading state');
        setIsLoading(false)
      }
    }
  }, [latestResponse])

  const handleSubmit = async (thought: string) => {
    setIsLoading(true)
    // Don't clear responses - we want to maintain conversation history
    
    // Mark where the new response will start
    setResponseStartIndex(messages.length)
    
    try {
      // Send text message to backend
      await sendText(thought)
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Failed to send message:', error)
      }
      setIsLoading(false)
    }
  }

  const handleClear = () => {
    setResponses([])
  }

  return (
    <>
      {/* Header */}
      <header className="relative bg-gradient-to-b from-[#1D1F1E] to-transparent">
        <div className="container-safe py-8">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-2xl font-heading font-semibold text-brand-green-400">
                re-frame
              </h1>
              <p className="text-sm text-[#999999] mt-1">
                Cognitive reframing support
              </p>
            </div>
            <div className="w-48">
              <LanguageSelector 
                value={selectedLanguage}
                onChange={setSelectedLanguage}
              />
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main id="main-content" className="flex-1">
        <div className="container-safe py-8 md:py-12">
          {/* Welcome section with warm messaging */}
          <section className="max-w-3xl mx-auto text-center mb-12 animate-fade-in">
            <h2 className="text-3xl md:text-4xl font-heading font-medium text-[#EDEDED] mb-6">
              Explore a new perspective
            </h2>
            <p className="text-lg text-[#999999] mb-4 leading-relaxed">
              We&apos;ll use evidence-based therapeutic techniques to spot thinking patterns and suggest gentler perspectives.
            </p>
            <p className="text-[#999999] max-w-2xl mx-auto">
              <span className="text-sm">Learn about <a href="/learn-cbt" className="text-brand-green-400 underline hover:text-brand-green-300">therapeutic frameworks in 2 minutes ↗</a></span>
            </p>
          </section>

          {/* Form section with organic card shape */}
          <section className="max-w-2xl mx-auto">
            <div className="relative">
              
              <div className="relative bg-[#F7F4F2] rounded-2xl shadow-lg border border-[#2a2a2a] p-8 md:p-10" data-testid="conversation-interface" style={{ 
                boxShadow: '0 4px 24px rgba(0, 0, 0, 0.1)',
                animation: 'fadeIn 250ms cubic-bezier(0.25, 0.1, 0.25, 1)'
              }}>
                <div className="flex justify-between items-start mb-6">
                  <div>
                    <h3 className="text-xl font-heading font-medium text-neutral-800 mb-2">
                      Tell us about the situation
                    </h3>
                    <p className="text-sm text-neutral-600">
                      A few sentences are enough — share what feels right.
                    </p>
                  </div>
                  <button
                    onClick={() => setUseAudioMode(!useAudioMode)}
                    className="flex items-center gap-2 px-3 py-1.5 text-sm text-neutral-800 rounded-full bg-neutral-200 hover:bg-neutral-300 transition-colors"
                  >
                    {useAudioMode ? (
                      <>
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                        </svg>
                        Switch to Text
                      </>
                    ) : (
                      <>
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                        </svg>
                        Switch to Voice
                      </>
                    )}
                  </button>
                </div>
              
              {useAudioMode ? (
                <NaturalConversation language={selectedLanguage} />
              ) : (
                <>
                  {/* Connection status for debugging */}
                  {process.env.NODE_ENV === 'development' && (
                    <div className="mb-4 text-xs text-neutral-500 flex items-center gap-2">
                      <span className={`inline-block w-2 h-2 rounded-full ${
                        isConnecting ? 'bg-yellow-500 animate-pulse' : 
                        isConnected ? 'bg-green-500' : 
                        'bg-red-500'
                      }`} />
                      <span>
                        {isConnecting ? 'Connecting...' : 
                         isConnected ? 'Connected' : 
                         `Disconnected${error ? ` - ${error.message}` : ''}`}
                      </span>
                    </div>
                  )}
                  <ThoughtInputForm 
                    onSubmit={handleSubmit}
                    onClear={handleClear}
                    isLoading={isLoading}
                    language={selectedLanguage}
                  />
                </>
              )}

                {responses.length > 0 && !useAudioMode && (
                  <div className="mt-8 space-y-4">
                    {responses.map((response, index) => (
                      <div key={index} className="p-6 bg-[#2a2a2a] border border-[#3a3a3a] rounded-xl animate-fade-in">
                        {/* Framework badges */}
                        {response.frameworks_used.length > 0 && (
                          <div className="flex gap-2 mb-4">
                            {response.frameworks_used.map(fw => (
                              <FrameworkBadge key={fw} framework={fw as Framework} />
                            ))}
                          </div>
                        )}
                        
                        {/* Main response with markdown */}
                        <div className="text-sm text-[#EDEDED] leading-relaxed prose prose-sm prose-invert max-w-none" data-testid="message-content">
                          <ReactMarkdown
                            components={{
                              p: ({children}) => <p className="mb-4">{children}</p>,
                              ul: ({children}) => <ul className="list-disc list-inside mb-4 space-y-2">{children}</ul>,
                              li: ({children}) => <li className="ml-4">{children}</li>,
                              strong: ({children}) => <strong className="font-semibold text-[#FFFFFF]">{children}</strong>,
                            }}
                          >
                            {response.response}
                          </ReactMarkdown>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                <p className="mt-6 text-sm text-neutral-500 text-center">
                  Private session — we don&apos;t store personal data.
                </p>
              </div>
            </div>
          </section>

          {/* How it works section with gentle illustrations */}
          <section className="max-w-3xl mx-auto mt-16 space-y-12">
            <div className="text-center">
              <h3 className="text-2xl font-heading font-medium text-[#EDEDED] mb-12">
                How re-frame works
              </h3>
              <div className="grid md:grid-cols-3 gap-8 mt-6">
                {/* Step 1 */}
                <div className="group">
                  <div className="mb-6">
                    <div className="w-16 h-16 mx-auto bg-brand-green-600 rounded-full flex items-center justify-center">
                      <span className="text-white font-semibold">1</span>
                    </div>
                  </div>
                  <h4 className="font-heading font-medium text-base text-[#EDEDED] mb-3">
                    Tell us what happened
                  </h4>
                  <p className="text-base text-[#999999] leading-relaxed">
                    Use your own words. Take the time you need.
                  </p>
                </div>

                {/* Step 2 */}
                <div className="group">
                  <div className="mb-6">
                    <div className="w-16 h-16 mx-auto bg-brand-green-600 rounded-full flex items-center justify-center">
                      <span className="text-white font-semibold">2</span>
                    </div>
                  </div>
                  <h4 className="font-heading font-medium text-base text-[#EDEDED] mb-3">
                    Notice thinking patterns
                  </h4>
                  <p className="text-base text-[#999999] leading-relaxed">
                    We&apos;ll apply therapeutic frameworks to highlight alternative perspectives.
                  </p>
                </div>

                {/* Step 3 */}
                <div className="group">
                  <div className="mb-6">
                    <div className="w-16 h-16 mx-auto bg-brand-green-600 rounded-full flex items-center justify-center">
                      <span className="text-white font-semibold">3</span>
                    </div>
                  </div>
                  <h4 className="font-heading font-medium text-base text-[#EDEDED] mb-3">
                    Pick a perspective that feels true
                  </h4>
                  <p className="text-base text-[#999999] leading-relaxed">
                    Select from alternative ways to view your situation.
                  </p>
                </div>
              </div>
            </div>

            {/* Trust message */}
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-warm-sand/10 via-soft-sky/10 to-breathing-mint/10 rounded-2xl blur-2xl" />
              <div className="relative border-t border-b border-[#3a3a3a] py-8">
                <p className="text-center text-[#999999] max-w-2xl mx-auto leading-relaxed">
                  <span className="block text-lg font-heading font-medium text-brand-green-400 mb-3">
                    Designed for people living with AvPD & social anxiety
                  </span>
                  This tool uses evidence-based therapeutic techniques. Your privacy is protected - 
                  we don&apos;t store any personal information.
                </p>
              </div>
            </div>
          </section>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-auto border-t border-[#3a3a3a]">
        <div className="container-safe py-8">
          <div className="flex flex-col items-center gap-4">
            <h2 className="text-xl font-heading font-semibold text-brand-green-400">
              re-frame
            </h2>
            <nav aria-label="Footer navigation">
              <ul className="flex gap-6 text-sm">
                <li>
                  <Link 
                    href="/privacy" 
                    className="text-[#999999] hover:text-brand-green-400 transition-colors"
                  >
                    Privacy
                  </Link>
                </li>
                <li>
                  <Link 
                    href="/support" 
                    className="text-[#999999] hover:text-brand-green-400 transition-colors"
                  >
                    Support
                  </Link>
                </li>
                <li>
                  <Link 
                    href="/about" 
                    className="text-[#999999] hover:text-brand-green-400 transition-colors"
                  >
                    About
                  </Link>
                </li>
              </ul>
            </nav>
            <p className="text-xs text-[#999999]">
              © 2024 re-frame.social
            </p>
          </div>
        </div>
      </footer>
    </>
  );
}
