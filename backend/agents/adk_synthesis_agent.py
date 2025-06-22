"""ADK-based Synthesis Agent for creating user-friendly responses."""

from typing import Any, Dict, List

from .adk_base import ADKReFrameAgent, ReFrameResponse


class ADKSynthesisAgent(ADKReFrameAgent):
    """ADK-based agent responsible for synthesizing CBT output into supportive responses."""

    INSTRUCTIONS = """You are a compassionate communication specialist working with individuals who have Avoidant Personality Disorder (AvPD).

Your role is to:
1. Take CBT framework output and create a warm, supportive response
2. Ensure language is non-threatening and validating
3. Present reframed thoughts in an accessible way
4. Include transparency about the AI assistance

Communication guidelines:
- Use gentle, non-judgmental language
- Acknowledge the difficulty of their situation
- Present alternatives as possibilities, not prescriptions
- Be clear that you're an AI providing CBT-based support
- Encourage self-compassion and gradual progress

Response structure:
1. Validation of their experience
2. Gentle exploration of the thought
3. Alternative perspectives (clearly marked as AI-generated)
4. Small, manageable suggestions
5. Transparency note about techniques used

Output format:
{
    "main_response": "complete response text",
    "key_points": ["point 1", "point 2"],
    "techniques_explained": "brief explanation of CBT techniques used",
    "transparency_summary": "how the AI processed their input",
    "encouragement": "supportive closing message"
}
"""

    def __init__(self):
        """Initialize the ADK Synthesis Agent."""
        super().__init__(
            name="ADKSynthesisAgent",
            instructions=self.INSTRUCTIONS,
            description="Synthesis agent for creating warm, supportive responses from CBT analysis for AvPD users",
        )

    def _extract_reasoning_path(self, response: str) -> Dict[str, Any]:
        """Extract synthesis reasoning for transparency."""
        return {
            "raw_response": response,
            "steps": [
                "Analyzed CBT framework output",
                "Selected appropriate tone and language",
                "Structured supportive response",
                "Added transparency elements",
                "Included encouragement and next steps",
            ],
            "agent_type": "synthesis",
            "focus": "user_friendly_communication_and_support",
            "communication_style": "warm_validating_non_judgmental",
        }

    def _extract_techniques_used(self, response: str) -> List[str]:
        """Extract communication and therapeutic techniques used."""
        techniques = ["supportive_communication", "transparency_provision"]
        response_lower = response.lower()
        
        # Communication techniques mapping
        technique_mapping = {
            "validation": "emotional_validation",
            "empathy": "empathetic_responding",
            "gentle": "gentle_communication",
            "understand": "understanding_acknowledgment",
            "support": "supportive_language",
            "encourage": "encouragement_provision",
            "transparent": "transparency_communication",
            "ai": "ai_disclosure",
            "technique": "technique_explanation",
            "progress": "progress_orientation",
        }
        
        for phrase, technique in technique_mapping.items():
            if phrase in response_lower:
                techniques.append(technique)
        
        return techniques

    async def create_user_response(self, cbt_data: Dict[str, Any]) -> ReFrameResponse:
        """Create final user-facing response from CBT analysis."""
        # Prepare synthesis input
        synthesis_input = {
            "cbt_analysis": cbt_data,
            "tone": "warm and supportive",
            "transparency_level": "high",
            "avpd_sensitivity": "maximum",
            "communication_style": "collaborative_and_encouraging",
            "safety_first": True,
        }

        return await self.process_with_transparency(synthesis_input)

    def format_transparency_block(self, techniques: List[str], reasoning: str) -> str:
        """Format transparency information for user display."""
        return f"""
🔍 **How I processed your thought:**
- Techniques used: {', '.join(techniques)}
- My approach: {reasoning}
- Note: I'm an AI using evidence-based CBT techniques to offer perspectives.
"""

    async def create_crisis_response(self, crisis_data: Dict[str, Any]) -> ReFrameResponse:
        """Create specialized response for crisis situations."""
        crisis_input = {
            "crisis_indicators": crisis_data,
            "response_type": "crisis_support",
            "priority": "immediate_safety",
            "tone": "caring_and_urgent",
            "referral_needed": True,
        }
        
        return await self.process_with_transparency(crisis_input)

    def get_communication_guidelines(self) -> Dict[str, Any]:
        """Return communication guidelines used by this agent."""
        return {
            "tone": "warm_validating_supportive",
            "language_style": "gentle_non_confrontational",
            "approach": "collaborative_not_directive",
            "validation": "always_acknowledge_feelings_first",
            "transparency": "high_level_ai_disclosure",
            "encouragement": "focus_on_gradual_progress",
            "safety": "crisis_aware_communication",
            "avpd_sensitivity": {
                "avoid_criticism": True,
                "minimize_shame": True,
                "respect_pace": True,
                "validate_difficulty": True,
            }
        }

    def get_response_components(self) -> List[str]:
        """Return standard components included in responses."""
        return [
            "emotional_validation",
            "thought_exploration",
            "alternative_perspectives",
            "manageable_suggestions",
            "transparency_disclosure",
            "encouragement",
            "next_steps",
        ]

    async def synthesize_multi_agent_output(
        self, 
        intake_output: Dict[str, Any],
        cbt_output: Dict[str, Any],
        additional_context: Dict[str, Any] = None
    ) -> ReFrameResponse:
        """Synthesize output from multiple agents into coherent user response."""
        synthesis_input = {
            "intake_analysis": intake_output,
            "cbt_analysis": cbt_output,
            "additional_context": additional_context or {},
            "synthesis_type": "multi_agent_coordination",
            "coherence_priority": "high",
            "user_experience_focus": "seamless_and_supportive",
        }
        
        return await self.process_with_transparency(synthesis_input)

    def get_tone_variations(self) -> Dict[str, str]:
        """Return different tone variations for different situations."""
        return {
            "standard": "warm, supportive, and encouraging",
            "crisis": "caring, urgent, and safety-focused",
            "progress": "celebrating, affirming, and motivating", 
            "setback": "understanding, validating, and hopeful",
            "first_time": "welcoming, explanatory, and reassuring",
            "returning": "familiar, building on progress, and consistent",
        }

    def get_transparency_levels(self) -> Dict[str, str]:
        """Return different levels of transparency disclosure."""
        return {
            "minimal": "Basic AI disclosure",
            "standard": "AI disclosure with technique overview", 
            "detailed": "Full technique explanation and reasoning process",
            "educational": "Teaching-focused with CBT education",
        }