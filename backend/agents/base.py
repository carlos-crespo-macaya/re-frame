"""Base agent configuration for re-frame agents."""

import json
import logging
from typing import Any

import google.generativeai as genai
from google.generativeai import GenerativeModel

from config.settings import get_settings

logger = logging.getLogger(__name__)


class ReFrameAgent:
    """Base agent class with re-frame specific configuration."""

    def __init__(self, name: str, instructions: str, model: GenerativeModel | None = None):
        """Initialize agent with Google AI Studio configuration."""
        self.name = name
        self.instructions = instructions
        settings = get_settings()

        # Configure Google AI API
        genai.configure(api_key=settings.google_ai_api_key)

        # Create model if not provided
        if model is None:
            self.model = GenerativeModel(
                model_name=settings.google_ai_model,
                generation_config={
                    "temperature": settings.google_ai_temperature,
                    "max_output_REDACTED,
                },
            )
        else:
            self.model = model

        logger.info(f"Initialized {name} agent with model {settings.google_ai_model}")

    async def run(self, input_data: dict[str, Any]) -> str:
        """Execute the agent with the given input."""
        # Format the prompt with instructions and input
        prompt = f"""
{self.instructions}

Input data:
{json.dumps(input_data, indent=2)}

Please provide your response in the exact JSON format specified in the instructions.
"""

        # Generate response
        response = self.model.generate_content(prompt)
        return response.text

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
                "model_used": get_settings().google_ai_model,
            }
        except Exception as e:
            logger.error(f"Error in {self.name}: {e!s}")
            return {"success": False, "error": str(e), "agent_name": self.name}

    def _extract_reasoning_path(self, response: Any) -> dict[str, Any]:
        """Extract reasoning path from agent response for transparency."""
        # This will be customized by each agent subclass
        return {"raw_response": str(response), "steps": []}
