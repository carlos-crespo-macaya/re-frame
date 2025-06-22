"""CBT Framework Agent for applying cognitive behavioral therapy techniques."""

from typing import Any

from .base import ReFrameAgent
from .models import AgentResponse, CBTAnalysis, IntakeAnalysis


class CBTFrameworkAgent(ReFrameAgent):
    """Agent responsible for applying CBT techniques to user thoughts."""

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
    "reframed_thoughts": ["reframed thought 1", "reframed thought 2"],
    "techniques_applied": [
        {
            "technique_name": "Cognitive Restructuring",
            "description": "Challenge negative automatic thoughts",
            "application": "How it was applied to this specific thought"
        }
    ],
    "action_suggestions": ["small actionable step 1", "small actionable step 2"],
    "validation": "Acknowledging and validating the person's feelings"
}
"""

    def __init__(self):
        """Initialize the CBT Framework Agent."""
        super().__init__(name="CBTFrameworkAgent", instructions=self.INSTRUCTIONS)

    def _extract_reasoning_path(self, response: Any) -> dict[str, Any]:
        """Extract CBT reasoning for transparency."""
        return {
            "raw_response": str(response),
            "steps": [
                "Identified cognitive distortions",
                "Selected appropriate CBT techniques",
                "Generated balanced alternatives",
                "Crafted gentle challenges",
                "Proposed gradual action steps",
            ],
        }

    async def apply_cbt_techniques(self, intake_analysis: IntakeAnalysis) -> AgentResponse:
        """Apply CBT techniques to validated user input."""
        import logging

        logger = logging.getLogger(__name__)

        # Prepare input for CBT processing
        cbt_input = {
            "thought_data": intake_analysis.model_dump(),
            "focus": "AvPD-sensitive reframing",
            "techniques_priority": [
                "cognitive_restructuring",
                "evidence_examination",
                "gradual_exposure",
            ],
        }

        result = await self.process_with_transparency(cbt_input)

        # Parse and validate the response
        if result.get("success") and result.get("response"):
            try:
                analysis_dict = self.parse_json_response(result["response"])
                # Validate the response matches our CBTAnalysis model
                analysis = CBTAnalysis.model_validate(analysis_dict)
                result["parsed_response"] = analysis
            except Exception as e:
                logger.error(f"Failed to validate CBT analysis: {e}")
                result["success"] = False
                result["error"] = f"Invalid response format: {str(e)}"

        return AgentResponse(**result)

    def get_avpd_specific_techniques(self) -> list[str]:
        """Return CBT techniques particularly effective for AvPD."""
        return [
            "Gentle cognitive restructuring",
            "Self-compassion exercises",
            "Gradual social exposure planning",
            "Fear of criticism analysis",
            "Perfectionism challenging",
            "Social situation reframing",
        ]
