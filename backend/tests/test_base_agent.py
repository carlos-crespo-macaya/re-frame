"""Tests for ReFrameAgent base class with Google AI Studio integration."""

import json
from unittest.mock import MagicMock, patch

import pytest
from google.api_core import exceptions as google_exceptions

from agents.base import ReFrameAgent


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    with patch("agents.base.get_settings") as mock:
        mock.return_value = MagicMock(
            google_ai_api_key="test-api-key",
            google_ai_model="gemini-1.5-flash",
            google_ai_temperature=0.7,
            google_ai_max_tokens=2048,
        )
        yield mock


@pytest.fixture
def mock_genai():
    """Mock Google AI SDK."""
    with patch("agents.base.genai") as mock:
        yield mock


@pytest.fixture
def mock_model():
    """Mock GenerativeModel."""
    with patch("agents.base.GenerativeModel") as mock:
        model_instance = MagicMock()
        mock.return_value = model_instance
        yield model_instance


class TestReFrameAgentInitialization:
    """Test agent initialization and configuration."""

    def test_agent_configures_google_ai_with_api_key(self, mock_settings, mock_genai, mock_model):
        """Test agent configures Google AI with API key from settings."""
        agent = ReFrameAgent(name="TestAgent", instructions="Test instructions")

        mock_genai.configure.assert_called_once_with(api_key="test-api-key")
        assert agent.name == "TestAgent"
        assert agent.instructions == "Test instructions"

    def test_agent_creates_model_with_correct_config(self, mock_settings, mock_genai):
        """Test agent creates GenerativeModel with correct configuration."""
        with patch("agents.base.GenerativeModel") as mock_model_class:
            agent = ReFrameAgent(name="TestAgent", instructions="Test instructions")

            mock_model_class.assert_called_once_with(
                model_name="gemini-1.5-flash",
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 2048,
                },
            )

    def test_agent_uses_provided_model_if_given(self, mock_settings, mock_genai):
        """Test agent uses provided model instead of creating new one."""
        custom_model = MagicMock()
        agent = ReFrameAgent(name="TestAgent", instructions="Test instructions", model=custom_model)

        assert agent.model == custom_model


class TestReFrameAgentRun:
    """Test agent run method with actual API calls."""

    @pytest.mark.asyncio
    async def test_run_generates_content_with_formatted_prompt(
        self, mock_settings, mock_genai, mock_model
    ):
        """Test run method formats prompt and calls generate_content."""
        agent = ReFrameAgent(name="TestAgent", instructions="Test instructions")

        # Mock response
        mock_response = MagicMock()
        mock_response.text = '{"result": "test response"}'
        agent.model.generate_content.return_value = mock_response

        input_data = {"thought": "I am worthless", "context": "At work"}
        result = await agent.run(input_data)

        # Verify prompt formatting
        expected_prompt = """
Test instructions

Input data:
{
  "thought": "I am worthless",
  "context": "At work"
}

Please provide your response in the exact JSON format specified in the instructions.
"""
        agent.model.generate_content.assert_called_once_with(expected_prompt)
        assert result == '{"result": "test response"}'

    @pytest.mark.asyncio
    async def test_run_handles_rate_limit_error(self, mock_settings, mock_genai, mock_model):
        """Test run method handles rate limit errors from Google AI."""
        agent = ReFrameAgent(name="TestAgent", instructions="Test instructions")

        # Mock rate limit error
        agent.model.generate_content.side_effect = google_exceptions.ResourceExhausted(
            "Rate limit exceeded"
        )

        with pytest.raises(google_exceptions.ResourceExhausted):
            await agent.run({"thought": "test"})

    @pytest.mark.asyncio
    async def test_run_handles_timeout_error(self, mock_settings, mock_genai, mock_model):
        """Test run method handles timeout errors."""
        agent = ReFrameAgent(name="TestAgent", instructions="Test instructions")

        # Mock timeout error
        agent.model.generate_content.side_effect = google_exceptions.DeadlineExceeded(
            "Request timeout"
        )

        with pytest.raises(google_exceptions.DeadlineExceeded):
            await agent.run({"thought": "test"})

    @pytest.mark.asyncio
    async def test_run_handles_invalid_api_key(self, mock_settings, mock_genai, mock_model):
        """Test run method handles invalid API key errors."""
        agent = ReFrameAgent(name="TestAgent", instructions="Test instructions")

        # Mock authentication error
        agent.model.generate_content.side_effect = google_exceptions.Unauthenticated(
            "Invalid API key"
        )

        with pytest.raises(google_exceptions.Unauthenticated):
            await agent.run({"thought": "test"})

    @pytest.mark.asyncio
    async def test_run_handles_empty_response(self, mock_settings, mock_genai, mock_model):
        """Test run method handles empty responses gracefully."""
        agent = ReFrameAgent(name="TestAgent", instructions="Test instructions")

        # Mock empty response
        mock_response = MagicMock()
        mock_response.text = ""
        agent.model.generate_content.return_value = mock_response

        result = await agent.run({"thought": "test"})
        assert result == ""

    @pytest.mark.asyncio
    async def test_run_handles_malformed_response(self, mock_settings, mock_genai, mock_model):
        """Test run method returns raw text even if not valid JSON."""
        agent = ReFrameAgent(name="TestAgent", instructions="Test instructions")

        # Mock malformed response
        mock_response = MagicMock()
        mock_response.text = "This is not JSON"
        agent.model.generate_content.return_value = mock_response

        result = await agent.run({"thought": "test"})
        assert result == "This is not JSON"


