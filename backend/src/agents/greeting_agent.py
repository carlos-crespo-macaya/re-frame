"""
Greeting Phase Agent for CBT Assistant.

This module implements the greeting phase of the conversation flow,
welcoming users and explaining the process.
"""

from google.adk.agents import LlmAgent

from src.agents.phase_manager import (
    ConversationPhase,
    PhaseManager,
    check_phase_transition,
)
from src.knowledge.cbt_context import BASE_CBT_CONTEXT
from src.utils.language_detection import LanguageDetector


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


def create_greeting_agent(model: str = "gemini-2.0-flash") -> LlmAgent:
    """
    Create a greeting phase agent.

    Args:
        model: The Gemini model to use

    Returns:
        An LlmAgent configured for the greeting phase
    """
    greeting_instruction = (
        BASE_CBT_CONTEXT
        + "\n\n## Greeting Phase Instructions\n\n"
        + PhaseManager.get_phase_instruction(ConversationPhase.GREETING)
        + "\n\n## Language Detection and Support\n"
        + "1. ALWAYS use the detect_user_language tool on the first user message\n"
        + "2. Store the detected language in session state as 'user_language' and 'language_name'\n"
        + "3. Respond in the detected language automatically\n"
        + "4. Currently supported languages: English (en) and Spanish (es)\n"
        + "5. If an unsupported language is detected, acknowledge it and continue in English\n\n"
        + "## Your Specific Tasks:\n"
        + "1. Detect the user's language using detect_user_language tool\n"
        + "2. Welcome the user warmly in their language and introduce yourself\n"
        + "3. Explain that this is a 4-phase cognitive reframing process:\n"
        + "   - Greeting (current): Introduction and overview\n"
        + "   - Discovery: Understanding thoughts and feelings\n"
        + "   - Reframing: Identifying and challenging unhelpful thoughts\n"
        + "   - Summary: Review insights and next steps\n"
        + "4. Include a clear disclaimer that this tool does not replace professional therapy\n"
        + "5. Ask if they're ready to begin the process\n"
        + "6. When the user acknowledges and is ready, use the check_phase_transition tool to move to 'discovery'\n\n"
        + "## Important Guidelines:\n"
        + "- Use a warm, welcoming tone\n"
        + "- Be clear but not overwhelming with information\n"
        + "- Keep the greeting concise (3-4 sentences)\n"
        + "- Wait for user acknowledgment before transitioning\n"
        + "- Never explicitly mention that you detected their language\n\n"
        + "## Localized Greetings:\n"
        + "Use the Localizer class to get appropriate greetings:\n"
        + "- English: Use Localizer.get('en', 'greeting.welcome'), etc.\n"
        + "- Spanish: Use Localizer.get('es', 'greeting.welcome'), etc.\n"
    )

    return LlmAgent(
        model=model,
        name="GreetingAgent",
        instruction=greeting_instruction,
        tools=[detect_user_language, check_phase_transition],
    )
