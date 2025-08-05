"""FastAPI router for text endpoints."""

import asyncio
import json
import os
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request, Response
from fastapi.responses import StreamingResponse
from google.adk.agents.run_config import RunConfig
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part, SpeechConfig

from src.agents.cbt_assistant import create_cbt_assistant
from src.models.api import (
    LanguageDetectionRequest,
    LanguageDetectionResponse,
    MessageRequest,
    MessageResponse,
    SessionInfo,
    SessionListResponse,
)
from src.utils.language_utils import (
    get_default_language,
    normalize_language_code,
    validate_language_code,
)
from src.utils.logging import get_logger, log_agent_event, log_session_event
from src.utils.performance_monitor import get_performance_monitor
from src.utils.rate_limiter import RateLimiter
from src.utils.session_manager import session_manager

logger = get_logger(__name__)

router = APIRouter(prefix="/api", tags=["text"])

# Rate limiter for language detection endpoint (100 requests per minute)
language_limiter = RateLimiter(max_requests=100, window_seconds=60)

APP_NAME = "CBT Reframing Assistant"


# Language detection function removed - using URL parameter only


async def start_agent_session(user_id, language_code="en-US"):
    """Starts an agent session"""
    logger.info(
        "agent_session_starting",
        user_id=user_id,
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
        user_id=user_id,
    )
    logger.info("adk_session_created", session=str(session), user_id=user_id)

    # Text mode only configuration
    run_config = RunConfig(
        response_modalities=["TEXT"],
        speech_config=SpeechConfig(language_code=language_code),
    )
    logger.debug("run_config_created", config=str(run_config))

    log_agent_event(
        logger,
        "session_initialized",
        session_id=session.id,
        language=language_code,
    )
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
        yield f"data: {json.dumps({'type': 'content', 'content': str(event)})}\n\n"


