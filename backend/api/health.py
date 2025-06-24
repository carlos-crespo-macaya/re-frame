"""Health check endpoints."""

from datetime import UTC, datetime
import logging

from fastapi import APIRouter
import google.generativeai as genai

from api.schemas import DependencyHealth, DetailedHealthStatus, HealthStatus
from config.settings import get_settings

router = APIRouter()
logger = logging.getLogger(__name__)

# Cache startup time
STARTUP_TIME = datetime.now(UTC)


def check_google_ai_health() -> dict:
    """Check Google AI API health."""
    try:
        settings = get_settings()
        if not settings.google_ai_api_key:
            return {"status": "error", "error": "API key not configured"}

        # Quick model availability check
        genai.configure(api_key=settings.google_ai_api_key)
        models = genai.list_models()
        model_names = [m.name for m in models]

        if f"models/{settings.google_ai_model}" in model_names:
            return {"status": "ok", "model": settings.google_ai_model, "available": True}
        return {"status": "error", "error": f"Model {settings.google_ai_model} not available"}

    except Exception as e:
        logger.error(f"Google AI health check failed: {e}")
        return {"status": "error", "error": str(e)}


@router.get(
    "/",
    response_model=HealthStatus,
    summary="Basic health check",
    description="Simple health check to verify the service is running",
    tags=["Health"],
)
async def health_check():
    """Basic health check endpoint."""
    return HealthStatus(
        status="ok",
        timestamp=datetime.now(UTC).isoformat(),
        service="re-frame-backend",
    )


@router.get(
    "/detailed",
    response_model=DetailedHealthStatus,
    summary="Detailed health check",
    description="Comprehensive health check including all dependencies",
    tags=["Health"],
)
async def detailed_health_check():
    """Detailed health check with component status."""
    settings = get_settings()

    # Check dependencies
    checks = {}

    # Google AI check
    try:
        ai_health = check_google_ai_health()
        checks["google_ai"] = DependencyHealth(
            status=ai_health["status"],
            error=ai_health.get("error"),
        )
    except Exception as e:
        logger.error(f"Error checking Google AI health: {e}")
        checks["google_ai"] = DependencyHealth(
            status="error",
            error=str(e),
        )

    # Overall status
    all_ok = all(check.status == "ok" for check in checks.values())
    overall_status = "ok" if all_ok else "degraded"

    return DetailedHealthStatus(
        status=overall_status,
        timestamp=datetime.now(UTC).isoformat(),
        service="re-frame-backend",
        version=settings.api_version,
        checks=checks,
    )


@router.get(
    "/live",
    summary="Liveness probe",
    description="Kubernetes liveness probe endpoint",
    tags=["Health"],
)
async def liveness_probe():
    """Kubernetes liveness probe - checks if service is alive."""
    return {"status": "alive"}


@router.get(
    "/ready",
    summary="Readiness probe",
    description="Kubernetes readiness probe endpoint",
    tags=["Health"],
    responses={
        200: {"description": "Service is ready to accept traffic"},
        503: {"description": "Service is not ready"},
    },
)
async def readiness_probe():
    """Kubernetes readiness probe - checks if service is ready to accept requests."""
    from fastapi import Response

    # Check if all critical dependencies are available
    ai_health = check_google_ai_health()

    if ai_health["status"] != "ok":
        return Response(
            content='{"status": "not_ready", "reason": "Dependencies not available", "details": {"google_ai": '
            + str(ai_health).replace("'", '"')
            + "}}",
            status_code=503,
            media_type="application/json",
        )

    return {"status": "ready"}


@router.get(
    "/startup",
    summary="Startup probe",
    description="Kubernetes startup probe endpoint",
    tags=["Health"],
)
async def startup_probe():
    """Kubernetes startup probe - used during initial startup."""
    from fastapi import Response

    uptime = (datetime.now(UTC) - STARTUP_TIME).total_seconds()

    # Consider started after 0.1 seconds for tests, 5 seconds for production
    startup_threshold = 0.1 if uptime < 10 else 5
    if uptime < startup_threshold:
        return Response(
            content='{"status": "starting", "uptime_seconds": ' + str(uptime) + "}",
            status_code=503,
            media_type="application/json",
        )

    return {
        "status": "started",
        "startup_time": STARTUP_TIME.isoformat(),
        "uptime_seconds": uptime,
    }
