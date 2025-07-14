"""Tests for speech-to-text service."""

import asyncio
import sys
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.services.speech_to_text import (
    GoogleSpeechToText,
    MockSpeechToText,
    TranscriptionResult,
    create_stt_service,
)
from src.utils.audio_utils import AudioConfig


class TestTranscriptionResult:
    """Test TranscriptionResult dataclass."""

    def test_basic_result(self):
        """Test basic transcription result."""
        result = TranscriptionResult(
            text="Hello world", confidence=0.95, language="en-US"
        )

        assert result.text == "Hello world"
        assert result.confidence == 0.95
        assert result.language == "en-US"
        assert result.is_final is True
        assert result.alternatives == []

    def test_with_alternatives(self):
        """Test result with alternatives."""
        alternatives = [
            {"text": "Hello word", "confidence": 0.85},
            {"text": "Hell world", "confidence": 0.70},
        ]

        result = TranscriptionResult(
            text="Hello world",
            confidence=0.95,
            language="en-US",
            is_final=False,
            alternatives=alternatives,
        )

        assert result.alternatives == alternatives
        assert not result.is_final


class TestMockSpeechToText:
    """Test MockSpeechToText implementation."""

    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test mock STT initialization."""
        stt = MockSpeechToText()
        assert not stt._is_initialized

        await stt.initialize()
        assert stt._is_initialized

    @pytest.mark.asyncio
    async def test_transcribe(self):
        """Test mock transcription."""
        stt = MockSpeechToText()

        # First transcription
        result1 = await stt.transcribe(b"audio_data_1")
        assert result1.text == "I've been feeling really anxious lately"
        assert result1.confidence == 0.95
        assert result1.language == "en-US"
        assert result1.is_final

        # Second transcription (should cycle through responses)
        result2 = await stt.transcribe(b"audio_data_2")
        assert result2.text == "Yes, especially before important meetings"

        # Test Spanish
        result3 = await stt.transcribe(b"audio_data_3", language="es-US")
        assert result3.language == "es-US"

    @pytest.mark.asyncio
    async def test_transcribe_stream(self):
        """Test mock streaming transcription."""
        stt = MockSpeechToText()

        # Create mock audio stream
        async def audio_stream():
            for i in range(25):  # Send 25 chunks
                yield f"chunk_{i}".encode()
                await asyncio.sleep(0.01)

        results = []
        async for result in stt.transcribe_stream(audio_stream()):
            results.append(result)

        # Should have partial results and one final result
        assert len(results) > 1

        # Check partial results
        partial_results = [r for r in results if not r.is_final]
        assert len(partial_results) > 0
        assert all(r.confidence == 0.8 for r in partial_results)

        # Check final result
        final_results = [r for r in results if r.is_final]
        assert len(final_results) == 1
        assert final_results[0].text == "I've been feeling really anxious lately"
        assert final_results[0].confidence == 0.95

    @pytest.mark.asyncio
    async def test_cleanup(self):
        """Test cleanup."""
        stt = MockSpeechToText()
        await stt.initialize()
        assert stt._is_initialized

        await stt.cleanup()
        assert not stt._is_initialized


class TestGoogleSpeechToText:
    """Test GoogleSpeechToText implementation."""

    @pytest.mark.asyncio
    async def test_initialization_without_library(self):
        """Test initialization when Google Cloud library is not installed."""
        # Mock the import to simulate library not installed

        with patch.dict(sys.modules, {"google.cloud.speech": None}):
            stt = GoogleSpeechToText()

            with pytest.raises(ImportError):
                await stt.initialize()

    @pytest.mark.asyncio
    async def test_initialization_with_mock_client(self):
        """Test initialization with mocked Google client."""
        mock_client = Mock()

        with patch("google.cloud.speech.SpeechClient", return_value=mock_client):
            stt = GoogleSpeechToText()
            await stt.initialize()

            assert stt._is_initialized
            assert stt.client == mock_client

    @pytest.mark.asyncio
    async def test_transcribe_with_mock(self):
        """Test transcription with mocked Google client."""
        # Create mock response
        mock_alternative = Mock()
        mock_alternative.transcript = "Test transcription"
        mock_alternative.confidence = 0.92

        mock_result = Mock()
        mock_result.alternatives = [mock_alternative]

        mock_response = Mock()
        mock_response.results = [mock_result]

        # Setup mocks
        mock_speech = Mock()
        mock_client = Mock()
        mock_client.recognize = Mock(return_value=mock_response)
        mock_speech.SpeechClient.return_value = mock_client

        with (
            patch("google.cloud.speech.SpeechClient", return_value=mock_client),
            patch("google.cloud.speech.RecognitionConfig") as mock_config,
            patch("google.cloud.speech.RecognitionAudio"),
            patch("asyncio.to_thread", AsyncMock(return_value=mock_response)),
        ):
            # Mock the AudioEncoding enum
            mock_config.AudioEncoding.LINEAR16 = "LINEAR16"

            stt = GoogleSpeechToText()
            await stt.initialize()

            result = await stt.transcribe(b"audio_data")

            assert result.text == "Test transcription"
            assert result.confidence == 0.92
            assert result.is_final

    @pytest.mark.asyncio
    async def test_transcribe_empty_response(self):
        """Test transcription with empty response."""
        mock_response = Mock()
        mock_response.results = []

        mock_speech = Mock()
        mock_client = Mock()
        mock_client.recognize = Mock(return_value=mock_response)
        mock_speech.SpeechClient.return_value = mock_client

        with (
            patch("google.cloud.speech.SpeechClient", return_value=mock_client),
            patch("google.cloud.speech.RecognitionConfig") as mock_config,
            patch("google.cloud.speech.RecognitionAudio"),
            patch("asyncio.to_thread", AsyncMock(return_value=mock_response)),
        ):
            # Mock the AudioEncoding enum
            mock_config.AudioEncoding.LINEAR16 = "LINEAR16"

            stt = GoogleSpeechToText()
            await stt.initialize()

            result = await stt.transcribe(b"audio_data")

            assert result.text == ""
            assert result.confidence == 0.0
            assert result.is_final


class TestCreateSTTService:
    """Test STT service factory."""

    def test_create_mock_service(self):
        """Test creating mock service."""
        service = create_stt_service("mock")
        assert isinstance(service, MockSpeechToText)

    def test_create_google_service(self):
        """Test creating Google service."""
        with patch("src.services.speech_to_text.GoogleSpeechToText"):
            service = create_stt_service("google", credentials_path="/path/to/creds")
            assert service is not None

    def test_create_unknown_service(self):
        """Test creating unknown service."""
        with pytest.raises(ValueError, match="Unknown STT provider"):
            create_stt_service("unknown")

    def test_create_with_custom_config(self):
        """Test creating service with custom config."""
        config = AudioConfig(sample_rate=48000)
        service = create_stt_service("mock", config=config)

        assert service.config.sample_rate == 48000
