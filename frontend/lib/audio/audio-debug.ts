/**
 * Audio debugging utilities for re-frame.social
 * Provides tools for debugging audio recording, playback, and streaming
 */

export interface AudioDebugInfo {
  contextState: AudioContextState
  sampleRate: number
  outputLatency: number
  baseLatency: number
  currentTime: number
}

export interface AudioLevelInfo {
  instant: number
  average: number
  peak: number
}

export interface DeviceInfo {
  deviceId: string
  label: string
  kind: MediaDeviceKind
  groupId: string
}

/**
 * Audio debugging utilities class
 */
export class AudioDebugger {
  private analyser: AnalyserNode | null = null
  private dataArray: Uint8Array | null = null
  
  /**
   * Get current audio context information
   */
  static getAudioContextInfo(context: AudioContext): AudioDebugInfo {
    return {
      contextState: context.state,
      sampleRate: context.sampleRate,
      outputLatency: context.outputLatency || 0,
      baseLatency: context.baseLatency || 0,
      currentTime: context.currentTime
    }
  }
  
  /**
   * Check browser audio support
   */
  static checkBrowserSupport(): {
    supported: boolean
    missing: string[]
  } {
    const missing: string[] = []
    
    if (!('AudioContext' in window || 'webkitAudioContext' in window)) {
      missing.push('AudioContext')
    }
    
    if (!('AudioWorklet' in window)) {
      missing.push('AudioWorklet')
    }
    
    if (!('mediaDevices' in navigator)) {
      missing.push('MediaDevices')
    }
    
    if (navigator.mediaDevices && !('getUserMedia' in navigator.mediaDevices)) {
      missing.push('getUserMedia')
    }
    
    return {
      supported: missing.length === 0,
      missing
    }
  }
  
