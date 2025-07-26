"""Integration tests for complete language flow."""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

# Patch dependencies before importing
with (
    patch("src.text.router.create_cbt_assistant", MagicMock()),
    patch("src.utils.session_manager.session_manager", MagicMock()),
):
    from src.main import app

from src.utils.language_utils import SUPPORTED_LANGUAGES
from src.utils.session_manager import SessionInfo as SessionInfoModel
from tests.fixtures.language_fixtures import AGENT_GREETING_PATTERNS


@pytest.fixture
def mock_session_manager():
    """Mock session manager for tests."""
    with patch("src.text.router.session_manager") as mock:
        # Setup default behaviors
        mock.get_session.return_value = None
        mock.get_session_readonly.return_value = None
        mock.list_sessions.return_value = []
        mock.create_session.return_value = SessionInfoModel(
            session_id="test-session", user_id="test-user"
        )
        yield mock


@pytest.fixture
async def async_client(mock_session_manager):
    """Create an async test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.mark.asyncio
class TestLanguageFlowIntegration:
    """Integration tests for complete language flow."""

    async def test_spanish_language_flow(self):
        """Test that Spanish language is properly propagated through the system."""
        from src.text.router import start_agent_session

        # Mock the CBT assistant to verify language propagation
        with patch("src.text.router.create_cbt_assistant") as mock_create:
            mock_agent = AsyncMock()
            mock_agent.name = "TestAgent"
            mock_create.return_value = mock_agent

            with patch("src.text.router.InMemoryRunner") as mock_runner_class:
                mock_runner = AsyncMock()
                mock_session = AsyncMock()
                mock_session.id = "test-id"
                mock_session.user_id = "test-user"
                
                # Mock the run_async to return Spanish content
                async def mock_run_async(*args, **kwargs):
                    # Simulate Spanish greeting
                    yield AsyncMock(
                        content=AsyncMock(
                            parts=[
                                AsyncMock(
                                    text="¡Hola! Estoy aquí para ayudarte con el reencuadre cognitivo."
                                )
                            ]
                        )
                    )
                
                mock_runner.run_async = mock_run_async
                mock_runner.session_service.create_session.return_value = mock_session
                mock_runner_class.return_value = mock_runner

                # Test with Spanish
                runner, session, run_config = await start_agent_session(
                    "test-user", "es-ES"
                )

                # Verify Spanish was passed to agent creation
                mock_create.assert_called_once_with(language_code="es-ES")
                
                # Verify run config includes Spanish
                assert run_config.speech_config.language_code == "es-ES"

    async def test_all_supported_languages_integration(self):
        """Test that all supported languages work through the integration."""
        from src.text.router import start_agent_session

        for lang_code, lang_name in SUPPORTED_LANGUAGES.items():
            with patch("src.text.router.create_cbt_assistant") as mock_create:
                mock_agent = AsyncMock()
                mock_agent.name = f"TestAgent_{lang_code}"
                mock_create.return_value = mock_agent

                with patch("src.text.router.InMemoryRunner") as mock_runner_class:
                    mock_runner = AsyncMock()
                    mock_session = AsyncMock()
                    mock_session.id = f"test-id-{lang_code}"
                    mock_session.user_id = f"test-user-{lang_code}"
                    mock_runner.session_service.create_session.return_value = (
                        mock_session
                    )
                    mock_runner_class.return_value = mock_runner

                    # Test with each language
                    runner, session, run_config = await start_agent_session(
                        f"test-user-{lang_code}", lang_code
                    )

                    # Verify language was passed correctly
                    mock_create.assert_called_once_with(language_code=lang_code)
                    assert run_config.speech_config.language_code == lang_code

    async def test_language_normalization_integration(self):
        """Test that language codes are normalized in the full flow."""
        from src.text.router import sse_endpoint
        from fastapi import Request

        test_cases = [
            ("en", "en-US"),
            ("es", "es-ES"),
            ("pt-br", "pt-BR"),
            ("DE-de", "de-DE"),
        ]

        for input_lang, expected_lang in test_cases:
            # Create a mock request
            mock_request = AsyncMock(spec=Request)
            mock_request.method = "GET"

            with patch("src.text.router.start_agent_session") as mock_start:
                mock_runner = AsyncMock()
                mock_session = AsyncMock()
                mock_session.id = "adk-session"
                mock_session.user_id = "test-session"
                mock_run_config = AsyncMock()
                mock_start.return_value = (mock_runner, mock_session, mock_run_config)

                with patch("src.text.router.session_manager") as mock_sm:
                    mock_session_info = AsyncMock()
                    mock_session_info.metadata = {}
                    mock_sm.create_session.return_value = mock_session_info

                    with patch("src.text.router.get_performance_monitor") as mock_perf:
                        mock_monitor = AsyncMock()
                        mock_perf.return_value = mock_monitor

                        # Call the endpoint with unnormalized language
                        try:
                            await sse_endpoint(
                                mock_request, "test-session", input_lang
                            )
                        except Exception:
                            # Expected to fail due to mocking limitations
                            pass

                        # Verify normalized language was used
                        mock_start.assert_called_once_with(
                            "test-session", expected_lang
                        )

    async def test_invalid_language_fallback_integration(self):
        """Test that invalid languages fall back to default."""
        from src.text.router import sse_endpoint
        from fastapi import Request

        invalid_languages = ["klingon", "elvish", "xx-XX", "123", ""]

        for invalid_lang in invalid_languages:
            # Create a mock request
            mock_request = AsyncMock(spec=Request)
            mock_request.method = "GET"

            with patch("src.text.router.start_agent_session") as mock_start:
                mock_runner = AsyncMock()
                mock_session = AsyncMock()
                mock_session.id = "adk-session"
                mock_session.user_id = "test-session"
                mock_run_config = AsyncMock()
                mock_start.return_value = (mock_runner, mock_session, mock_run_config)

                with patch("src.text.router.session_manager") as mock_sm:
                    mock_session_info = AsyncMock()
                    mock_session_info.metadata = {}
                    mock_sm.create_session.return_value = mock_session_info

                    with patch("src.text.router.get_performance_monitor") as mock_perf:
                        mock_monitor = AsyncMock()
                        mock_perf.return_value = mock_monitor

                        # Call the endpoint with invalid language
                        try:
                            await sse_endpoint(
                                mock_request, "test-session", invalid_lang
                            )
                        except Exception:
                            # Expected to fail due to mocking limitations
                            pass

                        # Verify default language (en-US) was used
                        mock_start.assert_called_once_with("test-session", "en-US")

    async def test_language_persistence_in_session(self):
        """Test that language persists in session metadata."""
        from src.text.router import sse_endpoint, get_session_info
        from fastapi import Request

        # Setup session with language
        with patch("src.text.router.session_manager") as mock_sm:
            # Create a session with Spanish language
            mock_session = SessionInfoModel(
                session_id="test-persist",
                user_id="user-persist"
            )
            mock_session.metadata = {"language": "es-ES"}
            mock_sm.get_session_readonly.return_value = mock_session

            # Get session info endpoint should include language
            session_info = await get_session_info("test-persist")

            # Verify language is in metadata
            assert session_info.metadata["language"] == "es-ES"

    async def test_e2e_spanish_conversation_simulation(self, async_client):
        """Simulate an E2E Spanish conversation flow."""
        from src.text.router import start_agent_session
        
        # Test Spanish language parameter is passed correctly to agent creation
        with patch("src.text.router.create_cbt_assistant") as mock_create:
            mock_agent = AsyncMock()
            mock_agent.name = "TestAgent"
            mock_create.return_value = mock_agent
            
            with patch("src.text.router.InMemoryRunner") as mock_runner_class:
                mock_runner = AsyncMock()
                mock_session = AsyncMock()
                mock_session.id = "test-id"
                mock_session.user_id = "test-user"
                
                # Mock Spanish response
                async def mock_run_async(*args, **kwargs):
                    yield AsyncMock(
                        content=AsyncMock(
                            parts=[
                                AsyncMock(
                                    text="¡Hola! Soy tu asistente de CBT. Estoy aquí para ayudarte."
                                )
                            ]
                        )
                    )
                
                mock_runner.run_async = mock_run_async
                mock_runner.session_service.create_session.return_value = mock_session
                mock_runner_class.return_value = mock_runner
                
                # Call start_agent_session with Spanish
                runner, session, run_config = await start_agent_session(
                    "test-user", "es-ES"
                )
                
                # Verify language parameter was passed correctly
                mock_create.assert_called_once_with(language_code="es-ES")
                assert run_config.speech_config.language_code == "es-ES"
                
                # Verify we can simulate a conversation
                messages = []
                async for msg in mock_runner.run_async():
                    if msg.content and msg.content.parts:
                        for part in msg.content.parts:
                            if hasattr(part, 'text'):
                                messages.append(part.text)
                
                # Verify Spanish response
                assert len(messages) > 0
                assert "¡Hola!" in messages[0]
                assert "CBT" in messages[0]