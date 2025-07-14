"""Tests for CBT Knowledge Tool."""

import pytest

from src.tools.cbt_knowledge_tool import (
    get_agent_prompt_for_phase,
    get_phase_tools,
    query_cbt_knowledge,
)


class TestQueryCBTKnowledge:
    """Test the query_cbt_knowledge function."""

    @pytest.mark.asyncio
    async def test_distortion_info_query_success(self):
        """Test successful distortion info query."""
        result = await query_cbt_knowledge("distortion_info", "MW")
        assert result["status"] == "success"
        assert "distortion" in result
        assert result["distortion"]["code"] == "MW"
        assert result["distortion"]["name"] == "Mind Reading"

    @pytest.mark.asyncio
    async def test_distortion_info_query_missing_code(self):
        """Test distortion info query without distortion code."""
        result = await query_cbt_knowledge("distortion_info")
        assert result["status"] == "error"
        assert "distortion_code required" in result["error"]

    @pytest.mark.asyncio
    async def test_distortion_info_query_invalid_code(self):
        """Test distortion info query with invalid code."""
        result = await query_cbt_knowledge("distortion_info", "XX")
        assert result["status"] == "error"
        assert "Unknown distortion code" in result["error"]

    @pytest.mark.asyncio
    async def test_distortion_info_case_insensitive(self):
        """Test distortion codes are case-insensitive."""
        result = await query_cbt_knowledge("distortion_info", "mw")
        assert result["status"] == "success"
        assert result["distortion"]["code"] == "MW"

    @pytest.mark.asyncio
    async def test_all_distortions_query(self):
        """Test querying all distortions."""
        result = await query_cbt_knowledge("all_distortions")
        assert result["status"] == "success"
        assert "distortions" in result
        assert isinstance(result["distortions"], list)
        assert len(result["distortions"]) == 10

        # Check structure of each distortion
        for distortion in result["distortions"]:
            assert "code" in distortion
            assert "name" in distortion
            assert "definition" in distortion

    @pytest.mark.asyncio
    async def test_reframing_strategies_general(self):
        """Test querying general reframing strategies."""
        result = await query_cbt_knowledge("reframing_strategies")
        assert result["status"] == "success"
        assert "strategies" in result
        assert "techniques" in result["strategies"]
        assert "principles" in result["strategies"]

    @pytest.mark.asyncio
    async def test_reframing_strategies_specific_distortion(self):
        """Test querying reframing strategies for specific distortion."""
        result = await query_cbt_knowledge("reframing_strategies", "FT")
        assert result["status"] == "success"
        assert "distortion" in result
        assert result["distortion"] == "Fortune Telling"
        assert "strategies" in result
        assert isinstance(result["strategies"], list)
        assert len(result["strategies"]) >= 3

    @pytest.mark.asyncio
    async def test_micro_actions_general(self):
        """Test querying general micro-action principles."""
        result = await query_cbt_knowledge("micro_actions")
        assert result["status"] == "success"
        assert "principles" in result
        assert "duration" in result["principles"]
        assert "specific" in result["principles"]

    @pytest.mark.asyncio
    async def test_micro_actions_specific_distortion(self):
        """Test querying micro-actions for specific distortion."""
        result = await query_cbt_knowledge("micro_actions", "CT")
        assert result["status"] == "success"
        assert "distortion" in result
        assert result["distortion"] == "Catastrophizing"
        assert "micro_actions" in result
        assert isinstance(result["micro_actions"], list)
        assert len(result["micro_actions"]) >= 2

    @pytest.mark.asyncio
    async def test_evidence_gathering_query(self):
        """Test querying evidence gathering techniques."""
        result = await query_cbt_knowledge("evidence_gathering")
        assert result["status"] == "success"
        assert "techniques" in result
        assert "techniques" in result["techniques"]
        assert "principles" in result["techniques"]

    @pytest.mark.asyncio
    async def test_therapeutic_principles_query(self):
        """Test querying therapeutic principles."""
        result = await query_cbt_knowledge("therapeutic_principles")
        assert result["status"] == "success"
        assert "principles" in result
        assert "collaborative_empiricism" in result["principles"]
        assert "self_efficacy" in result["principles"]

    @pytest.mark.asyncio
    async def test_balanced_thought_criteria_query(self):
        """Test querying balanced thought criteria."""
        result = await query_cbt_knowledge("balanced_thought_criteria")
        assert result["status"] == "success"
        assert "criteria" in result
        assert "believable" in result["criteria"]
        assert "evidence_based" in result["criteria"]

    @pytest.mark.asyncio
    async def test_cbt_model_query(self):
        """Test querying CBT model."""
        result = await query_cbt_knowledge("cbt_model")
        assert result["status"] == "success"
        assert "model" in result
        assert "components" in result["model"]
        assert "description" in result["model"]
        assert "flow" in result["model"]

    @pytest.mark.asyncio
    async def test_invalid_query_type(self):
        """Test invalid query type returns error with valid types."""
        result = await query_cbt_knowledge("invalid_query")
        assert result["status"] == "error"
        assert "Unknown query_type" in result["error"]
        assert "valid_types" in result
        assert isinstance(result["valid_types"], list)
        assert "distortion_info" in result["valid_types"]
        assert "all_distortions" in result["valid_types"]


