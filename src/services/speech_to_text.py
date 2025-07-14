"""Speech-to-text service for converting audio to text."""

import asyncio
import logging
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any

from ..utils.audio_utils import AudioConfig

logger = logging.getLogger(__name__)


@dataclass
class TranscriptionResult:
    """Result from speech transcription."""

    text: str
    confidence: float
    language: str
    is_final: bool = True
    alternatives: list[dict] | None = None

    def __post_init__(self):
        if self.alternatives is None:
            self.alternatives = []


class SpeechToTextService(ABC):
    """Abstract base class for speech-to-text services."""

    def __init__(self, config: AudioConfig | None = None):
        self.config = config or AudioConfig()
        self._is_initialized = False

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the STT service."""
        pass

    @abstractmethod
    async def transcribe(
        self, audio_data: bytes, language: str = "en-US"
    ) -> TranscriptionResult:
        """Transcribe audio data to text."""
        pass

    @abstractmethod
    def transcribe_stream(
        self, audio_stream: AsyncIterator[bytes], language: str = "en-US"
    ) -> AsyncIterator[TranscriptionResult]:
        """Transcribe streaming audio to text."""
        ...

    async def cleanup(self) -> None:
        """Clean up resources."""
        self._is_initialized = False


class MockSpeechToText(SpeechToTextService):
    """Mock implementation for testing."""

    def __init__(self, config: AudioConfig | None = None):
        super().__init__(config)
        self.mock_responses = [
            "I've been feeling really anxious lately",
            "Yes, especially before important meetings",
            "I think I'm catastrophizing the situation",
        ]
        self.response_index = 0

    async def initialize(self) -> None:
        """Initialize mock service."""
        self._is_initialized = True
        logger.info("Mock STT service initialized")

    async def transcribe(
        self, audio_data: bytes, language: str = "en-US"
    ) -> TranscriptionResult:
        """Return mock transcription."""
        if not self._is_initialized:
            await self.initialize()

        # Simulate processing delay
        await asyncio.sleep(0.5)

        # Return mock response
        text = self.mock_responses[self.response_index % len(self.mock_responses)]
        self.response_index += 1

        return TranscriptionResult(
            text=text, confidence=0.95, language=language, is_final=True
        )

    async def transcribe_stream(
        self, audio_stream: AsyncIterator[bytes], language: str = "en-US"
    ) -> AsyncIterator[TranscriptionResult]:
        """Stream mock transcriptions."""
        if not self._is_initialized:
            await self.initialize()

        chunks_received = 0
        partial_text = ""

        async for _chunk in audio_stream:
            chunks_received += 1

            # Simulate partial results every 5 chunks
            if chunks_received % 5 == 0:
                words = self.mock_responses[0].split()
                word_index = min(chunks_received // 5, len(words))
                partial_text = " ".join(words[:word_index])

                yield TranscriptionResult(
                    text=partial_text, confidence=0.8, language=language, is_final=False
                )

            # Final result after 20 chunks
            if chunks_received >= 20:
                yield TranscriptionResult(
                    text=self.mock_responses[0],
                    confidence=0.95,
                    language=language,
                    is_final=True,
                )
                break


class GoogleSpeechToText(SpeechToTextService):
    """Google Cloud Speech-to-Text implementation."""

    def __init__(
        self, config: AudioConfig | None = None, credentials_path: str | None = None
    ):
        super().__init__(config)
        self.credentials_path = credentials_path
        self.client: Any = None  # SpeechClient

    async def initialize(self) -> None:
        """Initialize Google STT client."""
        try:
            # Import Google Cloud Speech library
            from google.cloud import speech

            # Initialize client
            if self.credentials_path:
                from google.oauth2 import service_account

                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path
                )
                self.client = speech.SpeechClient(credentials=credentials)
            else:
                self.client = speech.SpeechClient()

            self._is_initialized = True
            logger.info("Google STT service initialized")

        except ImportError:
            logger.error(
                "Google Cloud Speech library not installed. Install with: pip install google-cloud-speech"
            )
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Google STT: {e}")
            raise

    async def transcribe(
        self, audio_data: bytes, language: str = "en-US"
    ) -> TranscriptionResult:
        """Transcribe audio using Google Speech-to-Text."""
        if not self._is_initialized:
            await self.initialize()

        from google.cloud import speech

        # Configure audio
        audio = speech.RecognitionAudio(content=audio_data)

        # Configure recognition
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=self.config.sample_rate,
            language_code=language,
            enable_automatic_punctuation=True,
            model="latest_long",
            use_enhanced=True,
        )

        # Perform recognition
        try:
            response = await asyncio.to_thread(
                self.client.recognize, config=config, audio=audio
            )

            if not response.results:
                return TranscriptionResult(
                    text="", confidence=0.0, language=language, is_final=True
                )

            # Get best result
            result = response.results[0]
            best_alternative = result.alternatives[0]

            # Get other alternatives
            alternatives = [
                {"text": alt.transcript, "confidence": alt.confidence}
                for alt in result.alternatives[1:]
            ]

            return TranscriptionResult(
                text=best_alternative.transcript,
                confidence=best_alternative.confidence,
                language=language,
                is_final=True,
                alternatives=alternatives,
            )

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise

    async def transcribe_stream(
        self, audio_stream: AsyncIterator[bytes], language: str = "en-US"
    ) -> AsyncIterator[TranscriptionResult]:
        """Stream transcription using Google Speech-to-Text."""
        if not self._is_initialized:
            await self.initialize()

        from google.cloud import speech

        # Configure streaming recognition
        config = speech.StreamingRecognitionConfig(
            config=speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=self.config.sample_rate,
                language_code=language,
                enable_automatic_punctuation=True,
                model="latest_long",
                use_enhanced=True,
            ),
            interim_results=True,
            single_utterance=False,
        )

        # Create request generator
        async def request_generator():
            yield speech.StreamingRecognizeRequest(streaming_config=config)
            async for chunk in audio_stream:
                yield speech.StreamingRecognizeRequest(audio_content=chunk)

        # Perform streaming recognition
        try:
            responses = await asyncio.to_thread(
                self.client.streaming_recognize, request_generator()
            )

            for response in responses:
                for result in response.results:
                    if not result.alternatives:
                        continue

                    best_alternative = result.alternatives[0]

                    yield TranscriptionResult(
                        text=best_alternative.transcript,
                        confidence=best_alternative.confidence,
                        language=language,
                        is_final=result.is_final,
                    )

        except Exception as e:
            logger.error(f"Streaming transcription failed: {e}")
            raise


def create_stt_service(
    provider: str = "mock", config: AudioConfig | None = None, **kwargs
) -> SpeechToTextService:
    """Factory function to create STT service."""
    if provider == "mock":
        return MockSpeechToText(config)
    elif provider == "google":
        return GoogleSpeechToText(config, **kwargs)
    else:
        raise ValueError(f"Unknown STT provider: {provider}")
