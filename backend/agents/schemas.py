"""Pydantic schemas for ADK agents in re-frame.

This module defines all input and output schemas for the multi-agent system,
ensuring type safety and validation across agent interactions.
"""

from typing import Any

from pydantic import BaseModel, Field


# Base schemas for common elements
class ExtractedElements(BaseModel):
    """Elements extracted from user input by intake agent."""

    situation: str = Field(..., description="The situation or context described")
    thoughts: list[str] = Field(default_factory=list, description="Thoughts identified")
    emotions: list[str] = Field(default_factory=list, description="Emotions identified")
    behaviors: list[str] = Field(default_factory=list, description="Behaviors identified")


class TechniqueApplication(BaseModel):
    """Details of a therapeutic technique application."""

    technique_name: str = Field(..., description="Name of the technique")
    description: str = Field(..., description="Brief description of the technique")
    application: str = Field(..., description="How it was applied to this specific thought")


# IntakeAgent schemas
class IntakeInput(BaseModel):
    """Input schema for the IntakeAgent."""

    user_thought: str = Field(
        ...,
        min_length=3,
        max_length=2000,
        description="The user's thought or situation to process",
    )
    timestamp: str = Field(default="current", description="Timestamp of the input")
    context: str = Field(default="initial_intake", description="Context of the interaction")


class IntakeOutput(BaseModel):
    """Output schema for the IntakeAgent."""

    is_valid: bool = Field(..., description="Whether the input is valid for processing")
    requires_crisis_support: bool = Field(
        default=False, description="Whether crisis support is needed"
    )
    extracted_elements: ExtractedElements = Field(
        ..., description="Elements extracted from the input"
    )
    identified_patterns: list[str] = Field(
        default_factory=list, description="Cognitive patterns identified"
    )
    validation_notes: str = Field(
        default="", description="Additional notes from validation"
    )


# CBTFrameworkAgent schemas
class CBTInput(BaseModel):
    """Input schema for the CBTFrameworkAgent."""

    intake_analysis: IntakeOutput = Field(..., description="Analysis from intake agent")
    techniques_priority: list[str] = Field(
        default_factory=lambda: [
            "cognitive_restructuring",
            "evidence_examination",
            "gradual_exposure",
        ],
        description="Priority order for techniques to apply",
    )
    focus: str = Field(
        default="AvPD-sensitive reframing", description="Focus area for CBT application"
    )


class CBTOutput(BaseModel):
    """Output schema for the CBTFrameworkAgent."""

    original_thought: str = Field(..., description="The original thought being addressed")
    cognitive_distortions: list[str] = Field(
        ..., description="Identified cognitive distortions"
    )
    reframed_thoughts: list[str] = Field(
        ..., description="Alternative reframed perspectives"
    )
    techniques_applied: list[TechniqueApplication] = Field(
        ..., description="CBT techniques that were applied"
    )
    action_suggestions: list[str] = Field(
        default_factory=list, description="Suggested actions for the user"
    )
    validation: str = Field(..., description="Validation of the user's experience")


# SynthesisAgent schemas
class SynthesisInput(BaseModel):
    """Input schema for the SynthesisAgent."""

    intake_analysis: IntakeOutput = Field(..., description="Analysis from intake agent")
    cbt_results: CBTOutput = Field(..., description="Results from CBT framework agent")
    original_thought: str = Field(..., description="Original user thought")
    tone: str = Field(default="warm and supportive", description="Desired tone")
    transparency_level: str = Field(default="high", description="Level of transparency")


class SynthesisOutput(BaseModel):
    """Output schema for the SynthesisAgent."""

    main_response: str = Field(..., description="Main response to the user")
    key_points: list[str] = Field(
        default_factory=list, description="Key points from the response"
    )
    techniques_explained: str = Field(
        ..., description="Explanation of techniques used"
    )
    transparency_summary: str = Field(
        ..., description="Summary of how the AI processed the input"
    )
    encouragement: str = Field(
        default="", description="Encouraging message for the user"
    )


# Multi-framework schemas (for future use)
class FrameworkAnalysis(BaseModel):
    """Analysis from a therapeutic framework."""

    framework_name: str = Field(..., description="Name of the framework (CBT, DBT, ACT)")
    insights: list[str] = Field(..., description="Key insights from this framework")
    techniques_used: list[str] = Field(..., description="Techniques applied")
    reframed_perspective: str = Field(..., description="Reframed perspective")


class MultiFrameworkInput(BaseModel):
    """Input for multi-framework processing."""

    intake_analysis: IntakeOutput
    frameworks_to_apply: list[str] = Field(
        default_factory=lambda: ["CBT", "DBT", "ACT"],
        description="Frameworks to apply",
    )


class MultiFrameworkOutput(BaseModel):
    """Output from multi-framework processing."""

    framework_analyses: list[FrameworkAnalysis]
    integrated_response: str
    recommended_framework: str
    confidence_score: float = Field(ge=0, le=1)


# Session response schema (for API responses)
class SessionResponse(BaseModel):
    """Complete session response combining all agent outputs."""

    success: bool
    response: str = Field(default="", description="Main response to user")
    transparency: dict[str, Any] = Field(
        default_factory=dict, description="Transparency data"
    )
    crisis_flag: bool = Field(default=False, description="Whether crisis support is needed")
    error: str | None = Field(default=None, description="Error message if any")
    workflow_stage: str = Field(default="", description="Stage where processing stopped")