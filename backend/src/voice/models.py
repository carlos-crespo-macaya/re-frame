"""Pydantic models for voice endpoints."""

from typing import Literal

from pydantic import BaseModel


class CreateVoiceSessionRequest(BaseModel):
    """Request to create a new voice session."""

    language: str = "en-US"


class VoiceSessionResponse(BaseModel):
    """Response after creating a voice session."""

    session_id: str
    status: Literal["created", "active", "ended"]
    language: str


class AudioChunkRequest(BaseModel):
    """Audio chunk to be processed."""

    data: str  # base64 encoded PCM audio
    timestamp: int
    sample_rate: int = 48000  # Audio sample rate (default 48kHz)


class VoiceControlRequest(BaseModel):
    """Control commands for voice session."""

    action: Literal["end_turn", "cancel", "end_session"]


class VoiceStreamMessage(BaseModel):
    """Message format for SSE stream."""

    type: Literal["audio", "transcript", "turn_complete", "error"]
    data: str | None = None
    text: str | None = None
    is_final: bool | None = None
    interrupted: bool | None = None
    error: str | None = None
