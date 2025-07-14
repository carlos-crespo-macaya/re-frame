# Audio Troubleshooting Guide

This guide helps diagnose and resolve common audio issues in re-frame.social.

## Quick Diagnostics

Run the built-in diagnostics in the browser console:
```javascript
import { runAudioDiagnostics } from '@/lib/audio/audio-debug'
await runAudioDiagnostics()
```

## Common Issues

### 1. No Microphone Input

#### Symptoms
- Recording button doesn't work
- No audio levels shown
- Error: "Microphone access denied"

#### Solutions

**Check Browser Permissions**
1. Click the lock icon in the address bar
2. Ensure microphone access is "Allow"
3. Reload the page

**Verify Device Connection**
```javascript
// Check available devices
const devices = await navigator.mediaDevices.enumerateDevices()
const mics = devices.filter(d => d.kind === 'audioinput')
console.log('Available microphones:', mics)
```

**Reset Permissions**
- Chrome: `chrome://settings/content/microphone`
- Firefox: `about:preferences#privacy`
- Safari: System Preferences > Security & Privacy > Microphone

### 2. Audio Context Suspended

#### Symptoms
- Recording appears to start but no audio captured
- Console shows: "AudioContext state: suspended"

#### Solutions

**Resume Context on User Interaction**
```javascript
// Add to recording start button handler
if (audioContext.state === 'suspended') {
  await audioContext.resume()
  console.log('AudioContext resumed')
}
```

**Check Context State**
```javascript
console.log('Current state:', audioContext.state)
console.log('Sample rate:', audioContext.sampleRate)
console.log('Base latency:', audioContext.baseLatency)
```

### 3. AudioWorklet Loading Failures

#### Symptoms
- Error: "Failed to load audio module"
- Recording doesn't initialize
- Console shows 404 errors for worklet files

#### Solutions

**Verify File Paths**
1. Check that worklet files exist in `/public/worklets/`
2. Ensure correct MIME type for JS files
3. Check for CORS issues if using CDN

**Debug Loading**
```javascript
try {
  await audioContext.audioWorklet.addModule('/worklets/audio-recorder-processor.js')
  console.log('Worklet loaded successfully')
} catch (error) {
  console.error('Worklet loading failed:', error)
  // Check network tab for actual error
}
```

**Fallback for Older Browsers**
```javascript
if (!('AudioWorklet' in window)) {
  console.warn('AudioWorklet not supported, using ScriptProcessorNode')
  // Implement fallback recording
}
```

### 4. Poor Audio Quality

#### Symptoms
- Choppy or distorted audio
- Background noise
- Echo or feedback

#### Solutions

**Optimize Media Constraints**
```javascript
const constraints = {
  audio: {
    echoCancellation: true,
    noiseSuppression: true,
    autoGainControl: true,
    sampleRate: 48000,
    channelCount: 1
  }
}
```

**Adjust Noise Gate Threshold**
```javascript
// Increase threshold for noisy environments
recorder.setNoiseGateThreshold(-40) // Default: -50dB
```

**Monitor Audio Levels**
```javascript
import { AudioDebugger } from '@/lib/audio/audio-debug'

const debugger = new AudioDebugger()
debugger.createLevelMonitor(audioContext, sourceNode)

// Check levels periodically
setInterval(() => {
  const levels = debugger.getAudioLevels()
  console.log('Audio levels:', levels)
}, 100)
```

### 5. Recording Size Issues

#### Symptoms
- Large file sizes
- Upload failures
- Memory warnings

#### Solutions

**Monitor Recording Duration**
```javascript
const MAX_DURATION = 5 * 60 * 1000 // 5 minutes

setTimeout(() => {
  if (recorder.recording) {
    recorder.stop()
    console.warn('Maximum recording duration reached')
  }
}, MAX_DURATION)
```

**Estimate File Size**
```javascript
// Calculate approximate size
const durationSeconds = recordingTime / 1000
const sampleRate = 48000
const bytesPerSample = 2 // 16-bit
const channels = 1
const expectedSize = durationSeconds * sampleRate * bytesPerSample * channels
console.log('Expected file size:', (expectedSize / 1024 / 1024).toFixed(2), 'MB')
```

### 6. Playback Issues

#### Symptoms
- No audio playback
- Distorted playback
- Playback at wrong speed

#### Solutions

**Verify Audio Format**
```javascript
// Check received audio data
console.log('Playback sample rate:', audioData.sampleRate)
console.log('Expected rate:', 24000)

// Create correct AudioBuffer
const audioBuffer = audioContext.createBuffer(
  1,               // channels
  audioData.length,// frame count
  24000           // sample rate (must match backend)
)
```

