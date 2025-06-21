"""
Intake Agent - Collects and validates user input
To be implemented in future tasks
"""
from typing import Dict, Any
from .base import BaseAgent


class IntakeAgent(BaseAgent):
    """
    Agent responsible for collecting and structuring user input
    """
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # TODO: Implement intake logic
        raise NotImplementedError("Intake agent not yet implemented")