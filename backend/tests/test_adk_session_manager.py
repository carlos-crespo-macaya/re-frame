"""Tests for ADK Session Manager."""

from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

import pytest

from agents.adk_session_manager import ADKSessionManager, SessionData
from agents.adk_base import ReFrameResponse, ReFrameTransparencyData


@pytest.fixture
def mock_agents():
    """Mock ADK agents."""
    with patch("agents.adk_session_manager.ADKIntakeAgent") as mock_intake, \
         patch("agents.adk_session_manager.ADKCBTFrameworkAgent") as mock_cbt, \
         patch("agents.adk_session_manager.ADKSynthesisAgent") as mock_synthesis:
        
        # Create mock instances
        intake_instance = AsyncMock()
        cbt_instance = AsyncMock()
        synthesis_instance = AsyncMock()
        
        mock_intake.return_value = intake_instance
        mock_cbt.return_value = cbt_instance
        mock_synthesis.return_value = synthesis_instance
        
        yield {
            "intake": intake_instance,
            "cbt": cbt_instance,
            "synthesis": synthesis_instance
        }


class TestSessionData:
    """Test SessionData class."""

    def test_session_data_initialization(self):
        """Test SessionData initializes with correct defaults."""
        session = SessionData()

        assert session.session_id is not None
        assert len(session.session_id) > 0
        assert isinstance(session.created_at, datetime)
        assert isinstance(session.last_activity, datetime)
        assert session.user_inputs == []
        assert session.agent_responses == []
        assert session.workflow_state == "initial"
        assert session.crisis_flags == []
        assert session.transparency_log == []

    def test_session_data_with_custom_id(self):
        """Test SessionData accepts custom session ID."""
        custom_id = "test-session-123"
        session = SessionData(session_id=custom_id)

        assert session.session_id == custom_id


class TestADKSessionManagerInitialization:
    """Test session manager initialization."""

    def test_session_manager_initializes_agents(self, mock_agents):
        """Test session manager initializes all required agents."""
        manager = ADKSessionManager()

        assert manager.intake_agent == mock_agents["intake"]
        assert manager.cbt_agent == mock_agents["cbt"]
        assert manager.synthesis_agent == mock_agents["synthesis"]
        assert manager.sessions == {}


class TestADKSessionManagerSessionManagement:
    """Test session management functionality."""

    def test_create_session_generates_unique_id(self, mock_agents):
        """Test session creation generates unique session ID."""
        manager = ADKSessionManager()

        session_id1 = manager.create_session()
        session_id2 = manager.create_session()

        assert session_id1 != session_id2
        assert session_id1 in manager.sessions
        assert session_id2 in manager.sessions

    def test_get_session_returns_correct_session(self, mock_agents):
        """Test getting session by ID."""
        manager = ADKSessionManager()

        session_id = manager.create_session()
        session = manager.get_session(session_id)

        assert session is not None
        assert session.session_id == session_id

    def test_get_session_returns_none_for_invalid_id(self, mock_agents):
        """Test getting session with invalid ID returns None."""
        manager = ADKSessionManager()

        session = manager.get_session("invalid-id")

        assert session is None


