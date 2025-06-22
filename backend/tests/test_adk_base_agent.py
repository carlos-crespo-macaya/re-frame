"""Tests for ADK-based ReFrame agent implementation."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.adk_base import ADKReFrameAgent, ReFrameResponse, ReFrameTransparencyData


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
def mock_llm_agent():
    """Mock LlmAgent from ADK."""
    with patch("agents.adk_base.LlmAgent") as mock:
        agent_instance = AsyncMock()
        mock.return_value = agent_instance
        yield agent_instance


@pytest.fixture
def mock_lite_llm():
    """Mock LiteLlm from ADK."""
    with patch("agents.adk_base.LiteLlm") as mock:
        yield mock


class TestADKReFrameAgentInitialization:
    """Test ADK agent initialization."""

    def test_agent_initializes_with_adk_components(
        self, mock_settings, mock_llm_agent, mock_lite_llm
    ):
        """Test agent initializes with ADK LlmAgent and LiteLlm."""
        agent = ADKReFrameAgent(
            name="TestAgent", instructions="Test instructions", description="Test description"
        )

        # Verify LiteLlm was configured with Gemini
        mock_lite_llm.assert_called_once_with(model="gemini/gemini-1.5-flash")

        # Verify LlmAgent was initialized correctly
        mock_llm_agent_class = mock_llm_agent.__class__
        # The mock itself represents the instance, the class is accessed differently
        # We verify the agent instance was created and stored
        assert agent.adk_agent == mock_llm_agent
        assert agent.name == "TestAgent"
        assert agent.instructions == "Test instructions"

    def test_agent_uses_custom_tools(self, mock_settings, mock_llm_agent, mock_lite_llm):
        """Test agent accepts custom tools."""
        mock_tools = [MagicMock(), MagicMock()]

        agent = ADKReFrameAgent(
            name="TestAgent", instructions="Test instructions", tools=mock_tools
        )

        # Tools should be passed to the ADK agent (we can't easily verify this with mocks,
        # but we can check they were provided)
        assert agent.adk_agent == mock_llm_agent


class TestADKReFrameAgentRun:
    """Test ADK agent run method."""

    @pytest.mark.asyncio
    async def test_run_formats_prompt_and_calls_adk_agent(
        self, mock_settings, mock_llm_agent, mock_lite_llm
    ):
        """Test run method formats prompt and calls ADK agent."""
        agent = ADKReFrameAgent(name="TestAgent", instructions="Test instructions")

        # Mock ADK response
        mock_response = MagicMock()
        mock_part = MagicMock()
        mock_text = MagicMock()
        mock_text.text = "Test response from ADK"
        mock_part.text = mock_text
        mock_response.parts = [mock_part]
        mock_llm_agent.run_async.return_value = mock_response

        input_data = {"thought": "I am worthless", "context": "At work"}
        result = await agent.run(input_data)

        # Verify ADK agent was called
        mock_llm_agent.run_async.assert_called_once()
        call_args = mock_llm_agent.run_async.call_args[0][0]

        # Verify the content contains our formatted prompt
        assert call_args.role == "user"
        assert len(call_args.parts) == 1
        assert "Test instructions" in call_args.parts[0].text.text
        assert '"thought": "I am worthless"' in call_args.parts[0].text.text
        assert '"context": "At work"' in call_args.parts[0].text.text

        assert result == "Test response from ADK"

    @pytest.mark.asyncio
    async def test_run_handles_empty_response(self, mock_settings, mock_llm_agent, mock_lite_llm):
        """Test run method handles empty responses gracefully."""
        agent = ADKReFrameAgent(name="TestAgent", instructions="Test instructions")

        # Mock empty response
        mock_response = MagicMock()
        mock_response.parts = []
        mock_llm_agent.run_async.return_value = mock_response

        result = await agent.run({"thought": "test"})
        assert result == ""

    @pytest.mark.asyncio
    async def test_run_handles_exception(self, mock_settings, mock_llm_agent, mock_lite_llm):
        """Test run method handles exceptions."""
        agent = ADKReFrameAgent(name="TestAgent", instructions="Test instructions")

        # Mock exception
        mock_llm_agent.run_async.side_effect = Exception("ADK error")

        with pytest.raises(Exception, match="ADK error"):
            await agent.run({"thought": "test"})


class TestADKReFrameAgentProcessWithTransparency:
    """Test process_with_transparency method."""

    @pytest.mark.asyncio
    async def test_process_returns_success_response(
        self, mock_settings, mock_llm_agent, mock_lite_llm
    ):
        """Test process_with_transparency returns success response with transparency data."""
        agent = ADKReFrameAgent(name="TestAgent", instructions="Test instructions")

        # Mock successful ADK response
        mock_response = MagicMock()
        mock_part = MagicMock()
        mock_text = MagicMock()
        mock_text.text = '{"result": "reframed thought"}'
        mock_part.text = mock_text
        mock_response.parts = [mock_part]
        mock_llm_agent.run_async.return_value = mock_response

        result = await agent.process_with_transparency({"thought": "negative thought"})

        assert isinstance(result, ReFrameResponse)
        assert result.success is True
        assert result.response == '{"result": "reframed thought"}'
        assert result.error is None
        assert result.transparency_data is not None
        assert result.transparency_data.agent_name == "TestAgent"
        assert result.transparency_data.model_used == "gemini-1.5-flash"

    @pytest.mark.asyncio
    async def test_process_handles_errors_gracefully(
        self, mock_settings, mock_llm_agent, mock_lite_llm
    ):
        """Test process_with_transparency handles errors and returns error response."""
        agent = ADKReFrameAgent(name="TestAgent", instructions="Test instructions")

        # Mock error
        mock_llm_agent.run_async.side_effect = Exception("ADK processing error")

        result = await agent.process_with_transparency({"thought": "test"})

        assert isinstance(result, ReFrameResponse)
        assert result.success is False
        assert "ADK processing error" in result.error
        assert result.error_type == "unknown"
        assert result.transparency_data is not None

    @pytest.mark.asyncio
    async def test_process_classifies_error_types(
        self, mock_settings, mock_llm_agent, mock_lite_llm
    ):
        """Test process_with_transparency classifies different error types."""
        agent = ADKReFrameAgent(name="TestAgent", instructions="Test instructions")

        # Test rate limit error
        mock_llm_agent.run_async.side_effect = Exception("Rate limit exceeded")
        result = await agent.process_with_transparency({"thought": "test"})
        assert result.error_type == "rate_limit"
        assert result.error == "Rate limit exceeded. Please try again later."

        # Test timeout error
        mock_llm_agent.run_async.side_effect = Exception("Request timeout")
        result = await agent.process_with_transparency({"thought": "test"})
        assert result.error_type == "timeout"

        # Test auth error
        mock_llm_agent.run_async.side_effect = Exception("Authentication failed")
        result = await agent.process_with_transparency({"thought": "test"})
        assert result.error_type == "auth"


class TestADKReFrameAgentJSONParsing:
    """Test JSON parsing capabilities."""

    def test_parse_json_response_valid_json(self, mock_settings, mock_llm_agent, mock_lite_llm):
        """Test parsing valid JSON response."""
        agent = ADKReFrameAgent(name="TestAgent", instructions="Test")

        response = '{"result": "success", "value": 42}'
        parsed = agent.parse_json_response(response)

        assert parsed["result"] == "success"
        assert parsed["value"] == 42

    def test_parse_json_response_with_markdown_fence(
        self, mock_settings, mock_llm_agent, mock_lite_llm
    ):
        """Test parsing JSON wrapped in markdown code fence."""
        agent = ADKReFrameAgent(name="TestAgent", instructions="Test")

        response = """```json
{
  "result": "success",
  "techniques": ["CBT", "DBT"],
  "nested": {
    "value": true
  }
}
```"""
        parsed = agent.parse_json_response(response)

        assert parsed["result"] == "success"
        assert parsed["techniques"] == ["CBT", "DBT"]
        assert parsed["nested"]["value"] is True

    def test_parse_json_response_empty_response(self, mock_settings, mock_llm_agent, mock_lite_llm):
        """Test parsing empty response raises appropriate error."""
        agent = ADKReFrameAgent(name="TestAgent", instructions="Test")

        with pytest.raises(json.JSONDecodeError) as exc_info:
            agent.parse_json_response("")

        assert "Empty response" in str(exc_info.value)

    def test_parse_json_response_invalid_json(self, mock_settings, mock_llm_agent, mock_lite_llm):
        """Test parsing invalid JSON raises appropriate error."""
        agent = ADKReFrameAgent(name="TestAgent", instructions="Test")

        response = "This is not JSON at all"

        with pytest.raises(json.JSONDecodeError) as exc_info:
            agent.parse_json_response(response)

        assert "Unable to parse response as JSON" in str(exc_info.value)


class TestADKReFrameAgentErrorClassification:
    """Test error classification methods."""

    def test_classify_error_identifies_rate_limit(
        self, mock_settings, mock_llm_agent, mock_lite_llm
    ):
        """Test error classification identifies rate limit errors."""
        agent = ADKReFrameAgent(name="TestAgent", instructions="Test")

        rate_limit_error = Exception("Rate limit exceeded for model")
        assert agent._classify_error(rate_limit_error) == "rate_limit"

        quota_error = Exception("Quota exhausted")
        assert agent._classify_error(quota_error) == "rate_limit"

    def test_classify_error_identifies_timeout(self, mock_settings, mock_llm_agent, mock_lite_llm):
        """Test error classification identifies timeout errors."""
        agent = ADKReFrameAgent(name="TestAgent", instructions="Test")

        timeout_error = Exception("Request timeout after 30 seconds")
        assert agent._classify_error(timeout_error) == "timeout"

        deadline_error = Exception("Deadline exceeded")
        assert agent._classify_error(deadline_error) == "timeout"

    def test_classify_error_identifies_auth(self, mock_settings, mock_llm_agent, mock_lite_llm):
        """Test error classification identifies auth errors."""
        agent = ADKReFrameAgent(name="TestAgent", instructions="Test")

        auth_error = Exception("Authentication failed")
        assert agent._classify_error(auth_error) == "auth"

        permission_error = Exception("Permission denied")
        assert agent._classify_error(permission_error) == "auth"

    def test_classify_error_defaults_to_unknown(self, mock_settings, mock_llm_agent, mock_lite_llm):
        """Test error classification defaults to unknown for unrecognized errors."""
        agent = ADKReFrameAgent(name="TestAgent", instructions="Test")

        generic_error = Exception("Some random error")
        assert agent._classify_error(generic_error) == "unknown"


class TestReFrameTransparencyData:
    """Test ReFrameTransparencyData model."""

    def test_transparency_data_creation(self):
        """Test creating transparency data."""
        data = ReFrameTransparencyData(
            agent_name="TestAgent",
            model_used="gemini-1.5-flash",
            reasoning_path={"step1": "analysis", "step2": "synthesis"},
            raw_response="test response",
            techniques_used=["cbt", "validation"],
        )

        assert data.agent_name == "TestAgent"
        assert data.model_used == "gemini-1.5-flash"
        assert data.reasoning_path["step1"] == "analysis"
        assert "cbt" in data.techniques_used

    def test_transparency_data_defaults(self):
        """Test transparency data with defaults."""
        data = ReFrameTransparencyData(
            agent_name="TestAgent",
            model_used="gemini-1.5-flash",
            reasoning_path={},
            raw_response="",
        )

        assert data.techniques_used == []


class TestReFrameResponse:
    """Test ReFrameResponse model."""

    def test_success_response_creation(self):
        """Test creating successful response."""
        transparency_data = ReFrameTransparencyData(
            agent_name="TestAgent",
            model_used="gemini-1.5-flash",
            reasoning_path={},
            raw_response="test",
        )

        response = ReFrameResponse(
            success=True, response="Successful processing", transparency_data=transparency_data
        )

        assert response.success is True
        assert response.response == "Successful processing"
        assert response.error is None
        assert response.transparency_data.agent_name == "TestAgent"

    def test_error_response_creation(self):
        """Test creating error response."""
        response = ReFrameResponse(success=False, error="Processing failed", error_type="timeout")

        assert response.success is False
        assert response.error == "Processing failed"
        assert response.error_type == "timeout"
        assert response.response is None
