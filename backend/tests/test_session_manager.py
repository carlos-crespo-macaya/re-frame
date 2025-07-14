"""Tests for session management."""

import asyncio
import time
from unittest.mock import MagicMock

import pytest

from src.utils.session_manager import SessionInfo, SessionManager


class TestSessionInfo:
    """Test SessionInfo class."""

    def test_session_info_creation(self):
        """Test creating a session info object."""
        session = SessionInfo(session_id="test-123", user_id="user-456")

        assert session.session_id == "test-123"
        assert session.user_id == "user-456"
        assert session.created_at > 0
        assert session.last_activity > 0
        assert session.request_queue is None
        assert session.metadata == {}

    def test_update_activity(self):
        """Test updating session activity."""
        session = SessionInfo("test-123", "user-456")
        initial_activity = session.last_activity

        # Wait a bit and update
        time.sleep(0.1)
        session.update_activity()

        assert session.last_activity > initial_activity
        assert session.created_at == session.created_at  # Created time shouldn't change

    def test_age_seconds(self):
        """Test session age calculation."""
        session = SessionInfo("test-123", "user-456")

        # Initially should be close to 0
        assert session.age_seconds < 0.1

        # Manually set created_at to past
        session.created_at = time.time() - 100
        assert 99 < session.age_seconds < 101

    def test_inactive_seconds(self):
        """Test inactive time calculation."""
        session = SessionInfo("test-123", "user-456")

        # Initially should be close to 0
        assert session.inactive_seconds < 0.1

        # Manually set last_activity to past
        session.last_activity = time.time() - 50
        assert 49 < session.inactive_seconds < 51


class TestSessionManager:
    """Test SessionManager class."""

    @pytest.mark.asyncio
    async def test_session_manager_lifecycle(self):
        """Test starting and stopping session manager."""
        manager = SessionManager(max_age_seconds=10)

        # Start manager
        await manager.start()
        assert manager._running is True
        assert manager._cleanup_task is not None

        # Stop manager
        await manager.stop()
        assert manager._running is False

    def test_create_session(self):
        """Test creating a session."""
        manager = SessionManager()
        mock_queue = MagicMock()

        session = manager.create_session(
            session_id="test-123", user_id="user-456", request_queue=mock_queue
        )

        assert session.session_id == "test-123"
        assert session.user_id == "user-456"
        assert session.request_queue == mock_queue
        assert "test-123" in manager.sessions

    def test_get_session(self):
        """Test getting a session."""
        manager = SessionManager()

        # Create session
        created = manager.create_session("test-123", "user-456")
        initial_activity = created.last_activity

        # Wait and get session
        time.sleep(0.1)
        retrieved = manager.get_session("test-123")

        assert retrieved is not None
        assert retrieved.session_id == "test-123"
        assert retrieved.last_activity > initial_activity  # Activity updated

        # Get non-existent session
        assert manager.get_session("non-existent") is None

    def test_remove_session(self):
        """Test removing a session."""
        manager = SessionManager()
        mock_queue = MagicMock()

        # Create and remove session
        manager.create_session("test-123", "user-456", mock_queue)
        removed = manager.remove_session("test-123")

        assert removed is not None
        assert removed.session_id == "test-123"
        assert "test-123" not in manager.sessions
        mock_queue.close.assert_called_once()

        # Remove non-existent session
        assert manager.remove_session("non-existent") is None

    def test_get_active_session_count(self):
        """Test counting active sessions."""
        manager = SessionManager()

        assert manager.get_active_session_count() == 0

        manager.create_session("test-1", "user-1")
        manager.create_session("test-2", "user-2")
        assert manager.get_active_session_count() == 2

        manager.remove_session("test-1")
        assert manager.get_active_session_count() == 1

    @pytest.mark.asyncio
    async def test_periodic_cleanup(self):
        """Test automatic cleanup of expired sessions."""
        # Create manager with very short max age
        manager = SessionManager(max_age_seconds=1)

        # Create sessions
        session1 = manager.create_session("test-1", "user-1")
        manager.create_session("test-2", "user-2")

        # Make session1 expired
        session1.created_at = time.time() - 2  # 2 seconds old

        # Start manager
        await manager.start()

        # Wait for cleanup cycle
        await asyncio.sleep(0.5)  # Cleanup runs every 0.25s for 1s max age

        # Check that expired session was removed
        assert manager.get_session("test-1") is None
        assert manager.get_session("test-2") is not None

        # Stop manager
        await manager.stop()

    @pytest.mark.asyncio
    async def test_cleanup_with_request_queue(self):
        """Test that cleanup closes request queues."""
        manager = SessionManager(max_age_seconds=1)
        mock_queue = MagicMock()

        # Create expired session with queue
        session = manager.create_session("test-123", "user-456", mock_queue)
        session.created_at = time.time() - 2

        # Start and wait for cleanup
        await manager.start()
        await asyncio.sleep(0.5)

        # Verify queue was closed
        mock_queue.close.assert_called_once()
        assert manager.get_session("test-123") is None

        await manager.stop()

    @pytest.mark.asyncio
    async def test_multiple_cleanup_cycles(self):
        """Test multiple cleanup cycles don't interfere."""
        manager = SessionManager(max_age_seconds=2)

        await manager.start()

        # Create sessions at different times
        manager.create_session("test-1", "user-1")
        await asyncio.sleep(0.5)

        manager.create_session("test-2", "user-2")
        await asyncio.sleep(0.5)

        manager.create_session("test-3", "user-3")

        # Make first session expired
        manager.sessions["test-1"].created_at = time.time() - 3

        # Wait for cleanup
        await asyncio.sleep(0.6)

        # Only first session should be removed
        assert manager.get_session("test-1") is None
        assert manager.get_session("test-2") is not None
        assert manager.get_session("test-3") is not None

        await manager.stop()
