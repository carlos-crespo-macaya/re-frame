/**
 * Audio simulation helpers for E2E testing
 */

/**
 * Set up audio simulation capabilities on the window object
 * This allows E2E tests to simulate audio input without requiring actual microphone access
 */
interface TestWindow extends Window {
  simulateAudioInput?: (base64Audio: string) => Promise<void>
}

export function setupAudioSimulation(window: Window) {
  // Add simulateAudioInput function to window for E2E tests
  (window as TestWindow).simulateAudioInput = async (base64Audio: string) => {
    // Decode base64 audio data
    const audioData = atob(base64Audio)
    const audioArray = new Uint8Array(audioData.length)
    for (let i = 0; i < audioData.length; i++) {
      audioArray[i] = audioData.charCodeAt(i)
    }
    
    // Dispatch custom event with audio data for testing
    window.dispatchEvent(new CustomEvent('test-audio-input', {
      detail: { audioData: audioArray }
    }))
  }
}