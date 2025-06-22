"""Framework Selector for intelligent routing to therapeutic frameworks."""

from typing import Any


class FrameworkSelector:
    """Intelligently selects which therapeutic frameworks to apply based on user input."""

    def __init__(self):
        """Initialize the Framework Selector."""
        self.max_frameworks = 3  # Avoid overwhelming users
        self.crisis_threshold = 8  # Emotion intensity that triggers crisis mode

    async def select_frameworks(
        self, intake_data: dict[str, Any], user_context: dict[str, Any] | None = None
    ) -> list[str]:
        """
        Select the most appropriate framework(s) based on intake analysis.

        Args:
            intake_data: Analyzed thought data from intake agent
            user_context: Optional user preferences and history

        Returns:
            List of 1-3 framework names in priority order
        """
        selected_frameworks = []

        # Check for crisis first
        if self._is_crisis(intake_data):
            selected_frameworks.append("DBT")  # DBT always first for crisis

        # Analyze primary need
        primary = self._determine_primary_framework(intake_data)
        if primary and primary not in selected_frameworks:
            selected_frameworks.append(primary)

        # Add complementary framework if appropriate
        if len(selected_frameworks) < self.max_frameworks and selected_frameworks:
            secondary = self.get_complementary_framework(selected_frameworks[0], intake_data)
            if secondary and secondary not in selected_frameworks:
                selected_frameworks.append(secondary)

        # Consider user preferences
        if user_context and "framework_preferences" in user_context:
            selected_frameworks = self._apply_user_preferences(
                selected_frameworks, user_context["framework_preferences"], intake_data
            )

        # Ensure we have at least one framework
        if not selected_frameworks:
            selected_frameworks.append("CBT")  # Default fallback

        return selected_frameworks[: self.max_frameworks]

    def _is_crisis(self, intake_data: dict[str, Any]) -> bool:
        """Determine if this is a crisis situation requiring immediate DBT skills."""
        emotion_intensity = intake_data.get("emotion_intensity", 0)
        is_crisis_flag = intake_data.get("is_crisis", False)
        categories = intake_data.get("thought_categories", [])

        return (
            emotion_intensity >= self.crisis_threshold
            or is_crisis_flag
            or "crisis" in categories
            or "self-harm" in categories
        )

    def _determine_primary_framework(self, intake_data: dict[str, Any]) -> str | None:
        """Determine the primary framework based on thought patterns."""
        categories = intake_data.get("thought_categories", [])
        distortions = intake_data.get("cognitive_distortions", [])
        thought = intake_data.get("original_thought", "").lower()

        # CBT for cognitive distortions and catastrophizing
        if any(d in distortions for d in ["catastrophizing", "fortune telling", "mind reading"]):
            return "CBT"
        if "catastrophizing" in categories:
            return "CBT"

        # DBT for high emotional dysregulation
        if intake_data.get("emotion_intensity", 0) >= 7:
            if any(cat in categories for cat in ["overwhelm", "distress", "emotional"]):
                return "DBT"

        # ACT for values conflicts and avoidance
        if any(cat in categories for cat in ["values", "meaninglessness", "avoidance"]):
            return "ACT"
        if "what's the point" in thought or "why bother" in thought:
            return "ACT"

        # Stoicism for control issues and external validation
        if any(cat in categories for cat in ["control", "validation", "approval"]):
            return "Stoicism"
        if any(phrase in thought for phrase in ["need everyone", "must be liked", "have to"]):
            return "Stoicism"

        # Default based on emotion intensity
        emotion_intensity = intake_data.get("emotion_intensity", 5)
        if emotion_intensity >= 7:
            return "DBT"
        if emotion_intensity >= 5:
            return "CBT"
        return "Stoicism"

    def get_complementary_framework(
        self, primary: str, intake_data: dict[str, Any]
    ) -> str | None:
        """Select a complementary framework that pairs well with the primary."""
        categories = intake_data.get("thought_categories", [])

        complementary_pairs = {
            "CBT": {
                "catastrophizing": "Stoicism",  # Add perspective
                "social": "ACT",  # Add values focus
                "default": "Stoicism",
            },
            "DBT": {
                "values": "ACT",  # Values-based action after stabilization
                "control": "Stoicism",  # Acceptance of uncontrollables
                "default": "ACT",
            },
            "ACT": {
                "catastrophizing": "CBT",  # Thought work with values
                "crisis": "DBT",  # Skills for distress
                "default": "Stoicism",  # Virtue ethics aligns with values
            },
            "Stoicism": {
                "distress": "DBT",  # Practical skills
                "avoidance": "ACT",  # Values-based action
                "default": "CBT",
            },
        }

        # Find matching category
        framework_map = complementary_pairs.get(primary, {})
        for category in categories:
            if category in framework_map:
                return framework_map[category]

        return framework_map.get("default")

    def _apply_user_preferences(
        self,
        selected: list[str],
        preferences: dict[str, float],
        intake_data: dict[str, Any],
    ) -> list[str]:
        """Adjust framework selection based on user preferences."""
        # Don't override crisis selections
        if self._is_crisis(intake_data):
            return selected

        # Get preference scores for unselected frameworks
        unselected = [f for f in ["CBT", "DBT", "ACT", "Stoicism"] if f not in selected]

        # Check if any unselected framework has significantly higher preference
        for framework in unselected:
            pref_score = preferences.get(framework, 0.25)
            if pref_score > 0.4 and len(selected) < self.max_frameworks:
                selected.append(framework)

        # Re-sort by preference if user has strong preferences
        if max(preferences.values()) > 0.4:
            selected.sort(key=lambda f: preferences.get(f, 0.25), reverse=True)

        return selected

    def get_framework_conflicts(self) -> dict[str, list[str]] | None:
        """
        Return any framework pairs that might give conflicting advice.

        Currently, we assume all frameworks can complement each other
        when properly synthesized, so we return None.
        """
        # In future, we might identify specific conflicts
        # For now, our synthesis agent handles harmonization
        return None
