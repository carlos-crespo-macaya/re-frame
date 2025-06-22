"""Reframing API endpoints."""

import logging
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from agents import ADKSessionManager, observability_manager

router = APIRouter()
logger = logging.getLogger(__name__)


class ReframeRequest(BaseModel):
    """Request model for reframing endpoint."""

    thought: str = Field(
        ..., min_length=5, max_length=2000, description="The thought or situation to reframe"
    )
    context: str | None = Field(
        None, max_length=500, description="Additional context about the situation"
    )


class ReframeResponse(BaseModel):
    """Response model for reframing endpoint."""

    success: bool
    response: str
    transparency: dict[str, Any]
    techniques_used: list[str]
    error: str | None = None


# Initialize ADK session manager (in production, this would be a singleton service)
session_manager = ADKSessionManager()


@router.post("/", response_model=ReframeResponse)
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
                transparency={
                    "stage": result.get("workflow_stage", "unknown"),
                    "issue": result.get("error"),
                },
                techniques_used=[],
                error=result.get("error"),
            )

        # Handle crisis responses
        if result.get("crisis_flag"):
            return ReframeResponse(
                success=True,
                response=result.get(
                    "response",
                    "I notice you might be going through a particularly difficult time. Please consider reaching out to a mental health professional or crisis helpline for immediate support.",
                ),
                transparency=result.get("transparency", {}),
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

        return ReframeResponse(
            success=True,
            response=main_response,
            transparency=result.get("transparency", {}),
            techniques_used=result.get("transparency", {}).get("techniques_applied", []),
        )

    except Exception as e:
        logger.error(f"Error in reframe endpoint: {e!s}", exc_info=True)
        return ReframeResponse(
            success=False,
            response="An unexpected error occurred. Please try again later.",
            transparency={"error": "internal_error"},
            techniques_used=[],
            error="Internal server error",
        )


@router.get("/techniques")
async def list_techniques():
    """List available CBT techniques."""
    techniques = {
        "cognitive_restructuring": {
            "name": "Cognitive Restructuring",
            "description": "Identifying and challenging negative thought patterns",
            "helpful_for": ["catastrophizing", "black-and-white thinking", "mind reading"],
        },
        "evidence_analysis": {
            "name": "Evidence For/Against",
            "description": "Examining evidence that supports or contradicts a thought",
            "helpful_for": ["assumptions", "jumping to conclusions", "negative predictions"],
        },
        "decatastrophizing": {
            "name": "Decatastrophizing",
            "description": "Reducing the perceived severity of feared outcomes",
            "helpful_for": ["worst-case scenario thinking", "anxiety about future events"],
        },
        "behavioral_experiments": {
            "name": "Behavioral Experiments",
            "description": "Testing assumptions through safe, gradual actions",
            "helpful_for": ["avoidance behaviors", "untested beliefs about social situations"],
        },
        "self_compassion": {
            "name": "Self-Compassion",
            "description": "Treating yourself with the same kindness you'd show a friend",
            "helpful_for": ["self-criticism", "perfectionism", "shame"],
        },
    }

    return {
        "techniques": techniques,
        "note": "These techniques are particularly selected for their effectiveness with AvPD-related challenges.",
    }


@router.get("/session/{session_id}/history")
async def get_session_history(session_id: str):
    """Get session history for a specific session."""
    history = session_manager.get_session_history(session_id)
    if not history:
        return {"error": "Session not found"}

    return {
        "session": history,
        "note": "Session data is automatically cleaned up after 24 hours for privacy.",
    }


@router.get("/observability/performance")
async def get_performance_metrics():
    """Get performance metrics for monitoring (admin only in production)."""
    return {
        "performance": observability_manager.get_performance_summary(),
        "errors": observability_manager.get_error_analysis(),
        "note": "This endpoint should be restricted to administrators in production.",
    }


@router.post("/observability/debug/enable")
async def enable_debug_mode():
    """Enable debug mode for detailed logging (admin only)."""
    observability_manager.enable_debug_mode()
    return {
        "message": "Debug mode enabled",
        "warning": "This should only be used for troubleshooting.",
    }


@router.post("/observability/debug/disable")
async def disable_debug_mode():
    """Disable debug mode."""
    observability_manager.disable_debug_mode()
    return {"message": "Debug mode disabled"}
