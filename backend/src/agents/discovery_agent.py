"""
Discovery Phase Agent for CBT Assistant.

This module implements the discovery phase of the conversation flow,
helping users explore their thoughts and emotions.
"""

from google.adk.agents import LlmAgent

from src.agents.phase_manager import (
    ConversationPhase,
    PhaseManager,
    check_phase_transition,
)
from src.knowledge.cbt_context import BASE_CBT_CONTEXT, CBT_MODEL
from src.utils.language_utils import get_language_instruction

from .ui_contract import enforce_ui_contract


def extract_thought_details(user_input: str) -> dict:
    """
    Extract key elements from user's thought description.

    This tool analyzes the user's input to identify the situation,
    automatic thoughts, emotions, and behaviors following the CBT model.

    Args:
        user_input: The user's description of their thoughts/situation

    Returns:
        dict: Extracted thought components
    """
    # In practice, this would use NLP or the LLM to extract components
    # For now, return a structured response that guides the agent
    return {
        "status": "success",
        "message": "Thought details captured. Continue exploring with the user.",
        "components_to_explore": [
            "situation",
            "automatic_thoughts",
            "emotions",
            "physical_sensations",
            "behaviors",
        ],
        "next_steps": [
            "Ask for more details about unclear components",
            "Validate the user's experience",
            "Prepare for transition to reframing",
        ],
    }


def identify_emotions(emotion_description: str) -> dict:
    """
    Identify and categorize emotions from user's description.

    This tool helps recognize and validate the emotions the user is experiencing.

    Args:
        emotion_description: The user's description of their emotions

    Returns:
        dict: Identified emotions with intensity indicators
    """
    # In practice, this would analyze the emotion description
    # to categorize and identify specific emotions

    return {
        "status": "success",
        "message": "Emotions identified. Validate these with the user.",
        "emotion_guidance": {
            "validate_first": "Always acknowledge and validate emotions",
            "explore_intensity": "Ask about intensity on a 0-10 scale",
            "physical_sensations": "Ask about body sensations",
            "emotion_context": "Understand when emotions are strongest",
        },
    }


def create_discovery_agent(
    model: str = "gemini-2.0-flash", language_code: str | None = None
) -> LlmAgent:
    """
    Create a discovery phase agent.

    Args:
        model: The Gemini model to use
        language_code: The language code for responses (e.g., 'en-US', 'es-ES')

    Returns:
        An LlmAgent configured for the discovery phase
    """
    # Get language-specific instruction
    language_instruction = get_language_instruction(language_code)
    discovery_instruction = (
        BASE_CBT_CONTEXT
        + f"\n\n## IMPORTANT: Language Requirement\n{language_instruction}\n"
        + "## Discovery Phase Instructions\n\n"
        + PhaseManager.get_phase_instruction(ConversationPhase.DISCOVERY)
        + "\n\n## Your Specific Tasks:\n"
        + "1. Help the user explore their thoughts and feelings about a specific situation\n"
        + "2. Use the CBT model to structure your exploration:\n"
        + f"   - Situation: {CBT_MODEL['components'][0]} (What happened? When? Where? Who was involved?)\n"
        + f"   - Automatic Thoughts: {CBT_MODEL['components'][1]} (What went through your mind?)\n"
        + f"   - Emotions: {CBT_MODEL['components'][2]} (What emotions did you feel? How intense 0-10?)\n"
        + f"   - Behaviors: {CBT_MODEL['components'][3]} (What did you do or want to do?)\n"
        + "3. Ask open-ended questions to understand each component\n"
        + "4. Validate their experience without judgment\n"
        + "5. Use the extract_thought_details tool to structure the information\n"
        + "6. Use the identify_emotions tool to help categorize emotions\n"
        + "7. Once you have a clear picture of the situation, thoughts, and emotions, use check_phase_transition to move to 'reframing'\n\n"
        + "## Important Guidelines:\n"
        + "- Be curious and non-judgmental\n"
        + "- Use empathetic reflections\n"
        + "- Ask one question at a time\n"
        + "- Allow the user to express themselves fully\n"
        + "- Don't rush - take time to understand\n"
        + "- Validate emotions before exploring thoughts\n\n"
        + "## Crisis Detection:\n"
        + "If the user expresses thoughts of self-harm or suicide, immediately:\n"
        + "1. Express concern for their safety\n"
        + "2. Provide appropriate crisis resources\n"
        + "3. Encourage immediate professional help\n"
        + "4. Do not continue with CBT exercises"
    )

    return LlmAgent(
        model=model,
        name="DiscoveryAgent",
        instruction=enforce_ui_contract(discovery_instruction, phase="discovery"),
        tools=[check_phase_transition, extract_thought_details, identify_emotions],
    )
