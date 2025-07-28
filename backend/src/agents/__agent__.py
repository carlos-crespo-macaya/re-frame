"""
CBT Assistant Agent - Entry point for ADK commands.

This module provides the agent instance that ADK commands (web, run, api_server)
will use to interact with the CBT Assistant.
"""

import os
import sys
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
from typing import Any

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Check if we're in test mode
_TEST_MODE = os.getenv("CBT_SKIP_AGENT_INIT", "0") in ("1", "true", "True", "TRUE")

# Define agent with proper type annotation
agent: Any

if _TEST_MODE:
    # Provide a cheap stub that satisfies attribute access in tests
    agent = SimpleNamespace(name="StubAgent", run=lambda *_, **__: None)
else:
    from src.agents.cbt_assistant import create_cbt_assistant

    @lru_cache(maxsize=1)
    def _get_agent():
        """Lazily create the CBT assistant agent on first use."""
        return create_cbt_assistant()

    class _AgentProxy:
        """Proxy that delays agent creation until first attribute access."""

        def __getattr__(self, item):
            return getattr(_get_agent(), item)

    agent = _AgentProxy()

# Make agent available for ADK (some versions look for root_agent)
root_agent = agent
__all__ = ["agent", "root_agent"]
