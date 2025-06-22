"""ADK-based agent implementation for re-frame agents."""

import json
import logging
from typing import Any, Dict, List, Optional

from google.adk.agents import LlmAgent
from google.adk.core.models import LiteLlm
from google.adk.core.types import Content, Part, Text
from pydantic import BaseModel

from config.settings import get_settings

logger = logging.getLogger(__name__)


class ReFrameTransparencyData(BaseModel):
    """Data structure for transparency information."""
    
    agent_name: str
    model_used: str
    reasoning_path: Dict[str, Any]
    raw_response: str
    techniques_used: List[str] = []


class ReFrameResponse(BaseModel):
    """Standard response format for re-frame agents."""
    
    success: bool
    response: Optional[str] = None
    error: Optional[str] = None
    error_type: Optional[str] = None
    transparency_data: Optional[ReFrameTransparencyData] = None


class ADKReFrameAgent:
    """ADK-based agent wrapper for re-frame specific functionality."""
    
    def __init__(
        self,
        name: str,
        instructions: str,
        description: Optional[str] = None,
        tools: Optional[List[Any]] = None,
    ):
        """Initialize ADK-based re-frame agent.
        
        Args:
            name: Agent name
            instructions: System instructions for the agent
            description: Agent description
            tools: List of tools available to the agent
        """
        self.name = name
        self.instructions = instructions
        settings = get_settings()
        
        # Configure ADK agent with Gemini
        self.adk_agent = LlmAgent(
            name=name,
            model=LiteLlm(model=f"gemini/{settings.google_ai_model}"),
            instruction=instructions,
            description=description or f"Re-frame {name} agent using CBT techniques",
            tools=tools or [],
        )
        
        # Store settings for transparency
        self._model_name = settings.google_ai_model
        
        logger.info(f"Initialized ADK {name} agent with model {settings.google_ai_model}")
    
    async def run(self, input_data: Dict[str, Any]) -> str:
        """Execute the agent with the given input.
        
        Args:
            input_data: Dictionary containing the input data for the agent
            
        Returns:
            The text response from the model
            
        Raises:
            Exception: If the agent execution fails
        """
        # Format the input for ADK
        prompt = self._format_prompt(input_data)
        
        try:
            # Create content for ADK
            content = Content(
                parts=[Part(text=Text(text=prompt))],
                role="user"
            )
            
            # Execute the agent
            response = await self.adk_agent.run_async(content)
            
            # Extract text from response
            if response and response.parts:
                text_parts = [
                    part.text.text for part in response.parts 
                    if part.text and part.text.text
                ]
                return "\n".join(text_parts) if text_parts else ""
            
            logger.warning(f"{self.name}: Received empty response from ADK agent")
            return ""
            
        except Exception as e:
            logger.error(f"{self.name}: Error executing ADK agent: {e!s}")
            raise
    
    async def process_with_transparency(self, input_data: Dict[str, Any]) -> ReFrameResponse:
        """Process input and return response with transparency data.
        
        Args:
            input_data: Input data for processing
            
        Returns:
            ReFrameResponse with success/error info and transparency data
        """
        try:
            # Execute agent
            response = await self.run(input_data)
            
            # Extract reasoning path for transparency
            reasoning_path = self._extract_reasoning_path(response)
            
            # Create transparency data
            transparency_data = ReFrameTransparencyData(
                agent_name=self.name,
                model_used=self._model_name,
                reasoning_path=reasoning_path,
                raw_response=response,
                techniques_used=self._extract_techniques_used(response),
            )
            
            return ReFrameResponse(
                success=True,
                response=response,
                transparency_data=transparency_data,
            )
            
        except Exception as e:
            # Handle different error types
            error_type = self._classify_error(e)
            error_message = self._get_user_friendly_error_message(e, error_type)
            
            logger.error(f"Error in {self.name}: {e!s}")
            
            return ReFrameResponse(
                success=False,
                error=error_message,
                error_type=error_type,
                transparency_data=ReFrameTransparencyData(
                    agent_name=self.name,
                    model_used=self._model_name,
                    reasoning_path={"error": str(e)},
                    raw_response="",
                ),
            )
    
    def _format_prompt(self, input_data: Dict[str, Any]) -> str:
        """Format input data into a prompt for the agent."""
        return f"""
{self.instructions}

Input data:
{json.dumps(input_data, indent=2)}

Please provide your response in the exact JSON format specified in the instructions.
"""
    
    def _extract_reasoning_path(self, response: str) -> Dict[str, Any]:
        """Extract reasoning path from agent response for transparency.
        
        This should be overridden by subclasses for agent-specific transparency.
        """
        return {
            "raw_response": response,
            "steps": [],
            "agent_type": "base",
        }
    
    def _extract_techniques_used(self, response: str) -> List[str]:
        """Extract CBT techniques used from the response.
        
        This should be overridden by subclasses for specific technique extraction.
        """
        return []
    
    def _classify_error(self, error: Exception) -> str:
        """Classify error type for user-friendly messaging."""
        error_str = str(error).lower()
        
        if "rate limit" in error_str or "quota" in error_str:
            return "rate_limit"
        elif "timeout" in error_str or "deadline" in error_str:
            return "timeout" 
        elif "auth" in error_str or "permission" in error_str:
            return "auth"
        elif "network" in error_str or "connection" in error_str:
            return "network"
        else:
            return "unknown"
    
    def _get_user_friendly_error_message(self, error: Exception, error_type: str) -> str:
        """Get user-friendly error message based on error type."""
        messages = {
            "rate_limit": "Rate limit exceeded. Please try again later.",
            "timeout": "Request timed out. Please try again.",
            "auth": "Authentication failed. Please check API configuration.",
            "network": "Network error. Please check your connection and try again.",
            "unknown": f"An unexpected error occurred: {str(error)}",
        }
        return messages.get(error_type, messages["unknown"])
    
    def parse_json_response(self, response: str) -> Dict[str, Any]:
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