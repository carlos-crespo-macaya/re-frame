"""Mock implementations for audio services used in testing."""

import base64
import hashlib


class MockSpeechToText:
    """Mock speech-to-text service for testing."""

    def __init__(self):
        self.responses: dict[str, str] = {}

    def register_response(self, audio_base64: str, transcript: str):
        """Register a response for a given audio sample.

        Args:
            audio_base64: Base64-encoded audio data
            transcript: The transcript to return for this audio
        """
        # Hash the decoded bytes, not the base64 string
        audio_bytes = base64.b64decode(audio_base64)
        audio_hash = hashlib.md5(audio_bytes).hexdigest()[:10]
        self.responses[audio_hash] = transcript

    async def transcribe(self, audio_data: bytes) -> str:
        """Transcribe audio data using pre-registered responses.

        Args:
            audio_data: Raw audio bytes

        Returns:
            The registered transcript or "Unknown audio"
        """
        audio_hash = hashlib.md5(audio_data).hexdigest()[:10]
        return self.responses.get(audio_hash, "Unknown audio")


class MockTextToSpeech:
    """Mock text-to-speech service for testing."""

    def __init__(self):
        self.synthesis_calls = []

    async def synthesize(self, text: str, voice_config=None) -> bytes:
        """Mock synthesize method that returns dummy audio data.

        Args:
            text: Text to synthesize
            voice_config: Optional voice configuration

        Returns:
            Mock audio data
        """
        self.synthesis_calls.append({"text": text, "voice_config": voice_config})
        # Return dummy PCM audio data (silence)
        return b"\x00" * 1600  # 100ms of silence at 16kHz
