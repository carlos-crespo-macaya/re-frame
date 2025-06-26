"""Data models for multilingual cognitive reframing system."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ConversationPhase(Enum):
    INTAKE = "intake"
    ANALYSIS = "analysis"
    SUMMARY = "summary"


@dataclass
class ConversationTurn:
    """Single turn in the conversation."""
    timestamp: datetime
    speaker: str  # "user" or "assistant"
    content: str
    phase: ConversationPhase
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IntakeData:
    """Data collected during intake phase."""
    situation: str
    automatic_thoughts: str
    emotions: str
    emotion_intensity: int
    crisis_indicators: List[str] = field(default_factory=list)


@dataclass
class AnalysisData:
    """Data generated during analysis phase."""
    cognitive_distortions: List[str]
    evidence_for: List[str]
    evidence_against: List[str]
    balanced_thought: str
    micro_action: str
    confidence_before: int
    confidence_after: int
    follow_up_insights: List[str] = field(default_factory=list)


@dataclass
class MultilingualSessionState:
    """Complete session state for multilingual support."""
    # Language settings
    user_language: str  # ISO 639-1 code
    language_name: str  # Human-readable name
    language_confidence: float
    
    # Conversation data
    intake_data: Optional[IntakeData] = None
    analysis_data: Optional[AnalysisData] = None
    conversation_history: List[ConversationTurn] = field(default_factory=list)
    
    # Metadata
    session_id: str = ""
    user_id: str = ""
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    # Flags
    exit_requested: bool = False
    crisis_detected: bool = False
    
    def add_turn(self, speaker: str, content: str, phase: ConversationPhase):
        """Add a conversation turn to history."""
        turn = ConversationTurn(
            timestamp=datetime.now(),
            speaker=speaker,
            content=content,
            phase=phase
        )
        self.conversation_history.append(turn)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'user_language': self.user_language,
            'language_name': self.language_name,
            'language_confidence': self.language_confidence,
            'intake_data': self.intake_data.__dict__ if self.intake_data else None,
            'analysis_data': self.analysis_data.__dict__ if self.analysis_data else None,
            'conversation_history': [
                {
                    'timestamp': turn.timestamp.isoformat(),
                    'speaker': turn.speaker,
                    'content': turn.content,
                    'phase': turn.phase.value
                }
                for turn in self.conversation_history
            ],
            'session_id': self.session_id,
            'user_id': self.user_id,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'exit_requested': self.exit_requested,
            'crisis_detected': self.crisis_detected
        }