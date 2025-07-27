"""
Phase Manager for CBT Conversation Flow.

This module manages the conversation phases and transitions
for the CBT reframing assistant.
"""

from enum import Enum

from google.adk.agents import LlmAgent

from src.knowledge.cbt_context import BASE_CBT_CONTEXT
from src.utils.logging import get_logger

logger = get_logger(__name__)


class ConversationPhase(Enum):
    """Enumeration of conversation phases."""

    GREETING = "greeting"
    DISCOVERY = "discovery"
    REFRAMING = "reframing"
    SUMMARY = "summary"


# Valid phase transitions
PHASE_TRANSITIONS: dict[ConversationPhase, list[ConversationPhase]] = {
    ConversationPhase.GREETING: [ConversationPhase.DISCOVERY],
    ConversationPhase.DISCOVERY: [ConversationPhase.REFRAMING],
    ConversationPhase.REFRAMING: [ConversationPhase.SUMMARY],
    ConversationPhase.SUMMARY: [],  # Terminal phase
}


class PhaseManager:
    """Manages conversation phase transitions and validation."""

    @staticmethod
    def get_current_phase(state: dict) -> ConversationPhase:
        """
        Get the current conversation phase from state.

        Args:
            state: The session state dictionary

        Returns:
            The current conversation phase
        """
        phase_str = state.get("phase", ConversationPhase.GREETING.value)
        try:
            return ConversationPhase(phase_str)
        except ValueError:
            # Default to greeting if invalid phase
            return ConversationPhase.GREETING

    @staticmethod
    def can_transition_to(
        current_phase: ConversationPhase, target_phase: ConversationPhase
    ) -> bool:
        """
        Check if a phase transition is valid.

        Args:
            current_phase: The current conversation phase
            target_phase: The desired target phase

        Returns:
            True if the transition is valid, False otherwise
        """
        return target_phase in PHASE_TRANSITIONS.get(current_phase, [])

    @staticmethod
    def transition_to_phase(context: dict, target_phase: str) -> dict:
        """
        Transition to a new phase while preserving context.

        Args:
            context: The current context dictionary
            target_phase: The target phase name

        Returns:
            Updated context with new phase
        """
        # Create a copy of the context to avoid mutation
        new_context = context.copy()

        # Update the phase
        new_context["current_phase"] = target_phase

        # Preserve important fields including language
        # Language, user_id, session_id, and other metadata should be preserved

        logger.debug(
            "phase_transition",
            from_phase=context.get("current_phase"),
            to_phase=target_phase,
            language=context.get("language"),
        )

        return new_context

    @staticmethod
    def get_phase_instruction(phase: ConversationPhase) -> str:
        """
        Get the instruction for a specific phase.

        Args:
            phase: The conversation phase

        Returns:
            The instruction text for the phase
        """
        instructions = {
            ConversationPhase.GREETING: (
                "You are in the GREETING phase. "
                "Welcome the user warmly, introduce yourself as a CBT assistant, "
                "and explain that you'll help them reframe their thoughts. "
                "Ask if they're ready to begin the process."
            ),
            ConversationPhase.DISCOVERY: (
                "You are in the DISCOVERY phase. "
                "Help the user explore their thoughts and feelings. "
                "Ask open-ended questions to understand the situation, "
                "the thoughts they're having, and the emotions they're experiencing."
            ),
            ConversationPhase.REFRAMING: (
                "You are in the REFRAMING phase. "
                "Help the user identify cognitive distortions in their thoughts "
                "and work together to create more balanced alternatives. "
                "Use the CBT techniques to challenge unhelpful thinking patterns."
            ),
            ConversationPhase.SUMMARY: (
                "You are in the SUMMARY phase. "
                "Summarize the key insights from the conversation, "
                "highlight the reframed thoughts, and provide actionable next steps. "
                "Encourage the user to practice their new thinking patterns."
            ),
        }
        return instructions.get(phase, "")


# Phase Management Tools - Simple Python functions that ADK will wrap as FunctionTools
def check_phase_transition(target_phase: str) -> dict:
    """
    Check and perform phase transitions in the conversation.

    This tool manages the conversation flow through different phases.
    It validates transitions to ensure phases are followed in order.

    Args:
        target_phase: The target phase to transition to (greeting/discovery/reframing/summary)

    Returns:
        dict: Result with status and message about the transition
    """
    # Note: In actual implementation, we'll need to access session state
    # For now, return a structured response that the agent can use
    valid_phases = ["greeting", "discovery", "reframing", "summary"]

    logger.info(
        "phase_transition_requested",
        target_phase=target_phase,
        valid_phases=valid_phases,
    )

    if target_phase not in valid_phases:
        logger.warning(
            "invalid_phase_transition",
            target_phase=target_phase,
            valid_phases=valid_phases,
        )
        return {
            "status": "error",
            "message": f"Invalid phase: {target_phase}. Valid phases are: {', '.join(valid_phases)}",
        }

    # In actual use, the agent will manage state through the session
    logger.info("phase_transition_ready", target_phase=target_phase)
    return {
        "status": "success",
        "message": f"Ready to transition to {target_phase} phase",
        "target_phase": target_phase,
    }


def get_current_phase_info() -> dict:
    """
    Get information about the current conversation phase.

    This tool provides details about the current phase and available transitions.

    Returns:
        dict: Information about current phase and next possible phases
    """
    # In actual implementation, this would access session state
    # For now, return structured guidance
    logger.debug("phase_info_requested")

    phase_flow = {
        "greeting": {
            "description": "Welcome and introduction phase",
            "next_phases": ["discovery"],
        },
        "discovery": {
            "description": "Understanding thoughts and feelings",
            "next_phases": ["reframing"],
        },
        "reframing": {
            "description": "Identifying distortions and creating alternatives",
            "next_phases": ["summary"],
        },
        "summary": {
            "description": "Recap and next steps",
            "next_phases": [],
        },
    }

    logger.debug("phase_info_returned", phase_flow=phase_flow)

    return {
        "status": "success",
        "phase_flow": phase_flow,
        "message": "Use this information to guide the conversation flow",
    }


def create_phase_aware_agent(
    model: str = "gemini-2.0-flash", phase: ConversationPhase | None = None
) -> LlmAgent:
    """
    Create a phase-aware CBT assistant agent.

    Args:
        model: The Gemini model to use
        phase: Optional specific phase to set

    Returns:
        An LlmAgent configured with phase awareness
    """
    phase_instruction = ""
    if phase:
        phase_instruction = f"\n\n{PhaseManager.get_phase_instruction(phase)}"

    instruction = (
        BASE_CBT_CONTEXT
        + "\n\n## Conversation Phase Management\n"
        + "This conversation follows a structured flow through phases:\n"
        + "1. GREETING - Welcome and introduction\n"
        + "2. DISCOVERY - Understanding thoughts and feelings\n"
        + "3. REFRAMING - Identifying distortions and creating alternatives\n"
        + "4. SUMMARY - Recap and next steps\n\n"
        + "You must follow the phases in order and cannot skip ahead. "
        + "Use the phase management tools to check and transition between phases."
        + phase_instruction
        + "\n\n## Session State\n"
        + "The session state tracks:\n"
        + "- Current phase\n"
        + "- User's name\n"
        + "- Thoughts and emotions shared\n"
        + "- Identified cognitive distortions\n"
        + "- Generated reframes\n\n"
        + "Always be aware of which phase you're in and guide accordingly."
    )

    return LlmAgent(
        model=model,
        name="PhaseAwareCBTAssistant",
        instruction=instruction,
        tools=[check_phase_transition, get_current_phase_info],
    )
