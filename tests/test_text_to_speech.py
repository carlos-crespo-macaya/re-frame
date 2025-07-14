"""Tests for text-to-speech service."""

from unittest.mock import AsyncMock, Mock, patch

import numpy as np
import pytest

from src.services.text_to_speech import (
    GoogleTextToSpeech,
    MockTextToSpeech,
    VoiceConfig,
    create_tts_service,
)
from src.utils.audio_utils import AudioConfig


class TestVoiceConfig:
    """Test VoiceConfig dataclass."""

    def test_default_config(self):
        """Test default voice configuration."""
        config = VoiceConfig(name="test-voice", language="en-US")

        assert config.name == "test-voice"
        assert config.language == "en-US"
        assert config.gender == "neutral"
        assert config.pitch == 0.0
        assert config.speaking_rate == 1.0
        assert config.volume_gain_db == 0.0

    def test_custom_config(self):
        """Test custom voice configuration."""
        config = VoiceConfig(
            name="custom-voice",
            language="es-US",
            gender="female",
            pitch=2.0,
            speaking_rate=1.2,
            volume_gain_db=-3.0,
        )

        assert config.gender == "female"
        assert config.pitch == 2.0
        assert config.speaking_rate == 1.2
        assert config.volume_gain_db == -3.0


class TestMockTextToSpeech:
    """Test MockTextToSpeech implementation."""

    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test mock TTS initialization."""
        tts = MockTextToSpeech()
        assert not tts._is_initialized

        await tts.initialize()
        assert tts._is_initialized
        assert len(tts.available_voices) > 0

    @pytest.mark.asyncio
    async def test_synthesize(self):
        """Test mock speech synthesis."""
        tts = MockTextToSpeech()
        await tts.initialize()

        text = "Hello, this is a test."
        audio_data = await tts.synthesize(text)

        assert isinstance(audio_data, bytes)
        assert len(audio_data) > 0

        # Check audio format (int16)
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        assert len(audio_array) > 0

        # Duration should be proportional to text length
        expected_duration = len(text) * 0.05
        expected_samples = int(expected_duration * 16000)
        assert len(audio_array) == expected_samples

    @pytest.mark.asyncio
    async def test_synthesize_with_voice_config(self):
        """Test synthesis with specific voice config."""
        tts = MockTextToSpeech()

        voice_config = VoiceConfig(
            name="es-US-Mock-A", language="es-US", gender="female", speaking_rate=1.5
        )

        audio_data = await tts.synthesize(
            "Hola, esto es una prueba.", voice_config=voice_config, language="es-US"
        )

        assert isinstance(audio_data, bytes)
        assert len(audio_data) > 0

    @pytest.mark.asyncio
    async def test_get_available_voices(self):
        """Test getting available voices."""
        tts = MockTextToSpeech()
        await tts.initialize()

        # Get all voices
        all_voices = await tts.get_available_voices()
        assert len(all_voices) > 0
        assert all(isinstance(v, VoiceConfig) for v in all_voices)

        # Get English voices
        en_voices = await tts.get_available_voices("en-US")
        assert len(en_voices) == 3
        assert all(v.language == "en-US" for v in en_voices)

        # Get Spanish voices
        es_voices = await tts.get_available_voices("es-US")
        assert len(es_voices) == 2
        assert all(v.language == "es-US" for v in es_voices)

    @pytest.mark.asyncio
    async def test_get_default_voice(self):
        """Test getting default voice."""
        tts = MockTextToSpeech()

        # English default
        en_voice = tts.get_default_voice("en-US")
        assert en_voice.name == "en-US-Standard-C"
        assert en_voice.language == "en-US"

        # Spanish default
        es_voice = tts.get_default_voice("es-US")
        assert es_voice.name == "es-US-Standard-A"
        assert es_voice.language == "es-US"

    @pytest.mark.asyncio
    async def test_cleanup(self):
        """Test cleanup."""
        tts = MockTextToSpeech()
        await tts.initialize()
        assert tts._is_initialized

        await tts.cleanup()
        assert not tts._is_initialized


class TestGoogleTextToSpeech:
    """Test GoogleTextToSpeech implementation."""

    @pytest.mark.asyncio
    async def test_initialization_without_library(self):
        """Test initialization when Google Cloud library is not installed."""
        # Mock the import to simulate library not installed
        import sys

        with patch.dict(sys.modules, {"google.cloud.texttospeech": None}):
            tts = GoogleTextToSpeech()

            with pytest.raises(ImportError):
                await tts.initialize()

    @pytest.mark.asyncio
    async def test_initialization_with_mock_client(self):
        """Test initialization with mocked Google client."""
        mock_client = Mock()

        # Mock voice list response
        mock_voice = Mock()
        mock_voice.name = "en-US-Standard-A"
        mock_voice.language_codes = ["en-US"]
        mock_voice.ssml_gender = 1  # FEMALE

        mock_response = Mock()
        mock_response.voices = [mock_voice]

        with (
            patch(
                "google.cloud.texttospeech.TextToSpeechClient", return_value=mock_client
            ),
            patch("google.cloud.texttospeech.SsmlVoiceGender") as mock_gender,
            patch("asyncio.to_thread", AsyncMock(return_value=mock_response)),
        ):
            # Mock gender enum values
            mock_gender.FEMALE = 1
            mock_gender.MALE = 2
            mock_gender.NEUTRAL = 3

            tts = GoogleTextToSpeech()
            await tts.initialize()

            assert tts._is_initialized
            assert tts.client == mock_client
            assert "en-US" in tts.available_voices

    @pytest.mark.skip(reason="Complex mocking scenario with asyncio.to_thread")
    @pytest.mark.asyncio
    async def test_synthesize_with_mock(self):
        """Test synthesis with mocked Google client."""
        mock_response = Mock()
        mock_response.audio_content = b"mock_audio_data"

        mock_client = Mock()
        mock_client.synthesize_speech = Mock(return_value=mock_response)
        mock_list_response = Mock(voices=[])

        # Create a mock AudioEncoding enum with LINEAR16 attribute
        mock_audio_encoding = Mock()
        mock_audio_encoding.LINEAR16 = "LINEAR16"

        with (
            patch(
                "google.cloud.texttospeech.TextToSpeechClient", return_value=mock_client
            ),
            patch("google.cloud.texttospeech.SynthesisInput"),
            patch("google.cloud.texttospeech.VoiceSelectionParams"),
            patch("google.cloud.texttospeech.AudioConfig"),
            patch("google.cloud.texttospeech.AudioEncoding", mock_audio_encoding),
            patch(
                "asyncio.to_thread",
                AsyncMock(side_effect=[mock_list_response, mock_response]),
            ),
        ):
            tts = GoogleTextToSpeech()
            await tts.initialize()

            audio_data = await tts.synthesize("Hello world")

            assert audio_data == b"mock_audio_data"
            mock_client.synthesize_speech.assert_called_once()

    @pytest.mark.asyncio
    async def test_synthesize_with_voice_config(self):
        """Test synthesis with specific voice config."""
        mock_response = Mock()
        mock_response.audio_content = b"mock_audio_data"

        mock_tts = Mock()
        mock_client = Mock()
        mock_client.synthesize_speech = Mock(return_value=mock_response)
        mock_client.list_voices = Mock(return_value=Mock(voices=[]))
        mock_tts.TextToSpeechClient.return_value = mock_client

        # Mock required classes
        mock_tts.SynthesisInput = Mock
        mock_tts.VoiceSelectionParams = Mock
        mock_tts.AudioConfig = Mock
        mock_tts.AudioEncoding.LINEAR16 = "LINEAR16"

        voice_config = VoiceConfig(
            name="es-US-Neural2-A",
            language="es-US",
            speaking_rate=1.2,
            pitch=2.0,
            volume_gain_db=-3.0,
        )

        mock_list_response = Mock(voices=[])

        with (
            patch(
                "google.cloud.texttospeech.TextToSpeechClient", return_value=mock_client
            ),
            patch("google.cloud.texttospeech.SynthesisInput"),
            patch("google.cloud.texttospeech.VoiceSelectionParams"),
            patch("google.cloud.texttospeech.AudioConfig"),
            patch("google.cloud.texttospeech.AudioEncoding") as mock_encoding,
            patch(
                "asyncio.to_thread",
                AsyncMock(side_effect=[mock_list_response, mock_response]),
            ),
        ):
            # Mock AudioEncoding enum
            mock_encoding.LINEAR16 = "LINEAR16"

            tts = GoogleTextToSpeech()
            await tts.initialize()

            audio_data = await tts.synthesize("Hola mundo", voice_config=voice_config)

            assert audio_data == b"mock_audio_data"


class TestCreateTTSService:
    """Test TTS service factory."""

    def test_create_mock_service(self):
        """Test creating mock service."""
        service = create_tts_service("mock")
        assert isinstance(service, MockTextToSpeech)

    def test_create_google_service(self):
        """Test creating Google service."""
        with patch("src.services.text_to_speech.GoogleTextToSpeech"):
            service = create_tts_service("google", credentials_path="/path/to/creds")
            assert service is not None

    def test_create_unknown_service(self):
        """Test creating unknown service."""
        with pytest.raises(ValueError, match="Unknown TTS provider"):
            create_tts_service("unknown")

    def test_create_with_custom_config(self):
        """Test creating service with custom config."""
        config = AudioConfig(sample_rate=48000)
        service = create_tts_service("mock", config=config)

        assert service.config.sample_rate == 48000
