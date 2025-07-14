"""Tests for audio utilities."""

import asyncio
from unittest.mock import AsyncMock, Mock

import numpy as np
import pytest

from src.utils.audio_utils import (
    AudioBuffer,
    AudioConfig,
    NoiseReducer,
    VoiceActivityDetector,
    stream_audio_chunks,
)


class TestAudioConfig:
    """Test AudioConfig class."""

    def test_default_config(self):
        """Test default audio configuration."""
        config = AudioConfig()
        assert config.sample_rate == 16000
        assert config.channels == 1
        assert config.chunk_size == 1024
        assert config.format == "int16"
        assert config.silence_threshold == 500.0

    def test_bytes_per_sample(self):
        """Test bytes per sample calculation."""
        config = AudioConfig(format="int16")
        assert config.bytes_per_sample == 2

        config = AudioConfig(format="float32")
        assert config.bytes_per_sample == 4

        config = AudioConfig(format="invalid")
        with pytest.raises(ValueError):
            _ = config.bytes_per_sample

    def test_bytes_per_chunk(self):
        """Test bytes per chunk calculation."""
        config = AudioConfig(chunk_size=1024, channels=1, format="int16")
        assert config.bytes_per_chunk == 1024 * 1 * 2


class TestAudioBuffer:
    """Test AudioBuffer class."""

    @pytest.mark.asyncio
    async def test_put_and_get(self):
        """Test putting and getting audio chunks."""
        buffer = AudioBuffer(max_size=10)

        # Put chunks
        chunk1 = b"audio_data_1"
        chunk2 = b"audio_data_2"

        await buffer.put(chunk1)
        await buffer.put(chunk2)

        # Get chunks
        result1 = await buffer.get()
        result2 = await buffer.get()

        assert result1 == chunk1
        assert result2 == chunk2

    @pytest.mark.asyncio
    async def test_close(self):
        """Test closing the buffer."""
        buffer = AudioBuffer()

        await buffer.put(b"test_data")
        assert not buffer.is_closed

        buffer.close()
        assert buffer.is_closed

        # Should raise error when putting after close
        with pytest.raises(RuntimeError):
            await buffer.put(b"more_data")

        # Should return None when getting from closed empty buffer
        await buffer.get()  # Get the existing data
        result = await buffer.get()
        assert result is None

    @pytest.mark.asyncio
    async def test_timeout_on_empty(self):
        """Test timeout when getting from empty buffer."""
        buffer = AudioBuffer()

        result = await buffer.get()
        assert result == b""  # Empty bytes, not None


