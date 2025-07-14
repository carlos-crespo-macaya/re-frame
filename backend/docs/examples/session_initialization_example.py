"""
Example of how to initialize a session with CBT context.

This shows how the greeting agent (or main orchestrator) would
initialize a session with all required CBT context.
"""

from src.knowledge.cbt_context import initialize_session_with_cbt_context


def setup_cbt_session(session):
    """
    Example function showing how to set up a new CBT session.

    This would typically be called when:
    1. A new user starts a conversation
    2. The greeting agent initializes the session
    3. A new session is created in the main orchestrator

    Args:
        session: The ADK session object that maintains conversation state
    """
    # Initialize the session with CBT context
    initialize_session_with_cbt_context(session)

    # The session now contains:
    # - cbt_guidelines: Core therapeutic principles
    # - distortion_types: List of all cognitive distortion keys
    # - phase: Set to "greeting" initially
    # - language: Set to "en" (English)
    # - safety_flags: Empty list for tracking crisis indicators

    # Additional session data can be added as needed
    session.state["user_name"] = None  # To be filled during greeting
    session.state["conversation_history"] = []

    return session


# Example usage in a greeting agent:
"""
async def greeting_agent_start(session):
    # Initialize CBT context
    setup_cbt_session(session)

    # Continue with greeting logic...
    response = "Hello! I'm here to help you explore your thoughts..."

    # Check for crisis indicators
    if any(indicator in user_input.lower() for indicator in CRISIS_INDICATORS):
        session.state["safety_flags"].append("crisis_detected")
        return CRISIS_RESPONSE_TEMPLATE

    # Transition to discovery phase
    session.state["phase"] = "discovery"

    return response
"""
