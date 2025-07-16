# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import base64
import json
import os
import warnings
from datetime import UTC, datetime
import asyncio
from typing import Optional
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
# Google ADK (Agent Development Kit) is an optional dependency. Attempt to
# import it, but gracefully degrade when it's unavailable so local development
# without the proprietary SDK still works and the remainder of the service can
# be started (e.g. for unit-tests that mock the ADK layer).

try:
    from google.adk.agents.live_request_queue import LiveRequestQueue  # type: ignore
    from google.adk.agents.run_config import RunConfig  # type: ignore
    from google.adk.runners import InMemoryRunner  # type: ignore
    from google.genai.types import Blob, Content, Part, SpeechConfig  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    # Provide extremely lightweight stand-ins so that type-checking and run-time
    # references do not fail.  These stubs purposefully implement only the
    # minimal surface area used by this application.

    class _Stub:
        def __init__(self, *_, **__):
            pass

        def __getattr__(self, _name):
            # Return a no-op callable for any attribute access.
            return lambda *_, **__: None

        # Support usage as an async iterator (e.g. for live event streams)
        def __aiter__(self):  # noqa: D401 – minimal stub
            return self

        async def __anext__(self):  # noqa: D401 – minimal stub
            raise StopAsyncIteration

    LiveRequestQueue = _Stub  # type: ignore
    RunConfig = _Stub  # type: ignore
    InMemoryRunner = _Stub  # type: ignore

    class _Blob(_Stub):
        def __init__(self, data=None, mime_type=None):
            self.data = data
            self.mime_type = mime_type

    Blob = _Blob  # type: ignore

    class _Content(_Stub):
        def __init__(self, role=None, parts=None):
            self.role = role
            self.parts = parts or []

    Content = _Content  # type: ignore

    class _Part(_Stub):
        def __init__(self, text: str | None = None):
            self.text = text
            self.inline_data = None

        @staticmethod
        def from_text(text: str):  # type: ignore
            return _Part(text)

    Part = _Part  # type: ignore

    class _SpeechConfig(_Stub):
        def __init__(self, language_code=None):
            self.language_code = language_code

    SpeechConfig = _SpeechConfig  # type: ignore

# Import CBT assistant instead of search agent
from src.agents.cbt_assistant import create_cbt_assistant
from src.models import (
    HealthCheckResponse,
    LanguageDetectionRequest,
    LanguageDetectionResponse,
    MessageRequest,
    MessageResponse,
    SessionInfo,
    SessionListResponse,
)
from src.utils.audio_converter import AudioConverter
from src.utils.session_manager import session_manager

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

#
# ADK Streaming
#

# Load Gemini API Key
load_dotenv()

APP_NAME = "CBT Reframing Assistant"


async def start_agent_session(user_id, is_audio=False, language_code="en-US"):
    """Starts an agent session"""

    # Create the CBT assistant agent
    cbt_agent = create_cbt_assistant()

    # Create a Runner
    runner = InMemoryRunner(
        app_name=APP_NAME,
        agent=cbt_agent,
    )

    # Create a Session
    session = await runner.session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,  # Replace with actual user ID
    )

    # Set response modality
    modality = "AUDIO" if is_audio else "TEXT"
    run_config = RunConfig(
        response_modalities=[modality],
        speech_config=SpeechConfig(language_code=language_code),
    )

    # Create a LiveRequestQueue for this session
    live_request_queue = LiveRequestQueue()

    # Start agent session
    live_events = runner.run_live(
        session=session,
        live_request_queue=live_request_queue,
        run_config=run_config,
    )
    return live_events, live_request_queue


async def agent_to_client_sse(live_events):
    """Agent to client communication via SSE"""
    async for event in live_events:
        # If the turn complete or interrupted, send it
        if event.turn_complete or event.interrupted:
            message = {
                "turn_complete": event.turn_complete,
                "interrupted": event.interrupted,
            }
            yield f"data: {json.dumps(message)}\n\n"
            print(f"[AGENT TO CLIENT]: {message}")
            continue

        # Read the Content and its first Part
        part: Part = event.content and event.content.parts and event.content.parts[0]
        if not part:
            continue

        # If it's audio, send Base64 encoded audio data
        is_audio = part.inline_data and part.inline_data.mime_type.startswith(
            "audio/pcm"
        )
        if is_audio:
            audio_data = part.inline_data and part.inline_data.data
            if audio_data:
                message = {
                    "mime_type": "audio/pcm",
                    "data": base64.b64encode(audio_data).decode("ascii"),
                }
                yield f"data: {json.dumps(message)}\n\n"
                print(f"[AGENT TO CLIENT]: audio/pcm: {len(audio_data)} bytes.")
                continue

        # If it's text and a parial text, send it
        if part.text and event.partial:
            message = {"mime_type": "text/plain", "data": part.text}
            yield f"data: {json.dumps(message)}\n\n"
            print(f"[AGENT TO CLIENT]: text/plain: {message}")


