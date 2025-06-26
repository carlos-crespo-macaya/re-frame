"""Pydantic models for the re-frame agent."""

from enum import Enum

from pydantic import BaseModel, Field


class StatusEnum(str, Enum):
    """Status values for the agent workflow."""

    SUCCESS = "success"
    FAILURE = "failure"


class IntakeData(BaseModel):
    """Data collected during intake conversation."""

    trigger_situation: str | None = Field(default=None, description="The triggering situation")
    automatic_thought: str | None = Field(
        default=None, description="The automatic negative thought"
    )
    emotion_data: str | None = Field(default=None, description="Emotional response and intensity")
    user_inputs: list[str] = Field(default_factory=list, description="User inputs")


class IntakeAgentOutput(BaseModel):
    """Output schema for the intake agent."""

    collection_complete: bool = Field(
        False, description="Whether all required data has been collected"
    )
    escalate: bool = Field(False, description="Whether to escalate/exit the conversation")
    crisis_detected: bool = Field(False, description="Whether a crisis situation was detected")
    data: IntakeData = Field(
        default_factory=lambda: IntakeData(), description="Collected intake data"
    )


class ReframeAnalysis(BaseModel):
    """CBT reframe analysis result."""

    distortions: list[str] = Field(
        default_factory=list, description="Cognitive distortions identified"
    )
    evidence_for: list[str] = Field(
        default_factory=list, description="Evidence supporting the thought"
    )
    evidence_against: list[str] = Field(
        default_factory=list, description="Evidence against the thought"
    )
    balanced_thought: str = Field(..., description="A more balanced perspective")
    micro_action: str = Field(..., description="A small actionable step")
    confidence_before: int = Field(..., description="Confidence in negative thought (0-100)")
    confidence_after: int | None = Field(None, description="Confidence after reframing (0-100)")
    tone: str = Field(default="warm", description="Tone of the therapeutic response")


class ProcessReframeResponse(BaseModel):
    """Response from process_reframe_data tool."""

    status: StatusEnum
    message: str
    result_json: str | None = None


class PdfReportResponse(BaseModel):
    """Response from create_pdf_report tool."""

    status: StatusEnum
    message: str
    pdf_base64: str | None = None


class SessionState(BaseModel):
    """Complete session state per POC specification."""

    intake_data: IntakeData | None = Field(default=None, description="Collected intake data")
    reframe_analysis: ReframeAnalysis | None = Field(default=None, description="Reframe analysis")
    collection_complete: bool = Field(
        False, description="Whether intake data collection is complete"
    )
    reframe_done: bool = Field(False, description="Whether reframing is complete")
    escalate: bool = Field(False, description="Whether to escalate the session")
    crisis_detected: bool = Field(False, description="Whether a crisis was detected")
    pdf_ready: bool = Field(False, description="Whether PDF has been generated")


class ConversationState(BaseModel):
    """State of the conversation."""

    intake_data: IntakeData | None = Field(default=None, description="Collected intake data")
    reframe_analysis: ReframeAnalysis | None = Field(default=None, description="Reframe analysis")
    pdf_report: PdfReportResponse | None = Field(default=None, description="PDF report")


class FrameworkAnalysis(BaseModel):
    """Analysis result from a therapeutic framework agent."""

    framework: str = Field(..., description="Framework name (cbt, dbt, act, stoicism)")
    key_insights: list[str] = Field(
        default_factory=list, description="Key insights from this framework"
    )
    reframe_suggestions: list[str] = Field(
        default_factory=list, description="Reframing suggestions"
    )
    practical_exercises: list[str] = Field(default_factory=list, description="Practical exercises")
    confidence_score: float = Field(
        ..., description="Confidence in this framework's applicability (0-1)"
    )
    reasoning: str = Field(..., description="Why this framework is relevant")


class SynthesisResult(BaseModel):
    """Result from synthesizing multiple framework analyses."""

    primary_framework: str = Field(..., description="Most applicable framework")
    unified_reframe: ReframeAnalysis = Field(
        ..., description="Synthesized reframe combining all frameworks"
    )
    integrated_insights: list[str] = Field(
        default_factory=list, description="Integrated insights across frameworks"
    )
    recommended_sequence: list[str] = Field(
        default_factory=list, description="Recommended order of exercises"
    )
    coherence_score: float = Field(..., description="How well the frameworks align (0-1)")
    conflicts_resolved: list[str] = Field(
        default_factory=list, description="Any conflicts resolved between frameworks"
    )
