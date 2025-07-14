"""Tests for audio format conversion utilities."""

import io
import struct
import wave

import numpy as np

from src.utils.audio_converter import AudioConverter


class TestAudioConverter:
    """Test cases for AudioConverter class."""

    @staticmethod
    def create_test_wav(sample_rate=48000, duration=1.0, frequency=440, channels=1):
        """Create a test WAV file with a sine wave.

        Args:
            sample_rate: Sample rate in Hz
            duration: Duration in seconds
            frequency: Frequency of sine wave in Hz
            channels: Number of channels

        Returns:
            bytes: WAV file data
        """
        # Generate sine wave
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio_data = np.sin(2 * np.pi * frequency * t)

        # Scale to 16-bit range
        audio_data = (audio_data * 32767).astype(np.int16)

        # Handle stereo
        if channels == 2:
            # Create stereo by duplicating the channel
            audio_data = np.column_stack((audio_data, audio_data))

        # Create WAV file in memory
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, "wb") as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())

        wav_buffer.seek(0)
        return wav_buffer.read()

    def test_convert_48khz_to_16khz(self):
        """Test conversion from 48kHz to 16kHz."""
        # Create 48kHz test audio
        test_wav = self.create_test_wav(sample_rate=48000, duration=1.0)

        # Convert to PCM
        pcm_data, metrics = AudioConverter.convert_to_pcm(test_wav, "audio/wav")

        # Verify conversion succeeded
        assert pcm_data is not None
        assert len(pcm_data) > 0
        assert metrics["error"] is None

        # Verify output is 16kHz (16000 samples per second * 2 bytes per sample)
        expected_size = 16000 * 2  # 1 second at 16kHz, 16-bit
        assert len(pcm_data) == expected_size

        # Verify metrics
        assert metrics["output_sample_rate"] == 16000
        assert metrics["output_channels"] == 1
        assert metrics["conversion_time"] > 0

    def test_convert_stereo_to_mono(self):
        """Test conversion from stereo to mono."""
        # Create stereo test audio
        test_wav = self.create_test_wav(sample_rate=16000, channels=2)

        # Convert to PCM
        pcm_data, metrics = AudioConverter.convert_to_pcm(test_wav, "audio/wav")

        # Verify conversion succeeded
        assert pcm_data is not None
        assert len(pcm_data) > 0
        assert metrics["error"] is None

        # Verify output is mono
        assert metrics["output_channels"] == 1

    def test_convert_various_sample_rates(self):
        """Test conversion from various sample rates."""
        sample_rates = [8000, 16000, 22050, 44100, 48000]

        for sample_rate in sample_rates:
            test_wav = self.create_test_wav(sample_rate=sample_rate, duration=0.5)
            pcm_data, metrics = AudioConverter.convert_to_pcm(test_wav, "audio/wav")

            # Verify conversion succeeded
            assert pcm_data is not None
            assert len(pcm_data) > 0
            assert metrics["error"] is None

            # Verify output is 16kHz
            expected_size = int(16000 * 0.5 * 2)  # 0.5 seconds at 16kHz, 16-bit
            assert len(pcm_data) == expected_size

    def test_conversion_performance(self):
        """Test that conversion is fast enough for 5 second audio."""
        # Create 5 second 48kHz stereo audio (worst case)
        test_wav = self.create_test_wav(sample_rate=48000, duration=5.0, channels=2)

        # Convert to PCM
        pcm_data, metrics = AudioConverter.convert_to_pcm(test_wav, "audio/wav")

        # Verify conversion succeeded
        assert pcm_data is not None
        assert metrics["error"] is None

        # Verify conversion time is under 100ms
        assert (
            metrics["conversion_time"] < 100
        ), f"Conversion took {metrics['conversion_time']}ms, expected < 100ms"

    def test_validate_pcm_data(self):
        """Test PCM data validation."""
        # Valid PCM data
        valid_pcm = np.random.randint(-32768, 32767, 1000, dtype=np.int16).tobytes()
        assert AudioConverter.validate_pcm_data(valid_pcm) is True

        # Empty data
        assert AudioConverter.validate_pcm_data(b"") is False

        # Odd length (invalid for 16-bit samples)
        assert AudioConverter.validate_pcm_data(b"123") is False

        # All zeros (invalid audio)
        zeros_pcm = np.zeros(1000, dtype=np.int16).tobytes()
        assert AudioConverter.validate_pcm_data(zeros_pcm) is False

    def test_unsupported_format(self):
        """Test handling of unsupported audio formats."""
        # Try to convert with unsupported format
        pcm_data, metrics = AudioConverter.convert_to_pcm(
            b"fake audio data", "audio/mp3"
        )

        # Should return empty data with error
        assert pcm_data == b""
        assert metrics["error"] is not None
        assert "Unsupported audio format" in metrics["error"]

    def test_corrupted_wav(self):
        """Test handling of corrupted WAV data."""
        # Create corrupted WAV data
        corrupted_wav = b"RIFF1234WAVEfmt corrupted data"

        pcm_data, metrics = AudioConverter.convert_to_pcm(corrupted_wav, "audio/wav")

        # Should handle gracefully
        assert pcm_data == b""
        assert metrics["error"] is not None

    def test_24bit_wav_conversion(self):
        """Test conversion of 24-bit WAV files."""
        # Create 24-bit test data
        samples = []
        for i in range(1000):
            # Generate 24-bit sample value
            value = int(np.sin(2 * np.pi * i / 100) * 8388607)  # 24-bit max
            # Pack as 3 bytes (little-endian)
            samples.append(struct.pack("<i", value)[:3])

        sample_data = b"".join(samples)

        # Test 24-bit sample reading
        audio_array = AudioConverter._read_24bit_samples(sample_data)
        assert len(audio_array) == 1000
        assert audio_array.dtype == np.int32
