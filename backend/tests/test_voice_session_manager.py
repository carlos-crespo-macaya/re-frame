"""Tests for voice session manager."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.voice.session_manager import VoiceSessionManager, voice_session_manager


class TestVoiceSessionManager:
    """Test voice session manager functionality."""

    def test_voice_session_manager_singleton(self):
        """Test that voice_session_manager is a singleton instance."""
        assert isinstance(voice_session_manager, VoiceSessionManager)

    @pytest.mark.asyncio
    async def test_start_stop(self):
        """Test starting and stopping the session manager."""
        manager = VoiceSessionManager()

        # Test start
        await manager.start()
        # Manager should be ready to accept sessions

        # Test stop
        await manager.stop()
        # All sessions should be cleaned up

    def test_get_nonexistent_session(self):
        """Test getting a session that doesn't exist."""
        manager = VoiceSessionManager()
        session = manager.get_session("nonexistent-id")
        assert session is None

    @pytest.mark.asyncio
    async def test_remove_nonexistent_session(self):
        """Test removing a session that doesn't exist."""
        manager = VoiceSessionManager()
        # Should not raise an error
        await manager.remove_session("nonexistent-id")

    @pytest.mark.asyncio
    async def test_create_session_basic(self):
        """Test basic session creation."""
        manager = VoiceSessionManager()

        with patch("src.voice.session_manager.uuid4") as mock_uuid:
            mock_uuid.return_value = "test-session-id"

            session = await manager.create_session("en-US")

            assert session is not None
            assert session.session_id == "voice-test-session-id"
            assert session.language == "en-US"
            assert session.status == "active"

    def test_get_existing_session(self):
        """Test getting an existing session."""
        manager = VoiceSessionManager()

        # Create a mock session
        mock_session = MagicMock()
        mock_session.session_id = "test-session"
        mock_session.status = "active"

        # Add to sessions dict
        manager.sessions["test-session"] = mock_session

        # Get the session
        session = manager.get_session("test-session")
        assert session == mock_session

    @pytest.mark.asyncio
    async def test_remove_existing_session(self):
        """Test removing an existing session."""
        manager = VoiceSessionManager()

        # Create a mock session
        mock_session = MagicMock()
        mock_session.session_id = "test-session"
        mock_session.cleanup = AsyncMock()

        # Add to sessions dict
        manager.sessions["test-session"] = mock_session

        # Remove the session
        await manager.remove_session("test-session")

        # Verify cleanup was called and session removed
        mock_session.cleanup.assert_called_once()
        assert "test-session" not in manager.sessions
