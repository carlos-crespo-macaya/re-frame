"""Tests for language detection endpoint."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from src.models import LanguageDetectionRequest
from src.utils.rate_limiter import RateLimiter


class TestLanguageDetectionEndpoint:
    """Test language detection endpoint functionality."""

    @pytest.mark.asyncio
    async def test_detect_english_text(self):
        """Test that language detection endpoint returns English (deprecated)."""

        with patch("src.text.router.language_limiter") as mock_limiter:
            mock_limiter.check_request = AsyncMock(return_value=True)

            from src.text.router import detect_language_endpoint

            # Create mock request objects
            request = LanguageDetectionRequest(text="Hello, how are you today?")
            mock_req = MagicMock()
            mock_req.client.host = "127.0.0.1"

            result = await detect_language_endpoint(request, mock_req)

            assert result.status == "success"
            assert result.language == "en"
            assert result.confidence == 1.0
            assert "deprecated" in result.message.lower()

    @pytest.mark.asyncio
    async def test_detect_spanish_text(self):
        """Test that Spanish text still returns English (deprecated)."""
        with patch("src.text.router.language_limiter") as mock_limiter:
            mock_limiter.check_request = AsyncMock(return_value=True)

            from src.text.router import detect_language_endpoint

            request = LanguageDetectionRequest(text="Hola, ¿cómo estás hoy?")
            mock_req = MagicMock()
            mock_req.client.host = "127.0.0.1"

            result = await detect_language_endpoint(request, mock_req)

            # Always returns English now
            assert result.status == "success"
            assert result.language == "en"
            assert result.confidence == 1.0
            assert "deprecated" in result.message.lower()

    @pytest.mark.asyncio
    async def test_detect_multiple_languages(self):
        """Test that mixed language text still returns English (deprecated)."""
        with patch("src.text.router.language_limiter") as mock_limiter:
            mock_limiter.check_request = AsyncMock(return_value=True)

            from src.text.router import detect_language_endpoint

            request = LanguageDetectionRequest(text="Bonjour comment allez-vous")
            mock_req = MagicMock()
            mock_req.client.host = "127.0.0.1"

            result = await detect_language_endpoint(request, mock_req)

            # Always returns English now
            assert result.status == "success"
            assert result.language == "en"
            assert result.confidence == 1.0
            assert "deprecated" in result.message.lower()

    @pytest.mark.asyncio
    async def test_no_supported_language_fallback(self):
        """Test that unsupported languages return English (deprecated)."""
        with patch("src.text.router.language_limiter") as mock_limiter:
            mock_limiter.check_request = AsyncMock(return_value=True)

            from src.text.router import detect_language_endpoint

            request = LanguageDetectionRequest(text="Bonjour comment allez-vous")
            mock_req = MagicMock()
            mock_req.client.host = "127.0.0.1"

            result = await detect_language_endpoint(request, mock_req)

            # Always returns English now
            assert result.status == "success"
            assert result.language == "en"
            assert result.confidence == 1.0
            assert "deprecated" in result.message.lower()

    @pytest.mark.asyncio
    async def test_detection_failure_fallback(self):
        """Test that detection failures still return English (deprecated)."""
        with patch("src.text.router.language_limiter") as mock_limiter:
            mock_limiter.check_request = AsyncMock(return_value=True)

            from src.text.router import detect_language_endpoint

            request = LanguageDetectionRequest(text="???")
            mock_req = MagicMock()
            mock_req.client.host = "127.0.0.1"

            result = await detect_language_endpoint(request, mock_req)

            # Always returns English now
            assert result.status == "success"
            assert result.language == "en"
            assert result.confidence == 1.0
            assert "deprecated" in result.message.lower()

    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Test rate limiting blocks requests."""
        with (patch("src.text.router.language_limiter") as mock_limiter,):
            mock_limiter.check_request = AsyncMock(return_value=False)

            from src.text.router import detect_language_endpoint

            request = LanguageDetectionRequest(text="Hello")
            mock_req = MagicMock()
            mock_req.client.host = "127.0.0.1"

            with pytest.raises(HTTPException) as exc_info:
                await detect_language_endpoint(request, mock_req)

            assert exc_info.value.status_code == 429
            assert "Rate limit exceeded" in exc_info.value.detail
            assert exc_info.value.headers["Retry-After"] == "60"

    @pytest.mark.asyncio
    async def test_no_client_host(self):
        """Test handling when client host is not available."""
        with patch("src.text.router.language_limiter") as mock_limiter:
            mock_limiter.check_request = AsyncMock(return_value=True)

            from src.text.router import detect_language_endpoint

            request = LanguageDetectionRequest(text="Hello")
            mock_req = MagicMock()
            mock_req.client = None  # No client info

            result = await detect_language_endpoint(request, mock_req)

            # Should still work, using "unknown" as client_host
            mock_limiter.check_request.assert_called_once_with("unknown")
            assert result.status == "success"
            assert result.language == "en"
            assert result.confidence == 1.0
            assert "deprecated" in result.message.lower()


class TestRateLimiter:
    """Test the RateLimiter utility."""

    @pytest.mark.asyncio
    async def test_rate_limiter_allows_requests_within_limit(self):
        """Test that requests within limit are allowed."""
        limiter = RateLimiter(max_requests=3, window_seconds=60)

        client_id = "127.0.0.1"

        # First 3 requests should be allowed
        assert await limiter.check_request(client_id) is True
        assert await limiter.check_request(client_id) is True
        assert await limiter.check_request(client_id) is True

        # 4th request should be blocked
        assert await limiter.check_request(client_id) is False

    @pytest.mark.asyncio
    async def test_rate_limiter_resets_after_window(self):
        """Test that rate limiter resets after time window."""
        limiter = RateLimiter(max_requests=2, window_seconds=1)

        client_id = "127.0.0.1"

        # Use up the limit
        assert await limiter.check_request(client_id) is True
        assert await limiter.check_request(client_id) is True
        assert await limiter.check_request(client_id) is False

        # Wait for window to expire
        import asyncio

        await asyncio.sleep(1.1)

        # Should be allowed again
        assert await limiter.check_request(client_id) is True

    @pytest.mark.asyncio
    async def test_rate_limiter_tracks_clients_separately(self):
        """Test that different clients are tracked separately."""
        limiter = RateLimiter(max_requests=2, window_seconds=60)

        client1 = "127.0.0.1"
        client2 = "192.168.1.1"

        # Use up limit for client1
        assert await limiter.check_request(client1) is True
        assert await limiter.check_request(client1) is True
        assert await limiter.check_request(client1) is False

        # client2 should still be allowed
        assert await limiter.check_request(client2) is True
        assert await limiter.check_request(client2) is True
        assert await limiter.check_request(client2) is False

    def test_rate_limiter_get_stats(self):
        """Test getting rate limiter statistics."""
        limiter = RateLimiter(max_requests=3, window_seconds=60)

        client_id = "127.0.0.1"

        # Initially, no requests
        current, reset_time = limiter.get_stats(client_id)
        assert current == 0
        assert reset_time == 0

        # After one request
        import asyncio

        asyncio.run(limiter.check_request(client_id))
        current, reset_time = limiter.get_stats(client_id)
        assert current == 1
        assert 0 <= reset_time <= 60
