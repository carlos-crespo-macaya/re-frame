"""Pre-recorded audio samples for testing."""

import base64
from pathlib import Path

import numpy as np


class AudioSamples:
    """Pre-recorded audio samples for testing."""

    _samples_cache: dict[str, str] = {}

    @classmethod
    def get_sample(cls, phrase: str, corrupted: bool = False) -> str:
        """Get base64-encoded audio for common test phrases.

        Args:
            phrase: The phrase to get audio for
            corrupted: Whether to return corrupted audio for error testing

        Returns:
            Base64-encoded audio data
        """
        if phrase in cls._samples_cache and not corrupted:
            return cls._samples_cache[phrase]

        samples = {
            "hello": "fixtures/audio/hello_16khz_pcm.raw",
            "i_feel_anxious": "fixtures/audio/i_feel_anxious_16khz_pcm.raw",
            "help_me_reframe": "fixtures/audio/help_me_reframe_16khz_pcm.raw",
            "silence": "fixtures/audio/silence_16khz_pcm.raw",
            "noisy_speech": "fixtures/audio/speech_with_noise_16khz_pcm.raw",
            "clipped_audio": "fixtures/audio/clipped_speech_16khz_pcm.raw",
        }

        audio_path = Path(__file__).parent / samples.get(phrase, samples["hello"])

        if not audio_path.exists():
            # Generate synthetic audio if file doesn't exist
            audio_data = cls._generate_synthetic_audio(phrase)
        else:
            with audio_path.open("rb") as f:
                audio_data = f.read()

        if corrupted:
            # Corrupt the audio data for error testing
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            audio_array[::10] = 32767  # Add clipping
            audio_data = audio_array.tobytes()

        encoded = base64.b64encode(audio_data).decode()
        cls._samples_cache[phrase] = encoded
        return encoded

    @staticmethod
    def _generate_synthetic_audio(phrase: str) -> bytes:
        """Generate synthetic audio for testing.

        Args:
            phrase: The phrase to generate audio for

        Returns:
            Raw PCM audio bytes
        """
        duration = 1.0  # seconds
        sample_rate = 16000
        samples = int(duration * sample_rate)

        # Generate simple tone for testing
        t = np.linspace(0, duration, samples)
        frequency = 440  # A4 note
        audio = np.sin(2 * np.pi * frequency * t)

        # Add some variation based on phrase
        if phrase == "silence":
            audio = np.zeros_like(audio)
        elif phrase == "noisy_speech":
            # Add white noise
            noise = np.random.normal(0, 0.1, samples)
            audio = audio * 0.7 + noise * 0.3
        elif phrase == "clipped_audio":
            # Amplify to cause clipping
            audio = audio * 2.0
            audio = np.clip(audio, -1.0, 1.0)

        # Convert to 16-bit PCM
        audio_int16 = (audio * 32767).astype(np.int16)
        return audio_int16.tobytes()
