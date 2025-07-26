"""
Greeting Phase Agent for CBT Assistant.

This module implements the greeting phase of the conversation flow,
welcoming users and explaining the process.
"""

from typing import Optional

from google.adk.agents import LlmAgent

from src.agents.phase_manager import (
    ConversationPhase,
    PhaseManager,
    check_phase_transition,
)
from src.knowledge.cbt_context import BASE_CBT_CONTEXT
from src.utils.language_detection import LanguageDetector
from src.utils.language_utils import get_language_instruction


def detect_user_language(user_input: str) -> dict:
    """
    Detect the language of user input and return language information.

    Args:
        user_input: The user's message

    Returns:
        dict: Language detection results
    """
    language_code = LanguageDetector.detect_with_fallback(user_input)
    language_name = LanguageDetector.get_language_name(language_code)

    return {
        "language_code": language_code,
        "language_name": language_name,
        "supported": LanguageDetector.is_supported(language_code),
    }


def create_greeting_agent(
    model: str = "gemini-2.0-flash", language_code: Optional[str] = None
) -> LlmAgent:
    """
    Create a greeting phase agent.

    Args:
        model: The Gemini model to use
        language_code: The language code for responses (e.g., 'en-US', 'es-ES')

    Returns:
        An LlmAgent configured for the greeting phase
    """
    # Get language-specific instruction
    language_instruction = get_language_instruction(language_code)
    greeting_instruction = (
        BASE_CBT_CONTEXT
        + f"\n\n## IMPORTANT: Language Requirement\n{language_instruction}\n"
        + "\n\n## Greeting Phase Instructions\n\n"
        + PhaseManager.get_phase_instruction(ConversationPhase.GREETING)
        + "\n\n## Language Support\n"
        + "1. You MUST respond in the language specified in the Language Requirement section above\n"
        + "2. The language has been pre-selected by the user\n"
        + "3. DO NOT switch languages based on user input\n"
        + "4. Maintain consistent language throughout the conversation\n\n"
        + "## Your Specific Tasks:\n"
        + "1. Welcome the user warmly in the specified language and introduce yourself\n"
        + "2. Explain that this is a 4-phase cognitive reframing process:\n"
        + "   - Greeting (current): Introduction and overview\n"
        + "   - Discovery: Understanding thoughts and feelings\n"
        + "   - Reframing: Identifying and challenging unhelpful thoughts\n"
        + "   - Summary: Review insights and next steps\n"
        + "3. Include a clear disclaimer that this tool does not replace professional therapy\n"
        + "4. Ask if they're ready to begin the process\n"
        + "5. When the user acknowledges and is ready, use the check_phase_transition tool to move to 'discovery'\n\n"
        + "## Important Guidelines:\n"
        + "- Use a warm, welcoming tone\n"
        + "- Be clear but not overwhelming with information\n"
        + "- Keep the greeting concise (3-4 sentences)\n"
        + "- Wait for user acknowledgment before transitioning\n"
    )

    return LlmAgent(
        model=model,
        name="GreetingAgent",
        instruction=greeting_instruction,
        tools=[check_phase_transition],
    )
