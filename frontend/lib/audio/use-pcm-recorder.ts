import { useState, useRef, useCallback } from 'react'
import { arrayBufferToBase64 } from './audio-utils'

export interface UsePCMRecorderOptions {
  sampleRate?: number
  onDataAvailable?: (pcmData: Float32Array) => void
  onError?: (error: Error) => void
}

export function usePCMRecorder(options: UsePCMRecorderOptions = {}) {
  const { sampleRate = 16000, onDataAvailable, onError } = options
  
  const [isRecording, setIsRecording] = useState(false)
  const [isInitialized, setIsInitialized] = useState(false)
  
  const audioContextRef = useRef<AudioContext | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const workletNodeRef = useRef<AudioWorkletNode | null>(null)
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null)
  const pcmBufferRef = useRef<Float32Array[]>([])
  const isRecordingRef = useRef(false)
  
  const initialize = useCallback(async () => {
    try {
      // Request microphone permission
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      })
      
      streamRef.current = stream
      
      // Create audio context
      audioContextRef.current = new AudioContext({ sampleRate })
      
      // Create inline worklet processor
      const processorCode = `
        class RecorderProcessor extends AudioWorkletProcessor {
          constructor() {
            super();
          }
          
          process(inputs, outputs, parameters) {
            const input = inputs[0];
            if (input && input[0]) {
              this.port.postMessage({
                type: 'audio',
                data: input[0].slice()
              });
            }
            return true;
          }
        }
        
        registerProcessor('recorder-processor', RecorderProcessor);
      `
      
      const blob = new Blob([processorCode], { type: 'application/javascript' })
      const workletUrl = URL.createObjectURL(blob)
      await audioContextRef.current.audioWorklet.addModule(workletUrl)
      
      // Create nodes
      sourceRef.current = audioContextRef.current.createMediaStreamSource(stream)
      workletNodeRef.current = new AudioWorkletNode(audioContextRef.current, 'recorder-processor')
      
      // Handle audio data
      workletNodeRef.current.port.onmessage = (event) => {
        if (event.data.type === 'audio') {
          const audioData = event.data.data as Float32Array
          // Remove logging to avoid spam
          if (isRecordingRef.current) {
            pcmBufferRef.current.push(audioData)
            onDataAvailable?.(audioData)
          }
        }
      }
      
      // Connect nodes
      sourceRef.current.connect(workletNodeRef.current)
      
      setIsInitialized(true)
      
      // Clean up blob URL
      URL.revokeObjectURL(workletUrl)
      
    } catch (error) {
      console.error('Failed to initialize PCM recorder:', error)
      onError?.(error as Error)
      throw error
    }
  }, [sampleRate, onDataAvailable, onError])
  
  const startRecording = useCallback(async () => {
    try {
      if (!isInitialized) {
        await initialize()
      }
      
      pcmBufferRef.current = []
      isRecordingRef.current = true
      setIsRecording(true)
      
    } catch (error) {
      console.error('Failed to start recording:', error)
      onError?.(error as Error)
    }
  }, [isInitialized, initialize, onError])
  
  const stopRecording = useCallback(async (): Promise<string | null> => {
    try {
      isRecordingRef.current = false
      setIsRecording(false)
      
      // Give it a moment to collect any final audio chunks
      await new Promise(resolve => setTimeout(resolve, 100))
      
      if (pcmBufferRef.current.length === 0) {
        return null
      }
      
      // Merge all audio chunks
      const totalLength = pcmBufferRef.current.reduce((acc, chunk) => acc + chunk.length, 0)
      const mergedAudio = new Float32Array(totalLength)
      let offset = 0
      
      for (const chunk of pcmBufferRef.current) {
        mergedAudio.set(chunk, offset)
        offset += chunk.length
      }
      
      // Convert Float32 to Int16
      const int16Data = new Int16Array(mergedAudio.length)
      for (let i = 0; i < mergedAudio.length; i++) {
        const s = Math.max(-1, Math.min(1, mergedAudio[i]))
        int16Data[i] = s < 0 ? s * 0x8000 : s * 0x7FFF
      }
      
      // Convert to base64
      const bytes = new Uint8Array(int16Data.buffer)
      const base64Audio = arrayBufferToBase64(bytes.buffer)
      
      // Clear buffer
      pcmBufferRef.current = []
      
      return base64Audio
      
    } catch (error) {
      console.error('Failed to stop recording:', error)
      onError?.(error as Error)
      return null
    }
  }, [onError])
  
  const cleanup = useCallback(() => {
    // Stop all tracks
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
      streamRef.current = null
    }
    
    // Disconnect nodes
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
    
    setIsInitialized(false)
    setIsRecording(false)
    pcmBufferRef.current = []
  }, [])
  
  return {
    isRecording,
    isInitialized,
    startRecording,
    stopRecording,
    cleanup
  }
}