"""Base agent configuration for re-frame agents."""

import json
import logging
from typing import Any

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
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
        api_key = settings.google_ai_api_key
        logger.info(
            f"{name}: Configuring with API key: {'*' * 10}{api_key[-4:] if len(api_key) > 4 else 'TOO_SHORT'}"
        )
        genai.configure(api_key=api_key)

        # Create model if not provided
        if model is None:
            logger.info(f"{name}: Creating GenerativeModel with {settings.google_ai_model}")
            self.model = GenerativeModel(
                model_name=settings.google_ai_model,
                generation_config={
                    "temperature": settings.google_ai_temperature,
                    "max_output_tokens": settings.google_ai_max_tokens,
                },
            )
        else:
            self.model = model

        logger.info(f"Initialized {name} agent with model {settings.google_ai_model}")

    async def run(self, input_data: dict[str, Any]) -> str:
        """Execute the agent with the given input.

        Makes actual API calls to Google AI Studio via the Gemini API.

        Args:
            input_data: Dictionary containing the input data for the agent

        Returns:
            The text response from the model

        Raises:
            google.api_core.exceptions.ResourceExhausted: Rate limit exceeded
            google.api_core.exceptions.DeadlineExceeded: Request timeout
            google.api_core.exceptions.Unauthenticated: Invalid API key
            Exception: Other API errors
        """
        # Format the prompt with instructions and input
        prompt = f"""
{self.instructions}

Input data:
{json.dumps(input_data, indent=2)}

Please provide your response in the exact JSON format specified in the instructions.
"""
        logger.info(f"{self.name}: Sending prompt to Gemini (length: {len(prompt)} chars)")
        logger.debug(f"{self.name}: Full prompt: {prompt[:500]}...")

        try:
            # Generate response - this makes the actual API call
            logger.info(f"{self.name}: Calling Gemini API...")
            response = self.model.generate_content(prompt)
            logger.info(f"{self.name}: Received response from Gemini")

            # The response object has a text property that contains the generated text
            # It could be empty if the model refuses to generate content
            if hasattr(response, "text") and response.text:
                logger.info(f"{self.name}: Response text length: {len(response.text)} chars")
                logger.debug(f"{self.name}: Response text: {response.text[:200]}...")
                return response.text
            # Handle empty response case
            logger.warning(f"{self.name}: Received empty response from model")
            return ""

        except Exception as e:
            # Log the error but re-raise it so calling code can handle appropriately
            logger.error(f"{self.name}: Error calling Gemini API: {e!s}")
            raise

    async def process_with_transparency(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Process input and return response with transparency data.

        Provides user-friendly error messages for common API errors.
        """
        logger.info(f"{self.name}: Starting process_with_transparency")
        try:
            # Execute agent
            response = await self.run(input_data)
            logger.info(
                f"{self.name}: Agent run completed, response length: {len(response) if response else 0}"
            )

            # Extract reasoning path for transparency
            reasoning_path = self._extract_reasoning_path(response)

            return {
                "success": True,
                "response": response,
                "reasoning_path": reasoning_path,
                "agent_name": self.name,
                "model_used": get_settings().google_ai_model,
            }
        except google_exceptions.ResourceExhausted as e:
            # Rate limit error - provide user-friendly message
            logger.error(f"{self.name}: Rate limit exceeded - {e!s}")
            return {
                "success": False,
                "error": "Rate limit exceeded. Please try again later.",
                "agent_name": self.name,
                "error_type": "rate_limit",
            }
        except google_exceptions.DeadlineExceeded as e:
            # Timeout error
            logger.error(f"{self.name}: Request timed out - {e!s}")
            return {
                "success": False,
                "error": "Request timed out. Please try again.",
                "agent_name": self.name,
                "error_type": "timeout",
            }
        except google_exceptions.Unauthenticated as e:
            # API key error
            logger.error(f"{self.name}: Authentication failed - {e!s}")
            return {
                "success": False,
                "error": "Authentication failed. Please check API configuration.",
                "agent_name": self.name,
                "error_type": "auth",
            }
        except Exception as e:
            # Generic error handling
            logger.error(f"Error in {self.name}: {e!s}")
            return {
                "success": False,
                "error": str(e),
                "agent_name": self.name,
                "error_type": "unknown",
            }

    def _extract_reasoning_path(self, response: Any) -> dict[str, Any]:
        """Extract reasoning path from agent response for transparency."""
        # This will be customized by each agent subclass
        return {"raw_response": str(response), "steps": []}

    def parse_json_response(self, response: str) -> dict[str, Any]:
        """Parse JSON from model response, handling common formatting issues.

        Args:
            response: Raw text response from the model

        Returns:
            Parsed JSON as dictionary

        Raises:
            json.JSONDecodeError: If response cannot be parsed as JSON
        """
        if not response:
            raise json.JSONDecodeError("Empty response", "", 0)

        # Try to parse as-is first
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Handle markdown code fence wrapped JSON
            if response.strip().startswith("```"):
                # Extract content between code fences
                lines = response.strip().split("\n")
                if lines[0].startswith("```"):
                    # Remove first and last lines (the fence markers)
                    json_content = "\n".join(lines[1:-1])
                    try:
                        return json.loads(json_content)
                    except json.JSONDecodeError:
                        pass

            # If all parsing attempts fail, re-raise the original error
            raise json.JSONDecodeError(
                f"Unable to parse response as JSON: {response[:100]}...", response, 0
            ) from None
