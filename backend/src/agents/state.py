# SPDX-License-Identifier: MIT
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Phase(str, Enum):
    WARMUP = "warmup"
    CLARIFY = "clarify"  # gather situation, thought, emotion, intensity
    REFRAME = "reframe"  # identify distortions + offer balanced thought
    SUMMARY = "summary"  # recap + ask 0-10 anxiety & confidence
    FOLLOWUP = "followup"  # limited short answers based on the summary
    CLOSED = "closed"


PHASE_ORDER: list[Phase] = [
    Phase.WARMUP,
    Phase.CLARIFY,
    Phase.REFRAME,
    Phase.SUMMARY,
    Phase.FOLLOWUP,
    Phase.CLOSED,
]


class SessionState(BaseModel):
    phase: Phase = Phase.WARMUP
    turn: int = 0
    max_turns: int = 14
    followups_left: int = 3
    user_language: str = "en"
    # Track what we've collected; purely informational for the UI/analytics.
    progress: dict[str, bool] = Field(
        default_factory=lambda: {
            "situation": False,
            "thought": False,
            "emotion": False,
            "intensity": False,
        }
    )
    suds_pre: int | None = None
    suds_post: int | None = None
    confidence_pre: int | None = None
    confidence_post: int | None = None
    crisis_flag: bool = False


class ControlBlock(BaseModel):
    # The model suggests; the orchestrator is the final arbiter.
    next_phase: Phase
    missing_fields: list[str] = []
    suggest_questions: list[str] = []
    crisis_detected: bool = False
    confidence_shift: dict[str, int] | None = None  # {"from":70,"to":45}


# --- Pydantic v1/v2 compatibility helpers ---
def model_validate(cls, data: Any):
    """Validate data against a Pydantic model for v1/v2."""
    try:
        return cls.model_validate(data)  # Pydantic v2
    except AttributeError:
        return cls.parse_obj(data)  # Pydantic v1


def model_dump(instance: BaseModel) -> dict[str, Any]:
    """Dump model to dict for v1/v2."""
    try:
        return instance.model_dump()  # Pydantic v2
    except AttributeError:
        return instance.dict()  # Pydantic v1
