"""Tests for voice stream handler."""

import asyncio
import base64
import json
from unittest.mock import MagicMock, patch

import pytest

from src.voice.session_manager import VoiceSession
from src.voice.stream_handler import create_voice_stream


class TestVoiceStreamHandler:
    """Test suite for voice stream handler."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock voice session."""
        session = MagicMock(spec=VoiceSession)
        session.session_id = "test-session-123"
        session.status = "active"
        session.agent_queue = asyncio.Queue()
        return session

    @pytest.mark.asyncio
    async def test_initial_connected_message(self, mock_session):
        """Test that stream sends initial connected message."""
        # Create stream generator
        stream = create_voice_stream(mock_session)

        # Get first message
        first_message = await anext(stream)

        # Parse the SSE message
        assert first_message.startswith("data: ")
        json_data = json.loads(first_message[6:].strip())

        # Verify it's a connected message
        assert json_data["type"] == "turn_complete"
        assert json_data["data"] == "connected"

    @pytest.mark.asyncio
    async def test_text_message_streaming(self, mock_session):
        """Test streaming of text messages."""
        # Create a mock event with text content
        mock_event = MagicMock()
        mock_event.partial = False
        mock_event.content = MagicMock()
        mock_part = MagicMock()
        mock_part.text = "Hello, how can I help you?"
        mock_part.inline_data = None
        mock_event.content.parts = [mock_part]
        mock_event.turn_complete = False

        # Add event to queue
        await mock_session.agent_queue.put(mock_event)

        # Create stream generator
        stream = create_voice_stream(mock_session)

        # Skip initial connected message
        await anext(stream)

        # Get text message
        text_message = await anext(stream)

        # Parse and verify
        json_data = json.loads(text_message[6:].strip())
        assert json_data["type"] == "transcript"
        assert json_data["text"] == "Hello, how can I help you?"
        assert json_data["is_final"] is True

    @pytest.mark.asyncio
    async def test_audio_message_streaming(self, mock_session):
        """Test streaming of audio messages."""
        # Create a mock event with audio content
        mock_event = MagicMock()
        mock_event.content = MagicMock()
        mock_part = MagicMock()
        mock_part.text = None
        mock_part.inline_data = MagicMock()
        mock_part.inline_data.mime_type = "audio/wav"
        mock_part.inline_data.data = b"fake_audio_data"
        mock_event.content.parts = [mock_part]
        mock_event.turn_complete = False

        # Add event to queue
        await mock_session.agent_queue.put(mock_event)

        # Create stream generator
        stream = create_voice_stream(mock_session)

        # Skip initial connected message
        await anext(stream)

        # Get audio message
        audio_message = await anext(stream)

        # Parse and verify
        json_data = json.loads(audio_message[6:].strip())
        assert json_data["type"] == "audio"
        assert json_data["data"] == base64.b64encode(b"fake_audio_data").decode("ascii")

    @pytest.mark.asyncio
    async def test_turn_complete_message(self, mock_session):
        """Test turn complete message handling."""
        # Create a mock turn complete event
        mock_event = MagicMock()
        mock_event.turn_complete = True
        mock_event.interrupted = False
        mock_event.content = None

        # Add event to queue
        await mock_session.agent_queue.put(mock_event)

        # Create stream generator
        stream = create_voice_stream(mock_session)

        # Skip initial connected message
        await anext(stream)

        # Get turn complete message
        turn_message = await anext(stream)

        # Parse and verify
        json_data = json.loads(turn_message[6:].strip())
        assert json_data["type"] == "turn_complete"
        assert json_data.get("interrupted") is False

    @pytest.mark.asyncio
    async def test_error_handling(self, mock_session):
        """Test error message handling."""
        # Create an error event
        error_event = {"type": "error", "error": "Test error message"}

        # Add event to queue
        await mock_session.agent_queue.put(error_event)

        # Create stream generator
        stream = create_voice_stream(mock_session)

        # Skip initial connected message
        await anext(stream)

        # Get error message
        error_message = await anext(stream)

        # Parse and verify
        json_data = json.loads(error_message[6:].strip())
        assert json_data["type"] == "error"
        assert json_data["error"] == "Test error message"

        # Stream should end after error
        with pytest.raises(StopAsyncIteration):
            await anext(stream)

    @pytest.mark.asyncio
    async def test_session_ended_handling(self, mock_session):
        """Test handling when session status changes to ended."""
        # Create stream generator
        stream = create_voice_stream(mock_session)

        # Skip initial connected message
        await anext(stream)

        # Change session status to ended
        mock_session.status = "ended"

        # Should get session ended message
        end_message = await anext(stream)

        # Parse and verify
        json_data = json.loads(end_message[6:].strip())
        assert json_data["type"] == "turn_complete"
        assert json_data["data"] == "session_ended"

    @pytest.mark.asyncio
    async def test_cancellation_handling(self, mock_session):
        """Test handling of stream cancellation."""
        # Create stream generator
        stream = create_voice_stream(mock_session)

        # Skip initial connected message
        await anext(stream)

        # Simulate cancellation by putting a CancelledError in the queue
        async def raise_cancelled():
            raise asyncio.CancelledError()

        with patch.object(mock_session.agent_queue, "get", side_effect=raise_cancelled):
            # Get cancellation message
            cancel_message = await anext(stream)

            # Parse and verify
            json_data = json.loads(cancel_message[6:].strip())
            assert json_data["type"] == "turn_complete"
            assert json_data["data"] == "stream_cancelled"

            # Stream should end after cancellation
            with pytest.raises(StopAsyncIteration):
                await anext(stream)

    @pytest.mark.asyncio
    async def test_websocket_error_handling(self, mock_session):
        """Test specific WebSocket error handling."""

        # Create an exception event that mentions WebSocket
        async def raise_websocket_error():
            raise Exception("WebSocket connection failed")

        # Create stream generator
        stream = create_voice_stream(mock_session)

        # Skip initial connected message
        await anext(stream)

        with patch.object(
            mock_session.agent_queue, "get", side_effect=raise_websocket_error
        ):
            # Get error message
            error_message = await anext(stream)

            # Parse and verify
            json_data = json.loads(error_message[6:].strip())
            assert json_data["type"] == "error"
            assert json_data["error"] == "Connection error. Please try again."

    @pytest.mark.asyncio
    async def test_audio_format_error_handling(self, mock_session):
        """Test specific audio format error handling."""

        # Create an exception event that mentions 1007
        async def raise_audio_error():
            raise Exception("Error code 1007: Invalid audio format")

        # Create stream generator
        stream = create_voice_stream(mock_session)

        # Skip initial connected message
        await anext(stream)

        with patch.object(
            mock_session.agent_queue, "get", side_effect=raise_audio_error
        ):
            # Get error message
            error_message = await anext(stream)

            # Parse and verify
            json_data = json.loads(error_message[6:].strip())
            assert json_data["type"] == "error"
            assert (
                json_data["error"] == "Audio format error. Please check audio encoding."
            )

    @pytest.mark.asyncio
    async def test_multiple_parts_in_event(self, mock_session):
        """Test handling events with multiple parts."""
        # Create a mock event with both text and audio parts
        mock_event = MagicMock()
        mock_event.partial = False
        mock_event.content = MagicMock()

        # Text part
        text_part = MagicMock()
        text_part.text = "Here is the response"
        text_part.inline_data = None

        # Audio part
        audio_part = MagicMock()
        audio_part.text = None
        audio_part.inline_data = MagicMock()
        audio_part.inline_data.mime_type = "audio/wav"
        audio_part.inline_data.data = b"audio_content"

        mock_event.content.parts = [text_part, audio_part]
        mock_event.turn_complete = False

        # Add event to queue
        await mock_session.agent_queue.put(mock_event)

        # Create stream generator
        stream = create_voice_stream(mock_session)

        # Skip initial connected message
        await anext(stream)

        # Should get text message first
        text_message = await anext(stream)
        json_data = json.loads(text_message[6:].strip())
        assert json_data["type"] == "transcript"
        assert json_data["text"] == "Here is the response"

        # Then audio message
        audio_message = await anext(stream)
        json_data = json.loads(audio_message[6:].strip())
        assert json_data["type"] == "audio"
        assert json_data["data"] == base64.b64encode(b"audio_content").decode("ascii")

    @pytest.mark.asyncio
    async def test_partial_transcript_handling(self, mock_session):
        """Test handling of partial transcripts."""
        # Create a mock event with partial flag
        mock_event = MagicMock()
        mock_event.partial = True
        mock_event.content = MagicMock()
        mock_part = MagicMock()
        mock_part.text = "This is a partial..."
        mock_part.inline_data = None
        mock_event.content.parts = [mock_part]
        mock_event.turn_complete = False

        # Add event to queue
        await mock_session.agent_queue.put(mock_event)

        # Create stream generator
        stream = create_voice_stream(mock_session)

        # Skip initial connected message
        await anext(stream)

        # Get partial transcript message
        partial_message = await anext(stream)

        # Parse and verify
        json_data = json.loads(partial_message[6:].strip())
        assert json_data["type"] == "transcript"
        assert json_data["text"] == "This is a partial..."
        assert json_data["is_final"] is False
