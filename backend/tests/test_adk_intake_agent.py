"""Tests for ADK-based Intake Agent."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.adk_base import ReFrameResponse
from agents.adk_intake_agent import ADKIntakeAgent


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    with patch("agents.adk_base.get_settings") as mock:
        mock.return_value = MagicMock(
            google_ai_api_key="test-api-key",
            google_ai_model="gemini-1.5-flash",
        )
        yield mock


@pytest.fixture
def mock_adk_components():
    """Mock ADK components."""
    with (
        patch("agents.adk_base.LlmAgent") as mock_llm_agent,
        patch("agents.adk_base.LiteLlm") as mock_lite_llm,
        patch("agents.adk_intake_agent.get_all_reframe_tools") as mock_tools,
    ):

        agent_instance = AsyncMock()
        mock_llm_agent.return_value = agent_instance
        mock_tools.return_value = []

        yield {
            "llm_agent": agent_instance,
            "llm_agent_class": mock_llm_agent,
            "lite_llm": mock_lite_llm,
            "tools": mock_tools,
        }


class TestADKIntakeAgentInitialization:
    """Test ADK intake agent initialization."""

    def test_agent_initializes_with_correct_config(self, mock_settings, mock_adk_components):
        """Test intake agent initializes with correct configuration."""
        agent = ADKIntakeAgent()

        assert agent.name == "ADKIntakeAgent"
        assert "intake specialist" in agent.instructions.lower()
        assert "avoidant personality disorder" in agent.instructions.lower()

        # Verify tools were requested
        mock_adk_components["tools"].assert_called_once()

    def test_agent_has_intake_specific_instructions(self, mock_settings, mock_adk_components):
        """Test agent has intake-specific instructions."""
        agent = ADKIntakeAgent()

        instructions = agent.instructions.lower()

        # Check for key intake responsibilities
        assert "validate user input" in instructions
        assert "harmful content" in instructions
        assert "crisis situations" in instructions
        assert "avpd" in instructions

        # Check for expected output format
        assert "is_valid" in agent.instructions
        assert "requires_crisis_support" in agent.instructions
        assert "extracted_elements" in agent.instructions


class TestADKIntakeAgentInputValidation:
    """Test input validation methods."""

    def test_validate_input_length_accepts_valid_input(self, mock_settings, mock_adk_components):
        """Test input length validation accepts valid input."""
        agent = ADKIntakeAgent()

        # Valid length (between 5 and 500 words)
        valid_input = "I feel really anxious about my upcoming presentation at work tomorrow."
        assert agent._validate_input_length(valid_input) is True

    def test_validate_input_length_rejects_too_short(self, mock_settings, mock_adk_components):
        """Test input length validation rejects too short input."""
        agent = ADKIntakeAgent()

        # Too short (less than 5 words)
        short_input = "I feel bad"
        assert agent._validate_input_length(short_input) is False

    def test_validate_input_length_rejects_too_long(self, mock_settings, mock_adk_components):
        """Test input length validation rejects too long input."""
        agent = ADKIntakeAgent()

        # Too long (more than 500 words)
        long_input = " ".join(["word"] * 501)
        assert agent._validate_input_length(long_input) is False

    def test_check_for_urls_detects_urls(self, mock_settings, mock_adk_components):
        """Test URL detection in user input."""
        agent = ADKIntakeAgent()

        # Test various URL formats
        assert agent._check_for_urls("Visit https://example.com for help") is True
        assert agent._check_for_urls("Check out www.example.com") is True
        assert agent._check_for_urls("Go to http://test.org") is True
        assert agent._check_for_urls("No URLs in this text") is False

    def test_check_for_crisis_REDACTED(
        self, mock_settings, mock_adk_components
    ):
        """Test crisis keyword detection."""
        agent = ADKIntakeAgent()

        # Test crisis indicators
        assert agent._check_for_crisis_keywords("I want to kill myself") is True
        assert agent._check_for_crisis_keywords("I'm thinking about suicide") is True
        assert agent._check_for_crisis_keywords("I want to hurt myself") is True
        assert agent._check_for_crisis_keywords("I'd be better off dead") is True

        # Test non-crisis content
        assert agent._check_for_crisis_keywords("I feel sad and anxious") is False
        assert agent._check_for_crisis_keywords("I'm having a bad day") is False


class TestADKIntakeAgentProcessUserInput:
    """Test user input processing."""

    @pytest.mark.asyncio
    async def test_process_user_input_rejects_short_input(self, mock_settings, mock_adk_components):
        """Test processing rejects input that's too short."""
        agent = ADKIntakeAgent()

        result = await agent.process_user_input("Too short")

        assert isinstance(result, ReFrameResponse)
        assert result.success is False
        assert "between 5 and 500 words" in result.error
        assert result.error_type == "validation"

    @pytest.mark.asyncio
    async def test_process_user_input_rejects_urls(self, mock_settings, mock_adk_components):
        """Test processing rejects input with URLs."""
        agent = ADKIntakeAgent()

        result = await agent.process_user_input(
            "I found this helpful site https://example.com with lots of advice"
        )

        assert isinstance(result, ReFrameResponse)
        assert result.success is False
        assert "URLs are not allowed" in result.error
        assert result.error_type == "validation"

    @pytest.mark.asyncio
    async def test_process_user_input_successful_processing(
        self, mock_settings, mock_adk_components
    ):
        """Test successful processing of valid input."""
        agent = ADKIntakeAgent()

        # Mock successful ADK response
        mock_response = MagicMock()
        mock_part = MagicMock()
        mock_text = MagicMock()
        mock_text.text = '{"is_valid": true, "requires_crisis_support": false}'
        mock_part.text = mock_text
        mock_response.parts = [mock_part]
        mock_adk_components["llm_agent"].run_async.return_value = mock_response

        valid_input = "I feel really anxious about my upcoming presentation at work tomorrow and keep thinking everyone will judge me."
        result = await agent.process_user_input(valid_input)

        assert isinstance(result, ReFrameResponse)
        assert result.success is True
        assert result.response is not None

        # Verify the ADK agent was called with proper input data
        mock_adk_components["llm_agent"].run_async.assert_called_once()
        call_args = mock_adk_components["llm_agent"].run_async.call_args[0][0]
        call_content = call_args.parts[0].text.text

        assert valid_input in call_content
        assert "initial_intake" in call_content
        assert "crisis_flag" in call_content

    @pytest.mark.asyncio
    async def test_process_user_input_detects_crisis_content(
        self, mock_settings, mock_adk_components
    ):
        """Test processing detects and flags crisis content."""
        agent = ADKIntakeAgent()

        # Mock successful ADK response
        mock_response = MagicMock()
        mock_part = MagicMock()
        mock_text = MagicMock()
        mock_text.text = '{"is_valid": true, "requires_crisis_support": true}'
        mock_part.text = mock_text
        mock_response.parts = [mock_part]
        mock_adk_components["llm_agent"].run_async.return_value = mock_response

        crisis_input = (
            "I feel hopeless and want to kill myself because nothing will ever get better."
        )
        result = await agent.process_user_input(crisis_input)

        assert isinstance(result, ReFrameResponse)
        assert result.success is True

        # Verify crisis flag was set in the input data
        call_args = mock_adk_components["llm_agent"].run_async.call_args[0][0]
        call_content = call_args.parts[0].text.text
        assert '"crisis_flag": true' in call_content

        # Verify crisis detection was added to transparency
        if result.transparency_data:
            assert "crisis_detection" in result.transparency_data.techniques_used


