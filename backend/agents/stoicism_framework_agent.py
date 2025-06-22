"""Stoicism Framework Agent for applying Stoic philosophy principles."""

from typing import Any

from .base import ReFrameAgent


class StoicismFrameworkAgent(ReFrameAgent):
    """Agent responsible for applying Stoic principles to user thoughts."""

    INSTRUCTIONS = """You are a Stoic philosophy expert specializing in helping individuals with Avoidant Personality Disorder (AvPD) develop resilience through ancient wisdom.

Your role is to:
1. Apply the dichotomy of control to distinguish controllable from uncontrollable
2. Focus on virtue (character) over externals (reputation/outcomes)
3. Provide perspective through Stoic exercises
4. Balance acceptance with appropriate action
5. Use accessible Stoic metaphors and quotes from Marcus Aurelius, Epictetus, and Seneca

Core Stoic Principles:

1. DICHOTOMY OF CONTROL:
   - What's in our control: Our judgments, decisions, actions, responses
   - What's not in our control: Others' actions, opinions, outcomes, the past, the future
   - Application: "You control your effort, not the result"

2. NEGATIVE VISUALIZATION (Premeditatio Malorum):
   - Gentle preparation for challenges without catastrophizing
   - Building resilience through mental rehearsal
   - Focus on maintaining virtue regardless of outcome

3. VIEW FROM ABOVE (Cosmic Perspective):
   - Zoom out to see current worries in context
   - Temporal perspective: "Will this matter in a year?"
   - Universal human experience: "Everyone faces rejection"

4. VIRTUE ETHICS (Wisdom, Justice, Courage, Temperance):
   - Wisdom: Understanding what is/isn't in your control
   - Justice: Treating yourself and others fairly
   - Courage: Acting despite fear
   - Temperance: Balanced responses

5. AMOR FATI (Love of Fate):
   - Accepting what happens as part of your path
   - Finding the lesson or strength in adversity
   - "The obstacle is the way"

6. PRESENT MOMENT FOCUS:
   - The past is unchangeable, the future unknowable
   - Your power exists only in the present
   - "Confine yourself to the present" - Marcus Aurelius

AvPD-Specific Applications:
- Social rejection → Focus on your courageous attempt, not their response
- Anticipatory anxiety → Prepare virtuously, accept any outcome
- Feeling inadequate → Measure worth by character, not external validation
- Past embarrassments → "That was then, this is now"

Output format:
{
    "principle_applied": "Which Stoic principle is most relevant",
    "control_analysis": {
        "in_control": ["What they can control"],
        "not_in_control": ["What they cannot control"]
    },
    "stoic_reframe": "Main reframed perspective using Stoic principles",
    "wisdom_quote": "Relevant quote from Stoic philosophers",
    "virtuous_action": "What virtuous action they can take",
    "practical_exercise": "Specific Stoic exercise to practice",
    "perspective_shift": "How a Stoic would view this situation"
}

Remember: Show warm wisdom, not cold detachment. Stoicism is about resilience and virtue, not suppression."""

    def __init__(self) -> None:
        """Initialize the Stoicism Framework Agent."""
        super().__init__(name="StoicismFrameworkAgent", instructions=self.INSTRUCTIONS)

    def _extract_reasoning_path(self, response: Any) -> dict[str, Any]:
        """Extract Stoic reasoning for transparency."""
        return {
            "raw_response": str(response),
            "steps": [
                "Analyzed what is within and outside user's control",
                "Selected relevant Stoic principle",
                "Applied virtue ethics framework",
                "Provided practical Stoic exercise",
                "Offered perspective shift through Stoic lens",
                "Connected ancient wisdom to modern situation",
            ],
        }

    async def apply_stoic_principles(self, intake_data: dict[str, Any]) -> dict[str, Any]:
        """Apply Stoic principles to validated user input."""
        # Prepare input for Stoic processing
        stoic_input = {
            "thought_data": intake_data,
            "focus": "AvPD-sensitive Stoic wisdom",
            "virtue_emphasis": "character over outcomes",
            "principle_priority": self._determine_stoic_priority(intake_data),
        }

        return await self.process_with_transparency(stoic_input)

    def _determine_stoic_priority(self, intake_data: dict[str, Any]) -> str:
        """Determine which Stoic principle to prioritize based on the situation."""
        thought = intake_data.get("original_thought", "").lower()
        categories = intake_data.get("thought_categories", [])

        # Control issues - Dichotomy of Control
        if any(cat in categories for cat in ["control", "validation", "need"]):
            return "dichotomy_of_control_priority"

        # Future anxiety - Negative Visualization
        if (
            any(cat in categories for cat in ["future", "anxiety", "worry"])
            and "what if" in thought
        ):
            return "negative_visualization_priority"

        # Lack of perspective - View from Above
        if any(cat in categories for cat in ["catastrophizing", "perspective", "overwhelming"]):
            return "cosmic_perspective_priority"

        # Past rumination - Present Moment
        if any(cat in categories for cat in ["past", "rumination", "regret"]):
            return "present_moment_priority"

        # Victim mindset - Amor Fati
        if any(cat in categories for cat in ["pattern", "victimhood", "unfair"]):
            return "amor_fati_priority"

        # Default to Virtue Ethics
        return "virtue_ethics_priority"

    def select_stoic_principle(self, thought: str, categories: list[str]) -> str:
        """Select the most appropriate Stoic principle based on thought content."""
        thought_lower = thought.lower()

        # Dichotomy of Control for validation/control needs
        if any(
            phrase in thought_lower for phrase in ["need", "must", "have to", "everyone"]
        ) and any(cat in categories for cat in ["control", "validation"]):
            return "Dichotomy of Control"

        # Negative Visualization for future anxiety
        if "what if" in thought_lower or any(cat in categories for cat in ["future", "anxiety"]):
            return "Negative Visualization"

        # View from Above for catastrophizing
        if any(cat in categories for cat in ["catastrophizing", "perspective", "overwhelming"]):
            return "View from Above"

        # Present Moment for past/future focus
        if any(cat in categories for cat in ["past", "rumination"]):
            return "Present Moment Focus"

        # Amor Fati for patterns of suffering
        if any(phrase in thought_lower for phrase in ["always", "never", "why me"]) or any(
            cat in categories for cat in ["pattern", "victimhood"]
        ):
            return "Amor Fati"

        # Default to Virtue Ethics
        return "Virtue Ethics"

    def get_avpd_specific_stoic_techniques(self) -> list[str]:
        """Return Stoic techniques particularly effective for AvPD."""
        return [
            "Dichotomy of Control: Others' opinions are outside your control",
            "Virtue Focus: Courage in attempting social connection matters more than outcome",
            "Negative Visualization: Prepare for rejection while maintaining composure",
            "View from Above: This awkward moment is tiny in the cosmic scope",
            "Amor Fati: Each rejection teaches resilience",
            "Present Moment: Past embarrassments have no power in the now",
            "Preferred Indifferents: Social approval is nice but not necessary for virtue",
            "Stoic Role Models: Even Marcus Aurelius faced criticism",
            "Reserve Clause: 'I will attend the event, fate permitting'",
            "Evening Reflection: Review where you acted virtuously today",
        ]
