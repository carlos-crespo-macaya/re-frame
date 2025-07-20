"""Load and concurrency tests for voice modality."""

import asyncio
import os
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from src.voice.session_manager import VoiceSession
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
    def mock_voice_session_manager(self):
        """Mock voice session manager for load tests."""
        with patch("src.voice.router.voice_session_manager") as mock:
            # Make create_session return different sessions
            sessions = {}

            async def create_session_side_effect(language):
                session_id = f"voice-{len(sessions) + 1}"
                session = MagicMock(spec=VoiceSession)
                session.session_id = session_id
                session.status = "active"
                session.language = language
                session.send_audio = AsyncMock()
                session.send_control = AsyncMock()
                sessions[session_id] = session
                return session

            def get_session_side_effect(session_id):
                return sessions.get(session_id)

            async def remove_session_side_effect(session_id):
                sessions.pop(session_id, None)

            mock.create_session = AsyncMock(side_effect=create_session_side_effect)
            mock.get_session = MagicMock(side_effect=get_session_side_effect)
            mock.remove_session = AsyncMock(side_effect=remove_session_side_effect)
            mock.sessions = sessions

            yield mock

    @pytest.mark.asyncio
    async def test_concurrent_voice_sessions(
        self, async_client, mock_voice_session_manager
    ):
        """Test handling multiple concurrent voice sessions."""
        # Skip if running in CI to avoid resource issues
        if os.getenv("CI"):
            pytest.skip("Skipping load test in CI environment")

        num_sessions = 10

        async def create_and_use_session(session_num):
            """Create a voice session and send some audio."""
            # Create session
            response = await async_client.post(
                "/api/voice/sessions", json={"language": "en-US"}
            )
            assert response.status_code == 200
            session_data = response.json()
            session_id = session_data["session_id"]

            # Send a few audio chunks
            for _ in range(3):
                response = await async_client.post(
                    f"/api/voice/sessions/{session_id}/audio",
                    json={
                        "data": AudioSamples.get_sample("hello"),
                        "timestamp": 1234567890,
                    },
                )
                assert response.status_code == 200
                await asyncio.sleep(0.1)  # Small delay between chunks

            # End session
            response = await async_client.delete(f"/api/voice/sessions/{session_id}")
            assert response.status_code == 200

            return session_id

        # Run concurrent sessions
        start_time = time.time()
        tasks = [create_and_use_session(i) for i in range(num_sessions)]
        session_ids = await asyncio.gather(*tasks)
        duration = time.time() - start_time

        # Verify all sessions were created and cleaned up
        assert len(session_ids) == num_sessions
        assert len(set(session_ids)) == num_sessions  # All unique
        assert len(mock_voice_session_manager.sessions) == 0  # All cleaned up

        # Basic performance check (should handle 10 sessions in reasonable time)
        assert duration < 30  # 30 seconds max

    @pytest.mark.asyncio
    async def test_sustained_voice_load(self, async_client, mock_voice_session_manager):
        """Test sustained load with voice sessions."""
        # Skip if running in CI
        if os.getenv("CI"):
            pytest.skip("Skipping load test in CI environment")

        duration_seconds = 5
        sessions_created = 0
        errors = []

        async def continuous_session_creation():
            """Continuously create and destroy sessions."""
            nonlocal sessions_created
            while True:
                try:
                    # Create session
                    response = await async_client.post(
                        "/api/voice/sessions", json={"language": "en-US"}
                    )
                    if response.status_code == 200:
                        session_id = response.json()["session_id"]
                        sessions_created += 1

                        # Send audio
                        await async_client.post(
                            f"/api/voice/sessions/{session_id}/audio",
                            json={
                                "data": AudioSamples.get_sample("hello"),
                                "timestamp": 1234567890,
                            },
                        )

                        # Clean up
                        await async_client.delete(f"/api/voice/sessions/{session_id}")
                    else:
                        errors.append(
                            f"Failed to create session: {response.status_code}"
                        )
                except Exception as e:
                    errors.append(str(e))

                await asyncio.sleep(0.1)  # Rate limit

        # Run for specified duration
        task = asyncio.create_task(continuous_session_creation())
        await asyncio.sleep(duration_seconds)
        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass

        # Verify results
        assert sessions_created > 0
        assert len(errors) < sessions_created * 0.1  # Less than 10% error rate
        assert len(mock_voice_session_manager.sessions) == 0  # All cleaned up

    @pytest.mark.asyncio
    async def test_voice_session_ramp_up(
        self, async_client, mock_voice_session_manager
    ):
        """Test gradual ramp-up of voice sessions."""
        # Skip if running in CI
        if os.getenv("CI"):
            pytest.skip("Skipping load test in CI environment")

        max_concurrent = 5
        ramp_duration = 3  # seconds

        active_sessions = []

        async def manage_session(delay):
            """Create session after delay, use it, then clean up."""
            await asyncio.sleep(delay)

            # Create session
            response = await async_client.post(
                "/api/voice/sessions", json={"language": "en-US"}
            )
            assert response.status_code == 200
            session_id = response.json()["session_id"]
            active_sessions.append(session_id)

            # Use session for a bit
            for _ in range(5):
                await async_client.post(
                    f"/api/voice/sessions/{session_id}/audio",
                    json={
                        "data": AudioSamples.get_sample("hello"),
                        "timestamp": 1234567890,
                    },
                )
                await asyncio.sleep(0.2)

            # Clean up
            await async_client.delete(f"/api/voice/sessions/{session_id}")
            active_sessions.remove(session_id)

        # Create sessions with increasing delays
        tasks = []
        for i in range(max_concurrent):
            delay = (i / max_concurrent) * ramp_duration
            tasks.append(asyncio.create_task(manage_session(delay)))

        # Wait for all to complete
        await asyncio.gather(*tasks)

        # Verify all cleaned up
        assert len(active_sessions) == 0
        assert len(mock_voice_session_manager.sessions) == 0

    @pytest.mark.asyncio
    async def test_voice_spike_load(self, async_client, mock_voice_session_manager):
        """Test sudden spike in voice session creation."""
        # Skip if running in CI
        if os.getenv("CI"):
            pytest.skip("Skipping load test in CI environment")

        spike_size = 20

        async def create_session():
            """Create a single session."""
            response = await async_client.post(
                "/api/voice/sessions", json={"language": "en-US"}
            )
            return response.status_code, (
                response.json() if response.status_code == 200 else None
            )

        # Create many sessions at once
        start_time = time.time()
        results = await asyncio.gather(
            *[create_session() for _ in range(spike_size)], return_exceptions=True
        )
        duration = time.time() - start_time

        # Count successes
        successes = sum(1 for r in results if isinstance(r, tuple) and r[0] == 200)

        # Should handle most requests successfully
        assert successes >= spike_size * 0.8  # At least 80% success rate
        assert duration < 10  # Should complete within 10 seconds

        # Clean up created sessions
        for result in results:
            if isinstance(result, tuple) and result[0] == 200 and result[1]:
                session_id = result[1]["session_id"]
                await async_client.delete(f"/api/voice/sessions/{session_id}")
