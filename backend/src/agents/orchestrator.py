"""
Orchestrator for managing conversation phases with Sequential Agents.

This module creates a sequential agent that routes conversations
to the appropriate phase-specific agents.
"""

from google.adk.agents import LlmAgent

from src.knowledge.cbt_context import (
    BASE_CBT_CONTEXT,
    CRISIS_INDICATORS,
    CRISIS_RESPONSE_TEMPLATE,
)


def check_for_crisis(user_input: str) -> dict:
    """
    Check if user input contains crisis indicators.

    Args:
        user_input: The user's message

    Returns:
        dict: Crisis check results
    """
    input_lower = user_input.lower()

    for indicator in CRISIS_INDICATORS:
        if indicator in input_lower:
            return {
                "crisis_detected": True,
                "response": CRISIS_RESPONSE_TEMPLATE,
                "action": "provide_support",
            }

    return {
        "crisis_detected": False,
        "action": "continue",
    }


def create_cbt_orchestrator(model: str = "gemini-2.0-flash") -> LlmAgent:
    """
    Create an orchestrator that manages the conversation flow through phases.

    Args:
        model: The Gemini model to use

    Returns:
        A SequentialAgent that routes to phase-specific agents
    """
    # Orchestrator instruction
    orchestrator_instruction = (
        BASE_CBT_CONTEXT
        + "\n\n## Orchestrator Role\n"
        + "You are the conversation orchestrator that routes user messages "
        + "to the appropriate phase-specific agent.\n\n"
        + "## Critical Safety Check\n"
        + "ALWAYS check for crisis indicators first using the check_for_crisis tool.\n"
        + "If a crisis is detected, immediately provide the crisis response "
        + "and do not continue with CBT exercises.\n\n"
        + "## Phase Routing\n"
        + "Based on the current phase in session state, route to:\n"
        + "- GREETING → GreetingAgent\n"
        + "- DISCOVERY → DiscoveryAgent\n"
        + "- REFRAMING → ReframingAgent\n"
        + "- SUMMARY → SummaryAgent\n\n"
        + "## Session State\n"
        + "The session state tracks:\n"
        + "- phase: Current conversation phase\n"
        + "- automatic_thought: The thought being worked on\n"
        + "- emotion_data: Captured emotions and intensity\n"
        + "- balanced_thought: The reframed thought\n"
        + "- micro_action: The behavioral experiment\n\n"
        + "## Phase Transitions\n"
        + "Agents will handle their own phase transitions using the check_phase_transition tool.\n"
        + "Your role is to route to the correct agent based on the current phase."
    )

    # Create main router agent that checks for crisis first
    router_agent = LlmAgent(
        model=model,
        name="CBTRouter",
        instruction=orchestrator_instruction,
        tools=[check_for_crisis],
    )

    # For now, return a simple CBT assistant that can handle all phases
    # SequentialAgent requires a different architecture
    return router_agent
