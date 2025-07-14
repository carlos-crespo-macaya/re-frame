"""Audio pipeline orchestrator for managing voice interaction flow."""

import asyncio
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

from ..utils.audio_utils import AudioConfig, NoiseReducer, VoiceActivityDetector
from .speech_to_text import SpeechToTextService
from .text_to_speech import TextToSpeechService, VoiceConfig

logger = logging.getLogger(__name__)


class PipelineState(Enum):
    """States of the audio pipeline."""

    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    ERROR = "error"


@dataclass
class AudioPipelineMetrics:
    """Metrics for monitoring pipeline performance."""

    total_sessions: int = 0
    active_sessions: int = 0
    total_audio_duration: float = 0.0
    total_processing_time: float = 0.0
    transcription_errors: int = 0
    synthesis_errors: int = 0
    average_latency: float = 0.0

    def record_session_start(self):
        """Record session start."""
        self.total_sessions += 1
        self.active_sessions += 1

    def record_session_end(self):
        """Record session end."""
        self.active_sessions = max(0, self.active_sessions - 1)

    def record_processing_time(self, duration: float):
        """Record processing time."""
        self.total_processing_time += duration
        # Simple moving average for latency
        self.average_latency = (self.average_latency * 0.9) + (duration * 0.1)


class AudioPipelineSession:
    """Individual audio session within the pipeline."""

    def __init__(
        self,
        session_id: str,
        audio_config: AudioConfig,
        stt_service: SpeechToTextService,
        tts_service: TextToSpeechService,
        language: str = "en-US",
    ):
        self.session_id = session_id
        self.audio_config = audio_config
        self.stt_service = stt_service
        self.tts_service = tts_service
        self.language = language

        self.state = PipelineState.IDLE
        self.noise_reducer = NoiseReducer(audio_config)
        self.vad = VoiceActivityDetector(audio_config)

        self._transcription_callback: Callable | None = None
        self._state_callback: Callable | None = None
        self._error_callback: Callable | None = None

        self.start_time = time.time()
        self.is_active = True

    def set_callbacks(
        self,
        on_transcription: Callable | None = None,
        on_state_change: Callable | None = None,
        on_error: Callable | None = None,
    ):
        """Set session callbacks."""
        self._transcription_callback = on_transcription
        self._state_callback = on_state_change
        self._error_callback = on_error

    async def _change_state(self, new_state: PipelineState):
        """Change pipeline state and notify."""
        old_state = self.state
        self.state = new_state
        logger.info(
            f"Session {self.session_id}: {old_state.value} -> {new_state.value}"
        )

        if self._state_callback:
            await self._state_callback(old_state, new_state)

    async def start_listening(self):
        """Start listening for audio input."""
        try:
            await self._change_state(PipelineState.LISTENING)

            # Start processors
            await self.noise_reducer.start()
            await self.vad.start()

            # Set up VAD callbacks
            self.vad.set_callbacks(
                on_speech_start=self._on_speech_start, on_speech_end=self._on_speech_end
            )

        except Exception as e:
            logger.error(f"Failed to start listening: {e}")
            await self._handle_error(e)

    async def stop_listening(self):
        """Stop listening for audio input."""
        try:
            await self._change_state(PipelineState.IDLE)

            # Stop processors
            await self.noise_reducer.stop()
            await self.vad.stop()

        except Exception as e:
            logger.error(f"Failed to stop listening: {e}")
            await self._handle_error(e)

    async def process_audio_chunk(self, chunk: bytes):
        """Process incoming audio chunk."""
        if self.state != PipelineState.LISTENING:
            return

        try:
            # Process through noise reducer and VAD
            processed = await self.noise_reducer.process_chunk(chunk)
            if processed:
                await self.vad.process_chunk(processed)

        except Exception as e:
            logger.error(f"Failed to process audio chunk: {e}")
            await self._handle_error(e)

    async def _on_speech_start(self):
        """Handle speech start event."""
        logger.debug(f"Session {self.session_id}: Speech started")

    async def _on_speech_end(self, speech_data: bytes):
        """Handle speech end event."""
        logger.debug(f"Session {self.session_id}: Speech ended")

        try:
            await self._change_state(PipelineState.PROCESSING)

            # Transcribe the speech
            start_time = time.time()
            result = await self.stt_service.transcribe(speech_data, self.language)
            transcription_time = time.time() - start_time

            logger.info(
                f"Transcription completed in {transcription_time:.2f}s: {result.text}"
            )

            # Notify callback
            if self._transcription_callback and result.text:
                await self._transcription_callback(result)

            # Return to listening
            await self._change_state(PipelineState.LISTENING)

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            await self._handle_error(e)

    async def speak(self, text: str, voice_config: VoiceConfig | None = None):
        """Synthesize and play speech."""
        try:
            await self._change_state(PipelineState.SPEAKING)

            # Synthesize speech
            start_time = time.time()
            audio_data = await self.tts_service.synthesize(
                text, voice_config, self.language
            )
            synthesis_time = time.time() - start_time

            logger.info(f"Speech synthesis completed in {synthesis_time:.2f}s")

            # In a real implementation, this would play the audio
            # For now, we just simulate the playback duration
            duration = len(audio_data) / (
                self.audio_config.sample_rate * 2
            )  # 2 bytes per sample
            await asyncio.sleep(duration)

            # Return to listening
            await self._change_state(PipelineState.LISTENING)

            return audio_data

        except Exception as e:
            logger.error(f"Speech synthesis failed: {e}")
            await self._handle_error(e)
            return None

    async def _handle_error(self, error: Exception):
        """Handle pipeline errors."""
        await self._change_state(PipelineState.ERROR)

        if self._error_callback:
            await self._error_callback(error)

    async def cleanup(self):
        """Clean up session resources."""
        self.is_active = False
        await self.stop_listening()


