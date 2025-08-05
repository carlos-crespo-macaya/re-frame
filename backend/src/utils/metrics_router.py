"""FastAPI router for metrics endpoints."""

from fastapi import APIRouter

from src.utils.performance_monitor import get_performance_monitor

router = APIRouter(prefix="/api", tags=["metrics"])


@router.get(
    "/metrics",
    summary="Performance metrics",
    operation_id="getMetrics",
)
async def get_metrics():
    """Get performance metrics."""
    performance_monitor = get_performance_monitor()
    return performance_monitor.get_metrics()
