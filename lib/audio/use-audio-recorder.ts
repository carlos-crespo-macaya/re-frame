import { useState, useCallback, useRef, useEffect } from 'react'
import { AudioRecorder, AudioRecorderOptions } from './audio-recorder'
import { MicPermissionState } from './audio-types'

export interface UseAudioRecorderOptions extends AudioRecorderOptions {
  onTranscription?: (text: string) => void
  onError?: (error: Error) => void
  onDataAvailable?: (data: Float32Array) => void
}

export interface AudioRecorderState {
  isRecording: boolean
  isProcessing: boolean
  micPermission: MicPermissionState
  error: Error | null
  audioBlob: Blob | null
  audioUrl: string | null
  isGateOpen: boolean
}

export function useAudioRecorder(options: UseAudioRecorderOptions = {}) {
  const [state, setState] = useState<AudioRecorderState>({
    isRecording: false,
    isProcessing: false,
    micPermission: 'prompt',
    error: null,
    audioBlob: null,
    audioUrl: null,
    isGateOpen: false
  })
  
  const recorderRef = useRef<AudioRecorder | null>(null)
  const audioUrlRef = useRef<string | null>(null)
  
  // Check microphone permission
  const checkMicPermission = useCallback(async () => {
    setState(prev => ({ ...prev, micPermission: 'checking' }))
    
    try {
      const result = await navigator.permissions.query({ name: 'microphone' as PermissionName })
      setState(prev => ({ ...prev, micPermission: result.state as MicPermissionState }))
      
      result.addEventListener('change', () => {
        setState(prev => ({ ...prev, micPermission: result.state as MicPermissionState }))
      })
    } catch (error) {
      // Fallback for browsers that don't support permission query
      setState(prev => ({ ...prev, micPermission: 'prompt' }))
    }
  }, [])
  
  // Initialize recorder
  const initializeRecorder = useCallback(async () => {
    if (recorderRef.current?.isInitialized) {
      return
    }
    
    try {
      const recorder = new AudioRecorder(options, {
        onGateStateChange: (isOpen) => {
          setState(prev => ({ ...prev, isGateOpen: isOpen }))
        },
        onError: (error) => {
          setState(prev => ({ ...prev, error }))
          if (options.onError) {
            options.onError(error)
          }
        },
        onStop: (audioBlob) => {
          setState(prev => ({ ...prev, audioBlob }))
        },
        onDataAvailable: options.onDataAvailable
      })
      
      await recorder.initialize()
      recorderRef.current = recorder
      setState(prev => ({ ...prev, micPermission: 'granted', error: null }))
      
    } catch (error) {
      const err = error as Error
      setState(prev => ({
        ...prev,
        error: err,
        micPermission: err.name === 'NotAllowedError' ? 'denied' : prev.micPermission
      }))
      
      if (options.onError) {
        options.onError(err)
      }
      
      throw err
    }
  }, [options])
  
  // Start recording
  const startRecording = useCallback(async () => {
    try {
      setState(prev => ({ ...prev, error: null }))
      
      // Initialize recorder if needed
      if (!recorderRef.current?.isInitialized) {
        await initializeRecorder()
      }
      
      if (!recorderRef.current) {
        throw new Error('Failed to initialize audio recorder')
      }
      
      // Clean up previous audio URL
      if (audioUrlRef.current) {
        URL.revokeObjectURL(audioUrlRef.current)
        audioUrlRef.current = null
      }
      
      await recorderRef.current.start()
      setState(prev => ({
        ...prev,
        isRecording: true,
        audioBlob: null,
        audioUrl: null
      }))
      
    } catch (error) {
      const err = error as Error
      setState(prev => ({ ...prev, error: err }))
      
      if (options.onError) {
        options.onError(err)
      }
    }
  }, [initializeRecorder, options])
  
  // Stop recording
  const stopRecording = useCallback(async () => {
    if (!recorderRef.current?.recording) {
      return
    }
    
    try {
      setState(prev => ({ ...prev, isProcessing: true }))
      
      const audioBlob = await recorderRef.current.stop()
      const audioUrl = URL.createObjectURL(audioBlob)
      
      audioUrlRef.current = audioUrl
      
      setState(prev => ({
        ...prev,
        isRecording: false,
        isProcessing: false,
        audioBlob,
        audioUrl
      }))
      
      // Here you would typically send the audio blob to a transcription service
      // For now, we'll just simulate it
      if (options.onTranscription) {
        setTimeout(() => {
          options.onTranscription!('This would be the transcribed text from the audio recording.')
        }, 1000)
      }
      
    } catch (error) {
      const err = error as Error
      setState(prev => ({
        ...prev,
        isRecording: false,
        isProcessing: false,
        error: err
      }))
      
      if (options.onError) {
        options.onError(err)
      }
    }
  }, [options])
  
  // Set noise gate threshold
  const setNoiseGateThreshold = useCallback((threshold: number) => {
    if (recorderRef.current) {
      recorderRef.current.setNoiseGateThreshold(threshold)
    }
  }, [])
  
  // Manual cleanup
  const cleanup = useCallback(() => {
    if (recorderRef.current) {
      recorderRef.current.cleanup()
      recorderRef.current = null
    }
    if (audioUrlRef.current) {
      URL.revokeObjectURL(audioUrlRef.current)
      audioUrlRef.current = null
    }
    setState({
      isRecording: false,
      isProcessing: false,
      micPermission: 'prompt',
      error: null,
      audioBlob: null,
      audioUrl: null,
      isGateOpen: false
    })
  }, [])
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (recorderRef.current) {
        recorderRef.current.cleanup()
      }
      if (audioUrlRef.current) {
        URL.revokeObjectURL(audioUrlRef.current)
      }
    }
  }, [])
  
  return {
    ...state,
    startRecording,
    stopRecording,
    checkMicPermission,
    setNoiseGateThreshold,
    cleanup
  }
}