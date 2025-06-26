"""Re-frame cognitive reframing assistant with language-aware agents."""

from reframe.orchestrators import LanguageAwareOrchestrator

# For ADK compatibility
orchestrator = LanguageAwareOrchestrator()
root_agent = orchestrator.pipeline

__version__ = "0.6.0"  # Language-aware architecture
__all__ = ["LanguageAwareOrchestrator", "root_agent"]