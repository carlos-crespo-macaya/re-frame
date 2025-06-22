"""
Synthesis Agent - Processes raw LLM output into responses
To be implemented in future tasks
"""

from typing import Any

from .base import BaseAgent


class SynthesisAgent(BaseAgent):
    """
    Agent responsible for synthesizing and formatting final responses
    """

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        # TODO: Implement synthesis logic
        raise NotImplementedError("Synthesis agent not yet implemented")
