"""ACT Framework Agent for applying Acceptance and Commitment Therapy techniques."""

from typing import Any

from .base import ReFrameAgent


class ACTFrameworkAgent(ReFrameAgent):
    """Agent responsible for applying ACT techniques to user thoughts."""

    INSTRUCTIONS = """You are an Acceptance and Commitment Therapy (ACT) specialist working with individuals who have Avoidant Personality Disorder (AvPD).

Your role is to:
1. Help users develop psychological flexibility through the six core ACT processes (Hexaflex)
2. Use defusion techniques to reduce the believability of unhelpful thoughts
3. Foster acceptance of difficult emotions without trying to eliminate them
4. Connect actions to personal values rather than anxiety reduction
5. Provide workable (small, achievable) steps toward valued living

The Six Core ACT Processes (Hexaflex):

1. CONTACT WITH PRESENT MOMENT (for anxiety about future/past):
   - 5-4-3-2-1 grounding exercise
   - Mindful breathing
   - Present moment anchoring

2. ACCEPTANCE (for fighting emotions):
   - Expansion exercises
   - Struggle switch metaphor
   - Guest house metaphor (Rumi)
   - Making room for difficult feelings

3. COGNITIVE DEFUSION (for thought fusion):
   - "I'm having the thought that..."
   - Singing thoughts to silly tunes
   - Leaves on a stream
   - Thank your mind technique

4. SELF-AS-CONTEXT (for "I am my anxiety"):
   - Chessboard metaphor
   - Sky and weather metaphor
   - Observer self exercises

5. VALUES CLARIFICATION (for meaninglessness):
   - Values exploration questions
   - Sweet spot exercise
   - Values vs goals distinction
   - What matters beyond avoidance

6. COMMITTED ACTION (for avoidance):
   - Willingness scale (1-10)
   - Baby steps toward values
   - Passengers on the bus metaphor
   - Bringing anxiety along

AvPD-Specific Considerations:
- Normalize anxiety as a frequent companion
- Emphasize willingness over willpower
- Use gentle, validating language
- Suggest very small initial steps
- Connect to authentic personal values
- Never promise anxiety will disappear

Output format:
{
    "act_process": "Primary ACT process being used",
    "defusion": "Defusion technique or reframe",
    "values_exploration": "Connection to what matters to the user",
    "acceptance": "Acceptance-based response to emotions",
    "metaphor": "Relevant ACT metaphor",
    "workable_action": "Small, concrete step they could take",
    "willingness_question": "Question about willingness to experience discomfort for values",
    "observer_self": "Connection to the observing self/self-as-context"
}

Remember: ACT is about living a rich, meaningful life WITH anxiety, not waiting until anxiety goes away."""

    def __init__(self) -> None:
        """Initialize the ACT Framework Agent."""
        super().__init__(name="ACTFrameworkAgent", instructions=self.INSTRUCTIONS)

    def _extract_reasoning_path(self, response: Any) -> dict[str, Any]:
        """Extract ACT reasoning for transparency."""
        return {
            "raw_response": str(response),
            "steps": [
                "Identified fusion with thoughts or struggle with emotions",
                "Selected appropriate ACT process from Hexaflex",
                "Applied defusion or acceptance techniques",
                "Connected to user's personal values",
                "Offered workable action step",
                "Emphasized willingness over elimination",
            ],
        }

    async def apply_act_techniques(self, intake_data: dict[str, Any]) -> dict[str, Any]:
        """Apply ACT techniques to validated user input."""
        # Prepare input for ACT processing
        act_input = {
            "thought_data": intake_data,
            "focus": "AvPD-sensitive psychological flexibility",
            "values_hint": intake_data.get("values_hint", "connection and authenticity"),
            "hexaflex_priority": self._determine_hexaflex_priority(intake_data),
        }

        return await self.process_with_transparency(act_input)

    def _determine_hexaflex_priority(self, intake_data: dict[str, Any]) -> str:
        """Determine which ACT process to prioritize based on the situation."""
        thought = intake_data.get("original_thought", "").lower()
        categories = intake_data.get("thought_categories", [])

        # Check for different patterns that suggest different ACT processes
        if any(cat in categories for cat in ["fusion", "identity", "self-concept"]):
            if "i am" in thought:
                return "self_as_context_priority"
            return "defusion_priority"

        if any(cat in categories for cat in ["struggle", "fight", "overwhelm"]):
            return "acceptance_priority"

        if any(cat in categories for cat in ["future", "past", "worry", "rumination"]):
            return "present_moment_priority"

        if any(cat in categories for cat in ["meaningless", "pointless", "why bother"]):
            return "values_priority"

        if any(cat in categories for cat in ["avoidance", "escape", "can't"]):
            return "committed_action_priority"

        # Default to defusion for most thought-based concerns
        return "defusion_priority"

    def select_hexaflex_process(self, thought: str, categories: list[str]) -> str:
        """Select the most appropriate ACT process based on thought content."""
        thought_lower = thought.lower()

        # Self-as-Context for identity fusion
        if any(phrase in thought_lower for phrase in ["i am", "i'm broken", "i'm damaged"]) and any(
            cat in categories for cat in ["identity", "self-concept"]
        ):
            return "Self-as-Context"

        # Acceptance for emotional struggle
        if any(
            phrase in thought_lower
            for phrase in ["can't stand", "can't handle", "too much", "unbearable"]
        ) or any(cat in categories for cat in ["avoidance", "struggle"]):
            return "Acceptance"

        # Present Moment for time travel
        if any(cat in categories for cat in ["future", "worry", "past", "rumination"]):
            return "Present Moment"

        # Values for meaninglessness
        if any(
            phrase in thought_lower
            for phrase in ["what's the point", "why bother", "doesn't matter"]
        ) or any(cat in categories for cat in ["values", "meaning"]):
            return "Values Clarification"

        # Defusion for thought believability
        if any(cat in categories for cat in ["catastrophizing", "fusion", "prediction"]):
            return "Cognitive Defusion"

        # Default to Committed Action
        return "Committed Action"

    def get_avpd_specific_act_techniques(self) -> list[str]:
        """Return ACT techniques particularly effective for AvPD."""
        return [
            "Cognitive Defusion: 'I'm having the thought that nobody likes me'",
            "Acceptance: Making room for social anxiety as a frequent visitor",
            "Present Moment: 5-4-3-2-1 grounding when lost in social worries",
            "Self-as-Context: You are the sky, social anxiety is just weather",
            "Values Clarification: What matters to you beyond avoiding judgment?",
            "Committed Action: Willing to feel awkward for 5 minutes for connection",
            "Passengers on Bus: Anxiety yelling directions but you're driving",
            "Struggle Switch: Turn off fighting anxiety, let it be there",
            "Leaves on Stream: Watch self-critical thoughts float by",
            "Willingness Scale: Rate willingness (not wanting) to feel anxious",
        ]
