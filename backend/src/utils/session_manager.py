"""Simple session management for POC."""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class SessionInfo:
    """Session metadata."""

    session_id: str
    user_id: str
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    request_queue: Any = None  # LiveRequestQueue
    metadata: dict[str, Any] = field(default_factory=dict)

    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity = time.time()

    @property
    def age_seconds(self) -> float:
        """Get session age in seconds."""
        return time.time() - self.created_at

    @property
    def inactive_seconds(self) -> float:
        """Get time since last activity in seconds."""
        return time.time() - self.last_activity


class SessionManager:
    """Simple in-memory session manager for POC."""

    def __init__(self, max_age_seconds: int = 3600):  # 1 hour default
        self.sessions: dict[str, SessionInfo] = {}
        self.max_age_seconds = max_age_seconds
        self._cleanup_task: asyncio.Task | None = None
        self._running = False

    async def start(self):
        """Start the session manager with periodic cleanup."""
        if not self._running:
            self._running = True
            self._cleanup_task = asyncio.create_task(self._periodic_cleanup())
            logger.info(f"Session manager started with {self.max_age_seconds}s max age")

    async def stop(self):
        """Stop the session manager."""
        self._running = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        logger.info("Session manager stopped")

    def create_session(
        self, session_id: str, user_id: str, request_queue: Any = None
    ) -> SessionInfo:
        """Create a new session."""
        session = SessionInfo(
            session_id=session_id, user_id=user_id, request_queue=request_queue
        )
        self.sessions[session_id] = session
        logger.info(f"Session created: {session_id} for user {user_id}")
        return session

    def get_session(self, session_id: str) -> SessionInfo | None:
        """Get session by ID and update activity."""
        session = self.sessions.get(session_id)
        if session:
            session.update_activity()
        return session

    def remove_session(self, session_id: str) -> SessionInfo | None:
        """Remove and return a session."""
        session = self.sessions.pop(session_id, None)
        if session:
            # Clean up request queue if exists
            if session.request_queue:
                session.request_queue.close()
            logger.info(f"Session removed: {session_id}")
        return session

    def get_session_readonly(self, session_id: str) -> SessionInfo | None:
        """Get session by ID without updating activity (for debugging)."""
        return self.sessions.get(session_id)

    def get_active_session_count(self) -> int:
        """Get count of active sessions."""
        return len(self.sessions)

    async def _periodic_cleanup(self):
        """Periodically clean up expired sessions."""
        cleanup_interval = min(
            300, max(self.max_age_seconds / 4, 1)
        )  # Check every 5 min or 1/4 of max age, with a minimum of 1 second

        while self._running:
            try:
                await asyncio.sleep(cleanup_interval)

                # Find expired sessions
                expired = []
                for session_id, session in self.sessions.items():
                    if session.age_seconds > self.max_age_seconds:
                        expired.append(session_id)

                # Clean up expired sessions
                for session_id in expired:
                    self.remove_session(session_id)

                if expired:
                    logger.info(f"Cleaned up {len(expired)} expired sessions")

                # Log status
                active_count = self.get_active_session_count()
                if active_count > 0:
                    logger.debug(f"Active sessions: {active_count}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in session cleanup: {e}")


# Global session manager instance
session_manager = SessionManager()
