# Browser Compatibility Matrix

This document details browser support for audio features in re-frame.social.

## Compatibility Overview

| Feature | Chrome | Edge | Firefox | Safari | Safari iOS | Chrome Android |
|---------|--------|------|---------|--------|------------|----------------|
| **Core Support** |
| Web Audio API | ✅ 10+ | ✅ 79+ | ✅ 25+ | ✅ 6+ | ✅ 6+ | ✅ 28+ |
| AudioContext | ✅ 35+ | ✅ 79+ | ✅ 25+ | ✅ 14.1+ | ✅ 14.5+ | ✅ 35+ |
| AudioWorklet | ✅ 66+ | ✅ 79+ | ✅ 76+ | ✅ 14.1+ | ✅ 14.5+ | ✅ 66+ |
| getUserMedia | ✅ 21+ | ✅ 79+ | ✅ 17+ | ✅ 11+ | ✅ 11+ | ✅ 21+ |
| **Recording** |
| MediaRecorder | ✅ 47+ | ✅ 79+ | ✅ 25+ | ✅ 14.1+ | ✅ 14.5+ | ✅ 47+ |
| 48kHz Support | ✅ | ✅ | ✅ | ✅ | ⚠️ | ⚠️ |
| Noise Gate | ✅ 66+ | ✅ 79+ | ✅ 76+ | ✅ 14.1+ | ✅ 14.5+ | ✅ 66+ |
| **Playback** |
| 24kHz PCM | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Streaming | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Constraints** |
| Echo Cancel | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Noise Suppress | ✅ | ✅ | ✅ | ✅ | ⚠️ | ✅ |
| Auto Gain | ✅ | ✅ | ✅ | ✅ | ⚠️ | ✅ |

**Legend:**
- ✅ Fully supported
- ⚠️ Partial support or requires workaround
- ❌ Not supported
- Version numbers indicate minimum required version

## Detailed Browser Requirements

### Desktop Browsers

#### Chrome/Chromium (66+)
- **Recommended**: Version 90+
- Full AudioWorklet support since v66
- Excellent WebRTC implementation
- Best performance for audio processing

#### Edge (79+)
- **Recommended**: Latest version
- Chromium-based versions only
- Same engine as Chrome
- Full feature parity with Chrome

#### Firefox (76+)
- **Recommended**: Version 90+
- AudioWorklet support added in v76
- Good WebRTC support
- May have higher latency than Chrome

#### Safari (14.1+)
- **Recommended**: Version 15+
- AudioWorklet support added in 14.1
- Requires user gesture for audio
- More restrictive autoplay policies

### Mobile Browsers

#### Safari iOS (14.5+)
- **Critical**: iOS 14.5+ required for AudioWorklet
- Requires user interaction to start AudioContext
- May downsample high sample rates
- Limited background audio support

#### Chrome Android (66+)
- **Recommended**: Latest version
- Full feature support
- Variable performance across devices
- May have different default sample rates

## Feature Detection

### Required Features Check
```javascript
function checkBrowserCompatibility() {
  const required = {
    audioContext: 'AudioContext' in window || 'webkitAudioContext' in window,
    audioWorklet: 'AudioWorklet' in window,
    getUserMedia: navigator.mediaDevices && 'getUserMedia' in navigator.mediaDevices,
    mediaRecorder: 'MediaRecorder' in window
  }
  
  const missing = Object.entries(required)
    .filter(([feature, supported]) => !supported)
    .map(([feature]) => feature)
  
  return {
    compatible: missing.length === 0,
    missing,
    required
  }
}
```

### Progressive Enhancement
```javascript
async function initializeAudio() {
  // Check for AudioWorklet support
  if ('AudioWorklet' in window) {
    // Use modern AudioWorklet approach
    await context.audioWorklet.addModule('/worklets/processor.js')
  } else {
    // Fallback to ScriptProcessorNode (deprecated)
    console.warn('Using deprecated ScriptProcessorNode')
    // Implement fallback...
  }
}
```

## Known Browser Issues

### Safari/WebKit Issues

1. **AudioWorklet Module Loading**
   - Issue: Strict CORS requirements
   - Solution: Ensure worklet files served with correct headers
   ```javascript
   // Headers required for Safari
   'Content-Type: application/javascript'
   'Access-Control-Allow-Origin: *'
   ```

2. **Sample Rate Limitations**
   - Issue: May not support all sample rates
   - Solution: Let browser choose default
   ```javascript
   // Don't specify sample rate on Safari
   const context = new AudioContext()
   console.log('Actual sample rate:', context.sampleRate)
   ```

