"""Agent implementations for re-frame."""

from .act_framework_agent import ACTFrameworkAgent
from .adk_observability import observability_manager
from .adk_session_manager import ADKSessionManager
from .base import ReFrameAgent
from .cbt_framework_agent import CBTFrameworkAgent
from .dbt_framework_agent import DBTFrameworkAgent
from .framework_selector import FrameworkSelector
from .intake_agent import IntakeAgent
from .multi_framework_synthesis import MultiFrameworkSynthesisAgent
from .stoicism_framework_agent import StoicismFrameworkAgent
from .synthesis_agent import SynthesisAgent

# Import ADK registry to auto-register agents when ADK is available
try:
    from .adk_registry import register_agents
    # Register agents for ADK web interface
    register_agents()
except ImportError:
    # ADK not available, skip registration
    pass

__all__ = [
    "ACTFrameworkAgent",
    "ADKSessionManager",
    "CBTFrameworkAgent",
    "DBTFrameworkAgent",
    "FrameworkSelector",
    "IntakeAgent",
    "MultiFrameworkSynthesisAgent",
    "ReFrameAgent",
    "StoicismFrameworkAgent",
    "SynthesisAgent",
    "observability_manager",
]
