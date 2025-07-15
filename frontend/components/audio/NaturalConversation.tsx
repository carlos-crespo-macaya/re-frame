'use client'

import { useState, useRef, useCallback, useEffect } from 'react'
import { Button } from '@/components/ui'
import { PCMPlayer } from '@/lib/audio/pcm-player'
import { arrayBufferToBase64 } from '@/lib/audio/audio-utils'

interface NaturalConversationProps {
  language?: string
}

export function NaturalConversation({ language = 'en-US' }: NaturalConversationProps) {
  const [isActive, setIsActive] = useState(false)
  const [status, setStatus] = useState<string>('Click to start conversation')
  
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
    pcmPlayerRef.current = new PCMPlayer(24000)
    
    return () => {
      if (pcmPlayerRef.current) {
        pcmPlayerRef.current.stop()
      }
    }
  }, [])
  
  // Cleanup on unmount
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
    }
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
    
    // Combine all chunks into a single buffer
    const combinedBuffer = new Uint8Array(totalLength)
    let offset = 0
    for (const chunk of audioBufferRef.current) {
      combinedBuffer.set(chunk, offset)
      offset += chunk.length
    }
    
    // Calculate audio level for silence detection
    let sum = 0
    for (let i = 0; i < combinedBuffer.length; i += 2) {
      const sample = (combinedBuffer[i] | (combinedBuffer[i + 1] << 8))
      const normalized = sample > 32767 ? sample - 65536 : sample
      sum += Math.abs(normalized / 32768.0)
    }
    const audioLevel = sum / (combinedBuffer.length / 2)
    lastAudioLevelRef.current = audioLevel
    
    // Convert to base64
    const base64Data = arrayBufferToBase64(combinedBuffer.buffer)
    
    // Log what we're sending
    if (process.env.NODE_ENV === 'development') {
      console.log('Sending audio chunk:', {
        sessionId: sessionIdRef.current,
        dataLength: base64Data.length,
        bufferSize: combinedBuffer.length,
        audioLevel: audioLevel.toFixed(4),
        timestamp: new Date().toISOString()
      })
    }
    
    // Send the combined audio data
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/send/${sessionIdRef.current}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          mime_type: 'audio/pcm',
          data: base64Data,
        })
      })
      
      if (!response.ok) {
        if (process.env.NODE_ENV === 'development') {
          console.error('Failed to send audio:', response.statusText)
        }
      } else {
        if (process.env.NODE_ENV === 'development') {
          console.log('Audio sent successfully')
        }
      }
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Error sending audio:', error)
      }
    }
    
    // Clear the buffer
    audioBufferRef.current = []
    
    // No turn_complete needed - backend handles turn detection automatically
  }, [])
  
  // Audio recorder handler
  const audioRecorderHandler = useCallback((pcmData: ArrayBuffer) => {
    // Add audio data to buffer
    const uint8Data = new Uint8Array(pcmData)
    audioBufferRef.current.push(uint8Data)
    
    // Log audio level for debugging
    const dataView = new DataView(pcmData)
    let maxValue = 0
    for (let i = 0; i < dataView.byteLength - 1; i += 2) {
      const sample = Math.abs(dataView.getInt16(i, true) / 32768)
      maxValue = Math.max(maxValue, sample)
    }
    
    if (maxValue > 0.01) {
      if (process.env.NODE_ENV === 'development') {
        console.log('Audio received with level:', maxValue.toFixed(3), 'buffer size:', uint8Data.length)
      }
    }
  }, [])
  
  // Start audio recording and SSE connection
  const startConversation = async () => {
    try {
      setStatus('Starting conversation...')
      
      // First test microphone access
      if (process.env.NODE_ENV === 'development') {
        console.log('Testing microphone access...')
      }
      const testStream = await navigator.mediaDevices.getUserMedia({ audio: true })
      if (process.env.NODE_ENV === 'development') {
        console.log('Test stream obtained:', testStream)
      }
      testStream.getTracks().forEach(track => {
        if (process.env.NODE_ENV === 'development') {
          console.log('Test track:', track.label, track.enabled)
        }
        track.stop()
      })
      
      // Generate session ID
      const sessionId = `audio-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      sessionIdRef.current = sessionId
      
      // Connect to SSE endpoint with audio mode
      const eventSource = new EventSource(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/events/${sessionId}?is_audio=true&language=${language}`
      )
      
      eventSource.onopen = () => {
        if (process.env.NODE_ENV === 'development') {
          console.log('Connected to audio session:', sessionId)
        }
        setStatus('Connected - Speak naturally!')
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
        setStatus('Connection error - click to restart')
      }
      
      eventSourceRef.current = eventSource
      
      // Create audio context first
      audioContextRef.current = new AudioContext({ sampleRate: 16000 })
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
        
        // Request microphone permission
        if (process.env.NODE_ENV === 'development') {
          console.log('Requesting microphone permission...')
        }
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: { channelCount: 1 }
        })
        
        if (process.env.NODE_ENV === 'development') {
          console.log('Microphone permission granted')
        }
        streamRef.current = stream
        
        // Create the source and worklet node
        sourceRef.current = audioContextRef.current.createMediaStreamSource(stream)
        const audioRecorderNode = new AudioWorkletNode(
          audioContextRef.current,
          'pcm-recorder-processor'
        )
        
        // Store the worklet node reference
        workletNodeRef.current = audioRecorderNode
        
        // Connect the microphone source to the worklet
        sourceRef.current.connect(audioRecorderNode)
        
        // Handle incoming audio data
        audioRecorderNode.port.onmessage = (event) => {
          // Convert to 16-bit PCM
          const pcmData = convertFloat32ToPCM(event.data)
          // Send the PCM data to the handler
          audioRecorderHandler(pcmData)
        }
        
        if (process.env.NODE_ENV === 'development') {
          console.log('Audio recording started with AudioWorklet')
        }
        
      } catch (error) {
        if (process.env.NODE_ENV === 'development') {
          console.error('Failed to setup AudioWorklet, falling back to ScriptProcessor:', error)
        }
        
        // Fallback to ScriptProcessor if AudioWorklet fails
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: { channelCount: 1 }
        })
        streamRef.current = stream
        
        sourceRef.current = audioContextRef.current.createMediaStreamSource(stream)
        const scriptProcessor = audioContextRef.current.createScriptProcessor(4096, 1, 1)
        
        scriptProcessor.onaudioprocess = (e) => {
          const inputData = e.inputBuffer.getChannelData(0)
          const pcmData = convertFloat32ToPCM(inputData)
          audioRecorderHandler(pcmData)
        }
        
        sourceRef.current.connect(scriptProcessor)
        // ScriptProcessor requires connection to destination for processing to work,
        // but we use a gain node set to 0 to prevent audio feedback
        const silentGain = audioContextRef.current.createGain()
        silentGain.gain.value = 0
        scriptProcessor.connect(silentGain)
        silentGain.connect(audioContextRef.current.destination)
        
        if (process.env.NODE_ENV === 'development') {
          console.log('Audio recording started with ScriptProcessor (fallback)')
        }
      }
      
      setIsActive(true)
      if (process.env.NODE_ENV === 'development') {
        console.log('Audio recording started, timer interval starting...')
      }
      
      // Start the buffer timer to send audio every 200ms
      bufferTimerRef.current = setInterval(() => {
        sendBufferedAudio()
      }, 200)
      if (process.env.NODE_ENV === 'development') {
        console.log('Buffer timer started')
      }
      
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Failed to start conversation:', error)
      }
      setStatus('Failed to start - click to retry')
    }
  }
  
  // Stop conversation and cleanup
  const stopConversation = () => {
    setStatus('Stopping conversation...')
    
    // Stop buffering timer
    if (bufferTimerRef.current) {
      clearInterval(bufferTimerRef.current)
      bufferTimerRef.current = null
    }
    
    // Stop silence timer
    if (silenceTimerRef.current) {
      clearTimeout(silenceTimerRef.current)
      silenceTimerRef.current = null
    }
    
    // Send any remaining buffered audio
    if (audioBufferRef.current.length > 0) {
      sendBufferedAudio()
    }
    
    // Disconnect audio nodes
    if (sourceRef.current) {
      sourceRef.current.disconnect()
      sourceRef.current = null
    }
    
    if (workletNodeRef.current) {
      workletNodeRef.current.disconnect()
      workletNodeRef.current = null
    }
    
    // Close audio context
    if (audioContextRef.current) {
      audioContextRef.current.close()
      audioContextRef.current = null
    }
    
    // Stop all tracks
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
      streamRef.current = null
    }
    
    // Close SSE connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
      eventSourceRef.current = null
    }
    
    // Reset PCM player
    if (pcmPlayerRef.current) {
      pcmPlayerRef.current.stop()
      pcmPlayerRef.current = new PCMPlayer(24000)
    }
    
    setIsActive(false)
    setStatus('Click to start conversation')
    sessionIdRef.current = null
    audioBufferRef.current = []
  }
  
  return (
    <div className="flex flex-col items-center space-y-4">
      <div className="text-center">
        <p className="text-sm text-neutral-600 mb-2">{status}</p>
      </div>
      
      <Button
        onClick={isActive ? stopConversation : startConversation}
        variant={isActive ? "secondary" : "primary"}
        size="large"
        className="min-w-[200px]"
      >
        {isActive ? (
          <>
            <span className="inline-block w-2 h-2 bg-red-500 rounded-full mr-2 animate-pulse" />
            Stop Conversation
          </>
        ) : (
          <>
            <svg 
              className="w-5 h-5 mr-2" 
              fill="none" 
              viewBox="0 0 24 24" 
              stroke="currentColor"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" 
              />
            </svg>
            Start Conversation
          </>
        )}
      </Button>
      
      {isActive && (
        <div className="text-xs text-neutral-500 text-center">
          <p>Speak naturally - the AI will respond when you pause</p>
          <p className="mt-1">Audio is streaming in real-time</p>
        </div>
      )}
    </div>
  )
}