@router.get(
    "/events/{session_id}", summary="SSE endpoint", operation_id="getEventStream"
)
@router.head(
    "/events/{session_id}",
    summary="SSE endpoint HEAD",
    operation_id="headEventStream",
)
async def sse_endpoint(
    request: Request, session_id: str, language: str = Query(default="en-US")
):
    """SSE endpoint for agent to client communication"""

    # Validate and normalize language
    normalized_language = normalize_language_code(language)
    if not validate_language_code(normalized_language):
        logger.warning(
            "invalid_language_code",
            session_id=session_id,
            requested_language=language,
            fallback=get_default_language(),
        )
        normalized_language = get_default_language()

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

    # Check if session already exists (reconnection)
    existing_session = session_manager.get_session_readonly(session_id)
    if existing_session:
        # Reconnecting to existing session
        greeting_sent = existing_session.metadata.get("greeting_sent", False)
        logger.info(
            "reconnecting_to_existing_session",
            session_id=session_id,
            greeting_sent=greeting_sent,
            existing_language=existing_session.metadata.get("language"),
        )
    else:
        greeting_sent = False

    # Start agent session for GET requests
    # Use session_id as user_id for ADK
    runner, adk_session, run_config = await start_agent_session(
        session_id, normalized_language
    )

    # Store the session with session manager
    session_info = session_manager.create_session(
        session_id=session_id,
        user_id=session_id,  # Using session_id as user_id for POC
        request_queue=None,  # No longer using LiveRequestQueue
    )
    session_info.metadata["language"] = normalized_language
    session_info.metadata["runner"] = runner
    session_info.metadata["adk_session"] = adk_session
    session_info.metadata["run_config"] = run_config
    session_info.metadata["message_queue"] = asyncio.Queue()

    # Preserve greeting state on reconnection
    session_info.metadata["greeting_sent"] = greeting_sent

    log_session_event(logger, session_id, "connected", language=normalized_language)

    # Track session start for performance monitoring
    performance_monitor = get_performance_monitor()
    await performance_monitor.start_session(session_id)

    message_queue = session_info.metadata["message_queue"]

    # Create the SSE stream with heartbeats
    async def stream_generator(request: Request):
        """Generate SSE stream with heartbeats."""
        yield f"data: {json.dumps({'type': 'connected', 'session_id': session_id})}\n\n"

        heartbeat_interval = int(os.getenv("HEARTBEAT_INTERVAL_SECONDS", "20"))
        heartbeat_queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()

        async def send_heartbeats():
            """Send periodic heartbeats to keep connection alive."""
            logger.debug(
                "heartbeat_task_started",
                session_id=session_id,
                interval=heartbeat_interval,
            )
            while True:
                try:
                    await asyncio.sleep(heartbeat_interval)
                    heartbeat_msg = {
                        "type": "heartbeat",
                        "timestamp": datetime.now(UTC).isoformat(),
                    }
                    await heartbeat_queue.put(heartbeat_msg)
                except asyncio.CancelledError:
                    logger.debug("heartbeat_task_cancelled", session_id=session_id)
                    break
                except Exception as e:
                    logger.error("heartbeat_error", error=str(e), session_id=session_id)

        heartbeat_task = asyncio.create_task(send_heartbeats())

        try:

            async def get_next_event():
                try:
                    # Add 1-second timeout to prevent hanging when client disconnects
                    event = await asyncio.wait_for(message_queue.get(), timeout=1.0)
                    logger.debug(
                        "event_retrieved",
                        session_id=session_id,
                        event_type=type(event).__name__,
                    )
                    return event
                except TimeoutError:
                    # Timeout is normal - it allows checking for disconnection
                    return None
                except Exception as e:
                    logger.error("queue_get_error", error=str(e))
                    return None

            while True:
                # Check if client has disconnected
                if await request.is_disconnected():
                    logger.info("client_disconnected", session_id=session_id)
                    break

                # Check if we should shutdown
                if session_info and session_info.metadata.get("sse_shutdown", False):
                    logger.info("sse_shutdown_requested", session_id=session_id)
                    break

                # Wait for either a heartbeat or a queued message
                tasks = []

                # Always wait for heartbeats
                heartbeat_task_wait = asyncio.create_task(heartbeat_queue.get())
                tasks.append(heartbeat_task_wait)

                # Wait for next event from queue
                event_task = asyncio.create_task(get_next_event())
                tasks.append(event_task)

                # Wait for first task to complete, with a timeout to allow disconnect checks
                done, pending = await asyncio.wait(
                    tasks, return_when=asyncio.FIRST_COMPLETED, timeout=1.0
                )

                # If timeout occurred, cancel pending tasks and loop again
                if not done:
                    for task in pending:
                        task.cancel()
                        try:
                            await task
                        except asyncio.CancelledError:
                            pass
                    continue

                # Cancel any remaining pending tasks
                for task in pending:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass

                # Process completed tasks
                for task in done:
                    if task == heartbeat_task_wait:
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
                            if event is None:
                                continue

                            logger.debug(
                                "processing_event",
                                session_id=session_id,
                                event_type=type(event).__name__,
                                has_turn_complete=hasattr(event, "turn_complete"),
                            )

                            # Handle string messages
                            if isinstance(event, str):
                                if event == "STREAM_END":
                                    logger.info(
                                        "stream_end_received", session_id=session_id
                                    )
                                    break
                                else:
                                    # Regular string message - use SSEMessage format
                                    string_message = {
                                        "type": "content",
                                        "content_type": "text/plain",
                                        "data": event,  # Text content directly, no base64 encoding needed
                                    }
                                    yield f"data: {json.dumps(string_message)}\n\n"
                                    logger.debug(
                                        "message_sent",
                                        session_id=session_id,
                                        content_length=len(event),
                                    )
                            # Handle Event objects
                            elif hasattr(event, "content") and event.content:
                                content = event.content
                                if hasattr(content, "parts") and content.parts:
                                    for part in content.parts:
                                        if hasattr(part, "text") and part.text:
                                            # Use SSEMessage format
                                            part_message = {
                                                "type": "content",
                                                "content_type": "text/plain",
                                                "data": part.text,  # Text content directly
                                            }
                                            yield f"data: {json.dumps(part_message)}\n\n"
                                            logger.debug(
                                                "event_message_sent",
                                                session_id=session_id,
                                                content_length=len(part.text),
                                            )
                            # Handle turn_complete events
                            elif (
                                hasattr(event, "turn_complete") and event.turn_complete
                            ):
                                turn_message: dict[str, Any] = {
                                    "type": "turn_complete",
                                    "turn_complete": True,
                                    "interrupted": getattr(event, "interrupted", False),
                                }
                                yield f"data: {json.dumps(turn_message)}\n\n"
                                logger.debug(
                                    "turn_complete_sent",
                                    session_id=session_id,
                                    interrupted=getattr(event, "interrupted", False),
                                )
                        except Exception as e:
                            logger.error(
                                "event_processing_error",
                                error=str(e),
                                session_id=session_id,
                            )

        except asyncio.CancelledError:
            logger.info("sse_connection_cancelled", session_id=session_id)
            raise
        except Exception as e:
            logger.error("sse_stream_error", error=str(e), session_id=session_id)
            error_msg = {
                "type": "error",
                "message": "Stream error occurred",
                "timestamp": datetime.now(UTC).isoformat(),
            }
            yield f"data: {json.dumps(error_msg)}\n\n"
        finally:
            heartbeat_task.cancel()
            try:
                await heartbeat_task
            except asyncio.CancelledError:
                pass
            logger.info("sse_stream_ended", session_id=session_id)

    return StreamingResponse(
        stream_generator(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable Nginx buffering
            "X-Session-Id": session_id,
        },
    )


