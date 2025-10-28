"""
Tests for middleware and cost accounting functionality.

Tests structured logging, cost calculations, and cost API endpoints.
"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime
import logging
from io import StringIO

from src.app.app import app
from src.infra.middleware import CostTrackingMiddleware, RequestMetrics
from src.infra.pricing import calculate_cost, get_supported_models, get_model_pricing
from src.providers.base import LLMResponse


class TestPricingCalculations:
    """Test the pricing calculation functionality."""
    
    def test_calculate_cost_gpt4o_mini(self):
        """Test cost calculation for GPT-4o-mini."""
        cost = calculate_cost("gpt-4o-mini", 1000, 500)
        expected = (1000/1000 * 0.000150) + (500/1000 * 0.000600)
        assert cost == pytest.approx(expected, abs=1e-6)
        assert cost == pytest.approx(0.00045, abs=1e-6)
    
    def test_calculate_cost_gpt4o(self):
        """Test cost calculation for GPT-4o."""
        cost = calculate_cost("gpt-4o", 2000, 1000)
        expected = (2000/1000 * 0.0025) + (1000/1000 * 0.010)
        assert cost == pytest.approx(expected, abs=1e-6)
        assert cost == pytest.approx(0.015, abs=1e-6)
    
    def test_calculate_cost_claude(self):
        """Test cost calculation for Claude."""
        cost = calculate_cost("claude-3-5-sonnet-20241022", 1500, 800)
        expected = (1500/1000 * 0.003) + (800/1000 * 0.015)
        assert cost == pytest.approx(expected, abs=1e-6)
        assert cost == pytest.approx(0.0165, abs=1e-6)
    
    def test_calculate_cost_unknown_model(self):
        """Test cost calculation for unknown model returns 0."""
        cost = calculate_cost("unknown-model", 1000, 500)
        assert cost == 0.0
    
    def test_calculate_cost_empty_model(self):
        """Test cost calculation for empty model name."""
        cost = calculate_cost("", 1000, 500)
        assert cost == 0.0
    
    def test_calculate_cost_zero_tokens(self):
        """Test cost calculation with zero tokens."""
        cost = calculate_cost("gpt-4o-mini", 0, 0)
        assert cost == 0.0
    
    def test_model_name_normalization(self):
        """Test that model names are normalized correctly."""
        # Test with various prefixes and formats
        cost1 = calculate_cost("gpt-4o-mini", 1000, 500)
        cost2 = calculate_cost("openai/gpt-4o-mini", 1000, 500)
        cost3 = calculate_cost("GPT-4O-MINI", 1000, 500)
        
        assert cost1 == cost2 == cost3
    
    def test_get_supported_models(self):
        """Test getting supported models."""
        models = get_supported_models()
        assert isinstance(models, dict)
        assert "gpt-4o-mini" in models
        assert "claude-3-5-sonnet-20241022" in models
        
        # Verify pricing structure
        gpt_pricing = models["gpt-4o-mini"]
        assert hasattr(gpt_pricing, 'input_cost_per_1k_tokens')
        assert hasattr(gpt_pricing, 'output_cost_per_1k_tokens')
        assert gpt_pricing.provider == "openai"
    
    def test_get_model_pricing(self):
        """Test getting pricing for specific model."""
        pricing = get_model_pricing("gpt-4o-mini")
        assert pricing is not None
        assert pricing.input_cost_per_1k_tokens == 0.000150
        assert pricing.output_cost_per_1k_tokens == 0.000600
        
        # Test unknown model
        unknown_pricing = get_model_pricing("unknown-model")
        assert unknown_pricing is None


class TestRequestMetrics:
    """Test the RequestMetrics dataclass."""
    
    def test_request_metrics_creation(self):
        """Test creating RequestMetrics."""
        metrics = RequestMetrics(
            request_id="test-123",
            path="/v1/chat",
            method="POST",
            status_code=200,
            latency_ms=150.5,
            model="gpt-4o-mini",
            tokens_in=100,
            tokens_out=50,
            cost_usd=0.001
        )
        
        assert metrics.request_id == "test-123"
        assert metrics.path == "/v1/chat"
        assert metrics.method == "POST"
        assert metrics.status_code == 200
        assert metrics.latency_ms == 150.5
        assert metrics.model == "gpt-4o-mini"
        assert metrics.tokens_in == 100
        assert metrics.tokens_out == 50
        assert metrics.cost_usd == 0.001
        assert isinstance(metrics.timestamp, datetime)
    
    def test_request_metrics_defaults(self):
        """Test RequestMetrics with default values."""
        metrics = RequestMetrics(
            request_id="test-456",
            path="/health",
            method="GET",
            status_code=200,
            latency_ms=10.0
        )
        
        assert metrics.model is None
        assert metrics.tokens_in == 0
        assert metrics.tokens_out == 0
        assert metrics.cost_usd == 0.0
        assert metrics.timestamp is not None


class TestCostTrackingMiddleware:
    """Test the cost tracking middleware."""
    
    @pytest.fixture
    def middleware(self):
        """Create middleware instance for testing."""
        mock_app = Mock()
        return CostTrackingMiddleware(mock_app, buffer_size=10)
    
    def test_middleware_initialization(self, middleware):
        """Test middleware initialization."""
        assert middleware.buffer_size == 10
        assert len(middleware.recent_requests) == 0
        assert middleware.logger is not None
    
    def test_get_recent_requests_empty(self, middleware):
        """Test getting recent requests when buffer is empty."""
        requests = middleware.get_recent_requests(limit=5)
        assert requests == []
    
    def test_get_cost_summary_empty(self, middleware):
        """Test getting cost summary when buffer is empty."""
        summary = middleware.get_cost_summary(limit=5)
        expected = {
            "total_requests": 0,
            "total_cost_usd": 0.0,
            "avg_cost_per_request": 0.0,
            "models_used": {},
            "cost_by_model": {}
        }
        assert summary["total_requests"] == expected["total_requests"]
        assert summary["total_cost_usd"] == expected["total_cost_usd"]
        assert summary["avg_cost_per_request"] == expected["avg_cost_per_request"]
        assert summary["models_used"] == expected["models_used"]
        assert summary["cost_by_model"] == expected["cost_by_model"]
    
    def test_buffer_management(self, middleware):
        """Test that buffer respects max size."""
        # Add more requests than buffer size
        for i in range(15):
            metrics = RequestMetrics(
                request_id=f"test-{i}",
                path="/test",
                method="GET",
                status_code=200,
                latency_ms=10.0
            )
            middleware.recent_requests.append(metrics)
        
        # Should only keep last 10 requests
        assert len(middleware.recent_requests) == 10
        assert middleware.recent_requests[0].request_id == "test-5"
        assert middleware.recent_requests[-1].request_id == "test-14"
    
    def test_cost_summary_with_data(self, middleware):
        """Test cost summary with actual data."""
        # Add test requests
        requests_data = [
            ("gpt-4o-mini", 1000, 500, 0.0045),
            ("gpt-4o", 2000, 1000, 0.015),
            ("gpt-4o-mini", 500, 250, 0.000225),
            (None, 0, 0, 0.0)  # Non-LLM request
        ]
        
        for model, tokens_in, tokens_out, cost in requests_data:
            metrics = RequestMetrics(
                request_id=f"test-{model or 'none'}",
                path="/v1/chat" if model else "/health",
                method="POST",
                status_code=200,
                latency_ms=100.0,
                model=model,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                cost_usd=cost
            )
            middleware.recent_requests.append(metrics)
        
        summary = middleware.get_cost_summary(limit=10)
        
        assert summary["total_requests"] == 4
        assert summary["requests_with_llm"] == 3
        assert summary["total_cost_usd"] == pytest.approx(0.019725, abs=1e-6)
        assert summary["avg_cost_per_request"] == pytest.approx(0.006575, abs=1e-6)
        assert summary["models_used"]["gpt-4o-mini"] == 2
        assert summary["models_used"]["gpt-4o"] == 1
        assert summary["cost_by_model"]["gpt-4o-mini"] == pytest.approx(0.004725, abs=1e-6)
        assert summary["cost_by_model"]["gpt-4o"] == pytest.approx(0.015, abs=1e-6)


class TestMiddlewareIntegration:
    """Test middleware integration with FastAPI."""
    
    def setup_method(self):
        """Setup test client."""
        self.client = TestClient(app)
    
    def test_middleware_adds_headers(self):
        """Test that middleware adds request ID and cost headers."""
        response = self.client.get("/health")
        
        assert response.status_code == 200
        assert "X-Request-ID" in response.headers
        assert "X-Cost-USD" in response.headers
        
        # Health endpoint should have zero cost
        assert response.headers["X-Cost-USD"] == "0.0"
        
        # Request ID should be a valid UUID format
        request_id = response.headers["X-Request-ID"]
        assert len(request_id) == 36  # UUID format
        assert request_id.count("-") == 4
    
    @patch("src.api.chat_router.create_provider")
    def test_middleware_captures_llm_metrics(self, mock_create_provider):
        """Test that middleware captures LLM metrics from chat endpoint."""
        # Mock provider response
        mock_provider = Mock()
        mock_provider.generate.return_value = LLMResponse(
            text="Test response",
            model="gpt-4o-mini",
            tokens_in=100,
            tokens_out=50
        )
        mock_create_provider.return_value = mock_provider
        
        response = self.client.post("/v1/chat", json={
            "messages": [
                {"role": "user", "content": "Hello"}
            ],
            "options": {
                "use_search": False,
                "temperature": 0.7,
                "max_tokens": 100
            }
        })
        
        assert response.status_code == 200
        
        # Check cost header is present and non-zero
        cost = float(response.headers["X-Cost-USD"])
        assert cost > 0
        
        # Verify cost calculation
        expected_cost = calculate_cost("gpt-4o-mini", 100, 50)
        assert cost == pytest.approx(expected_cost, abs=1e-6)
    
    @patch("src.infra.middleware.CostTrackingMiddleware._log_request_metrics")
    def test_structured_logging(self, mock_log_metrics):
        """Test that structured logging is called."""
        response = self.client.get("/health")
        assert response.status_code == 200
        
        # Verify logging was called
        mock_log_metrics.assert_called_once()
        
        # Check the metrics passed to logging
        call_args = mock_log_metrics.call_args[0]
        metrics = call_args[0]
        
        assert isinstance(metrics, RequestMetrics)
        assert metrics.path == "/health"
        assert metrics.method == "GET"
        assert metrics.status_code == 200
        assert metrics.latency_ms > 0
    
    def test_json_log_structure(self, caplog):
        """Test the structure of JSON logs."""
        with caplog.at_level(logging.INFO):
            response = self.client.get("/health")
            assert response.status_code == 200
        
        # Find the request completion log
        log_records = [record for record in caplog.records 
                      if record.levelname == "INFO" and "request_completed" in record.getMessage()]
        
        assert len(log_records) > 0
        
        # Parse the JSON log
        log_message = log_records[0].getMessage()
        log_data = json.loads(log_message)
        
        # Verify required fields
        required_fields = ["event", "request_id", "path", "method", "status", 
                          "latency_ms", "timestamp"]
        for field in required_fields:
            assert field in log_data
        
        assert log_data["event"] == "request_completed"
        assert log_data["path"] == "/health"
        assert log_data["method"] == "GET"
        assert log_data["status"] == 200
        assert log_data["latency_ms"] >= 0
    
    @patch("src.api.chat_router.create_provider")
    def test_json_log_with_llm_metrics(self, mock_create_provider, caplog):
        """Test JSON logs include LLM metrics for chat requests."""
        # Mock provider response
        mock_provider = Mock()
        mock_provider.generate.return_value = LLMResponse(
            text="Test response",
            model="gpt-4o-mini",
            tokens_in=150,
            tokens_out=75
        )
        mock_create_provider.return_value = mock_provider
        
        with caplog.at_level(logging.INFO):
            response = self.client.post("/v1/chat", json={
                "messages": [{"role": "user", "content": "Test"}],
                "options": {"use_search": False}
            })
            assert response.status_code == 200
        
        # Find the request completion log
        log_records = [record for record in caplog.records 
                      if record.levelname == "INFO" and "request_completed" in record.getMessage()]
        
        assert len(log_records) > 0
        
        # Parse the JSON log
        log_message = log_records[0].getMessage()
        log_data = json.loads(log_message)
        
        # Verify LLM fields are present
        llm_fields = ["model", "tokens_in", "tokens_out", "cost_usd"]
        for field in llm_fields:
            assert field in log_data
        
        assert log_data["model"] == "gpt-4o-mini"
        assert log_data["tokens_in"] == 150
        assert log_data["tokens_out"] == 75
        assert log_data["cost_usd"] > 0


class TestCostAPI:
    """Test the cost tracking API endpoints."""
    
    def setup_method(self):
        """Setup test client."""
        self.client = TestClient(app)
    
    def test_cost_health_endpoint(self):
        """Test the cost health check endpoint."""
        response = self.client.get("/v1/costs/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "buffer_usage" in data
        assert "buffer_utilization" in data
    
    def test_latest_costs_endpoint(self):
        """Test the latest costs summary endpoint."""
        response = self.client.get("/v1/costs/latest")
        assert response.status_code == 200
        
        data = response.json()
        required_fields = ["total_requests", "requests_with_llm", "total_cost_usd",
                          "avg_cost_per_request", "models_used", "cost_by_model", "time_range"]
        
        for field in required_fields:
            assert field in data
        
        # Initially should be mostly empty
        assert isinstance(data["total_requests"], int)
        assert isinstance(data["total_cost_usd"], float)
        assert isinstance(data["models_used"], dict)
        assert isinstance(data["cost_by_model"], dict)
    
    def test_recent_requests_endpoint(self):
        """Test the recent requests endpoint."""
        response = self.client.get("/v1/costs/requests")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        # If there are requests, verify structure
        if data:
            request = data[0]
            required_fields = ["request_id", "path", "method", "status_code",
                              "latency_ms", "timestamp"]
            for field in required_fields:
                assert field in request
    
    def test_cost_endpoint_limits(self):
        """Test cost endpoint parameter validation."""
        # Test invalid limit values
        response = self.client.get("/v1/costs/latest?limit=0")
        assert response.status_code == 400
        
        response = self.client.get("/v1/costs/latest?limit=2000")
        assert response.status_code == 400
        
        response = self.client.get("/v1/costs/requests?limit=0")
        assert response.status_code == 400
        
        response = self.client.get("/v1/costs/requests?limit=1000")
        assert response.status_code == 400
        
        # Test valid limits
        response = self.client.get("/v1/costs/latest?limit=50")
        assert response.status_code == 200
        
        response = self.client.get("/v1/costs/requests?limit=10")
        assert response.status_code == 200
    
    @patch("src.api.chat_router.create_provider")
    def test_cost_tracking_end_to_end(self, mock_create_provider):
        """Test complete cost tracking flow."""
        # Mock provider response
        mock_provider = Mock()
        mock_provider.generate.return_value = LLMResponse(
            text="Test response",
            model="gpt-4o-mini",
            tokens_in=200,
            tokens_out=100
        )
        mock_create_provider.return_value = mock_provider
        
        # Make a chat request
        chat_response = self.client.post("/v1/chat", json={
            "messages": [{"role": "user", "content": "Hello"}],
            "options": {"use_search": False}
        })
        assert chat_response.status_code == 200
        
        # Check that cost was calculated and returned
        cost_header = float(chat_response.headers["X-Cost-USD"])
        expected_cost = calculate_cost("gpt-4o-mini", 200, 100)
        assert cost_header == pytest.approx(expected_cost, abs=1e-6)
        
        # Check cost summary endpoint
        summary_response = self.client.get("/v1/costs/latest")
        assert summary_response.status_code == 200
        
        summary = summary_response.json()
        assert summary["requests_with_llm"] >= 1
        assert summary["total_cost_usd"] >= expected_cost
        assert "gpt-4o-mini" in summary["models_used"]
        assert "gpt-4o-mini" in summary["cost_by_model"]
        
        # Check recent requests endpoint
        requests_response = self.client.get("/v1/costs/requests?limit=5")
        assert requests_response.status_code == 200
        
        requests = requests_response.json()
        assert len(requests) >= 1
        
        # Find the chat request
        chat_requests = [r for r in requests if r["path"] == "/v1/chat"]
        assert len(chat_requests) >= 1
        
        chat_request = chat_requests[0]
        assert chat_request["model"] == "gpt-4o-mini"
        assert chat_request["tokens_in"] == 200
        assert chat_request["tokens_out"] == 100
        assert chat_request["cost_usd"] == pytest.approx(expected_cost, abs=1e-6)