class TestGetAgentPromptForPhase:
    """Test the get_agent_prompt_for_phase function."""

    def test_valid_phases(self):
        """Test valid phase names return appropriate prompts."""
        # Phases with existing prompt files
        phases_with_prompts = ["discovery", "parser", "reframing", "summary"]
        for phase in phases_with_prompts:
            result = get_agent_prompt_for_phase(phase)
            assert isinstance(result, list)
            assert len(result) == 1  # Should contain the prompt file content
            assert isinstance(result[0], str)
            assert len(result[0]) > 0  # Content should not be empty

        # Greeting phase has no prompt file
        result = get_agent_prompt_for_phase("greeting")
        assert isinstance(result, list)
        assert result == []

    def test_invalid_phase(self):
        """Test invalid phase returns empty list."""
        result = get_agent_prompt_for_phase("invalid_phase")
        assert result == []

    def test_none_phase(self):
        """Test None phase returns empty list."""
        result = get_agent_prompt_for_phase(None)
        assert result == []


class TestGetPhaseTools:
    """Test the get_phase_tools function."""

    def test_greeting_phase_tools(self):
        """Test greeting phase has no tools."""
        tools = get_phase_tools("greeting")
        assert tools == []

    def test_discovery_phase_tools(self):
        """Test discovery phase has query_cbt_knowledge tool."""
        tools = get_phase_tools("discovery")
        assert "query_cbt_knowledge" in tools

    def test_parser_phase_tools(self):
        """Test parser phase has query_cbt_knowledge tool."""
        tools = get_phase_tools("parser")
        assert "query_cbt_knowledge" in tools

    def test_reframing_phase_tools(self):
        """Test reframing phase has query_cbt_knowledge tool."""
        tools = get_phase_tools("reframing")
        assert "query_cbt_knowledge" in tools

    def test_summary_phase_tools(self):
        """Test summary phase has no tools."""
        tools = get_phase_tools("summary")
        assert tools == []

    def test_invalid_phase_tools(self):
        """Test invalid phase returns empty list."""
        tools = get_phase_tools("invalid_phase")
        assert tools == []


class TestDistortionCodesCoverage:
    """Test that all distortion codes can be queried."""

    @pytest.mark.asyncio
    async def test_all_distortion_codes_queryable(self):
        """Test that all distortion codes from all_distortions can be queried individually."""
        # First get all distortions
        all_result = await query_cbt_knowledge("all_distortions")
        assert all_result["status"] == "success"

        # Then query each one individually
        for distortion in all_result["distortions"]:
            code = distortion["code"]
            individual_result = await query_cbt_knowledge("distortion_info", code)
            assert individual_result["status"] == "success"
            assert individual_result["distortion"]["code"] == code
            assert individual_result["distortion"]["name"] == distortion["name"]
