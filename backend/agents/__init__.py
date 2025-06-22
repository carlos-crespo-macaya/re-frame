"""Agent implementations using Google ADK."""

# Legacy agents (for backwards compatibility during migration)
from .cbt_framework_agent import CBTFrameworkAgent
from .intake_agent import IntakeAgent
from .synthesis_agent import SynthesisAgent

# ADK-based agents (new implementation)
from .adk_base import ADKReFrameAgent, ReFrameResponse, ReFrameTransparencyData
from .adk_intake_agent import ADKIntakeAgent
from .adk_cbt_agent import ADKCBTFrameworkAgent
from .adk_synthesis_agent import ADKSynthesisAgent
from .adk_session_manager import ADKSessionManager, SessionData
from .adk_tools import get_all_reframe_tools
from .adk_config import ADKConfigurationManager, config_manager
from .adk_observability import ADKObservabilityManager, observability_manager

__all__ = [
    # Legacy agents
    "CBTFrameworkAgent",
    "IntakeAgent",
    "SynthesisAgent",
    # ADK agents
    "ADKReFrameAgent",
    "ReFrameResponse", 
    "ReFrameTransparencyData",
    "ADKIntakeAgent",
    "ADKCBTFrameworkAgent",
    "ADKSynthesisAgent",
    "ADKSessionManager",
    "SessionData",
    "get_all_reframe_tools",
    "ADKConfigurationManager",
    "config_manager",
    "ADKObservabilityManager",
    "observability_manager",
]
