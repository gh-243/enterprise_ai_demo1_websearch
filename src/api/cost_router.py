"""
Cost tracking API router.

Provides endpoints to access cost and usage metrics.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel, Field

from src.infra.middleware import CostTrackingMiddleware, get_middleware_instance as _get_middleware_instance


def get_middleware_instance() -> CostTrackingMiddleware:
    """Get the middleware instance dependency."""
    instance = _get_middleware_instance()
    if instance is None:
        raise HTTPException(
            status_code=500,
            detail="Cost tracking middleware not initialized"
        )
    return instance


class CostSummaryResponse(BaseModel):
    """Response model for cost summary."""
    total_requests: int = Field(..., description="Total number of requests")
    requests_with_llm: int = Field(..., description="Requests that used LLM")
    total_cost_usd: float = Field(..., description="Total cost in USD")
    avg_cost_per_request: float = Field(..., description="Average cost per LLM request")
    models_used: dict = Field(..., description="Models used and request counts")
    cost_by_model: dict = Field(..., description="Cost breakdown by model")
    time_range: dict = Field(..., description="Time range of analyzed requests")


class RequestMetricsResponse(BaseModel):
    """Response model for individual request metrics."""
    request_id: str
    path: str
    method: str
    status_code: int
    latency_ms: float
    model: Optional[str] = None
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float = 0.0
    timestamp: str


# Router
cost_router = APIRouter(prefix="/v1/costs", tags=["costs"])





@cost_router.get("/latest", response_model=CostSummaryResponse)
async def get_latest_costs(
    limit: int = 100,
    middleware: CostTrackingMiddleware = Depends(get_middleware_instance)
) -> CostSummaryResponse:
    """
    Get cost summary for the most recent requests.
    
    Args:
        limit: Number of recent requests to analyze (default: 100, max: 1000)
        
    Returns:
        Cost summary with statistics and breakdowns
    """
    # Validate limit
    if limit < 1 or limit > 1000:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 1000"
        )
    
    try:
        summary = middleware.get_cost_summary(limit=limit)
        return CostSummaryResponse(**summary)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve cost summary: {str(e)}"
        )


@cost_router.get("/requests", response_model=list[RequestMetricsResponse])
async def get_recent_requests(
    limit: int = 50,
    middleware: CostTrackingMiddleware = Depends(get_middleware_instance)
) -> list[RequestMetricsResponse]:
    """
    Get detailed metrics for recent requests.
    
    Args:
        limit: Number of recent requests to return (default: 50, max: 500)
        
    Returns:
        List of request metrics
    """
    # Validate limit
    if limit < 1 or limit > 500:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 500"
        )
    
    try:
        recent_requests = middleware.get_recent_requests(limit=limit)
        
        return [
            RequestMetricsResponse(
                request_id=req["request_id"],
                path=req["path"],
                method=req["method"],
                status_code=req["status_code"],
                latency_ms=req["latency_ms"],
                model=req.get("model"),
                tokens_in=req.get("tokens_in", 0),
                tokens_out=req.get("tokens_out", 0),
                cost_usd=req.get("cost_usd", 0.0),
                timestamp=req["timestamp"].isoformat() if hasattr(req["timestamp"], 'isoformat') else str(req["timestamp"])
            )
            for req in recent_requests
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve request metrics: {str(e)}"
        )


@cost_router.get("/health")
async def cost_health_check(middleware: CostTrackingMiddleware = Depends(get_middleware_instance)):
    """
    Health check for cost tracking functionality.
    
    Returns:
        Status of cost tracking system
    """
    try:
        buffer_size = len(middleware.recent_requests)
        max_buffer_size = middleware.buffer_size
        
        return {
            "status": "healthy",
            "buffer_usage": f"{buffer_size}/{max_buffer_size}",
            "buffer_utilization": round((buffer_size / max_buffer_size) * 100, 1)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }