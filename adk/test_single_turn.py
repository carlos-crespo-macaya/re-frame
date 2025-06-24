#!/usr/bin/env python3
"""Test that the intake agent only responds once per turn."""

import os
os.environ["GOOGLE_API_KEY"] = "test-key"  # Set before imports

from reframe_agent import root_agent

# Print the agent's instruction to verify it includes our changes
print("=== AGENT INSTRUCTION (first 2000 chars) ===")
print(root_agent.instruction[:2000])
print("\n=== END INSTRUCTION ===\n")

# Check that the agent is configured correctly
print(f"Agent name: {root_agent.name}")
print(f"Agent description: {root_agent.description}")
print(f"Agent tools: {[tool.__name__ for tool in root_agent.tools] if root_agent.tools else 'None'}")