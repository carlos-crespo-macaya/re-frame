"""
Reframing Phase Agent for CBT Assistant.

This module implements the reframing phase where users work through
cognitive restructuring to create balanced alternative thoughts.
"""

from google.adk.agents import LlmAgent

from src.agents.phase_manager import (
    ConversationPhase,
    PhaseManager,
    check_phase_transition,
)
from src.knowledge.cbt_context import (
    BALANCED_THOUGHT_CRITERIA,
    BASE_CBT_CONTEXT,
    COGNITIVE_DISTORTIONS,
    EVIDENCE_GATHERING,
    MICRO_ACTION_PRINCIPLES,
)
from src.utils.language_utils import get_language_instruction


def gather_evidence_for_thought(thought: str, evidence_type: str) -> dict:
    """
    Guide the user through gathering evidence for or against their thought.

    Args:
        thought: The automatic thought being examined
        evidence_type: Either "for" or "against"

    Returns:
        dict: Guidance for evidence gathering
    """
    if evidence_type == "for":
        prompts = [
            "What makes you think this thought might be true?",
            "What evidence supports this belief?",
            "What past experiences align with this thought?",
        ]
    else:
        prompts = [
            "What evidence might suggest it's not completely true?",
            "Are there any facts that don't fit with this thought?",
            "What would you tell a friend who had this thought?",
        ]

    return {
        "status": "success",
        "evidence_type": evidence_type,
        "suggested_prompts": prompts,
        "principles": EVIDENCE_GATHERING["principles"],
        "next_step": "Collect user's evidence before proceeding",
    }


def create_balanced_thought(
    original_thought: str,
    evidence_for: list[str],
    evidence_against: list[str],
    distortions: list[str],
) -> dict:
    """
    Help create a balanced alternative thought based on evidence.

    Args:
        original_thought: The original automatic thought
        evidence_for: Evidence supporting the thought
        evidence_against: Evidence contradicting the thought
        distortions: Identified cognitive distortions

    Returns:
        dict: Guidance for creating balanced thought
    """
    return {
        "status": "success",
        "criteria": BALANCED_THOUGHT_CRITERIA,
        "instructions": [
            "Acknowledge any truth in the original thought",
            "Incorporate evidence from both sides",
            "Create a thought that is believable and helpful",
            "Keep it concise (30-40 words max)",
        ],
        "avoid": [
            "Toxic positivity",
            "Dismissing real concerns",
            "Overly complex statements",
        ],
    }


def design_micro_action(thought: str, distortion: str) -> dict:
    """
    Design a small behavioral experiment to test the thought.

    Args:
        thought: The thought to test
        distortion: The primary distortion identified

    Returns:
        dict: Micro-action design guidance
    """
    # Get specific micro-actions for the distortion
    distortion_data = None
    for dist in COGNITIVE_DISTORTIONS.values():
        if dist["code"] == distortion:
            distortion_data = dist
            break

    suggested_actions: list[str] = []
    if distortion_data:
        suggested_actions = list(distortion_data.get("micro_actions", []))

    return {
        "status": "success",
        "principles": MICRO_ACTION_PRINCIPLES,
        "distortion_specific_actions": suggested_actions,
        "general_guidelines": [
            "Make it specific and measurable",
            "Ensure it can be done today",
            "Frame as an experiment, not a test",
            "Focus on gathering information",
        ],
    }


def create_reframing_agent(
    model: str = "gemini-2.0-flash", language_code: str | None = None
) -> LlmAgent:
    """
    Create a reframing phase agent.

    Args:
        model: The Gemini model to use
        language_code: The language code for responses (e.g., 'en-US', 'es-ES')

    Returns:
        An LlmAgent configured for the reframing phase
    """
    # Get language-specific instruction
    language_instruction = get_language_instruction(language_code)
    # Build distortion reference
    distortion_quick_ref = "\n\n## Quick Distortion Reference:\n"
    for _, dist in COGNITIVE_DISTORTIONS.items():
        distortion_quick_ref += f"- {dist['code']}: {dist['name']}\n"

    reframing_instruction = (
        BASE_CBT_CONTEXT
        + f"\n\n## IMPORTANT: Language Requirement\n{language_instruction}\n"
        + "## Reframing Phase Instructions\n\n"
        + PhaseManager.get_phase_instruction(ConversationPhase.REFRAMING)
        + "\n\n## Your Specific Role:\n"
        + "You are the reframing specialist, focused on performing a single cognitive "
        + "restructuring intervention on the user's automatic thought.\n\n"
        + "## Task Sequence:\n"
        + "1. First, silently analyze the thought to identify distortions (use parser agent internally)\n"
        + "2. Share 1-2 main distortions with the user in simple terms\n"
        + "3. Guide evidence gathering using Socratic questioning\n"
        + "4. Help create a balanced alternative thought\n"
        + "5. Propose a micro-action to test the thought\n"
        + "6. Transition to summary phase\n\n"
        + "## Key Guidelines:\n"
        + "- Use collaborative language ('Let's explore...', 'What do you think...')\n"
        + "- Avoid CBT jargon when talking to users\n"
        + "- Ask one question at a time\n"
        + "- Validate before challenging\n"
        + "- Maximum 2 rounds of evidence gathering\n"
        + "- Keep the focus narrow on this specific thought\n\n"
        + "## Evidence Gathering Flow:\n"
        + "1. Start: 'What makes you think this thought might be true?'\n"
        + "2. Follow: 'And what evidence might suggest it's not completely true?'\n"
        + "3. If stuck, offer gentle prompts from the tool\n\n"
        + "## Creating Balanced Thoughts:\n"
        + "- Must acknowledge any truth in original\n"
        + "- Based on evidence gathered\n"
        + "- Believable and moderate\n"
        + "- 30-40 words maximum\n"
        + "- User should feel it's realistic\n\n"
        + "## Micro-Action Design:\n"
        + "- 10 minutes or less\n"
        + "- Targets the main distortion\n"
        + "- Involves doing, not just thinking\n"
        + "- Safe and achievable today\n"
        + "- Framed as an experiment\n"
        + distortion_quick_ref
        + "\n\n## Internal Process:\n"
        + "When you receive a thought to work with:\n"
        + "1. Internally identify distortions (don't share the analysis process)\n"
        + "2. Translate distortions into user-friendly language\n"
        + "3. Focus on the 1-2 most relevant distortions\n"
        + "4. Guide the conversation naturally\n\n"
        + "## Crisis Protocol:\n"
        + "If user expresses self-harm or suicidal thoughts:\n"
        + "1. Stop the reframing process\n"
        + "2. Express genuine concern\n"
        + "3. Provide crisis resources\n"
        + "4. Encourage immediate professional help"
    )

    return LlmAgent(
        model=model,
        name="ReframingAgent",
        instruction=reframing_instruction,
        tools=[
            check_phase_transition,
            gather_evidence_for_thought,
            create_balanced_thought,
            design_micro_action,
        ],
    )
