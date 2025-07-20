# Voice Mode Implementation Plan (Final)

## Overview
Complete replacement of the non-functional voice mode with a new implementation using separate endpoints and ADK streaming.

## Approach
- **Remove all current voice-related code**
- **Implement new voice endpoints from scratch**
- **No backwards compatibility needed**
- **No performance comparisons**

## Implementation

### 1. Remove Current Voice Code

#### Files/Code to Remove:
- `/backend/src/utils/speech_to_text.py` - Delete entirely
- In `/backend/src/main.py`:
  - Remove `is_audio` parameter from SSE endpoint
  - Remove audio handling in `send_message_endpoint`
  - Remove voice configuration in `start_agent_session`
  - Remove all audio/pcm processing code

#### Keep:
- Text mode endpoints (working fine)
- `/backend/src/utils/audio_converter.py` (might be useful for format conversion)

### 2. New Voice Architecture

#### Endpoints:
```
POST /api/voice/sessions                          - Create voice session
POST /api/voice/sessions/{session_id}/audio      - Send audio chunk
GET  /api/voice/sessions/{session_id}/stream     - SSE for responses  
POST /api/voice/sessions/{session_id}/control    - Control commands
```

#### File Structure:
```
backend/src/
├── voice/
│   ├── __init__.py
│   ├── models.py           # Pydantic models for voice endpoints
│   ├── session_manager.py  # Voice session management
│   ├── stream_handler.py   # ADK streaming integration
│   └── router.py          # FastAPI router for voice endpoints
```

### 3. Models

```python
# voice/models.py
from pydantic import BaseModel
from typing import Literal

class CreateVoiceSessionRequest(BaseModel):
    language: str = "en-US"

class VoiceSessionResponse(BaseModel):
    session_id: str
    status: Literal["created", "active", "ended"]
    language: str

class AudioChunkRequest(BaseModel):
    data: str  # base64 encoded PCM audio
    timestamp: int

class VoiceControlRequest(BaseModel):
    action: Literal["end_turn", "cancel", "end_session"]
```

### 4. Voice Router

```python
# voice/router.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/api/voice", tags=["voice"])

@router.post("/sessions", response_model=VoiceSessionResponse)
async def create_voice_session(request: CreateVoiceSessionRequest):
    """Create a new voice session with ADK streaming."""
    # Implementation here

@router.post("/sessions/{session_id}/audio")
async def send_audio_chunk(session_id: str, audio: AudioChunkRequest):
    """Send audio chunk to active voice session."""
    # Implementation here

@router.get("/sessions/{session_id}/stream")
async def voice_stream(session_id: str):
    """SSE endpoint for voice responses."""
    # Return StreamingResponse with ADK audio stream

@router.post("/sessions/{session_id}/control")
async def voice_control(session_id: str, control: VoiceControlRequest):
    """Send control commands to voice session."""
    # Implementation here
```

### 5. Frontend Changes

Update `use-natural-conversation.ts`:
- Remove all current audio sending logic
- Use new generated client methods:
  ```typescript
  // Create session
  const session = await ApiClient.createVoiceSession({ language })
  
  // Setup SSE
  const eventSource = REDACTED(session.sessionId)
  
  // Send audio chunks
  await ApiClient.sendAudioChunk(session.sessionId, {
    data: base64Audio,
    timestamp: Date.now()
  })
  ```

### 6. Main.py Updates

```python
# In main.py - just add the router
from src.voice.router import router as voice_router

app.include_router(voice_router)

# Remove all is_audio related code from existing endpoints
```

## Implementation Order

1. **Clean up** - Remove all current voice code
2. **Create voice module** - New clean implementation
3. **Update OpenAPI** - Add new endpoints
4. **Regenerate client** - `pnpm run generate:api`
5. **Update frontend** - Use new client methods

## No Legacy Support

- Text mode: `/api/events/{id}` + `/api/send/{id}` (unchanged)
- Voice mode: `/api/voice/*` endpoints (completely new)
- No shared code between modes
- No migration needed - just switch to new endpoints

## Benefits

1. **Clean separation** - Voice and text are completely independent
2. **Proper streaming** - ADK streaming for real-time audio
3. **Type safety** - Full OpenAPI/TypeScript support
4. **Maintainable** - Clear, focused implementation