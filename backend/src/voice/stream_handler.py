"""Stream handler for ADK voice integration."""

import asyncio
import base64
import logging
from collections.abc import AsyncGenerator

from src.voice.models import VoiceStreamMessage
from src.voice.session_manager import VoiceSession

logger = logging.getLogger(__name__)


async def create_voice_stream(session: VoiceSession) -> AsyncGenerator[str, None]:
    """Create SSE stream for voice session responses."""

    # Send initial connected message
    msg = VoiceStreamMessage(type="turn_complete", data="connected")
    yield f"data: {msg.model_dump_json()}\n\n"

    # Stream events from agent queue
    while session.status == "active":
        try:
            # Get event from agent queue
            event = await session.agent_queue.get()

            # Handle different event types
            if isinstance(event, dict) and event.get("type") == "error":
                msg = VoiceStreamMessage(
                    type="error", error=event.get("error", "Unknown error")
                )
                yield f"data: {msg.model_dump_json()}\n\n"
                break

            # Handle ADK events
            if hasattr(event, "content") and event.content:
                content = event.content

                # Check for audio response
                if hasattr(content, "parts") and content.parts:
                    for part in content.parts:
                        if hasattr(part, "inline_data") and part.inline_data:
                            mime_type = getattr(part.inline_data, "mime_type", "")

                            if mime_type.startswith("audio/"):
                                # Send audio data
                                audio_data = part.inline_data.data
                                if audio_data:
                                    msg = VoiceStreamMessage(
                                        type="audio",
                                        data=base64.b64encode(audio_data).decode(
                                            "ascii"
                                        ),
                                    )
                                    yield f"data: {msg.model_dump_json()}\n\n"

                        elif hasattr(part, "text") and part.text:
                            # Send text (transcript or response)
                            msg = VoiceStreamMessage(
                                type="transcript",
                                text=part.text,
                                is_final=not getattr(event, "partial", False),
                            )
                            yield f"data: {msg.model_dump_json()}\n\n"

            # Handle turn complete
            if hasattr(event, "turn_complete") and event.turn_complete:
                msg = VoiceStreamMessage(
                    type="turn_complete",
                    interrupted=getattr(event, "interrupted", False),
                )
                yield f"data: {msg.model_dump_json()}\n\n"

        except asyncio.CancelledError:
            # Handle cancellation gracefully
            logger.info(f"Voice stream cancelled for session {session.session_id}")
            msg = VoiceStreamMessage(type="turn_complete", data="stream_cancelled")
            yield f"data: {msg.model_dump_json()}\n\n"
            break
        except Exception as e:
            logger.error(f"Error in voice stream: {e}")
            # Provide more specific error messages
            error_msg = str(e)
            if "1007" in error_msg:
                error_msg = "Audio format error. Please check audio encoding."
            elif "WebSocket" in error_msg:
                error_msg = "Connection error. Please try again."

            msg = VoiceStreamMessage(type="error", error=error_msg)
            yield f"data: {msg.model_dump_json()}\n\n"
            break

    # Send final message if session ended
    if session.status == "ended":
        msg = VoiceStreamMessage(type="turn_complete", data="session_ended")
        yield f"data: {msg.model_dump_json()}\n\n"
