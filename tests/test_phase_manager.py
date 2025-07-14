"""Tests for Phase Manager."""

from src.agents.phase_manager import (
    PHASE_TRANSITIONS,
    ConversationPhase,
    PhaseManager,
    check_phase_transition,
    create_phase_aware_agent,
    get_current_phase_info,
)
from src.knowledge.cbt_context import BASE_CBT_CONTEXT


class TestConversationPhase:
    """Test the ConversationPhase enum."""

    def test_phase_values(self):
        """Test that phases have correct values."""
        assert ConversationPhase.GREETING.value == "greeting"
        assert ConversationPhase.DISCOVERY.value == "discovery"
        assert ConversationPhase.REFRAMING.value == "reframing"
        assert ConversationPhase.SUMMARY.value == "summary"

    def test_all_phases_defined(self):
        """Test that all expected phases are defined."""
        phases = list(ConversationPhase)
        assert len(phases) == 4
        expected_values = {"greeting", "discovery", "reframing", "summary"}
        actual_values = {phase.value for phase in phases}
        assert actual_values == expected_values


class TestPhaseTransitions:
    """Test phase transition rules."""

    def test_greeting_transitions(self):
        """Test transitions from greeting phase."""
        assert PHASE_TRANSITIONS[ConversationPhase.GREETING] == [
            ConversationPhase.DISCOVERY
        ]

    def test_discovery_transitions(self):
        """Test transitions from discovery phase."""
        assert PHASE_TRANSITIONS[ConversationPhase.DISCOVERY] == [
            ConversationPhase.REFRAMING
        ]

    def test_reframing_transitions(self):
        """Test transitions from reframing phase."""
        assert PHASE_TRANSITIONS[ConversationPhase.REFRAMING] == [
            ConversationPhase.SUMMARY
        ]

    def test_summary_is_terminal(self):
        """Test that summary phase has no transitions."""
        assert PHASE_TRANSITIONS[ConversationPhase.SUMMARY] == []


class TestPhaseManager:
    """Test the PhaseManager class."""

    def test_get_current_phase_default(self):
        """Test getting current phase with empty state."""
        state = {}
        phase = PhaseManager.get_current_phase(state)
        assert phase == ConversationPhase.GREETING

    def test_get_current_phase_from_state(self):
        """Test getting current phase from state."""
        state = {"phase": "discovery"}
        phase = PhaseManager.get_current_phase(state)
        assert phase == ConversationPhase.DISCOVERY

    def test_get_current_phase_invalid(self):
        """Test getting current phase with invalid value."""
        state = {"phase": "invalid_phase"}
        phase = PhaseManager.get_current_phase(state)
        assert phase == ConversationPhase.GREETING  # Defaults to greeting

    def test_can_transition_valid(self):
        """Test valid phase transitions."""
        assert PhaseManager.can_transition_to(
            ConversationPhase.GREETING, ConversationPhase.DISCOVERY
        )
        assert PhaseManager.can_transition_to(
            ConversationPhase.DISCOVERY, ConversationPhase.REFRAMING
        )
        assert PhaseManager.can_transition_to(
            ConversationPhase.REFRAMING, ConversationPhase.SUMMARY
        )

    def test_can_transition_invalid(self):
        """Test invalid phase transitions."""
        # Cannot skip phases
        assert not PhaseManager.can_transition_to(
            ConversationPhase.GREETING, ConversationPhase.REFRAMING
        )
        assert not PhaseManager.can_transition_to(
            ConversationPhase.GREETING, ConversationPhase.SUMMARY
        )
        # Cannot go backwards
        assert not PhaseManager.can_transition_to(
            ConversationPhase.DISCOVERY, ConversationPhase.GREETING
        )
        # Cannot transition from summary
        assert not PhaseManager.can_transition_to(
            ConversationPhase.SUMMARY, ConversationPhase.GREETING
        )

    def test_get_phase_instruction(self):
        """Test getting phase instructions."""
        greeting_instruction = PhaseManager.get_phase_instruction(
            ConversationPhase.GREETING
        )
        assert "GREETING phase" in greeting_instruction
        assert "Welcome the user" in greeting_instruction

        discovery_instruction = PhaseManager.get_phase_instruction(
            ConversationPhase.DISCOVERY
        )
        assert "DISCOVERY phase" in discovery_instruction
        assert "explore their thoughts" in discovery_instruction

        reframing_instruction = PhaseManager.get_phase_instruction(
            ConversationPhase.REFRAMING
        )
        assert "REFRAMING phase" in reframing_instruction
        assert "cognitive distortions" in reframing_instruction

        summary_instruction = PhaseManager.get_phase_instruction(
            ConversationPhase.SUMMARY
        )
        assert "SUMMARY phase" in summary_instruction
        assert "Summarize the key insights" in summary_instruction


