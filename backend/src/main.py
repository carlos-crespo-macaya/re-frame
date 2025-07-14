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
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from google.adk.agents.live_request_queue import LiveRequestQueue
from google.adk.agents.run_config import RunConfig
from google.adk.runners import InMemoryRunner
from google.genai.types import Blob, Content, Part, SpeechConfig

# Import CBT assistant instead of search agent
from agents.cbt_assistant import create_cbt_assistant
from utils.audio_converter import AudioConverter
from utils.session_manager import session_manager

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

#
# ADK Streaming
#

# Load Gemini API Key
load_dotenv()

APP_NAME = "CBT Reframing Assistant"


async def start_agent_session(user_id, is_audio=False):
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
        speech_config=SpeechConfig(language_code="es-ES"),
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
        "http://frontend:3000",  # Docker service name
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
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


@app.get("/")
async def root():
    """Serves the index.html or API info"""
    index_path = Path(STATIC_DIR) / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "CBT Assistant API", "docs": "/docs", "health": "/health"}


@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run"""
    return {
        "status": "healthy",
        "service": "cbt-assistant-api",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": ENVIRONMENT,
    }


@app.get("/api/events/{session_id}")
async def sse_endpoint(session_id: str, is_audio: str = "false"):
    """SSE endpoint for agent to client communication"""

    # Start agent session
    # Use session_id as user_id for ADK
    live_events, live_request_queue = await start_agent_session(
        session_id, is_audio == "true"
    )

    # Store the session with session manager
    session_manager.create_session(
        session_id=session_id,
        user_id=session_id,  # Using session_id as user_id for POC
        request_queue=live_request_queue,
    )

    print(f"Client session {session_id} connected via SSE, audio mode: {is_audio}")

    def cleanup():
        session_manager.remove_session(session_id)
        print(f"Client session {session_id} disconnected from SSE")

    async def event_generator():
        try:
            # Send initial connection event
            yield f"data: {json.dumps({'type': 'connected', 'session_id': session_id})}\n\n"

            async for data in agent_to_client_sse(live_events):
                yield data
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
        },
    )


@app.post("/api/send/{session_id}")
async def send_message_endpoint(session_id: str, request: Request):
    """HTTP endpoint for client to agent communication"""

    # Get the session from session manager
    session = session_manager.get_session(session_id)
    if not session or not session.request_queue:
        return {"error": "Session not found"}

    live_request_queue = session.request_queue

    # Parse the message
    message = await request.json()
    mime_type = message["mime_type"]
    data = message["data"]

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
        # Convert audio to PCM format
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
            return {"error": f"Audio conversion failed: {metrics['error']}"}

        if not pcm_data:
            return {"error": "Audio conversion resulted in empty data"}

        # Validate PCM data
        if not AudioConverter.validate_pcm_data(pcm_data):
            return {"error": "Invalid PCM data after conversion"}

        # Send converted PCM to agent
        live_request_queue.send_realtime(Blob(data=pcm_data, mime_type="audio/pcm"))
        print(f"[CLIENT TO AGENT]: converted audio/pcm: {len(pcm_data)} bytes")
    else:
        return {"error": f"Mime type not supported: {mime_type}"}

    return {"status": "sent"}


@app.get("/api/session/{session_id}")
async def get_session_info(session_id: str):
    """Get session information for debugging."""
    session = session_manager.get_session_readonly(session_id)
    if not session:
        return {"error": "Session not found"}

    return {
        "session_id": session.session_id,
        "user_id": session.user_id,
        "created_at": session.created_at,
        "last_activity": session.last_activity,
        "age_seconds": session.age_seconds,
        "inactive_seconds": session.inactive_seconds,
        "has_request_queue": session.request_queue is not None,
    }


@app.get("/api/sessions")
async def list_sessions():
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

    return {
        "total_sessions": session_manager.get_active_session_count(),
        "sessions": sessions,
    }


@app.get("/api/pdf/{session_id}")
async def download_pdf(session_id: str):
    """Download PDF summary for a session - minimal implementation for local testing"""
    from datetime import datetime

    # For POC, return a simple text file as PDF
    # In production, this would use pdf_generator utility
    pdf_content = f"""Session Summary
==================
Session ID: {session_id}
Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

This is a mock PDF for local testing.
In production, this would contain:
- Session transcript
- Key insights identified
- Reframed perspectives
- Resources mentioned

Thank you for using re-frame.
""".encode()

    return Response(
        content=pdf_content,
        media_type="text/plain",  # Using text/plain for POC
        headers={
            "Content-Disposition": f"attachment; filename=session-summary-{session_id}.txt",
            "Content-Type": "text/plain",
        },
    )


@app.post("/api/language/detect")
async def detect_language(request: Request):
    """Detect language from user input"""
    # TODO: Implement language detection using the language_detection utility
    # For now, return a placeholder response
    data = await request.json()
    return {
        "status": "not_implemented",
        "message": "Language detection will be implemented in Epic 1",
        "text": data.get("text", ""),
    }
