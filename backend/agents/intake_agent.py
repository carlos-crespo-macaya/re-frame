"""Intake Agent for collecting and validating user input."""

from .base import ReFrameAgent
from typing import Dict, Any
import re


class IntakeAgent(ReFrameAgent):
    """Agent responsible for collecting and validating user thoughts."""
    
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
        """Initialize the Intake Agent."""
        super().__init__(
            name="IntakeAgent",
            instructions=self.INSTRUCTIONS
        )
    
    def _extract_reasoning_path(self, response: Any) -> Dict[str, Any]:
        """Extract intake reasoning for transparency."""
        return {
            "raw_response": str(response),
            "steps": [
                "Content validation and safety check",
                "Thought pattern identification",
                "Emotion and behavior extraction",
                "AvPD-specific pattern recognition"
            ]
        }
    
    def _validate_input_length(self, text: str) -> bool:
        """Validate input is within reasonable bounds."""
        word_count = len(text.split())
        return 5 <= word_count <= 500
    
    def _check_for_urls(self, text: str) -> bool:
        """Check if input contains URLs (potential spam)."""
        url_pattern = r'https?://\S+|www\.\S+'
        return bool(re.search(url_pattern, text))
    
    async def process_user_input(self, user_input: str) -> Dict[str, Any]:
        """Process and validate user input."""
        # Basic validation
        if not self._validate_input_length(user_input):
            return {
                "success": False,
                "error": "Input must be between 5 and 500 words."
            }
        
        if self._check_for_urls(user_input):
            return {
                "success": False,
                "error": "URLs are not allowed in thoughts."
            }
        
        # Process with agent
        input_data = {
            "user_thought": user_input,
            "timestamp": "current",
            "context": "initial_intake"
        }
        
        return await self.process_with_transparency(input_data)