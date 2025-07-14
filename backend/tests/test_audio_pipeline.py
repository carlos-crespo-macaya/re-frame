"""Tests for audio pipeline orchestrator."""

from unittest.mock import AsyncMock

import pytest

from src.services.audio_pipeline import (
    AudioPipeline,
    AudioPipelineMetrics,
    AudioPipelineSession,
    PipelineState,
)
from src.services.speech_to_text import MockSpeechToText
from src.services.text_to_speech import MockTextToSpeech
from src.utils.audio_utils import AudioConfig


class TestPipelineState:
    """Test PipelineState enum."""

    def test_state_values(self):
        """Test pipeline state values."""
        assert PipelineState.IDLE.value == "idle"
        assert PipelineState.LISTENING.value == "listening"
        assert PipelineState.PROCESSING.value == "processing"
        assert PipelineState.SPEAKING.value == "speaking"
        assert PipelineState.ERROR.value == "error"


class TestAudioPipelineMetrics:
    """Test AudioPipelineMetrics class."""

    def test_initial_metrics(self):
        """Test initial metric values."""
        metrics = AudioPipelineMetrics()

        assert metrics.total_sessions == 0
        assert metrics.active_sessions == 0
        assert metrics.total_audio_duration == 0.0
        assert metrics.total_processing_time == 0.0
        assert metrics.transcription_errors == 0
        assert metrics.synthesis_errors == 0
        assert metrics.average_latency == 0.0

    def test_session_tracking(self):
        """Test session tracking."""
        metrics = AudioPipelineMetrics()

        metrics.record_session_start()
        assert metrics.total_sessions == 1
        assert metrics.active_sessions == 1

        metrics.record_session_start()
        assert metrics.total_sessions == 2
        assert metrics.active_sessions == 2

        metrics.record_session_end()
        assert metrics.total_sessions == 2
        assert metrics.active_sessions == 1

        metrics.record_session_end()
        metrics.record_session_end()  # Extra end should not go negative
        assert metrics.active_sessions == 0

    def test_processing_time_tracking(self):
        """Test processing time tracking."""
        metrics = AudioPipelineMetrics()

        metrics.record_processing_time(1.0)
        assert metrics.total_processing_time == 1.0
        assert metrics.average_latency == 0.1  # 0.0 * 0.9 + 1.0 * 0.1

        metrics.record_processing_time(2.0)
        assert metrics.total_processing_time == 3.0
        assert abs(metrics.average_latency - 0.29) < 0.01  # 0.1 * 0.9 + 2.0 * 0.1


class TestAudioPipelineSession:
    """Test AudioPipelineSession class."""

    @pytest.fixture
    def mock_services(self):
        """Create mock services for testing."""
        stt = MockSpeechToText()
        tts = MockTextToSpeech()
        return stt, tts

    @pytest.mark.asyncio
    async def test_session_creation(self, mock_services):
        """Test session creation."""
        stt, tts = mock_services
        config = AudioConfig()

        session = AudioPipelineSession(
            session_id="test-123",
            audio_config=config,
            stt_service=stt,
            tts_service=tts,
            language="en-US",
        )

        assert session.session_id == "test-123"
        assert session.state == PipelineState.IDLE
        assert session.language == "en-US"
        assert session.is_active

    @pytest.mark.asyncio
    async def test_start_stop_listening(self, mock_services):
        """Test starting and stopping listening."""
        stt, tts = mock_services
        session = AudioPipelineSession(
            session_id="test-123",
            audio_config=AudioConfig(),
            stt_service=stt,
            tts_service=tts,
        )

        # Track state changes
        state_changes = []

        async def on_state_change(old_state, new_state):
            state_changes.append((old_state, new_state))

        session.set_callbacks(on_state_change=on_state_change)

        # Start listening
        await session.start_listening()
        assert session.state == PipelineState.LISTENING
        assert len(state_changes) == 1
        assert state_changes[0] == (PipelineState.IDLE, PipelineState.LISTENING)

        # Stop listening
        await session.stop_listening()
        assert session.state == PipelineState.IDLE
        assert len(state_changes) == 2
        assert state_changes[1] == (PipelineState.LISTENING, PipelineState.IDLE)

    @pytest.mark.asyncio
    async def test_process_audio_chunk(self, mock_services):
        """Test processing audio chunks."""
        stt, tts = mock_services
        session = AudioPipelineSession(
            session_id="test-123",
            audio_config=AudioConfig(),
            stt_service=stt,
            tts_service=tts,
        )

        await session.start_listening()

        # Process chunk should work when listening
        await session.process_audio_chunk(b"audio_data")

        # Should not raise error when not listening
        await session.stop_listening()
        await session.process_audio_chunk(b"more_data")  # Should be ignored

    @pytest.mark.asyncio
    async def test_speech_detection_and_transcription(self, mock_services):
        """Test speech detection and transcription flow."""
        stt, tts = mock_services

        # Initialize STT service
        await stt.initialize()

        session = AudioPipelineSession(
            session_id="test-123",
            audio_config=AudioConfig(),
            stt_service=stt,
            tts_service=tts,
        )

        # Track transcriptions
        transcriptions = []

        async def on_transcription(result):
            transcriptions.append(result)

        session.set_callbacks(on_transcription=on_transcription)

        # Simulate speech end event
        await session._on_speech_end(b"speech_audio_data")

        # Should have received transcription
        assert len(transcriptions) == 1
        assert transcriptions[0].text == "I've been feeling really anxious lately"
        assert session.state == PipelineState.LISTENING

    @pytest.mark.asyncio
    async def test_speak(self, mock_services):
        """Test speech synthesis."""
        stt, tts = mock_services

        # Initialize TTS service
        await tts.initialize()

        session = AudioPipelineSession(
            session_id="test-123",
            audio_config=AudioConfig(),
            stt_service=stt,
            tts_service=tts,
        )

        await session.start_listening()

        # Synthesize speech
        audio_data = await session.speak("Hello, how are you?")

        assert audio_data is not None
        assert len(audio_data) > 0
        assert session.state == PipelineState.LISTENING

    @pytest.mark.asyncio
    async def test_error_handling(self, mock_services):
        """Test error handling."""
        stt, tts = mock_services

        session = AudioPipelineSession(
            session_id="test-123",
            audio_config=AudioConfig(),
            stt_service=stt,
            tts_service=tts,
        )

        # Track errors
        errors = []

        async def on_error(error):
            errors.append(error)

        session.set_callbacks(on_error=on_error)

        # Simulate error
        test_error = ValueError("Test error")
        await session._handle_error(test_error)

        assert session.state == PipelineState.ERROR
        assert len(errors) == 1
        assert errors[0] == test_error

    @pytest.mark.asyncio
    async def test_cleanup(self, mock_services):
        """Test session cleanup."""
        stt, tts = mock_services

        session = AudioPipelineSession(
            session_id="test-123",
            audio_config=AudioConfig(),
            stt_service=stt,
            tts_service=tts,
        )

        await session.start_listening()
        assert session.is_active

        await session.cleanup()
        assert not session.is_active
        assert session.state == PipelineState.IDLE


