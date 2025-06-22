"""ADK-based CBT Framework Agent for applying cognitive behavioral therapy techniques."""

from typing import Any

from .adk_base import ADKReFrameAgent, ReFrameResponse
from .adk_tools import get_all_reframe_tools


class ADKCBTFrameworkAgent(ADKReFrameAgent):
    """ADK-based agent responsible for applying CBT techniques to user thoughts."""

    INSTRUCTIONS = """You are a Cognitive Behavioral Therapy (CBT) specialist working with individuals who have Avoidant Personality Disorder (AvPD).

Your role is to:
1. Analyze the thought patterns provided by the intake agent
2. Apply appropriate CBT techniques for reframing
3. Generate alternative, balanced perspectives
4. Explain which CBT techniques you're using and why

CBT Techniques to apply:
- Cognitive Restructuring: Challenge negative automatic thoughts
- Evidence For/Against: Examine evidence supporting or contradicting the thought
- Decatastrophizing: Reduce catastrophic thinking
- Behavioral Experiments: Suggest safe ways to test assumptions
- Graded Exposure: Propose small steps for facing fears

Guidelines:
- Be gentle and non-confrontational (crucial for AvPD)
- Acknowledge the person's feelings as valid
- Provide multiple reframing options
- Explain your reasoning transparently
- Focus on safety and gradual progress

Output format:
{
    "original_thought": "user's thought",
    "cognitive_distortions": ["distortion 1", "distortion 2"],
    "techniques_applied": ["technique 1", "technique 2"],
    "reframed_thoughts": [
        {
            "thought": "reframed version",
            "technique": "CBT technique used",
            "explanation": "why this helps"
        }
    ],
    "gentle_challenges": ["challenge 1", "challenge 2"],
    "small_steps": ["step 1", "step 2"],
    "transparency_notes": "explanation of approach"
}
"""

    def __init__(self):
        """Initialize the ADK CBT Framework Agent."""
        super().__init__(
            name="ADKCBTFrameworkAgent",
            instructions=self.INSTRUCTIONS,
            description="CBT specialist agent for applying evidence-based cognitive reframing techniques for AvPD",
            tools=get_all_reframe_tools(),
        )

    def _extract_reasoning_path(self, response: str) -> dict[str, Any]:
        """Extract CBT reasoning for transparency."""
        return {
            "raw_response": response,
            "steps": [
                "Identified cognitive distortions",
                "Selected appropriate CBT techniques",
                "Generated balanced alternatives",
                "Crafted gentle challenges",
                "Proposed gradual action steps",
            ],
            "agent_type": "cbt_framework",
            "focus": "cognitive_reframing_and_behavioral_planning",
            "approach": "avpd_sensitive_cbt",
        }

    def _extract_techniques_used(self, response: str) -> list[str]:
        """Extract CBT techniques used from the response."""
        techniques = []
        response_lower = response.lower()

        # Map technique mentions to standard names
        technique_mapping = {
            "cognitive restructuring": "cognitive_restructuring",
            "evidence": "evidence_examination",
            "decatastroph": "decatastrophizing",
            "behavioral experiment": "behavioral_experiments",
            "graded exposure": "graded_exposure",
            "thought challenging": "thought_challenging",
            "reframing": "cognitive_reframing",
            "mindfulness": "mindfulness",
            "self-compassion": "self_compassion",
            "gradual": "gradual_approach",
        }

        for phrase, technique in technique_mapping.items():
            if phrase in response_lower:
                techniques.append(technique)

        # Always include base CBT techniques for this agent
        if not techniques:
            techniques = ["cognitive_restructuring", "evidence_examination"]

        return techniques

    async def apply_cbt_techniques(self, intake_data: dict[str, Any]) -> ReFrameResponse:
        """Apply CBT techniques to validated user input."""
        # Prepare input for CBT processing
        cbt_input = {
            "thought_data": intake_data,
            "focus": "AvPD-sensitive reframing",
            "techniques_priority": [
                "cognitive_restructuring",
                "evidence_examination",
                "gradual_exposure",
            ],
            "safety_level": "maximum_gentleness",
            "approach": "collaborative_not_confrontational",
        }

        return await self.process_with_transparency(cbt_input)

    def get_avpd_specific_techniques(self) -> list[str]:
        """Return CBT techniques particularly effective for AvPD."""
        return [
            "gentle_cognitive_restructuring",
            "self_compassion_exercises",
            "gradual_social_exposure_planning",
            "fear_of_criticism_analysis",
            "perfectionism_challenging",
            "social_situation_reframing",
        ]

    def get_cognitive_distortions(self) -> list[str]:
        """Return common cognitive distortions this agent can identify."""
        return [
            "all_or_nothing_thinking",
            "catastrophizing",
            "mind_reading",
            "fortune_telling",
            "emotional_reasoning",
            "should_statements",
            "labeling",
            "personalization",
            "mental_filter",
            "disqualifying_positive",
        ]

    def get_reframing_strategies(self) -> dict[str, str]:
        """Return reframing strategies used by this agent."""
        return {
            "balanced_perspective": "Present multiple viewpoints on the situation",
            "evidence_based": "Examine actual evidence for and against the thought",
            "compassionate_reframe": "Reframe with self-compassion and understanding",
            "gradual_challenge": "Gently question assumptions without confrontation",
            "behavioral_focus": "Shift focus to actionable behavioral changes",
            "strength_identification": "Identify personal strengths and past successes",
        }

    async def analyze_thought_patterns(self, thoughts: list[str]) -> ReFrameResponse:
        """Analyze multiple thoughts for patterns and provide comprehensive CBT analysis."""
        analysis_input = {
            "thoughts_list": thoughts,
            "analysis_type": "pattern_identification",
            "focus": "avpd_specific_patterns",
            "depth": "comprehensive",
        }

        return await self.process_with_transparency(analysis_input)

    def get_safety_guidelines(self) -> dict[str, Any]:
        """Return safety guidelines for AvPD-sensitive CBT application."""
        return {
            "approach": "collaborative_not_directive",
            "pace": "gradual_and_patient",
            "validation": "always_validate_feelings_first",
            "challenge_style": "gentle_questioning_not_confrontation",
            "crisis_handling": "immediate_referral_to_professional_help",
            "boundaries": "respect_comfort_zones_while_encouraging_growth",
            "language": "non_judgmental_and_empathetic",
        }
