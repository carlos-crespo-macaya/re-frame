"""
CBT Assistant Agent Utility Module.

This module provides utilities for creating CBT Assistant agents.
The main agent instance for ADK commands is in __agent__.py.
"""

from google.adk.agents import LlmAgent

from src.agents.phase_manager import check_phase_transition, get_current_phase_info
from src.knowledge.cbt_context import BASE_CBT_CONTEXT
from src.utils.logging import get_logger

logger = get_logger(__name__)


def create_cbt_assistant(model: str = "gemini-2.0-flash") -> LlmAgent:
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
        + "\n\n## IMPORTANT: Initial Greeting\n"
        + "When a new session starts and you're in the greeting phase, immediately provide "
        + "a warm welcome message without waiting for user input. Introduce yourself and "
        + "explain how you can help with cognitive reframing."
    )

    logger.info(
        "creating_cbt_assistant",
        model=model,
        tools=["check_phase_transition", "get_current_phase_info"],
    )

    agent = LlmAgent(
        model=model,
        name="CBTAssistant",
        instruction=enhanced_instruction,
        tools=[check_phase_transition, get_current_phase_info],
    )

    logger.info("cbt_assistant_created", model=model, agent_name=agent.name)

    return agent
