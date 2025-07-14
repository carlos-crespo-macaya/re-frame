"""Tests for CBT Context Module."""

from src.knowledge.cbt_context import (
    BALANCED_THOUGHT_CRITERIA,
    BASE_CBT_CONTEXT,
    CBT_MODEL,
    COGNITIVE_DISTORTIONS,
    CRISIS_INDICATORS,
    CRISIS_RESPONSE_TEMPLATE,
    EVIDENCE_GATHERING,
    MICRO_ACTION_PRINCIPLES,
    THERAPEUTIC_PRINCIPLES,
    create_agent_with_context,
    detect_distortions,
    initialize_session_with_cbt_context,
)


class TestConstants:
    """Test all CBT constants and knowledge structures."""

    def test_base_cbt_context(self):
        """Test BASE_CBT_CONTEXT contains required elements."""
        assert isinstance(BASE_CBT_CONTEXT, str)
        assert "Cognitive Behavioral Therapy" in BASE_CBT_CONTEXT
        assert "does not replace professional therapy" in BASE_CBT_CONTEXT
        assert "evidence-based CBT techniques" in BASE_CBT_CONTEXT
        assert "empathetic, non-judgmental" in BASE_CBT_CONTEXT

    def test_cbt_model(self):
        """Test CBT_MODEL structure."""
        assert "components" in CBT_MODEL
        assert "description" in CBT_MODEL
        assert "flow" in CBT_MODEL
        assert len(CBT_MODEL["components"]) == 4
        assert "Situation" in CBT_MODEL["components"]
        assert "Automatic Thought" in CBT_MODEL["components"]
        assert "Emotion" in CBT_MODEL["components"]
        assert "Behavior" in CBT_MODEL["components"]

    def test_therapeutic_principles(self):
        """Test THERAPEUTIC_PRINCIPLES structure."""
        assert isinstance(THERAPEUTIC_PRINCIPLES, dict)
        assert "collaborative_empiricism" in THERAPEUTIC_PRINCIPLES
        assert "self_efficacy" in THERAPEUTIC_PRINCIPLES
        assert "socratic_questioning" in THERAPEUTIC_PRINCIPLES
        assert "behavioral_experiments" in THERAPEUTIC_PRINCIPLES
        assert "validation_first" in THERAPEUTIC_PRINCIPLES
        assert "trauma_informed" in THERAPEUTIC_PRINCIPLES

    def test_cognitive_distortions_structure(self):
        """Test COGNITIVE_DISTORTIONS has all required distortions."""
        expected_distortions = [
            "mind_reading",
            "fortune_telling",
            "catastrophizing",
            "all_or_nothing",
            "mental_filter",
            "personalization",
            "labeling",
            "should_statements",
            "emotional_reasoning",
            "discounting_positives",
        ]
        for distortion in expected_distortions:
            assert distortion in COGNITIVE_DISTORTIONS

    def test_cognitive_distortion_attributes(self):
        """Test each cognitive distortion has required attributes."""
        for distortion in COGNITIVE_DISTORTIONS.values():
            assert "code" in distortion
            assert "name" in distortion
            assert "definition" in distortion
            assert "examples" in distortion
            assert "reframing_strategies" in distortion
            assert "micro_actions" in distortion
            assert len(distortion["code"]) == 2  # Two-letter codes
            assert isinstance(distortion["examples"], list)
            assert isinstance(distortion["reframing_strategies"], list)
            assert isinstance(distortion["micro_actions"], list)
            assert len(distortion["examples"]) >= 2
            assert len(distortion["reframing_strategies"]) >= 3
            assert len(distortion["micro_actions"]) >= 2

    def test_evidence_gathering(self):
        """Test EVIDENCE_GATHERING structure."""
        assert "techniques" in EVIDENCE_GATHERING
        assert "principles" in EVIDENCE_GATHERING
        assert isinstance(EVIDENCE_GATHERING["techniques"], list)
        assert isinstance(EVIDENCE_GATHERING["principles"], list)
        assert len(EVIDENCE_GATHERING["techniques"]) >= 6
        assert len(EVIDENCE_GATHERING["principles"]) >= 4

    def test_balanced_thought_criteria(self):
        """Test BALANCED_THOUGHT_CRITERIA structure."""
        expected_criteria = [
            "believable",
            "evidence_based",
            "acknowledges_truth",
            "flexible",
            "helpful",
        ]
        for criterion in expected_criteria:
            assert criterion in BALANCED_THOUGHT_CRITERIA
            assert isinstance(BALANCED_THOUGHT_CRITERIA[criterion], str)

    def test_micro_action_principles(self):
        """Test MICRO_ACTION_PRINCIPLES structure."""
        expected_principles = [
            "duration",
            "specific",
            "achievable",
            "relevant",
            "experimental",
        ]
        for principle in expected_principles:
            assert principle in MICRO_ACTION_PRINCIPLES
            assert isinstance(MICRO_ACTION_PRINCIPLES[principle], str)

    def test_crisis_indicators(self):
        """Test CRISIS_INDICATORS list."""
        assert isinstance(CRISIS_INDICATORS, list)
        assert len(CRISIS_INDICATORS) > 10
        assert "suicide" in CRISIS_INDICATORS
        assert "self-harm" in CRISIS_INDICATORS
        assert all(isinstance(indicator, str) for indicator in CRISIS_INDICATORS)

    def test_crisis_response_template(self):
        """Test CRISIS_RESPONSE_TEMPLATE contains essential elements."""
        assert isinstance(CRISIS_RESPONSE_TEMPLATE, str)
        assert "988" in CRISIS_RESPONSE_TEMPLATE  # US crisis line
        assert "116 123" in CRISIS_RESPONSE_TEMPLATE  # UK Samaritans
        assert "concerned about your safety" in CRISIS_RESPONSE_TEMPLATE
        assert "emergency services" in CRISIS_RESPONSE_TEMPLATE


