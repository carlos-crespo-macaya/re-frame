"""DBT Framework Agent for applying Dialectical Behavior Therapy techniques."""

from typing import Any

from .base import ReFrameAgent


class DBTFrameworkAgent(ReFrameAgent):
    """Agent responsible for applying DBT techniques to user thoughts."""

    INSTRUCTIONS = """You are a Dialectical Behavior Therapy (DBT) specialist working with individuals who have Avoidant Personality Disorder (AvPD).

Your role is to:
1. Assess the situation and emotion intensity to select the appropriate DBT module
2. Apply DBT techniques that balance acceptance AND change
3. Use dialectical thinking - holding two truths at once
4. Provide specific, actionable DBT skills
5. Always use "AND" instead of "BUT" to maintain dialectical balance

DBT Modules and when to use them:

1. DISTRESS TOLERANCE (for high distress, crisis, overwhelming emotions):
   - TIPP: Temperature, Intense exercise, Paced breathing, Paired muscle relaxation
   - ACCEPTS: Activities, Contributing, Comparisons, Emotions, Push away, Thoughts, Sensations
   - IMPROVE: Imagery, Meaning, Prayer, Relaxation, One thing, Vacation, Encouragement

2. EMOTION REGULATION (for understanding and managing emotions):
   - PLEASE: treat PhysicaL illness, balance Eating, avoid mood-Altering substances, balance Sleep, get Exercise
   - Check the Facts: Examine evidence for and against thoughts
   - Opposite Action: Act opposite to emotion urges when not justified

3. INTERPERSONAL EFFECTIVENESS (for relationship and communication challenges):
   - DEARMAN: Describe, Express, Assert, Reinforce, Mindful, Appear confident, Negotiate
   - GIVE: Gentle, Interested, Validate, Easy manner
   - FAST: Fair, Apologies (no over-apologizing), Stick to values, Truthful

4. MINDFULNESS (for rumination, being present):
   - Wise Mind: Balance emotion mind and reasonable mind
   - What Skills: Observe, Describe, Participate
   - How Skills: Non-judgmentally, One-mindfully, Effectively

Guidelines for AvPD:
- Start with validation and acceptance
- Introduce change strategies gently
- Adapt intensity to user's distress level
- Don't overwhelm with too many acronyms
- Focus on small, manageable steps
- Recognize when distress tolerance is needed over problem-solving

Output format:
{
    "module_used": "Distress Tolerance|Emotion Regulation|Interpersonal Effectiveness|Mindfulness",
    "technique": "specific DBT technique used",
    "acceptance_statement": "validation of their experience",
    "change_strategy": "specific skill or action to try",
    "wise_mind_reframe": "balanced perspective using AND",
    "skill_practice": "concrete step to practice the skill",
    "dialectical_synthesis": "integration of acceptance and change",
    "crisis_resources": "only if needed for high distress/crisis"
}

Remember: Always model dialectical thinking by using "AND" to join seemingly opposite truths."""

    def __init__(self) -> None:
        """Initialize the DBT Framework Agent."""
        super().__init__(name="DBTFrameworkAgent", instructions=self.INSTRUCTIONS)

    def _extract_reasoning_path(self, response: Any) -> dict[str, Any]:
        """Extract DBT reasoning for transparency."""
        return {
            "raw_response": str(response),
            "steps": [
                "Assessed emotion intensity and situation",
                "Selected appropriate DBT module",
                "Applied dialectical thinking (acceptance AND change)",
                "Chose specific DBT technique",
                "Created balanced reframe using Wise Mind",
                "Provided actionable skill practice",
            ],
        }

    async def apply_dbt_techniques(self, intake_data: dict[str, Any]) -> dict[str, Any]:
        """Apply DBT techniques to validated user input."""
        # Prepare input for DBT processing
        dbt_input = {
            "thought_data": intake_data,
            "focus": "AvPD-sensitive DBT application",
            "emotion_intensity": intake_data.get("emotion_intensity", 5),
            "dialectical_balance": "acceptance AND change",
            "priority": self._determine_dbt_priority(intake_data),
        }

        return await self.process_with_transparency(dbt_input)

    def _determine_dbt_priority(self, intake_data: dict[str, Any]) -> str:
        """Determine which DBT module to prioritize based on the situation."""
        emotion_intensity = intake_data.get("emotion_intensity", 5)
        categories = intake_data.get("thought_categories", [])

        # Crisis or very high distress - prioritize Distress Tolerance
        if emotion_intensity >= 9 or "crisis" in categories:
            return "distress_tolerance_priority"

        # Interpersonal issues - prioritize Interpersonal Effectiveness
        if any(cat in categories for cat in ["interpersonal", "relationship", "communication"]):
            return "interpersonal_effectiveness_priority"

        # Rumination or past-focused - prioritize Mindfulness
        if any(cat in categories for cat in ["rumination", "past", "worry"]):
            return "mindfulness_priority"

        # Default to Emotion Regulation for moderate distress
        return "emotion_regulation_priority"

    def select_dbt_module(self, intake_data: dict[str, Any]) -> str:
        """Select the most appropriate DBT module based on the situation."""
        emotion_intensity = intake_data.get("emotion_intensity", 5)
        thought = intake_data.get("original_thought", "").lower()

        # High distress situations
        if emotion_intensity >= 8 or any(
            word in thought for word in ["panic", "can't handle", "escape", "crisis"]
        ):
            return "Distress Tolerance"

        # Interpersonal situations
        if any(word in thought for word in ["boundaries", "ask", "relationship", "communicate"]):
            return "Interpersonal Effectiveness"

        # Rumination or mindfulness needs
        if any(word in thought for word in ["thinking about", "replaying", "can't stop"]):
            return "Mindfulness"

        # Default to Emotion Regulation
        return "Emotion Regulation"

    def get_avpd_specific_dbt_techniques(self) -> list[str]:
        """Return DBT techniques particularly effective for AvPD."""
        return [
            "Distress Tolerance: TIPP for social anxiety peaks",
            "Distress Tolerance: ACCEPTS for overwhelming social situations",
            "Emotion Regulation: Check the Facts for social assumptions",
            "Emotion Regulation: PLEASE for vulnerability factors",
            "Interpersonal Effectiveness: Gentle DEARMAN for boundaries",
            "Interpersonal Effectiveness: GIVE for maintaining relationships",
            "Interpersonal Effectiveness: FAST for self-respect",
            "Mindfulness: Wise Mind for balanced perspective",
            "Radical Acceptance of social anxiety while working on change",
            "Opposite Action for avoidance urges",
        ]
