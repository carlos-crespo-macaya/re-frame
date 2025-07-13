export interface AudioRecorderOptions {
  sampleRate?: number
  channelCount?: number
  echoCancellation?: boolean
  noiseSuppression?: boolean
  autoGainControl?: boolean
}

export interface AudioRecorderCallbacks {
  onDataAvailable?: (data: Float32Array) => void
  onGateStateChange?: (isOpen: boolean) => void
  onError?: (error: Error) => void
  onStop?: (audioBlob: Blob) => void
}

export class AudioRecorder {
  private audioContext: AudioContext | null = null
  private mediaStream: MediaStream | null = null
  private source: MediaStreamAudioSourceNode | null = null
  private noiseGate: AudioWorkletNode | null = null
  private recorder: AudioWorkletNode | null = null
  private recordedChunks: Float32Array[] = []
  private isRecording = false
  private callbacks: AudioRecorderCallbacks
  
  constructor(
    private options: AudioRecorderOptions = {},
    callbacks: AudioRecorderCallbacks = {}
  ) {
    this.callbacks = callbacks
  }
  
  async initialize(): Promise<void> {
    try {
      // Create audio context
      this.audioContext = new AudioContext({
        sampleRate: this.options.sampleRate || 48000
      })
      
      // Load worklet modules using configured paths
      const { getRecordingConfig } = await import('./audio-config')
      const config = getRecordingConfig()
      await this.audioContext.audioWorklet.addModule(config.worklets.processorPath)
      await this.audioContext.audioWorklet.addModule(config.worklets.recorderPath)
      
      // Request microphone access
      this.mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: this.options.channelCount || 1,
          echoCancellation: this.options.echoCancellation !== false,
          noiseSuppression: this.options.noiseSuppression !== false,
          autoGainControl: this.options.autoGainControl !== false
        }
      })
      
      // Create audio nodes
      this.source = this.audioContext.createMediaStreamSource(this.mediaStream)
      
      // Create noise gate
      this.noiseGate = new AudioWorkletNode(this.audioContext, 'noise-gate-processor')
      this.noiseGate.port.onmessage = (event) => {
        if (event.data.type === 'gateState' && this.callbacks.onGateStateChange) {
          this.callbacks.onGateStateChange(event.data.isOpen)
        }
      }
      
      // Create recorder
      this.recorder = new AudioWorkletNode(this.audioContext, 'audio-recorder-processor')
      this.recorder.port.onmessage = (event) => {
        if (event.data.type === 'AUDIO_DATA') {
          this.recordedChunks.push(event.data.audioData)
          if (this.callbacks.onDataAvailable) {
            this.callbacks.onDataAvailable(event.data.audioData)
          }
        }
      }
      
      // Connect audio graph
      this.source.connect(this.noiseGate)
      this.noiseGate.connect(this.recorder)
      this.recorder.connect(this.audioContext.destination)
      
    } catch (error) {
      this.cleanup()
      if (this.callbacks.onError) {
        this.callbacks.onError(error as Error)
      }
      throw error
    }
  }
  
  async start(): Promise<void> {
    if (!this.recorder || !this.audioContext) {
      throw new Error('Audio recorder not initialized')
    }
    
    if (this.isRecording) {
      return
    }
    
    this.recordedChunks = []
    this.isRecording = true
    
    // Resume audio context if suspended
    if (this.audioContext.state === 'suspended') {
      await this.audioContext.resume()
    }
    
    this.recorder.port.postMessage({ type: 'START_RECORDING' })
  }
  
  async stop(): Promise<Blob> {
    if (!this.recorder || !this.isRecording) {
      throw new Error('Not recording')
    }
    
    this.isRecording = false
    this.recorder.port.postMessage({ type: 'STOP_RECORDING' })
    
    // Wait a bit for any remaining chunks
    await new Promise(resolve => setTimeout(resolve, 100))
    
    // Convert recorded chunks to WAV blob
    const audioBlob = this.createWAVBlob(this.recordedChunks)
    
    if (this.callbacks.onStop) {
      this.callbacks.onStop(audioBlob)
    }
    
    return audioBlob
  }
  
  setNoiseGateThreshold(threshold: number): void {
    if (!this.noiseGate) return
    
    const param = this.noiseGate.parameters.get('threshold')
    if (param) {
      param.value = threshold
    }
  }
  
  cleanup(): void {
    if (this.source) {
      this.source.disconnect()
      this.source = null
    }
    
    if (this.noiseGate) {
      this.noiseGate.disconnect()
      this.noiseGate = null
    }
    
    if (this.recorder) {
      this.recorder.disconnect()
      this.recorder = null
    }
    
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach(track => track.stop())
      this.mediaStream = null
    }
    
    if (this.audioContext) {
      this.audioContext.close()
      this.audioContext = null
    }
    
    this.recordedChunks = []
    this.isRecording = false
  }
  
  private createWAVBlob(chunks: Float32Array[]): Blob {
    // Calculate total length
    const totalLength = chunks.reduce((acc, chunk) => acc + chunk.length, 0)
    
    // Merge all chunks
    const audioData = new Float32Array(totalLength)
    let offset = 0
    for (const chunk of chunks) {
      audioData.set(chunk, offset)
      offset += chunk.length
    }
    
    // Convert to WAV
    const sampleRate = this.audioContext?.sampleRate || 48000
    const wavData = this.encodeWAV(audioData, sampleRate)
    
    return new Blob([wavData], { type: 'audio/wav' })
  }
  
  private encodeWAV(samples: Float32Array, sampleRate: number): ArrayBuffer {
    const buffer = new ArrayBuffer(44 + samples.length * 2)
    const view = new DataView(buffer)
    
    // WAV header
    const writeString = (offset: number, string: string) => {
      for (let i = 0; i < string.length; i++) {
        view.setUint8(offset + i, string.charCodeAt(i))
      }
    }
    
    writeString(0, 'RIFF')
    view.setUint32(4, 36 + samples.length * 2, true)
    writeString(8, 'WAVE')
    writeString(12, 'fmt ')
    view.setUint32(16, 16, true)
    view.setUint16(20, 1, true)
    view.setUint16(22, 1, true)
    view.setUint32(24, sampleRate, true)
    view.setUint32(28, sampleRate * 2, true)
    view.setUint16(32, 2, true)
    view.setUint16(34, 16, true)
    writeString(36, 'data')
    view.setUint32(40, samples.length * 2, true)
    
    // Convert float samples to 16-bit PCM
    let offset = 44
    for (let i = 0; i < samples.length; i++) {
      const sample = Math.max(-1, Math.min(1, samples[i]))
      view.setInt16(offset, sample * 0x7FFF, true)
      offset += 2
    }
    
    return buffer
  }
  
  get isInitialized(): boolean {
    return this.audioContext !== null && this.mediaStream !== null
  }
  
  get recording(): boolean {
    return this.isRecording
  }
}