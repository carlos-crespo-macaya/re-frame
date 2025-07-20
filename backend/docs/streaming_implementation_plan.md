# Voice Mode Streaming Implementation Plan

## Overview
Implement separate endpoints for text and voice modes to provide optimal user experience for each modality.

## Current State
- **Text Mode**: `/api/events/{session_id}` (SSE) + `/api/send/{session_id}` (POST)
  - ✅ Working well with request-response pattern
  - ✅ Good for typing-based interactions
  
- **Voice Mode**: Same endpoints as text mode
  - ❌ Using request-response for audio chunks (not ideal)
  - ❌ No real-time bidirectional streaming
  - ❌ Higher latency due to chunking

## Proposed Architecture

### 1. Text Mode (Keep As Is)
- **Endpoint**: `/api/events/{session_id}`
- **Method**: GET (SSE)
- **Send Messages**: `/api/send/{session_id}` (POST)
- **Pattern**: Traditional SSE + REST
- **Why**: Works well for text, no changes needed

### 2. Voice Mode (New Implementation)
- **Endpoint**: `/api/voice/stream/{session_id}`
- **Method**: WebSocket
- **Pattern**: ADK's `run_async_stream` with bidirectional streaming
- **Why**: Real-time audio streaming, lower latency, natural conversation flow

## Implementation Steps

### Phase 1: Create WebSocket Infrastructure
1. Add WebSocket endpoint `/api/voice/stream/{session_id}`
2. Implement WebSocket connection handler
3. Create audio stream manager class

### Phase 2: Integrate ADK Streaming
1. Use ADK's `run_async_stream` instead of `run_async`
2. Create async generators for client→agent and agent→client streams
3. Handle audio format conversion in real-time

### Phase 3: Frontend Updates
1. Update `use-natural-conversation.ts` to use WebSocket
2. Remove audio buffering (stream directly)
3. Handle WebSocket lifecycle (connect/disconnect/reconnect)

## Code Structure

```
backend/src/
├── streaming/
│   ├── __init__.py
│   ├── voice_stream_handler.py    # WebSocket handler for voice
│   ├── audio_stream_manager.py    # Manages bidirectional audio streams
│   └── stream_protocols.py        # Message formats for streaming
├── main.py                        # Add new WebSocket route
└── utils/
    └── speech_to_text.py         # Remove (STT handled by ADK in streaming)
```

## API Design

### Text Mode Endpoints (No Changes)
```
GET  /api/events/{session_id}?language=en-US
POST /api/send/{session_id}
```

### Voice Mode Endpoints (New)
```
WS   /api/voice/stream/{session_id}?language=en-US
```

### WebSocket Message Format

**Client → Server (Audio)**
```json
{
  "type": "audio",
  "data": "base64_encoded_pcm_audio"
}
```

**Client → Server (Control)**
```json
{
  "type": "control",
  "action": "end_turn" | "cancel" | "ping"
}
```

**Server → Client (Audio)**
```json
{
  "type": "audio",
  "data": "base64_encoded_pcm_audio"
}
```

**Server → Client (Transcript)**
```json
{
  "type": "transcript",
  "text": "What the user said",
  "is_final": true
}
```

**Server → Client (Control)**
```json
{
  "type": "turn_complete",
  "interrupted": false
}
```

## Benefits of Separation

1. **Performance**: Each mode optimized for its use case
2. **Clarity**: Clear separation of concerns
3. **Maintainability**: Easier to debug and enhance each mode
4. **User Experience**: 
   - Text: Traditional request-response feel
   - Voice: Real-time conversational experience

## Migration Strategy

1. Keep existing endpoints working (backward compatibility)
2. Implement new voice endpoints alongside
3. Update frontend to detect mode and use appropriate endpoint
4. Deprecate audio support in old endpoints after migration

## Testing Plan

1. Unit tests for WebSocket handlers
2. Integration tests for ADK streaming
3. End-to-end tests for full voice conversation flow
4. Performance tests comparing old vs new approach

## Success Metrics

- Voice latency < 200ms (vs current ~1-2s)
- Smooth bidirectional conversation
- No audio buffering delays
- Natural interruption handling