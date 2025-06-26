"""Root agent module for ADK to find at expected location."""

import logging
import os

logger = logging.getLogger(__name__)

# Check if we have required environment variables
required_vars = ["GOOGLE_API_KEY", "LANGFUSE_HOST", "LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY"]
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    # Create a simple fallback agent for ADK to recognize
    logger.warning(f"Missing environment variables: {missing_vars}")
    logger.warning("Creating fallback agent - set environment variables for full functionality")
    
    async def root_agent(user_query: str) -> str:
        """Fallback agent when environment variables are missing."""
        return (
            "⚠️ Environment configuration needed!\n\n"
            f"Missing: {', '.join(missing_vars)}\n\n"
            "Please set these environment variables:\n"
            + "\n".join([f"export {var}='your-value'" for var in missing_vars])
            + "\n\nThen restart ADK to use the full cognitive reframing assistant."
        )
else:
    # Import the conversational multilingual agent when properly configured
    try:
        from reframe.agents.maya_conversational_agent import MayaConversationalMultilingualAgent
        root_agent = MayaConversationalMultilingualAgent()
        logger.info("Successfully loaded Maya Conversational - Multilingual cognitive reframing assistant with flow control")
    except Exception as e:
        logger.error(f"Failed to load agent: {e}")
        # Fallback in case of other errors
        async def root_agent(user_query: str) -> str:
            return f"Error loading agent: {str(e)}"

# Make it available at the expected path
__all__ = ["root_agent"]