class TestReFrameAgentProcessWithTransparency:
    """Test agent process_with_transparency method."""

    @pytest.mark.asyncio
    async def test_process_returns_success_with_transparency_data(
        self, mock_settings, mock_genai, mock_model
    ):
        """Test process_with_transparency returns success response with transparency data."""
        agent = ReFrameAgent(name="TestAgent", instructions="Test instructions")

        # Mock successful response
        mock_response = MagicMock()
        mock_response.text = '{"result": "reframed thought"}'
        agent.model.generate_content.return_value = mock_response

        result = await agent.process_with_transparency({"thought": "negative thought"})

        assert result["success"] is True
        assert result["response"] == '{"result": "reframed thought"}'
        assert result["agent_name"] == "TestAgent"
        assert result["model_used"] == "gemini-1.5-flash"
        assert "reasoning_path" in result

    @pytest.mark.asyncio
    async def test_process_handles_errors_gracefully(self, mock_settings, mock_genai, mock_model):
        """Test process_with_transparency handles errors and returns error response."""
        agent = ReFrameAgent(name="TestAgent", instructions="Test instructions")

        # Mock error
        agent.model.generate_content.side_effect = Exception("API error")

        result = await agent.process_with_transparency({"thought": "test"})

        assert result["success"] is False
        assert result["error"] == "API error"
        assert result["agent_name"] == "TestAgent"

    @pytest.mark.asyncio
    async def test_process_handles_rate_limit_with_user_friendly_message(
        self, mock_settings, mock_genai, mock_model
    ):
        """Test process_with_transparency provides user-friendly message for rate limits."""
        agent = ReFrameAgent(name="TestAgent", instructions="Test instructions")

        # Mock rate limit error
        agent.model.generate_content.side_effect = google_exceptions.ResourceExhausted(
            "Rate limit exceeded"
        )

        result = await agent.process_with_transparency({"thought": "test"})

        assert result["success"] is False
        assert (
            "rate limit" in result["error"].lower()
            or "resource exhausted" in result["error"].lower()
        )
        assert result["agent_name"] == "TestAgent"


class TestReFrameAgentJSONParsing:
    """Test JSON parsing capabilities."""

    @pytest.mark.asyncio
    async def test_agent_parses_valid_json_response(self, mock_settings, mock_genai, mock_model):
        """Test agent can work with valid JSON responses."""
        agent = ReFrameAgent(name="TestAgent", instructions="Return JSON")

        # Mock valid JSON response
        mock_response = MagicMock()
        mock_response.text = '{"techniques": ["CBT", "DBT"], "reframed": "positive thought"}'
        agent.model.generate_content.return_value = mock_response

        result = await agent.run({"thought": "test"})

        # Verify we can parse the response
        parsed = json.loads(result)
        assert parsed["techniques"] == ["CBT", "DBT"]
        assert parsed["reframed"] == "positive thought"

    @pytest.mark.asyncio
    async def test_agent_handles_json_with_markdown_fence(
        self, mock_settings, mock_genai, mock_model
    ):
        """Test agent handles JSON wrapped in markdown code fence."""
        agent = ReFrameAgent(name="TestAgent", instructions="Return JSON")

        # Mock response with markdown fence
        mock_response = MagicMock()
        mock_response.text = """```json
{
  "result": "test",
  "success": true
}
```"""
        agent.model.generate_content.return_value = mock_response

        result = await agent.run({"thought": "test"})

        # For now, just verify we get the raw response
        # JSON extraction from markdown can be added later
        assert "```json" in result
        assert '"result": "test"' in result


class TestReFrameAgentReasoningPath:
    """Test reasoning path extraction."""

    def test_extract_reasoning_path_default_implementation(
        self, mock_settings, mock_genai, mock_model
    ):
        """Test default reasoning path extraction returns basic structure."""
        agent = ReFrameAgent(name="TestAgent", instructions="Test")

        response = '{"test": "response"}'
        reasoning_path = agent._extract_reasoning_path(response)

        assert reasoning_path["raw_response"] == response
        assert reasoning_path["steps"] == []


class TestReFrameAgentJSONParsingHelper:
    """Test JSON parsing helper method."""

    def test_parse_json_response_valid_json(self, mock_settings, mock_genai, mock_model):
        """Test parsing valid JSON response."""
        agent = ReFrameAgent(name="TestAgent", instructions="Test")

        response = '{"result": "success", "value": 42}'
        parsed = agent.parse_json_response(response)

        assert parsed["result"] == "success"
        assert parsed["value"] == 42

    def test_parse_json_response_with_markdown_fence(self, mock_settings, mock_genai, mock_model):
        """Test parsing JSON wrapped in markdown code fence."""
        agent = ReFrameAgent(name="TestAgent", instructions="Test")

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

    def test_parse_json_response_empty_response(self, mock_settings, mock_genai, mock_model):
        """Test parsing empty response raises appropriate error."""
        agent = ReFrameAgent(name="TestAgent", instructions="Test")

        with pytest.raises(json.JSONDecodeError) as exc_info:
            agent.parse_json_response("")

        assert "Empty response" in str(exc_info.value)

    def test_parse_json_response_invalid_json(self, mock_settings, mock_genai, mock_model):
        """Test parsing invalid JSON raises appropriate error."""
        agent = ReFrameAgent(name="TestAgent", instructions="Test")

        response = "This is not JSON at all"

        with pytest.raises(json.JSONDecodeError) as exc_info:
            agent.parse_json_response(response)

        assert "Unable to parse response as JSON" in str(exc_info.value)

    def test_parse_json_response_malformed_markdown(self, mock_settings, mock_genai, mock_model):
        """Test parsing malformed markdown-wrapped JSON."""
        agent = ReFrameAgent(name="TestAgent", instructions="Test")

        response = """```json
{
  "incomplete": "json",
```"""

        with pytest.raises(json.JSONDecodeError) as exc_info:
            agent.parse_json_response(response)

        assert "Unable to parse response as JSON" in str(exc_info.value)
