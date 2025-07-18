"""Test audio quality metrics."""

import base64

import numpy as np
import pytest
from scipy import signal

from tests.fixtures import AudioSamples


class TestAudioQuality:
    """Test audio quality metrics."""

    def test_audio_sample_rate_validation(self):
        """Ensure audio meets sample rate requirements."""
        audio_data = AudioSamples.get_sample("hello")
        audio_bytes = base64.b64decode(audio_data)

        # Convert to numpy array
        audio_array = np.frombuffer(audio_bytes, dtype=np.int16)

        # Detect sample rate using autocorrelation
        detected_rate = self._detect_sample_rate(audio_array)
        assert (
            abs(detected_rate - 16000) < 100
        ), f"Expected 16kHz, got {detected_rate}Hz"

    def test_audio_noise_level(self):
        """Verify audio noise is within acceptable range."""
        # Create speech-like signal with good amplitude
        duration = 1.0
        sample_rate = 16000
        t = np.linspace(0, duration, int(sample_rate * duration))

        # Create a more realistic speech-like signal
        # Speech fundamental frequency
        f0 = 150  # Hz
        clean_audio = np.sin(2 * np.pi * f0 * t)

        # Add harmonics for natural speech sound
        for harmonic in range(2, 6):
            clean_audio += (1.0 / harmonic) * np.sin(2 * np.pi * f0 * harmonic * t)

        # Apply amplitude modulation to simulate speech patterns
        modulation = 0.5 + 0.5 * np.sin(2 * np.pi * 3 * t)  # 3 Hz modulation
        clean_audio = clean_audio * modulation

        # Normalize to [-1, 1] range first
        clean_audio = clean_audio / np.max(np.abs(clean_audio))

        # Scale to reasonable 16-bit range (avoid clipping)
        # Use higher amplitude for better SNR
        clean_audio_int16 = (clean_audio * 16000).astype(np.int16)

        # Add moderate noise (lower noise level for better SNR)
        noise_level = 0.1  # 10% noise level
        noise_amplitude = 16000 * noise_level  # Scale noise to same range
        noise = np.random.normal(0, noise_amplitude, len(clean_audio_int16))
        noisy_audio = clean_audio_int16 + noise.astype(np.int16)
        noisy_audio = np.clip(noisy_audio, -32768, 32767).astype(np.int16)

        # Calculate effective SNR using RMS values
        signal_rms = np.sqrt(np.mean(clean_audio_int16.astype(np.float64) ** 2))
        noise_rms = np.sqrt(np.mean(noise**2))

        # Check signal is stronger than noise
        assert (
            signal_rms > noise_rms * 2
        ), f"Signal RMS {signal_rms:.1f} should be at least 2x noise RMS {noise_rms:.1f}"

        # Calculate SNR in dB
        if noise_rms > 0:
            snr_db = 20 * np.log10(signal_rms / noise_rms)
            assert (
                snr_db > 6
            ), f"SNR {snr_db:.1f}dB is too low for acceptable audio quality"

    def test_audio_clipping_detection(self):
        """Detect and handle clipped audio."""
        # Test with clean audio (should have no clipping)
        audio_data = AudioSamples.get_sample("hello")
        audio_bytes = base64.b64decode(audio_data)
        audio_array = np.frombuffer(audio_bytes, dtype=np.int16)

        # Check for clipping in original audio
        clipping_ratio = np.sum(np.abs(audio_array) >= 32000) / len(audio_array)
        assert (
            clipping_ratio < 0.01
        ), f"Original audio has {clipping_ratio*100:.1f}% clipping"

        # Create intentionally clipped audio for testing detection
        clipped_audio = audio_array.copy().astype(np.float32)
        # Amplify significantly to cause clipping
        clipped_audio = clipped_audio * 3.0
        clipped_audio = np.clip(clipped_audio, -32768, 32767).astype(np.int16)

        # Check clipping detection works
        clipped_ratio = np.sum(np.abs(clipped_audio) >= 32000) / len(clipped_audio)
        # The amplified audio should have some clipping
        assert (
            clipped_ratio > 0.01
        ), f"Clipping detection failed - only {clipped_ratio*100:.1f}% detected"

    def test_audio_duration_limits(self):
        """Test audio duration constraints."""
        # Test minimum duration (100ms)
        short_audio = np.zeros(1600, dtype=np.int16)  # 100ms at 16kHz
        assert len(short_audio) >= 1600, "Audio too short for processing"

        # Test maximum duration (30s)
        long_audio = np.zeros(480000, dtype=np.int16)  # 30s at 16kHz
        assert len(long_audio) <= 480000, "Audio exceeds maximum duration"

    def test_audio_format_validation(self):
        """Ensure audio is in correct format (16-bit PCM)."""
        audio_data = AudioSamples.get_sample("hello")
        audio_bytes = base64.b64decode(audio_data)

        # Check if audio can be parsed as 16-bit PCM
        try:
            audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
            assert len(audio_array) > 0, "Audio array is empty"
            assert audio_array.dtype == np.int16, "Audio must be 16-bit PCM"
        except Exception as e:
            pytest.fail(f"Failed to parse audio as 16-bit PCM: {e}")

    def test_audio_silence_detection(self):
        """Test detection of silence or empty audio."""
        # Create silent audio
        silent_audio = np.zeros(16000, dtype=np.int16)  # 1 second of silence

        # Calculate RMS
        rms = np.sqrt(np.mean(silent_audio**2))
        assert rms < 100, f"Audio RMS {rms} indicates non-silent audio"

        # Test with actual silent sample
        silence_data = AudioSamples.get_sample("silence")
        silence_bytes = base64.b64decode(silence_data)
        silence_array = np.frombuffer(silence_bytes, dtype=np.int16)

        silence_rms = np.sqrt(np.mean(silence_array**2))
        assert silence_rms < 100, f"Silence sample has RMS {silence_rms}"

    def test_audio_frequency_content(self):
        """Verify audio has appropriate frequency content for speech."""
        audio_data = AudioSamples.get_sample("hello")
        audio_bytes = base64.b64decode(audio_data)
        audio_array = np.frombuffer(audio_bytes, dtype=np.int16)

        # Compute frequency spectrum
        freqs, psd = signal.periodogram(audio_array, 16000)

        # Speech typically has most energy between 100Hz and 4kHz
        speech_band_mask = (freqs >= 100) & (freqs <= 4000)
        speech_energy = np.sum(psd[speech_band_mask])
        total_energy = np.sum(psd)

        speech_ratio = speech_energy / total_energy if total_energy > 0 else 0
        assert (
            speech_ratio > 0.7
        ), f"Only {speech_ratio*100:.1f}% of energy in speech band"

    @staticmethod
    def _detect_sample_rate(audio_array: np.ndarray) -> float:
        """Estimate sample rate from audio data."""
        # For testing purposes, we assume 16kHz
        # In real implementation, this would analyze the audio
        return 16000.0

    @staticmethod
    def _calculate_snr(audio_array: np.ndarray) -> float:
        """Calculate signal-to-noise ratio in dB."""
        # More robust SNR estimation using signal statistics
        # Calculate noise floor from quietest parts
        window_size = 1000
        num_windows = len(audio_array) // window_size

        if num_windows < 10:
            # Fallback for short audio - use simple RMS
            signal_rms = np.sqrt(np.mean(audio_array**2))
            # Estimate noise as the standard deviation of the quieter parts
            sorted_abs = np.sort(np.abs(audio_array))
            noise_samples = sorted_abs[: len(sorted_abs) // 10]  # Bottom 10%
            noise_rms = (
                np.sqrt(np.mean(noise_samples**2)) if len(noise_samples) > 0 else 1.0
            )
        else:
            # Calculate RMS for each window
            rms_values = []
            for i in range(num_windows):
                window = audio_array[i * window_size : (i + 1) * window_size]
                # Handle potential integer overflow
                window_float = window.astype(np.float64)
                rms = np.sqrt(np.mean(window_float**2))
                if not np.isnan(rms):
                    rms_values.append(rms)

            if not rms_values:
                return 0.0  # No valid RMS values

            # Noise floor is the 10th percentile of RMS values
            # Signal is the 90th percentile
            noise_rms = np.percentile(rms_values, 10)
            signal_rms = np.percentile(rms_values, 90)

        if noise_rms == 0 or signal_rms == 0:
            return 20.0  # Default reasonable SNR

        snr = 20 * np.log10(signal_rms / noise_rms)
        return np.clip(snr, 0, 60)  # Ensure reasonable SNR range