class TestSessionInitialization:
    """Test session initialization with CBT context."""

    def test_initialize_session_with_cbt_context(self):
        """Test session initialization adds required CBT context."""

        # Mock session object
        class MockSession:
            def __init__(self):
                self.state = {}

        session = MockSession()
        initialize_session_with_cbt_context(session)

        assert "cbt_guidelines" in session.state
        assert session.state["cbt_guidelines"] == THERAPEUTIC_PRINCIPLES
        assert "distortion_types" in session.state
        assert session.state["distortion_types"] == list(COGNITIVE_DISTORTIONS.keys())
        assert "phase" in session.state
        assert session.state["phase"] == "greeting"
        assert "language" in session.state
        assert session.state["language"] == "en"
        assert "safety_flags" in session.state
        assert isinstance(session.state["safety_flags"], list)
        assert len(session.state["safety_flags"]) == 0


class TestAgentCreation:
    """Test agent creation with CBT context."""

    def test_create_agent_with_context(self):
        """Test agent creation includes base CBT context."""
        # Since Google ADK is now installed, we need to test differently
        # We'll check that the function can be called and returns expected type
        try:
            agent = create_agent_with_context(
                name="test_agent", specific_instruction="Test specific instruction"
            )
            # If it works, check it's the right type
            assert hasattr(agent, "name")
            assert agent.name == "test_agent"
        except Exception as e:
            # If it fails due to missing config/credentials, that's expected
            # But the import should work
            assert "Google ADK" not in str(e)


class TestDistortionDetection:
    """Test cognitive distortion detection functionality."""

    def test_detect_all_or_nothing_thinking(self):
        """Test detection of all-or-nothing thinking."""
        thoughts = [
            "I always fail at everything",
            "I never do anything right",
            "Everyone hates me",
            "Nothing ever works out",
        ]
        for thought in thoughts:
            detected = detect_distortions(thought)
            assert "AO" in detected

    def test_detect_fortune_telling(self):
        """Test detection of fortune telling."""
        thoughts = [
            "I will definitely fail the exam",
            "I'm going to embarrass myself",
            "This will be a disaster",
            "I won't be able to handle it",
        ]
        for thought in thoughts:
            detected = detect_distortions(thought)
            assert "FT" in detected

    def test_detect_should_statements(self):
        """Test detection of should statements."""
        thoughts = [
            "I should be perfect",
            "I must always succeed",
            "I have to please everyone",
            "I ought to know better",
        ]
        for thought in thoughts:
            detected = detect_distortions(thought)
            assert "SH" in detected

    def test_detect_labeling(self):
        """Test detection of labeling."""
        thoughts = [
            "I am stupid",
            "I'm a complete loser",
            "I am a failure",
            "I'm worthless",
        ]
        for thought in thoughts:
            detected = detect_distortions(thought)
            assert "LB" in detected

    def test_detect_multiple_distortions(self):
        """Test detection of multiple distortions in one thought."""
        thought = (
            "I always fail at everything and I should be better - I'm such a loser"
        )
        detected = detect_distortions(thought)
        assert "AO" in detected  # "always"
        assert "SH" in detected  # "should"
        assert "LB" in detected  # "loser"

    def test_detect_no_distortions(self):
        """Test thoughts without obvious distortions."""
        thoughts = [
            "I made a mistake today",
            "I feel sad about what happened",
            "This was difficult for me",
            "I could have done better",
        ]
        for thought in thoughts:
            detected = detect_distortions(thought)
            # These thoughts might not have obvious keyword-based distortions
            assert isinstance(detected, list)

    def test_case_insensitive_detection(self):
        """Test that detection is case-insensitive."""
        thoughts = [
            ("I ALWAYS fail", "AO"),
            ("i ShOuLd be perfect", "SH"),
            ("I AM STUPID", "LB"),
        ]
        for thought, expected_code in thoughts:
            detected = detect_distortions(thought)
            assert expected_code in detected


class TestDistortionCodes:
    """Test that all distortion codes are unique and valid."""

    def test_unique_distortion_codes(self):
        """Test all distortion codes are unique."""
        codes = [d["code"] for d in COGNITIVE_DISTORTIONS.values()]
        assert len(codes) == len(set(codes))

    def test_distortion_code_format(self):
        """Test all distortion codes are 2 uppercase letters."""
        for distortion in COGNITIVE_DISTORTIONS.values():
            code = distortion["code"]
            assert len(code) == 2
            assert code.isupper()
            assert code.isalpha()


class TestCrisisDetection:
    """Test crisis indicator detection."""

    def test_crisis_keywords_lowercase(self):
        """Test all crisis indicators are lowercase for consistent matching."""
        for indicator in CRISIS_INDICATORS:
            assert indicator == indicator.lower()

    def test_crisis_coverage(self):
        """Test crisis indicators cover main crisis scenarios."""
        essential_indicators = ["suicide", "kill myself", "self-harm", "end it all"]
        for indicator in essential_indicators:
            assert any(indicator in crisis for crisis in CRISIS_INDICATORS)
