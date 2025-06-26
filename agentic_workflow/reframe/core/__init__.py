"""Core business logic for re-frame."""

from .multilingual_models import (
    ConversationPhase,
    ConversationTurn,
    IntakeData,
    AnalysisData,
    MultilingualSessionState,
)

# Keep backward compatibility during migration
try:
    from .models import SessionState, ReframeAnalysis
    __all__ = [
        "ConversationPhase",
        "ConversationTurn", 
        "IntakeData",
        "AnalysisData",
        "MultilingualSessionState",
        "SessionState",  # For backward compatibility
        "ReframeAnalysis",  # For backward compatibility
    ]
except ImportError:
    __all__ = [
        "ConversationPhase",
        "ConversationTurn", 
        "IntakeData",
        "AnalysisData",
        "MultilingualSessionState",
    ]