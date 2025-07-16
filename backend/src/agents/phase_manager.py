"""Phase Manager for CBT Conversation Flow.

Manages conversation phases and transitions for the CBT reframing assistant.

We enable **deferred evaluation** of type-annotations so helper functions that
reference ``ConversationPhase`` can be declared prior to the enum definition.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Sequence
from .utils.intent import classify_intent
# limit for trimming memory blobs
TOKEN_LIMIT = 8000  # keep a cushion below model max

# ----------  NEW HELPERS  --------------------------------------------------- #

def handoff_prompt(frm: ConversationPhase, to: ConversationPhase) -> str:
    """Human‑sounding sentence that bridges two phases."""
    return (
        f"🟢 **Great job!** We’ve finished *{frm.value}*. "
        f"Next up: **{to.value.title()}**. Ready?"
    )

def _trim_list(items: Sequence[str], keep: int = 3) -> List[str]:
    return list(items[-keep:])

# ---------------------------------------------------------------------------
# Optional ADK dependency – we provide a lightweight stub when the actual SDK
# is not available in the execution environment (e.g. during CI).
# ---------------------------------------------------------------------------

try:
    from google.adk.agents import LlmAgent  # type: ignore
except ModuleNotFoundError:  # pragma: no cover – stub fallback

    class LlmAgent:  # type: ignore[override]
        """Extremely thin stub so that type-checks and imports succeed."""

        def __init__(self, *, model: str, name: str, instruction: str, tools=None):
            self.model = model
            self.name = name
            self.instruction = instruction
            self.tools = tools or []

        def __str__(self) -> str:  # noqa: D401 – needed by tests
            return self.instruction

from src.knowledge.cbt_context import BASE_CBT_CONTEXT


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

    def transition(self, state: Dict[str, Any], target: ConversationPhase) -> None:
        """Perform phase transition with a human-friendly summary."""
        prev_raw = state.get("phase")

        # Safely coerce the previous phase (it may be missing or a plain string)
        if isinstance(prev_raw, ConversationPhase):
            prev_phase = prev_raw
        else:
            try:
                prev_phase = ConversationPhase(prev_raw)
            except Exception:  # noqa: BLE001
                prev_phase = ConversationPhase.GREETING

        state["phase"] = target
        state["transition_summary"] = handoff_prompt(prev_phase, target)

    def register_user_message(self, state: Dict[str, Any], user_msg: str) -> None:
        """Call on every user turn; tag intent & trim long lists."""
        state["intent"] = classify_intent(user_msg)

        # trim memory blobs if growing too large
        for key in ("thoughts_recorded", "emotions_captured"):
            if isinstance(state.get(key), list) and len(state[key]) > 6:
                state[key] = _trim_list(state[key])

        # cheap length check for state size
        combined = " ".join(state.get(k, "") for k in ("thoughts_recorded", "transition_summary"))
        if len(combined) > TOKEN_LIMIT:
            state["thoughts_recorded"] = _trim_list(state.get("thoughts_recorded", []))


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

    if target_phase not in valid_phases:
        return {
            "status": "error",
            "message": f"Invalid phase: {target_phase}. Valid phases are: {', '.join(valid_phases)}",
        }

    # In actual use, the agent will manage state through the session
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
    return {
        "status": "success",
        "phase_flow": {
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
        },
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
