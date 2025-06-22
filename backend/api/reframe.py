"""Reframing API endpoints."""

import json
import logging
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from agents import (
    CBTFrameworkAgent,
    IntakeAgent,
    SynthesisAgent,
    observability_manager,
)
from agents.models import (
    CBTAnalysis,
    IntakeAnalysis,
    SessionResponse,
    SynthesisInput,
    SynthesisOutput,
)

router = APIRouter()
logger = logging.getLogger("api.reframe")


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
    key_points: list[str] = Field(default_factory=list)
    techniques_explained: str = ""


# Temporary session manager implementation
class TemporarySessionManager:
    """Temporary session manager until ADK is configured."""

    def __init__(self):
        self.intake_agent = IntakeAgent()
        self.cbt_agent = CBTFrameworkAgent()
        self.synthesis_agent = SynthesisAgent()

    async def process_user_input(self, thought: str) -> SessionResponse:
        """Process user thought through agents."""
        try:
            logger.info(
                f"Starting TemporarySessionManager processing for thought: '{thought[:50]}...'"
            )

            # Process through intake
            logger.info("Calling IntakeAgent...")
            intake_result = await self.intake_agent.process_user_input(thought)
            logger.info(f"IntakeAgent returned: success={intake_result.success}")

            if not intake_result.success:
                return SessionResponse(
                    success=False,
                    error=intake_result.error or "Failed to process input",
                    workflow_stage="intake",
                )

            # Get the parsed intake analysis
            if not hasattr(intake_result, "parsed_response") or not intake_result.parsed_response:
                return SessionResponse(
                    success=False,
                    error="Invalid intake response format",
                    workflow_stage="intake",
                )

            intake_analysis: IntakeAnalysis = intake_result.parsed_response

            # Apply CBT framework
            logger.info("Calling CBTFrameworkAgent...")
            cbt_result = await self.cbt_agent.apply_cbt_techniques(intake_analysis)
            logger.info(f"CBTFrameworkAgent returned: success={cbt_result.success}")

            if not cbt_result.success:
                return SessionResponse(
                    success=False,
                    error=cbt_result.error or "Failed to apply framework",
                    workflow_stage="framework",
                )

            # Get the parsed CBT analysis
            if not hasattr(cbt_result, "parsed_response") or not cbt_result.parsed_response:
                return SessionResponse(
                    success=False,
                    error="Invalid CBT response format",
                    workflow_stage="framework",
                )

            cbt_analysis: CBTAnalysis = cbt_result.parsed_response

            # Synthesize response
            synthesis_input = SynthesisInput(
                intake_analysis=intake_analysis,
                cbt_results=cbt_analysis,
                original_thought=thought,
            )

            logger.info("Calling SynthesisAgent...")
            synthesis_result = await self.synthesis_agent.create_user_response(synthesis_input)
            logger.info(f"SynthesisAgent returned: success={synthesis_result.success}")

            if not synthesis_result.success:
                return SessionResponse(
                    success=False,
                    error=synthesis_result.error or "Failed to synthesize response",
                    workflow_stage="synthesis",
                )

            # Get the parsed synthesis output
            if not hasattr(synthesis_result, "parsed_response") or not synthesis_result.parsed_response:
                return SessionResponse(
                    success=False,
                    error="Invalid synthesis response format",
                    workflow_stage="synthesis",
                )

            synthesis_output: SynthesisOutput = synthesis_result.parsed_response

            # Build the final response
            return SessionResponse(
                success=True,
                response=synthesis_output.main_response,
                transparency={
                    "techniques_applied": [
                        tech.technique_name for tech in cbt_analysis.techniques_applied
                    ],
                    "reasoning_path": {
                        "intake": intake_result.reasoning_path,
                        "cbt": cbt_result.reasoning_path,
                        "synthesis": synthesis_result.reasoning_path,
                    },
                    "stage": "complete",
                    "key_points": synthesis_output.key_points,
                    "techniques_explained": synthesis_output.techniques_explained,
                },
                crisis_flag=intake_analysis.requires_crisis_support,
            )
        except Exception as e:
            logger.error(f"Error in session processing: {e}", exc_info=True)
            return SessionResponse(
                success=False,
                error=str(e),
                workflow_stage="error",
            )

    def get_session_history(self, session_id: str) -> dict[str, Any] | None:
        """Get session history - not implemented yet."""
        return None


# Initialize session manager (in production, this would be a singleton service)
session_manager = TemporarySessionManager()


@router.post("/", response_model=ReframeResponse)
async def reframe_thought(reframe_request: ReframeRequest):
    """Process a thought for cognitive reframing using ADK session manager."""
    try:
        logger.info(f"Reframe request received: {len(reframe_request.thought)} characters")

        # Process through complete ADK workflow
        logger.info("Calling session_manager.process_user_input")
        result = await session_manager.process_user_input(reframe_request.thought)
        logger.info(f"session_manager returned: success={result.success}")

        if not result.success:
            return ReframeResponse(
                success=False,
                response="I wasn't able to process your thought. Please try rephrasing it.",
                transparency={
                    "stage": result.workflow_stage or "unknown",
                    "issue": result.error,
                },
                techniques_used=[],
                error=result.error,
            )

        # Handle crisis responses
        if result.crisis_flag:
            return ReframeResponse(
                success=True,
                response=result.response or "I notice you might be going through a particularly difficult time. Please consider reaching out to a mental health professional or crisis helpline for immediate support.",
                transparency=result.transparency,
                techniques_used=["crisis_detection"],
                error=None,
            )

        # Extract key information from transparency data
        techniques_used = result.transparency.get("techniques_applied", [])
        key_points = result.transparency.get("key_points", [])
        techniques_explained = result.transparency.get("techniques_explained", "")

        return ReframeResponse(
            success=True,
            response=result.response or "",
            transparency=result.transparency,
            techniques_used=techniques_used,
            key_points=key_points,
            techniques_explained=techniques_explained,
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