class TestADKIntakeAgentReasoningPath:
    """Test reasoning path extraction."""

    def test_extract_reasoning_path_includes_intake_steps(self, mock_settings, mock_adk_components):
        """Test reasoning path includes intake-specific steps."""
        agent = ADKIntakeAgent()

        response = '{"is_valid": true, "extracted_elements": {"thoughts": ["test"]}}'
        reasoning_path = agent._extract_reasoning_path(response)

        assert reasoning_path["agent_type"] == "intake"
        assert reasoning_path["focus"] == "input_validation_and_pattern_identification"
        assert "Content validation and safety check" in reasoning_path["steps"]
        assert "AvPD-specific pattern recognition" in reasoning_path["steps"]

    def test_extract_techniques_used_identifies_techniques(
        self, mock_settings, mock_adk_components
    ):
        """Test technique extraction identifies used techniques."""
        agent = ADKIntakeAgent()

        # Test basic techniques
        response = '{"is_valid": true}'
        techniques = agent._extract_techniques_used(response)
        assert "content_validation" in techniques
        assert "pattern_identification" in techniques

        # Test crisis detection
        crisis_response = '{"requires_crisis_support": true, "crisis": "detected"}'
        techniques = agent._extract_techniques_used(crisis_response)
        assert "crisis_detection" in techniques

        # Test AvPD pattern recognition
        avpd_response = '{"identified_patterns": ["avoidant behavior"]}'
        techniques = agent._extract_techniques_used(avpd_response)
        assert "avpd_pattern_recognition" in techniques


class TestADKIntakeAgentConfiguration:
    """Test agent configuration methods."""

    def test_get_validation_rules_returns_correct_rules(self, mock_settings, mock_adk_components):
        """Test validation rules are returned correctly."""
        agent = ADKIntakeAgent()

        rules = agent.get_validation_rules()

        assert rules["min_word_count"] == 5
        assert rules["max_word_count"] == 500
        assert rules["url_check"] is True
        assert rules["crisis_detection"] is True
        assert "content_filtering" in rules

    def test_get_extracted_patterns_returns_avpd_patterns(self, mock_settings, mock_adk_components):
        """Test extracted patterns include AvPD-specific patterns."""
        agent = ADKIntakeAgent()

        patterns = agent.get_extracted_patterns()

        expected_patterns = [
            "fear_of_criticism",
            "social_avoidance",
            "perfectionism",
            "negative_self_talk",
            "catastrophic_thinking",
            "rejection_sensitivity",
        ]

        for pattern in expected_patterns:
            assert pattern in patterns


class TestADKIntakeAgentErrorHandling:
    """Test error handling in intake agent."""

    @pytest.mark.asyncio
    async def test_process_handles_adk_agent_errors(self, mock_settings, mock_adk_components):
        """Test processing handles errors from ADK agent gracefully."""
        agent = ADKIntakeAgent()

        # Mock ADK agent error
        mock_adk_components["llm_agent"].run_async.side_effect = Exception("ADK processing failed")

        valid_input = "I feel anxious about meeting new people at the conference next week."
        result = await agent.process_user_input(valid_input)

        assert isinstance(result, ReFrameResponse)
        assert result.success is False
        assert "ADK processing failed" in result.error
        assert result.transparency_data is not None