@router.post(
    "/send/{session_id}",
    response_model=MessageResponse,
    summary="Send message",
    operation_id="sendMessage",
)
async def send_message_endpoint(
    session_id: str, message: MessageRequest
) -> MessageResponse:
    """HTTP endpoint for text message communication only."""
    performance_monitor = get_performance_monitor()
    async with performance_monitor.track_request("text"):
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
            raise HTTPException(
                status_code=500, detail="Session not properly initialized"
            )

        # Only accept text/plain messages
        if message.mime_type != "text/plain":
            raise HTTPException(
                status_code=415,
                detail="Only text/plain messages are supported. Use /voice endpoints for audio.",
            )

        # Skip empty messages
        if not message.data or not message.data.strip():
            logger.info("empty_message_received", session_id=session_id)
            return MessageResponse(status="sent", error=None)

        # Check if this is the first user message (reactive greeting)
        greeting_sent = session.metadata.get("greeting_sent", False)
        if not greeting_sent:
            # Mark greeting as sent - the agent will send greeting on first message
            session.metadata["greeting_sent"] = True
            logger.info(
                "first_user_message_received",
                session_id=session_id,
                language=session.metadata.get("language"),
            )

        content = Content(role="user", parts=[Part.from_text(text=message.data)])

        log_agent_event(
            logger,
            "message_received",
            session_id=session_id,
            mime_type=message.mime_type,
            text=message.data,
        )

        # Process message and get events
        try:
            events = await process_message(runner, adk_session, content, run_config)

            # Queue events for SSE delivery
            event_count = 0
            for event in events:
                if message_queue:
                    await message_queue.put(event)
                event_count += 1

            # Send a final turn_complete event after all content
            # Create a simple object with the required attributes
            class TurnCompleteEvent:
                turn_complete = True
                interrupted = False

            turn_complete_event = TurnCompleteEvent()
            logger.info(
                "creating_turn_complete_event",
                session_id=session_id,
                has_queue=message_queue is not None,
            )
            if message_queue:
                await message_queue.put(turn_complete_event)
                logger.info("turn_complete_queued", session_id=session_id)

            log_agent_event(
                logger,
                "message_processed",
                session_id=session_id,
                event_count=event_count,
            )
        except Exception as e:
            logger.error(
                "message_processing_error", session_id=session_id, error=str(e)
            )
            raise HTTPException(
                status_code=500, detail=f"Error processing message: {e!s}"
            ) from e

        return MessageResponse(status="sent", error=None)


@router.get(
    "/session/{session_id}",
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
        metadata={
            "language": session.metadata.get("language", "en-US"),
            "has_runner": "runner" in session.metadata,
            "has_adk_session": "adk_session" in session.metadata,
            "phase_status": session.metadata.get("phase_status", "unknown"),
        },
    )


@router.get(
    "/sessions",
    response_model=SessionListResponse,
    summary="List all sessions",
    operation_id="listSessions",
)
async def list_sessions() -> SessionListResponse:
    """List all active sessions."""
    sessions = session_manager.list_sessions()
    return SessionListResponse(
        total_sessions=len(sessions),
        sessions=[
            {
                "session_id": s.session_id,
                "age_seconds": s.age_seconds,
                "inactive_seconds": s.inactive_seconds,
            }
            for s in sessions
        ],
    )


@router.get("/pdf/{session_id}", summary="Download PDF", operation_id="downloadPdf")
async def download_pdf(session_id: str):
    """Download PDF summary for a session - minimal implementation for local testing"""
    from datetime import datetime

    # For POC, return a simple text file as PDF
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Generate simple PDF content
    pdf_content = f"""
CBT Reframing Session Summary
==============================
Session ID: {session_id}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This is a placeholder PDF summary for the CBT reframing session.
In production, this would contain:
- Key insights from the conversation
- Reframed thoughts and situations
- Personalized coping strategies
- Progress notes

Thank you for using the CBT Reframing Assistant!
"""

    # Return as plain text for now (POC)
    return Response(
        content=pdf_content,
        media_type="text/plain",
        headers={
            "Content-Disposition": f'attachment; filename="session_{session_id}_summary.txt"'
        },
    )


@router.post(
    "/language/detect",
    response_model=LanguageDetectionResponse,
    summary="Detect language",
    operation_id="detectLanguage",
)
async def detect_language_endpoint(
    request: LanguageDetectionRequest,
    req: Request,
) -> LanguageDetectionResponse:
    """Detect the language of the provided text - DEPRECATED: Always returns English."""
    # Rate limiting
    client_host = req.client.host if req.client else "unknown"
    if not await language_limiter.check_request(client_host):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later.",
            headers={"Retry-After": "60"},
        )

    # Language detection is deprecated - always return English
    # Language should be specified via URL parameter instead
    logger.info(
        "language_detection_endpoint_called_deprecated",
        text_length=len(request.text) if request.text else 0,
    )

    return LanguageDetectionResponse(
        status="success",
        language="en",
        confidence=1.0,
        message="Language detection is deprecated. Use language URL parameter instead.",
    )


@router.delete(
    "/session/{session_id}/sse",
    summary="Close SSE connection",
    operation_id="closeSSEConnection",
)
async def close_sse_connection(session_id: str):
    """Close an SSE connection gracefully by setting shutdown flag."""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Set shutdown flag
    session.metadata["sse_shutdown"] = True

    # Also put STREAM_END in the queue if it exists
    message_queue = session.metadata.get("message_queue")
    if message_queue:
        await message_queue.put("STREAM_END")

    logger.info("sse_close_requested", session_id=session_id)
    return {"status": "closing"}