class TestNoiseReducer:
    """Test NoiseReducer class."""

    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test noise reducer initialization."""
        reducer = NoiseReducer()

        await reducer.start()
        assert reducer._is_active

        await reducer.stop()
        assert not reducer._is_active

    @pytest.mark.asyncio
    async def test_calibration(self):
        """Test noise calibration."""
        config = AudioConfig(sample_rate=16000, chunk_size=160)  # 10ms chunks
        reducer = NoiseReducer(config, noise_gate_threshold=0.02)

        # Generate 1 second of calibration data (100 chunks)
        for _ in range(100):
            # Create low-amplitude noise
            noise = np.random.randint(-100, 100, size=160, dtype=np.int16)
            await reducer.calibrate(noise.tobytes())

        assert reducer.noise_profile is not None
        assert reducer.noise_profile > 0

    @pytest.mark.asyncio
    async def test_process_chunk(self):
        """Test audio chunk processing."""
        reducer = NoiseReducer(noise_gate_threshold=0.1)
        await reducer.start()

        # Create audio with both signal and noise
        signal = np.sin(2 * np.pi * 440 * np.linspace(0, 0.1, 1600)) * 10000
        noise = np.random.randint(-1000, 1000, size=1600)
        audio = (signal + noise).astype(np.int16)

        processed = await reducer.process_chunk(audio.tobytes())

        assert processed is not None
        assert len(processed) == len(audio.tobytes())

        # Verify noise reduction occurred
        processed_array = np.frombuffer(processed, dtype=np.int16)
        assert np.mean(np.abs(processed_array)) <= np.mean(np.abs(audio))


class TestVoiceActivityDetector:
    """Test VoiceActivityDetector class."""

    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test VAD initialization."""
        vad = VoiceActivityDetector()

        await vad.start()
        assert vad._is_active

        await vad.stop()
        assert not vad._is_active

    @pytest.mark.asyncio
    async def test_speech_detection(self):
        """Test speech detection."""
        vad = VoiceActivityDetector(
            energy_threshold=0.01, min_speech_duration=0.1, min_silence_duration=0.2
        )

        speech_started = False
        speech_data = None

        async def on_speech_start():
            nonlocal speech_started
            speech_started = True

        async def on_speech_end(data):
            nonlocal speech_data
            speech_data = data

        vad.set_callbacks(on_speech_start, on_speech_end)
        await vad.start()

        # Simulate speech with high energy
        high_energy = (
            np.sin(2 * np.pi * 440 * np.linspace(0, 0.5, 8000)) * 5000
        ).astype(np.int16)

        # Process multiple chunks to trigger speech start
        for i in range(10):
            chunk = high_energy[i * 800 : (i + 1) * 800].tobytes()
            await vad.process_chunk(chunk)
            await asyncio.sleep(0.05)

        assert speech_started

        # Simulate silence to trigger speech end
        silence = np.zeros(1600, dtype=np.int16)
        for _ in range(10):
            await vad.process_chunk(silence.tobytes())
            await asyncio.sleep(0.05)

        assert speech_data is not None
        assert len(speech_data) > 0

    @pytest.mark.asyncio
    async def test_no_speech_for_short_bursts(self):
        """Test that short bursts don't trigger speech detection."""
        vad = VoiceActivityDetector(
            energy_threshold=0.01,
            min_speech_duration=0.5,  # Require 500ms of speech
            min_silence_duration=0.1,
        )

        speech_started = False

        async def on_speech_start():
            nonlocal speech_started
            speech_started = True

        vad.set_callbacks(on_speech_start=on_speech_start)
        await vad.start()

        # Short burst of high energy (only 200ms)
        high_energy = (
            np.sin(2 * np.pi * 440 * np.linspace(0, 0.2, 3200)) * 5000
        ).astype(np.int16)

        for i in range(4):
            chunk = high_energy[i * 800 : (i + 1) * 800].tobytes()
            await vad.process_chunk(chunk)
            await asyncio.sleep(0.05)

        # Then silence
        silence = np.zeros(800, dtype=np.int16).tobytes()
        await vad.process_chunk(silence)

        assert not speech_started  # Should not trigger due to short duration


class TestStreamAudioChunks:
    """Test audio streaming function."""

    @pytest.mark.asyncio
    async def test_streaming_with_processors(self):
        """Test streaming audio through processors."""

        # Create mock audio source
        async def audio_source():
            for i in range(5):
                yield f"chunk_{i}".encode()

        # Create mock processors
        processor1 = Mock()
        processor1.process_chunk = AsyncMock(side_effect=lambda x: x + b"_p1")

        processor2 = Mock()
        processor2.process_chunk = AsyncMock(side_effect=lambda x: x + b"_p2")

        # Stream through processors
        chunks = []
        async for chunk in stream_audio_chunks(
            audio_source(), [processor1, processor2]
        ):
            chunks.append(chunk)

        # Verify processing chain
        assert len(chunks) == 5
        assert chunks[0] == b"chunk_0_p1_p2"
        assert chunks[4] == b"chunk_4_p1_p2"

        # Verify all processors were called
        assert processor1.process_chunk.call_count == 5
        assert processor2.process_chunk.call_count == 5

    @pytest.mark.asyncio
    async def test_streaming_with_none_result(self):
        """Test streaming when processor returns None."""

        async def audio_source():
            for i in range(3):
                yield f"chunk_{i}".encode()

        # Processor that filters out chunk_1
        processor = Mock()
        processor.process_chunk = AsyncMock(
            side_effect=lambda x: None if b"chunk_1" in x else x
        )

        chunks = []
        async for chunk in stream_audio_chunks(audio_source(), [processor]):
            chunks.append(chunk)

        # Should only get 2 chunks (chunk_1 filtered out)
        assert len(chunks) == 2
        assert chunks[0] == b"chunk_0"
        assert chunks[1] == b"chunk_2"
