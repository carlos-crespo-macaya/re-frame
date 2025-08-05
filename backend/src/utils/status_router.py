"""FastAPI router for status and feature flags endpoints."""

from datetime import UTC, datetime

from fastapi import APIRouter, Request

from src.models.api import HealthCheckResponse, UIFeatureFlags
from src.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api", tags=["status"])


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Health check",
    operation_id="getHealthCheck",
)
async def health_check() -> HealthCheckResponse:
    """Health check endpoint for Cloud Run"""
    return HealthCheckResponse(
        status="healthy",
        service="CBT Reframing Assistant API",
        version="1.0.0",
        timestamp=datetime.now(UTC).isoformat(),
    )


@router.get(
    "/feature-flags/ui",
    response_model=UIFeatureFlags,
    summary="Get UI feature flags",
    operation_id="getUiFeatureFlags",
)
async def get_ui_feature_flags(request: Request) -> UIFeatureFlags:
    """Return the UI feature flags for gating interfaces."""
    service = request.app.state.feature_flags_service
    flags = service.get_ui_flags()
    return UIFeatureFlags(**flags.to_dict())
