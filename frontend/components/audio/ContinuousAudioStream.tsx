'use client'

import { useState, useRef, useCallback, useEffect } from 'react'
import { Button } from '@/components/ui'
import { arrayBufferToBase64 } from '@/lib/audio/audio-utils'

interface ContinuousAudioStreamProps {
  language?: string
}

export function ContinuousAudioStream({ language = 'en-US' }: ContinuousAudioStreamProps) {
  const [isActive, setIsActive] = useState(false)
  const [sessionId, setSessionId] = useState<string | null>(null)
  
  // Refs
  const eventSourceRef = useRef<EventSource | null>(null)
  const audioContextRef = useRef<AudioContext | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null)
  const workletNodeRef = useRef<AudioWorkletNode | null>(null)
  const audioBufferRef = useRef<Uint8Array[]>([])
  const bufferTimerRef = useRef<NodeJS.Timeout | null>(null)
  
  // PCM Player
  const pcmPlayerRef = useRef<AudioContext | null>(null)
  const nextStartTime = useRef(0)
  
  // Initialize PCM player
  useEffect(() => {
    pcmPlayerRef.current = new AudioContext({ sampleRate: 24000 })
    return () => {
      if (pcmPlayerRef.current) {
        pcmPlayerRef.current.close()
      }
    }
  }, [])
  
  // Play PCM audio
  const playPCM = async (base64Data: string) => {
    if (!pcmPlayerRef.current) return
    
    try {
      // Decode base64
      const binaryString = atob(base64Data)
      const bytes = new Uint8Array(binaryString.length)
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i)
      }
      
      // Convert to Int16Array
      const int16Data = new Int16Array(bytes.buffer)
      
      // Convert to Float32
      const float32Data = new Float32Array(int16Data.length)
      for (let i = 0; i < int16Data.length; i++) {
        float32Data[i] = int16Data[i] / 32768.0
      }
      
      // Create and play buffer
      const audioBuffer = pcmPlayerRef.current.createBuffer(1, float32Data.length, 24000)
      audioBuffer.copyToChannel(float32Data, 0)
      
      const source = pcmPlayerRef.current.createBufferSource()
      source.buffer = audioBuffer
      source.connect(pcmPlayerRef.current.destination)
      
      const currentTime = pcmPlayerRef.current.currentTime
      if (nextStartTime.current < currentTime) {
        nextStartTime.current = currentTime
      }
      
      source.start(nextStartTime.current)
      nextStartTime.current += audioBuffer.duration
      
    } catch (error) {
      console.error('Failed to play audio:', error)
    }
  }
  
  // Send buffered audio
  const sendBufferedAudio = useCallback(async () => {
    if (audioBufferRef.current.length === 0 || !sessionId) return
    
    // Combine chunks
    let totalLength = 0
    for (const chunk of audioBufferRef.current) {
      totalLength += chunk.length
    }
    
    const combinedBuffer = new Uint8Array(totalLength)
    let offset = 0
    for (const chunk of audioBufferRef.current) {
      combinedBuffer.set(chunk, offset)
      offset += chunk.length
    }
    
    // Send audio
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/send/${sessionId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          mime_type: 'audio/pcm',
          data: arrayBufferToBase64(combinedBuffer.buffer),
        })
      })
      
      if (!response.ok) {
        console.error('Failed to send audio:', response.statusText)
      }
    } catch (error) {
      console.error('Error sending audio:', error)
    }
    
    audioBufferRef.current = []
  }, [sessionId])
  
  // Start streaming
  const startStream = async () => {
    try {
      // Generate session ID
      const newSessionId = Math.random().toString().substring(10)
      setSessionId(newSessionId)
      
      // Connect SSE
      const eventSource = new EventSource(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/events/${newSessionId}?is_audio=true`
      )
      
      eventSource.onopen = () => {
        console.log('SSE connected for audio session:', newSessionId)
      }
      
      eventSource.onmessage = async (event) => {
        const message = JSON.parse(event.data)
        
        if (message.mime_type === 'audio/pcm' && message.data) {
          await playPCM(message.data)
        }
        
        if (message.turn_complete) {
          nextStartTime.current = 0 // Reset audio timing
        }
      }
      
      eventSource.onerror = (error) => {
        console.error('SSE error:', error)
      }
      
      eventSourceRef.current = eventSource
      
      // Start microphone
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true
        }
      })
      
      streamRef.current = stream
      audioContextRef.current = new AudioContext({ sampleRate: 16000 })
      
      // Create worklet
      const processorCode = `
        class RecorderProcessor extends AudioWorkletProcessor {
          process(inputs) {
            const input = inputs[0];
            if (input && input[0]) {
              this.port.postMessage(input[0].slice());
            }
            return true;
          }
        }
        registerProcessor('recorder-processor', RecorderProcessor);
      `
      
      const blob = new Blob([processorCode], { type: 'application/javascript' })
      const workletUrl = URL.createObjectURL(blob)
      await audioContextRef.current.audioWorklet.addModule(workletUrl)
      
      sourceRef.current = audioContextRef.current.createMediaStreamSource(stream)
      workletNodeRef.current = new AudioWorkletNode(audioContextRef.current, 'recorder-processor')
      
      // Handle audio data
      workletNodeRef.current.port.onmessage = (event) => {
        const float32Data = event.data
        
        // Convert to Int16
        const int16Data = new Int16Array(float32Data.length)
        for (let i = 0; i < float32Data.length; i++) {
          int16Data[i] = float32Data[i] * 0x7fff
        }
        
        audioBufferRef.current.push(new Uint8Array(int16Data.buffer))
      }
      
      sourceRef.current.connect(workletNodeRef.current)
      
      // Start buffer timer
      bufferTimerRef.current = setInterval(sendBufferedAudio, 200)
      
      URL.revokeObjectURL(workletUrl)
      setIsActive(true)
      
    } catch (error) {
      console.error('Failed to start stream:', error)
    }
  }
  
  // Stop streaming
  const stopStream = () => {
    // Stop timer
    if (bufferTimerRef.current) {
      clearInterval(bufferTimerRef.current)
      bufferTimerRef.current = null
    }
    
    // Send remaining audio
    sendBufferedAudio()
    
    // Stop audio
    if (sourceRef.current) {
      sourceRef.current.disconnect()
    }
    if (workletNodeRef.current) {
      workletNodeRef.current.disconnect()
    }
    if (audioContextRef.current) {
      audioContextRef.current.close()
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
    }
    
    // Close SSE
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
    }
    
    setIsActive(false)
    setSessionId(null)
    audioBufferRef.current = []
  }
  
  return (
    <div className="text-center">
      <button
        onClick={isActive ? stopStream : startStream}
        className={`
          w-16 h-16 rounded-full transition-all duration-200
          ${isActive 
            ? 'bg-red-500 hover:bg-red-600' 
            : 'bg-neutral-300 hover:bg-neutral-400'
          }
          flex items-center justify-center mx-auto
        `}
      >
        {isActive ? (
          <span className="w-4 h-4 bg-white rounded-full" />
        ) : (
          <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
          </svg>
        )}
      </button>
      
      {isActive && (
        <p className="mt-2 text-sm text-neutral-600">Audio streaming active</p>
      )}
    </div>
  )
}