class TestADKSessionManagerWorkflow:
    """Test multi-agent workflow processing."""

    @pytest.mark.asyncio
    async def test_process_user_input_successful_workflow(self, mock_agents):
        """Test successful processing through complete workflow."""
        manager = ADKSessionManager()

        # Mock successful responses from each agent
        intake_transparency = ReFrameTransparencyData(
            agent_name="ADKIntakeAgent",
            model_used="gemini-1.5-flash",
            reasoning_path={"agent_type": "intake"},
            raw_response='{"is_valid": true, "requires_crisis_support": false}'
        )
        intake_response = ReFrameResponse(
            success=True,
            response='{"is_valid": true, "requires_crisis_support": false}',
            transparency_data=intake_transparency
        )
        mock_agents["intake"].process_user_input.return_value = intake_response

        cbt_transparency = ReFrameTransparencyData(
            agent_name="ADKCBTFrameworkAgent",
            model_used="gemini-1.5-flash",
            reasoning_path={"agent_type": "cbt"},
            raw_response='{"reframed_thoughts": [{"thought": "balanced view"}]}'
        )
        cbt_response = ReFrameResponse(
            success=True,
            response='{"reframed_thoughts": [{"thought": "balanced view"}]}',
            transparency_data=cbt_transparency
        )
        mock_agents["cbt"].apply_cbt_techniques.return_value = cbt_response

        synthesis_transparency = ReFrameTransparencyData(
            agent_name="ADKSynthesisAgent",
            model_used="gemini-1.5-flash",
            reasoning_path={"agent_type": "synthesis"},
            raw_response='{"main_response": "Here is a supportive response..."}'
        )
        synthesis_response = ReFrameResponse(
            success=True,
            response='{"main_response": "Here is a supportive response..."}',
            transparency_data=synthesis_transparency
        )
        mock_agents["synthesis"].create_user_response.return_value = synthesis_response

        # Process user input
        user_input = "I feel anxious about my presentation tomorrow."
        result = await manager.process_user_input(user_input)

        # Verify successful workflow completion
        assert result["success"] is True
        assert result["response"] is not None
        assert result["workflow_stage"] == "completed"
        assert result["session_id"] is not None
        assert result["crisis_flag"] is False

        # Verify transparency data
        assert "transparency" in result
        assert len(result["transparency"]["agents_used"]) == 3
        assert "ADKIntakeAgent" in result["transparency"]["agents_used"]
        assert "ADKCBTFrameworkAgent" in result["transparency"]["agents_used"]
        assert "ADKSynthesisAgent" in result["transparency"]["agents_used"]

        # Verify agents were called in correct order
        mock_agents["intake"].process_user_input.assert_called_once_with(user_input)
        mock_agents["cbt"].apply_cbt_techniques.assert_called_once()
        mock_agents["synthesis"].create_user_response.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_user_input_intake_validation_failure(self, mock_agents):
        """Test workflow stops at intake validation failure."""
        manager = ADKSessionManager()

        # Mock intake validation failure
        intake_response = ReFrameResponse(
            success=False,
            error="Input too short",
            error_type="validation"
        )
        mock_agents["intake"].process_user_input.return_value = intake_response

        user_input = "Too short"
        result = await manager.process_user_input(user_input)

        # Verify workflow stopped at intake
        assert result["success"] is False
        assert result["error"] == "Input too short"
        assert result["workflow_stage"] == "intake_validation"

        # Verify subsequent agents were not called
        mock_agents["intake"].process_user_input.assert_called_once()
        mock_agents["cbt"].apply_cbt_techniques.assert_not_called()
        mock_agents["synthesis"].create_user_response.assert_not_called()

    @pytest.mark.asyncio
    async def test_process_user_input_crisis_detection(self, mock_agents):
        """Test workflow handles crisis detection."""
        manager = ADKSessionManager()

        # Mock intake response with crisis flag
        intake_transparency = ReFrameTransparencyData(
            agent_name="ADKIntakeAgent",
            model_used="gemini-1.5-flash",
            reasoning_path={"agent_type": "intake"},
            raw_response='{"is_valid": true, "requires_crisis_support": true}'
        )
        intake_response = ReFrameResponse(
            success=True,
            response='{"is_valid": true, "requires_crisis_support": true}',
            transparency_data=intake_transparency
        )
        mock_agents["intake"].process_user_input.return_value = intake_response

        # Mock crisis response from synthesis agent
        crisis_transparency = ReFrameTransparencyData(
            agent_name="ADKSynthesisAgent",
            model_used="gemini-1.5-flash",
            reasoning_path={"agent_type": "synthesis"},
            raw_response='{"main_response": "Crisis support resources..."}'
        )
        crisis_response = ReFrameResponse(
            success=True,
            response='{"main_response": "Crisis support resources..."}',
            transparency_data=crisis_transparency
        )
        mock_agents["synthesis"].create_crisis_response.return_value = crisis_response

        user_input = "I want to hurt myself because I can't cope anymore."
        result = await manager.process_user_input(user_input)

        # Verify crisis workflow
        assert result["success"] is True
        assert result["crisis_flag"] is True
        assert result["workflow_stage"] == "crisis_response"

        # Verify crisis response was called
        mock_agents["synthesis"].create_crisis_response.assert_called_once()
        
        # Verify CBT agent was skipped
        mock_agents["cbt"].apply_cbt_techniques.assert_not_called()

    @pytest.mark.asyncio
    async def test_process_user_input_with_existing_session(self, mock_agents):
        """Test processing with existing session ID."""
        manager = ADKSessionManager()

        # Create session
        session_id = manager.create_session()

        # Mock successful responses
        intake_response = ReFrameResponse(
            success=True,
            response='{"is_valid": true, "requires_crisis_support": false}'
        )
        mock_agents["intake"].process_user_input.return_value = intake_response

        cbt_response = ReFrameResponse(
            success=True,
            response='{"reframed_thoughts": []}'
        )
        mock_agents["cbt"].apply_cbt_techniques.return_value = cbt_response

        synthesis_response = ReFrameResponse(
            success=True,
            response='{"main_response": "response"}'
        )
        mock_agents["synthesis"].create_user_response.return_value = synthesis_response

        user_input = "I feel anxious about work."
        result = await manager.process_user_input(user_input, session_id=session_id)

        # Verify same session was used
        assert result["session_id"] == session_id

        # Verify session was updated
        session = manager.get_session(session_id)
        assert user_input in session.user_inputs
        assert len(session.agent_responses) == 1

    @pytest.mark.asyncio
    async def test_process_user_input_cbt_error(self, mock_agents):
        """Test workflow handles CBT processing error."""
        manager = ADKSessionManager()

        # Mock successful intake
        intake_response = ReFrameResponse(
            success=True,
            response='{"is_valid": true, "requires_crisis_support": false}'
        )
        mock_agents["intake"].process_user_input.return_value = intake_response

        # Mock CBT error
        cbt_response = ReFrameResponse(
            success=False,
            error="CBT processing failed",
            error_type="processing_error"
        )
        mock_agents["cbt"].apply_cbt_techniques.return_value = cbt_response

        user_input = "I feel anxious."
        result = await manager.process_user_input(user_input)

        # Verify workflow stopped at CBT
        assert result["success"] is False
        assert result["error"] == "CBT processing failed"
        assert result["workflow_stage"] == "cbt_processing"

        # Verify synthesis was not called
        mock_agents["synthesis"].create_user_response.assert_not_called()


