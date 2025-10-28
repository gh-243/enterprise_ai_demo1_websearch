"""
ASGI middleware for request tracking and cost accounting.

This middleware provides:
- Request ID/trace ID generation
- LLM metrics capture and cost calculation
- Structured JSON logging per request
- In-memory cost tracking for recent requests
"""

import json
import logging
import time
import uuid
from collections import deque
from typing import Callable, Dict, Any, Optional, Deque
from dataclasses import dataclass, asdict
from datetime import datetime

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.infra.pricing import calculate_cost

# Global middleware instance for singleton access
_middleware_instance: Optional['CostTrackingMiddleware'] = None


@dataclass
class RequestMetrics:
    """Metrics for a single request."""
    request_id: str
    path: str
    method: str
    status_code: int
    latency_ms: float
    model: Optional[str] = None
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float = 0.0
    timestamp: datetime = None
    
    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class CostTrackingMiddleware(BaseHTTPMiddleware):
    """
    ASGI middleware that tracks request metrics and LLM costs.
    
    Features:
    - Generates unique request/trace IDs
    - Captures LLM usage metrics from request state
    - Calculates costs using pricing table
    - Logs structured JSON per request
    - Maintains in-memory buffer of recent requests
    """
    
    def __init__(self, app: Callable, buffer_size: int = 1000):
        """
        Initialize the middleware.
        
        Args:
            app: ASGI application
            buffer_size: Maximum number of requests to keep in memory
        """
        global _middleware_instance
        super().__init__(app)
        self.buffer_size = buffer_size
        self.recent_requests: Deque[RequestMetrics] = deque(maxlen=buffer_size)
        self.logger = logging.getLogger(__name__)
        _middleware_instance = self
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and capture metrics.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain
            
        Returns:
            HTTP response with added headers
        """
        # Generate request ID
        request_id = str(uuid.uuid4())
        
        # Store request ID in request state for use by handlers
        request.state.request_id = request_id
        request.state.llm_metrics = {}
        
        # Record start time
        start_time = time.time()
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract LLM metrics from request state
            llm_metrics = getattr(request.state, 'llm_metrics', {})
            
            # Calculate cost if we have LLM metrics
            cost_usd = 0.0
            if llm_metrics.get('model') and (llm_metrics.get('tokens_in') or llm_metrics.get('tokens_out')):
                cost_usd = calculate_cost(
                    model=llm_metrics.get('model', ''),
                    tokens_in=llm_metrics.get('tokens_in', 0),
                    tokens_out=llm_metrics.get('tokens_out', 0)
                )
            
            # Create metrics record
            metrics = RequestMetrics(
                request_id=request_id,
                path=str(request.url.path),
                method=request.method,
                status_code=response.status_code,
                latency_ms=round(latency_ms, 2),
                model=llm_metrics.get('model'),
                tokens_in=llm_metrics.get('tokens_in', 0),
                tokens_out=llm_metrics.get('tokens_out', 0),
                cost_usd=cost_usd
            )
            
            # Store in buffer
            self.recent_requests.append(metrics)
            
            # Log structured JSON
            self._log_request_metrics(metrics)
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Cost-USD"] = str(cost_usd)
            
            return response
            
        except Exception as e:
            # Calculate latency even for errors
            latency_ms = (time.time() - start_time) * 1000
            
            # Create error metrics record
            metrics = RequestMetrics(
                request_id=request_id,
                path=str(request.url.path),
                method=request.method,
                status_code=500,
                latency_ms=round(latency_ms, 2)
            )
            
            # Store in buffer
            self.recent_requests.append(metrics)
            
            # Log error
            self._log_request_error(metrics, e)
            
            # Re-raise the exception
            raise
    
    def _log_request_metrics(self, metrics: RequestMetrics) -> None:
        """
        Log request metrics as structured JSON.
        
        Args:
            metrics: Request metrics to log
        """
        log_data = {
            "event": "request_completed",
            "request_id": metrics.request_id,
            "path": metrics.path,
            "method": metrics.method,
            "status": metrics.status_code,
            "latency_ms": metrics.latency_ms,
            "timestamp": metrics.timestamp.isoformat(),
        }
        
        # Add LLM metrics if available
        if metrics.model:
            log_data.update({
                "model": metrics.model,
                "tokens_in": metrics.tokens_in,
                "tokens_out": metrics.tokens_out,
                "cost_usd": metrics.cost_usd
            })
        
        self.logger.info(json.dumps(log_data))
    
    def _log_request_error(self, metrics: RequestMetrics, error: Exception) -> None:
        """
        Log request error as structured JSON.
        
        Args:
            metrics: Request metrics
            error: Exception that occurred
        """
        log_data = {
            "event": "request_error",
            "request_id": metrics.request_id,
            "path": metrics.path,
            "method": metrics.method,
            "latency_ms": metrics.latency_ms,
            "error": str(error),
            "error_type": type(error).__name__,
            "timestamp": metrics.timestamp.isoformat(),
        }
        
        self.logger.error(json.dumps(log_data))
    
    def get_recent_requests(self, limit: int = 100) -> list[Dict[str, Any]]:
        """
        Get recent request metrics.
        
        Args:
            limit: Maximum number of requests to return
            
        Returns:
            List of request metrics as dictionaries
        """
        recent = list(self.recent_requests)[-limit:]
        return [asdict(metrics) for metrics in recent]
    
    def get_cost_summary(self, limit: int = 100) -> Dict[str, Any]:
        """
        Get cost summary for recent requests.
        
        Args:
            limit: Number of recent requests to analyze
            
        Returns:
            Cost summary statistics
        """
        recent = list(self.recent_requests)[-limit:]
        
        if not recent:
            return {
                "total_requests": 0,
                "total_cost_usd": 0.0,
                "avg_cost_per_request": 0.0,
                "models_used": {},
                "cost_by_model": {}
            }
        
        total_cost = sum(r.cost_usd for r in recent)
        requests_with_cost = [r for r in recent if r.cost_usd > 0]
        
        # Calculate model usage statistics
        models_used = {}
        cost_by_model = {}
        
        for request in requests_with_cost:
            model = request.model or "unknown"
            models_used[model] = models_used.get(model, 0) + 1
            cost_by_model[model] = cost_by_model.get(model, 0.0) + request.cost_usd
        
        return {
            "total_requests": len(recent),
            "requests_with_llm": len(requests_with_cost),
            "total_cost_usd": round(total_cost, 6),
            "avg_cost_per_request": round(total_cost / len(requests_with_cost), 6) if requests_with_cost else 0.0,
            "models_used": models_used,
            "cost_by_model": {k: round(v, 6) for k, v in cost_by_model.items()},
            "time_range": {
                "from": recent[0].timestamp.isoformat() if recent else None,
                "to": recent[-1].timestamp.isoformat() if recent else None
            }
        }


def get_middleware_instance() -> Optional['CostTrackingMiddleware']:
    """Get the global middleware instance."""
    return _middleware_instance