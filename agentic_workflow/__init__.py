"""Agentic workflow for re-frame.social cognitive reframing assistant."""

# Import the multilingual agent for ADK
from reframe.agents.maya_multilingual_agent import MayaMultilingualAgent

# Create the root agent instance that ADK expects
root_agent = MayaMultilingualAgent()  # Maya with multilingual support

__all__ = ["root_agent"]
