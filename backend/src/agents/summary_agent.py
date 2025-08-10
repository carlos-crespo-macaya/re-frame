"""
Summary Phase Agent for CBT Assistant.

This module implements the summary phase where users receive a comprehensive
recap of their session with key insights and actionable takeaways.
"""

from google.adk.agents import LlmAgent

from src.agents.phase_manager import (
    ConversationPhase,
    PhaseManager,
    check_phase_transition,
)
from src.knowledge.cbt_context import BASE_CBT_CONTEXT
from src.utils.language_utils import get_language_instruction

from .ui_contract import enforce_ui_contract


def extract_key_insights(
    thought: str, distortions: list[str], balanced_thought: str
) -> dict:
    """
    Extract key insights from the reframing process.

    Args:
        thought: The original automatic thought
        distortions: Identified cognitive distortions
        balanced_thought: The reframed thought

    Returns:
        dict: Key insights from the session
    """
    return {
        "status": "success",
        "insight_categories": [
            "Thinking patterns noticed",
            "Evidence that challenged the thought",
            "What made the balanced thought helpful",
            "Learning about your thinking style",
        ],
        "guidance": "Highlight 2-3 most meaningful insights for the user",
    }


def generate_action_items(
    balanced_thought: str, micro_action: str, distortions: list[str]
) -> dict:
    """
    Generate personalized action items based on the session.

    Args:
        balanced_thought: The reframed thought
        micro_action: The behavioral experiment planned
        distortions: Identified cognitive distortions

    Returns:
        dict: Action items for continued practice
    """
    return {
        "status": "success",
        "action_categories": [
            "Complete the micro-action experiment",
            "Practice the balanced thought when similar situations arise",
            "Notice when the identified distortions appear",
            "Optional: Journal about the experiment results",
        ],
        "principles": [
            "Keep actions simple and specific",
            "Focus on observation, not perfection",
            "Frame as experiments and learning",
            "Maximum 3-4 action items",
        ],
    }


def format_session_summary(
    situation: str,
    thought: str,
    emotions: dict,
    distortions: list[str],
    balanced_thought: str,
    micro_action: str,
    insights: list[str],
    action_items: list[str],
) -> dict:
    """
    Format the complete session summary.

    Args:
        situation: The situation explored
        thought: Original automatic thought
        emotions: Emotions and intensities
        distortions: Identified distortions
        balanced_thought: Reframed thought
        micro_action: Planned experiment
        insights: Key insights
        action_items: Future actions

    Returns:
        dict: Formatted summary structure
    """
    return {
        "status": "success",
        "summary_sections": {
            "situation_explored": situation,
            "original_thought": thought,
            "emotions_identified": emotions,
            "thinking_patterns": distortions,
            "balanced_perspective": balanced_thought,
            "experiment_planned": micro_action,
            "key_insights": insights,
            "next_steps": action_items,
        },
        "formatting_guidelines": [
            "Use clear section headers",
            "Keep language accessible",
            "Highlight the most important elements",
            "End with encouragement",
        ],
    }


def create_summary_agent(
    model: str = "gemini-2.0-flash", language_code: str | None = None
) -> LlmAgent:
    """
    Create a summary phase agent.

    Args:
        model: The Gemini model to use
        language_code: The language code for responses (e.g., 'en-US', 'es-ES')

    Returns:
        An LlmAgent configured for the summary phase
    """
    # Get language-specific instruction
    language_instruction = get_language_instruction(language_code)
    summary_instruction = (
        BASE_CBT_CONTEXT
        + f"\n\n## IMPORTANT: Language Requirement\n{language_instruction}\n"
        + "## Summary Phase Instructions\n\n"
        + PhaseManager.get_phase_instruction(ConversationPhase.SUMMARY)
        + "\n\n## Your Specific Role:\n"
        + "You are the summary specialist, responsible for creating a concise, relatable "
        + "recap of the CBT session.\n\n"
        + "## Task Sequence:\n"
        + "1. Acknowledge completion of the reframing work\n"
        + "2. Create a structured summary of the session\n"
        + "3. Extract 2-3 key insights from the process\n"
        + "4. Ask how true the balanced thought feels now (0–10) and how the user feels now: anxiety 0–10 and confidence 0–10\n"
        + "5. Provide encouragement and closure\n\n"
        + "## Summary Structure:\n"
        + "### What We Explored\n"
        + "- Situation: [Brief description]\n"
        + "- Automatic thought: [The original thought]\n"
        + "- Emotions: [List with intensities]\n\n"
        + "### What We Discovered\n"
        + "- Thinking patterns: [User-friendly distortion names]\n"
        + "- Evidence gathered: [Key points that challenged the thought]\n"
        + "- Balanced perspective: [The reframed thought]\n\n"
        + "### How It Feels Now\n"
        + "- Truth rating for the balanced thought (0–10): [ask user]\n"
        + "- Anxiety now (0–10): [ask user]\n"
        + "- Confidence now (0–10): [ask user]\n\n"
        + "### Your Action Plan\n"
        + "- Today's experiment: [The micro-action]\n"
        + "- Practice opportunities: [When to use balanced thought]\n"
        + "- What to notice: [Patterns to observe]\n\n"
        + "### Key Takeaways\n"
        + "- [2-3 personalized insights]\n\n"
        + "## Guidelines:\n"
        + "- Keep summary concise but complete\n"
        + "- Use the user's own words when possible\n"
        + "- Make insights specific and relatable\n"
        + "- End with genuine encouragement\n"
        + "- Acknowledge this is one step in a journey\n\n"
        + "## Language Tips:\n"
        + "- 'You discovered...' instead of 'We found...'\n"
        + "- 'You might notice...' for future observations\n"
        + "- 'One thing that stood out...' for insights\n"
        + "- Validate their effort and openness\n\n"
        + "## Closing Options:\n"
        + "1. Offer to clarify any part of the summary\n"
        + "2. Mention summary will be available for download (coming soon)\n"
        + "3. Encourage trying the micro-action\n"
        + "4. Thank them for engaging with the process\n\n"
        + "## Do NOT:\n"
        + "- Make the summary too long or detailed\n"
        + "- Include CBT jargon without explanation\n"
        + "- Overwhelm with too many action items\n"
        + "- Minimize the work they've done\n"
        + "- Promise outcomes or cures"
    )

    return LlmAgent(
        model=model,
        name="SummaryAgent",
        instruction=enforce_ui_contract(summary_instruction, phase="summary"),
        tools=[
            check_phase_transition,
            extract_key_insights,
            format_session_summary,
        ],
    )
