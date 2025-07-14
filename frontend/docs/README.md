# Frontend Audio Documentation

This directory contains comprehensive documentation for the audio system in re-frame.social.

## Documentation Contents

### 📋 [Audio Format Specification](./AUDIO_FORMAT_SPECIFICATION.md)
Complete technical specification of audio formats used throughout the application:
- Recording format (48kHz WAV)
- Transmission format (Base64 encoded)
- Playback format (24kHz PCM)
- Audio flow diagrams
- Performance considerations

### 🔧 [Audio Troubleshooting Guide](./AUDIO_TROUBLESHOOTING_GUIDE.md)
Step-by-step guide for diagnosing and resolving audio issues:
- Common problems and solutions
- Debug commands and utilities
- Performance optimization tips
- Network debugging
- Support resources

### 🌐 [Browser Compatibility Matrix](./BROWSER_COMPATIBILITY.md)
Detailed browser support information:
- Feature support matrix
- Minimum browser versions
- Known browser-specific issues
- Polyfills and fallbacks
- Testing recommendations

## Quick Start

### For Developers

1. **Understanding the Audio Pipeline**
   - Read the [Audio Format Specification](./AUDIO_FORMAT_SPECIFICATION.md) to understand how audio flows through the system
   - Review the audio flow diagram to see the complete pipeline

2. **Debugging Audio Issues**
   - Import and run diagnostics:
     ```javascript
     import { runAudioDiagnostics } from '@/lib/audio/audio-debug'
     await runAudioDiagnostics()
     ```
   - Follow the [Troubleshooting Guide](./AUDIO_TROUBLESHOOTING_GUIDE.md) for specific issues

3. **Browser Testing**
   - Check the [Compatibility Matrix](./BROWSER_COMPATIBILITY.md) for supported browsers
   - Use feature detection before initializing audio

### For QA/Testing

1. **Test Coverage**
   - Test in all Tier 1 browsers (Chrome 90+, Firefox 90+, Safari 15+, Edge 90+)
   - Verify mobile support on iOS Safari 14.5+ and Android Chrome latest
   - Use the manual testing checklist in the compatibility guide

2. **Common Test Scenarios**
   - Microphone permission flows
   - Recording and playback quality
   - Network interruption handling
   - Browser-specific edge cases

## Key Technical Details

### Recording Pipeline
```
Microphone (48kHz) → Noise Gate → Recorder → WAV Encoder → Base64 → Backend
```

### Playback Pipeline
```
Backend (24kHz PCM) → Base64 Decode → AudioBuffer → Web Audio API → Speakers
```

### Critical Requirements
- **AudioWorklet API**: Required for recording (Chrome 66+, Firefox 76+, Safari 14.1+)
- **getUserMedia**: Required for microphone access
- **Web Audio API**: Core requirement for all audio processing

## Audio Debug Utilities

The `audio-debug.ts` module provides comprehensive debugging tools:

```javascript
import { AudioDebugger, audioDebugConsole } from '@/lib/audio/audio-debug'

// Check browser support
const support = AudioDebugger.checkBrowserSupport()

// Monitor audio levels
const debugger = new AudioDebugger()
debugger.createLevelMonitor(context, source)

// Create diagnostic report
const report = await AudioDebugger.createDiagnosticReport()
console.log(report)

// Performance monitoring
const perfMonitor = AudioDebugger.createPerformanceMonitor()
perfMonitor.mark('operation-start')
// ... perform operation ...
perfMonitor.mark('operation-end')
perfMonitor.measure('operation-time', 'operation-start', 'operation-end')
perfMonitor.logStats()
```

## Known Issues

1. **Safari iOS**: Requires iOS 14.5+ for AudioWorklet support
2. **Mobile Sample Rates**: Some devices may not support 48kHz natively
3. **Firefox Latency**: Higher processing latency compared to Chrome
4. **Autoplay Policies**: All browsers require user interaction to start audio

## Updates and Maintenance

When updating the audio system:
1. Update the format specification if audio formats change
2. Add new issues and solutions to the troubleshooting guide
3. Update browser compatibility when new versions are tested
4. Keep debug utilities in sync with implementation

## Related Files

- `/lib/audio/audio-recorder.ts` - Main recording implementation
- `/lib/audio/audio-config.ts` - Audio configuration
- `/lib/audio/audio-debug.ts` - Debug utilities
- `/lib/streaming/message-protocol.ts` - Message format definitions
- `/public/worklets/` - AudioWorklet processors

## Support

For audio-related issues:
1. Run diagnostics using the debug utilities
2. Check the troubleshooting guide
3. Verify browser compatibility
4. Generate a diagnostic report for support tickets