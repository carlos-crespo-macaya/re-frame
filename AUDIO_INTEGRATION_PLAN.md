# Audio Integration Plan for re-frame.social

## Overview

This document outlines the requirements and implementation plan to add real-time audio streaming capabilities to re-frame.social, similar to the ADK-SSE-streaming project. This would allow users to speak their thoughts instead of (or in addition to) typing them.

## User Experience Enhancements

### 1. UI Modifications
Add to the existing thought input form:
- **Microphone button**: Next to the text area for voice input
- **Audio indicator**: Visual feedback when recording/speaking
- **Mode toggle**: Switch between text and voice input
- **Audio playback controls**: For listening to AI responses

### 2. Interaction Flow
```
Current: Type thought → Submit → Read response
Enhanced: Speak thought → Real-time transcription → Submit → Hear/Read response
```

## Technical Requirements

### Frontend Components Needed

#### 1. Audio Infrastructure (`/lib/audio/`)
```
lib/audio/
├── audio-recorder.ts      # Microphone recording setup
├── audio-player.ts        # Audio playback setup
├── audio-worklets/
│   ├── pcm-recorder.ts    # Recording worklet
│   └── pcm-player.ts      # Playback worklet
└── audio-utils.ts         # Encoding/decoding utilities
```

#### 2. SSE Client (`/lib/streaming/`)
```
lib/streaming/
├── sse-client.ts          # SSE connection management
├── message-protocol.ts    # Message type definitions
└── session-manager.ts     # Session ID handling
```

#### 3. Updated Components
```
components/forms/
├── ThoughtInputForm.tsx   # Add audio recording UI
└── AudioControls.tsx      # New component for audio UI

components/ui/
├── AudioVisualizer.tsx    # Waveform/level indicator
├── RecordButton.tsx       # Microphone button with states
└── PlaybackControls.tsx   # Audio response controls
```

### Implementation Details

#### 1. Message Protocol Extension
```typescript
interface ReframeMessage {
  mime_type: "text/plain" | "audio/pcm";
  data: string;  // text or base64 audio
  message_type: "thought" | "response" | "transcription";
  session_id: string;
  turn_complete?: boolean;
  interrupted?: boolean;
}
```

#### 2. Audio Configuration
```typescript
const AUDIO_CONFIG = {
  recording: {
    sampleRate: 16000,
    channels: 1,
    bitDepth: 16,
    bufferInterval: 200  // ms
  },
  playback: {
    sampleRate: 24000,
    channels: 1,
    bufferSize: 180  // seconds
  }
};
```

#### 3. State Management
```typescript
interface AudioState {
  isRecording: boolean;
  isPlaying: boolean;
  audioEnabled: boolean;
  micPermission: 'granted' | 'denied' | 'prompt';
  transcription: string;
  audioLevel: number;
}
```

### Backend Requirements

1. **SSE Endpoint**: `/api/events/{sessionId}`
2. **Message Endpoint**: `/api/send/{sessionId}`
3. **Audio Processing**:
   - PCM audio decoding
   - Speech-to-text integration
   - Text-to-speech for responses
4. **Session Management**: Track audio/text mode per session

### Key Features to Implement

#### 1. Core Audio Features
- [x] Microphone permission handling
- [x] Real-time audio streaming
- [x] PCM audio encoding/decoding
- [x] Audio worklet implementation
- [x] Ring buffer for playback

#### 2. User Experience
- [x] Visual recording indicator
- [x] Audio level visualization
- [x] Interruption handling
- [x] Error recovery
- [x] Fallback to text mode

#### 3. Accessibility
- [x] Keyboard shortcuts for recording
- [x] Screen reader announcements
- [x] Visual indicators for audio events
- [x] Captions for audio responses

### Integration Steps

1. **Phase 1: Infrastructure**
   - Set up WebAudio contexts
   - Implement audio worklets
   - Create SSE client
   - Add session management

2. **Phase 2: UI Components**
   - Add microphone button to form
   - Implement recording indicators
   - Create audio visualizer
   - Add playback controls

3. **Phase 3: Integration**
   - Connect audio to existing form
   - Handle mode switching
   - Implement transcription display
   - Add audio response playback

4. **Phase 4: Polish**
   - Error handling
   - Performance optimization
   - Cross-browser testing
   - Accessibility testing

### Security Considerations

1. **HTTPS Required**: Microphone access requires secure context
2. **Permission Management**: Graceful handling of denied permissions
3. **Data Privacy**: 
   - Audio data should follow same privacy rules as text
   - No audio storage without consent
   - Clear indicators when recording

### Performance Optimization

1. **Lazy Loading**: Load audio components only when needed
2. **Worker Threads**: Use AudioWorklets for processing
3. **Efficient Encoding**: Consider compression for bandwidth
4. **Buffer Management**: Prevent memory leaks with proper cleanup

### Testing Requirements

1. **Unit Tests**:
   - Audio utilities
   - SSE client
   - Message handling

2. **Integration Tests**:
   - Recording flow
   - Playback flow
   - Mode switching

3. **E2E Tests**:
   - Full audio conversation flow
   - Error scenarios
   - Permission handling

### Accessibility Enhancements

1. **For AvPD Users**:
   - Option to review/edit transcription before sending
   - Adjustable recording delay
   - Non-intimidating UI design
   - Clear consent and control

2. **General Accessibility**:
   - Keyboard-only operation
   - Screen reader support
   - Visual alternatives to audio
   - Customizable audio settings

### Estimated Implementation Time

- Infrastructure setup: 2-3 days
- UI components: 2-3 days
- Integration: 3-4 days
- Testing & polish: 2-3 days
- **Total: 9-13 days**

### Additional Considerations

1. **Progressive Enhancement**: Text input remains primary, audio is optional
2. **Mobile Support**: Test on various mobile browsers
3. **Bandwidth**: Monitor and optimize data usage
4. **Latency**: Keep audio delays under 300ms
5. **Fallbacks**: Graceful degradation if audio fails

This enhancement would make re-frame.social more accessible to users who find speaking easier than typing, while maintaining the calm, supportive environment essential for the target audience.