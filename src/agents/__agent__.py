"""
CBT Assistant Agent - Entry point for ADK commands.

This module provides the agent instance that ADK commands (web, run, api_server)
will use to interact with the CBT Assistant.
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.agents.cbt_assistant import create_cbt_assistant  # noqa: E402

# Create the agent instance that ADK will use
agent = create_cbt_assistant()

# Make agent available for ADK (some versions look for root_agent)
root_agent = agent
__all__ = ["agent", "root_agent"]
