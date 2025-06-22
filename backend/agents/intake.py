"""
Intake Agent - Collects and validates user input
To be implemented in future tasks
"""

from typing import Any

from .base import ReFrameAgent


class IntakeAgent(ReFrameAgent):
    """
    Agent responsible for collecting and structuring user input
    """

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        # TODO: Implement intake logic
        raise NotImplementedError("Intake agent not yet implemented")
