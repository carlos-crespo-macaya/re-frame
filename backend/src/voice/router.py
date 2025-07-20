"""FastAPI router for voice endpoints."""

import base64
import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from src.voice.models import (
    AudioChunkRequest,
    CreateVoiceSessionRequest,
    VoiceControlRequest,
    VoiceSessionResponse,
)
from src.voice.session_manager import voice_session_manager
from src.voice.stream_handler import create_voice_stream

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/voice", tags=["voice"])


@router.post("/sessions", response_model=VoiceSessionResponse)
async def create_voice_session(
    request: CreateVoiceSessionRequest,
) -> VoiceSessionResponse:
    """Create a new voice session with ADK streaming."""
    try:
        session = await voice_session_manager.create_session(request.language)

        return VoiceSessionResponse(
            session_id=session.session_id,
            status=session.status,  # type: ignore
            language=session.language,
        )
    except Exception as e:
        logger.error("Failed to create voice session: %s", str(e))
        raise HTTPException(
            status_code=500, detail="Failed to create voice session"
        ) from e


@router.post("/sessions/{session_id}/audio")
async def send_audio_chunk(session_id: str, audio: AudioChunkRequest):
    """Send audio chunk to active voice session."""
    session = voice_session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status != "active":
        raise HTTPException(status_code=400, detail="Session is not active")

    try:
        # Decode base64 audio
        audio_data = base64.b64decode(audio.data)

        # Send to ADK with sample rate
        await session.send_audio(audio_data, audio.sample_rate)

        return {"status": "received"}
    except Exception as e:
        logger.error("Failed to process audio chunk: %s", str(e))
        raise HTTPException(status_code=500, detail="Failed to process audio") from e


@router.get("/sessions/{session_id}/stream")
async def voice_stream(session_id: str):
    """SSE endpoint for voice responses."""
    session = voice_session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return StreamingResponse(
        create_voice_stream(session),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/sessions/{session_id}/control")
async def voice_control(session_id: str, control: VoiceControlRequest):
    """Send control commands to voice session."""
    session = voice_session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        await session.send_control(control.action)
        return {"status": "ok", "action": control.action}
    except Exception as e:
        logger.error("Failed to process control command: %s", str(e))
        raise HTTPException(
            status_code=500, detail="Failed to process control command"
        ) from e


@router.delete("/sessions/{session_id}")
async def end_voice_session(session_id: str):
    """End a voice session."""
    session = voice_session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    await voice_session_manager.remove_session(session_id)
    return {"status": "ended"}
