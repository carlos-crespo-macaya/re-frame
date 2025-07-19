import { useState, useRef, useCallback, useEffect } from 'react'
import { PCMPlayer } from './pcm-player'
import { arrayBufferToBase64 } from './audio-utils'
import { ApiClient, logApiError, EventSourceParams } from '../api'
import { generateAudioSessionId } from '../utils/session'
import { createClientMessage } from '../streaming/message-protocol'

// Audio configuration - aligned with backend expectation
const AUDIO_SAMPLE_RATE = 16000

export interface UseNaturalConversationOptions {
  language?: string
  onTranscription?: (text: string) => void
  onError?: (error: Error) => void
}

export interface NaturalConversationState {
  isActive: boolean
  status: string
  error: Error | null
}

export function useNaturalConversation(options: UseNaturalConversationOptions = {}) {
  const {
    language = 'en-US',
    onTranscription,
    onError
  } = options

  const [state, setState] = useState<NaturalConversationState>({
    isActive: false,
    status: 'Click to start conversation',
    error: null
  })

  // Refs for audio components
  const audioContextRef = useRef<AudioContext | null>(null)
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null)
  const workletNodeRef = useRef<AudioWorkletNode | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const pcmPlayerRef = useRef<PCMPlayer | null>(null)
  const eventSourceRef = useRef<EventSource | null>(null)
  const sessionIdRef = useRef<string | null>(null)

  // Audio buffering for 0.2s intervals
  const audioBufferRef = useRef<Uint8Array[]>([])
  const bufferTimerRef = useRef<NodeJS.Timeout | null>(null)
  const silenceTimerRef = useRef<NodeJS.Timeout | null>(null)
  const lastAudioLevelRef = useRef<number>(0)

  // Initialize PCM player on mount
  useEffect(() => {
    pcmPlayerRef.current = new PCMPlayer(AUDIO_SAMPLE_RATE)

    return () => {
      if (pcmPlayerRef.current) {
        pcmPlayerRef.current.stop()
      }
    }
  }, [])

  // Cleanup will be defined later, so we don't include it in deps
  useEffect(() => {
    return () => {
      // Clean up timers
      if (bufferTimerRef.current) {
        clearInterval(bufferTimerRef.current)
        bufferTimerRef.current = null
      }
      if (silenceTimerRef.current) {
        clearTimeout(silenceTimerRef.current)
        silenceTimerRef.current = null
      }

      // Clean up audio resources
      if (workletNodeRef.current) {
        workletNodeRef.current.disconnect()
        workletNodeRef.current = null
      }
      if (sourceRef.current) {
        sourceRef.current.disconnect()
        sourceRef.current = null
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop())
        streamRef.current = null
      }
      if (audioContextRef.current) {
        audioContextRef.current.close()
        audioContextRef.current = null
      }

      // Clean up SSE connection
      if (eventSourceRef.current) {
        eventSourceRef.current.close()
        eventSourceRef.current = null
      }

      // Clear audio buffer
      audioBufferRef.current = []
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Convert Float32 samples to 16-bit PCM
  const convertFloat32ToPCM = (inputData: Float32Array): ArrayBuffer => {
    const pcm16 = new Int16Array(inputData.length)
    for (let i = 0; i < inputData.length; i++) {
      // Multiply by 0x7fff (32767) to scale the float value to 16-bit PCM range
      pcm16[i] = inputData[i] * 0x7fff
    }
    return pcm16.buffer
  }

  // Helper function to send audio messages
  const sendAudioMessage = useCallback(async (
    data: string,
    turnComplete: boolean = false
  ) => {
    if (!sessionIdRef.current) return

    try {
      const message = createClientMessage({
        mimeType: 'audio/pcm',
        data,
        messageType: 'thought',
        sessionId: sessionIdRef.current,
        turnComplete
      })

      await ApiClient.sendMessage(sessionIdRef.current, message)
    } catch (error) {
      logApiError(error, `sendAudioMessage(${sessionIdRef.current})`)
      if (onError) {
        onError(error as Error)
      }
      throw error
    }
  }, [onError])

  // Send turn complete signal
  const sendTurnComplete = useCallback(async () => {
    try {
      await sendAudioMessage('', true)
    } catch {
      // Error already handled in sendAudioMessage
    }
  }, [sendAudioMessage])

  // Send buffered audio data every 0.2 seconds
  const sendBufferedAudio = useCallback(async () => {
    if (audioBufferRef.current.length === 0 || !sessionIdRef.current) {
      return
    }

    // Calculate total length
    let totalLength = 0
    for (const chunk of audioBufferRef.current) {
      totalLength += chunk.length
    }

    // Merge all chunks
    const mergedBuffer = new Uint8Array(totalLength)
    let offset = 0
    for (const chunk of audioBufferRef.current) {
      mergedBuffer.set(chunk, offset)
      offset += chunk.length
    }

    // Clear buffer
    audioBufferRef.current = []

    // Calculate audio level for silence detection
    const float32Data = new Float32Array(mergedBuffer.buffer)
    const audioLevel = Math.sqrt(
      float32Data.reduce((sum, sample) => sum + sample * sample, 0) / float32Data.length
    )
    lastAudioLevelRef.current = audioLevel

    // Convert to base64
    const base64Audio = arrayBufferToBase64(mergedBuffer.buffer)

    // Send to API using the centralized client
    try {
      await sendAudioMessage(base64Audio, false)
    } catch {
      // Error already handled in sendAudioMessage
      return
    }

    // Detect silence (1.5 seconds)
    if (audioLevel < 0.01) { // Silence threshold
      if (!silenceTimerRef.current) {
        silenceTimerRef.current = setTimeout(() => {
          if (process.env.NODE_ENV === 'development') {
            console.log('Silence detected, completing turn')
          }
          sendTurnComplete()
        }, 1500)
      }
    } else {
      // Cancel silence timer if audio detected
      if (silenceTimerRef.current) {
        clearTimeout(silenceTimerRef.current)
        silenceTimerRef.current = null
      }
    }
  }, [sendTurnComplete, sendAudioMessage])

  // Setup SSE connection
  const setupSSEConnection = useCallback((sessionId: string) => {
    const params: EventSourceParams = {
      is_audio: true,
      language
    }
    
    const eventSource = ApiClient.createEventSource(sessionId, params)

    eventSource.onopen = () => {
      if (process.env.NODE_ENV === 'development') {
        console.log('Connected to audio session:', sessionId)
      }
      setState(prev => ({ ...prev, status: 'Connected - Speak naturally!' }))
    }

    eventSource.onmessage = async (event) => {
      try {
        const data = JSON.parse(event.data)

        // Handle audio playback
        if (data.mime_type === 'audio/pcm' && data.data && pcmPlayerRef.current) {
          await pcmPlayerRef.current.playPCM(data.data)
        }

        // Handle transcriptions
        if (data.mime_type === 'text/plain' && data.message_type === 'transcription') {
          if (process.env.NODE_ENV === 'development') {
            console.log('Transcription:', data.data)
          }
          if (onTranscription) {
            onTranscription(data.data)
          }
        }

        // Reset on turn complete
        if (data.turn_complete === true && pcmPlayerRef.current) {
          pcmPlayerRef.current.reset()
        }
      } catch (err) {
        if (process.env.NODE_ENV === 'development') {
          console.error('Failed to parse message:', err)
        }
      }
    }

    eventSource.onerror = (error) => {
      if (process.env.NODE_ENV === 'development') {
        console.error('SSE error:', error)
      }
      setState(prev => ({ ...prev, status: 'Connection error - click to restart' }))
      if (onError) {
        onError(new Error('SSE connection error'))
      }
    }

    eventSourceRef.current = eventSource
  }, [language, onTranscription, onError])

  // Setup audio recording
  const setupAudioRecording = useCallback(async () => {
    // Create audio context
    audioContextRef.current = new AudioContext({ sampleRate: AUDIO_SAMPLE_RATE })
    if (process.env.NODE_ENV === 'development') {
      console.log('AudioContext sample rate:', audioContextRef.current.sampleRate)
    }

    // Load the AudioWorklet module
    try {
      // Create the worklet processor inline to avoid path issues
      const workletCode = `
        class PCMRecorderProcessor extends AudioWorkletProcessor {
          constructor() {
            super();
          }
          
          process(inputs, outputs, parameters) {
            if (inputs.length > 0 && inputs[0].length > 0) {
              // Use the first channel
              const inputChannel = inputs[0][0];
              // Copy the buffer to avoid issues with recycled memory
              const inputCopy = new Float32Array(inputChannel);
              this.port.postMessage(inputCopy);
            }
            return true;
          }
        }
        
        registerProcessor("pcm-recorder-processor", PCMRecorderProcessor);
      `;

      const blob = new Blob([workletCode], { type: 'application/javascript' });
      const workletUrl = URL.createObjectURL(blob);

      await audioContextRef.current.audioWorklet.addModule(workletUrl);
      URL.revokeObjectURL(workletUrl);
      if (process.env.NODE_ENV === 'development') {
        console.log('AudioWorklet module loaded successfully')
      }
    } catch (error) {
      console.error('Failed to load AudioWorklet:', error)
      throw error
    }

    // Get microphone stream
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
        sampleRate: AUDIO_SAMPLE_RATE
      }
    })
    streamRef.current = stream

    // Create audio source from microphone
    sourceRef.current = audioContextRef.current.createMediaStreamSource(stream)

    // Create and connect the AudioWorkletNode
    workletNodeRef.current = new AudioWorkletNode(
      audioContextRef.current,
      'pcm-recorder-processor'
    )

    // Handle messages from the worklet (audio data)
    workletNodeRef.current.port.onmessage = (event) => {
      const float32Data = event.data as Float32Array
      const pcmData = convertFloat32ToPCM(float32Data)
      audioBufferRef.current.push(new Uint8Array(pcmData))
    }

    // Connect the nodes
    sourceRef.current.connect(workletNodeRef.current)
    workletNodeRef.current.connect(audioContextRef.current.destination)

    // Start periodic buffer sending
    bufferTimerRef.current = setInterval(() => {
      sendBufferedAudio()
    }, 200)
  }, [sendBufferedAudio])

  // Start conversation
  const startConversation = useCallback(async () => {
    if (state.isActive) return

    setState(prev => ({ ...prev, status: 'Requesting microphone permission...', error: null }))

    try {
      // Test microphone permission
      const testStream = await navigator.mediaDevices.getUserMedia({ audio: true })
      testStream.getTracks().forEach(track => track.stop())

      // Generate session ID using centralized utility
      const sessionId = generateAudioSessionId()
      sessionIdRef.current = sessionId

      // Setup SSE connection
      setupSSEConnection(sessionId)

      // Setup audio recording
      await setupAudioRecording()

      setState(prev => ({ ...prev, isActive: true, status: 'Recording - speak naturally!' }))
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Failed to start conversation:', error)
      }
      setState(prev => ({
        ...prev,
        status: 'Failed to start - check microphone permissions',
        error: error as Error
      }))
      if (onError) {
        onError(error as Error)
      }
    }
  }, [state.isActive, setupSSEConnection, setupAudioRecording, onError])

  // Clean up resources
  const cleanup = useCallback(() => {
    // Clean up timers
    if (bufferTimerRef.current) {
      clearInterval(bufferTimerRef.current)
      bufferTimerRef.current = null
    }
    if (silenceTimerRef.current) {
      clearTimeout(silenceTimerRef.current)
      silenceTimerRef.current = null
    }

    // Clean up audio resources
    if (workletNodeRef.current) {
      workletNodeRef.current.disconnect()
      workletNodeRef.current = null
    }
    if (sourceRef.current) {
      sourceRef.current.disconnect()
      sourceRef.current = null
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
      streamRef.current = null
    }
    if (audioContextRef.current) {
      audioContextRef.current.close()
      audioContextRef.current = null
    }

    // Clean up SSE connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
      eventSourceRef.current = null
    }

    // Clear audio buffer
    audioBufferRef.current = []
  }, [])

  // Stop conversation
  const stopConversation = useCallback(() => {
    if (!state.isActive) return

    cleanup()
    setState({
      isActive: false,
      status: 'Conversation ended',
      error: null
    })
  }, [state.isActive, cleanup])

  return {
    ...state,
    startConversation,
    stopConversation
  }
}