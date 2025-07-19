"""Performance monitoring for voice modality."""

import asyncio
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any

from src.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""

    request_count: int = 0
    error_count: int = 0
    total_duration: float = 0.0
    response_times: list[float] = field(default_factory=list)
    audio_processing_times: dict[str, list[float]] = field(default_factory=dict)
    stt_latencies: list[float] = field(default_factory=list)
    tts_latencies: list[float] = field(default_factory=list)
    session_durations: dict[str, float] = field(default_factory=dict)
    concurrent_sessions: list[int] = field(default_factory=list)
    _start_time: float = field(default_factory=time.time)

    def record_request(self, duration: float, success: bool = True) -> None:
        """Record a request completion."""
        self.request_count += 1
        self.response_times.append(duration)
        if not success:
            self.error_count += 1

    def record_audio_processing(self, stage: str, duration: float) -> None:
        """Record audio processing stage duration."""
        if stage not in self.audio_processing_times:
            self.audio_processing_times[stage] = []
        self.audio_processing_times[stage].append(duration)

    def record_stt_latency(self, duration: float) -> None:
        """Record speech-to-text latency."""
        self.stt_latencies.append(duration)

    def record_tts_latency(self, duration: float) -> None:
        """Record text-to-speech latency."""
        self.tts_latencies.append(duration)

    def record_session_duration(self, session_id: str, duration: float) -> None:
        """Record session duration."""
        self.session_durations[session_id] = duration

    def record_concurrent_sessions(self, count: int) -> None:
        """Record number of concurrent sessions."""
        self.concurrent_sessions.append(count)

    def get_summary(self) -> dict[str, Any]:
        """Get performance summary."""
        uptime = time.time() - self._start_time

        summary: dict[str, Any] = {
            "uptime_seconds": uptime,
            "total_requests": self.request_count,
            "error_count": self.error_count,
            "error_rate": (
                self.error_count / self.request_count if self.request_count > 0 else 0
            ),
            "throughput_rps": self.request_count / uptime if uptime > 0 else 0,
        }

        # Response time statistics
        if self.response_times:
            sorted_times = sorted(self.response_times)
            summary["response_times"] = {
                "min": min(sorted_times),
                "max": max(sorted_times),
                "avg": sum(sorted_times) / len(sorted_times),
                "p50": sorted_times[int(len(sorted_times) * 0.50)],
                "p95": sorted_times[int(len(sorted_times) * 0.95)],
                "p99": sorted_times[int(len(sorted_times) * 0.99)],
            }

        # Audio processing statistics
        if self.audio_processing_times:
            summary["audio_processing"] = {}
            for stage, times in self.audio_processing_times.items():
                if times:
                    summary["audio_processing"][stage] = {
                        "avg": sum(times) / len(times),
                        "min": min(times),
                        "max": max(times),
                    }

        # STT/TTS latencies
        if self.stt_latencies:
            summary["stt_latency_avg"] = sum(self.stt_latencies) / len(
                self.stt_latencies
            )
        if self.tts_latencies:
            summary["tts_latency_avg"] = sum(self.tts_latencies) / len(
                self.tts_latencies
            )

        # Session statistics
        if self.session_durations:
            durations = list(self.session_durations.values())
            summary["session_stats"] = {
                "total_sessions": len(durations),
                "avg_duration": sum(durations) / len(durations),
                "max_duration": max(durations),
            }

        # Concurrent sessions
        if self.concurrent_sessions:
            summary["concurrent_sessions"] = {
                "max": max(self.concurrent_sessions),
                "avg": sum(self.concurrent_sessions) / len(self.concurrent_sessions),
            }

        return summary


class PerformanceMonitor:
    """Monitor performance metrics for voice modality."""

    def __init__(self):
        """Initialize performance monitor."""
        self.metrics = PerformanceMetrics()
        self._active_sessions: dict[str, float] = {}
        self._lock = asyncio.Lock()

    @asynccontextmanager
    async def track_request(self, request_type: str = "voice"):
        """Context manager to track request performance."""
        start_time = time.time()
        success = True

        try:
            yield
        except Exception as e:
            success = False
            logger.error(f"Request failed: {e}")
            raise
        finally:
            duration = time.time() - start_time
            self.metrics.record_request(duration, success)

            # Log slow requests
            if duration > 2.0:
                logger.warning(
                    "slow_request",
                    request_type=request_type,
                    duration=duration,
                    success=success,
                )

    @asynccontextmanager
    async def track_audio_processing(self, stage: str):
        """Track audio processing stage performance."""
        start_time = time.time()

        try:
            yield
        finally:
            duration = time.time() - start_time
            self.metrics.record_audio_processing(stage, duration)

            # Log slow processing
            if duration > 1.0:
                logger.warning(
                    "slow_audio_processing",
                    stage=stage,
                    duration=duration,
                )

    async def start_session(self, session_id: str) -> None:
        """Mark session start."""
        async with self._lock:
            self._active_sessions[session_id] = time.time()
            self.metrics.record_concurrent_sessions(len(self._active_sessions))

    async def end_session(self, session_id: str) -> None:
        """Mark session end and record duration."""
        async with self._lock:
            if session_id in self._active_sessions:
                start_time = self._active_sessions.pop(session_id)
                duration = time.time() - start_time
                self.metrics.record_session_duration(session_id, duration)

                logger.info(
                    "session_ended",
                    session_id=session_id,
                    duration=duration,
                    remaining_sessions=len(self._active_sessions),
                )

    def record_stt_latency(self, duration: float) -> None:
        """Record STT processing latency."""
        self.metrics.record_stt_latency(duration)

        # Alert on high latency
        if duration > 2.0:
            logger.warning("high_stt_latency", duration=duration)

    def record_tts_latency(self, duration: float) -> None:
        """Record TTS processing latency."""
        self.metrics.record_tts_latency(duration)

        # Alert on high latency
        if duration > 2.0:
            logger.warning("high_tts_latency", duration=duration)

    def get_metrics(self) -> dict[str, Any]:
        """Get current performance metrics."""
        summary = self.metrics.get_summary()
        summary["active_sessions"] = len(self._active_sessions)
        return summary  # type: ignore[no-any-return]

    def reset_metrics(self) -> None:
        """Reset all metrics (useful for testing)."""
        self.metrics = PerformanceMetrics()
        self._active_sessions.clear()

    async def log_periodic_summary(self, interval: int = 300) -> None:
        """Log performance summary periodically (default: every 5 minutes)."""
        try:
            while True:
                await asyncio.sleep(interval)
                summary = self.get_metrics()
                logger.info("performance_summary", **summary)
        except asyncio.CancelledError:
            logger.info("performance_monitoring_stopped")
            raise


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance."""
    return performance_monitor