3. **Autoplay Restrictions**
   - Issue: Requires user gesture
   - Solution: Start audio on user interaction
   ```javascript
   button.addEventListener('click', async () => {
     if (context.state === 'suspended') {
       await context.resume()
     }
   })
   ```

### Firefox Issues

1. **AudioWorklet Performance**
   - Issue: Higher latency than Chrome
   - Solution: Use larger buffer sizes
   ```javascript
   // Increase buffer for Firefox
   const isFirefox = navigator.userAgent.includes('Firefox')
   const bufferSize = isFirefox ? 512 : 256
   ```

2. **Permission Prompts**
   - Issue: More aggressive permission prompts
   - Solution: Clear user communication

### Mobile-Specific Issues

1. **iOS Audio Interruptions**
   - Issue: Phone calls pause audio
   - Solution: Handle visibility/focus events
   ```javascript
   document.addEventListener('visibilitychange', () => {
     if (document.hidden) {
       // Pause audio
     } else {
       // Resume audio
     }
   })
   ```

2. **Android Sample Rate Variety**
   - Issue: Devices have different native rates
   - Solution: Always resample if needed
   ```javascript
   // Check actual vs desired sample rate
   if (context.sampleRate !== 48000) {
     console.warn('Resampling required:', context.sampleRate)
   }
   ```

## Polyfills and Fallbacks

### AudioContext Polyfill
```javascript
window.AudioContext = window.AudioContext || window.webkitAudioContext

if (!window.AudioContext) {
  throw new Error('Web Audio API not supported')
}
```

### MediaDevices Polyfill
```javascript
if (!navigator.mediaDevices) {
  navigator.mediaDevices = {}
}

if (!navigator.mediaDevices.getUserMedia) {
  navigator.mediaDevices.getUserMedia = function(constraints) {
    const getUserMedia = navigator.getUserMedia ||
                        navigator.webkitGetUserMedia ||
                        navigator.mozGetUserMedia ||
                        navigator.msGetUserMedia
    
    if (!getUserMedia) {
      return Promise.reject(new Error('getUserMedia not supported'))
    }
    
    return new Promise((resolve, reject) => {
      getUserMedia.call(navigator, constraints, resolve, reject)
    })
  }
}
```

### ScriptProcessorNode Fallback
```javascript
class AudioWorkletPolyfill {
  constructor(context, processorName) {
    // Use ScriptProcessorNode as fallback
    this.processor = context.createScriptProcessor(4096, 1, 1)
    this.processor.onaudioprocess = this.process.bind(this)
  }
  
  process(event) {
    // Simplified processing
    const input = event.inputBuffer.getChannelData(0)
    const output = event.outputBuffer.getChannelData(0)
    output.set(input)
  }
  
  connect(destination) {
    this.processor.connect(destination)
  }
  
  disconnect() {
    this.processor.disconnect()
  }
}
```

## Testing Recommendations

### Manual Testing Checklist
- [ ] Test in Chrome (latest)
- [ ] Test in Firefox (latest)
- [ ] Test in Safari (latest)
- [ ] Test in Edge (latest)
- [ ] Test on iOS Safari
- [ ] Test on Android Chrome
- [ ] Test with slow network
- [ ] Test with background tabs

### Automated Testing
```javascript
// Feature detection tests
describe('Browser Compatibility', () => {
  test('has required APIs', () => {
    expect(window.AudioContext).toBeDefined()
    expect(window.AudioWorklet).toBeDefined()
    expect(navigator.mediaDevices).toBeDefined()
  })
  
  test('can create audio context', () => {
    const context = new AudioContext()
    expect(context.state).toBe('suspended')
    context.close()
  })
})
```

## Support Strategy

### Tier 1 (Full Support)
- Chrome 90+
- Edge 90+
- Firefox 90+
- Safari 15+

### Tier 2 (Basic Support)
- Chrome 66-89
- Firefox 76-89
- Safari 14.1-14.x
- Mobile browsers (latest versions)

### Tier 3 (Degraded Experience)
- Browsers without AudioWorklet
- Older mobile browsers
- Provide text-only fallback

## Future Considerations

### Upcoming Features
- WebCodecs API for better compression
- WebTransport for lower latency
- SharedArrayBuffer for better performance
- Native noise suppression APIs

### Deprecation Timeline
- ScriptProcessorNode: Deprecated, avoid use
- webkitAudioContext: Use standard AudioContext
- Legacy getUserMedia: Use mediaDevices.getUserMedia