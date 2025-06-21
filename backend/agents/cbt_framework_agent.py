"""CBT Framework Agent for applying cognitive behavioral therapy techniques."""

from .base import ReFrameAgent
from typing import Dict, Any, List


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
        """Initialize the CBT Framework Agent."""
        super().__init__(
            name="CBTFrameworkAgent",
            instructions=self.INSTRUCTIONS
        )
    
    def _extract_reasoning_path(self, response: Any) -> Dict[str, Any]:
        """Extract CBT reasoning for transparency."""
        return {
            "raw_response": str(response),
            "steps": [
                "Identified cognitive distortions",
                "Selected appropriate CBT techniques",
                "Generated balanced alternatives",
                "Crafted gentle challenges",
                "Proposed gradual action steps"
            ]
        }
    
    async def apply_cbt_techniques(self, intake_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply CBT techniques to validated user input."""
        # Prepare input for CBT processing
        cbt_input = {
            "thought_data": intake_data,
            "focus": "AvPD-sensitive reframing",
            "techniques_priority": [
                "cognitive_restructuring",
                "evidence_examination",
                "gradual_exposure"
            ]
        }
        
        return await self.process_with_transparency(cbt_input)
    
    def get_avpd_specific_techniques(self) -> List[str]:
        """Return CBT techniques particularly effective for AvPD."""
        return [
            "Gentle cognitive restructuring",
            "Self-compassion exercises",
            "Gradual social exposure planning",
            "Fear of criticism analysis",
            "Perfectionism challenging",
            "Social situation reframing"
        ]