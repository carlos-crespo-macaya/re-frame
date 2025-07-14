"""Crisis detection patterns and utilities for safety features."""

import re


class CrisisDetector:
    """Detects potential crisis situations in user input."""

    def __init__(self):
        # Crisis keywords grouped by category
        self.crisis_patterns = {
            "suicide": [
                r"\b(kill\s+myself|end\s+my\s+life|ending\s+my\s+life|suicide|suicidal)\b",
                r"\b(want\s+to\s+die|better\s+off\s+dead|no\s+reason\s+to\s+live)\b",
                r"\b(ending\s+it\s+all|can\'t\s+go\s+on|life\s+isn\'t\s+worth)\b",
                r"\b(better\s+if\s+I\s+was\s+dead|better\s+off\s+if\s+I\s+was\s+dead|would\s+be\s+better.*dead)\b",
            ],
            "self_harm": [
                r"\b(hurt\s+myself|harm\s+myself|cut\s+myself|cutting)\b",
                r"\b(self[\s-]?harm|self[\s-]?injury)\b",
            ],
            "violence": [
                r"\b(hurt\s+someone|kill\s+someone|harm\s+others)\b",
                r"\b(violent\s+thoughts|homicidal)\b",
            ],
            "immediate_danger": [
                r"\b(about\s+to|going\s+to|right\s+now).*?(kill|hurt|harm|end)\b",
                r"\b(plan\s+to|decided\s+to|thinking\s+about).*?(die|suicide|hurt|ending\s+my\s+life|ending\s+it)\b",
                r"\b(tonight|today|now|immediately).*?(kill\s+myself|end\s+my\s+life|suicide)\b",
            ],
        }

        # Context indicators that might reduce crisis severity
        self.past_tense_indicators = [
            r"\b(used\s+to|in\s+the\s+past|previously|before)\b",
            r"\b(was\s+feeling|had\s+thoughts|felt\s+like)\b",
        ]

        # Academic/hypothetical context
        self.academic_indicators = [
            r"\b(research|researching|studying|learning\s+about|read\s+about)\b",
            r"\b(someone\s+else|my\s+friend|hypothetically)\b",
        ]

    def detect_crisis(self, text: str) -> tuple[bool, str | None, list[str]]:
        """
        Detect if the text contains crisis indicators.

        Args:
            text: User input text to analyze

        Returns:
            Tuple of (is_crisis, crisis_type, matched_patterns)
        """
        text_lower = text.lower()

        # Check for past tense or academic context
        is_past_tense = any(
            re.search(pattern, text_lower) for pattern in self.past_tense_indicators
        )
        is_academic = any(
            re.search(pattern, text_lower) for pattern in self.academic_indicators
        )

        matched_patterns = []
        crisis_type = None

        # Check each crisis category
        for category, patterns in self.crisis_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    matched_patterns.append(pattern)
                    if not crisis_type or category == "immediate_danger":
                        crisis_type = category

        # Determine if this is an actual crisis
        is_crisis = bool(matched_patterns) and not (
            is_past_tense and "immediate_danger" not in str(crisis_type)
        )

        # Academic context generally overrides crisis detection unless immediate danger
        if is_academic and crisis_type != "immediate_danger":
            is_crisis = False

        return is_crisis, crisis_type, matched_patterns

    def get_severity_level(self, crisis_type: str | None) -> str:
        """
        Get the severity level of the crisis.

        Args:
            crisis_type: Type of crisis detected

        Returns:
            Severity level: 'critical', 'high', or 'medium'
        """
        if not crisis_type:
            return "none"

        severity_map = {
            "immediate_danger": "critical",
            "suicide": "critical",
            "self_harm": "high",
            "violence": "high",
        }

        return severity_map.get(crisis_type, "medium")


# Tool function for ADK agents
def check_crisis_indicators(user_message: str) -> dict:
    """
    Check if user message contains crisis indicators.

    Args:
        user_message: The user's message to analyze

    Returns:
        dict: Crisis detection results including severity and type
    """
    detector = CrisisDetector()
    is_crisis, crisis_type, matched_patterns = detector.detect_crisis(user_message)
    severity = detector.get_severity_level(crisis_type)

    return {
        "crisis_detected": is_crisis,
        "crisis_type": crisis_type,
        "severity": severity,
        "matched_patterns": matched_patterns,
        "requires_immediate_response": severity in ["critical", "high"],
    }
