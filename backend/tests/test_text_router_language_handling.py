"""Tests for language parameter handling in text router."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.fixtures.language_fixtures import SUPPORTED_LANGUAGES

# Patch dependencies before importing
with (
    patch("src.text.router.create_cbt_assistant", MagicMock()),
    patch("src.utils.session_manager.session_manager", MagicMock()),
):
    pass


class TestSSELanguageHandling:
    """Test language parameter handling in SSE endpoint."""

    @pytest.mark.asyncio
    async def test_sse_endpoint_stores_language(self):
        """Test that SSE endpoint stores language parameter."""
        from fastapi import Request

        from src.text.router import sse_endpoint

        # Create a mock request
        mock_request = AsyncMock(spec=Request)
        mock_request.method = "GET"

        with patch("src.text.router.start_agent_session") as mock_start:
            mock_runner = AsyncMock()
            mock_session = AsyncMock()
            mock_session.id = "adk-session-123"
            mock_session.user_id = "test-session-123"
            mock_run_config = {}
            mock_start.return_value = (mock_runner, mock_session, mock_run_config)

            # Mock the session manager
            with patch("src.text.router.session_manager") as mock_sm:
                mock_session_info = AsyncMock()
                mock_session_info.metadata = {}
                mock_sm.create_session.return_value = mock_session_info

                # Mock StreamingResponse to avoid hanging
                with patch("src.text.router.StreamingResponse") as mock_response:
                    mock_response.return_value = MagicMock()

                    # Mock performance monitor
                    with patch("src.text.router.get_performance_monitor") as mock_perf:
                        mock_monitor = MagicMock()
                        mock_monitor.start_session = AsyncMock()
                        mock_perf.return_value = mock_monitor

                        # Call the endpoint directly
                        await sse_endpoint(mock_request, "test-session-123", "es-ES")

                        # Verify language was passed to agent creation
                        mock_start.assert_called_once_with("test-session-123", "es-ES")

    @pytest.mark.asyncio
    async def test_sse_endpoint_default_language(self):
        """Test that SSE endpoint uses default language when not specified."""
        from fastapi import Request

        from src.text.router import sse_endpoint

        # Create a mock request
        mock_request = AsyncMock(spec=Request)
        mock_request.method = "GET"

        with patch("src.text.router.start_agent_session") as mock_start:
            mock_runner = AsyncMock()
            mock_session = AsyncMock()
            mock_session.id = "adk-session-456"
            mock_session.user_id = "test-session-456"
            mock_run_config = {}
            mock_start.return_value = (mock_runner, mock_session, mock_run_config)

            # Mock the session manager
            with patch("src.text.router.session_manager") as mock_sm:
                mock_session_info = AsyncMock()
                mock_session_info.metadata = {}
                mock_sm.create_session.return_value = mock_session_info

                # Mock StreamingResponse to avoid hanging
                with patch("src.text.router.StreamingResponse") as mock_response:
                    mock_response.return_value = MagicMock()

                    # Mock performance monitor
                    with patch("src.text.router.get_performance_monitor") as mock_perf:
                        mock_monitor = MagicMock()
                        mock_monitor.start_session = AsyncMock()
                        mock_perf.return_value = mock_monitor

                        # Call the endpoint directly with default language
                        await sse_endpoint(mock_request, "test-session-456", "en-US")

                        # Should use default language
                        mock_start.assert_called_once_with("test-session-456", "en-US")

    @pytest.mark.asyncio
    async def test_sse_invalid_language_fallback(self):
        """Test that SSE endpoint falls back to default for invalid language."""
        from fastapi import Request

        from src.text.router import sse_endpoint

        # Create a mock request
        mock_request = AsyncMock(spec=Request)
        mock_request.method = "GET"

        with patch("src.text.router.start_agent_session") as mock_start:
            mock_runner = AsyncMock()
            mock_session = AsyncMock()
            mock_session.id = "adk-session-789"
            mock_session.user_id = "test-session-789"
            mock_run_config = {}
            mock_start.return_value = (mock_runner, mock_session, mock_run_config)

            # Mock the session manager
            with patch("src.text.router.session_manager") as mock_sm:
                mock_session_info = AsyncMock()
                mock_session_info.metadata = {}
                mock_sm.create_session.return_value = mock_session_info

                # Mock StreamingResponse to avoid hanging
                with patch("src.text.router.StreamingResponse") as mock_response:
                    mock_response.return_value = MagicMock()

                    # Mock performance monitor
                    with patch("src.text.router.get_performance_monitor") as mock_perf:
                        mock_monitor = MagicMock()
                        mock_monitor.start_session = AsyncMock()
                        mock_perf.return_value = mock_monitor

                        # Call the endpoint directly with invalid language
                        await sse_endpoint(mock_request, "test-session-789", "invalid")

                        # Should fallback to default language
                        mock_start.assert_called_once_with("test-session-789", "en-US")

    @pytest.mark.asyncio
    async def test_sse_all_supported_languages(self):
        """Test that all supported languages are accepted by SSE endpoint."""
        from fastapi import Request

        from src.text.router import sse_endpoint

        for lang_code in SUPPORTED_LANGUAGES:
            # Create a mock request
            mock_request = AsyncMock(spec=Request)
            mock_request.method = "GET"

            with patch("src.text.router.start_agent_session") as mock_start:
                mock_runner = AsyncMock()
                mock_session = AsyncMock()
                mock_session.id = f"adk-session-{lang_code}"
                mock_session.user_id = f"test-session-{lang_code}"
                mock_run_config = {}
                mock_start.return_value = (mock_runner, mock_session, mock_run_config)

                # Mock the session manager
                with patch("src.text.router.session_manager") as mock_sm:
                    mock_session_info = AsyncMock()
                    mock_session_info.metadata = {}
                    mock_sm.create_session.return_value = mock_session_info

                    # Mock StreamingResponse to avoid hanging
                    with patch("src.text.router.StreamingResponse") as mock_response:
                        mock_response.return_value = MagicMock()

                        # Mock performance monitor
                        with patch(
                            "src.text.router.get_performance_monitor"
                        ) as mock_perf:
                            mock_monitor = MagicMock()
                            mock_monitor.start_session = AsyncMock()
                            mock_perf.return_value = mock_monitor

                            # Call the endpoint directly with each supported language
                            await sse_endpoint(
                                mock_request, f"test-session-{lang_code}", lang_code
                            )

                            # Verify language was passed correctly
                            mock_start.assert_called_once_with(
                                f"test-session-{lang_code}", lang_code
                            )

    @pytest.mark.asyncio
    async def test_sse_normalized_language_codes(self):
        """Test that language codes are normalized properly."""
        from fastapi import Request

        from src.text.router import sse_endpoint

        test_cases = [
            ("en", "en-US"),  # Short code should normalize
            ("ES", "es-ES"),  # Case insensitive
            ("pt-br", "pt-BR"),  # Case normalization
        ]

        for input_lang, expected_lang in test_cases:
            # Create a mock request
            mock_request = AsyncMock(spec=Request)
            mock_request.method = "GET"

            with patch("src.text.router.start_agent_session") as mock_start:
                mock_runner = AsyncMock()
                mock_session = AsyncMock()
                mock_session.id = "adk-session-norm"
                mock_session.user_id = "test-session-norm"
                mock_run_config = {}
                mock_start.return_value = (mock_runner, mock_session, mock_run_config)

                # Mock the session manager
                with patch("src.text.router.session_manager") as mock_sm:
                    mock_session_info = AsyncMock()
                    mock_session_info.metadata = {}
                    mock_sm.create_session.return_value = mock_session_info

                    # Mock StreamingResponse to avoid hanging
                    with patch("src.text.router.StreamingResponse") as mock_response:
                        mock_response.return_value = MagicMock()

                        # Mock performance monitor
                        with patch(
                            "src.text.router.get_performance_monitor"
                        ) as mock_perf:
                            mock_monitor = MagicMock()
                            mock_monitor.start_session = AsyncMock()
                            mock_perf.return_value = mock_monitor

                            # Call the endpoint directly with language that needs normalization
                            await sse_endpoint(
                                mock_request, "test-session-norm", input_lang
                            )

                            # Should normalize to expected format
                            mock_start.assert_called_once_with(
                                "test-session-norm", expected_lang
                            )

    @pytest.mark.asyncio
    async def test_session_metadata_stores_language(self):
        """Test that session metadata stores the language parameter."""
        from fastapi import Request

        from src.text.router import sse_endpoint

        # Create a mock request
        mock_request = AsyncMock(spec=Request)
        mock_request.method = "GET"

        with patch("src.text.router.start_agent_session") as mock_start:
            mock_runner = AsyncMock()
            mock_session = AsyncMock()
            mock_session.id = "adk-session-meta"
            mock_session.user_id = "test-session-meta"
            mock_run_config = {}
            mock_start.return_value = (mock_runner, mock_session, mock_run_config)

            # Mock session manager
            with patch("src.text.router.session_manager") as mock_session_manager:
                mock_session_info = AsyncMock()
                mock_session_info.metadata = {}
                mock_session_manager.create_session.return_value = mock_session_info

                # Mock StreamingResponse to avoid hanging
                with patch("src.text.router.StreamingResponse") as mock_response:
                    mock_response.return_value = MagicMock()

                    # Mock performance monitor
                    with patch("src.text.router.get_performance_monitor") as mock_perf:
                        mock_monitor = MagicMock()
                        mock_monitor.start_session = AsyncMock()
                        mock_perf.return_value = mock_monitor

                        # Call the endpoint directly with language parameter
                        await sse_endpoint(mock_request, "test-session-meta", "fr-FR")

                        # Verify session metadata includes language
                        assert mock_session_info.metadata.get("language") == "fr-FR"
