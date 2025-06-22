"""Reframing API endpoints."""

import logging
from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from agents import CBTFrameworkAgent, IntakeAgent, SynthesisAgent
from middleware.rate_limiting import get_rate_limit, limiter

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


# Initialize agents (in production, these would be managed differently)
intake_agent = IntakeAgent()
cbt_agent = CBTFrameworkAgent()
synthesis_agent = SynthesisAgent()


@router.post("/", response_model=ReframeResponse)
@limiter.limit(get_rate_limit())
async def reframe_thought(request: Request, reframe_request: ReframeRequest):
    """Process a thought for cognitive reframing."""
    try:
        logger.info(f"Reframe request received: {len(reframe_request.thought)} characters")

        # Step 1: Intake processing
        intake_result = await intake_agent.process_user_input(reframe_request.thought)

        if not intake_result.get("success"):
            return ReframeResponse(
                success=False,
                response="I wasn't able to process your thought. Please try rephrasing it.",
                transparency={"stage": "intake", "issue": intake_result.get("error")},
                techniques_used=[],
                error=intake_result.get("error"),
            )

        # Check for crisis content
        if intake_result.get("requires_crisis_support"):
            return ReframeResponse(
                success=True,
                response="I notice you might be going through a particularly difficult time. While I can offer CBT-based perspectives, please consider reaching out to a mental health professional or crisis helpline for immediate support.",
                transparency={"stage": "intake", "crisis_detected": True},
                techniques_used=["crisis_detection"],
                error=None,
            )

        # Step 2: Apply CBT techniques
        cbt_result = await cbt_agent.apply_cbt_techniques(intake_result)

        if not cbt_result.get("success"):
            return ReframeResponse(
                success=False,
                response="I encountered an issue while processing your thought. Please try again.",
                transparency={"stage": "cbt_framework", "issue": cbt_result.get("error")},
                techniques_used=[],
                error=cbt_result.get("error"),
            )

        # Step 3: Synthesize response
        synthesis_result = await synthesis_agent.create_user_response(cbt_result)

        if not synthesis_result.get("success"):
            return ReframeResponse(
                success=False,
                response="I had trouble creating a response. Please try again.",
                transparency={"stage": "synthesis", "issue": synthesis_result.get("error")},
                techniques_used=[],
                error=synthesis_result.get("error"),
            )

        # Extract response data
        response_data = synthesis_result.get("response", {})

        return ReframeResponse(
            success=True,
            response=response_data.get("main_response", ""),
            transparency={
                "intake": intake_result.get("reasoning_path", {}),
                "cbt_analysis": cbt_result.get("reasoning_path", {}),
                "synthesis": synthesis_result.get("reasoning_path", {}),
                "model_used": synthesis_result.get("model_used", ""),
            },
            techniques_used=response_data.get("techniques_explained", []),
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
@limiter.limit(get_rate_limit())
async def list_techniques(request: Request):
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
