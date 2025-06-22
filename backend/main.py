"""Main FastAPI application for re-frame backend."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api import health, reframe
from config.settings import get_settings
from middleware import setup_cors, setup_logging, setup_rate_limiting
from middleware.rate_limiting import get_rate_limit, limiter

# Configure logging before creating app
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    # Startup
    logger.info("Starting re-frame API...")
    settings = get_settings()
    logger.info(f"Environment: {settings.api_title} v{settings.api_version}")

    yield

    # Shutdown
    logger.info("Shutting down re-frame API...")


# Create FastAPI app
app = FastAPI(
    title=get_settings().api_title,
    description=get_settings().api_description,
    version=get_settings().api_version,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure middleware
setup_logging(app)
setup_cors(app)
setup_rate_limiting(app)

# Include routers
app.include_router(health.router, prefix="/api/health", tags=["health"])
app.include_router(reframe.router, prefix="/api/reframe", tags=["reframe"])


@app.get("/")
@limiter.limit(get_rate_limit())
async def root(request: Request):
    """Root endpoint with basic information."""
    return {
        "service": "re-frame API",
        "version": get_settings().api_version,
        "description": "AI-assisted cognitive reframing support for AvPD",
        "endpoints": {
            "health": "/api/health",
            "docs": "/api/docs",
            "reframe": "/api/reframe"
        }
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc!s}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "request_id": getattr(request.state, "request_id", "unknown")
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=None  # Use our custom logging
    )
