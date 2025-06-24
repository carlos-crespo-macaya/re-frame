"""Pydantic schemas for API documentation and validation."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# Request schemas
class ReframeRequest(BaseModel):
    """Request model for cognitive reframing."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "thought": "Everyone will judge me if I speak up in the meeting",
                "context": "I have a presentation tomorrow",
            }
        }
    )

    thought: str = Field(
        ...,
        min_length=5,
        max_length=2000,
        description="The thought or situation to reframe. Should be a complete thought or worry.",
        json_schema_extra={
            "examples": [
                "I'll embarrass myself if I try to contribute",
                "They must think I'm incompetent",
                "I should just avoid all social situations",
            ]
        },
    )

    context: str | None = Field(
        None,
        max_length=500,
        description="Additional context about the situation (optional)",
        json_schema_extra={
            "examples": [
                "This happens every time I'm in groups",
                "After what happened last week",
                "I've been feeling this way for months",
            ]
        },
    )


# Response schemas
class TransparencyData(BaseModel):
    """Transparency information about the reframing process."""

    techniques_applied: list[str] = Field(
        default_factory=list, description="CBT techniques used in the reframing"
    )
    reasoning_path: list[str] = Field(
        default_factory=list, description="Step-by-step reasoning process"
    )
    confidence: float | None = Field(
        None, ge=0.0, le=1.0, description="Model confidence in the reframing (0-1)"
    )
    stage: str | None = Field(None, description="Processing stage where any issues occurred")
    crisis_detected: bool = Field(False, description="Whether crisis indicators were detected")


class ReframeResponse(BaseModel):
    """Response model for cognitive reframing."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "response": "It's understandable to feel anxious about speaking up. Consider that others might actually appreciate your input, and even if you stumble, most people are focused on their own contributions rather than judging yours.",
                "transparency": {
                    "techniques_applied": ["cognitive_restructuring", "perspective_taking"],
                    "reasoning_path": [
                        "Identified mind-reading cognitive distortion",
                        "Challenged assumption about others' thoughts",
                        "Offered balanced perspective",
                    ],
                    "confidence": 0.85,
                },
                "techniques_used": ["cognitive_restructuring", "perspective_taking"],
                "error": None,
            }
        }
    )

    success: bool = Field(..., description="Whether the reframing was successful")
    response: str = Field(..., description="The reframed perspective or support message")
    transparency: TransparencyData = Field(
        ..., description="Transparency data about the reframing process"
    )
    techniques_used: list[str] = Field(
        default_factory=list, description="List of CBT techniques applied"
    )
    error: str | None = Field(None, description="Error message if the request failed")


class ErrorResponse(BaseModel):
    """Standard error response."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detail": "Rate limit exceeded. Please try again in 3600 seconds.",
                "error_type": "rate_limit",
                "request_id": "req_123abc",
            }
        }
    )

    detail: str = Field(..., description="Human-readable error message")
    error_type: str | None = Field(None, description="Error classification for client handling")
    request_id: str | None = Field(None, description="Request ID for troubleshooting")


# Health check schemas
class HealthStatus(BaseModel):
    """Basic health status."""

    status: str = Field(
        ...,
        description="Service status",
        json_schema_extra={"examples": ["ok", "degraded", "error"]},
    )
    timestamp: str = Field(..., description="ISO timestamp of the check")
    service: str = Field(default="re-frame-backend", description="Service name")


class DependencyHealth(BaseModel):
    """Health status of a dependency."""

    status: str = Field(
        ...,
        description="Dependency status",
        json_schema_extra={"examples": ["ok", "error", "timeout"]},
    )
    error: str | None = Field(None, description="Error message if dependency is unhealthy")
    latency_ms: float | None = Field(None, description="Response time in milliseconds")


class DetailedHealthStatus(HealthStatus):
    """Detailed health status with dependency checks."""

    checks: dict[str, DependencyHealth] = Field(
        ..., description="Individual dependency health checks"
    )
    version: str | None = Field(None, description="Application version")


# Technique schemas
class TechniqueInfo(BaseModel):
    """Information about a CBT technique."""

    name: str = Field(..., description="Human-readable technique name")
    description: str = Field(..., description="What the technique does")
    helpful_for: list[str] = Field(..., description="Thought patterns this technique addresses")


class TechniquesResponse(BaseModel):
    """Response listing available techniques."""

    techniques: dict[str, TechniqueInfo] = Field(
        ..., description="Map of technique IDs to their information"
    )
    note: str = Field(..., description="Additional context about the techniques")


# Session schemas
class SessionInteraction(BaseModel):
    """A single interaction within a session."""

    timestamp: str = Field(..., description="ISO timestamp of the interaction")
    thought: str = Field(..., description="User's original thought")
    response: str = Field(..., description="System's reframed response")
    techniques_used: list[str] = Field(
        default_factory=list, description="Techniques applied in this interaction"
    )


class SessionHistory(BaseModel):
    """Session history data."""

    session_id: str = Field(..., description="Unique session identifier")
    created_at: str = Field(..., description="Session creation timestamp")
    last_activity: str = Field(..., description="Last activity timestamp")
    interactions: list[SessionInteraction] = Field(
        default_factory=list, description="List of interactions in this session"
    )
    total_interactions: int = Field(..., description="Total number of interactions")


class SessionHistoryResponse(BaseModel):
    """Response for session history request."""

    session: SessionHistory | None = Field(None, description="Session data if found")
    error: str | None = Field(None, description="Error message if session not found")
    note: str = Field(
        default="Session data is automatically cleaned up after 24 hours for privacy.",
        description="Privacy notice",
    )


# Performance schemas
class PerformanceMetrics(BaseModel):
    """System performance metrics."""

    avg_response_time: float = Field(..., description="Average response time in seconds")
    p95_response_time: float | None = Field(None, description="95th percentile response time")
    p99_response_time: float | None = Field(None, description="99th percentile response time")
    total_requests: int = Field(..., description="Total requests processed")
    success_rate: float = Field(..., ge=0.0, le=1.0, description="Success rate (0-1)")
    error_rate: float = Field(..., ge=0.0, le=1.0, description="Error rate (0-1)")
    requests_per_minute: float = Field(..., description="Current request rate")
    active_sessions: int = Field(..., description="Number of active sessions")
    cache_hit_rate: float | None = Field(None, ge=0.0, le=1.0, description="Cache hit rate (0-1)")


class ErrorAnalysis(BaseModel):
    """Error analysis data."""

    total_errors: int = Field(..., description="Total number of errors")
    error_rate: float = Field(..., ge=0.0, le=1.0, description="Overall error rate")
    errors_by_type: dict[str, int] = Field(..., description="Error counts by type")
    common_errors: list[dict[str, Any]] = Field(
        default_factory=list, description="Most common error patterns"
    )
    error_trend: str = Field(
        ...,
        description="Error trend direction",
        json_schema_extra={"examples": ["increasing", "decreasing", "stable"]},
    )


class PerformanceResponse(BaseModel):
    """Performance monitoring response."""

    performance: PerformanceMetrics = Field(..., description="Current performance metrics")
    errors: ErrorAnalysis = Field(..., description="Error analysis")
    note: str = Field(
        default="This endpoint should be restricted to administrators in production.",
        description="Security notice",
    )
