"""Audio utilities for voice interaction support."""

import asyncio
import logging
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class AudioConfig:
    """Audio configuration settings."""

    sample_rate: int = 16000  # 16kHz for speech processing
    channels: int = 1  # Mono
    chunk_size: int = 1024  # Buffer size in frames
    format: str = "int16"  # 16-bit PCM
    silence_threshold: float = 500.0  # RMS threshold for silence detection

    @property
    def bytes_per_sample(self) -> int:
        """Calculate bytes per sample based on format."""
        if self.format == "int16":
            return 2
        elif self.format == "float32":
            return 4
        else:
            raise ValueError(f"Unsupported format: {self.format}")

    @property
    def bytes_per_chunk(self) -> int:
        """Calculate total bytes per chunk."""
        return self.chunk_size * self.channels * self.bytes_per_sample


class AudioProcessor(ABC):
    """Abstract base class for audio processing."""

    def __init__(self, config: AudioConfig | None = None):
        self.config = config or AudioConfig()
        self._is_active = False

    @abstractmethod
    async def start(self) -> None:
        """Start audio processing."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Stop audio processing."""
        pass

    @abstractmethod
    async def process_chunk(self, chunk: bytes) -> bytes | None:
        """Process a single audio chunk."""
        pass

    def calculate_rms(self, audio_chunk: bytes) -> float:
        """Calculate root mean square (RMS) of audio chunk for volume detection."""
        if self.config.format == "int16":
            audio_array = np.frombuffer(audio_chunk, dtype=np.int16)
        else:
            raise ValueError(f"Unsupported format for RMS: {self.config.format}")

        if len(audio_array) == 0:
            return 0.0

        return float(np.sqrt(np.mean(audio_array.astype(float) ** 2)))

    def is_silence(self, audio_chunk: bytes) -> bool:
        """Check if audio chunk is silence based on RMS threshold."""
        rms = self.calculate_rms(audio_chunk)
        return rms < self.config.silence_threshold


class AudioBuffer:
    """Thread-safe audio buffer for streaming."""

    def __init__(self, max_size: int = 100):
        self.buffer: asyncio.Queue = asyncio.Queue(maxsize=max_size)
        self._closed = False

    async def put(self, chunk: bytes) -> None:
        """Add audio chunk to buffer."""
        if self._closed:
            raise RuntimeError("Buffer is closed")
        await self.buffer.put(chunk)

    async def get(self) -> bytes | None:
        """Get audio chunk from buffer."""
        if self._closed and self.buffer.empty():
            return None
        try:
            return await asyncio.wait_for(self.buffer.get(), timeout=0.1)
        except TimeoutError:
            return None if self._closed else b""

    def close(self) -> None:
        """Close the buffer."""
        self._closed = True

    @property
    def is_closed(self) -> bool:
        """Check if buffer is closed."""
        return self._closed


class NoiseReducer(AudioProcessor):
    """Simple noise reduction for audio input."""

    def __init__(
        self, config: AudioConfig | None = None, noise_gate_threshold: float = 0.02
    ):
        super().__init__(config)
        self.noise_gate_threshold = noise_gate_threshold
        self.noise_profile = None
        self.calibration_chunks: list[bytes] = []
        self.calibration_duration = 1.0  # Seconds of silence to calibrate

    async def start(self) -> None:
        """Start noise reduction."""
        self._is_active = True
        logger.info("Noise reducer started")

    async def stop(self) -> None:
        """Stop noise reduction."""
        self._is_active = False
        logger.info("Noise reducer stopped")

    async def calibrate(self, audio_chunk: bytes) -> None:
        """Calibrate noise profile from background audio."""
        self.calibration_chunks.append(audio_chunk)

        # Check if we have enough samples
        total_samples = len(self.calibration_chunks) * self.config.chunk_size
        required_samples = int(self.config.sample_rate * self.calibration_duration)

        if total_samples >= required_samples:
            # Calculate noise profile
            all_audio = b"".join(self.calibration_chunks)
            audio_array = np.frombuffer(all_audio, dtype=np.int16)
            self.noise_profile = np.mean(np.abs(audio_array))
            logger.info(f"Noise profile calibrated: {self.noise_profile}")
            self.calibration_chunks.clear()

    async def process_chunk(self, chunk: bytes) -> bytes:
        """Apply noise reduction to audio chunk."""
        if not self._is_active:
            return chunk

        # Convert to numpy array
        audio_array = np.frombuffer(chunk, dtype=np.int16).astype(np.float32)

        # Apply noise gate with calibrated profile if available
        if self.noise_profile is not None:
            # Use calibrated noise level with a margin (e.g., 1.5x noise floor)
            threshold = self.noise_profile * 1.5
        else:
            # Fall back to default threshold
            threshold = self.noise_gate_threshold * 32768

        mask = np.abs(audio_array) > threshold
        audio_array = audio_array * mask

        # Convert back to bytes
        result: bytes = audio_array.astype(np.int16).tobytes()
        return result


