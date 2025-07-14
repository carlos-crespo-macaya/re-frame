"""Text-to-speech service for converting text to audio."""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from ..utils.audio_utils import AudioConfig

logger = logging.getLogger(__name__)


@dataclass
class VoiceConfig:
    """Configuration for TTS voice."""

    name: str
    language: str
    gender: str = "neutral"
    pitch: float = 0.0  # -20.0 to 20.0
    speaking_rate: float = 1.0  # 0.25 to 4.0
    volume_gain_db: float = 0.0  # -96.0 to 16.0


class TextToSpeechService(ABC):
    """Abstract base class for text-to-speech services."""

    def __init__(self, config: AudioConfig | None = None):
        self.config = config or AudioConfig()
        self._is_initialized = False
        self.available_voices: dict[str, list[VoiceConfig]] = {}

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the TTS service."""
        pass

    @abstractmethod
    async def synthesize(
        self,
        text: str,
        voice_config: VoiceConfig | None = None,
        language: str = "en-US",
    ) -> bytes:
        """Synthesize text to audio."""
        pass

    @abstractmethod
    async def get_available_voices(
        self, language: str | None = None
    ) -> list[VoiceConfig]:
        """Get available voices for a language."""
        pass

    async def cleanup(self) -> None:
        """Clean up resources."""
        self._is_initialized = False

    def get_default_voice(self, language: str = "en-US") -> VoiceConfig:
        """Get default voice for a language."""
        if language.startswith("es"):
            return VoiceConfig(
                name="es-US-Standard-A", language="es-US", gender="neutral"
            )
        else:
            return VoiceConfig(
                name="en-US-Standard-C", language="en-US", gender="neutral"
            )


class MockTextToSpeech(TextToSpeechService):
    """Mock implementation for testing."""

    def __init__(self, config: AudioConfig | None = None):
        super().__init__(config)
        self.mock_voices = {
            "en-US": [
                VoiceConfig("en-US-Mock-A", "en-US", "female"),
                VoiceConfig("en-US-Mock-B", "en-US", "male"),
                VoiceConfig("en-US-Mock-C", "en-US", "neutral"),
            ],
            "es-US": [
                VoiceConfig("es-US-Mock-A", "es-US", "female"),
                VoiceConfig("es-US-Mock-B", "es-US", "male"),
            ],
        }

    async def initialize(self) -> None:
        """Initialize mock service."""
        self._is_initialized = True
        self.available_voices = self.mock_voices
        logger.info("Mock TTS service initialized")

    async def synthesize(
        self,
        text: str,
        voice_config: VoiceConfig | None = None,
        language: str = "en-US",
    ) -> bytes:
        """Generate mock audio data."""
        if not self._is_initialized:
            await self.initialize()

        # Simulate processing delay
        await asyncio.sleep(0.3)

        # Generate mock audio data (silence)
        # Duration proportional to text length
        duration = len(text) * 0.05  # 50ms per character
        num_samples = int(duration * self.config.sample_rate)

        # Create a simple sine wave for testing
        import numpy as np

        frequency = 440  # A4 note
        t = np.linspace(0, duration, num_samples)
        wave = np.sin(2 * np.pi * frequency * t) * 0.1  # Low volume

        # Add some envelope to make it sound more natural
        envelope = np.exp(-t * 2)  # Exponential decay
        wave = wave * envelope

        # Convert to int16
        audio_data = (wave * 32767).astype(np.int16)

        return audio_data.tobytes()  # type: ignore[no-any-return]

    async def get_available_voices(
        self, language: str | None = None
    ) -> list[VoiceConfig]:
        """Get mock voices."""
        if not self._is_initialized:
            await self.initialize()

        if language:
            return self.available_voices.get(language, [])

        # Return all voices
        all_voices = []
        for voices in self.available_voices.values():
            all_voices.extend(voices)
        return all_voices


class GoogleTextToSpeech(TextToSpeechService):
    """Google Cloud Text-to-Speech implementation."""

    def __init__(
        self, config: AudioConfig | None = None, credentials_path: str | None = None
    ):
        super().__init__(config)
        self.credentials_path = credentials_path
        self.client: Any = None  # TextToSpeechClient

    async def initialize(self) -> None:
        """Initialize Google TTS client."""
        try:
            # Import Google Cloud TTS library
            from google.cloud import texttospeech

            # Initialize client
            if self.credentials_path:
                from google.oauth2 import service_account

                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path
                )
                self.client = texttospeech.TextToSpeechClient(credentials=credentials)
            else:
                self.client = texttospeech.TextToSpeechClient()

            # Load available voices
            await self._load_available_voices()

            self._is_initialized = True
            logger.info("Google TTS service initialized")

        except ImportError:
            logger.error(
                "Google Cloud Text-to-Speech library not installed. Install with: pip install google-cloud-texttospeech"
            )
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Google TTS: {e}")
            raise

    async def _load_available_voices(self) -> None:
        """Load available voices from Google."""
        from google.cloud import texttospeech

        try:
            response = await asyncio.to_thread(self.client.list_voices)

            for voice in response.voices:
                language = voice.language_codes[0]

                if language not in self.available_voices:
                    self.available_voices[language] = []

                # Map Google's SSML gender to our gender string
                gender_map = {
                    texttospeech.SsmlVoiceGender.FEMALE: "female",
                    texttospeech.SsmlVoiceGender.MALE: "male",
                    texttospeech.SsmlVoiceGender.NEUTRAL: "neutral",
                }

                self.available_voices[language].append(
                    VoiceConfig(
                        name=voice.name,
                        language=language,
                        gender=gender_map.get(voice.ssml_gender, "neutral"),
                    )
                )

        except Exception as e:
            logger.error(f"Failed to load voices: {e}")

    async def synthesize(
        self,
        text: str,
        voice_config: VoiceConfig | None = None,
        language: str = "en-US",
    ) -> bytes:
        """Synthesize text using Google Text-to-Speech."""
        if not self._is_initialized:
            await self.initialize()

        from google.cloud import texttospeech

        # Use provided voice config or default
        if not voice_config:
            voice_config = self.get_default_voice(language)

        # Set up synthesis input
        synthesis_input = texttospeech.SynthesisInput(text=text)

        # Set up voice
        voice = texttospeech.VoiceSelectionParams(
            language_code=voice_config.language, name=voice_config.name
        )

        # Set up audio config
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            sample_rate_hertz=self.config.sample_rate,
            speaking_rate=voice_config.speaking_rate,
            pitch=voice_config.pitch,
            volume_gain_db=voice_config.volume_gain_db,
        )

        try:
            # Perform synthesis
            response = await asyncio.to_thread(
                self.client.synthesize_speech,
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config,
            )

            return response.audio_content  # type: ignore[no-any-return]

        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            raise

    async def get_available_voices(
        self, language: str | None = None
    ) -> list[VoiceConfig]:
        """Get available voices from Google."""
        if not self._is_initialized:
            await self.initialize()

        if language:
            return self.available_voices.get(language, [])

        # Return all voices
        all_voices = []
        for voices in self.available_voices.values():
            all_voices.extend(voices)
        return all_voices


def create_tts_service(
    provider: str = "mock", config: AudioConfig | None = None, **kwargs
) -> TextToSpeechService:
    """Factory function to create TTS service."""
    if provider == "mock":
        return MockTextToSpeech(config)
    elif provider == "google":
        return GoogleTextToSpeech(config, **kwargs)
    else:
        raise ValueError(f"Unknown TTS provider: {provider}")