class TestADKSessionManagerUtilities:
    """Test utility methods."""

    def test_get_session_history_returns_correct_data(self, mock_agents):
        """Test getting session history."""
        manager = ADKSessionManager()

        session_id = manager.create_session()
        session = manager.get_session(session_id)
        
        # Add some test data
        session.user_inputs.append("Test input")
        session.agent_responses.append({"test": "response"})
        session.workflow_state = "completed"

        history = manager.get_session_history(session_id)

        assert history is not None
        assert history["session_id"] == session_id
        assert history["workflow_state"] == "completed"
        assert history["response_count"] == 1
        assert "created_at" in history
        assert "last_activity" in history

    def test_get_session_history_invalid_id(self, mock_agents):
        """Test getting history for invalid session ID."""
        manager = ADKSessionManager()

        history = manager.get_session_history("invalid-id")

        assert history is None

    def test_cleanup_expired_sessions(self, mock_agents):
        """Test cleaning up expired sessions."""
        manager = ADKSessionManager()

        # Create sessions
        session_id1 = manager.create_session()
        session_id2 = manager.create_session()

        # Make one session old
        old_session = manager.get_session(session_id1)
        old_session.last_activity = datetime.utcnow() - timedelta(hours=25)

        # Clean up sessions older than 24 hours
        cleaned_count = manager.cleanup_expired_sessions(max_age_hours=24)

        assert cleaned_count == 1
        assert session_id1 not in manager.sessions
        assert session_id2 in manager.sessions


class TestADKSessionManagerResponseParsing:
    """Test response parsing methods."""

    def test_parse_intake_response_valid_json(self, mock_agents):
        """Test parsing valid intake response."""
        manager = ADKSessionManager()

        response = '{"is_valid": true, "requires_crisis_support": false}'
        parsed = manager._parse_intake_response(response)

        assert parsed is not None
        assert parsed["is_valid"] is True
        assert parsed["requires_crisis_support"] is False

    def test_parse_intake_response_invalid_json(self, mock_agents):
        """Test parsing invalid intake response."""
        manager = ADKSessionManager()

        response = "This is not JSON"
        parsed = manager._parse_intake_response(response)

        assert parsed is None

    def test_parse_cbt_response_valid_json(self, mock_agents):
        """Test parsing valid CBT response."""
        manager = ADKSessionManager()

        response = '{"reframed_thoughts": [{"thought": "balanced view"}]}'
        parsed = manager._parse_cbt_response(response)

        assert parsed is not None
        assert "reframed_thoughts" in parsed

    def test_parse_cbt_response_invalid_json(self, mock_agents):
        """Test parsing invalid CBT response."""
        manager = ADKSessionManager()

        response = "Invalid JSON content"
        parsed = manager._parse_cbt_response(response)

        assert parsed is None