"""Pydantic models for agent inputs and outputs."""

from typing import Any

from pydantic import BaseModel, Field


# Intake Agent Models
class IntakeInput(BaseModel):
    """Input for the intake agent."""

    user_thought: str = Field(..., description="The user's thought or situation")
    timestamp: str = Field(default="current", description="Timestamp of the input")
    context: str = Field(default="initial_intake", description="Context of the intake")


class ExtractedElements(BaseModel):
    """Elements extracted from user input."""

    situation: str = Field(..., description="Brief description of the situation")
    thoughts: list[str] = Field(default_factory=list, description="Identified thoughts")
    emotions: list[str] = Field(default_factory=list, description="Identified emotions")
    behaviors: list[str] = Field(default_factory=list, description="Identified behaviors")


class IntakeAnalysis(BaseModel):
    """Output from the intake agent analysis."""

    is_valid: bool = Field(..., description="Whether the input is valid")
    requires_crisis_support: bool = Field(
        default=False, description="Whether crisis support is needed"
    )
    extracted_elements: ExtractedElements
    identified_patterns: list[str] = Field(
        default_factory=list, description="Identified cognitive patterns"
    )
    validation_notes: str = Field("", description="Any validation notes or observations")


# CBT Framework Agent Models
class CBTInput(BaseModel):
    """Input for the CBT framework agent."""

    intake_analysis: IntakeAnalysis
    original_thought: str | None = None


class CBTTechnique(BaseModel):
    """A CBT technique application."""

    technique_name: str
    description: str
    application: str


class CBTAnalysis(BaseModel):
    """Output from the CBT framework agent."""

    original_thought: str
    cognitive_distortions: list[str] = Field(
        default_factory=list, description="Identified cognitive distortions"
    )
    reframed_thoughts: list[str] = Field(
        default_factory=list, description="Alternative perspectives"
    )
    techniques_applied: list[CBTTechnique] = Field(
        default_factory=list, description="CBT techniques applied"
    )
    action_suggestions: list[str] = Field(
        default_factory=list, description="Suggested actions"
    )
    validation: str = Field("", description="Validation and encouragement")


# Synthesis Agent Models
class SynthesisInput(BaseModel):
    """Input for the synthesis agent."""

    intake_analysis: IntakeAnalysis
    cbt_results: CBTAnalysis
    original_thought: str


class SynthesisOutput(BaseModel):
    """Output from the synthesis agent."""

    main_response: str = Field(..., description="Main response to the user")
    key_points: list[str] = Field(
        default_factory=list, description="Key takeaway points"
    )
    techniques_explained: str = Field(
        "", description="Explanation of techniques used"
    )
    transparency_summary: str = Field(
        "", description="Transparency about the AI process"
    )
    encouragement: str = Field("", description="Encouraging message")


# Agent Response Models
class AgentResponse(BaseModel):
    """Standard response from any agent."""

    success: bool
    response: Any | None = None
    reasoning_path: dict[str, Any] = Field(default_factory=dict)
    agent_name: str
    model_used: str
    error: str | None = None
    error_type: str | None = None


# Session Manager Models
class SessionResponse(BaseModel):
    """Response from the session manager."""

    success: bool
    response: str | None = None
    transparency: dict[str, Any] = Field(default_factory=dict)
    crisis_flag: bool = False
    error: str | None = None
    workflow_stage: str | None = None


# API Response Model (already exists in api/reframe.py)
class ReframeResponseData(BaseModel):
    """Complete reframe response data."""

    success: bool
    response: str
    transparency: dict[str, Any]
    techniques_used: list[str]
    frameworks_used: list[str] = Field(default_factory=list)
    key_points: list[str] = Field(default_factory=list)
    techniques_explained: str = ""
    error: str | None = None