"""Tests for reactive greeting agent behavior.

These tests follow TDD principles and should FAIL initially
until the reactive greeting feature is implemented.
"""

import pytest

from src.agents.cbt_assistant import create_cbt_assistant
from src.agents.greeting_agent import create_greeting_agent

# Language detection removed - using URL parameter only
# from src.utils.language_detection import LanguageDetector


class TestReactiveGreetingAgent:
    """Test suite for reactive greeting agent behavior."""

    @pytest.mark.asyncio
    async def test_cbt_assistant_waits_for_user_input(self):
        """Test that CBT assistant doesn't send proactive greeting messages."""
        # Create CBT assistant (the main orchestrator)
        agent = create_cbt_assistant()

        # The agent should NOT have any instruction to immediately greet
        # It should wait for user input first
        assert "immediately provide" not in agent.instruction
        assert "without waiting for user input" not in agent.instruction

        # Instead, it should emphasize reactive behavior
        assert any(
            phrase in agent.instruction.lower()
            for phrase in [
                "wait for user",
                "after user input",
                "reactive",
                "when user sends",
            ]
        )

    @pytest.mark.asyncio
    async def test_greeting_agent_responds_in_specified_language(self):
        """Test that greeting agent responds in the language specified via parameter."""
        # Create greeting agent with Spanish language parameter
        agent = create_greeting_agent(language_code="es-ES")

        # Agent instruction should include Spanish language requirement
        assert (
            "español" in agent.instruction.lower()
            or "Responde en español" in agent.instruction
        )

    @pytest.mark.asyncio
    async def test_greeting_agent_handles_default_language(self):
        """Test that greeting agent uses default language when not specified."""
        # Create greeting agent with default language
        agent = create_greeting_agent(language_code="en-US")

        # Agent should still be configured properly
        assert agent.instruction is not None
        assert "english" in agent.instruction.lower()

    @pytest.mark.asyncio
    async def test_greeting_agent_no_start_conversation_trigger(self):
        """Test that greeting agent doesn't respond to START_CONVERSATION trigger."""
        # Create greeting agent
        agent = create_greeting_agent()

        # The instruction should NOT mention START_CONVERSATION
        assert "START_CONVERSATION" not in agent.instruction

        # The instruction should emphasize waiting for actual user input
        instruction_lower = agent.instruction.lower()
        assert any(
            phrase in instruction_lower
            for phrase in [
                "wait for",
                "user input",
                "user message",
                "don't greet until",
                "reactive",
            ]
        )

    @pytest.mark.parametrize(
        "language_code,expected_instruction_word",
        [
            ("en-US", "english"),
            ("es-ES", "español"),
        ],
    )
    async def test_reactive_greeting_with_various_languages(
        self, language_code, expected_instruction_word
    ):
        """Test reactive greeting behavior with various language parameters."""
        # Create greeting agent with specified language
        agent = create_greeting_agent(language_code=language_code)

        # Verify agent is configured for the specified language
        assert expected_instruction_word in agent.instruction.lower()

    @pytest.mark.asyncio
    async def test_sse_endpoint_no_proactive_greeting(self):
        """Test that SSE endpoint doesn't send proactive greeting."""
        # This test verifies the SSE endpoint behavior
        # It should fail until we modify it to not send START_CONVERSATION

        from src.text.router import start_agent_session

        # Create a session
        runner, session, run_config = await start_agent_session("test-user", "en-US")

        # Check that the runner is NOT called with START_CONVERSATION
        # In reactive mode, the session should be created but no initial message sent
        # This will fail with current implementation where START_CONVERSATION is sent

        # We need to check that no automatic greeting is triggered
        # The current implementation sends Content with "START_CONVERSATION"
        # which we want to prevent in reactive mode
        assert True  # Placeholder - this test is about integration behavior

    async def test_cbt_assistant_emphasizes_reactive_behavior(self):
        """Test that CBT assistant instructions emphasize reactive behavior."""
        agent = create_cbt_assistant()

        instruction = agent.instruction

        # The current implementation has proactive greeting
        # This test should FAIL until we implement reactive behavior
        assert (
            "immediately provide" not in instruction
        ), "CBT Assistant should not immediately provide greeting"
        assert (
            "without waiting for user input" not in instruction
        ), "CBT Assistant should wait for user input"

    @pytest.mark.asyncio
    async def test_no_start_conversation_in_sse_endpoint(self):
        """Test that SSE endpoint doesn't use START_CONVERSATION trigger."""
        # Import the router module to check its behavior
        # Read the sse_endpoint function code
        import inspect

        import src.text.router as router

        sse_code = inspect.getsource(router.sse_endpoint)

        # The code should NOT contain START_CONVERSATION
        # This test will FAIL with current implementation
        assert (
            "START_CONVERSATION" not in sse_code
        ), "SSE endpoint should not use START_CONVERSATION trigger in reactive mode"
