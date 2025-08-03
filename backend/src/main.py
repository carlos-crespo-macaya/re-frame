"""
CBT Reframing Assistant API

This is the main FastAPI application file that sets up the API server.
It includes routers for text and voice endpoints and handles basic app configuration.
"""

import asyncio
import os
import warnings
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.models.api import HealthCheckResponse, UIFeatureFlags
from src.text.router import router as text_router
from src.utils.feature_flags.service import create_feature_flag_service
from src.utils.logging import get_logger, setup_logging
from src.utils.performance_monitor import get_performance_monitor
from src.utils.session_manager import session_manager
from src.voice.router import router as voice_router
from src.voice.session_manager import voice_session_manager

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

# Set up logging
setup_logging(log_level=os.getenv("LOG_LEVEL", "INFO"))
logger = get_logger(__name__)

# Load environment variables
load_dotenv()
logger.info("application_started", app_name="CBT Reframing Assistant")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan with startup and shutdown events."""
    # Startup
    logger.info("starting_session_manager")
    await session_manager.start()
    logger.info("session_manager_started")

    # Start voice session manager
    logger.info("starting_voice_session_manager")
    await voice_session_manager.start()
    logger.info("voice_session_manager_started")

    # Initialize feature flags service
    logger.info("initializing_feature_flags_service")
    app.state.feature_flags_service = create_feature_flag_service()
    logger.info("feature_flags_service_initialized")

    # Start performance monitoring task
    performance_monitor = get_performance_monitor()
    monitor_task = asyncio.create_task(performance_monitor.log_periodic_summary())
    app.state.monitor_task = monitor_task
    logger.info("performance_monitoring_started")

    try:
        yield
    finally:
        # Shutdown feature flags service
        if hasattr(app.state, "feature_flags_service"):
            logger.info("shutting_down_feature_flags_service")
            app.state.feature_flags_service.close()
            logger.info("feature_flags_service_shutdown")

    # Shutdown
    logger.info("stopping_performance_monitor")
    if hasattr(app.state, "monitor_task"):
        app.state.monitor_task.cancel()
        try:
            await app.state.monitor_task
        except asyncio.CancelledError:
            logger.info("performance_monitor_cancelled")

    logger.info("stopping_session_manager")
    await session_manager.stop()

    logger.info("stopping_voice_session_manager")
    await voice_session_manager.stop()

    logger.info("application_shutdown")


# FastAPI app
app = FastAPI(
    title="CBT Reframing Assistant API",
    description="Cognitive Behavioral Therapy assistant powered by Google's ADK",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS based on environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
if ENVIRONMENT == "production":
    allowed_origins = [
        "https://re-frame.social",
        "https://www.re-frame.social",
    ]
    # Use regex pattern for Cloud Run URLs
    cloud_run_origin_regex = (
        r"https://re-frame-(frontend|backend)-[a-z0-9]+-[a-z0-9-]+\.run\.app"
    )
else:
    allowed_origins = [
        "http://localhost:3000",  # Frontend dev server
        "http://127.0.0.1:3000",  # Alternative localhost
        "http://frontend:3000",  # Docker service name
    ]

logger.info("cors_configured", environment=ENVIRONMENT, origins=allowed_origins)

# Configure CORS middleware
cors_config = {
    "allow_origins": allowed_origins,
    "allow_credentials": True,
    "allow_methods": ["GET", "POST", "OPTIONS", "HEAD", "DELETE"],
    "allow_headers": ["*"],
    "expose_headers": ["X-Session-Id", "X-Phase-Status"],
}

# Add regex pattern for production Cloud Run URLs
if ENVIRONMENT == "production":
    cors_config["allow_origin_regex"] = cloud_run_origin_regex

app.add_middleware(CORSMiddleware, **cors_config)

# Include routers
app.include_router(text_router)
app.include_router(voice_router)

STATIC_DIR = Path("static")
# Only mount static files if the directory exists
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", summary="Root endpoint", operation_id="getRoot")
async def root():
    """Serves the index.html or API info"""
    index_path = Path(STATIC_DIR) / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "CBT Assistant API", "docs": "/docs", "health": "/health"}


@app.get(
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


@app.get(
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


@app.get(
    "/api/metrics",
    summary="Performance metrics",
    operation_id="getMetrics",
)
async def get_metrics():
    """Get performance metrics."""
    performance_monitor = get_performance_monitor()
    return performance_monitor.get_metrics()


# Main entry point
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=bool(os.getenv("RELOAD", "true").lower() == "true"),
    )
