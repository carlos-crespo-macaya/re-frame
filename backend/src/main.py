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

import asyncio
import base64
import json
import os
import warnings
from datetime import UTC, datetime
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from google.adk.agents.run_config import RunConfig
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part, SpeechConfig

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
from src.utils.logging import (
    get_logger,
    log_agent_event,
    log_session_event,
    setup_logging,
)
from src.utils.session_manager import session_manager

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

# Set up logging
setup_logging(log_level=os.getenv("LOG_LEVEL", "INFO"))
logger = get_logger(__name__)

#
# ADK Streaming
#

# Load Gemini API Key
load_dotenv()
logger.info("application_started", app_name="CBT Reframing Assistant")

APP_NAME = "CBT Reframing Assistant"


async def start_agent_session(user_id, is_audio=False, language_code="en-US"):
    """Starts an agent session"""
    logger.info(
        "agent_session_starting",
        user_id=user_id,
        is_audio=is_audio,
        language_code=language_code,
    )

    # Create the CBT assistant agent with language support
    cbt_agent = create_cbt_assistant(language_code=language_code)
    logger.debug("cbt_agent_created", agent_name=cbt_agent.name)

    # Create a Runner
    runner = InMemoryRunner(
        app_name=APP_NAME,
        agent=cbt_agent,
    )
    logger.debug("runner_created", app_name=APP_NAME)

    # Create a Session
    session = await runner.session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,  # Replace with actual user ID
    )
    logger.info("adk_session_created", session=str(session), user_id=user_id)

    # Set response modality
    modality = "AUDIO" if is_audio else "TEXT"
    run_config = RunConfig(
        response_modalities=[modality],
        speech_config=SpeechConfig(language_code=language_code),
    )

    # Return runner, session, and run_config for later use
    return runner, session, run_config


async def process_message(runner, session, message_content, run_config):
    """Process a single message using run_async"""
    logger.info("processing_message", session=str(session))

    # Use run_async for request-response pattern
    events = []
    async for event in runner.run_async(
        user_id=session.user_id,
        session_id=session.id,
        new_message=message_content,
        run_config=run_config,
    ):
        events.append(event)

    logger.info("message_processed", session=str(session), event_count=len(events))
    return events


