'use client'

import { useState, FormEvent, KeyboardEvent, useCallback, useEffect, useRef } from 'react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui'
import { AudioControls } from './AudioControls'
import { createDefaultAudioState, AudioMode, AudioState, useAudioRecorder } from '@/lib/audio'
import { useSSEClient } from '@/lib/streaming/use-sse-client'
import { checkAudioSupport, arrayBufferToBase64, float32ToPcm16 } from '@/lib/audio/audio-utils'

interface ThoughtInputFormProps {
  onSubmit: (thought: string) => void
  onClear: () => void
  isLoading?: boolean
}

export default function ThoughtInputForm({ 
  onSubmit, 
  onClear, 
  isLoading = false 
}: ThoughtInputFormProps) {
  const [thought, setThought] = useState('')
  const [audioState, setAudioState] = useState<AudioState>(createDefaultAudioState())
  const [audioSupported, setAudioSupported] = useState(false)
  const maxLength = 1000
  const audioBufferRef = useRef<Float32Array[]>([])
  const bufferTimeoutRef = useRef<NodeJS.Timeout>()
  
  // Initialize SSE client
  const sseClient = useSSEClient({
    baseUrl: process.env.NEXT_PUBLIC_API_URL || '/api/sse',
    autoConnect: false,
    enableRateLimit: true,
    rateLimitMs: 100
  })
  
  // Initialize audio recorder
  const audioRecorder = useAudioRecorder({
    onTranscription: (text) => {
      setAudioState(prev => ({
        ...prev,
        transcription: text,
        isProcessing: false
      }))
    },
    onError: (error) => {
      setAudioState(prev => ({
        ...prev,
        error: error,
        isProcessing: false,
        isRecording: false
      }))
    },
    onDataAvailable: (audioData) => {
      // Buffer audio data
      audioBufferRef.current.push(audioData)
      
      // Clear existing timeout
      if (bufferTimeoutRef.current) {
        clearTimeout(bufferTimeoutRef.current)
      }
      
      // Set new timeout to send buffered data after 200ms
      bufferTimeoutRef.current = setTimeout(() => {
        sendBufferedAudio()
      }, 200)
    }
  })

  // Check audio support on mount
  useEffect(() => {
    const support = checkAudioSupport()
    setAudioSupported(support.audioContext && support.audioWorklet && support.getUserMedia)
  }, [])
  
  // Listen for SSE messages
  useEffect(() => {
    if (sseClient.isConnected) {
      const transcriptionMessages = sseClient.getMessagesByType('transcription')
      const latestTranscription = transcriptionMessages[transcriptionMessages.length - 1]
      
      if (latestTranscription) {
        setAudioState(prev => ({
          ...prev,
          transcription: latestTranscription.data,
          isProcessing: false
        }))
      }
    }
  }, [sseClient.messages, sseClient.isConnected])
  
  // Send buffered audio data
  const sendBufferedAudio = useCallback(async () => {
    if (audioBufferRef.current.length === 0 || !sseClient.isConnected) return
    
    try {
      // Merge all audio chunks
      const totalLength = audioBufferRef.current.reduce((acc, chunk) => acc + chunk.length, 0)
      const mergedAudio = new Float32Array(totalLength)
      let offset = 0
      
      for (const chunk of audioBufferRef.current) {
        mergedAudio.set(chunk, offset)
        offset += chunk.length
      }
      
      // Convert to 16-bit PCM and base64
      const pcm16 = float32ToPcm16(mergedAudio)
      const arrayBuffer = pcm16.buffer.slice(pcm16.byteOffset, pcm16.byteOffset + pcm16.byteLength) as ArrayBuffer
      const base64Audio = arrayBufferToBase64(arrayBuffer)
      
      // Send via SSE
      await sseClient.sendAudio(base64Audio, false)
      
      // Clear buffer
      audioBufferRef.current = []
    } catch (error) {
      console.error('Failed to send audio buffer:', error)
    }
  }, [sseClient])
  
  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (thought.trim() && !isLoading) {
      onSubmit(thought.trim())
      setThought('')
      // Reset audio state and cleanup recorder after submission
      setAudioState(createDefaultAudioState())
      audioRecorder.cleanup()
      sseClient.disconnect()
    }
  }

  const handleClear = () => {
    setThought('')
    onClear()
    // Reset audio state and cleanup recorder
    setAudioState(createDefaultAudioState())
    audioRecorder.cleanup()
    sseClient.disconnect()
    audioBufferRef.current = []
    if (bufferTimeoutRef.current) {
      clearTimeout(bufferTimeoutRef.current)
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter' && thought.trim() && !isLoading) {
      e.preventDefault()
      onSubmit(thought.trim())
      setThought('')
    }
  }

  // Update audio state from recorder
  useEffect(() => {
    setAudioState(prev => ({
      ...prev,
      isRecording: audioRecorder.isRecording,
      isProcessing: audioRecorder.isProcessing,
      micPermission: audioRecorder.micPermission,
      error: audioRecorder.error,
      audioLevel: audioRecorder.isGateOpen ? 0.7 : 0.1 // Simulate audio level
    }))
  }, [
    audioRecorder.isRecording,
    audioRecorder.isProcessing,
    audioRecorder.micPermission,
    audioRecorder.error,
    audioRecorder.isGateOpen
  ])
  
  // Audio handlers
  const handleStartRecording = useCallback(async () => {
    try {
      setAudioState(prev => ({ ...prev, error: null, audioEnabled: true }))
      
      // Connect to SSE for streaming
      await sseClient.connect()
      
      await audioRecorder.startRecording()
    } catch (error) {
      console.error('Failed to start recording:', error)
      setAudioState(prev => ({ ...prev, error: error as Error }))
    }
  }, [audioRecorder, sseClient])

  const handleStopRecording = useCallback(async () => {
    try {
      setAudioState(prev => ({ ...prev, isProcessing: true }))
      
      // Send any remaining buffered audio
      if (audioBufferRef.current.length > 0) {
        await sendBufferedAudio()
      }
      
      await audioRecorder.stopRecording()
      
      // In instant mode, auto-submit after recording
      if (audioState.mode === 'instant' && audioState.transcription) {
        onSubmit(audioState.transcription)
        setThought('')
        setAudioState(createDefaultAudioState())
        sseClient.disconnect()
      }
    } catch (error) {
      console.error('Failed to stop recording:', error)
    }
  }, [audioRecorder, audioState.mode, audioState.transcription, onSubmit, sendBufferedAudio, sseClient])

  const handleModeChange = useCallback((mode: AudioMode) => {
    setAudioState(prev => ({
      ...prev,
      mode
    }))
  }, [])

  const handleTranscriptionEdit = useCallback((text: string) => {
    setAudioState(prev => ({
      ...prev,
      transcription: text
    }))
    setThought(text)
  }, [])

  const handleTranscriptionAccept = useCallback(() => {
    setThought(audioState.transcription)
    setAudioState(prev => ({
      ...prev,
      transcription: ''
    }))
  }, [audioState.transcription])

  const handleReRecord = useCallback(() => {
    setAudioState(prev => ({
      ...prev,
      transcription: ''
    }))
    handleStartRecording()
  }, [handleStartRecording])

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
          
          {/* Audio Controls - positioned inside textarea */}
          {audioSupported && audioState.micPermission !== 'denied' && (
            <div data-testid="audio-controls">
              <AudioControls
                audioState={audioState}
                onStartRecording={handleStartRecording}
                onStopRecording={handleStopRecording}
                onModeChange={handleModeChange}
                onTranscriptionEdit={handleTranscriptionEdit}
                onTranscriptionAccept={handleTranscriptionAccept}
                onReRecord={handleReRecord}
                onPermissionDenied={() => {
                  setAudioState(prev => ({ ...prev, micPermission: 'denied', audioEnabled: false }))
                  setAudioSupported(false)
                }}
                disabled={isLoading}
                className="audio-controls--in-textarea"
              />
            </div>
          )}
          
          {/* Decorative element */}
          <div className="absolute -bottom-2 -right-2 w-16 h-16 bg-gradient-to-br from-primary-200/30 to-secondary-200/30 rounded-full blur-xl pointer-events-none" />
        </div>
        
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
      </div>

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