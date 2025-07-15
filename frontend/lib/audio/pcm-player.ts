/**
 * PCM Audio Player
 * Plays PCM audio data received from the backend
 */

export class PCMPlayer {
  private audioContext: AudioContext | null = null
  private sampleRate: number
  private isPlaying = false
  private audioQueue: AudioBuffer[] = []
  private nextStartTime = 0
  private isFirstChunk = true
  private startDelay = 0.1 // 100ms initial buffer
  
  constructor(sampleRate = 24000) {
    this.sampleRate = sampleRate
  }
  
  async initialize() {
    if (!this.audioContext) {
      this.audioContext = new AudioContext({ sampleRate: this.sampleRate })
      this.nextStartTime = this.audioContext.currentTime
    }
  }
  
  async playPCM(base64Data: string) {
    try {
      if (!this.audioContext) {
        await this.initialize()
      }
      
      // Decode base64 to array buffer
      const binaryString = atob(base64Data)
      const bytes = new Uint8Array(binaryString.length)
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i)
      }
      
      // Convert bytes to Int16Array (PCM data)
      // Ensure we have an even number of bytes and proper alignment
      const byteLength = Math.floor(bytes.length / 2) * 2
      const int16Data = new Int16Array(byteLength / 2)
      
      // Manually convert bytes to int16 values
      for (let i = 0; i < int16Data.length; i++) {
        const low = bytes[i * 2]
        const high = bytes[i * 2 + 1]
        // Combine bytes (little-endian)
        int16Data[i] = (high << 8) | low
      }
      
      // Convert Int16 to Float32 for Web Audio API
      const float32Data = new Float32Array(int16Data.length)
      for (let i = 0; i < int16Data.length; i++) {
        float32Data[i] = int16Data[i] / 32768.0
      }
      
      // Create audio buffer
      const audioBuffer = this.audioContext!.createBuffer(
        1, // mono
        float32Data.length,
        this.sampleRate
      )
      audioBuffer.copyToChannel(float32Data, 0)
      
      // Schedule playback
      const source = this.audioContext!.createBufferSource()
      source.buffer = audioBuffer
      source.connect(this.audioContext!.destination)
      
      // Play immediately or queue with initial buffer
      const currentTime = this.audioContext!.currentTime
      
      if (this.isFirstChunk) {
        // Add initial delay for first chunk to allow buffering
        this.nextStartTime = currentTime + this.startDelay
        this.isFirstChunk = false
      } else if (this.nextStartTime < currentTime) {
        // Reset if we're behind
        this.nextStartTime = currentTime
      }
      
      source.start(this.nextStartTime)
      
      // Update next start time
      this.nextStartTime += audioBuffer.duration
      
      // Reset if there's a gap
      source.onended = () => {
        const now = this.audioContext!.currentTime
        if (now > this.nextStartTime + 0.1) {
          // Reset if more than 100ms gap
          this.nextStartTime = now
        }
      }
      
    } catch (error) {
      console.error('Failed to play PCM audio:', error)
    }
  }
  
  stop() {
    if (this.audioContext) {
      this.audioContext.close()
      this.audioContext = null
    }
    this.nextStartTime = 0
    this.audioQueue = []
    this.isFirstChunk = true
  }
  
  reset() {
    this.isFirstChunk = true
    this.nextStartTime = this.audioContext ? this.audioContext.currentTime : 0
  }
}