async def agent_to_client_sse(live_events):
    """Agent to client communication via SSE"""
    async for event in live_events:
        logger.debug(
            "agent_event_received",
            event_type=type(event).__name__,
            has_content=hasattr(event, "content") and event.content is not None,
            has_turn_complete=hasattr(event, "turn_complete"),
            has_interrupted=hasattr(event, "interrupted"),
            has_partial=hasattr(event, "partial"),
        )

        # Check if this is the final event with turn_complete
        is_turn_complete = hasattr(event, "turn_complete") and event.turn_complete

        # Only send turn_complete if there's no content (it's a standalone turn complete event)
        if is_turn_complete and not (hasattr(event, "content") and event.content):
            message = {
                "turn_complete": True,
                "interrupted": getattr(event, "interrupted", False),
            }
            yield f"data: {json.dumps(message)}\n\n"
            log_agent_event(
                logger,
                "turn_complete",
                turn_complete=True,
                interrupted=getattr(event, "interrupted", False),
            )
            continue

        # Read the Content and its first Part
        if hasattr(event, "content") and event.content:
            logger.debug(
                "event_has_content",
                content_role=getattr(event.content, "role", None),
                parts_count=(
                    len(event.content.parts) if hasattr(event.content, "parts") else 0
                ),
            )

            if hasattr(event.content, "parts") and event.content.parts:
                part = event.content.parts[0]

                # If it's audio, send Base64 encoded audio data
                if (
                    hasattr(part, "inline_data")
                    and part.inline_data
                    and hasattr(part.inline_data, "mime_type")
                ):
                    is_audio = part.inline_data.mime_type.startswith("audio/pcm")
                    if is_audio and hasattr(part.inline_data, "data"):
                        audio_data = part.inline_data.data
                        if audio_data:
                            message = {
                                "mime_type": "audio/pcm",
                                "data": base64.b64encode(audio_data).decode("ascii"),
                            }
                            yield f"data: {json.dumps(message)}\n\n"
                            log_agent_event(
                                logger,
                                "audio_sent",
                                mime_type="audio/pcm",
                                size_bytes=len(audio_data),
                            )
                            continue

                # If it's text, send it (remove partial check for now)
                if hasattr(part, "text") and part.text:
                    logger.debug("part_has_text", text_preview=part.text[:100])
                    message = {"mime_type": "text/plain", "data": part.text}
                    yield f"data: {json.dumps(message)}\n\n"
                    log_agent_event(
                        logger,
                        "text_sent",
                        mime_type="text/plain",
                        text=part.text,
                        is_partial=getattr(event, "partial", False),
                    )

                    # If this event also has turn_complete, send that too
                    if is_turn_complete:
                        logger.debug(
                            "sending_turn_complete_after_content",
                            is_turn_complete=is_turn_complete,
                        )
                        message = {
                            "turn_complete": True,
                            "interrupted": getattr(event, "interrupted", False),
                        }
                        yield f"data: {json.dumps(message)}\n\n"
                        log_agent_event(
                            logger, "turn_complete_after_content", turn_complete=True
                        )


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
        "http://127.0.0.1:3000",  # Alternative localhost
        "http://frontend:3000",  # Docker service name
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "HEAD"],
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
    logger.info("starting_session_manager")
    await session_manager.start()
    logger.info("session_manager_started")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown."""
    logger.info("stopping_session_manager")
    await session_manager.stop()
    logger.info("application_shutdown")


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
@app.head(
    "/api/events/{session_id}",
    summary="SSE endpoint HEAD",
    operation_id="headEventStream",
)
async def sse_endpoint(
    request: Request, session_id: str, is_audio: bool = False, language: str = "en-US"
):
    """SSE endpoint for agent to client communication"""

    # Handle HEAD requests
    if request.method == "HEAD":
        return Response(
            headers={
                "Content-Type": "text/event-stream",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            }
        )

    # Start agent session for GET requests
    # Use session_id as user_id for ADK
    runner, adk_session, run_config = await start_agent_session(
        session_id, is_audio, language
    )

    # Store the session with session manager
    session_info = session_manager.create_session(
        session_id=session_id,
        user_id=session_id,  # Using session_id as user_id for POC
        request_queue=None,  # No longer using LiveRequestQueue
    )
    session_info.metadata["language"] = language
    session_info.metadata["runner"] = runner
    session_info.metadata["adk_session"] = adk_session
    session_info.metadata["run_config"] = run_config
    session_info.metadata["message_queue"] = asyncio.Queue()

    log_session_event(
        logger, session_id, "connected", is_audio=is_audio, language=language
    )

    # Send initial greeting message
    logger.info("sending_initial_greeting", session_id=session_id)
    initial_content = Content(
        role="user",
        parts=[
            Part.from_text(text="[System: New session started. Please greet the user.]")
        ],
    )

    # Process initial greeting
    greeting_events = await process_message(
        runner, adk_session, initial_content, run_config
    )

    # Queue the greeting events
    logger.info(
        "queueing_greeting_events",
        session_id=session_id,
        event_count=len(greeting_events),
    )
    for i, event in enumerate(greeting_events):
        logger.debug(
            "queueing_event",
            session_id=session_id,
            event_index=i,
            event_type=type(event).__name__,
            has_content=hasattr(event, "content") and event.content is not None,
        )
        await session_info.metadata["message_queue"].put(event)
    logger.info(
        "greeting_events_queued",
        session_id=session_id,
        total_events=len(greeting_events),
    )

    def cleanup():
        session_manager.remove_session(session_id)
        log_session_event(logger, session_id, "disconnected")

    async def event_generator():
        heartbeat_task = None

        # Simple queue for heartbeats
        heartbeat_queue = asyncio.Queue(maxsize=1)

        async def send_heartbeats():
            """Send heartbeats every 15 seconds."""
            try:
                while True:
                    await asyncio.sleep(15)
                    try:
                        # Use put_nowait to avoid blocking if queue is full
                        heartbeat_queue.put_nowait(
                            {
                                "type": "heartbeat",
                                "timestamp": datetime.now(UTC).isoformat(),
                            }
                        )
                    except asyncio.QueueFull:
                        # If queue is full, remove old heartbeat and add new one
                        try:
                            heartbeat_queue.get_nowait()
                            heartbeat_queue.put_nowait(
                                {
                                    "type": "heartbeat",
                                    "timestamp": datetime.now(UTC).isoformat(),
                                }
                            )
                        except Exception:
                            pass
            except asyncio.CancelledError:
                pass

        try:
            # Send initial connection event
            yield f"data: {json.dumps({'type': 'connected', 'session_id': session_id})}\n\n"

            # Start heartbeat sender
            heartbeat_task = asyncio.create_task(send_heartbeats())

            # Get message queue from session
            message_queue = session_info.metadata.get("message_queue")
            if not message_queue:
                logger.error("no_message_queue", session_id=session_id)
                yield f"data: {json.dumps({'type': 'error', 'message': 'No message queue'})}\\n\\n"
                return

            # Process events from queue
            async def get_next_event():
                """Get next event from queue"""
                try:
                    event = await message_queue.get()
                    logger.debug(
                        "event_retrieved_from_queue",
                        session_id=session_id,
                        event_type=type(event).__name__,
                    )
                    return event
                except Exception as e:
                    logger.error("queue_get_error", error=str(e))
                    return None

            while True:
                # Wait for either a heartbeat or a queued message
                tasks = []

                # Always wait for heartbeats
                heartbeat_task = asyncio.create_task(heartbeat_queue.get())
                tasks.append(heartbeat_task)

                # Wait for next event from queue
                event_task = asyncio.create_task(get_next_event())
                tasks.append(event_task)

                # Wait for first task to complete if we have tasks
                if not tasks:
                    await asyncio.sleep(0.1)
                    continue

                done, pending = await asyncio.wait(
                    tasks, return_when=asyncio.FIRST_COMPLETED
                )

                # Cancel pending tasks
                for task in pending:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass

                # Process completed tasks
                for task in done:
                    if task == heartbeat_task:
                        try:
                            heartbeat_msg = task.result()
                            yield f"data: {json.dumps(heartbeat_msg)}\n\n"
                            logger.debug(
                                "heartbeat_sent",
                                session_id=session_id,
                                timestamp=heartbeat_msg.get("timestamp"),
                            )
                        except Exception as e:
                            logger.error("heartbeat_error", error=str(e))
                    elif task == event_task:
                        try:
                            event = task.result()
                            if event:
                                logger.info(
                                    "processing_agent_event",
                                    session_id=session_id,
                                    event_type=type(event).__name__,
                                    has_content=hasattr(event, "content"),
                                    has_turn_complete=hasattr(event, "turn_complete"),
                                    has_partial=hasattr(event, "partial"),
                                )

                                # Convert event to SSE format
                                # Create an async generator from the single event
                                async def single_event(evt=event):
                                    yield evt

                                async for sse_msg in agent_to_client_sse(
                                    single_event()
                                ):
                                    logger.debug(
                                        "sse_message_generated",
                                        session_id=session_id,
                                        message_preview=sse_msg[:100],
                                    )
                                    yield sse_msg
                        except Exception as e:
                            logger.error(
                                "event_processing_error", error=str(e), exc_info=True
                            )
        except Exception as e:
            logger.error(
                "sse_stream_error", session_id=session_id, error=str(e), exc_info=True
            )
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        finally:
            if heartbeat_task and not heartbeat_task.done():
                heartbeat_task.cancel()
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
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Get session components
    runner = session.metadata.get("runner")
    adk_session = session.metadata.get("adk_session")
    run_config = session.metadata.get("run_config")
    message_queue = session.metadata.get("message_queue")

    if not all([runner, adk_session, run_config, message_queue]):
        raise HTTPException(status_code=500, detail="Session not properly initialized")

    # Parse the message
    mime_type = message.mime_type
    data = message.data

    # Process the message based on type
    if mime_type == "text/plain":
        content = Content(role="user", parts=[Part.from_text(text=data)])

        log_agent_event(
            logger,
            "message_received",
            session_id=session_id,
            mime_type=mime_type,
            text=data,
        )

        # Process message and get events
        try:
            events = await process_message(runner, adk_session, content, run_config)

            # Queue events for SSE delivery
            for event in events:
                if message_queue:
                    await message_queue.put(event)

            # Send a final turn_complete event after all content
            turn_complete_event = type(
                "Event",
                (),
                {
                    "turn_complete": True,
                    "interrupted": False,
                    "content": None,
                    "partial": False,
                },
            )()
            if message_queue:
                await message_queue.put(turn_complete_event)

            log_agent_event(
                logger,
                "message_processed",
                session_id=session_id,
                event_count=len(events),
            )
        except Exception as e:
            logger.error(
                "message_processing_error", session_id=session_id, error=str(e)
            )
            raise HTTPException(
                status_code=500, detail=f"Error processing message: {e!s}"
            ) from e
    elif mime_type == "audio/pcm":
        # For now, audio is not supported in non-live mode
        raise HTTPException(
            status_code=501,
            detail="Audio processing not yet implemented in request-response mode",
        )
    elif mime_type in AudioConverter.SUPPORTED_INPUT_FORMATS:
        # Audio conversion not supported in request-response mode
        raise HTTPException(
            status_code=501,
            detail="Audio processing not yet implemented in request-response mode",
        )
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
