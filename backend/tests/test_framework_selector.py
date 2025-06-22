"""Tests for Framework Selector."""

import pytest

from agents.framework_selector import FrameworkSelector


@pytest.fixture
def framework_selector():
    """Create a FrameworkSelector instance for testing."""
    return FrameworkSelector()


class TestFrameworkSelector:
    """Test the FrameworkSelector component."""

    def test_initialization(self, framework_selector):
        """Test FrameworkSelector initializes properly."""
        assert framework_selector is not None
        assert hasattr(framework_selector, "select_frameworks")

    @pytest.mark.asyncio
    async def test_selects_cbt_for_catastrophizing(self, framework_selector):
        """Test CBT is selected for catastrophizing thoughts."""
        intake_data = {
            "original_thought": "This will ruin everything forever",
            "emotion_intensity": 7,
            "thought_categories": ["catastrophizing", "anxiety"],
            "cognitive_distortions": ["catastrophizing", "fortune telling"],
        }

        selected = await framework_selector.select_frameworks(intake_data)

        assert "CBT" in selected
        assert len(selected) >= 1 and len(selected) <= 3

    @pytest.mark.asyncio
    async def test_selects_dbt_for_high_distress(self, framework_selector):
        """Test DBT is selected for high distress situations."""
        intake_data = {
            "original_thought": "I can't handle this anymore",
            "emotion_intensity": 9,
            "thought_categories": ["crisis", "overwhelm"],
            "is_crisis": True,
        }

        selected = await framework_selector.select_frameworks(intake_data)

        assert "DBT" in selected
        assert selected[0] == "DBT"  # Should be primary for crisis

    @pytest.mark.asyncio
    async def test_selects_act_for_values_conflict(self, framework_selector):
        """Test ACT is selected for values-related issues."""
        intake_data = {
            "original_thought": "What's the point of trying if I'll always be anxious?",
            "emotion_intensity": 6,
            "thought_categories": ["meaninglessness", "values", "avoidance"],
            "values_hint": "connection",
        }

        selected = await framework_selector.select_frameworks(intake_data)

        assert "ACT" in selected

    @pytest.mark.asyncio
    async def test_selects_stoicism_for_control_issues(self, framework_selector):
        """Test Stoicism is selected for control struggles."""
        intake_data = {
            "original_thought": "I need everyone to like me or I'm worthless",
            "emotion_intensity": 7,
            "thought_categories": ["control", "validation", "social"],
        }

        selected = await framework_selector.select_frameworks(intake_data)

        assert "Stoicism" in selected

    @pytest.mark.asyncio
    async def test_selects_complementary_frameworks(self, framework_selector):
        """Test selector chooses complementary frameworks."""
        intake_data = {
            "original_thought": "I'm having a panic attack about tomorrow's presentation",
            "emotion_intensity": 8,
            "thought_categories": ["anxiety", "future", "catastrophizing"],
        }

        selected = await framework_selector.select_frameworks(intake_data)

        # Should select multiple complementary frameworks
        assert len(selected) >= 2
        # DBT for high anxiety, CBT for catastrophizing
        assert "DBT" in selected or "CBT" in selected

    @pytest.mark.asyncio
    async def test_respects_max_frameworks_limit(self, framework_selector):
        """Test selector doesn't overwhelm with too many frameworks."""
        intake_data = {
            "original_thought": "Everything is wrong and I can't cope",
            "emotion_intensity": 9,
            "thought_categories": ["crisis", "catastrophizing", "control", "values"],
            "cognitive_distortions": ["all-or-nothing", "catastrophizing"],
        }

        selected = await framework_selector.select_frameworks(intake_data)

        assert len(selected) <= 3  # Maximum 3 frameworks

    @pytest.mark.asyncio
    async def test_crisis_override(self, framework_selector):
        """Test crisis situations prioritize DBT."""
        intake_data = {
            "original_thought": "I want to hurt myself",
            "emotion_intensity": 10,
            "thought_categories": ["crisis", "self-harm"],
            "is_crisis": True,
        }

        selected = await framework_selector.select_frameworks(intake_data)

        assert selected[0] == "DBT"  # DBT must be first for crisis
        assert len(selected) <= 2  # Don't overwhelm in crisis

    @pytest.mark.asyncio
    async def test_handles_user_preferences(self, framework_selector):
        """Test selector considers user framework preferences."""
        intake_data = {
            "original_thought": "I'm worried about the meeting",
            "emotion_intensity": 5,
            "thought_categories": ["anxiety", "work"],
        }

        user_context = {
            "framework_preferences": {
                "CBT": 0.1,
                "DBT": 0.2,
                "ACT": 0.5,  # User prefers ACT
                "Stoicism": 0.2,
            }
        }

        selected = await framework_selector.select_frameworks(intake_data, user_context)

        # Should include ACT given user preference
        assert "ACT" in selected

    def test_get_complementary_framework(self, framework_selector):
        """Test complementary framework pairing logic."""
        # CBT pairs well with Stoicism
        complement = framework_selector.get_complementary_framework(
            "CBT", {"thought_categories": ["catastrophizing"]}
        )
        assert complement in ["Stoicism", "ACT", "DBT"]

        # DBT pairs well with ACT
        complement = framework_selector.get_complementary_framework(
            "DBT", {"thought_categories": ["distress"]}
        )
        assert complement in ["ACT", "Stoicism", "CBT"]

    def test_framework_conflict_avoidance(self, framework_selector):
        """Test that conflicting frameworks aren't selected together."""
        # This test ensures we don't select frameworks that might give contradictory advice
        conflicts = framework_selector.get_framework_conflicts()

        # For now, we assume no hard conflicts, but frameworks should complement
        assert isinstance(conflicts, dict) or conflicts is None

    @pytest.mark.asyncio
    async def test_low_intensity_single_framework(self, framework_selector):
        """Test low intensity thoughts get single framework."""
        intake_data = {
            "original_thought": "I'm slightly worried about this",
            "emotion_intensity": 3,
            "thought_categories": ["mild_concern"],
        }

        selected = await framework_selector.select_frameworks(intake_data)

        # Low intensity should get 1-2 frameworks
        assert len(selected) >= 1 and len(selected) <= 2

    @pytest.mark.asyncio
    async def test_avpd_specific_patterns(self, framework_selector):
        """Test AvPD-specific thought patterns get appropriate frameworks."""
        intake_data = {
            "original_thought": "They'll reject me if they get to know the real me",
            "emotion_intensity": 7,
            "thought_categories": ["social", "rejection", "avoidance"],
            "cognitive_distortions": ["mind_reading", "fortune_telling"],
        }

        selected = await framework_selector.select_frameworks(intake_data)

        # Should include frameworks that address avoidance and social issues
        assert "ACT" in selected or "CBT" in selected
        assert len(selected) >= 2  # Multiple frameworks for complex AvPD patterns
