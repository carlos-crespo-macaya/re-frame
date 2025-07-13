export type AudioMode = 'instant' | 'manual'
export type MicPermissionState = 'prompt' | 'granted' | 'denied' | 'checking'

export interface AudioState {
  audioEnabled: boolean
  isRecording: boolean
  isProcessing: boolean
  audioLevel: number
  micPermission: MicPermissionState
  mode: AudioMode
  transcription: string
  error?: string | null
}

export function createDefaultAudioState(): AudioState {
  return {
    audioEnabled: false,
    isRecording: false,
    isProcessing: false,
    audioLevel: 0,
    micPermission: 'prompt',
    mode: 'instant',
    transcription: '',
    error: null
  }
}