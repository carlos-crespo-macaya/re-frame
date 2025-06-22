"""Tests for DBT Framework Agent."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from agents.dbt_framework_agent import DBTFrameworkAgent


@pytest.fixture
def dbt_agent():
    """Create a DBT agent instance for testing."""
    with patch("agents.base.genai.configure"), patch("agents.base.GenerativeModel"):
        return DBTFrameworkAgent()


@pytest.fixture
def sample_intake_data():
    """Sample intake data for testing DBT techniques."""
    return {
        "original_thought": "I can't handle this social situation, I need to leave now",
        "context": "At a work team meeting with 10 people",
        "emotion_intensity": 9,
        "thought_categories": ["social", "anxiety", "avoidance"],
    }


@pytest.fixture
def crisis_intake_data():
    """Sample crisis intake data for testing distress tolerance."""
    return {
        "original_thought": "Everyone hates me and I can't cope anymore",
        "context": "After perceived rejection from friend group",
        "emotion_intensity": 10,
        "thought_categories": ["social", "self-worth", "crisis"],
    }


@pytest.mark.asyncio
async def test_dbt_agent_initialization(dbt_agent):
    """Test DBT agent initializes with correct configuration."""
    assert dbt_agent.name == "DBTFrameworkAgent"
    assert "Dialectical Behavior Therapy" in dbt_agent.instructions
    assert "AvPD" in dbt_agent.instructions
    assert "acceptance AND change" in dbt_agent.instructions


@pytest.mark.asyncio
async def test_dbt_agent_applies_distress_tolerance(dbt_agent, sample_intake_data):
    """Test DBT agent applies distress tolerance techniques for high anxiety."""
    # Mock the LLM response
    mock_response = {
        "module_used": "Distress Tolerance",
        "technique": "TIPP",
        "acceptance_statement": "This anxiety in social situations is real and valid, especially with AvPD.",
        "change_strategy": "Let's use TIPP to help you cope: Try paced breathing - in for 4, hold for 4, out for 6.",
        "wise_mind_reframe": "I can feel overwhelmed AND use skills to get through this moment.",
        "skill_practice": "Set a timer for 10 minutes. Use paced breathing. Then reassess if you need to leave.",
        "dialectical_synthesis": "This is hard AND I have tools to help me cope.",
    }

    # Mock the run method
    dbt_agent.run = AsyncMock(return_value=json.dumps(mock_response))

    result = await dbt_agent.apply_dbt_techniques(sample_intake_data)

    assert result["success"] is True
    assert result["agent_name"] == "DBTFrameworkAgent"
    assert "response" in result

    response_data = json.loads(result["response"])
    assert response_data["module_used"] == "Distress Tolerance"
    assert response_data["technique"] == "TIPP"


@pytest.mark.asyncio
async def test_dbt_agent_applies_emotion_regulation(dbt_agent):
    """Test DBT agent applies emotion regulation for moderate distress."""
    intake_data = {
        "original_thought": "My coworker ignored my suggestion, they must think I'm stupid",
        "context": "During team brainstorming session",
        "emotion_intensity": 6,
        "thought_categories": ["social", "self-worth", "work"],
    }

    mock_response = {
        "module_used": "Emotion Regulation",
        "technique": "Check the Facts",
        "acceptance_statement": "It's painful when we feel ignored or dismissed.",
        "change_strategy": "Let's check the facts: Were they focused on something else? Have they ignored all your suggestions?",
        "wise_mind_reframe": "I felt ignored AND there might be other explanations for their behavior.",
        "skill_practice": "List 3 alternative explanations for why they didn't respond to your suggestion.",
        "dialectical_synthesis": "My feelings are valid AND the situation might not be what it seems.",
    }

    dbt_agent.run = AsyncMock(return_value=json.dumps(mock_response))

    result = await dbt_agent.apply_dbt_techniques(intake_data)

    response_data = json.loads(result["response"])
    assert response_data["module_used"] == "Emotion Regulation"
    assert response_data["technique"] == "Check the Facts"


@pytest.mark.asyncio
async def test_dbt_agent_applies_interpersonal_effectiveness(dbt_agent):
    """Test DBT agent applies interpersonal effectiveness for relationship issues."""
    intake_data = {
        "original_thought": "I can't ask for help because they'll think I'm needy and reject me",
        "context": "Need to ask colleague for assistance with project",
        "emotion_intensity": 7,
        "thought_categories": ["social", "help-seeking", "fear"],
    }

    mock_response = {
        "module_used": "Interpersonal Effectiveness",
        "technique": "DEARMAN",
        "acceptance_statement": "Asking for help feels vulnerable when you fear rejection.",
        "change_strategy": "Let's use DEARMAN: Describe what you need help with objectively, Express why it matters, Assert your request clearly.",
        "wise_mind_reframe": "Needing help is human AND I can ask for it skillfully.",
        "skill_practice": "Write out your request using DEARMAN format before the conversation.",
        "dialectical_synthesis": "I fear being seen as needy AND asking for help appropriately is professional.",
    }

    dbt_agent.run = AsyncMock(return_value=json.dumps(mock_response))

    result = await dbt_agent.apply_dbt_techniques(intake_data)

    response_data = json.loads(result["response"])
    assert response_data["module_used"] == "Interpersonal Effectiveness"
    assert response_data["technique"] == "DEARMAN"


@pytest.mark.asyncio
async def test_dbt_agent_applies_mindfulness(dbt_agent):
    """Test DBT agent applies mindfulness for rumination."""
    intake_data = {
        "original_thought": "I keep replaying that awkward conversation from yesterday",
        "context": "Ruminating about brief interaction with neighbor",
        "emotion_intensity": 5,
        "thought_categories": ["social", "rumination", "past"],
    }

    mock_response = {
        "module_used": "Mindfulness",
        "technique": "Wise Mind",
        "acceptance_statement": "It's natural to replay social interactions when we have social anxiety.",
        "change_strategy": "Let's find your Wise Mind: What would you tell a friend who was ruminating like this?",
        "wise_mind_reframe": "The conversation happened AND dwelling on it won't change the past.",
        "skill_practice": "When you notice rumination, describe 5 things you can see right now to return to the present.",
        "dialectical_synthesis": "I can acknowledge the discomfort from yesterday AND choose to focus on today.",
    }

    dbt_agent.run = AsyncMock(return_value=json.dumps(mock_response))

    result = await dbt_agent.apply_dbt_techniques(intake_data)

    response_data = json.loads(result["response"])
    assert response_data["module_used"] == "Mindfulness"
    assert response_data["technique"] == "Wise Mind"


@pytest.mark.asyncio
async def test_dbt_agent_handles_crisis_appropriately(dbt_agent, crisis_intake_data):
    """Test DBT agent prioritizes safety in crisis situations."""
    mock_response = {
        "module_used": "Distress Tolerance",
        "technique": "TIPP",
        "acceptance_statement": "You're in extreme distress right now, and that's incredibly difficult.",
        "change_strategy": "First priority is getting through this moment safely. Try the T in TIPP: splash cold water on your face or hold ice.",
        "wise_mind_reframe": "This pain is intense AND it will not last forever.",
        "skill_practice": "Focus only on the next hour. Use TIPP, then ACCEPTS if needed.",
        "dialectical_synthesis": "This moment feels unbearable AND you have survived difficult moments before.",
        "crisis_resources": "If these feelings persist, please reach out to a crisis helpline or trusted person.",
    }

    dbt_agent.run = AsyncMock(return_value=json.dumps(mock_response))

    result = await dbt_agent.apply_dbt_techniques(crisis_intake_data)

    response_data = json.loads(result["response"])
    assert response_data["module_used"] == "Distress Tolerance"
    assert "crisis_resources" in response_data
    assert "TIPP" in response_data["technique"]


@pytest.mark.asyncio
async def test_dbt_agent_uses_dialectical_language(dbt_agent, sample_intake_data):
    """Test DBT agent consistently uses 'AND' instead of 'BUT'."""
    mock_response = {
        "module_used": "Distress Tolerance",
        "technique": "ACCEPTS",
        "acceptance_statement": "Social situations are genuinely challenging for you.",
        "change_strategy": "You feel overwhelmed AND you can try the A in ACCEPTS - engage in an Activity.",
        "wise_mind_reframe": "This is difficult AND I'm learning to cope differently.",
        "skill_practice": "I'm anxious AND I'm choosing to stay for 5 more minutes.",
        "dialectical_synthesis": "I want to leave AND I want to challenge my avoidance.",
    }

    dbt_agent.run = AsyncMock(return_value=json.dumps(mock_response))

    result = await dbt_agent.apply_dbt_techniques(sample_intake_data)

    response_text = json.dumps(json.loads(result["response"]))
    # Ensure no "but" statements in therapeutic content
    assert " but " not in response_text.lower() or "but" not in response_text.split()
    # Ensure proper use of "AND"
    assert " AND " in response_text


def test_dbt_agent_avpd_specific_techniques(dbt_agent):
    """Test DBT agent provides AvPD-specific DBT techniques."""
    techniques = dbt_agent.get_avpd_specific_dbt_techniques()

    assert isinstance(techniques, list)
    assert len(techniques) > 0

    # Check for key DBT modules
    technique_str = " ".join(techniques).lower()
    assert any(term in technique_str for term in ["distress tolerance", "tipp", "accepts"])
    assert any(
        term in technique_str for term in ["emotion regulation", "please", "check the facts"]
    )
    assert any(term in technique_str for term in ["interpersonal", "dearman", "give", "fast"])
    assert any(term in technique_str for term in ["mindfulness", "wise mind"])


@pytest.mark.asyncio
async def test_dbt_agent_module_selection(dbt_agent):
    """Test DBT agent selects appropriate module based on situation."""
    test_cases = [
        {
            "thought": "I'm panicking and need to escape",
            "emotion_intensity": 9,
            "expected_module": "Distress Tolerance",
        },
        {
            "thought": "Why do I always feel so angry after social events?",
            "emotion_intensity": 6,
            "expected_module": "Emotion Regulation",
        },
        {
            "thought": "I need to set boundaries but don't know how",
            "emotion_intensity": 5,
            "expected_module": "Interpersonal Effectiveness",
        },
        {
            "thought": "I can't stop thinking about what happened",
            "emotion_intensity": 4,
            "expected_module": "Mindfulness",
        },
    ]

    for test_case in test_cases:
        intake_data = {
            "original_thought": test_case["thought"],
            "emotion_intensity": test_case["emotion_intensity"],
            "thought_categories": ["test"],
        }

        result = dbt_agent.select_dbt_module(intake_data)
        assert result == test_case["expected_module"]


@pytest.mark.asyncio
async def test_dbt_response_structure_validation(dbt_agent, sample_intake_data):
    """Test DBT agent response has required structure."""
    mock_response = {
        "module_used": "Distress Tolerance",
        "technique": "TIPP",
        "acceptance_statement": "Your anxiety is valid",
        "change_strategy": "Let's try TIPP",
        "wise_mind_reframe": "I'm anxious AND I can cope",
        "skill_practice": "Practice paced breathing",
        "dialectical_synthesis": "This is hard AND I have skills",
    }

    dbt_agent.run = AsyncMock(return_value=json.dumps(mock_response))

    result = await dbt_agent.apply_dbt_techniques(sample_intake_data)

    assert result["success"] is True
    response_data = json.loads(result["response"])

    # Validate all required fields are present
    required_fields = [
        "module_used",
        "technique",
        "acceptance_statement",
        "change_strategy",
        "wise_mind_reframe",
        "skill_practice",
        "dialectical_synthesis",
    ]

    for field in required_fields:
        assert field in response_data, f"Missing required field: {field}"


@pytest.mark.asyncio
async def test_dbt_agent_handles_errors_gracefully(dbt_agent, sample_intake_data):
    """Test DBT agent handles errors appropriately."""
    dbt_agent.run = AsyncMock(side_effect=Exception("API error"))

    result = await dbt_agent.apply_dbt_techniques(sample_intake_data)

    assert result["success"] is False
    assert "error" in result
    assert result["agent_name"] == "DBTFrameworkAgent"
