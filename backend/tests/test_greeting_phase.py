"""
Tests for the Warmup Phase implementation.

These tests verify that the warmup phase meets all acceptance criteria:
- Explains the cognitive reframing process
- Includes therapy disclaimer
- Has welcoming tone
- Transitions to clarify when acknowledged
"""

import pytest

from src.agents.greeting_agent import create_greeting_agent
from src.agents.state import Phase


class TestGreetingPhase:
    """Test suite for the greeting phase of the CBT assistant."""

    def test_greeting_agent_creation(self):
        """Test that greeting agent can be created successfully."""
        agent = create_greeting_agent()
        assert agent is not None
        assert agent.name == "GreetingAgent"
        # New architecture: no tools in individual agents
        assert len(agent.tools) == 0
        # Language detection happens in router, phase transitions in orchestrator

    def test_greeting_explains_process(self):
        """Test that greeting explains the cognitive reframing process."""
        agent = create_greeting_agent()
        instruction = agent.instruction

        # Check for cognitive reframing mention
        assert "cognitive reframing" in instruction.lower()

        # Check all phases are mentioned (new phase names)
        assert "warmup" in instruction.lower()
        assert "clarify" in instruction.lower()
        assert "reframe" in instruction.lower()
        assert "summary" in instruction.lower()

    def test_greeting_includes_disclaimer(self):
        """Test that greeting includes therapy disclaimer."""
        agent = create_greeting_agent()
        instruction = agent.instruction

        # Check for therapy disclaimer
        assert (
            "not replace professional therapy" in instruction
            or "not a replacement for professional therapy" in instruction
            or "isn't a replacement for professional therapy" in instruction
        )

    def test_greeting_is_welcoming(self):
        """Test that greeting has a welcoming tone."""
        agent = create_greeting_agent()
        instruction = agent.instruction

        # Check for welcoming language in instructions
        assert any(
            word in instruction.lower() for word in ["welcome", "hello", "warm", "glad"]
        )

        # Check for localized greetings section
        assert (
            "Localized Greetings" in instruction or "welcoming" in instruction.lower()
        )

    def test_greeting_transitions_on_acknowledgment(self):
        """Test that greeting mentions transition to discovery phase."""
        agent = create_greeting_agent()
        instruction = agent.instruction

        # Check for transition instructions (orchestrator handles transitions now)
        assert "ready" in instruction.lower()
        # Orchestrator handles transitions, so no phase transition tool needed

    def test_greeting_includes_cbt_context(self):
        """Test that greeting agent includes BASE_CBT_CONTEXT."""
        agent = create_greeting_agent()
        instruction = agent.instruction

        # Check for CBT context elements
        assert "Cognitive Behavioral Therapy" in instruction
        assert "evidence-based" in instruction
        assert "empathetic" in instruction

    def test_greeting_phase_specific_instructions(self):
        """Test that greeting has phase-specific instructions."""
        agent = create_greeting_agent()
        instruction = agent.instruction

        # Check for warmup phase specifics
        assert "WARMUP phase" in instruction
        assert (
            "Welcome the user warmly" in instruction
            or "welcome the user" in instruction.lower()
        )
        assert "introduce yourself" in instruction

    def test_greeting_agent_tools(self):
        """Test that greeting agent has no tools (orchestrator handles transitions)."""
        agent = create_greeting_agent()

        # New architecture: agents don't have phase management tools
        # The orchestrator handles all phase transitions
        assert len(agent.tools) == 0
        # Language detection happens in router, phase transitions in orchestrator

    def test_greeting_conciseness_instruction(self):
        """Test that greeting includes instruction to be concise."""
        agent = create_greeting_agent()
        instruction = agent.instruction

        # Check for conciseness guidance
        assert "concise" in instruction.lower()
        assert "3-4 sentences" in instruction

    def test_greeting_wait_for_acknowledgment(self):
        """Test that greeting waits for user acknowledgment before transitioning."""
        agent = create_greeting_agent()
        instruction = agent.instruction

        # Check for waiting instruction
        assert (
            "wait for user acknowledgment" in instruction.lower()
            or "user acknowledges" in instruction.lower()
        )

    @pytest.mark.asyncio
    async def test_greeting_agent_with_runner(self):
        """Test greeting agent with InMemoryRunner (integration test)."""
        from google.adk.runners import InMemoryRunner

        agent = create_greeting_agent()
        runner = InMemoryRunner(agent=agent)

        # Create session
        user_id = "test_user"
        session_id = "greeting_test"
        await runner.session_service.create_session(
            app_name=runner.app_name,
            user_id=user_id,
            session_id=session_id,
        )

        # Initialize session state
        session = await runner.session_service.get_session(
            app_name=runner.app_name,
            user_id=user_id,
            session_id=session_id,
        )
        session.state["phase"] = Phase.WARMUP.value

        # Test greeting response
        # In a real integration test, we would create a message like:
        # message = Content(parts=[Part(text="Hello")], role="user")
        # and test the actual response
        # For now, we just verify the agent can be used with a runner
        assert runner is not None
        assert agent is not None

    def test_phase_manager_integration(self):
        """Test that greeting agent properly integrates with new phase system."""
        agent = create_greeting_agent()

        # Verify warmup phase instruction is included
        assert "WARMUP phase" in agent.instruction
        assert "Welcome the user and explain the process" in agent.instruction

    def test_greeting_phase_transitions(self):
        """Test valid transitions from warmup phase."""
        from src.agents.state import PHASE_ORDER, Phase

        # Warmup should transition to clarify in the phase order
        warmup_index = PHASE_ORDER.index(Phase.WARMUP)
        next_phase = PHASE_ORDER[warmup_index + 1]
        assert next_phase == Phase.CLARIFY

        # Verify phase order integrity
        assert Phase.WARMUP in PHASE_ORDER
        assert Phase.CLARIFY in PHASE_ORDER
        assert Phase.REFRAME in PHASE_ORDER
        assert Phase.SUMMARY in PHASE_ORDER
