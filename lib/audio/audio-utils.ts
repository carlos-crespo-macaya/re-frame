/**
 * Utility functions for audio processing and management
 */

/**
 * Convert ArrayBuffer to base64 string
 */
export function arrayBufferToBase64(buffer: ArrayBuffer): string {
  let binary = '';
  const bytes = new Uint8Array(buffer);
  const len = bytes.byteLength;
  
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  
  return btoa(binary);
}

/**
 * Convert base64 string to ArrayBuffer
 */
export function base64ToArrayBuffer(base64: string): ArrayBuffer {
  const binaryString = atob(base64);
  const len = binaryString.length;
  const bytes = new Uint8Array(len);
  
  for (let i = 0; i < len; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  
  return bytes.buffer;
}

/**
 * Convert Float32Array to 16-bit PCM
 */
export function float32ToPcm16(float32Array: Float32Array): Int16Array {
  const pcm16 = new Int16Array(float32Array.length);
  
  for (let i = 0; i < float32Array.length; i++) {
    // Clamp to [-1, 1] range
    const clamped = Math.max(-1, Math.min(1, float32Array[i]));
    
    // Convert to 16-bit PCM
    // Handle negative values correctly to get full -32768 range
    if (clamped < 0) {
      pcm16[i] = Math.round(clamped * 32768);
    } else {
      pcm16[i] = Math.round(clamped * 32767);
    }
  }
  
  return pcm16;
}

/**
 * Convert 16-bit PCM to Float32Array
 */
export function pcm16ToFloat32(pcm16Array: Int16Array): Float32Array {
  const float32 = new Float32Array(pcm16Array.length);
  
  for (let i = 0; i < pcm16Array.length; i++) {
    float32[i] = pcm16Array[i] / 32768;
  }
  
  return float32;
}

/**
 * Generate a unique session ID
 */
export function generateSessionId(): string {
  const segments = [8, 4, 4, 4, 12];
  const chars = '0123456789abcdef';
  let result = '';
  
  for (let i = 0; i < segments.length; i++) {
    if (i > 0) result += '-';
    
    for (let j = 0; j < segments[i]; j++) {
      result += chars[Math.floor(Math.random() * chars.length)];
    }
  }
  
  return result;
}

/**
 * Calculate RMS audio level from samples
 * @returns Level between 0 and 1
 */
export function calculateAudioLevel(samples: Float32Array): number {
  if (samples.length === 0) return 0;
  
  let sum = 0;
  for (let i = 0; i < samples.length; i++) {
    sum += samples[i] * samples[i];
  }
  
  const rms = Math.sqrt(sum / samples.length);
  return Math.min(1, rms);
}

/**
 * Format duration in milliseconds to mm:ss
 */
export function formatDuration(ms: number): string {
  if (ms < 0) ms = 0;
  
  const seconds = Math.floor(ms / 1000);
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

/**
 * Debounce function calls
 */
export function debounce<T extends (...args: any[]) => any>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delay);
  };
}

/**
 * Throttle function calls
 */
export function throttle<T extends (...args: any[]) => any>(
  fn: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle = false;
  
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      fn(...args);
      inThrottle = true;
      setTimeout(() => {
        inThrottle = false;
      }, limit);
    }
  };
}

/**
 * Check if browser supports required audio features
 */
export function isAudioSupported(): boolean {
  if (typeof window === 'undefined') return false;
  
  return !!(
    ((window as any).AudioContext || (window as any).webkitAudioContext) &&
    typeof navigator !== 'undefined' &&
    navigator.mediaDevices &&
    navigator.mediaDevices.getUserMedia
  );
}

/**
 * Get audio constraints for getUserMedia
 */
export function getAudioConstraints(sampleRate: number = 16000): MediaStreamConstraints {
  return {
    audio: {
      channelCount: 1,
      sampleRate,
      echoCancellation: true,
      noiseSuppression: true,
      autoGainControl: true
    },
    video: false
  };
}

/**
 * Check detailed audio support in the browser
 */
export function checkAudioSupport(): {
  audioContext: boolean;
  audioWorklet: boolean;
  getUserMedia: boolean;
} {
  if (typeof window === 'undefined') {
    return {
      audioContext: false,
      audioWorklet: false,
      getUserMedia: false
    };
  }
  
  const AudioContextClass = (window as any).AudioContext || (window as any).webkitAudioContext;
  const hasAudioContext = !!AudioContextClass;
  const hasAudioWorklet = hasAudioContext && AudioContextClass.prototype && 'audioWorklet' in AudioContextClass.prototype;
  const hasGetUserMedia = !!(navigator?.mediaDevices?.getUserMedia);
  
  return {
    audioContext: hasAudioContext,
    audioWorklet: hasAudioWorklet,
    getUserMedia: hasGetUserMedia
  };
}