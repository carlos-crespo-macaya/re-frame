"""CBT Assistant Agent Package.

This package optionally depends on Google's **Agent Development Kit (ADK)**.
For local development and Continuous Integration environments where the ADK is
not available we install a *very lightweight* stub under ``google.adk`` **at
import time** so that the rest of the codebase can simply ``import
google.adk.agents`` without additional guard-clauses.
"""

from __future__ import annotations

import sys
import types


# ---------------------------------------------------------------------------
# Provide on-the-fly stub for ``google.adk.agents`` when the real SDK is not
# installed.  We do this *before* importing any sub-modules so that subsequent
# import statements resolve successfully.
# ---------------------------------------------------------------------------

if "google.adk.agents" not in sys.modules:  # pragma: no cover – runtime guard

    google_mod = types.ModuleType("google")
    adk_mod = types.ModuleType("google.adk")
    agents_mod = types.ModuleType("google.adk.agents")

    class _LlmAgent:  # noqa: D401 – minimal stub
        def __init__(self, *, model: str, name: str, instruction: str, tools=None):
            self.model = model
            self.name = name
            self.instruction = instruction
            self.tools = tools or []

        def __str__(self):  # type: ignore[override]
            return self.instruction

    agents_mod.LlmAgent = _LlmAgent  # type: ignore[attr-defined]

    # Register the nested hierarchy in sys.modules **and** as attributes so that
    # ``import google.adk.agents`` and ``from google.adk import agents`` both work.
    sys.modules.update(
        {
            "google": google_mod,
            "google.adk": adk_mod,
            "google.adk.agents": agents_mod,
        }
    )

    google_mod.adk = adk_mod  # type: ignore[attr-defined]
    adk_mod.agents = agents_mod  # type: ignore[attr-defined]


# The remaining imports rely on the (real or stubbed) ADK being importable.
# Import sub-modules *lazily* so that missing optional dependencies (e.g.
# reportlab, numpy) do **not** break basic import of ``src.agents`` which is
# required by many utility modules in the test-suite.  We swallow
# ``ImportError`` because those sub-modules are not needed for the unit tests
# that focus on helper utilities (intent classification, summarisation, …).


def _safe_import(name: str):  # noqa: D401 – internal helper
    try:
        module = __import__(name, fromlist=["*"])
        globals()[name.rsplit(".", 1)[-1]] = module
    except ModuleNotFoundError:
        # Optional feature – skip when dependency chain is incomplete.
        pass


for _mod in (
    "src.agents.__agent__",
    "src.agents.discovery_agent",
    "src.agents.greeting_agent",
    "src.agents.parser_agent",
    "src.agents.reframing_agent",
    "src.agents.summary_agent",
):
    _safe_import(_mod)

# Export only symbols that made it into globals()

_exports = [
    "agent",
    "create_discovery_agent",
    "create_greeting_agent",
    "create_parser_agent",
    "create_reframing_agent",
    "create_summary_agent",
    "root_agent",
]

__all__ = [name for name in _exports if name in globals()]

__all__ = [
    "agent",
    "create_discovery_agent",
    "create_greeting_agent",
    "create_parser_agent",
    "create_reframing_agent",
    "create_summary_agent",
    "root_agent",
]