**Debug Playback Pipeline**
```javascript
// Log each step
console.log('1. Received base64 data:', data.substring(0, 50) + '...')
console.log('2. Decoded array length:', decodedArray.length)
console.log('3. AudioBuffer duration:', audioBuffer.duration)
console.log('4. Playing audio...')
```

### 7. Browser-Specific Issues

#### Safari/iOS
- **Issue**: AudioWorklet may not be available
- **Solution**: Check version (requires Safari 14.1+/iOS 14.5+)
- **Workaround**: Use ScriptProcessorNode fallback

#### Mobile Chrome
- **Issue**: Different default sample rates
- **Solution**: Always specify explicit sample rate
- **Note**: May require user gesture to start

#### Firefox
- **Issue**: Stricter autoplay policies
- **Solution**: Ensure user interaction before audio playback

## Performance Optimization

### Monitor Processing Time
```javascript
import { AudioDebugger } from '@/lib/audio/audio-debug'

const perfMonitor = AudioDebugger.createPerformanceMonitor()

// Mark recording start
perfMonitor.mark('record-start')

// ... recording happens ...

// Mark recording end
perfMonitor.mark('record-end')
perfMonitor.measure('recording-duration', 'record-start', 'record-end')

// View statistics
perfMonitor.logStats()
```

### Memory Management
```javascript
// Clean up after recording
recorder.cleanup()

// Revoke object URLs
URL.revokeObjectURL(audioUrl)

// Clear large arrays
recordedChunks = []
```

## Debug Commands

### Console Commands for Testing

```javascript
// 1. Test microphone access
(async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    console.log('✓ Microphone access granted')
    stream.getTracks().forEach(track => track.stop())
  } catch (e) {
    console.error('✗ Microphone access denied:', e)
  }
})()

// 2. Test AudioContext
(() => {
  const ctx = new AudioContext()
  console.log('AudioContext state:', ctx.state)
  console.log('Sample rate:', ctx.sampleRate)
  ctx.close()
})()

// 3. Test AudioWorklet support
console.log('AudioWorklet supported:', 'AudioWorklet' in window)

// 4. List all audio devices
navigator.mediaDevices.enumerateDevices().then(devices => {
  console.table(devices.filter(d => d.kind === 'audioinput'))
})

// 5. Download last recording
window.debugDownloadLastRecording = (blob) => {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `debug-recording-${Date.now()}.wav`
  a.click()
}
```

## Logging Best Practices

### Enable Verbose Logging
```javascript
// Add to development environment
if (process.env.NODE_ENV === 'development') {
  window.AUDIO_DEBUG = true
}

// In audio code
if (window.AUDIO_DEBUG) {
  console.log('[Audio]', 'Starting recording...')
}
```

### Structured Logging
```javascript
const audioLogger = {
  info: (message, data = {}) => {
    console.log(`[Audio ${new Date().toISOString()}] ${message}`, data)
  },
  error: (message, error) => {
    console.error(`[Audio ERROR ${new Date().toISOString()}] ${message}`, error)
  }
}
```

## Network Debugging

### Monitor SSE Connection
```javascript
// Log all SSE messages
eventSource.onmessage = (event) => {
  console.log('[SSE]', event.data)
  // Process message...
}

eventSource.onerror = (error) => {
  console.error('[SSE Error]', error)
}
```

### Track Message Sizes
```javascript
// Log base64 audio size
const audioSize = base64Data.length * 0.75 // Approximate decoded size
console.log('Audio message size:', (audioSize / 1024).toFixed(2), 'KB')
```

## When All Else Fails

1. **Clear Browser Data**
   - Clear site data including permissions
   - Restart browser

2. **Test in Incognito/Private Mode**
   - Eliminates extension conflicts
   - Fresh permission state

3. **Try Different Browser**
   - Test in Chrome, Firefox, Safari
   - Note any browser-specific issues

4. **Check System Audio**
   - Verify microphone works in other apps
   - Check system audio settings
   - Restart audio services if needed

5. **Generate Diagnostic Report**
   ```javascript
   import { AudioDebugger } from '@/lib/audio/audio-debug'
   const report = await AudioDebugger.createDiagnosticReport()
   console.log(report)
   // Copy report for support ticket
   ```

## Support Resources

- Check browser console for errors
- Enable verbose logging in development
- Use audio debugging utilities
- Test with example audio files
- Compare with working demo environment