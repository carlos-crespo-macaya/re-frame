"""Tests for session language management."""

import pytest

from src.models import SessionInfo as SessionModel
from src.utils.session_manager import SessionManager
from tests.fixtures.language_fixtures import SUPPORTED_LANGUAGES


class TestSessionLanguageManagement:
    """Test language storage and retrieval in sessions."""

    @pytest.fixture
    def session_manager(self):
        """Create a fresh session manager for each test."""
        return SessionManager()

    def test_create_session_with_language(self, session_manager):
        """Test creating a session with language metadata."""
        session = session_manager.create_session(
            session_id="test-123", user_id="user-123"
        )
        session.metadata["language"] = "es-ES"

        retrieved = session_manager.get_session("test-123")
        assert retrieved.metadata.get("language") == "es-ES"

    def test_session_language_persistence(self, session_manager):
        """Test that language persists across session retrievals."""
        # Create session with language
        session = session_manager.create_session(
            session_id="test-456", user_id="user-456"
        )
        session.metadata["language"] = "pt-BR"

        # Simulate retrieval in different request
        retrieved = session_manager.get_session("test-456")
        assert retrieved.metadata.get("language") == "pt-BR"

    def test_missing_language_defaults(self, session_manager):
        """Test that missing language returns None."""
        session = session_manager.create_session(
            session_id="test-789", user_id="user-789"
        )
        # Don't set language

        # Should return None or we handle default elsewhere
        assert session.metadata.get("language") is None

    def test_multiple_sessions_different_languages(self, session_manager):
        """Test multiple sessions can have different languages."""
        # Create sessions with different languages
        session1 = session_manager.create_session(
            session_id="session-en", user_id="user-en"
        )
        session1.metadata["language"] = "en-US"

        session2 = session_manager.create_session(
            session_id="session-es", user_id="user-es"
        )
        session2.metadata["language"] = "es-ES"

        session3 = session_manager.create_session(
            session_id="session-de", user_id="user-de"
        )
        session3.metadata["language"] = "de-DE"

        # Verify each session maintains its language
        assert (
            session_manager.get_session("session-en").metadata.get("language")
            == "en-US"
        )
        assert (
            session_manager.get_session("session-es").metadata.get("language")
            == "es-ES"
        )
        assert (
            session_manager.get_session("session-de").metadata.get("language")
            == "de-DE"
        )

    def test_session_language_update(self, session_manager):
        """Test updating session language (though not recommended)."""
        session = session_manager.create_session(
            session_id="test-update", user_id="user-update"
        )
        session.metadata["language"] = "en-US"

        # Update language
        retrieved = session_manager.get_session("test-update")
        retrieved.metadata["language"] = "fr-FR"

        # Verify update persisted
        final = session_manager.get_session("test-update")
        assert final.metadata.get("language") == "fr-FR"

    def test_all_supported_languages_in_session(self, session_manager):
        """Test that all supported languages can be stored in sessions."""
        for idx, lang_code in enumerate(SUPPORTED_LANGUAGES):
            session_id = f"test-lang-{idx}"
            session = session_manager.create_session(
                session_id=session_id, user_id=f"user-{idx}"
            )
            session.metadata["language"] = lang_code

            # Verify storage
            retrieved = session_manager.get_session(session_id)
            assert retrieved.metadata.get("language") == lang_code

    def test_session_info_includes_language(self, session_manager):
        """Test that session info includes language in metadata."""
        from datetime import UTC, datetime

        session = session_manager.create_session(
            session_id="test-info", user_id="user-info"
        )
        session.metadata["language"] = "ja-JP"

        # Get session info (simulating what the endpoint returns)
        session_info = SessionModel(
            session_id=session.session_id,
            user_id=session.user_id,
            created_at=datetime.fromtimestamp(session.created_at, tz=UTC).isoformat(),
            last_activity=datetime.fromtimestamp(
                session.last_activity, tz=UTC
            ).isoformat(),
            age_seconds=session.age_seconds,
            inactive_seconds=session.inactive_seconds,
            has_request_queue=session.request_queue is not None,
            metadata={
                "language": session.metadata.get("language", "en-US"),
                "has_runner": "runner" in session.metadata,
                "has_adk_session": "adk_session" in session.metadata,
            },
        )

        assert session_info.metadata["language"] == "ja-JP"
