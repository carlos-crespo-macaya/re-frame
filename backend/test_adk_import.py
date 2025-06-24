#!/usr/bin/env python3
"""Test if ADK imports work correctly."""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Test importing as ADK would
    from agents.agent import root_agent

    print("✓ Successfully imported root_agent from agents.agent")
    print(f"  Agent name: {root_agent.name}")
    print(f"  Agent type: {type(root_agent).__name__}")
except ImportError as e:
    print(f"✗ Failed to import: {e}")

try:
    # Test alternative import
    from agents import root_agent

    print("✓ Successfully imported root_agent from agents")
except ImportError as e:
    print(f"✗ Failed to import from agents: {e}")