class AudioPipeline:
    """Main audio pipeline orchestrator."""

    def __init__(
        self,
        stt_service: SpeechToTextService,
        tts_service: TextToSpeechService,
        audio_config: AudioConfig | None = None,
    ):
        self.stt_service = stt_service
        self.tts_service = tts_service
        self.audio_config = audio_config or AudioConfig()

        self.sessions: dict[str, AudioPipelineSession] = {}
        self.metrics = AudioPipelineMetrics()
        self._is_initialized = False

    async def initialize(self):
        """Initialize the audio pipeline."""
        try:
            # Initialize services
            await self.stt_service.initialize()
            await self.tts_service.initialize()

            self._is_initialized = True
            logger.info("Audio pipeline initialized")

        except Exception as e:
            logger.error(f"Failed to initialize audio pipeline: {e}")
            raise

    async def create_session(
        self,
        session_id: str,
        language: str = "en-US",
        callbacks: dict[str, Callable] | None = None,
    ) -> AudioPipelineSession:
        """Create a new audio session."""
        if not self._is_initialized:
            await self.initialize()

        # Create session
        session = AudioPipelineSession(
            session_id=session_id,
            audio_config=self.audio_config,
            stt_service=self.stt_service,
            tts_service=self.tts_service,
            language=language,
        )

        # Set callbacks
        if callbacks:
            session.set_callbacks(**callbacks)

        # Store session
        self.sessions[session_id] = session
        self.metrics.record_session_start()

        logger.info(f"Created audio session: {session_id}")
        return session

    async def get_session(self, session_id: str) -> AudioPipelineSession | None:
        """Get an existing session."""
        return self.sessions.get(session_id)

    async def close_session(self, session_id: str):
        """Close and clean up a session."""
        session = self.sessions.get(session_id)
        if session:
            await session.cleanup()
            del self.sessions[session_id]
            self.metrics.record_session_end()
            logger.info(f"Closed audio session: {session_id}")

    async def cleanup(self):
        """Clean up all resources."""
        # Close all sessions
        session_ids = list(self.sessions.keys())
        for session_id in session_ids:
            await self.close_session(session_id)

        # Clean up services
        await self.stt_service.cleanup()
        await self.tts_service.cleanup()

        self._is_initialized = False
        logger.info("Audio pipeline cleaned up")

    def get_metrics(self) -> AudioPipelineMetrics:
        """Get pipeline metrics."""
        return self.metrics
