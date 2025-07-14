"""Safety response system for crisis situations."""

from typing import Any

from src.utils.crisis_detection import CrisisDetector


class SafetyResponse:
    """Handles responses to crisis situations."""

    def __init__(self):
        self.crisis_detector = CrisisDetector()

        # Crisis response templates
        self.response_templates = {
            "critical": """I'm very concerned about what you've shared. Your safety is the top priority right now.

**Please reach out for immediate help:**
- **National Suicide Prevention Lifeline**: 988 or 1-800-273-8255
- **Crisis Text Line**: Text HOME to 741741
- **Emergency Services**: 911

You don't have to go through this alone. These services have trained professionals available 24/7 who want to help.

Would you like me to provide additional local resources?""",
            "high": """I notice you're going through something very difficult. It's important that you talk to someone who can provide professional support.

**Available resources:**
- **National Suicide Prevention Lifeline**: 988
- **Crisis Text Line**: Text HOME to 741741
- **SAMHSA National Helpline**: 1-800-662-4357

These services are confidential and available 24/7. Is there anything specific I can help you find?""",
            "medium": """It sounds like you're dealing with some challenging thoughts. While I can offer CBT techniques, it's important to also connect with professional support.

**Helpful resources:**
- **Psychology Today Therapist Finder**: psychologytoday.com
- **SAMHSA Treatment Locator**: findtreatment.samhsa.gov
- **Your primary care doctor** can also provide referrals

Would you like to continue with some coping strategies while you consider these options?""",
        }

        self.follow_up_questions = {
            "critical": "Are you in a safe place right now? Is there someone you trust who could be with you?",
            "high": "Have you talked to anyone about these feelings? Would you like help finding support in your area?",
            "medium": "What kind of support would be most helpful for you right now?",
        }

    def get_crisis_response(self, user_input: str) -> dict[str, Any] | None:
        """
        Generate appropriate crisis response based on user input.

        Args:
            user_input: The user's message

        Returns:
            Dict with response details or None if no crisis detected
        """
        is_crisis, crisis_type, matched_patterns = self.crisis_detector.detect_crisis(
            user_input
        )

        if not is_crisis:
            return None

        severity = self.crisis_detector.get_severity_level(crisis_type)

        return {
            "is_crisis": True,
            "crisis_type": crisis_type,
            "severity": severity,
            "immediate_response": self.response_templates.get(
                severity, self.response_templates["medium"]
            ),
            "follow_up": self.follow_up_questions.get(severity, ""),
            "matched_patterns": matched_patterns,
            "should_end_session": severity == "critical",
        }

    def format_response_for_session(self, crisis_response: dict[str, Any]) -> str:
        """
        Format crisis response for session output.

        Args:
            crisis_response: Crisis response dictionary

        Returns:
            Formatted response string
        """
        response_parts = [crisis_response["immediate_response"]]

        if crisis_response.get("follow_up"):
            response_parts.append(f"\n{crisis_response['follow_up']}")

        if crisis_response.get("should_end_session"):
            response_parts.append(
                "\n**Note**: For your safety, I'm focusing on getting you connected with immediate help rather than continuing our CBT session."
            )

        return "\n".join(response_parts)
