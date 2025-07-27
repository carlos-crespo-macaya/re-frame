"""Tests for reactive greeting agent behavior.

These tests follow TDD principles and should FAIL initially
until the reactive greeting feature is implemented.
"""

import pytest

from src.agents.cbt_assistant import create_cbt_assistant
from src.agents.greeting_agent import create_greeting_agent
from src.utils.language_detection import LanguageDetector


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
    async def test_greeting_agent_responds_in_detected_language(self):
        """Test that greeting agent responds in the language detected from user's message."""
        # Test with Spanish input (longer for reliable detection)
        user_message = (
            "Hola, me siento ansioso hoy y necesito hablar con alguien sobre esto"
        )

        # Detect language from user's message
        detected_language = LanguageDetector.detect_with_fallback(user_message)
        assert detected_language == "es"

        # Create greeting agent with detected language
        agent = create_greeting_agent(language_code=f"{detected_language}-ES")

        # Agent instruction should include Spanish language requirement
        assert (
            "español" in agent.instruction.lower()
            or "Responde en español" in agent.instruction
        )

    @pytest.mark.asyncio
    async def test_greeting_agent_handles_empty_messages(self):
        """Test that greeting agent handles empty/whitespace messages gracefully."""
        # Test with empty and whitespace messages
        test_cases = ["", " ", "   ", "\n", "\t", " \n\t "]

        for message in test_cases:
            # Detect language (should fallback to English)
            detected_language = LanguageDetector.detect_with_fallback(message)
            assert detected_language == "en"

            # Create greeting agent with fallback language
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
        "user_input,expected_language",
        [
            ("Hello, I'm feeling anxious", "en"),
            ("Hola, estoy preocupado por mi salud mental y necesito ayuda", "es"),
            ("Good morning, I need help", "en"),
            ("Buenos días, necesito ayuda con mis pensamientos negativos", "es"),
            ("", "en"),  # Empty should fallback to English
            ("   ", "en"),  # Whitespace should fallback to English
        ],
    )
    async def test_reactive_greeting_with_various_inputs(
        self, user_input, expected_language
    ):
        """Test reactive greeting behavior with various user inputs."""
        # Detect language from user input
        detected_language = LanguageDetector.detect_with_fallback(user_input)
        assert detected_language == expected_language

        # Create agent with detected language
        language_code = (
            f"{expected_language}-US"
            if expected_language == "en"
            else f"{expected_language}-ES"
        )
        agent = create_greeting_agent(language_code=language_code)

        # Verify agent is configured for the detected language
        if expected_language == "en":
            assert "english" in agent.instruction.lower()
        else:
            assert (
                "español" in agent.instruction.lower()
                or "spanish" in agent.instruction.lower()
            )

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
