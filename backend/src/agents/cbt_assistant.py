"""
CBT Assistant Agent Utility Module.

This module provides utilities for creating CBT Assistant agents.
The main agent instance for ADK commands is in __agent__.py.
"""

from google.adk.agents import LlmAgent

from src.knowledge.cbt_context import BASE_CBT_CONTEXT
from src.utils.language_utils import get_language_instruction
from src.utils.logging import get_logger

from .ui_contract import enforce_ui_contract

logger = get_logger(__name__)


def create_cbt_assistant(
    model: str = "gemini-2.0-flash", language_code: str = "en-US"
) -> LlmAgent:
    """
    Create a CBT Assistant agent with specified model.

    This is a utility function for tests and custom implementations.
    For ADK commands (web, run, api_server), use the agent in __agent__.py.

    Args:
        model: The Gemini model to use (default: gemini-2.0-flash)
        language_code: The language code for responses (default: en-US)

    Returns:
        An LlmAgent configured for CBT assistance
    """
    # Get language-specific instruction
    language_instruction = get_language_instruction(language_code)

    # Format it for the CBT context
    formatted_language_instruction = (
        f"\n\n## IMPORTANT: Language Requirement\n{language_instruction}\n"
        f"Translate all CBT concepts appropriately and maintain a warm, professional tone."
    )

    # Enhanced instruction that makes use of session state and phase management
    enhanced_instruction = (
        BASE_CBT_CONTEXT
        + formatted_language_instruction
        + "\n\n## Session State Management\n"
        + "You have access to session state that persists between turns. "
        + "The session state includes:\n"
        + "- user_name: The user's name if they've shared it\n"
        + "- phase: Current conversation phase (warmup/clarify/reframe/summary/followup/closed)\n"
        + "- thoughts_recorded: List of thoughts the user has shared\n"
        + "- emotions_captured: List of emotions the user has expressed\n"
        + "- distortions_detected: List of cognitive distortion codes identified\n"
        + "- reframes_generated: List of reframed thoughts\n\n"
        + "Use this information to maintain context and provide personalized responses. "
        + "If the user shares their name, remember to use it in subsequent interactions."
        + "\n\n## Conversation Phase Management\n"
        + "This conversation follows a structured flow through phases:\n"
        + "1. WARMUP - Welcome and orientation\n"
        + "2. CLARIFY - Situation, thought, emotion, intensity\n"
        + "3. REFRAME - Identify distortions + offer a balanced alternative\n"
        + "4. SUMMARY - Recap + SUDS/confidence check (no actions)\n"
        + "5. FOLLOWUP - Brief clarifications only\n"
        + "6. CLOSED - Session end\n\n"
        + "Phase transitions are determined by the orchestrator; do not invoke tools."
        + "\n\n## IMPORTANT: Reactive Behavior\n"
        + "Wait for the user to send their first message before greeting them. "
        + "When they do, provide a warm welcome message in response. "
        + "Do not send any messages until the user initiates the conversation."
    )

    logger.info(
        "creating_cbt_assistant",
        model=model,
        language_code=language_code,
        tools=[],
    )

    agent = LlmAgent(
        model=model,
        name="CBTAssistant",
        instruction=enforce_ui_contract(enhanced_instruction, phase=None),
        tools=[],
    )

    logger.info("cbt_assistant_created", model=model, agent_name=agent.name)

    return agent
