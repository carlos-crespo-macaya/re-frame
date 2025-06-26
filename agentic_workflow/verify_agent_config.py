#!/usr/bin/env python3
"""Verify that the correct agent is configured for ADK."""

import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

print("🔍 Verifying ADK agent configuration...")

# Check run_adk.py
print("\n1. Checking run_adk.py:")
try:
    from run_adk import agent, runner
    print(f"   ✅ Agent type: {type(agent).__name__}")
    print(f"   ✅ Agent name: {agent.name}")
    print(f"   ✅ Runner configured: {runner is not None}")
except Exception as e:
    print(f"   ❌ Error loading run_adk: {e}")

# Check adk_agent.py
print("\n2. Checking adk_agent.py:")
try:
    from adk_agent import maya, runner as adk_runner
    print(f"   ✅ Agent type: {type(maya).__name__}")
    print(f"   ✅ Agent name: {maya.name}")
    print(f"   ✅ Runner configured: {adk_runner is not None}")
except Exception as e:
    print(f"   ❌ Error loading adk_agent: {e}")

# Check agent.py
print("\n3. Checking agent.py:")
try:
    from agent import agent as main_agent
    print(f"   ✅ Agent type: {type(main_agent).__name__}")
    print(f"   ✅ Agent name: {main_agent.name}")
except Exception as e:
    print(f"   ❌ Error loading agent: {e}")

# Check if multilingual agent has language detection tools
print("\n4. Checking multilingual capabilities:")
try:
    from reframe.agents.maya_multilingual_agent import MayaMultilingualAgent
    test_agent = MayaMultilingualAgent()
    tools = [tool.__name__ for tool in test_agent.tools if hasattr(tool, '__name__')]
    print(f"   ✅ Tools available: {tools}")
    if 'detect_language' in tools:
        print("   ✅ Language detection tool present")
    else:
        print("   ❌ Language detection tool missing!")
except Exception as e:
    print(f"   ❌ Error checking multilingual agent: {e}")

print("\n✨ Verification complete!")