class TestAudioPipeline:
    """Test AudioPipeline class."""

    @pytest.fixture
    def pipeline(self):
        """Create pipeline for testing."""
        stt = MockSpeechToText()
        tts = MockTextToSpeech()
        config = AudioConfig()
        return AudioPipeline(stt, tts, config)

    @pytest.mark.asyncio
    async def test_initialization(self, pipeline):
        """Test pipeline initialization."""
        assert not pipeline._is_initialized

        await pipeline.initialize()
        assert pipeline._is_initialized

    @pytest.mark.asyncio
    async def test_create_session(self, pipeline):
        """Test session creation."""
        await pipeline.initialize()

        # Create session
        session = await pipeline.create_session(session_id="test-456", language="es-US")

        assert session is not None
        assert session.session_id == "test-456"
        assert session.language == "es-US"
        assert "test-456" in pipeline.sessions
        assert pipeline.metrics.total_sessions == 1
        assert pipeline.metrics.active_sessions == 1

    @pytest.mark.asyncio
    async def test_create_session_with_callbacks(self, pipeline):
        """Test session creation with callbacks."""
        await pipeline.initialize()

        # Define callbacks
        on_transcription = AsyncMock()
        on_state_change = AsyncMock()

        callbacks = {
            "on_transcription": on_transcription,
            "on_state_change": on_state_change,
        }

        session = await pipeline.create_session(
            session_id="test-789", callbacks=callbacks
        )

        # Verify callbacks are set
        assert session._transcription_callback == on_transcription
        assert session._state_callback == on_state_change

    @pytest.mark.asyncio
    async def test_get_session(self, pipeline):
        """Test getting existing session."""
        await pipeline.initialize()

        # Create session
        await pipeline.create_session("test-123")

        # Get session
        session = await pipeline.get_session("test-123")
        assert session is not None
        assert session.session_id == "test-123"

        # Get non-existent session
        session = await pipeline.get_session("non-existent")
        assert session is None

    @pytest.mark.asyncio
    async def test_close_session(self, pipeline):
        """Test closing session."""
        await pipeline.initialize()

        # Create and close session
        await pipeline.create_session("test-123")
        assert "test-123" in pipeline.sessions

        await pipeline.close_session("test-123")
        assert "test-123" not in pipeline.sessions
        assert pipeline.metrics.active_sessions == 0

        # Close non-existent session (should not raise error)
        await pipeline.close_session("non-existent")

    @pytest.mark.asyncio
    async def test_cleanup(self, pipeline):
        """Test pipeline cleanup."""
        await pipeline.initialize()

        # Create multiple sessions
        await pipeline.create_session("test-1")
        await pipeline.create_session("test-2")
        await pipeline.create_session("test-3")

        assert len(pipeline.sessions) == 3

        # Cleanup
        await pipeline.cleanup()

        assert len(pipeline.sessions) == 0
        assert not pipeline._is_initialized
        assert pipeline.metrics.active_sessions == 0

    @pytest.mark.asyncio
    async def test_get_metrics(self, pipeline):
        """Test getting metrics."""
        await pipeline.initialize()

        # Create sessions and simulate activity
        await pipeline.create_session("test-1")
        await pipeline.create_session("test-2")
        await pipeline.close_session("test-1")

        metrics = pipeline.get_metrics()
        assert metrics.total_sessions == 2
        assert metrics.active_sessions == 1

    @pytest.mark.asyncio
    async def test_auto_initialization(self, pipeline):
        """Test automatic initialization when creating session."""
        assert not pipeline._is_initialized

        # Should auto-initialize
        session = await pipeline.create_session("test-123")

        assert pipeline._is_initialized
        assert session is not None
