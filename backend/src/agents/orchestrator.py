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

# Will use SequentialAgent in future phases
# from google.adk.agents import SequentialAgent
# from src.agents.discovery_agent import create_discovery_agent
# from src.agents.greeting_agent import create_greeting_agent
# from src.agents.reframing_agent import create_reframing_agent


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
    # Create phase-specific agents (to be integrated later)
    # greeting_agent = create_greeting_agent(model)
    # discovery_agent = create_discovery_agent(model)
    # reframing_agent = create_reframing_agent(model)

    # Summary agent placeholder - will be implemented in Phase 7
    # summary_instruction = (
    #     BASE_CBT_CONTEXT
    #     + "\n\n## Summary Phase\n"
    #     + "You are in the summary phase. This phase will be fully implemented soon.\n"
    #     + "For now, provide a brief recap of:\n"
    #     + "1. The situation and thought explored\n"
    #     + "2. The cognitive distortions identified\n"
    #     + "3. The balanced thought created\n"
    #     + "4. The micro-action planned\n"
    #     + "5. Encouragement for continued practice"
    # )

    # from google.adk.agents import LlmAgent

    # summary_agent = LlmAgent(
    #     model=model,
    #     name="SummaryAgent",
    #     instruction=summary_instruction,
    #     tools=[],
    # )

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


# ---------------------------------------------------------------------------
# Convenience helpers used by the React front-end patch.  These are **not**
# part of the original orchestrator design but exposing them at module level
# keeps the import surface area minimal while satisfying runtime dependencies
# in the new UX code.
# ---------------------------------------------------------------------------


def reply_suggestions(state: dict | None = None) -> list[str]:  # noqa: D401
    """Return quick-reply suggestions based on the current *phase*.

    The implementation here mirrors the behaviour outlined in the UX patch –
    we only surface suggestions during the SUMMARY phase.  When no *state*
    dict is provided we default to an empty list so that callers in unrelated
    contexts don't fail.
    """

    if not state:
        return []

    if str(state.get("phase", "")).upper() == "SUMMARY":
        return ["Yes", "No", "Explain more"]
    return []


# ---------------------------------------------------------------------------
# Streaming helper (stub)
# ---------------------------------------------------------------------------


async def stream(user_message: str):  # noqa: D401
    """Yield *tokens* for the assistant response in a streaming fashion.

    This implementation is deliberately minimal: it constructs a canned reply
    acknowledging the user message and then yields it word-by-word so that the
    front-end can render an incremental stream over websockets/SSE without the
    full complexity of server-side chunking.
    """

    response = f"You said: {user_message}. Let's continue our CBT journey together."
    for token in response.split():
        yield token + " "
