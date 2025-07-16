"""
CBT Assistant Agent Utility Module.

This module provides utilities for creating CBT Assistant agents.
The main agent instance for ADK commands is in __agent__.py.
"""

# The ADK dependency is only available in certain environments.
# Import it lazily so that local development without the SDK does not crash.
try:
    from google.adk.agents import LlmAgent  # type: ignore
except ModuleNotFoundError:  # pragma: no cover – handled gracefully below
    LlmAgent = None  # type: ignore

from src.agents.phase_manager import check_phase_transition, get_current_phase_info
from src.knowledge.cbt_context import BASE_CBT_CONTEXT


def create_cbt_assistant(model: str = "gemini-2.0-flash-live-001") -> LlmAgent:
    """
    Create a CBT Assistant agent with specified model.

    This is a utility function for tests and custom implementations.
    For ADK commands (web, run, api_server), use the agent in __agent__.py.

    Args:
        model: The Gemini model to use (default: gemini-2.0-flash)

    Returns:
        An LlmAgent configured for CBT assistance
    """
    # Enhanced instruction that makes use of session state and phase management
    enhanced_instruction = (
        BASE_CBT_CONTEXT
        + "\n\n## Session State Management\n"
        + "You have access to session state that persists between turns. "
        + "The session state includes:\n"
        + "- user_name: The user's name if they've shared it\n"
        + "- phase: Current conversation phase (greeting/discovery/reframing/summary)\n"
        + "- thoughts_recorded: List of thoughts the user has shared\n"
        + "- emotions_captured: List of emotions the user has expressed\n"
        + "- distortions_detected: List of cognitive distortion codes identified\n"
        + "- reframes_generated: List of reframed thoughts\n\n"
        + "Use this information to maintain context and provide personalized responses. "
        + "If the user shares their name, remember to use it in subsequent interactions."
        + "\n\n## Conversation Phase Management\n"
        + "This conversation follows a structured flow through phases:\n"
        + "1. GREETING - Welcome and introduction\n"
        + "2. DISCOVERY - Understanding thoughts and feelings\n"
        + "3. REFRAMING - Identifying distortions and creating alternatives\n"
        + "4. SUMMARY - Recap and next steps\n\n"
        + "You must follow the phases in order and cannot skip ahead. "
        + "Use the phase management tools to check and transition between phases."
    )

    # If the ADK is not available (e.g. during open-source development or in
    # CI) fall back to a very simple echo agent so that the remainder of the
    # application – especially the SSE plumbing – continues to work.  This
    # provides a graceful degradation instead of an import-time crash.

    if LlmAgent is None:  # pragma: no cover
        class _EchoAgent:  # Minimal stub matching the ADK agent interface
            name = "EchoAgent"

            async def __call__(self, *args, **kwargs):  # noqa: D401 – simple stub
                user_content = kwargs.get("content") or ""
                return f"You said: {user_content}"

        return _EchoAgent()  # type: ignore

    agent = LlmAgent(
        model=model,
        name="CBTAssistant",
        instruction=enhanced_instruction,
        tools=[check_phase_transition, get_current_phase_info],
    )

    return agent
