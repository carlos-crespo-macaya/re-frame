"""Tests for Multi-Framework Synthesis Agent."""

from unittest.mock import AsyncMock, Mock, patch

import google.generativeai as genai
import pytest

from agents.multi_framework_synthesis import MultiFrameworkSynthesisAgent


@pytest.fixture
def mock_genai_model():
    """Create a mock GenerativeModel."""
    mock_model = Mock(spec=genai.GenerativeModel)
    mock_model.generate_content_async = AsyncMock()
    return mock_model


@pytest.fixture
def synthesis_agent(mock_genai_model):
    """Create a MultiFrameworkSynthesisAgent instance for testing."""
    with patch("google.generativeai.GenerativeModel", return_value=mock_genai_model):
        return MultiFrameworkSynthesisAgent()


class TestMultiFrameworkSynthesisAgent:
    """Test the MultiFrameworkSynthesisAgent component."""

    def test_initialization(self, synthesis_agent):
        """Test MultiFrameworkSynthesisAgent initializes properly."""
        assert synthesis_agent is not None
        assert hasattr(synthesis_agent, "synthesize_responses")
        assert hasattr(synthesis_agent, "model")

    @pytest.mark.asyncio
    async def test_synthesizes_multiple_framework_outputs(self, synthesis_agent, mock_genai_model):
        """Test agent synthesizes multiple framework outputs cohesively."""
        framework_outputs = {
            "CBT": {
                "reasoning_path": [
                    "Identifying catastrophizing pattern",
                    "Examining evidence for/against",
                ],
                "reframed_thought": "I may feel anxious, but I can prepare and do my best",
                "techniques_applied": ["thought_challenging", "evidence_examination"],
            },
            "ACT": {
                "reasoning_path": [
                    "Acknowledging anxiety as normal",
                    "Focusing on values-based action",
                ],
                "reframed_thought": "I can feel anxious AND still take meaningful action",
                "techniques_applied": ["acceptance", "values_clarification"],
            },
        }

        mock_response = Mock()
        mock_response.text = """
        **Integrated Reframing:**
        While anxiety about the presentation is uncomfortable, it's a normal human experience that doesn't have to control your actions. The evidence shows you've prepared well, and even with anxiety present, you can choose to move forward with what matters to you.

        **Combined Techniques:**
        - Thought Challenging (CBT): Examined catastrophic predictions
        - Acceptance (ACT): Acknowledged anxiety without fighting it
        - Values-Based Action (ACT): Connected to your professional growth values

        **Reasoning Path:**
        1. Identified catastrophizing pattern about the presentation
        2. Examined actual evidence vs. anxious predictions
        3. Acknowledged that anxiety is normal and doesn't require elimination
        4. Connected the presentation to your values of professional growth
        5. Synthesized a both/and approach: feel anxious AND take action
        """
        mock_genai_model.generate_content_async.return_value = mock_response

        result = await synthesis_agent.synthesize_responses(
            framework_outputs,
            {
                "original_thought": "I'll completely fail the presentation and everyone will judge me"
            },
        )

        assert "integrated_reframing" in result
        assert "combined_techniques" in result
        assert "reasoning_path" in result
        assert len(result["reasoning_path"]) > 0

    @pytest.mark.asyncio
    async def test_handles_single_framework_gracefully(self, synthesis_agent, mock_genai_model):
        """Test agent handles single framework output without synthesis."""
        framework_outputs = {
            "DBT": {
                "reasoning_path": ["Applied distress tolerance"],
                "reframed_thought": "I can use TIPP to manage this crisis",
                "techniques_applied": ["TIPP", "radical_acceptance"],
            }
        }

        # With single framework, should return it directly formatted
        result = await synthesis_agent.synthesize_responses(
            framework_outputs, {"original_thought": "I can't handle this crisis"}
        )

        # Should still provide integrated format even with single framework
        assert "integrated_reframing" in result
        assert result["integrated_reframing"] == framework_outputs["DBT"]["reframed_thought"]

    @pytest.mark.asyncio
    async def test_preserves_crisis_prioritization(self, synthesis_agent, mock_genai_model):
        """Test synthesis preserves DBT crisis management as primary."""
        framework_outputs = {
            "DBT": {
                "reasoning_path": ["Crisis detected", "Applying TIPP"],
                "reframed_thought": "First: Use TIPP to regulate. Then we can examine thoughts.",
                "techniques_applied": ["TIPP", "distress_tolerance"],
                "is_crisis": True,
            },
            "CBT": {
                "reasoning_path": ["Identifying distortions"],
                "reframed_thought": "This situation is difficult but manageable",
                "techniques_applied": ["thought_challenging"],
            },
        }

        mock_response = Mock()
        mock_response.text = """
        **Integrated Reframing:**
        IMMEDIATE: Use TIPP skills to regulate your nervous system. Once you're more regulated, remember that while this situation is genuinely difficult, you have tools to manage it step by step.

        **Combined Techniques:**
        - TIPP (DBT): Temperature, Intense exercise, Paced breathing, Paired muscle relaxation
        - Distress Tolerance (DBT): Crisis survival skills
        - Thought Challenging (CBT): For use after stabilization

        **Reasoning Path:**
        1. Crisis detected - prioritizing immediate safety and regulation
        2. Applied TIPP for nervous system regulation
        3. Once regulated, gentle thought examination can follow
        """
        mock_genai_model.generate_content_async.return_value = mock_response

        result = await synthesis_agent.synthesize_responses(
            framework_outputs, {"original_thought": "I want to hurt myself", "is_crisis": True}
        )

        # Should maintain crisis prioritization
        assert "IMMEDIATE" in result["integrated_reframing"]
        assert "TIPP" in result["integrated_reframing"]

    @pytest.mark.asyncio
    async def test_handles_conflicting_approaches(self, synthesis_agent, mock_genai_model):
        """Test synthesis resolves potential conflicts between frameworks."""
        framework_outputs = {
            "CBT": {
                "reasoning_path": ["Challenge the thought"],
                "reframed_thought": "I should push through anxiety to prove it wrong",
                "techniques_applied": ["exposure"],
            },
            "ACT": {
                "reasoning_path": ["Accept the anxiety"],
                "reframed_thought": "I can make space for anxiety without fighting it",
                "techniques_applied": ["acceptance"],
            },
        }

        mock_response = Mock()
        mock_response.text = """
        **Integrated Reframing:**
        You can acknowledge anxiety without letting it control you. Rather than fighting it OR being controlled by it, you can notice it's there and still choose actions aligned with your values.

        **Combined Techniques:**
        - Acceptance (ACT): Making space for difficult emotions
        - Behavioral Activation (CBT): Taking valued action despite anxiety
        - Defusion (ACT): Seeing thoughts as thoughts, not commands

        **Reasoning Path:**
        1. Recognized the both/and nature: acceptance AND action
        2. Integrated exposure with willingness rather than white-knuckling
        3. Focused on values-based action rather than anxiety elimination
        """
        mock_genai_model.generate_content_async.return_value = mock_response

        result = await synthesis_agent.synthesize_responses(
            framework_outputs, {"original_thought": "I must avoid all anxiety-provoking situations"}
        )

        # Should integrate rather than contradict
        assert (
            "both/and" in result["reasoning_path"][0]
            or "acknowledge" in result["integrated_reframing"]
        )

    @pytest.mark.asyncio
    async def test_includes_all_framework_techniques(self, synthesis_agent, mock_genai_model):
        """Test synthesis includes techniques from all frameworks."""
        framework_outputs = {
            "CBT": {
                "techniques_applied": ["thought_challenging", "evidence_examination"],
            },
            "DBT": {
                "techniques_applied": ["opposite_action", "PLEASE"],
            },
            "Stoicism": {
                "techniques_applied": ["dichotomy_of_control", "negative_visualization"],
            },
        }

        mock_response = Mock()
        mock_response.text = """
        **Combined Techniques:**
        - Thought Challenging (CBT)
        - Evidence Examination (CBT)
        - Opposite Action (DBT)
        - PLEASE skills (DBT)
        - Dichotomy of Control (Stoicism)
        - Negative Visualization (Stoicism)
        """
        mock_genai_model.generate_content_async.return_value = mock_response

        result = await synthesis_agent.synthesize_responses(
            framework_outputs, {"original_thought": "Everything is terrible"}
        )

        # All techniques should be represented
        all_techniques = []
        for fw in framework_outputs.values():
            all_techniques.extend(fw["techniques_applied"])

        assert "combined_techniques" in result

    @pytest.mark.asyncio
    async def test_maintains_therapeutic_boundaries(self, synthesis_agent, mock_genai_model):
        """Test synthesis maintains appropriate therapeutic boundaries."""
        framework_outputs = {
            "DBT": {
                "reframed_thought": "This is hard AND I can cope",
            },
            "ACT": {
                "reframed_thought": "I can feel pain AND move toward what matters",
            },
        }

        mock_response = Mock()
        mock_response.text = """
        **Integrated Reframing:**
        This is genuinely difficult, AND you have strengths and tools to work with it. If you're in crisis, please reach out to professional support.

        **Disclaimer:**
        This is peer support, not therapy. For crisis support, contact 988 or emergency services.
        """
        mock_genai_model.generate_content_async.return_value = mock_response

        result = await synthesis_agent.synthesize_responses(
            framework_outputs, {"original_thought": "I can't go on", "emotion_intensity": 10}
        )

        # Should include appropriate boundaries/disclaimers
        assert "professional support" in result["integrated_reframing"] or "crisis" in result.get(
            "disclaimer", ""
        )

    @pytest.mark.asyncio
    async def test_handles_empty_framework_outputs(self, synthesis_agent):
        """Test synthesis handles empty framework outputs gracefully."""
        framework_outputs = {}

        result = await synthesis_agent.synthesize_responses(
            framework_outputs, {"original_thought": "I'm struggling"}
        )

        # Should return meaningful error or default
        assert result is not None
        assert "error" in result or "integrated_reframing" in result

    @pytest.mark.asyncio
    async def test_preserves_framework_attribution(self, synthesis_agent, mock_genai_model):
        """Test synthesis preserves which framework contributed what."""
        framework_outputs = {
            "CBT": {
                "reasoning_path": ["Identified all-or-nothing thinking"],
                "techniques_applied": ["cognitive_restructuring"],
            },
            "Stoicism": {
                "reasoning_path": ["Applied dichotomy of control"],
                "techniques_applied": ["dichotomy_of_control"],
            },
        }

        mock_response = Mock()
        mock_response.text = """
        **Framework Contributions:**
        - CBT: Identified all-or-nothing thinking pattern
        - Stoicism: Clarified what is/isn't in your control

        **Integrated Reframing:**
        While you can't control others' opinions (Stoicism), you can examine whether your predictions are based on facts or all-or-nothing thinking (CBT).
        """
        mock_genai_model.generate_content_async.return_value = mock_response

        result = await synthesis_agent.synthesize_responses(
            framework_outputs, {"original_thought": "Everyone hates me"}
        )

        # Should maintain framework attribution
        assert "framework_contributions" in result or "CBT" in result.get(
            "integrated_reframing", ""
        )

    @pytest.mark.asyncio
    async def test_respects_user_framework_effectiveness(self, synthesis_agent, mock_genai_model):
        """Test synthesis considers user's framework effectiveness history."""
        framework_outputs = {
            "CBT": {"reframed_thought": "Evidence doesn't support this"},
            "ACT": {"reframed_thought": "I can act despite this thought"},
        }

        user_context = {
            "framework_effectiveness": {
                "CBT": 0.3,  # Less effective for user
                "ACT": 0.8,  # More effective for user
            }
        }

        mock_response = Mock()
        mock_response.text = """
        **Integrated Reframing:**
        While examining evidence can be helpful, what matters most is that you can take meaningful action even when difficult thoughts arise. Your values can guide you forward.

        **Emphasis:**
        Prioritizing ACT approach based on what has worked best for you.
        """
        mock_genai_model.generate_content_async.return_value = mock_response

        result = await synthesis_agent.synthesize_responses(
            framework_outputs, {"original_thought": "I'm worthless"}, user_context
        )

        # Should emphasize more effective framework
        assert "values" in result["integrated_reframing"] or "ACT" in result.get("emphasis", "")

    def test_get_synthesis_priority(self, synthesis_agent):
        """Test framework priority ordering for synthesis."""
        # Crisis should prioritize DBT
        priority = synthesis_agent.get_synthesis_priority(
            {"DBT": {"is_crisis": True}, "CBT": {}}, {"is_crisis": True}
        )
        assert priority[0] == "DBT"

        # Non-crisis should balance frameworks
        priority = synthesis_agent.get_synthesis_priority(
            {"CBT": {}, "ACT": {}, "Stoicism": {}}, {"is_crisis": False}
        )
        assert len(priority) == 3

