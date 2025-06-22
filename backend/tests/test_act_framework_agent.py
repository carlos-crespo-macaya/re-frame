"""Tests for ACT Framework Agent."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from agents.act_framework_agent import ACTFrameworkAgent


@pytest.fixture
def act_agent():
    """Create an ACT agent instance for testing."""
    with patch("agents.base.genai.configure"), patch("agents.base.GenerativeModel"):
        return ACTFrameworkAgent()


@pytest.fixture
def sample_intake_data():
    """Sample intake data for testing ACT techniques."""
    return {
        "original_thought": "I want to join the book club but I'll just embarrass myself",
        "context": "Saw book club invitation at work",
        "emotion_intensity": 7,
        "thought_categories": ["social", "fear", "avoidance"],
        "values_hint": "intellectual connection",
    }


@pytest.fixture
def anxiety_fusion_data():
    """Sample data for testing thought fusion."""
    return {
        "original_thought": "I am socially broken and always will be",
        "context": "After awkward conversation with neighbor",
        "emotion_intensity": 8,
        "thought_categories": ["social", "self-concept", "fusion"],
    }


@pytest.mark.asyncio
async def test_act_agent_initialization(act_agent):
    """Test ACT agent initializes with correct configuration."""
    assert act_agent.name == "ACTFrameworkAgent"
    assert "Acceptance and Commitment Therapy" in act_agent.instructions
    assert "AvPD" in act_agent.instructions
    assert "psychological flexibility" in act_agent.instructions


@pytest.mark.asyncio
async def test_act_agent_applies_defusion(act_agent, anxiety_fusion_data):
    """Test ACT agent applies cognitive defusion techniques."""
    mock_response = {
        "act_process": "Cognitive Defusion",
        "defusion": "You're having the thought 'I am socially broken'. Notice it's a thought, not a fact.",
        "values_exploration": "Despite this painful thought, what matters to you about connecting with others?",
        "acceptance": "It's painful to have thoughts like this. They're just thoughts visiting, not permanent residents.",
        "metaphor": "Your thoughts are like pop-up ads - annoying but you don't have to click on them.",
        "workable_action": "Try saying 'I'm having the thought that I'm socially broken' and notice the difference.",
        "willingness_question": "Are you willing to have this thought while still doing something you care about?",
        "observer_self": "Notice the you that observes these thoughts has been there through many different thoughts.",
    }

    act_agent.run = AsyncMock(return_value=json.dumps(mock_response))

    result = await act_agent.apply_act_techniques(anxiety_fusion_data)

    assert result["success"] is True
    assert result["agent_name"] == "ACTFrameworkAgent"

    response_data = json.loads(result["response"])
    assert response_data["act_process"] == "Cognitive Defusion"
    assert "thought" in response_data["defusion"].lower()
    assert "not a fact" in response_data["defusion"]


@pytest.mark.asyncio
async def test_act_agent_applies_values_and_action(act_agent, sample_intake_data):
    """Test ACT agent connects to values and suggests committed action."""
    mock_response = {
        "act_process": "Values + Committed Action",
        "defusion": "Notice 'I'll embarrass myself' is your mind's prediction, not a fact.",
        "values_exploration": "It sounds like intellectual connection and sharing ideas matters to you.",
        "acceptance": "It's completely normal to feel fear when approaching something meaningful.",
        "metaphor": "Like a sailor navigating by stars (values) rather than avoiding storms (anxiety).",
        "workable_action": "What if you attended just the first 15 minutes? You can bring your anxiety along.",
        "willingness_question": "How willing are you to feel awkward for 15 minutes if it means moving toward connection?",
        "observer_self": "Notice: the 'you' that wants connection has been there through all the anxious thoughts.",
    }

    act_agent.run = AsyncMock(return_value=json.dumps(mock_response))

    result = await act_agent.apply_act_techniques(sample_intake_data)

    response_data = json.loads(result["response"])
    assert response_data["act_process"] == "Values + Committed Action"
    assert "intellectual connection" in response_data["values_exploration"]
    assert "15 minutes" in response_data["workable_action"]


@pytest.mark.asyncio
async def test_act_agent_applies_acceptance(act_agent):
    """Test ACT agent applies acceptance for overwhelming emotions."""
    intake_data = {
        "original_thought": "I can't handle this anxiety, it's too much",
        "context": "Before important presentation",
        "emotion_intensity": 9,
        "thought_categories": ["anxiety", "avoidance", "overwhelm"],
    }

    mock_response = {
        "act_process": "Acceptance",
        "defusion": "Your mind is telling you a story about what you can and can't handle.",
        "values_exploration": "What does this presentation mean to you? What are you moving toward?",
        "acceptance": "Anxiety is here in full force. Can you breathe and make space for it, like opening windows in a stuffy room?",
        "metaphor": "Anxiety is like a wave - you can't stop it, but you can learn to surf with it.",
        "workable_action": "Place your hand on your chest, breathe into the anxiety, and take one small step forward.",
        "willingness_question": "Are you willing to have anxiety present while you do what matters?",
        "observer_self": "You are the ocean, not the waves. The anxious waves will pass.",
    }

    act_agent.run = AsyncMock(return_value=json.dumps(mock_response))

    result = await act_agent.apply_act_techniques(intake_data)

    response_data = json.loads(result["response"])
    assert response_data["act_process"] == "Acceptance"
    assert "make space" in response_data["acceptance"]
    assert "wave" in response_data["metaphor"]


@pytest.mark.asyncio
async def test_act_agent_applies_present_moment(act_agent):
    """Test ACT agent applies present moment awareness for future worries."""
    intake_data = {
        "original_thought": "What if everyone judges me at the party next week",
        "context": "Thinking about upcoming social event",
        "emotion_intensity": 6,
        "thought_categories": ["social", "future", "worry"],
    }

    mock_response = {
        "act_process": "Contact with Present Moment",
        "defusion": "Your mind is time traveling to next week's party. That's what minds do.",
        "values_exploration": "What about social connection is important enough that you're considering going?",
        "acceptance": "Worry about the future is natural. It shows you care about how things go.",
        "metaphor": "Your mind is like a time machine stuck in 'future worry' mode. You can gently return to now.",
        "workable_action": "Try the 5-4-3-2-1 grounding: Notice 5 things you see right now, 4 you hear...",
        "willingness_question": "Can you be willing to plan for the party without living there in your mind?",
        "observer_self": "The you sitting here now is not at the party. That future hasn't happened yet.",
    }

    act_agent.run = AsyncMock(return_value=json.dumps(mock_response))

    result = await act_agent.apply_act_techniques(intake_data)

    response_data = json.loads(result["response"])
    assert response_data["act_process"] == "Contact with Present Moment"
    assert "5-4-3-2-1" in response_data["workable_action"]


@pytest.mark.asyncio
async def test_act_agent_applies_self_as_context(act_agent):
    """Test ACT agent helps distinguish self from experiences."""
    intake_data = {
        "original_thought": "I am my anxiety, it defines everything about me",
        "context": "Reflecting on life with social anxiety",
        "emotion_intensity": 7,
        "thought_categories": ["identity", "fusion", "self-concept"],
    }

    mock_response = {
        "act_process": "Self-as-Context",
        "defusion": "Notice how you said 'I am anxiety' versus 'I have anxiety' - there's a difference.",
        "values_exploration": "Who are you beyond the anxiety? What has remained constant about you?",
        "acceptance": "Anxiety has been a frequent visitor in your life. That doesn't make it your identity.",
        "metaphor": "You are the sky - vast, unchanging. Anxiety is just weather passing through.",
        "workable_action": "List three things about yourself that have nothing to do with anxiety.",
        "willingness_question": "Are you willing to explore who you are beyond this anxious story?",
        "observer_self": "The you that notices anxiety is not anxious. That observer has always been there.",
    }

    act_agent.run = AsyncMock(return_value=json.dumps(mock_response))

    result = await act_agent.apply_act_techniques(intake_data)

    response_data = json.loads(result["response"])
    assert response_data["act_process"] == "Self-as-Context"
    assert "sky" in response_data["metaphor"]
    assert "observer" in response_data["observer_self"]


def test_act_agent_avpd_specific_techniques(act_agent):
    """Test ACT agent provides AvPD-specific techniques."""
    techniques = act_agent.get_avpd_specific_act_techniques()

    assert isinstance(techniques, list)
    assert len(techniques) > 0

    # Check for key ACT processes
    technique_str = " ".join(techniques).lower()
    assert any(term in technique_str for term in ["defusion", "thoughts", "i'm having the thought"])
    assert any(term in technique_str for term in ["values", "matters", "meaningful"])
    assert any(term in technique_str for term in ["acceptance", "willing", "make room"])
    assert any(term in technique_str for term in ["present", "moment", "grounding"])
    assert any(term in technique_str for term in ["observer", "self-as-context", "sky"])
    assert any(term in technique_str for term in ["committed action", "small step", "willing to"])


@pytest.mark.asyncio
async def test_act_agent_hexaflex_selection(act_agent):
    """Test ACT agent selects appropriate Hexaflex process based on situation."""
    test_cases = [
        {
            "thought": "I'll die of embarrassment if I speak up",
            "categories": ["catastrophizing", "fusion"],
            "expected_process": "Cognitive Defusion",
        },
        {
            "thought": "I can't stand feeling this anxious",
            "categories": ["avoidance", "struggle"],
            "expected_process": "Acceptance",
        },
        {
            "thought": "What's the point if I'll always be anxious?",
            "categories": ["values", "meaning"],
            "expected_process": "Values Clarification",
        },
        {
            "thought": "I'm lost in worries about tomorrow's meeting",
            "categories": ["future", "worry"],
            "expected_process": "Present Moment",
        },
        {
            "thought": "I am broken",
            "categories": ["identity", "self-concept"],
            "expected_process": "Self-as-Context",
        },
    ]

    for test_case in test_cases:
        result = act_agent.select_hexaflex_process(test_case["thought"], test_case["categories"])
        assert result == test_case["expected_process"]


@pytest.mark.asyncio
async def test_act_agent_provides_workable_actions(act_agent, sample_intake_data):
    """Test ACT agent provides small, workable actions."""
    mock_response = {
        "act_process": "Values + Committed Action",
        "defusion": "Notice the prediction machine in your head.",
        "values_exploration": "Connection through shared interests matters to you.",
        "acceptance": "Fear is a normal passenger when we move toward what matters.",
        "metaphor": "Values are like a compass - they show direction, not destination.",
        "workable_action": "Could you read one paragraph at the next meeting? Or just introduce yourself?",
        "willingness_question": "What level of discomfort are you willing to experience for connection?",
        "observer_self": "The you that values connection exists regardless of anxious thoughts.",
    }

    act_agent.run = AsyncMock(return_value=json.dumps(mock_response))

    result = await act_agent.apply_act_techniques(sample_intake_data)

    response_data = json.loads(result["response"])
    # Check that workable action is small and specific
    assert "workable_action" in response_data
    assert any(
        term in response_data["workable_action"].lower()
        for term in ["one", "small", "just", "could you"]
    )


@pytest.mark.asyncio
async def test_act_response_structure_validation(act_agent, sample_intake_data):
    """Test ACT agent response has required structure."""
    mock_response = {
        "act_process": "Values + Committed Action",
        "defusion": "That's a thought",
        "values_exploration": "What matters to you?",
        "acceptance": "Make room for the feeling",
        "metaphor": "Like waves in the ocean",
        "workable_action": "Take one small step",
        "willingness_question": "Are you willing?",
        "observer_self": "You are not your thoughts",
    }

    act_agent.run = AsyncMock(return_value=json.dumps(mock_response))

    result = await act_agent.apply_act_techniques(sample_intake_data)

    assert result["success"] is True
    response_data = json.loads(result["response"])

    # Validate all required fields are present
    required_fields = [
        "act_process",
        "defusion",
        "values_exploration",
        "acceptance",
        "metaphor",
        "workable_action",
        "willingness_question",
        "observer_self",
    ]

    for field in required_fields:
        assert field in response_data, f"Missing required field: {field}"


@pytest.mark.asyncio
async def test_act_agent_handles_errors_gracefully(act_agent, sample_intake_data):
    """Test ACT agent handles errors appropriately."""
    act_agent.run = AsyncMock(side_effect=Exception("API error"))

    result = await act_agent.apply_act_techniques(sample_intake_data)

    assert result["success"] is False
    assert "error" in result
    assert result["agent_name"] == "ACTFrameworkAgent"


@pytest.mark.asyncio
async def test_act_agent_emphasizes_willingness_not_willpower(act_agent, sample_intake_data):
    """Test ACT agent emphasizes willingness over willpower."""
    mock_response = {
        "act_process": "Values + Committed Action",
        "defusion": "Your mind is warning you about embarrassment.",
        "values_exploration": "Intellectual connection seems important to you.",
        "acceptance": "You don't have to like anxiety, just be willing to have it along.",
        "metaphor": "Like inviting an annoying relative to dinner - they're there but don't run the show.",
        "workable_action": "Show up for 10 minutes with anxiety as your guest.",
        "willingness_question": "On a scale of 1-10, how willing (not wanting) are you to feel anxious for connection?",
        "observer_self": "Notice who's choosing - you, not your anxiety.",
    }

    act_agent.run = AsyncMock(return_value=json.dumps(mock_response))

    result = await act_agent.apply_act_techniques(sample_intake_data)

    response_data = json.loads(result["response"])
    # Check for willingness language, not forcing or fighting
    response_text = json.dumps(response_data).lower()
    assert "willing" in response_text
    assert "force" not in response_text
    assert "eliminate" not in response_text
    assert "get rid of" not in response_text