class TestPhaseManagementTools:
    """Test the phase management tool functions."""

    def test_check_phase_transition_valid(self):
        """Test check_phase_transition with valid phase."""
        result = check_phase_transition("discovery")
        assert result["status"] == "success"
        assert "Ready to transition" in result["message"]
        assert result["target_phase"] == "discovery"

    def test_check_phase_transition_invalid(self):
        """Test check_phase_transition with invalid phase."""
        result = check_phase_transition("invalid_phase")
        assert result["status"] == "error"
        assert "Invalid phase" in result["message"]
        assert "greeting" in result["message"]  # Should list valid phases

    def test_check_phase_transition_all_valid_phases(self):
        """Test that all valid phases are accepted."""
        valid_phases = ["greeting", "discovery", "reframing", "summary"]
        for phase in valid_phases:
            result = check_phase_transition(phase)
            assert result["status"] == "success"
            assert result["target_phase"] == phase

    def test_get_current_phase_info_structure(self):
        """Test get_current_phase_info returns correct structure."""
        result = get_current_phase_info()
        assert result["status"] == "success"
        assert "phase_flow" in result
        assert "message" in result

        # Check all phases are documented
        phase_flow = result["phase_flow"]
        assert set(phase_flow.keys()) == {
            "greeting",
            "discovery",
            "reframing",
            "summary",
        }

        # Check each phase has required fields
        for _phase, info in phase_flow.items():
            assert "description" in info
            assert "next_phases" in info
            assert isinstance(info["next_phases"], list)

    def test_get_current_phase_info_transitions(self):
        """Test that phase_flow matches PHASE_TRANSITIONS."""
        result = get_current_phase_info()
        phase_flow = result["phase_flow"]

        assert phase_flow["greeting"]["next_phases"] == ["discovery"]
        assert phase_flow["discovery"]["next_phases"] == ["reframing"]
        assert phase_flow["reframing"]["next_phases"] == ["summary"]
        assert phase_flow["summary"]["next_phases"] == []


class TestPhaseAwareAgent:
    """Test the phase-aware agent creation."""

    def test_create_phase_aware_agent_default(self):
        """Test creating phase-aware agent with defaults."""
        agent = create_phase_aware_agent()
        assert agent.name == "PhaseAwareCBTAssistant"
        assert agent.model == "gemini-2.0-flash"
        assert BASE_CBT_CONTEXT in agent.instruction
        assert "Conversation Phase Management" in agent.instruction

    def test_create_phase_aware_agent_custom_model(self):
        """Test creating phase-aware agent with custom model."""
        agent = create_phase_aware_agent(model="gemini-1.5-pro")
        assert agent.model == "gemini-1.5-pro"

    def test_create_phase_aware_agent_with_phase(self):
        """Test creating phase-aware agent with specific phase."""
        agent = create_phase_aware_agent(phase=ConversationPhase.DISCOVERY)
        instruction = agent.instruction
        assert "DISCOVERY phase" in instruction
        assert "explore their thoughts" in instruction

    def test_phase_aware_agent_has_tools(self):
        """Test that phase-aware agent has phase management tools."""
        agent = create_phase_aware_agent()
        assert len(agent.tools) == 2
        # The tools should be the functions we defined
        tool_names = [tool.__name__ for tool in agent.tools]
        assert "check_phase_transition" in tool_names
        assert "get_current_phase_info" in tool_names

    def test_phase_aware_agent_instruction_content(self):
        """Test that phase-aware agent has complete instructions."""
        agent = create_phase_aware_agent()
        instruction = agent.instruction

        # Should have CBT context
        assert "cognitive reframing" in instruction.lower()

        # Should have phase management section
        assert "Conversation Phase Management" in instruction
        assert "1. GREETING" in instruction
        assert "2. DISCOVERY" in instruction
        assert "3. REFRAMING" in instruction
        assert "4. SUMMARY" in instruction

        # Should have phase rules
        assert "follow the phases in order" in instruction
        assert "cannot skip ahead" in instruction

        # Should have session state info
        assert "Session State" in instruction
        assert "Current phase" in instruction
