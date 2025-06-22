"""Reframing API endpoints."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, status

from agents import ADKSessionManager, observability_manager
from api.schemas import (
    ReframeRequest,
    ReframeResponse,
    TechniquesResponse,
    TechniqueInfo,
    SessionHistoryResponse,
    SessionHistory,
    SessionInteraction,
    PerformanceResponse,
    PerformanceMetrics,
    ErrorAnalysis,
    TransparencyData,
)

router = APIRouter()
logger = logging.getLogger(__name__)


# Initialize ADK session manager (in production, this would be a singleton service)
session_manager = ADKSessionManager()


@router.post(
    "/",
    response_model=ReframeResponse,
    summary="Reframe a thought",
    description="Process a thought through cognitive reframing using multiple therapeutic frameworks",
    responses={
        200: {
            "description": "Successful reframing",
            "model": ReframeResponse,
        },
        422: {
            "description": "Validation error - thought too short/long or invalid format",
        },
        429: {
            "description": "Rate limit exceeded - too many requests",
        },
    },
    tags=["Cognitive Reframing"],
)
async def reframe_thought(reframe_request: ReframeRequest):
    """Process a thought for cognitive reframing using ADK session manager."""
    try:
        logger.info(f"Reframe request received: {len(reframe_request.thought)} characters")

        # Process through complete ADK workflow
        result = await session_manager.process_user_input(reframe_request.thought)

        if not result["success"]:
            return ReframeResponse(
                success=False,
                response="I wasn't able to process your thought. Please try rephrasing it.",
                transparency=TransparencyData(
                    stage=result.get("workflow_stage", "unknown"),
                    techniques_applied=[],
                ),
                techniques_used=[],
                error=result.get("error"),
            )

        # Handle crisis responses
        if result.get("crisis_flag"):
            return ReframeResponse(
                success=True,
                response=result.get("response", "I notice you might be going through a particularly difficult time. Please consider reaching out to a mental health professional or crisis helpline for immediate support."),
                transparency=TransparencyData(
                    crisis_detected=True,
                    techniques_applied=["crisis_detection"],
                ),
                techniques_used=["crisis_detection"],
                error=None,
            )

        # Parse the successful response
        response_text = result.get("response", "")
        if isinstance(response_text, str):
            try:
                import json

                response_data = json.loads(response_text)
                main_response = response_data.get("main_response", response_text)
            except json.JSONDecodeError:
                main_response = response_text
        else:
            main_response = str(response_text)

        # Extract transparency data
        transparency_raw = result.get("transparency", {})
        transparency = TransparencyData(
            techniques_applied=transparency_raw.get("techniques_applied", []),
            reasoning_path=transparency_raw.get("reasoning_path", []),
            confidence=transparency_raw.get("confidence"),
            stage=transparency_raw.get("stage"),
        )
        
        return ReframeResponse(
            success=True,
            response=main_response,
            transparency=transparency,
            techniques_used=transparency.techniques_applied,
        )

    except Exception as e:
        logger.error(f"Error in reframe endpoint: {e!s}", exc_info=True)
        return ReframeResponse(
            success=False,
            response="An unexpected error occurred. Please try again later.",
            transparency=TransparencyData(
                stage="error",
                techniques_applied=[],
            ),
            techniques_used=[],
            error="Internal server error",
        )


@router.get(
    "/techniques",
    response_model=TechniquesResponse,
    summary="List available techniques",
    description="Get a list of all cognitive behavioral therapy techniques available in the system",
    tags=["Reference"],
)
async def list_techniques():
    """List available CBT techniques."""
    techniques = {
        "cognitive_restructuring": TechniqueInfo(
            name="Cognitive Restructuring",
            description="Identifying and challenging negative thought patterns",
            helpful_for=["catastrophizing", "black-and-white thinking", "mind reading"],
        ),
        "evidence_analysis": TechniqueInfo(
            name="Evidence For/Against",
            description="Examining evidence that supports or contradicts a thought",
            helpful_for=["assumptions", "jumping to conclusions", "negative predictions"],
        ),
        "decatastrophizing": TechniqueInfo(
            name="Decatastrophizing",
            description="Reducing the perceived severity of feared outcomes",
            helpful_for=["worst-case scenario thinking", "anxiety about future events"],
        ),
        "behavioral_experiments": TechniqueInfo(
            name="Behavioral Experiments",
            description="Testing assumptions through safe, gradual actions",
            helpful_for=["avoidance behaviors", "untested beliefs about social situations"],
        ),
        "self_compassion": TechniqueInfo(
            name="Self-Compassion",
            description="Treating yourself with the same kindness you'd show a friend",
            helpful_for=["self-criticism", "perfectionism", "shame"],
        ),
    }

    return TechniquesResponse(
        techniques=techniques,
        note="These techniques are particularly selected for their effectiveness with AvPD-related challenges.",
    )


@router.get(
    "/session/{session_id}/history",
    response_model=SessionHistoryResponse,
    summary="Get session history",
    description="Retrieve the interaction history for a specific session",
    responses={
        200: {
            "description": "Session history retrieved successfully",
        },
        404: {
            "description": "Session not found",
        },
    },
    tags=["Sessions"],
)
async def get_session_history(session_id: str):
    """Get session history for a specific session."""
    history = session_manager.get_session_history(session_id)
    
    if not history:
        return SessionHistoryResponse(
            session=None,
            error="Session not found",
        )
    
    # Convert raw history to schema
    interactions = [
        SessionInteraction(
            timestamp=interaction.get("timestamp", ""),
            thought=interaction.get("thought", ""),
            response=interaction.get("response", ""),
            techniques_used=interaction.get("techniques_used", []),
        )
        for interaction in history.get("interactions", [])
    ]
    
    session_data = SessionHistory(
        session_id=history.get("session_id", session_id),
        created_at=history.get("created_at", ""),
        last_activity=history.get("last_activity", ""),
        interactions=interactions,
        total_interactions=len(interactions),
    )
    
    return SessionHistoryResponse(
        session=session_data,
        error=None,
    )


@router.get(
    "/observability/performance",
    response_model=PerformanceResponse,
    summary="Get performance metrics",
    description="Retrieve system performance metrics and error analysis (admin only in production)",
    tags=["Monitoring"],
)
async def get_performance_metrics():
    """Get performance metrics for monitoring (admin only in production)."""
    perf_data = observability_manager.get_performance_summary()
    error_data = observability_manager.get_error_analysis()
    
    # Convert to schema
    performance = PerformanceMetrics(
        avg_response_time=perf_data.get("avg_response_time", 0.0),
        p95_response_time=perf_data.get("p95_response_time"),
        p99_response_time=perf_data.get("p99_response_time"),
        total_requests=perf_data.get("total_requests", 0),
        success_rate=perf_data.get("success_rate", 0.0),
        error_rate=perf_data.get("error_rate", 0.0),
        requests_per_minute=perf_data.get("requests_per_minute", 0.0),
        active_sessions=perf_data.get("active_sessions", 0),
        cache_hit_rate=perf_data.get("cache_hit_rate"),
    )
    
    errors = ErrorAnalysis(
        total_errors=error_data.get("total_errors", 0),
        error_rate=error_data.get("error_rate", 0.0),
        errors_by_type=error_data.get("errors_by_type", {}),
        common_errors=error_data.get("common_errors", []),
        error_trend=error_data.get("error_trend", "stable"),
    )
    
    return PerformanceResponse(
        performance=performance,
        errors=errors,
    )


@router.post(
    "/observability/debug/enable",
    summary="Enable debug mode",
    description="Enable detailed debug logging (admin only)",
    tags=["Monitoring"],
)
async def enable_debug_mode():
    """Enable debug mode for detailed logging (admin only)."""
    observability_manager.enable_debug_mode()
    return {
        "message": "Debug mode enabled",
        "warning": "This should only be used for troubleshooting.",
    }


@router.post(
    "/observability/debug/disable",
    summary="Disable debug mode",
    description="Disable debug logging",
    tags=["Monitoring"],
)
async def disable_debug_mode():
    """Disable debug mode."""
    observability_manager.disable_debug_mode()
    return {"message": "Debug mode disabled"}
