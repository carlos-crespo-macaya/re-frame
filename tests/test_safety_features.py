"""Tests for safety features including crisis detection and response."""

from src.utils.crisis_detection import CrisisDetector
from src.utils.local_resources import LocalResourceProvider
from src.utils.safety_response import SafetyResponse


class TestCrisisDetection:
    """Test crisis detection functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.detector = CrisisDetector()

    def test_detect_suicide_keywords(self):
        """Test detection of suicide-related keywords."""
        test_cases = [
            ("I want to kill myself", True, "suicide"),
            ("I feel like ending my life", True, "suicide"),
            ("Life isn't worth living anymore", True, "suicide"),
            ("I can't go on like this", True, "suicide"),
            ("Everything would be better if I was dead", True, "suicide"),
        ]

        for text, expected_crisis, expected_type in test_cases:
            is_crisis, crisis_type, _ = self.detector.detect_crisis(text)
            assert is_crisis == expected_crisis, f"Failed to detect crisis in: {text}"
            assert crisis_type == expected_type, f"Wrong crisis type for: {text}"

    def test_detect_self_harm(self):
        """Test detection of self-harm indicators."""
        test_cases = [
            ("I want to hurt myself", True, "self_harm"),
            ("I've been cutting", True, "self_harm"),
            ("Thoughts of self-harm", True, "self_harm"),
            ("I need to harm myself to feel better", True, "self_harm"),
        ]

        for text, expected_crisis, expected_type in test_cases:
            is_crisis, crisis_type, _ = self.detector.detect_crisis(text)
            assert is_crisis == expected_crisis
            assert crisis_type == expected_type

    def test_detect_violence(self):
        """Test detection of violence indicators."""
        test_cases = [
            ("I want to hurt someone", True, "violence"),
            ("I have violent thoughts about my boss", True, "violence"),
            ("I might harm others", True, "violence"),
        ]

        for text, expected_crisis, expected_type in test_cases:
            is_crisis, crisis_type, _ = self.detector.detect_crisis(text)
            assert is_crisis == expected_crisis
            assert crisis_type == expected_type

    def test_immediate_danger_priority(self):
        """Test that immediate danger is prioritized."""
        text = "I'm about to kill myself right now"
        is_crisis, crisis_type, _ = self.detector.detect_crisis(text)
        assert is_crisis is True
        assert crisis_type == "immediate_danger"

    def test_past_tense_handling(self):
        """Test that past tense reduces crisis detection."""
        test_cases = [
            ("I used to feel like hurting myself", False),
            ("I was feeling suicidal last year", False),
            ("In the past, I had thoughts of self-harm", False),
            ("I previously felt like ending it all", False),
        ]

        for text, expected_crisis in test_cases:
            is_crisis, _, _ = self.detector.detect_crisis(text)
            assert (
                is_crisis == expected_crisis
            ), f"Past tense not handled correctly for: {text}"

    def test_academic_context(self):
        """Test that academic context is handled appropriately."""
        test_cases = [
            ("I'm researching suicide prevention", False),
            ("My friend told me about self-harm", False),
            ("I read about violent thoughts in psychology", False),
            ("Studying depression and suicidal ideation", False),
        ]

        for text, expected_crisis in test_cases:
            is_crisis, _, _ = self.detector.detect_crisis(text)
            assert is_crisis == expected_crisis

    def test_severity_levels(self):
        """Test severity level assignment."""
        assert self.detector.get_severity_level("immediate_danger") == "critical"
        assert self.detector.get_severity_level("suicide") == "critical"
        assert self.detector.get_severity_level("self_harm") == "high"
        assert self.detector.get_severity_level("violence") == "high"
        assert self.detector.get_severity_level(None) == "none"


class TestSafetyResponse:
    """Test safety response system."""

    def setup_method(self):
        """Set up test fixtures."""
        self.responder = SafetyResponse()

    def test_crisis_response_generation(self):
        """Test that appropriate responses are generated."""
        response = self.responder.get_crisis_response("I want to kill myself")

        assert response is not None
        assert response["is_crisis"] is True
        assert response["crisis_type"] == "suicide"
        assert response["severity"] == "critical"
        assert "988" in response["immediate_response"]
        assert response["should_end_session"] is True

    def test_no_crisis_returns_none(self):
        """Test that non-crisis text returns None."""
        response = self.responder.get_crisis_response("I'm feeling a bit sad today")
        assert response is None

    def test_response_formatting(self):
        """Test response formatting."""
        crisis_response = {
            "immediate_response": "Test response",
            "follow_up": "Test follow up",
            "should_end_session": True,
        }

        formatted = self.responder.format_response_for_session(crisis_response)
        assert "Test response" in formatted
        assert "Test follow up" in formatted
        assert "focusing on getting you connected" in formatted

    def test_different_severity_responses(self):
        """Test that different severities get different responses."""
        # Critical response
        critical = self.responder.get_crisis_response(
            "I'm going to kill myself right now"
        )
        assert critical["severity"] == "critical"
        assert "911" in critical["immediate_response"]

        # High severity response
        high = self.responder.get_crisis_response("I've been cutting myself")
        assert high["severity"] == "high"
        assert "Crisis Text Line" in high["immediate_response"]


class TestLocalResources:
    """Test local resource provider."""

    def setup_method(self):
        """Set up test fixtures."""
        self.provider = LocalResourceProvider()

    def test_get_us_resources(self):
        """Test US resource retrieval."""
        resources = self.provider.get_resources_by_country("US")

        assert "national" in resources
        assert "online" in resources
        assert any(r["number"] == "988" for r in resources["national"])
        assert any("psychologytoday.com" in r["url"] for r in resources["online"])

    def test_get_uk_resources(self):
        """Test UK resource retrieval."""
        resources = self.provider.get_resources_by_country("UK")

        assert "national" in resources
        assert any(r["name"] == "Samaritans" for r in resources["national"])
        assert any(r["number"] == "116 123" for r in resources["national"])

    def test_get_international_resources(self):
        """Test fallback to international resources."""
        resources = self.provider.get_resources_by_country("XX")  # Unknown country

        assert "national" in resources or "online" in resources
        assert any("befrienders.org" in str(r) for r in resources.get("online", []))

    def test_format_resources_text(self):
        """Test resource text formatting."""
        text = self.provider.format_resources_text("US")

        assert "24/7 Crisis Support:" in text
        assert "988" in text
        assert "Online Resources:" in text
        assert "psychologytoday.com" in text

    def test_format_resources_without_online(self):
        """Test formatting without online resources."""
        text = self.provider.format_resources_text("US", include_online=False)

        assert "24/7 Crisis Support:" in text
        assert "Online Resources:" not in text

    def test_get_emergency_contacts(self):
        """Test emergency contact retrieval."""
        # US emergency contacts
        us_emergency = self.provider.get_emergency_contacts("US")
        assert any(c["number"] == "911" for c in us_emergency)
        assert any(c["number"] == "988" for c in us_emergency)

        # UK emergency contacts
        uk_emergency = self.provider.get_emergency_contacts("UK")
        assert any(c["number"] == "999" for c in uk_emergency)
        assert any(c["number"] == "116 123" for c in uk_emergency)

        # Default emergency contacts
        default_emergency = self.provider.get_emergency_contacts("XX")
        assert any(c["number"] == "112" for c in default_emergency)


class TestIntegration:
    """Integration tests for safety features."""

    def setup_method(self):
        """Set up test fixtures."""
        self.responder = SafetyResponse()
        self.provider = LocalResourceProvider()

    def test_full_crisis_flow(self):
        """Test complete crisis detection and response flow."""
        # User expresses crisis
        user_input = "I'm thinking about ending my life tonight"

        # Get crisis response
        response = self.responder.get_crisis_response(user_input)
        assert response is not None
        assert response["is_crisis"] is True
        assert response["severity"] == "critical"

        # Format response
        formatted = self.responder.format_response_for_session(response)
        assert "988" in formatted
        assert "Your safety is the top priority" in formatted

        # Get local resources (could be based on user location)
        resources = self.provider.format_resources_text("US")
        assert "National Suicide Prevention Lifeline" in resources

    def test_non_crisis_flow(self):
        """Test that non-crisis situations are handled normally."""
        user_input = "I'm feeling anxious about my upcoming exam"

        response = self.responder.get_crisis_response(user_input)
        assert response is None  # No crisis detected

    def test_past_crisis_discussion(self):
        """Test that past crisis discussions don't trigger immediate response."""
        user_input = (
            "I used to have suicidal thoughts, but therapy helped me overcome them"
        )

        response = self.responder.get_crisis_response(user_input)
        assert response is None  # Past tense, not current crisis