#
# FastAPI web app
#

app = FastAPI(
    title="CBT Reframing Assistant API",
    description="Cognitive Behavioral Therapy assistant powered by Google's ADK",
    version="1.0.0",
)

# Local micro-routers (websocket chat & ASR enhancement).  We import lazily
# here to avoid circular-import issues during test discovery.
from src.routers import asr, websocket  # noqa: E402  pylint: disable=wrong-import-position

app.include_router(asr.router, prefix="/api/v1")
app.include_router(websocket.router, prefix="/api/v1")

# Configure CORS based on environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
if ENVIRONMENT == "production":
    allowed_origins = [
        "https://re-frame.social",
        "https://www.re-frame.social",
        "https://cbt-assistant-web-*.run.app",  # Cloud Run URLs
    ]
else:
    allowed_origins = [
        "http://localhost:3000",  # Frontend dev server
        "http://127.0.0.1:3000",  # Alternative localhost
        "http://frontend:3000",  # Docker service name
        "null",  # file:// URLs used when opening debug-sse.html directly
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,  # No cookies or auth headers required for SSE/API
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Session-Id", "X-Phase-Status"],
)

STATIC_DIR = Path("static")
# Only mount static files if the directory exists
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Session manager will handle active sessions
# active_sessions = {}  # Replaced by session_manager


