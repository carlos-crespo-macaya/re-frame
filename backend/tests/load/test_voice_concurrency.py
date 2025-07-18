"""Load and concurrency tests for voice modality."""

import asyncio
import os
import time
from typing import List, Tuple
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from tests.fixtures import AudioSamples


class TestVoiceConcurrency:
    """Test system under concurrent voice load."""

    @pytest.fixture
    async def async_client(self):
        """Create an async test client."""
        from src.main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            yield ac

    @pytest.fixture
    def mock_session_manager(self):
        """Mock session manager for load tests."""
        with patch("src.main.session_manager") as mock:
            # Create mock sessions
            mock.sessions = {}

            def create_mock_session(session_id):
                """Create a mock session with required metadata."""
                mock_session = MagicMock()
                mock_queue = AsyncMock()
                mock_runner = AsyncMock()
                mock_adk_session = MagicMock()
                mock_run_config = MagicMock()

                # Mock runner.run_async to return an async generator
                async def mock_run_async(*args, **kwargs):
                    # Return minimal events for load testing
                    yield MagicMock(content=MagicMock(parts=[MagicMock(text="Test response")]))
                    yield MagicMock(turn_complete=True)

                mock_runner.run_async = mock_run_async

                mock_session.metadata = {
                    "message_queue": mock_queue,
                    "runner": mock_runner,
                    "adk_session": mock_adk_session,
                    "run_config": mock_run_config,
                    "language": "en-US",
                }
                mock_session.session_id = session_id
                mock_session.user_id = session_id

                return mock_session

            def get_session(session_id):
                if session_id not in mock.sessions:
                    mock.sessions[session_id] = create_mock_session(session_id)
                return mock.sessions[session_id]

            mock.get_session.side_effect = get_session
            mock.create_session.side_effect = lambda **kwargs: create_mock_session(
                kwargs.get("session_id")
            )

            yield mock

    @pytest.mark.load
    @pytest.mark.asyncio
    async def test_concurrent_voice_sessions(self, async_client, mock_session_manager):
        """Test handling multiple simultaneous voice sessions."""

        async def simulate_voice_user(user_id: int) -> Tuple[int, float]:
            """Simulate a single voice user interaction."""
            session_id = f"session-{user_id}"
            audio_data = AudioSamples.get_sample("hello")

            start_time = time.time()
            response = await async_client.post(
                f"/api/send/{session_id}",
                json={"mime_type": "audio/pcm", "data": audio_data},
            )
            elapsed = time.time() - start_time

            return response.status_code, elapsed

        # Enable voice mode for load test
        with patch("src.config.VOICE_MODE_ENABLED", True):
            # Get number of concurrent users from env or default
            concurrent_users = int(os.getenv("CONCURRENT_USERS", "50"))

            # Simulate concurrent users
            tasks = [simulate_voice_user(i) for i in range(concurrent_users)]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        # Analyze results
        successful = [r for r in results if isinstance(r, tuple) and r[0] == 200]
        failed = [
            r
            for r in results
            if isinstance(r, Exception) or (isinstance(r, tuple) and r[0] != 200)
        ]

        # Success rate should be > 95%
        success_rate = len(successful) / len(results)
        assert (
            success_rate > 0.95
        ), f"Success rate {success_rate:.1%} below 95% threshold"

        # Response time analysis
        if successful:
            response_times = [r[1] for r in successful]
            avg_time = sum(response_times) / len(response_times)
            p95_time = sorted(response_times)[int(len(response_times) * 0.95)]
            p99_time = sorted(response_times)[int(len(response_times) * 0.99)]

            # Performance assertions
            assert avg_time < 1.0, f"Average response time {avg_time:.2f}s exceeds 1s"
            assert p95_time < 2.0, f"P95 response time {p95_time:.2f}s exceeds 2s"
            assert p99_time < 5.0, f"P99 response time {p99_time:.2f}s exceeds 5s"

            # Log performance metrics
            print(
                f"\nLoad test results: {len(successful)} successful, {len(failed)} failed"
            )
            print(
                f"Response times - Avg: {avg_time:.2f}s, P95: {p95_time:.2f}s, P99: {p99_time:.2f}s"
            )
            print(f"Success rate: {success_rate:.1%}")

    @pytest.mark.load
    @pytest.mark.asyncio
    async def test_sustained_voice_load(self, async_client, mock_session_manager):
        """Test system under sustained voice load for configured duration."""
        start_time = time.time()
        test_duration = int(os.getenv("TEST_DURATION", "60"))  # Default 60 seconds
        end_time = start_time + test_duration

        request_count = 0
        error_count = 0
        response_times: List[float] = []

        async def continuous_requests():
            nonlocal request_count, error_count

            while time.time() < end_time:
                try:
                    session_id = f"sustained-{request_count}"
                    audio_data = AudioSamples.get_sample("hello")

                    req_start = time.time()
                    response = await async_client.post(
                        f"/api/send/{session_id}",
                        json={"mime_type": "audio/pcm", "data": audio_data},
                    )
                    req_time = time.time() - req_start

                    request_count += 1
                    response_times.append(req_time)

                    if response.status_code != 200:
                        error_count += 1

                    # Target 10 requests per second
                    await asyncio.sleep(0.1)

                except Exception as e:
                    error_count += 1
                    print(f"Request error: {e}")

        # Run with configured number of workers
        concurrent_workers = int(os.getenv("CONCURRENT_WORKERS", "5"))

        with patch("src.config.VOICE_MODE_ENABLED", True):
            workers = [continuous_requests() for _ in range(concurrent_workers)]
            await asyncio.gather(*workers)

        # Calculate metrics
        duration = time.time() - start_time
        throughput = request_count / duration
        error_rate = error_count / request_count if request_count > 0 else 0

        # Assertions
        assert (
            throughput > concurrent_workers * 8
        ), f"Throughput {throughput:.1f} req/s below target {concurrent_workers * 8} req/s"
        assert error_rate < 0.01, f"Error rate {error_rate:.1%} exceeds 1%"

        # Response time analysis
        if response_times:
            avg_response = sum(response_times) / len(response_times)
            assert avg_response < 0.5, f"Average response {avg_response:.2f}s exceeds 0.5s"

        print(f"\nSustained load test results:")
        print(f"Duration: {duration:.1f}s")
        print(f"Total requests: {request_count}")
        print(f"Throughput: {throughput:.1f} req/s")
        print(f"Error rate: {error_rate:.1%}")
        print(f"Average response time: {avg_response:.3f}s")

    @pytest.mark.load
    @pytest.mark.asyncio
    async def test_voice_session_ramp_up(self, async_client, mock_session_manager):
        """Test system behavior during gradual load increase."""
        max_users = int(os.getenv("MAX_USERS", "100"))
        ramp_duration = int(os.getenv("RAMP_DURATION", "30"))  # seconds
        users_per_second = max_users / ramp_duration

        results = []
        start_time = time.time()

        async def simulate_user(user_id: int, delay: float):
            """Simulate a user starting after a delay."""
            await asyncio.sleep(delay)
            session_id = f"ramp-{user_id}"
            audio_data = AudioSamples.get_sample("hello")

            req_start = time.time()
            try:
                response = await async_client.post(
                    f"/api/send/{session_id}",
                    json={"mime_type": "audio/pcm", "data": audio_data},
                )
                elapsed = time.time() - req_start
                return user_id, response.status_code, elapsed
            except Exception as e:
                return user_id, 500, time.time() - req_start

        with patch("src.config.VOICE_MODE_ENABLED", True):
            # Create tasks with staggered start times
            tasks = []
            for i in range(max_users):
                delay = i / users_per_second
                tasks.append(simulate_user(i, delay))

            # Execute all tasks
            results = await asyncio.gather(*tasks, return_exceptions=True)

        # Analyze results by time buckets
        bucket_size = 5  # seconds
        buckets = {}

        for result in results:
            if isinstance(result, tuple) and len(result) == 3:
                user_id, status, response_time = result
                bucket = int(user_id / (users_per_second * bucket_size))
                if bucket not in buckets:
                    buckets[bucket] = {"success": 0, "total": 0, "times": []}
                buckets[bucket]["total"] += 1
                if status == 200:
                    buckets[bucket]["success"] += 1
                    buckets[bucket]["times"].append(response_time)

        # Print performance degradation analysis
        print(f"\nRamp-up test results (max {max_users} users over {ramp_duration}s):")
        for bucket in sorted(buckets.keys()):
            data = buckets[bucket]
            success_rate = data["success"] / data["total"]
            avg_time = sum(data["times"]) / len(data["times"]) if data["times"] else 0
            concurrent = int((bucket + 1) * bucket_size * users_per_second)
            print(
                f"  {concurrent:3d} users: {success_rate:.1%} success, {avg_time:.2f}s avg response"
            )

        # Verify system remains stable
        final_bucket = max(buckets.keys())
        final_success_rate = buckets[final_bucket]["success"] / buckets[final_bucket]["total"]
        assert (
            final_success_rate > 0.90
        ), f"Success rate at max load {final_success_rate:.1%} below 90%"

    @pytest.mark.load
    @pytest.mark.asyncio
    async def test_voice_spike_load(self, async_client, mock_session_manager):
        """Test system response to sudden traffic spikes."""
        baseline_users = 10
        spike_users = 100
        spike_duration = 10  # seconds

        async def simulate_baseline_user(user_id: int):
            """Simulate baseline traffic."""
            while True:
                session_id = f"baseline-{user_id}-{int(time.time())}"
                audio_data = AudioSamples.get_sample("hello")

                try:
                    await async_client.post(
                        f"/api/send/{session_id}",
                        json={"mime_type": "audio/pcm", "data": audio_data},
                    )
                except Exception:
                    pass

                await asyncio.sleep(1)  # One request per second

        async def simulate_spike_user(user_id: int):
            """Simulate spike traffic."""
            session_id = f"spike-{user_id}"
            audio_data = AudioSamples.get_sample("hello")

            start = time.time()
            response = await async_client.post(
                f"/api/send/{session_id}",
                json={"mime_type": "audio/pcm", "data": audio_data},
            )
            return response.status_code, time.time() - start

        with patch("src.config.VOICE_MODE_ENABLED", True):
            # Start baseline traffic
            baseline_tasks = []
            for i in range(baseline_users):
                task = asyncio.create_task(simulate_baseline_user(i))
                baseline_tasks.append(task)

            # Let baseline stabilize
            await asyncio.sleep(5)

            # Create spike
            print(f"\nCreating traffic spike: {spike_users} additional users")
            spike_start = time.time()
            spike_tasks = [simulate_spike_user(i) for i in range(spike_users)]
            spike_results = await asyncio.gather(*spike_tasks, return_exceptions=True)

            # Cancel baseline tasks
            for task in baseline_tasks:
                task.cancel()

        # Analyze spike handling
        successful_spike = [
            r for r in spike_results if isinstance(r, tuple) and r[0] == 200
        ]
        spike_success_rate = len(successful_spike) / len(spike_results)

        if successful_spike:
            spike_response_times = [r[1] for r in successful_spike]
            avg_spike_time = sum(spike_response_times) / len(spike_response_times)
            max_spike_time = max(spike_response_times)

            print(f"Spike results:")
            print(f"  Success rate: {spike_success_rate:.1%}")
            print(f"  Average response: {avg_spike_time:.2f}s")
            print(f"  Max response: {max_spike_time:.2f}s")

            # System should handle spikes gracefully
            assert spike_success_rate > 0.80, f"Spike success rate {spike_success_rate:.1%} below 80%"
            assert avg_spike_time < 3.0, f"Average spike response {avg_spike_time:.2f}s exceeds 3s"