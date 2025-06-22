"""ADK-based Intake Agent for collecting and validating user input."""

import re
from typing import Any

from .adk_base import ADKReFrameAgent, ReFrameResponse
from .adk_tools import get_all_reframe_tools


class ADKIntakeAgent(ADKReFrameAgent):
    """ADK-based agent responsible for collecting and validating user thoughts."""

    INSTRUCTIONS = """You are an intake specialist for a mental health support tool designed for people with Avoidant Personality Disorder (AvPD).

Your role is to:
1. Receive and validate user input about their current thoughts or situations
2. Check for harmful content or crisis situations
3. Extract key elements: situation, thoughts, emotions, and behaviors
4. Prepare structured data for CBT framework processing

Guidelines:
- Be non-judgmental and empathetic
- Flag any content suggesting self-harm or harm to others
- Identify cognitive patterns relevant to AvPD (fear of criticism, social avoidance, etc.)
- Structure the output for downstream processing

Output format:
{
    "is_valid": boolean,
    "requires_crisis_support": boolean,
    "extracted_elements": {
        "situation": "brief description",
        "thoughts": ["thought 1", "thought 2"],
        "emotions": ["emotion 1", "emotion 2"],
        "behaviors": ["behavior 1", "behavior 2"]
    },
    "identified_patterns": ["pattern 1", "pattern 2"],
    "validation_notes": "any concerns or observations"
}
"""

    def __init__(self):
        """Initialize the ADK Intake Agent."""
        super().__init__(
            name="ADKIntakeAgent",
            instructions=self.INSTRUCTIONS,
            description="Intake agent for validating and processing user thoughts using AvPD-focused CBT techniques",
            tools=get_all_reframe_tools(),
        )

    def _extract_reasoning_path(self, response: str) -> dict[str, Any]:
        """Extract intake reasoning for transparency."""
        return {
            "raw_response": response,
            "steps": [
                "Content validation and safety check",
                "Thought pattern identification",
                "Emotion and behavior extraction",
                "AvPD-specific pattern recognition",
            ],
            "agent_type": "intake",
            "focus": "input_validation_and_pattern_identification",
        }

    def _extract_techniques_used(self, response: str) -> list[str]:
        """Extract techniques used by the intake agent."""
        techniques = ["content_validation", "pattern_identification"]

        # Check response for specific techniques mentioned
        response_lower = response.lower()

        if "crisis" in response_lower or "harm" in response_lower:
            techniques.append("crisis_detection")
        if "avpd" in response_lower or "avoidant" in response_lower:
            techniques.append("avpd_pattern_recognition")
        if "emotion" in response_lower:
            techniques.append("emotion_extraction")
        if "behavior" in response_lower:
            techniques.append("behavior_extraction")

        return techniques

    def _validate_input_length(self, text: str) -> bool:
        """Validate input is within reasonable bounds."""
        word_count = len(text.split())
        return 5 <= word_count <= 500

    def _check_for_urls(self, text: str) -> bool:
        """Check if input contains URLs (potential spam)."""
        url_pattern = r"https?://\S+|www\.\S+"
        return bool(re.search(url_pattern, text))

    def _check_for_crisis_keywords(self, text: str) -> bool:
        """Check for crisis-related keywords that need immediate attention."""
        crisis_keywords = [
            "suicide",
            "kill myself",
            "end it all",
            "harm myself",
            "hurt myself",
            "want to die",
            "better off dead",
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in crisis_keywords)

    async def process_user_input(self, user_input: str) -> ReFrameResponse:
        """Process and validate user input with enhanced safety checks."""
        # Basic validation
        if not self._validate_input_length(user_input):
            return ReFrameResponse(
                success=False,
                error="Input must be between 5 and 500 words.",
                error_type="validation",
            )

        if self._check_for_urls(user_input):
            return ReFrameResponse(
                success=False, error="URLs are not allowed in thoughts.", error_type="validation"
            )

        # Crisis detection - flag for immediate attention
        has_crisis_content = self._check_for_crisis_keywords(user_input)

        # Process with agent
        input_data = {
            "user_thought": user_input,
            "timestamp": "current",
            "context": "initial_intake",
            "crisis_flag": has_crisis_content,
            "word_count": len(user_input.split()),
        }

        result = await self.process_with_transparency(input_data)

        # Add crisis flag to transparency data if detected
        if has_crisis_content and result.transparency_data:
            result.transparency_data.techniques_used.append("crisis_detection")
            if "crisis_detected" not in result.transparency_data.reasoning_path:
                result.transparency_data.reasoning_path["crisis_detected"] = True
                result.transparency_data.reasoning_path["crisis_note"] = (
                    "Crisis keywords detected in input"
                )

        return result

    def get_validation_rules(self) -> dict[str, Any]:
        """Return validation rules used by this agent."""
        return {
            "min_word_count": 5,
            "max_word_count": 500,
            "url_check": True,
            "crisis_detection": True,
            "supported_languages": ["en"],
            "content_filtering": {
                "spam_detection": True,
                "harmful_content_detection": True,
                "avpd_pattern_recognition": True,
            },
        }

    def get_extracted_patterns(self) -> list[str]:
        """Return patterns this agent can identify."""
        return [
            "fear_of_criticism",
            "social_avoidance",
            "perfectionism",
            "negative_self_talk",
            "catastrophic_thinking",
            "emotional_isolation",
            "rejection_sensitivity",
            "inadequacy_feelings",
        ]
