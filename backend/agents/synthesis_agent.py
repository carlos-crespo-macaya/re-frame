"""Synthesis Agent for creating user-friendly responses."""

from .base import ReFrameAgent
from typing import Dict, Any


class SynthesisAgent(ReFrameAgent):
    """Agent responsible for synthesizing CBT output into supportive responses."""
    
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
        """Initialize the Synthesis Agent."""
        super().__init__(
            name="SynthesisAgent",
            instructions=self.INSTRUCTIONS
        )
    
    def _extract_reasoning_path(self, response: Any) -> Dict[str, Any]:
        """Extract synthesis reasoning for transparency."""
        return {
            "raw_response": str(response),
            "steps": [
                "Analyzed CBT framework output",
                "Selected appropriate tone and language",
                "Structured supportive response",
                "Added transparency elements",
                "Included encouragement and next steps"
            ]
        }
    
    async def create_user_response(self, cbt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create final user-facing response from CBT analysis."""
        # Prepare synthesis input
        synthesis_input = {
            "cbt_analysis": cbt_data,
            "tone": "warm and supportive",
            "transparency_level": "high",
            "avpd_sensitivity": "maximum"
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