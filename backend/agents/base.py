"""Base agent configuration for re-frame agents."""

import logging
from typing import Any

import google.generativeai as genai
from google import adk
from google.generativeai import GenerativeModel

from config.settings import get_settings

logger = logging.getLogger(__name__)


class ReFrameAgent(adk.LlmAgent):
    """Base agent class with re-frame specific configuration."""

    def __init__(self, name: str, instructions: str, model: GenerativeModel | None = None):
        """Initialize agent with Google AI Studio configuration."""
        settings = get_settings()

        # Configure Google AI API
        genai.configure(api_key=settings.google_ai_api_key)

        # Create model if not provided
        if model is None:
            model = GenerativeModel(
                model_name=settings.google_ai_model,
                generation_config={
                    "temperature": settings.google_ai_temperature,
                    "max_output_REDACTED,
                }
            )

        # Initialize parent class
        super().__init__(
            name=name,
            instructions=instructions,
            model=model
        )

        logger.info(f"Initialized {name} agent with model {settings.google_ai_model}")

    async def process_with_transparency(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Process input and return response with transparency data."""
        try:
            # Execute agent
            response = await self.run(input_data)

            # Extract reasoning path for transparency
            reasoning_path = self._extract_reasoning_path(response)

            return {
                "success": True,
                "response": response,
                "reasoning_path": reasoning_path,
                "agent_name": self.name,
                "model_used": get_settings().google_ai_model
            }
        except Exception as e:
            logger.error(f"Error in {self.name}: {e!s}")
            return {
                "success": False,
                "error": str(e),
                "agent_name": self.name
            }

    def _extract_reasoning_path(self, response: Any) -> dict[str, Any]:
        """Extract reasoning path from agent response for transparency."""
        # This will be customized by each agent subclass
        return {
            "raw_response": str(response),
            "steps": []
        }
