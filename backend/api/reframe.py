"""API endpoints for cognitive reframing workflow."""

import sys
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Add agentic_workflow to Python path
agentic_path = Path(__file__).parent.parent.parent / "agentic_workflow"
sys.path.insert(0, str(agentic_path))

from orchestrator import POCReframeOrchestrator
from utils.prompt_manager import prompt_manager

router = APIRouter(
    prefix="/api/v1/reframe",
    tags=["Cognitive Reframing"],
)

# Initialize orchestrator once at module level
try:
    print("Initializing reframe orchestrator...")
    # Pre-download prompts
    prompt_manager.download_all_prompts()
    orchestrator = POCReframeOrchestrator()
    print("Orchestrator initialized successfully")
except Exception as e:
    print(f"Failed to initialize orchestrator: {e}")
    orchestrator = None


class ReframeRequest(BaseModel):
    """Request model for cognitive reframing."""
    message: str
    user_id: str = "anonymous"


class ReframeResponse(BaseModel):
    """Response model for cognitive reframing."""
    success: bool
    response: str
    session_state: dict[str, Any] | None = None
    pdf_url: str | None = None
    error: str | None = None


@router.post("/", response_model=ReframeResponse)
async def create_reframe_session(request: ReframeRequest) -> ReframeResponse:
    """
    Start a cognitive reframing session.
    
    This endpoint initializes the 3-agent workflow:
    1. Intake Agent - Gathers information
    2. Reframe Agent - Applies CBT techniques
    3. PDF Agent - Creates summary document
    """
    if not orchestrator:
        raise HTTPException(
            status_code=503,
            detail="Reframing service is not available. Please check logs."
        )
    
    try:
        # Run the orchestrator session
        result = await orchestrator.run_session(
            user_id=request.user_id,
            initial_message=request.message
        )
        
        # Extract response based on phase
        if result["session_state"]["crisis_detected"]:
            response_text = result.get("response", "Crisis support resources: 024 (Spain)")
        elif result["session_state"]["pdf_ready"]:
            response_text = "Your cognitive reframing session is complete. Download your summary below."
        elif result["session_state"]["reframe_done"]:
            response_text = result.get("response", "Reframing analysis complete.")
        elif result["session_state"]["collection_complete"]:
            response_text = result.get("response", "Information gathered. Processing reframe...")
        else:
            response_text = result.get("response", "Please continue sharing...")
        
        return ReframeResponse(
            success=True,
            response=response_text,
            session_state=result["session_state"],
            pdf_url=f"/api/v1/reframe/pdf/{result.get('filename')}" if result.get("filename") else None
        )
        
    except Exception as e:
        return ReframeResponse(
            success=False,
            response="An error occurred during the reframing process.",
            error=str(e)
        )


@router.post("/continue", response_model=ReframeResponse)
async def continue_reframe_session(
    request: ReframeRequest,
    session_state: dict[str, Any]
) -> ReframeResponse:
    """Continue an existing reframing session with additional input."""
    if not orchestrator:
        raise HTTPException(
            status_code=503,
            detail="Reframing service is not available."
        )
    
    # For POC, we'll need to modify orchestrator to support continuing sessions
    # For now, return a message indicating this needs implementation
    return ReframeResponse(
        success=False,
        response="Session continuation not yet implemented in POC.",
        error="Feature under development"
    )


@router.get("/health")
async def reframe_health() -> dict[str, str]:
    """Check if the reframing service is healthy."""
    if orchestrator:
        return {"status": "healthy", "service": "cognitive-reframing"}
    else:
        raise HTTPException(
            status_code=503,
            detail="Reframing service is not initialized"
        )