@app.on_event("startup")
async def startup_event():
    """Start background tasks on startup."""
    await session_manager.start()


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown."""
    await session_manager.stop()


@app.get("/", summary="Root endpoint", operation_id="getRoot")
async def root():
    """Serves the index.html or API info"""
    index_path = Path(STATIC_DIR) / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "CBT Assistant API", "docs": "/docs", "health": "/health"}


@app.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Health check",
    operation_id="getHealthCheck",
)
async def health_check() -> HealthCheckResponse:
    """Health check endpoint for Cloud Run"""
    return HealthCheckResponse(
        status="healthy",
        service="CBT Reframing Assistant API",
        version="1.0.0",
        timestamp=datetime.now(UTC).isoformat(),
    )


@app.get(
    "/api/events/{session_id}", summary="SSE endpoint", operation_id="getEventStream"
)
async def sse_endpoint(
    session_id: str, is_audio: bool = False, language: str = "en-US"
):
    """SSE endpoint for agent to client communication"""

    # Start agent session
    # Use session_id as user_id for ADK
    live_events, live_request_queue = await start_agent_session(
        session_id, is_audio, language
    )

    # Store the session with session manager
    session_info = session_manager.create_session(
        session_id=session_id,
        user_id=session_id,  # Using session_id as user_id for POC
        request_queue=live_request_queue,
    )
    session_info.metadata["language"] = language

    print(f"Client session {session_id} connected via SSE, audio mode: {is_audio}")

    def cleanup():
        session_manager.remove_session(session_id)
        print(f"Client session {session_id} disconnected from SSE")

    async def event_generator():
        try:
            # Send initial connection event
            yield f"data: {json.dumps({'type': 'connected', 'session_id': session_id})}\n\n"

            # Forward all agent events to the client
            async for data in agent_to_client_sse(live_events):
                yield data

            # If the agent event stream finishes (e.g. before the user sends
            # the first request) keep the SSE connection open so that the same
            # connection can still be used once requests start flowing.  We
            # periodically emit an SSE comment line as a heartbeat to prevent
            # proxies from timing-out the idle connection.
            while True:
                # SSE comment lines start with ':' and are ignored by the
                # browser EventSource but keep the HTTP stream alive.
                yield ": keep-alive\n\n"
                # A moderate heartbeat interval (15s) is more than enough to
                # avoid the common 30s idle-timeout on many reverse proxies
                # while still being infrequent so it will not create undue
                # traffic.
                await asyncio.sleep(15)
        except Exception as e:
            print(f"Error in SSE stream: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        finally:
            cleanup()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable proxy buffering
            # Starlette's CORSMiddleware fails to append CORS headers to
            # streaming responses.  We therefore add the header explicitly so
            # that browsers allow EventSource connections even when the page
            # is served from file:// (origin "null") or other allowed origins.
            # For development we echo back the Origin header value when it is
            # present, otherwise we fall back to "*" so that file:// (origin
            # "null") requests are permitted.  We also explicitly disable
            # credentials on this streaming response because EventSource does
            # not send cookies by default.
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "false",
        },
    )


@app.post(
    "/api/send/{session_id}",
    response_model=MessageResponse,
    summary="Send message",
    operation_id="sendMessage",
)
async def send_message_endpoint(
    session_id: str, message: MessageRequest
) -> MessageResponse:
    """HTTP endpoint for client to agent communication"""

    # Get the session from session manager
    session = session_manager.get_session(session_id)
    if not session or not session.request_queue:
        raise HTTPException(status_code=404, detail="Session not found")

    live_request_queue = session.request_queue

    # Parse the message
    mime_type = message.mime_type
    data = message.data

    # Send the message to the agent
    if mime_type == "text/plain":
        content = Content(role="user", parts=[Part.from_text(text=data)])
        live_request_queue.send_content(content=content)
        print(f"[CLIENT TO AGENT]: {data}")
    elif mime_type == "audio/pcm":
        decoded_data = base64.b64decode(data)
        live_request_queue.send_realtime(Blob(data=decoded_data, mime_type=mime_type))
        print(f"[CLIENT TO AGENT]: audio/pcm: {len(decoded_data)} bytes")
    elif mime_type in AudioConverter.SUPPORTED_INPUT_FORMATS:
        # For now, we need to properly convert audio to PCM
        # ADK only accepts audio/pcm format
        if mime_type == "audio/webm":
            # WebM conversion is not implemented yet
            raise HTTPException(
                status_code=501,
                detail="WebM audio conversion is not implemented. Please use WAV format or send PCM directly.",
            )
        else:
            # Convert other audio formats to PCM
            decoded_data = base64.b64decode(data)
            pcm_data, metrics = AudioConverter.convert_to_pcm(decoded_data, mime_type)

            # Log conversion metrics
            print(
                f"[AUDIO CONVERSION]: {mime_type} -> PCM in {metrics['conversion_time']:.1f}ms"
            )
            print(
                f"[AUDIO CONVERSION]: {metrics['input_size']} -> {metrics['output_size']} bytes"
            )

            if metrics.get("error"):
                raise HTTPException(
                    status_code=422,
                    detail=f"Audio conversion failed: {metrics['error']}",
                )

            if not pcm_data:
                raise HTTPException(
                    status_code=422, detail="Audio conversion resulted in empty data"
                )

            # Validate PCM data
            if not AudioConverter.validate_pcm_data(pcm_data):
                raise HTTPException(
                    status_code=422, detail="Invalid PCM data after conversion"
                )

            # Send converted PCM to agent
            live_request_queue.send_realtime(Blob(data=pcm_data, mime_type="audio/pcm"))
            print(f"[CLIENT TO AGENT]: converted audio/pcm: {len(pcm_data)} bytes")
    else:
        raise HTTPException(
            status_code=415, detail=f"Mime type not supported: {mime_type}"
        )

    return MessageResponse(status="sent", error=None)


@app.get(
    "/api/session/{session_id}",
    response_model=SessionInfo,
    summary="Get session info",
    operation_id="getSessionInfo",
)
async def get_session_info(session_id: str) -> SessionInfo:
    """Get session information for debugging."""
    session = session_manager.get_session_readonly(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return SessionInfo(
        session_id=session.session_id,
        user_id=session.user_id,
        created_at=datetime.fromtimestamp(session.created_at, tz=UTC).isoformat(),
        last_activity=datetime.fromtimestamp(session.last_activity, tz=UTC).isoformat(),
        age_seconds=session.age_seconds,
        inactive_seconds=session.inactive_seconds,
        has_request_queue=session.request_queue is not None,
        metadata=session.metadata if hasattr(session, "metadata") else None,
    )


@app.get(
    "/api/sessions",
    response_model=SessionListResponse,
    summary="List all sessions",
    operation_id="listSessions",
)
async def list_sessions() -> SessionListResponse:
    """List all active sessions for debugging."""
    sessions = []
    for session_id, session in session_manager.sessions.items():
        sessions.append(
            {
                "session_id": session_id,
                "age_seconds": session.age_seconds,
                "inactive_seconds": session.inactive_seconds,
            }
        )

    return SessionListResponse(
        total_sessions=session_manager.get_active_session_count(),
        sessions=sessions,
    )


@app.get("/api/pdf/{session_id}", summary="Download PDF", operation_id="downloadPdf")
async def download_pdf(session_id: str):
    """Download PDF summary for a session - minimal implementation for local testing"""
    from datetime import datetime

    # For POC, return a simple text file as PDF
    # In production, this would use pdf_generator utility
    pdf_content = f"""Session Summary
==================
Session ID: {session_id}
Date: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M UTC')}

This is a mock PDF for local testing.
In production, this would contain:
- Session transcript
- Key insights identified
- Reframed perspectives
- Resources mentioned

Thank you for using CBT Assistant.
""".encode()

    return Response(
        content=b"Mock PDF content for " + pdf_content,  # Mock PDF binary content
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="reframe-summary-{session_id}.pdf"',
        },
    )


@app.post(
    "/api/language/detect",
    response_model=LanguageDetectionResponse,
    summary="Detect language",
    operation_id="detectLanguage",
)
async def detect_language(
    request: LanguageDetectionRequest,
) -> LanguageDetectionResponse:
    """Detect language from user input"""
    # TODO: Implement language detection using the language_detection utility
    # For now, return a placeholder response
    return LanguageDetectionResponse(
        status="not_implemented",
        message="Language detection will be implemented in Epic 1",
        language=None,
        confidence=None,
    )
