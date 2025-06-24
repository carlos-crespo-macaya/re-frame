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
    automatic_thought: str | None = Field(default=None, description="The automatic negative thought")
    emotion_data: str | None = Field(default=None, description="Emotional response and intensity")
    user_inputs: list[str] = Field(default_factory=list, description="User inputs")


class IntakeAgentOutput(BaseModel):
    """Output schema for the intake agent."""

    collection_complete: bool = Field(False, description="Whether all required data has been collected")
    escalate: bool = Field(False, description="Whether to escalate/exit the conversation")
    crisis_detected: bool = Field(False, description="Whether a crisis situation was detected")
    data: IntakeData = Field(default_factory=lambda: IntakeData(), description="Collected intake data")


class ReframeAnalysis(BaseModel):
    """CBT reframe analysis result."""

    distortions: list[str] = Field(default_factory=list, description="Cognitive distortions identified")
    evidence_for: list[str] = Field(default_factory=list, description="Evidence supporting the thought")
    evidence_against: list[str] = Field(default_factory=list, description="Evidence against the thought")
    balanced_thought: str = Field(..., description="A more balanced perspective")
    micro_action: str = Field(..., description="A small actionable step")
    certainty_before: int = Field(..., description="Certainty in negative thought (0-100)")
    certainty_after: int = Field(..., description="Certainty after reframing (0-100)")
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
    """State of the session."""

    intake_data: IntakeData | None = Field(default=None, description="Collected intake data")
    reframe_analysis: ReframeAnalysis | None = Field(default=None, description="Reframe analysis")
    pdf_report: PdfReportResponse | None = Field(default=None, description="PDF report")

class ConversationState(BaseModel):
    """State of the conversation."""

    intake_data: IntakeData | None = Field(default=None, description="Collected intake data")
    reframe_analysis: ReframeAnalysis | None = Field(default=None, description="Reframe analysis")
    pdf_report: PdfReportResponse | None = Field(default=None, description="PDF report")
