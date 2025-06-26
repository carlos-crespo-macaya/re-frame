"""Orchestrator with proper language detection and propagation."""

from google.adk.agents import SequentialAgent
from google.adk.sessions import DatabaseSessionService, InMemorySessionService
from reframe.agents.intake_with_language import IntakeWithLanguageAgent
from reframe.agents.analysis_with_language import AnalysisWithLanguageAgent
from reframe.agents.pdf_with_language import PDFWithLanguageAgent
from reframe.config.settings import get_settings
from reframe.config.logging import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)


class LanguageAwareOrchestrator:
    """Orchestrator that properly handles language detection and propagation."""
    
    def __init__(self):
        self.settings = get_settings()
        
        # Initialize agents
        logger.info("Initializing language-aware agents...")
        self.intake_agent = IntakeWithLanguageAgent()
        self.analysis_agent = AnalysisWithLanguageAgent()
        self.pdf_agent = PDFWithLanguageAgent()
        
        # Session management
        if self.settings.supabase_connection_string:
            self.session_service = DatabaseSessionService(
                db_url=self.settings.supabase_connection_string
            )
            logger.info("Using DatabaseSessionService for session state")
        else:
            self.session_service = InMemorySessionService()
            logger.info("Using InMemorySessionService for session state")
        
        # Create sequential pipeline
        self.pipeline = SequentialAgent(
            name="language_aware_pipeline",
            sub_agents=[
                self.intake_agent,    # Detects language and collects data
                self.analysis_agent,  # Uses language from state for CBT
                self.pdf_agent       # Creates summary in detected language
            ],
            description="Cognitive reframing with proper language handling"
        )
        
        logger.info("✅ Language-aware orchestrator initialized")
        logger.info("Language detection happens in intake agent and propagates via session state")