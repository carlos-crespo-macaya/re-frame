"""Tests for performance monitor."""

import asyncio
import time

import pytest

from src.utils.performance_monitor import (
    PerformanceMetrics,
    PerformanceMonitor,
    get_performance_monitor,
    performance_monitor,
)


class TestPerformanceMetrics:
    """Test performance metrics tracking."""

    def test_initial_metrics(self):
        """Test initial state of performance metrics."""
        metrics = PerformanceMetrics()
        assert metrics.request_count == 0
        assert metrics.error_count == 0
        assert metrics.total_duration == 0.0
        assert len(metrics.response_times) == 0

    def test_record_request_success(self):
        """Test recording a successful request."""
        metrics = PerformanceMetrics()
        metrics.record_request(0.1, success=True)

        assert metrics.request_count == 1
        assert metrics.error_count == 0
        assert 0.1 in metrics.response_times

    def test_record_request_failure(self):
        """Test recording a failed request."""
        metrics = PerformanceMetrics()
        metrics.record_request(0.2, success=False)

        assert metrics.request_count == 1
        assert metrics.error_count == 1
        assert 0.2 in metrics.response_times

    def test_record_audio_processing(self):
        """Test recording audio processing times."""
        metrics = PerformanceMetrics()
        metrics.record_audio_processing("vad", 0.05)
        metrics.record_audio_processing("vad", 0.03)

        assert "vad" in metrics.audio_processing_times
        assert len(metrics.audio_processing_times["vad"]) == 2
        assert 0.05 in metrics.audio_processing_times["vad"]
        assert 0.03 in metrics.audio_processing_times["vad"]

    def test_record_stt_latency(self):
        """Test recording STT latency."""
        metrics = PerformanceMetrics()
        metrics.record_stt_latency(0.15)

        assert 0.15 in metrics.stt_latencies

    def test_record_tts_latency(self):
        """Test recording TTS latency."""
        metrics = PerformanceMetrics()
        metrics.record_tts_latency(0.25)

        assert 0.25 in metrics.tts_latencies

    def test_record_session_duration(self):
        """Test recording session duration."""
        metrics = PerformanceMetrics()
        metrics.record_session_duration("session-1", 120.5)

        assert metrics.session_durations["session-1"] == 120.5

    def test_record_concurrent_sessions(self):
        """Test recording concurrent sessions."""
        metrics = PerformanceMetrics()
        metrics.record_concurrent_sessions(5)

        assert 5 in metrics.concurrent_sessions


class TestPerformanceMonitor:
    """Test performance monitor functionality."""

    def test_get_performance_monitor_singleton(self):
        """Test that get_performance_monitor returns singleton."""
        monitor1 = get_performance_monitor()
        monitor2 = get_performance_monitor()
        assert monitor1 is monitor2
        assert monitor1 is performance_monitor

    def test_reset_metrics(self):
        """Test resetting metrics."""
        monitor = PerformanceMonitor()

        # Add some data
        monitor.metrics.record_request(0.1)
        monitor._active_sessions["session-1"] = time.time()

        # Reset
        monitor.reset_metrics()

        # Verify reset
        assert monitor.metrics.request_count == 0
        assert len(monitor._active_sessions) == 0

    @pytest.mark.asyncio
    async def test_start_session(self):
        """Test starting a session."""
        monitor = PerformanceMonitor()
        await monitor.start_session("session-1")

        assert "session-1" in monitor._active_sessions

    @pytest.mark.asyncio
    async def test_end_session(self):
        """Test ending a session."""
        monitor = PerformanceMonitor()

        # Start a session
        await monitor.start_session("session-1")
        await asyncio.sleep(0.1)  # Let some time pass

        # End the session
        await monitor.end_session("session-1")

        assert "session-1" not in monitor._active_sessions
        assert "session-1" in monitor.metrics.session_durations

    @pytest.mark.asyncio
    async def test_get_metrics(self):
        """Test getting metrics summary."""
        monitor = PerformanceMonitor()

        # Add some test data
        monitor.metrics.record_request(0.1, success=True)
        await monitor.start_session("session-1")

        # Get metrics
        metrics = monitor.get_metrics()

        assert "uptime_seconds" in metrics
        assert "total_requests" in metrics
        assert metrics["total_requests"] == 1
        assert metrics["active_sessions"] == 1

    @pytest.mark.asyncio
    async def test_track_request_context(self):
        """Test tracking request with context manager."""
        monitor = PerformanceMonitor()

        # Reset to ensure clean state
        monitor.reset_metrics()

        # Track a successful request
        async with monitor.track_request("test"):
            await asyncio.sleep(0.01)

        assert monitor.metrics.request_count == 1
        assert monitor.metrics.error_count == 0

    @pytest.mark.asyncio
    async def test_track_request_with_error(self):
        """Test tracking request that raises an error."""
        monitor = PerformanceMonitor()

        # Reset to ensure clean state
        monitor.reset_metrics()

        # Track a failed request
        with pytest.raises(ValueError):
            async with monitor.track_request("test"):
                raise ValueError("Test error")

        assert monitor.metrics.request_count == 1
        assert monitor.metrics.error_count == 1
