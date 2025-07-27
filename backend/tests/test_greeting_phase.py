"""
Tests for the Greeting Phase implementation.

These tests verify that the greeting phase meets all acceptance criteria:
- Explains the 4-phase process
- Includes therapy disclaimer
- Has welcoming tone
- Transitions to discovery when acknowledged
"""

import pytest

from src.agents.greeting_agent import create_greeting_agent
from src.agents.phase_manager import ConversationPhase


class TestGreetingPhase:
    """Test suite for the greeting phase of the CBT assistant."""

    def test_greeting_agent_creation(self):
        """Test that greeting agent can be created successfully."""
        agent = create_greeting_agent()
        assert agent is not None
        assert agent.name == "GreetingAgent"
        # In reactive implementation, only phase transition tool
        assert len(agent.tools) == 1
        tool_names = [tool.__name__ for tool in agent.tools]
        assert "check_phase_transition" in tool_names
        # Language detection happens in router, not agent
        assert "detect_user_language" not in tool_names

    def test_greeting_explains_process(self):
        """Test that greeting explains the 4-phase process."""
        agent = create_greeting_agent()
        instruction = agent.instruction

        # Check for mention of 4 phases
        assert (
            "4-phase" in instruction or "4-step" in instruction or "four" in instruction
        )
        assert "cognitive reframing" in instruction.lower()

        # Check all phases are mentioned
        assert "greeting" in instruction.lower()
        assert "discovery" in instruction.lower()
        assert "reframing" in instruction.lower()
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

        # Check for transition instructions
        assert "check_phase_transition" in instruction
        assert "discovery" in instruction
        assert "ready" in instruction.lower()

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

        # Check for greeting phase specifics
        assert "GREETING phase" in instruction
        assert "Welcome the user warmly" in instruction
        assert "introduce yourself" in instruction

    def test_greeting_agent_tools(self):
        """Test that greeting agent has proper phase transition tools."""
        agent = create_greeting_agent()

        # In reactive implementation, only check_phase_transition tool
        assert len(agent.tools) == 1
        tool_names = [tool.__name__ for tool in agent.tools]
        assert "check_phase_transition" in tool_names
        # Language detection happens in router
        assert "detect_user_language" not in tool_names

        # Test check_phase_transition tool functionality
        check_tool = next(
            tool for tool in agent.tools if tool.__name__ == "check_phase_transition"
        )
        result = check_tool("discovery")
        assert isinstance(result, dict)
        assert result["status"] == "success"
        assert "discovery" in result["message"]

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
        session.state["phase"] = ConversationPhase.GREETING.value

        # Test greeting response
        # In a real integration test, we would create a message like:
        # message = Content(parts=[Part(text="Hello")], role="user")
        # and test the actual response
        # For now, we just verify the agent can be used with a runner
        assert runner is not None
        assert agent is not None

    def test_phase_manager_integration(self):
        """Test that greeting agent properly integrates with PhaseManager."""
        from src.agents.phase_manager import ConversationPhase, PhaseManager

        agent = create_greeting_agent()

        # Get phase instruction from PhaseManager
        phase_instruction = PhaseManager.get_phase_instruction(
            ConversationPhase.GREETING
        )

        # Verify it's included in agent instruction
        assert phase_instruction in agent.instruction

    def test_greeting_phase_transitions(self):
        """Test valid transitions from greeting phase."""
        from src.agents.phase_manager import (
            PHASE_TRANSITIONS,
            ConversationPhase,
            PhaseManager,
        )

        # Greeting should only transition to discovery
        valid_transitions = PHASE_TRANSITIONS[ConversationPhase.GREETING]
        assert len(valid_transitions) == 1
        assert ConversationPhase.DISCOVERY in valid_transitions

        # Test transition validation
        assert PhaseManager.can_transition_to(
            ConversationPhase.GREETING, ConversationPhase.DISCOVERY
        )
        assert not PhaseManager.can_transition_to(
            ConversationPhase.GREETING, ConversationPhase.REFRAMING
        )
        assert not PhaseManager.can_transition_to(
            ConversationPhase.GREETING, ConversationPhase.SUMMARY
        )
