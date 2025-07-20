"""Voice session management for ADK streaming."""

import asyncio
import logging
import time
from typing import Any
from uuid import uuid4

from google.adk.agents.run_config import RunConfig
from google.adk.runners import InMemoryRunner, LiveRequestQueue
from google.genai.types import Blob, Content, Part, SpeechConfig

from src.agents.cbt_assistant import create_cbt_assistant

logger = logging.getLogger(__name__)


class VoiceSession:
    """Manages a single voice streaming session."""

    def __init__(self, session_id: str, language: str = "en-US"):
        self.session_id = session_id
        self.language = language
        self.status = "created"
        self.created_at = time.time()
        self.last_activity = time.time()

        # ADK components
        self.runner: InMemoryRunner | None = None
        self.adk_session: Any | None = None
        self.agent_name = "CBT Reframing Assistant"

        # Streaming components
        self.live_request_queue: LiveRequestQueue | None = None
        self.live_events: Any | None = None
        self.agent_queue: asyncio.Queue = asyncio.Queue()  # Responses from agent
        self.stream_task: asyncio.Task | None = None

    async def initialize(self):
        """Initialize ADK components for streaming."""
        logger.info(f"Initializing voice session {self.session_id}")

        # Create CBT assistant agent
        cbt_agent = create_cbt_assistant(model="gemini-2.0-flash-live-001", language_code=self.language)

        # Create runner
        self.runner = InMemoryRunner(
            app_name=self.agent_name,
            agent=cbt_agent,
        )

        # Create ADK session
        self.adk_session = await self.runner.session_service.create_session(
            app_name=self.agent_name,
            user_id=self.session_id,
        )

        # Setup streaming components
        self.live_request_queue = LiveRequestQueue()

        # Configure for audio streaming
        run_config = RunConfig(
            response_modalities=["AUDIO"],
            speech_config=SpeechConfig(language_code=self.language),
        )

        # Start live streaming
        self.live_events = self.runner.run_live(
            session=self.adk_session,
            live_request_queue=self.live_request_queue,
            run_config=run_config,
        )

        self.status = "active"
        logger.info(f"Voice session {self.session_id} initialized")

    async def start_streaming(self):
        """Start the ADK streaming process."""
        if not self.live_events:
            raise RuntimeError("Session not initialized")

        # Start the streaming task
        self.stream_task = asyncio.create_task(self._stream_handler())
        logger.info(f"Started streaming for session {self.session_id}")

    async def _stream_handler(self):
        """Handle bidirectional streaming with ADK."""
        try:
            # Stream events from ADK live
            async for event in self.live_events:
                # Put events in agent queue for SSE delivery
                await self.agent_queue.put(event)
                self.last_activity = time.time()

                # Check if turn is complete
                if hasattr(event, "turn_complete") and event.turn_complete:
                    logger.debug(f"Turn complete in session {self.session_id}")

        except Exception as e:
            logger.error(f"Stream handler error in session {self.session_id}: {e}")
            await self.agent_queue.put({"type": "error", "error": str(e)})
        finally:
            self.status = "ended"

    async def send_audio(self, audio_data: bytes):
        """Send audio chunk to ADK."""
        if self.status != "active" or not self.live_request_queue:
            raise RuntimeError("Session not active")

        # Create content with audio
        content = Content(
            role="user",
            parts=[Part(inline_data=Blob(mime_type="audio/pcm", data=audio_data))],
        )

        # Send to ADK via live request queue
        self.live_request_queue.send_content(content)
        self.last_activity = time.time()

    async def send_control(self, action: str):
        """Send control command."""
        if action == "end_turn" and self.live_request_queue:
            # Signal end of audio input
            self.live_request_queue.close()
        elif action == "end_session":
            await self.cleanup()

    async def cleanup(self):
        """Clean up session resources."""
        logger.info(f"Cleaning up voice session {self.session_id}")

        self.status = "ended"

        # Cancel streaming task
        if self.stream_task and not self.stream_task.done():
            self.stream_task.cancel()

        # Clear queue
        while not self.agent_queue.empty():
            self.agent_queue.get_nowait()

        # Close live request queue
        if self.live_request_queue:
            self.live_request_queue = None


class VoiceSessionManager:
    """Manages all voice sessions."""

    def __init__(self):
        self.sessions: dict[str, VoiceSession] = {}
        self._cleanup_task: asyncio.Task | None = None

    async def start(self):
        """Start the session manager."""
        self._cleanup_task = asyncio.create_task(self._cleanup_inactive_sessions())
        logger.info("Voice session manager started")

    async def stop(self):
        """Stop the session manager."""
        if self._cleanup_task:
            self._cleanup_task.cancel()

        # Clean up all sessions
        for session in list(self.sessions.values()):
            await session.cleanup()

        logger.info("Voice session manager stopped")

    async def create_session(self, language: str = "en-US") -> VoiceSession:
        """Create a new voice session."""
        session_id = f"voice-{uuid4()}"
        session = VoiceSession(session_id, language)

        # Initialize ADK components
        await session.initialize()
        await session.start_streaming()

        self.sessions[session_id] = session
        logger.info(f"Created voice session {session_id}")

        return session

    def get_session(self, session_id: str) -> VoiceSession | None:
        """Get an existing session."""
        return self.sessions.get(session_id)

    async def remove_session(self, session_id: str):
        """Remove and cleanup a session."""
        session = self.sessions.pop(session_id, None)
        if session:
            await session.cleanup()

    async def _cleanup_inactive_sessions(self):
        """Periodically clean up inactive sessions."""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute

                current_time = time.time()
                inactive_sessions = []

                for session_id, session in self.sessions.items():
                    # Remove sessions inactive for 5 minutes
                    if current_time - session.last_activity > 300:
                        inactive_sessions.append(session_id)

                for session_id in inactive_sessions:
                    logger.info(f"Removing inactive session {session_id}")
                    await self.remove_session(session_id)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in session cleanup: {e}")


# Global instance
voice_session_manager = VoiceSessionManager()
