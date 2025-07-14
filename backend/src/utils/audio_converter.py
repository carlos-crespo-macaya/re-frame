"""Audio format conversion utilities for handling browser audio inputs."""

import io
import logging
import struct
import time
import wave
from typing import ClassVar

import numpy as np
from scipy import signal

logger = logging.getLogger(__name__)


class AudioConverter:
    """Handles audio format conversion for different browser inputs."""

    SUPPORTED_INPUT_FORMATS: ClassVar[dict[str, str]] = {
        "audio/wav": "wav",
        "audio/webm": "webm",
        "audio/mp4": "mp4",
        "audio/mpeg": "mp3",
        "audio/ogg": "ogg",
    }

    TARGET_SAMPLE_RATE = 16000  # 16kHz for ADK
    TARGET_CHANNELS = 1  # Mono
    TARGET_SAMPLE_WIDTH = 2  # 16-bit

    @classmethod
    def convert_to_pcm(cls, audio_data: bytes, mime_type: str) -> tuple[bytes, dict]:
        """Convert audio data to 16kHz mono PCM format.

        Args:
            audio_data: Raw audio bytes
            mime_type: MIME type of the input audio

        Returns:
            Tuple of (converted PCM bytes, metrics dict)
        """
        start_time = time.time()
        metrics = {
            "input_format": mime_type,
            "input_size": len(audio_data),
            "conversion_time": 0,
            "output_sample_rate": cls.TARGET_SAMPLE_RATE,
            "output_channels": cls.TARGET_CHANNELS,
            "output_size": 0,
            "error": None,
        }

        try:
            # Handle WAV format (most common from browsers)
            if mime_type == "audio/wav":
                pcm_data = cls._convert_wav_to_pcm(audio_data)
            else:
                # For now, only support WAV. Other formats would require
                # additional libraries like ffmpeg-python
                raise ValueError(f"Unsupported audio format: {mime_type}")

            metrics["output_size"] = len(pcm_data)
            metrics["conversion_time"] = (time.time() - start_time) * 1000  # ms

            logger.info(
                f"Audio conversion completed: {mime_type} -> PCM "
                f"({metrics['input_size']} -> {metrics['output_size']} bytes) "
                f"in {metrics['conversion_time']:.1f}ms"
            )

            return pcm_data, metrics

        except Exception as e:
            logger.error(f"Audio conversion failed: {e}")
            metrics["error"] = str(e)
            metrics["conversion_time"] = (time.time() - start_time) * 1000

            # Return empty PCM data as fallback
            return b"", metrics

    @classmethod
    def _convert_wav_to_pcm(cls, wav_data: bytes) -> bytes:
        """Convert WAV audio to 16kHz mono PCM.

        Args:
            wav_data: WAV file bytes

        Returns:
            PCM audio bytes
        """
        # Read WAV file
        with (
            io.BytesIO(wav_data) as wav_buffer,
            wave.open(wav_buffer, "rb") as wav_file,
        ):
            params = wav_file.getparams()
            frames = wav_file.readframes(params.nframes)

            # Log input parameters
            logger.debug(
                f"Input WAV: {params.framerate}Hz, "
                f"{params.nchannels} channels, "
                f"{params.sampwidth} bytes/sample"
            )

            # Convert to numpy array
            audio_array: np.ndarray
            if params.sampwidth == 1:
                temp_array = np.frombuffer(frames, dtype=np.uint8)
                # Convert to signed
                audio_array = temp_array.astype(np.float32) - 128
                audio_array = audio_array / 128.0
            elif params.sampwidth == 2:
                temp_array = np.frombuffer(frames, dtype=np.int16)
                audio_array = temp_array.astype(np.float32) / 32768.0
            elif params.sampwidth == 3:
                # 24-bit audio needs special handling
                temp_array = cls._read_24bit_samples(frames)
                audio_array = temp_array.astype(np.float32) / 8388608.0
            elif params.sampwidth == 4:
                temp_array = np.frombuffer(frames, dtype=np.int32)
                audio_array = temp_array.astype(np.float32) / 2147483648.0
            else:
                raise ValueError(f"Unsupported sample width: {params.sampwidth}")

            # Handle multi-channel to mono conversion
            if params.nchannels > 1:
                # Reshape to (samples, channels)
                audio_array = audio_array.reshape(-1, params.nchannels)
                # Average channels to get mono
                audio_array = np.mean(audio_array, axis=1)

            # Resample if needed
            if params.framerate != cls.TARGET_SAMPLE_RATE:
                # Calculate resampling ratio
                resample_ratio = cls.TARGET_SAMPLE_RATE / params.framerate
                num_output_samples = int(len(audio_array) * resample_ratio)

                # Use scipy's resample for better quality
                audio_array = signal.resample(audio_array, num_output_samples)

                logger.debug(
                    f"Resampled from {params.framerate}Hz to "
                    f"{cls.TARGET_SAMPLE_RATE}Hz"
                )

            # Convert back to 16-bit PCM
            audio_array = np.clip(audio_array * 32768, -32768, 32767)
            pcm_data = audio_array.astype(np.int16).tobytes()

            return pcm_data

    @staticmethod
    def _read_24bit_samples(data: bytes) -> np.ndarray:
        """Read 24-bit samples from bytes."""
        # 24-bit samples are 3 bytes each
        num_samples = len(data) // 3
        samples = np.zeros(num_samples, dtype=np.int32)

        for i in range(num_samples):
            # Read 3 bytes and interpret as signed 24-bit integer
            b1, b2, b3 = struct.unpack("BBB", data[i * 3 : (i + 1) * 3])
            # Combine bytes (little-endian)
            value = b1 | (b2 << 8) | (b3 << 16)
            # Sign extend from 24-bit to 32-bit
            if value & 0x800000:  # If sign bit is set
                value = value - 0x1000000  # Subtract 2^24 instead of OR with 0xFF000000
            samples[i] = value

        return samples

    @classmethod
    def validate_pcm_data(cls, pcm_data: bytes) -> bool:
        """Validate that PCM data is in expected format.

        Args:
            pcm_data: PCM audio bytes

        Returns:
            True if valid, False otherwise
        """
        if not pcm_data:
            return False

        # Check if length is even (16-bit samples)
        if len(pcm_data) % 2 != 0:
            logger.warning("PCM data length is not even")
            return False

        # Check if we can interpret as int16 array
        try:
            audio_array = np.frombuffer(pcm_data, dtype=np.int16)
            # Basic sanity check - audio should have some variation
            if np.all(audio_array == 0):
                logger.warning("PCM data is all zeros")
                return False
            return True
        except Exception as e:
            logger.error(f"Failed to validate PCM data: {e}")
            return False
