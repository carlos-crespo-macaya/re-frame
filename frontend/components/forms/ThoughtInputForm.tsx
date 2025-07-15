'use client'

import { useState, FormEvent, KeyboardEvent, useCallback, useEffect, useRef } from 'react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui'
import { createDefaultAudioState, AudioState } from '@/lib/audio'
import { useSSEClient } from '@/lib/streaming/use-sse-client'
import { checkAudioSupport, arrayBufferToBase64 } from '@/lib/audio/audio-utils'
import { usePCMRecorder } from '@/lib/audio/use-pcm-recorder'
import { PCMPlayer } from '@/lib/audio/pcm-player'

interface ThoughtInputFormProps {
  onSubmit: (thought: string) => void
  onClear: () => void
  isLoading?: boolean
  language?: string
}

export default function ThoughtInputForm({ 
  onSubmit, 
  onClear, 
  isLoading = false,
  language = 'en-US'
}: ThoughtInputFormProps) {
  const [thought, setThought] = useState('')
  const [audioState, setAudioState] = useState<AudioState>(createDefaultAudioState())
  const [audioSupported, setAudioSupported] = useState(false)
  const [audioSessionActive, setAudioSessionActive] = useState(false)
  const maxLength = 1000
  const pcmPlayerRef = useRef<PCMPlayer | null>(null)
  
  // Initialize SSE client for audio mode only - ensure only one instance
  const sseClient = useSSEClient({
    baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    autoConnect: false,
    enableRateLimit: false  // Disable rate limiting for audio
  })
  
  // Store refs to avoid dependency issues
  const sseClientRef = useRef(sseClient)
  useEffect(() => {
    sseClientRef.current = sseClient
  }, [sseClient])
  

  // Initialize PCM player and check audio support on mount
  useEffect(() => {
    const support = checkAudioSupport()
    setAudioSupported(support.audioContext && support.audioWorklet && support.getUserMedia)
    
    // Initialize PCM player for audio playback (24kHz for ADK output)
    pcmPlayerRef.current = new PCMPlayer(24000)
    
    return () => {
      if (pcmPlayerRef.current) {
        pcmPlayerRef.current.stop()
      }
    }
  }, [])
  
  
  // Track last processed message index to avoid reprocessing
  const lastProcessedIndexRef = useRef<number>(-1)
  
  
  // Listen for SSE messages - process only new messages
  useEffect(() => {
    if (!sseClient.isConnected || !audioSessionActive) {
      return
    }
    
    const messages = sseClient.messages
    const startIndex = lastProcessedIndexRef.current + 1
    
    // Process only new messages since last check
    for (let i = startIndex; i < messages.length; i++) {
      const msg = messages[i]
      
      // In audio mode, we don't show transcriptions
      // Just handle the audio flow without text interference
      
      // Handle audio playback - play once immediately when received
      if (msg.mime_type === 'audio/pcm' && msg.data && pcmPlayerRef.current) {
        // Play audio asynchronously without blocking
        pcmPlayerRef.current.playPCM(msg.data).catch(err => {
          if (process.env.NODE_ENV === 'development') {
            console.error('Error playing audio:', err)
          }
        })
      }
      
      // Handle turn completion
      if (msg.turn_complete === true && pcmPlayerRef.current) {
        pcmPlayerRef.current.reset()
        setAudioState(prev => ({ ...prev, isProcessing: false }))
      }
    }
    
    // Update last processed index
    if (messages.length > 0) {
      lastProcessedIndexRef.current = messages.length - 1
    }
  }, [sseClient.messages, sseClient.isConnected, audioSessionActive])
  
  
  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (thought.trim() && !isLoading) {
      onSubmit(thought.trim())
      setThought('')
      // Don't disconnect here - keep form clean
    }
  }

  const handleClear = () => {
    setThought('')
    onClear()
    // Reset audio state
    setAudioState(createDefaultAudioState())
    // Cleanup audio session if active
    if (audioSessionActive) {
      pcmRecorder.cleanup()
      sseClient.disconnect()
      setAudioSessionActive(false)
      lastProcessedIndexRef.current = -1
    }
    // Reset PCM player
    if (pcmPlayerRef.current) {
      pcmPlayerRef.current.stop()
      pcmPlayerRef.current = new PCMPlayer(24000)
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter' && thought.trim() && !isLoading) {
      e.preventDefault()
      onSubmit(thought.trim())
      setThought('')
    }
  }

  // Initialize audio recording timer for continuous streaming
  const audioTimerRef = useRef<NodeJS.Timeout | null>(null)
  const audioBufferRef = useRef<Float32Array[]>([])
  const silenceTimerRef = useRef<NodeJS.Timeout | null>(null)
  const lastAudioLevelRef = useRef<number>(0)
  
  // Send audio buffer periodically
  const sendAudioBuffer = useCallback(async () => {
    if (audioBufferRef.current.length === 0 || !sseClient.isConnected) {
      return
    }
    
    // Merge all audio chunks
    const totalLength = audioBufferRef.current.reduce((acc, chunk) => acc + chunk.length, 0)
    const mergedAudio = new Float32Array(totalLength)
    let offset = 0
    
    for (const chunk of audioBufferRef.current) {
      mergedAudio.set(chunk, offset)
      offset += chunk.length
    }
    
    // Calculate audio level for silence detection
    const audioLevel = Math.sqrt(
      mergedAudio.reduce((sum, sample) => sum + sample * sample, 0) / mergedAudio.length
    )
    lastAudioLevelRef.current = audioLevel
    
    // Convert Float32 to Int16
    const int16Data = new Int16Array(mergedAudio.length)
    for (let i = 0; i < mergedAudio.length; i++) {
      const s = Math.max(-1, Math.min(1, mergedAudio[i]))
      int16Data[i] = s < 0 ? s * 0x8000 : s * 0x7FFF
    }
    
    // Convert to base64
    const bytes = new Uint8Array(int16Data.buffer)
    const base64Audio = arrayBufferToBase64(bytes.buffer)
    
    // Send audio without turn_complete
    if (process.env.NODE_ENV === 'development') {
      console.log(`Sending audio chunk: ${base64Audio.length} bytes, level: ${audioLevel.toFixed(3)}`)
    }
    await sseClient.sendAudio(base64Audio, false)
    
    // Clear buffer
    audioBufferRef.current = []
    
    // Reset silence timer if we have audio
    if (audioLevel > 0.01) { // Threshold for silence
      if (silenceTimerRef.current) {
        clearTimeout(silenceTimerRef.current)
      }
      // Start new silence timer - if no audio for 1.5 seconds, send turn_complete
      silenceTimerRef.current = setTimeout(async () => {
        if (sseClient.isConnected) {
          if (process.env.NODE_ENV === 'development') {
            console.log('Silence detected, sending turn_complete')
          }
          await sseClient.sendMessage('', 'text/plain', {
            messageType: 'thought',
            turnComplete: true
          })
        }
      }, 1500)
    } else {
      if (process.env.NODE_ENV === 'development') {
        console.log('Audio level below threshold:', audioLevel)
      }
    }
  }, [sseClient])
  
  // Modified PCM recorder with continuous streaming
  const pcmRecorder = usePCMRecorder({
    sampleRate: 16000,
    onDataAvailable: (pcmData) => {
      // Add to buffer for periodic sending
      audioBufferRef.current.push(pcmData)
    },
    onError: (error) => {
      setAudioState(prev => ({
        ...prev,
        error: error,
        isProcessing: false,
        isRecording: false
      }))
    }
  })
  
  const pcmRecorderRef = useRef(pcmRecorder)
  useEffect(() => {
    pcmRecorderRef.current = pcmRecorder
  }, [pcmRecorder])
  
  // Clean up audio session on unmount
  useEffect(() => {
    const cleanupOnUnmount = () => {
      if (pcmRecorderRef.current) {
        pcmRecorderRef.current.cleanup()
      }
      if (sseClientRef.current && sseClientRef.current.isConnected) {
        sseClientRef.current.disconnect()
      }
    }
    
    return cleanupOnUnmount
  }, [])
  
  // Audio handlers
  const handleStartRecording = useCallback(async () => {
    try {
      // Check if already connected
      if (sseClient.isConnected) {
        if (process.env.NODE_ENV === 'development') {
          console.warn('SSE already connected, disconnecting first')
        }
        sseClient.disconnect()
        await new Promise(resolve => setTimeout(resolve, 100))
      }
      
      setAudioState(prev => ({ ...prev, error: null, audioEnabled: true }))
      
      // Connect to SSE for streaming with selected language and audio mode
      await sseClient.connect(undefined, language, true)
      setAudioSessionActive(true)
      lastProcessedIndexRef.current = -1  // Reset message tracking
      
      // Start recording - this will request browser microphone permission if needed
      await pcmRecorder.startRecording()
      
      // Start periodic audio sending (every 200ms)
      audioTimerRef.current = setInterval(sendAudioBuffer, 200)
      
      // If we get here, permission was granted and recording started
      setAudioState(prev => ({ 
        ...prev, 
        micPermission: 'granted',
        isRecording: true
      }))
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Failed to start recording:', error)
      }
      // Check if it's a permission error
      if (error instanceof Error && error.name === 'NotAllowedError') {
        setAudioState(prev => ({ ...prev, micPermission: 'denied', error: error as Error }))
      } else {
        setAudioState(prev => ({ ...prev, error: error as Error }))
      }
      // Clean up on error
      sseClient.disconnect()
      setAudioSessionActive(false)
    }
  }, [pcmRecorder, sseClient, language, sendAudioBuffer])

  const handleStopRecording = useCallback(async () => {
    try {
      setAudioState(prev => ({ ...prev, isProcessing: false, isRecording: false }))
      
      // Stop the audio timer
      if (audioTimerRef.current) {
        clearInterval(audioTimerRef.current)
        audioTimerRef.current = null
      }
      
      // Stop the silence timer
      if (silenceTimerRef.current) {
        clearTimeout(silenceTimerRef.current)
        silenceTimerRef.current = null
      }
      
      // Send any remaining audio with turn_complete
      await sendAudioBuffer()
      
      // Send final turn_complete to ensure we get a response
      if (sseClient.isConnected) {
        await sseClient.sendMessage('', 'text/plain', {
          messageType: 'thought',
          turnComplete: true
        })
      }
      
      // Stop recording
      await pcmRecorder.stopRecording()
      
      // Disconnect SSE after a short delay to allow final responses
      setTimeout(() => {
        sseClient.disconnect()
        setAudioSessionActive(false)
        lastProcessedIndexRef.current = -1
      }, 2000)
      
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Failed to stop recording:', error)
      }
      setAudioState(prev => ({ ...prev, isProcessing: false, isRecording: false }))
    }
  }, [pcmRecorder, sseClient, sendAudioBuffer])


  const isSubmitDisabled = !thought.trim() || isLoading

  // Status messages based on input length
  const getStatusMessage = () => {
    if (thought.length === 0) return ""
    if (thought.length < 50) return "Continue if you'd like to add more context."
    if (thought.length < 200) return "Good amount of detail."
    if (thought.length < 500) return "Comprehensive description."
    return "Maximum detail captured."
  }

  return (
    <form onSubmit={handleSubmit} className="w-full space-y-6">
      <div className="space-y-3">
        <div className="relative">
          {!audioState.isRecording ? (
            <textarea
              id="thought-input"
              value={thought}
              onChange={(e) => setThought(e.target.value.slice(0, maxLength))}
              onKeyDown={handleKeyDown}
              placeholder="What happened? How did it feel?"
              className={cn(
                "w-full min-h-[140px] resize-y rounded-xl",
                "bg-white",
                "border-2 border-neutral-200",
                "focus:border-primary-400",
                "focus:ring-4 focus:ring-primary-400/20",
                "px-5 py-4 pr-16", // Added right padding for audio button
                "text-base text-neutral-800",
                "placeholder:text-neutral-400",
                "transition-all duration-200",
                isLoading && "opacity-60 cursor-not-allowed"
              )}
              disabled={isLoading}
              maxLength={maxLength}
              aria-describedby="character-count encouraging-message"
              required
            />
          ) : (
            <div className={cn(
              "w-full min-h-[140px] rounded-xl",
              "bg-neutral-50",
              "border-2 border-primary-400",
              "px-5 py-4",
              "flex items-center justify-center",
              "transition-all duration-200"
            )}>
              <div className="text-center">
                <div className="flex justify-center mb-2">
                  <span className="inline-block w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                </div>
                <p className="text-neutral-600">Audio conversation active</p>
                <p className="text-sm text-neutral-500 mt-1">Click the mic to stop</p>
              </div>
            </div>
          )}
          
          
          {/* Decorative element */}
          <div className="absolute -bottom-2 -right-2 w-16 h-16 bg-gradient-to-br from-primary-200/30 to-secondary-200/30 rounded-full blur-xl pointer-events-none" />
        </div>
        
        {!audioState.isRecording && (
          <div className="flex justify-between items-end">
            <p 
              id="encouraging-message"
              className="text-sm text-neutral-600 italic"
              aria-live="polite"
            >
              {getStatusMessage()}
            </p>
            <div 
              id="character-count" 
              className="text-sm text-neutral-500"
              aria-live="polite"
            >
              {thought.length} / {maxLength}
            </div>
          </div>
        )}
      </div>

      {!audioState.isRecording && (
        <div className="flex flex-col sm:flex-row gap-3 sm:gap-6 items-center justify-center">
          <Button
            type="submit"
            disabled={isSubmitDisabled}
            loading={isLoading}
            variant="primary"
            size="large"
            className="w-full sm:w-auto group relative overflow-hidden"
          >
            {isLoading ? (
                <span>Processing...</span>
              ) : (
                <span>Generate perspective</span>
              )}
          </Button>
          <Button
            type="button"
            onClick={handleClear}
            disabled={isLoading}
            variant="secondary"
            size="large"
            className="w-full sm:w-auto group"
          >
            <span className="flex items-center gap-2">
              <span className="group-hover:rotate-180 transition-transform duration-300">
                ↻
              </span>
              <span>Clear</span>
            </span>
          </Button>
        </div>
      )}

      {isLoading && (
        <div 
          className="text-center space-y-2"
          role="status"
          aria-live="polite"
        >
          <div className="flex justify-center gap-2">
            <span className="inline-block w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
            <span className="inline-block w-2 h-2 bg-secondary-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
            <span className="inline-block w-2 h-2 bg-accent-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
          <p className="text-sm text-neutral-600">
            Analyzing your input...
          </p>
        </div>
      )}

      {/* Tip for keyboard shortcut */}
      <p className="text-xs text-neutral-500 text-center">
        <kbd className="px-2 py-1 bg-neutral-100 rounded text-xs">Ctrl</kbd> + 
        <kbd className="px-2 py-1 bg-neutral-100 rounded text-xs ml-1">Enter</kbd>
        <span className="ml-2">to submit</span>
      </p>
    </form>
  )
}