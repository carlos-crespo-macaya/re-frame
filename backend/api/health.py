"""Health check endpoints."""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from datetime import datetime
import logging

from config.settings import get_settings
from middleware.rate_limiting import limiter, get_rate_limit

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/")
@limiter.limit(get_rate_limit())
async def health_check(request: Request):
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "re-frame API",
        "version": get_settings().api_version
    }


@router.get("/detailed")
@limiter.limit(get_rate_limit())
async def detailed_health_check(request: Request):
    """Detailed health check with component status."""
    settings = get_settings()
    
    # Check various components
    components = {
        "api": "healthy",
        "google_ai": "unknown",  # Will be checked when implemented
        "rate_limiting": "healthy",
        "logging": "healthy"
    }
    
    # Check if Google AI API key is configured
    if settings.google_ai_api_key:
        components["google_ai"] = "configured"
    else:
        components["google_ai"] = "not_configured"
    
    overall_status = "healthy" if all(
        status in ["healthy", "configured"] 
        for status in components.values()
    ) else "degraded"
    
    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "service": "re-frame API",
        "version": settings.api_version,
        "components": components,
        "configuration": {
            "model": settings.google_ai_model,
            "rate_limit": f"{settings.rate_limit_requests} requests per hour",
            "cors_origins": settings.cors_origins
        }
    }