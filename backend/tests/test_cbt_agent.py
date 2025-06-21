"""Tests for CBT Framework Agent."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from agents.cbt_framework_agent import CBTFrameworkAgent


@pytest.fixture
def cbt_agent():
    """Create a CBT agent instance for testing."""
    with patch("agents.base.genai.configure"), patch("agents.base.GenerativeModel"):
        return CBTFrameworkAgent()


@pytest.fixture
def sample_intake_data():
    """Sample intake data for testing."""
    return {
        "original_thought": "Nobody wants to talk to me because I'm boring and worthless",
        "context": "At work, colleagues didn't invite me to lunch",
        "emotion_intensity": 8,
        "thought_categories": ["social", "self-worth"],
    }


@pytest.mark.asyncio
async def test_cbt_agent_initialization(cbt_agent):
    """Test CBT agent initializes with correct configuration."""
    assert cbt_agent.name == "CBTFrameworkAgent"
    assert "Cognitive Behavioral Therapy" in cbt_agent.instructions
    assert "AvPD" in cbt_agent.instructions


@pytest.mark.asyncio
async def test_cbt_agent_applies_techniques(cbt_agent, sample_intake_data):
    """Test CBT agent applies appropriate techniques to user thought."""
    # Mock the LLM response
    mock_response = {
        "original_thought": "Nobody wants to talk to me because I'm boring and worthless",
        "cognitive_distortions": ["mind reading", "labeling", "all-or-nothing thinking"],
        "techniques_applied": ["cognitive_restructuring", "evidence_examination"],
        "reframed_thoughts": [
            {
                "thought": "I don't know for certain why I wasn't invited. There could be many reasons unrelated to me.",
                "technique": "cognitive_restructuring",
                "explanation": "Challenges the assumption that you know others' thoughts and motivations",
            },
            {
                "thought": "Even if I feel boring sometimes, this doesn't define my entire worth as a person.",
                "technique": "evidence_examination",
                "explanation": "Separates a feeling from a global judgment about self-worth",
            },
        ],
        "gentle_challenges": [
            "What evidence do I have that colleagues think I'm boring?",
            "Have there been times when people seemed interested in talking with me?",
        ],
        "small_steps": [
            "Tomorrow, try greeting one colleague warmly",
            "Notice one positive interaction, however small",
        ],
        "transparency_notes": "Using gentle cognitive restructuring suitable for AvPD to challenge negative assumptions while validating feelings",
    }

    # Mock the run method
    cbt_agent.run = AsyncMock(return_value=json.dumps(mock_response))

    result = await cbt_agent.apply_cbt_techniques(sample_intake_data)

    assert result["success"] is True
    assert result["agent_name"] == "CBTFrameworkAgent"
    assert "response" in result
    assert "reasoning_path" in result


@pytest.mark.asyncio
async def test_cbt_agent_handles_errors_gracefully(cbt_agent, sample_intake_data):
    """Test CBT agent handles errors appropriately."""
    # Mock an error
    cbt_agent.run = AsyncMock(side_effect=Exception("API error"))

    result = await cbt_agent.apply_cbt_techniques(sample_intake_data)

    assert result["success"] is False
    assert "error" in result
    assert result["agent_name"] == "CBTFrameworkAgent"


def test_cbt_agent_avpd_specific_techniques(cbt_agent):
    """Test CBT agent provides AvPD-specific techniques."""
    techniques = cbt_agent.get_avpd_specific_techniques()

    assert isinstance(techniques, list)
    assert len(techniques) > 0
    assert any("gentle" in t.lower() for t in techniques)
    assert any("gradual" in t.lower() for t in techniques)
    assert any("compassion" in t.lower() for t in techniques)


@pytest.mark.asyncio
async def test_cbt_agent_transparency_extraction(cbt_agent):
    """Test CBT agent extracts reasoning path for transparency."""
    mock_response = "Test response"
    reasoning_path = cbt_agent._extract_reasoning_path(mock_response)

    assert "raw_response" in reasoning_path
    assert "steps" in reasoning_path
    assert len(reasoning_path["steps"]) > 0
    assert "Identified cognitive distortions" in reasoning_path["steps"]


@pytest.mark.asyncio
async def test_cbt_agent_formats_input_correctly(cbt_agent, sample_intake_data):
    """Test CBT agent formats input data correctly for processing."""
    # Mock the process_with_transparency method to check input
    processed_input = None

    async def capture_input(input_data):
        nonlocal processed_input
        processed_input = input_data
        return {"success": True, "response": {}}

    cbt_agent.process_with_transparency = capture_input

    await cbt_agent.apply_cbt_techniques(sample_intake_data)

    assert processed_input is not None
    assert "thought_data" in processed_input
    assert processed_input["focus"] == "AvPD-sensitive reframing"
    assert "techniques_priority" in processed_input
    assert "cognitive_restructuring" in processed_input["techniques_priority"]


@pytest.mark.asyncio
async def test_cbt_response_structure_validation(cbt_agent, sample_intake_data):
    """Test CBT agent response has required structure."""
    # Mock a complete response
    mock_response = {
        "original_thought": sample_intake_data["original_thought"],
        "cognitive_distortions": ["mind reading"],
        "techniques_applied": ["cognitive_restructuring"],
        "reframed_thoughts": [
            {
                "thought": "Reframed thought",
                "technique": "cognitive_restructuring",
                "explanation": "Why this helps",
            }
        ],
        "gentle_challenges": ["Challenge 1"],
        "small_steps": ["Step 1"],
        "transparency_notes": "Explanation",
    }

    cbt_agent.run = AsyncMock(return_value=json.dumps(mock_response))

    result = await cbt_agent.apply_cbt_techniques(sample_intake_data)

    assert result["success"] is True

    # Parse the response
    response_data = json.loads(result["response"])

    # Validate structure
    assert "original_thought" in response_data
    assert "cognitive_distortions" in response_data
    assert "techniques_applied" in response_data
    assert "reframed_thoughts" in response_data
    assert "gentle_challenges" in response_data
    assert "small_steps" in response_data
    assert "transparency_notes" in response_data

    # Validate reframed thoughts structure
    for reframed in response_data["reframed_thoughts"]:
        assert "thought" in reframed
        assert "technique" in reframed
        assert "explanation" in reframed