class VoiceActivityDetector(AudioProcessor):
    """Detect voice activity in audio stream."""

    def __init__(
        self,
        config: AudioConfig | None = None,
        energy_threshold: float = 0.01,
        min_speech_duration: float = 0.3,
        min_silence_duration: float = 0.5,
    ):
        super().__init__(config)
        self.energy_threshold = energy_threshold
        self.min_speech_duration = min_speech_duration
        self.min_silence_duration = min_silence_duration

        self.speech_buffer: list[bytes] = []
        self.is_speaking = False
        self.speech_start_time: float | None = None
        self.silence_start_time: float | None = None

        self._speech_callback: Callable | None = None
        self._silence_callback: Callable | None = None

    def set_callbacks(
        self,
        on_speech_start: Callable | None = None,
        on_speech_end: Callable | None = None,
    ) -> None:
        """Set callbacks for speech events."""
        self._speech_callback = on_speech_start
        self._silence_callback = on_speech_end

    async def start(self) -> None:
        """Start voice activity detection."""
        self._is_active = True
        logger.info("Voice activity detector started")

    async def stop(self) -> None:
        """Stop voice activity detection."""
        self._is_active = False
        logger.info("Voice activity detector stopped")

    async def process_chunk(self, chunk: bytes) -> bytes | None:
        """Process audio chunk for voice activity."""
        if not self._is_active:
            return chunk

        # Calculate energy
        audio_array = np.frombuffer(chunk, dtype=np.int16).astype(np.float32)
        energy = np.mean(np.abs(audio_array)) / 32768.0

        current_time = asyncio.get_event_loop().time()

        if energy > self.energy_threshold:
            # Voice detected
            if not self.is_speaking:
                if self.speech_start_time is None:
                    self.speech_start_time = current_time
                elif current_time - self.speech_start_time >= self.min_speech_duration:
                    self.is_speaking = True
                    if self._speech_callback:
                        await self._speech_callback()
                    logger.debug("Speech started")

            self.silence_start_time = None
            self.speech_buffer.append(chunk)

        else:
            # Silence detected
            if self.is_speaking:
                if self.silence_start_time is None:
                    self.silence_start_time = current_time
                elif (
                    current_time - self.silence_start_time >= self.min_silence_duration
                ):
                    self.is_speaking = False
                    if self._silence_callback:
                        speech_data = b"".join(self.speech_buffer)
                        await self._silence_callback(speech_data)
                    logger.debug("Speech ended")
                    self.speech_buffer.clear()

            self.speech_start_time = None

        return chunk


async def stream_audio_chunks(
    audio_source: AsyncIterator[bytes], processors: list[AudioProcessor]
) -> AsyncIterator[bytes]:
    """Stream audio through a pipeline of processors."""
    async for chunk in audio_source:
        processed_chunk: bytes | None = chunk
        for processor in processors:
            if processed_chunk is None:
                break
            result = await processor.process_chunk(processed_chunk)
            processed_chunk = result if result is not None else None

        if processed_chunk is not None:
            yield processed_chunk
