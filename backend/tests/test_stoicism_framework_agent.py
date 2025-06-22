"""Tests for Stoicism Framework Agent."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from agents.stoicism_framework_agent import StoicismFrameworkAgent


@pytest.fixture
def stoicism_agent():
    """Create a Stoicism agent instance for testing."""
    with patch("agents.base.genai.configure"), patch("agents.base.GenerativeModel"):
        return StoicismFrameworkAgent()


@pytest.fixture
def sample_intake_data():
    """Sample intake data for testing Stoic techniques."""
    return {
        "original_thought": "My friend hasn't texted back in 3 days. They must hate me now.",
        "context": "Sent friendly check-in message",
        "emotion_intensity": 6,
        "thought_categories": ["social", "rejection", "worry"],
    }


@pytest.fixture
def control_intake_data():
    """Sample data for testing dichotomy of control."""
    return {
        "original_thought": "I need everyone at the party to like me or I'm a failure",
        "context": "Upcoming work social event",
        "emotion_intensity": 8,
        "thought_categories": ["social", "control", "validation"],
    }


@pytest.mark.asyncio
async def test_stoicism_agent_initialization(stoicism_agent):
    """Test Stoicism agent initializes with correct configuration."""
    assert stoicism_agent.name == "StoicismFrameworkAgent"
    assert "Stoic philosophy" in stoicism_agent.instructions
    assert "AvPD" in stoicism_agent.instructions
    assert "dichotomy of control" in stoicism_agent.instructions.lower()
    assert "virtue" in stoicism_agent.instructions.lower()


@pytest.mark.asyncio
async def test_stoicism_agent_applies_dichotomy_of_control(stoicism_agent, control_intake_data):
    """Test Stoicism agent applies dichotomy of control principle."""
    mock_response = {
        "principle_applied": "Dichotomy of Control",
        "control_analysis": {
            "in_control": [
                "Your behavior and kindness",
                "Your effort to be pleasant",
                "Your responses to others",
            ],
            "not_in_control": [
                "Others' opinions of you",
                "Whether people like you",
                "How others choose to respond",
            ],
        },
        "stoic_reframe": "Focus on being the kind of person you respect, not on being liked. You control your character, not others' judgments.",
        "wisdom_quote": "Epictetus: 'You have power over your mind—not outside events. Realize this, and you will find strength.'",
        "virtuous_action": "Attend with the intention to be kind and genuine. Success is in your conduct, not their approval.",
        "practical_exercise": "Before the party, write three qualities you'll embody (e.g., kindness, authenticity, courage).",
        "perspective_shift": "A Stoic succeeds by acting virtuously, regardless of external validation.",
    }

    stoicism_agent.run = AsyncMock(return_value=json.dumps(mock_response))

    result = await stoicism_agent.apply_stoic_principles(control_intake_data)

    assert result["success"] is True
    assert result["agent_name"] == "StoicismFrameworkAgent"

    response_data = json.loads(result["response"])
    assert response_data["principle_applied"] == "Dichotomy of Control"
    assert "in_control" in response_data["control_analysis"]
    assert "not_in_control" in response_data["control_analysis"]


@pytest.mark.asyncio
async def test_stoicism_agent_applies_virtue_ethics(stoicism_agent, sample_intake_data):
    """Test Stoicism agent applies virtue ethics for character focus."""
    mock_response = {
        "principle_applied": "Virtue Ethics",
        "control_analysis": {
            "in_control": ["Your friendly intention", "Your choice to reach out"],
            "not_in_control": ["Their response time", "Their feelings"],
        },
        "stoic_reframe": "You acted with the virtue of friendship by reaching out. Their response timing reflects their life, not your worth.",
        "wisdom_quote": "Marcus Aurelius: 'What brings no benefit to the hive brings none to the bee.'",
        "virtuous_action": "You've demonstrated courage (reaching out) and friendship (caring). This is success regardless of response.",
        "practical_exercise": "Identify which virtue you practiced: Courage? Kindness? Justice? Wisdom?",
        "perspective_shift": "A friend who reaches out with care has already succeeded in friendship.",
    }

    stoicism_agent.run = AsyncMock(return_value=json.dumps(mock_response))

    result = await stoicism_agent.apply_stoic_principles(sample_intake_data)

    response_data = json.loads(result["response"])
    assert response_data["principle_applied"] == "Virtue Ethics"
    assert "virtue" in response_data["stoic_reframe"].lower()


@pytest.mark.asyncio
async def test_stoicism_agent_applies_negative_visualization(stoicism_agent):
    """Test Stoicism agent applies premeditatio malorum appropriately."""
    intake_data = {
        "original_thought": "I can't give this presentation, what if I completely fail?",
        "context": "Important work presentation tomorrow",
        "emotion_intensity": 9,
        "thought_categories": ["anxiety", "future", "catastrophizing"],
    }

    mock_response = {
        "principle_applied": "Negative Visualization",
        "control_analysis": {
            "in_control": ["Your preparation", "Your effort", "Your composure"],
            "not_in_control": ["Technical difficulties", "Audience reactions", "Perfect delivery"],
        },
        "stoic_reframe": "Even if things go poorly, you'll have shown courage by trying. The attempt itself is virtuous.",
        "wisdom_quote": "Seneca: 'Every new thing excites the mind, but a mind that seeks truth turns from the new to the old.'",
        "virtuous_action": "Prepare well, then accept any outcome with equanimity. Your character is shown in the attempt.",
        "practical_exercise": "Visualize it going poorly, then ask: 'Will I have acted with integrity?' If yes, you've succeeded.",
        "perspective_shift": "A Stoic measures success by effort and virtue, not by smooth performance.",
    }

    stoicism_agent.run = AsyncMock(return_value=json.dumps(mock_response))

    result = await stoicism_agent.apply_stoic_principles(intake_data)

    response_data = json.loads(result["response"])
    assert response_data["principle_applied"] == "Negative Visualization"
    assert "courage" in response_data["stoic_reframe"].lower()


@pytest.mark.asyncio
async def test_stoicism_agent_applies_cosmic_perspective(stoicism_agent):
    """Test Stoicism agent applies view from above for perspective."""
    intake_data = {
        "original_thought": "I said something stupid in the meeting and now everyone thinks I'm an idiot",
        "context": "Made awkward comment during team meeting",
        "emotion_intensity": 7,
        "thought_categories": ["embarrassment", "rumination", "social"],
    }

    mock_response = {
        "principle_applied": "View from Above",
        "control_analysis": {
            "in_control": ["How you handle this now", "Learning from the experience"],
            "not_in_control": ["What was already said", "Others' thoughts"],
        },
        "stoic_reframe": "In the vast scope of time, this moment is a tiny ripple. Your character matters more than one awkward comment.",
        "wisdom_quote": "Marcus Aurelius: 'Remember that in a little while you and everyone you know will be dead.'",
        "virtuous_action": "Show wisdom by learning, courage by moving forward, and temperance by not dwelling.",
        "practical_exercise": "Imagine viewing this from space. How significant does this meeting seem from that height?",
        "perspective_shift": "In a year, this will likely be forgotten. Your response to it reveals your character.",
    }

    stoicism_agent.run = AsyncMock(return_value=json.dumps(mock_response))

    result = await stoicism_agent.apply_stoic_principles(intake_data)

    response_data = json.loads(result["response"])
    assert response_data["principle_applied"] == "View from Above"
    assert any(
        word in response_data["perspective_shift"].lower() for word in ["year", "time", "forgotten"]
    )


@pytest.mark.asyncio
async def test_stoicism_agent_applies_amor_fati(stoicism_agent):
    """Test Stoicism agent applies amor fati for acceptance."""
    intake_data = {
        "original_thought": "They rejected my invitation. I'm always the one being rejected.",
        "context": "Asked someone to coffee, they declined",
        "emotion_intensity": 8,
        "thought_categories": ["rejection", "pattern", "social"],
    }

    mock_response = {
        "principle_applied": "Amor Fati",
        "control_analysis": {
            "in_control": ["Your courage to ask", "How you respond to rejection"],
            "not_in_control": ["Their decision", "Their reasons"],
        },
        "stoic_reframe": "This rejection is part of your path to becoming more resilient. Embrace it as a teacher, not an enemy.",
        "wisdom_quote": "Nietzsche: 'My formula for greatness is amor fati: not merely to endure but to love what is necessary.'",
        "virtuous_action": "You showed courage by asking. Now show wisdom by learning and temperance by accepting gracefully.",
        "practical_exercise": "Write: 'This rejection is making me stronger and wiser.' Find one way this is true.",
        "perspective_shift": "Each rejection builds your resilience muscle. A Stoic sees obstacles as training.",
    }

    stoicism_agent.run = AsyncMock(return_value=json.dumps(mock_response))

    result = await stoicism_agent.apply_stoic_principles(intake_data)

    response_data = json.loads(result["response"])
    assert response_data["principle_applied"] == "Amor Fati"
    assert (
        "teacher" in response_data["stoic_reframe"]
        or "training" in response_data["perspective_shift"]
    )


@pytest.mark.asyncio
async def test_stoicism_agent_applies_present_moment(stoicism_agent):
    """Test Stoicism agent applies present moment focus."""
    intake_data = {
        "original_thought": "I'm still cringing about what I said at last year's holiday party",
        "context": "Random memory of past embarrassment",
        "emotion_intensity": 5,
        "thought_categories": ["past", "rumination", "embarrassment"],
    }

    mock_response = {
        "principle_applied": "Present Moment Focus",
        "control_analysis": {
            "in_control": ["Your actions right now", "What you do today"],
            "not_in_control": ["The past", "Others' memories"],
        },
        "stoic_reframe": "The past exists only in your mind now. Your power lies in this present moment, not in unchangeable history.",
        "wisdom_quote": "Marcus Aurelius: 'Confine yourself to the present.'",
        "virtuous_action": "Show wisdom by focusing on today's opportunities for virtue, not yesterday's embarrassments.",
        "practical_exercise": "When the memory arises, say: 'That was then, this is now. What virtuous action can I take now?'",
        "perspective_shift": "You can't change the past, but you can choose virtue in this moment.",
    }

    stoicism_agent.run = AsyncMock(return_value=json.dumps(mock_response))

    result = await stoicism_agent.apply_stoic_principles(intake_data)

    response_data = json.loads(result["response"])
    assert response_data["principle_applied"] == "Present Moment Focus"
    assert (
        "present" in response_data["stoic_reframe"].lower()
        or "now" in response_data["stoic_reframe"].lower()
    )


def test_stoicism_agent_avpd_specific_techniques(stoicism_agent):
    """Test Stoicism agent provides AvPD-specific Stoic techniques."""
    techniques = stoicism_agent.get_avpd_specific_stoic_techniques()

    assert isinstance(techniques, list)
    assert len(techniques) > 0

    # Check for key Stoic concepts
    technique_str = " ".join(techniques).lower()
    assert any(term in technique_str for term in ["control", "dichotomy", "controllable"])
    assert any(term in technique_str for term in ["virtue", "character", "courage"])
    assert any(term in technique_str for term in ["perspective", "cosmic", "view from above"])
    assert any(term in technique_str for term in ["amor fati", "accept", "embrace"])
    assert any(term in technique_str for term in ["present", "moment", "now"])


@pytest.mark.asyncio
async def test_stoicism_agent_principle_selection(stoicism_agent):
    """Test Stoicism agent selects appropriate principle based on situation."""
    test_cases = [
        {
            "thought": "I need everyone to like me",
            "categories": ["control", "validation"],
            "expected_principle": "Dichotomy of Control",
        },
        {
            "thought": "What if I fail tomorrow?",
            "categories": ["future", "anxiety"],
            "expected_principle": "Negative Visualization",
        },
        {
            "thought": "This minor mistake is ruining my life",
            "categories": ["catastrophizing", "perspective"],
            "expected_principle": "View from Above",
        },
        {
            "thought": "I'm still upset about last year",
            "categories": ["past", "rumination"],
            "expected_principle": "Present Moment Focus",
        },
        {
            "thought": "Why does this always happen to me?",
            "categories": ["pattern", "victimhood"],
            "expected_principle": "Amor Fati",
        },
    ]

    for test_case in test_cases:
        result = stoicism_agent.select_stoic_principle(
            test_case["thought"], test_case["categories"]
        )
        assert result == test_case["expected_principle"]


@pytest.mark.asyncio
async def test_stoicism_response_structure_validation(stoicism_agent, sample_intake_data):
    """Test Stoicism agent response has required structure."""
    mock_response = {
        "principle_applied": "Dichotomy of Control",
        "control_analysis": {
            "in_control": ["Your actions"],
            "not_in_control": ["Others' actions"],
        },
        "stoic_reframe": "Focus on what you control",
        "wisdom_quote": "A quote from Marcus Aurelius",
        "virtuous_action": "Act with virtue",
        "practical_exercise": "Practice this exercise",
        "perspective_shift": "See it differently",
    }

    stoicism_agent.run = AsyncMock(return_value=json.dumps(mock_response))

    result = await stoicism_agent.apply_stoic_principles(sample_intake_data)

    assert result["success"] is True
    response_data = json.loads(result["response"])

    # Validate all required fields are present
    required_fields = [
        "principle_applied",
        "control_analysis",
        "stoic_reframe",
        "wisdom_quote",
        "virtuous_action",
        "practical_exercise",
        "perspective_shift",
    ]

    for field in required_fields:
        assert field in response_data, f"Missing required field: {field}"

    # Validate control_analysis structure
    assert "in_control" in response_data["control_analysis"]
    assert "not_in_control" in response_data["control_analysis"]


@pytest.mark.asyncio
async def test_stoicism_agent_handles_errors_gracefully(stoicism_agent, sample_intake_data):
    """Test Stoicism agent handles errors appropriately."""
    stoicism_agent.run = AsyncMock(side_effect=Exception("API error"))

    result = await stoicism_agent.apply_stoic_principles(sample_intake_data)

    assert result["success"] is False
    assert "error" in result
    assert result["agent_name"] == "StoicismFrameworkAgent"


@pytest.mark.asyncio
async def test_stoicism_agent_emphasizes_virtue_over_outcomes(stoicism_agent, sample_intake_data):
    """Test Stoicism agent emphasizes virtue/character over external outcomes."""
    mock_response = {
        "principle_applied": "Virtue Ethics",
        "control_analysis": {
            "in_control": ["Your character", "Your choices"],
            "not_in_control": ["Others' responses", "Outcomes"],
        },
        "stoic_reframe": "Success lies in acting virtuously, not in receiving the response you want.",
        "wisdom_quote": "Epictetus: 'Wealth consists not in having great possessions, but in having few wants.'",
        "virtuous_action": "You showed care by reaching out. This virtuous act is complete regardless of response.",
        "practical_exercise": "List the virtues you demonstrated (courage, friendship, care) - these are your true achievements.",
        "perspective_shift": "A Stoic measures worth by character, not by external validation.",
    }

    stoicism_agent.run = AsyncMock(return_value=json.dumps(mock_response))

    result = await stoicism_agent.apply_stoic_principles(sample_intake_data)

    response_data = json.loads(result["response"])
    response_text = json.dumps(response_data).lower()

    # Check emphasis on virtue over outcomes
    assert "virtue" in response_text or "character" in response_text
    assert "regardless" in response_text or "not in" in response_text
    assert "external" not in response_data.get("virtuous_action", "").lower()  # Virtue is internal