  /**
   * Get available audio input devices
   */
  static async getAudioInputDevices(): Promise<DeviceInfo[]> {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices()
      return devices
        .filter(device => device.kind === 'audioinput')
        .map(device => ({
          deviceId: device.deviceId,
          label: device.label || `Microphone ${device.deviceId.slice(0, 8)}`,
          kind: device.kind,
          groupId: device.groupId
        }))
    } catch (error) {
      console.error('Failed to enumerate devices:', error)
      return []
    }
  }
  
  /**
   * Check microphone permissions
   */
  static async checkMicrophonePermission(): Promise<PermissionState> {
    try {
      const result = await navigator.permissions.query({ name: 'microphone' as PermissionName })
      return result.state
    } catch (error) {
      // Fallback: try to get user media
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
        stream.getTracks().forEach(track => track.stop())
        return 'granted'
      } catch {
        return 'denied'
      }
    }
  }
  
  /**
   * Create audio level monitor
   */
  createLevelMonitor(context: AudioContext, source: AudioNode): void {
    this.analyser = context.createAnalyser()
    this.analyser.fftSize = 256
    this.dataArray = new Uint8Array(this.analyser.frequencyBinCount)
    source.connect(this.analyser)
  }
  
  /**
   * Get current audio levels
   */
  getAudioLevels(): AudioLevelInfo | null {
    if (!this.analyser || !this.dataArray) {
      return null
    }
    
    this.analyser.getByteFrequencyData(this.dataArray)
    
    let sum = 0
    let peak = 0
    
    for (let i = 0; i < this.dataArray.length; i++) {
      const value = this.dataArray[i]
      sum += value
      if (value > peak) {
        peak = value
      }
    }
    
    const average = sum / this.dataArray.length
    const instant = this.dataArray[0] // Use first bin as instant level
    
    return {
      instant: instant / 255,
      average: average / 255,
      peak: peak / 255
    }
  }
  
  /**
   * Cleanup level monitor
   */
  cleanup(): void {
    if (this.analyser) {
      this.analyser.disconnect()
      this.analyser = null
    }
    this.dataArray = null
  }
  
  /**
   * Save audio blob for debugging
   */
  static downloadAudioBlob(blob: Blob, filename?: string): void {
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename || `audio-debug-${Date.now()}.wav`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }
  
  /**
   * Log audio blob information
   */
  static logBlobInfo(blob: Blob, label = 'Audio Blob'): void {
    console.group(label)
    console.log('Size:', blob.size, 'bytes')
    console.log('Type:', blob.type)
    console.log('Duration estimate:', (blob.size / 96000).toFixed(2), 'seconds (at 48kHz mono)')
    console.groupEnd()
  }
  
  /**
   * Create diagnostic report
   */
  static async createDiagnosticReport(): Promise<string> {
    const report: string[] = ['Audio Diagnostic Report', '=' * 30, '']
    
    // Browser support
    const support = this.checkBrowserSupport()
    report.push('Browser Support:')
    report.push(`  Supported: ${support.supported}`)
    if (!support.supported) {
      report.push(`  Missing: ${support.missing.join(', ')}`)
    }
    report.push('')
    
    // Permissions
    const permission = await this.checkMicrophonePermission()
    report.push('Microphone Permission:')
    report.push(`  Status: ${permission}`)
    report.push('')
    
    // Audio devices
    const devices = await this.getAudioInputDevices()
    report.push('Audio Input Devices:')
    if (devices.length === 0) {
      report.push('  No devices found')
    } else {
      devices.forEach((device, index) => {
        report.push(`  ${index + 1}. ${device.label}`)
        report.push(`     ID: ${device.deviceId}`)
        report.push(`     Group: ${device.groupId}`)
      })
    }
    report.push('')
    
    // Browser info
    report.push('Browser Information:')
    report.push(`  User Agent: ${navigator.userAgent}`)
    report.push(`  Platform: ${navigator.platform}`)
    report.push('')
    
    // Timestamp
    report.push(`Generated: ${new Date().toISOString()}`)
    
    return report.join('\n')
  }
  
  /**
   * Monitor audio processing performance
   */
  static createPerformanceMonitor() {
    const marks: Map<string, number> = new Map()
    const measures: Map<string, number[]> = new Map()
    
    return {
      mark(name: string) {
        marks.set(name, performance.now())
      },
      
      measure(name: string, startMark: string, endMark?: string) {
        const start = marks.get(startMark)
        if (!start) return
        
        const end = endMark ? marks.get(endMark) : performance.now()
        if (!end) return
        
        const duration = end - start
        
        if (!measures.has(name)) {
          measures.set(name, [])
        }
        measures.get(name)!.push(duration)
      },
      
      getStats(name: string) {
        const values = measures.get(name)
        if (!values || values.length === 0) return null
        
        const sorted = [...values].sort((a, b) => a - b)
        const sum = values.reduce((a, b) => a + b, 0)
        
        return {
          count: values.length,
          min: sorted[0],
          max: sorted[sorted.length - 1],
          avg: sum / values.length,
          median: sorted[Math.floor(sorted.length / 2)],
          p95: sorted[Math.floor(sorted.length * 0.95)],
          p99: sorted[Math.floor(sorted.length * 0.99)]
        }
      },
      
      logStats() {
        console.group('Audio Performance Stats')
        measures.forEach((values, name) => {
          const stats = this.getStats(name)
          if (stats) {
            console.group(name)
            console.log(`Count: ${stats.count}`)
            console.log(`Min: ${stats.min.toFixed(2)}ms`)
            console.log(`Max: ${stats.max.toFixed(2)}ms`)
            console.log(`Avg: ${stats.avg.toFixed(2)}ms`)
            console.log(`Median: ${stats.median.toFixed(2)}ms`)
            console.log(`P95: ${stats.p95.toFixed(2)}ms`)
            console.log(`P99: ${stats.p99.toFixed(2)}ms`)
            console.groupEnd()
          }
        })
        console.groupEnd()
      },
      
      reset() {
        marks.clear()
        measures.clear()
      }
    }
  }
}

/**
 * Console utilities for debugging
 */
export const audioDebugConsole = {
  /**
   * Log with audio debug prefix
   */
  log(...args: any[]) {
    console.log('[Audio Debug]', ...args)
  },
  
  /**
   * Error with audio debug prefix
   */
  error(...args: any[]) {
    console.error('[Audio Debug]', ...args)
  },
  
  /**
   * Create a logger with custom prefix
   */
  createLogger(prefix: string) {
    return {
      log: (...args: any[]) => console.log(`[Audio Debug: ${prefix}]`, ...args),
      error: (...args: any[]) => console.error(`[Audio Debug: ${prefix}]`, ...args),
      warn: (...args: any[]) => console.warn(`[Audio Debug: ${prefix}]`, ...args),
      info: (...args: any[]) => console.info(`[Audio Debug: ${prefix}]`, ...args)
    }
  }
}

// Export convenience function for quick diagnostics
export async function runAudioDiagnostics(): Promise<void> {
  const report = await AudioDebugger.createDiagnosticReport()
  console.log(report)
}