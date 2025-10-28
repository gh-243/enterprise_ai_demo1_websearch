"""
Tests for the chat API router.

Tests the chat endpoint functionality including web search integration.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
import json

from src.app.app import app
from src.providers.base import LLMResponse
from src.models import SearchResult, Citation as ModelCitation
from src.search_service import SearchError
from src.api.chat_router import CitationResponse


# Test client
client = TestClient(app)


class TestChatRouter:
    """Test the chat API router."""
    
    def test_chat_basic_success(self):
        """Test basic chat request without search."""
        with patch("src.api.chat_router.create_provider") as mock_create_provider:
            # Mock provider
            mock_provider = Mock()
            mock_provider.generate.return_value = LLMResponse(
                text="Hello! How can I help you?",
                model="gpt-4",
                tokens_in=10,
                tokens_out=8
            )
            mock_create_provider.return_value = mock_provider
            
            # Make request
            response = client.post("/v1/chat", json={
                "messages": [
                    {"role": "user", "content": "Hello"}
                ],
                "options": {
                    "use_search": False,
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["text"] == "Hello! How can I help you?"
            assert data["model"] == "gpt-4"
            assert data["tokens_in"] == 10
            assert data["tokens_out"] == 8
            assert data["citations"] is None
            assert "trace_id" in data
            
            # Verify provider was called correctly
            mock_provider.generate.assert_called_once()
            call_args = mock_provider.generate.call_args
            assert len(call_args[1]["messages"]) == 1
            assert call_args[1]["messages"][0].role == "user"
            assert call_args[1]["messages"][0].content == "Hello"
            assert call_args[1]["temperature"] == 0.7
            assert call_args[1]["max_tokens"] == 1000
    
    def test_chat_with_multiple_messages(self):
        """Test chat with conversation history."""
        with patch("src.api.chat_router.create_provider") as mock_create_provider:
            mock_provider = Mock()
            mock_provider.generate.return_value = LLMResponse(
                text="Yes, I remember our previous conversation.",
                model="gpt-4",
                tokens_in=25,
                tokens_out=12
            )
            mock_create_provider.return_value = mock_provider
            
            response = client.post("/v1/chat", json={
                "messages": [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi there!"},
                    {"role": "user", "content": "Do you remember what we talked about?"}
                ]
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["text"] == "Yes, I remember our previous conversation."
            
            # Verify all messages were passed
            call_args = mock_provider.generate.call_args
            assert len(call_args[1]["messages"]) == 3
    
    @patch("src.api.chat_router._perform_web_search_augmentation")
    def test_chat_with_search_success(self, mock_search_aug):
        """Test chat with web search enabled."""
        with patch("src.api.chat_router.create_provider") as mock_create_provider:
            # Mock search augmentation
            mock_citations = [
                ModelCitation(
                    url="https://example.com/1",
                    title="Test Page 1",
                    start_index=10,
                    end_index=50
                )
            ]
            mock_search_aug.return_value = mock_citations
            
            # Mock provider
            mock_provider = Mock()
            mock_provider.generate.return_value = LLMResponse(
                text="Based on the search results, here's what I found...",
                model="gpt-4",
                tokens_in=100,
                tokens_out=25
            )
            mock_create_provider.return_value = mock_provider
            
            response = client.post("/v1/chat", json={
                "messages": [
                    {"role": "user", "content": "What's the weather like?"}
                ],
                "options": {
                    "use_search": True,
                    "domains": ["weather.com"],
                    "temperature": 0.5
                }
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["text"] == "Based on the search results, here's what I found..."
            assert data["citations"] is not None
            assert len(data["citations"]) == 1
            assert data["citations"][0]["id"] == 1
            assert data["citations"][0]["url"] == "https://example.com/1"
            assert data["citations"][0]["title"] == "Test Page 1"
            
            # Verify search augmentation was called
            mock_search_aug.assert_called_once()
    
    def test_chat_validation_errors(self):
        """Test various validation errors."""
        # Empty messages
        response = client.post("/v1/chat", json={
            "messages": []
        })
        assert response.status_code == 422
        
        # Invalid role
        response = client.post("/v1/chat", json={
            "messages": [
                {"role": "invalid", "content": "Hello"}
            ]
        })
        assert response.status_code == 422
        
        # Empty content
        response = client.post("/v1/chat", json={
            "messages": [
                {"role": "user", "content": ""}
            ]
        })
        assert response.status_code == 422
        
        # Invalid temperature
        response = client.post("/v1/chat", json={
            "messages": [
                {"role": "user", "content": "Hello"}
            ],
            "options": {
                "temperature": 3.0  # Too high
            }
        })
        assert response.status_code == 422
        
        # Invalid max_tokens
        response = client.post("/v1/chat", json={
            "messages": [
                {"role": "user", "content": "Hello"}
            ],
            "options": {
                "max_tokens": 0  # Too low
            }
        })
        assert response.status_code == 422
        
        # Too many domains
        response = client.post("/v1/chat", json={
            "messages": [
                {"role": "user", "content": "Hello"}
            ],
            "options": {
                "domains": [f"domain{i}.com" for i in range(25)]  # Too many
            }
        })
        assert response.status_code == 422
        
        # Invalid domain format
        response = client.post("/v1/chat", json={
            "messages": [
                {"role": "user", "content": "Hello"}
            ],
            "options": {
                "domains": ["https://invalid-domain.com"]
            }
        })
        assert response.status_code == 422
    
    def test_provider_errors(self):
        """Test various provider error scenarios."""
        # ValueError from provider
        with patch("src.api.chat_router.create_provider") as mock_create_provider:
            mock_provider = Mock()
            mock_provider.generate.side_effect = ValueError("Invalid input")
            mock_create_provider.return_value = mock_provider
            
            response = client.post("/v1/chat", json={
                "messages": [
                    {"role": "user", "content": "Hello"}
                ]
            })
            
            assert response.status_code == 400
            assert "Invalid input" in response.json()["detail"]
        
        # ConnectionError from provider
        with patch("src.api.chat_router.create_provider") as mock_create_provider:
            mock_provider = Mock()
            mock_provider.generate.side_effect = ConnectionError("Network error")
            mock_create_provider.return_value = mock_provider
            
            response = client.post("/v1/chat", json={
                "messages": [
                    {"role": "user", "content": "Hello"}
                ]
            })
            
            assert response.status_code == 502
            assert "Provider connection error" in response.json()["detail"]
        
        # RuntimeError from provider
        with patch("src.api.chat_router.create_provider") as mock_create_provider:
            mock_provider = Mock()
            mock_provider.generate.side_effect = RuntimeError("API error")
            mock_create_provider.return_value = mock_provider
            
            response = client.post("/v1/chat", json={
                "messages": [
                    {"role": "user", "content": "Hello"}
                ]
            })
            
            assert response.status_code == 500
            assert "Provider error" in response.json()["detail"]
        
        # Unexpected error
        with patch("src.api.chat_router.create_provider") as mock_create_provider:
            mock_provider = Mock()
            mock_provider.generate.side_effect = Exception("Unexpected")
            mock_create_provider.return_value = mock_provider
            
            response = client.post("/v1/chat", json={
                "messages": [
                    {"role": "user", "content": "Hello"}
                ]
            })
            
            assert response.status_code == 500
            assert "Unexpected error" in response.json()["detail"]
    
    @patch("src.api.chat_router._perform_web_search_augmentation")
    def test_search_error_handling(self, mock_search_aug):
        """Test search error scenarios."""
        with patch("src.api.chat_router.create_provider") as mock_create_provider:
            # Mock search error
            mock_search_aug.side_effect = SearchError(
                code="API_ERROR",
                message="Search API failed"
            )
            
            mock_provider = Mock()
            mock_create_provider.return_value = mock_provider
            
            response = client.post("/v1/chat", json={
                "messages": [
                    {"role": "user", "content": "Hello"}
                ],
                "options": {"use_search": True}
            })
            
            assert response.status_code == 503
            assert "Search service error" in response.json()["detail"]
    
    def test_default_options(self):
        """Test that default options are applied correctly."""
        with patch("src.api.chat_router.create_provider") as mock_create_provider:
            mock_provider = Mock()
            mock_provider.generate.return_value = LLMResponse(
                text="Response",
                model="gpt-4",
                tokens_in=5,
                tokens_out=3
            )
            mock_create_provider.return_value = mock_provider
            
            response = client.post("/v1/chat", json={
                "messages": [
                    {"role": "user", "content": "Hello"}
                ]
                # No options provided
            })
            
            assert response.status_code == 200
            
            # Verify default options were used
            call_args = mock_provider.generate.call_args
            assert call_args[1]["temperature"] == 0.7  # Default
            assert call_args[1]["max_tokens"] == 1000  # Default


class TestWebSearchAugmentation:
    """Test the web search augmentation functionality."""
    
    @pytest.mark.asyncio
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    @patch("src.api.chat_router.SearchService")
    async def test_search_augmentation_success(self, mock_search_service_class):
        """Test successful web search augmentation."""
        from src.api.chat_router import _perform_web_search_augmentation
        from src.providers.base import LLMMessage
        from src.api.chat_router import ChatOptions
        
        # Mock search service
        mock_search_service = Mock()
        from datetime import datetime
        from src.models import Source
        mock_search_result = SearchResult(
            query="What is the weather?",
            text="Search context information",
            citations=[
                ModelCitation(
                    url="https://example.com",
                    title="Example Page",
                    start_index=0,
                    end_index=10
                )
            ],
            sources=[
                Source(url="https://example.com", type="web")
            ],
            search_id="test-123",
            timestamp=datetime.now()
        )
        mock_search_service.search.return_value = mock_search_result
        mock_search_service_class.return_value = mock_search_service
        
        # Test data
        messages = [
            LLMMessage(role="user", content="What is the weather?")
        ]
        options = ChatOptions(use_search=True)
        
        # Call function
        citations = await _perform_web_search_augmentation(messages, options, "trace-123")
        
        # Verify results
        assert len(citations) == 1
        assert citations[0].url == "https://example.com"
        
        # Verify search service was called
        mock_search_service.search.assert_called_once_with(
            "What is the weather?",
            mock_search_service.search.call_args[0][1]  # SearchOptions
        )
        
        # Verify system message was inserted
        assert len(messages) == 2
        assert messages[0].role == "system"
        assert "Search context information" in messages[0].content
        assert messages[1].role == "user"
        assert messages[1].content == "What is the weather?"
    
    @pytest.mark.asyncio
    @patch.dict("os.environ", {}, clear=True)
    async def test_search_augmentation_missing_api_key(self):
        """Test search augmentation with missing API key."""
        from src.api.chat_router import _perform_web_search_augmentation
        from src.providers.base import LLMMessage
        from src.api.chat_router import ChatOptions
        
        messages = [
            LLMMessage(role="user", content="Test query")
        ]
        options = ChatOptions(use_search=True)
        
        with pytest.raises(SearchError) as exc_info:
            await _perform_web_search_augmentation(messages, options, "trace-123")
        
        assert exc_info.value.code == "MISSING_API_KEY"
    
    @pytest.mark.asyncio
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    @patch("src.api.chat_router.SearchService")
    async def test_search_augmentation_no_user_messages(self, mock_search_service_class):
        """Test search augmentation with no user messages."""
        from src.api.chat_router import _perform_web_search_augmentation
        from src.providers.base import LLMMessage
        from src.api.chat_router import ChatOptions
        
        messages = [
            LLMMessage(role="system", content="You are an assistant")
        ]
        options = ChatOptions(use_search=True)
        
        citations = await _perform_web_search_augmentation(messages, options, "trace-123")
        
        assert citations == []
        # No search service should be created
        mock_search_service_class.assert_not_called()
    
    @pytest.mark.asyncio
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    @patch("src.api.chat_router.SearchService")
    async def test_search_augmentation_with_domains(self, mock_search_service_class):
        """Test search augmentation with domain filtering."""
        from src.api.chat_router import _perform_web_search_augmentation
        from src.providers.base import LLMMessage
        from src.api.chat_router import ChatOptions
        
        # Mock search service
        mock_search_service = Mock()
        from datetime import datetime
        from src.models import Source
        mock_search_result = SearchResult(
            query="Test query",
            text="",
            citations=[],
            sources=[],
            search_id="test-789",
            timestamp=datetime.now()
        )
        mock_search_service.search.return_value = mock_search_result
        mock_search_service_class.return_value = mock_search_service
        
        messages = [
            LLMMessage(role="user", content="Test query")
        ]
        options = ChatOptions(
            use_search=True,
            domains=["example.com", "test.org"]
        )
        
        await _perform_web_search_augmentation(messages, options, "trace-123")
        
        # Verify domain filtering was applied
        search_args = mock_search_service.search.call_args
        search_options = search_args[0][1]
        assert search_options.allowed_domains == ["example.com", "test.org"]
    
    @pytest.mark.asyncio
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    @patch("src.api.chat_router.SearchService")
    async def test_search_augmentation_system_message_placement(self, mock_search_service_class):
        """Test that system messages are placed correctly."""
        from src.api.chat_router import _perform_web_search_augmentation
        from src.providers.base import LLMMessage
        from src.api.chat_router import ChatOptions
        
        # Mock search service
        mock_search_service = Mock()
        from datetime import datetime
        from src.models import Source
        mock_search_result = SearchResult(
            query="What is Python?",
            text="Search results",
            citations=[
                ModelCitation(
                    url="https://example.com",
                    title="Example",
                    start_index=0,
                    end_index=5
                )
            ],
            sources=[
                Source(url="https://example.com", type="web")
            ],
            search_id="test-456",
            timestamp=datetime.now()
        )
        mock_search_service.search.return_value = mock_search_result
        mock_search_service_class.return_value = mock_search_service
        
        # Start with existing system message
        messages = [
            LLMMessage(role="system", content="You are a helpful assistant"),
            LLMMessage(role="user", content="What is Python?")
        ]
        options = ChatOptions(use_search=True)
        
        await _perform_web_search_augmentation(messages, options, "trace-123")
        
        # Verify message order
        assert len(messages) == 3
        assert messages[0].role == "system"
        assert messages[0].content == "You are a helpful assistant"
        assert messages[1].role == "system"
        assert "Search results" in messages[1].content
        assert messages[2].role == "user"
        assert messages[2].content == "What is Python?"


class TestChatModels:
    """Test the Pydantic models for chat API."""
    
    def test_chat_message_validation(self):
        """Test ChatMessage validation."""
        from src.api.chat_router import ChatMessage
        
        # Valid message
        msg = ChatMessage(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"
        
        # Invalid role
        with pytest.raises(ValueError):
            ChatMessage(role="invalid", content="Hello")
        
        # Empty content
        with pytest.raises(ValueError):
            ChatMessage(role="user", content="")
    
    def test_chat_options_validation(self):
        """Test ChatOptions validation."""
        from src.api.chat_router import ChatOptions
        
        # Default values
        options = ChatOptions()
        assert options.use_search is False
        assert options.domains is None
        assert options.temperature == 0.7
        assert options.max_tokens == 1000
        
        # Valid custom values
        options = ChatOptions(
            use_search=True,
            domains=["example.com"],
            temperature=0.5,
            max_tokens=500
        )
        assert options.use_search is True
        assert options.domains == ["example.com"]
        
        # Invalid temperature
        with pytest.raises(ValueError):
            ChatOptions(temperature=3.0)
        
        # Invalid max_tokens
        with pytest.raises(ValueError):
            ChatOptions(max_tokens=0)
        
        # Too many domains
        with pytest.raises(ValueError):
            ChatOptions(domains=[f"domain{i}.com" for i in range(25)])
        
        # Invalid domain format
        with pytest.raises(ValueError):
            ChatOptions(domains=["invalid domain with spaces"])
        
        with pytest.raises(ValueError):
            ChatOptions(domains=["https://example.com"])
    
    def test_citation_model(self):
        """Test Citation model."""
        from src.api.chat_router import CitationResponse
        
        citation = CitationResponse(
            id=1,
            url="https://example.com",
            title="Example Page",
            start_index=10,
            end_index=50
        )
        
        assert citation.id == 1
        assert citation.url == "https://example.com"
        assert citation.title == "Example Page"
        assert citation.start_index == 10
        assert citation.end_index == 50
    
    def test_chat_response_model(self):
        """Test ChatResponse model."""
        from src.api.chat_router import ChatResponse, CitationResponse
        
        # Without citations
        response = ChatResponse(
            text="Hello there!",
            model="gpt-4",
            tokens_in=10,
            tokens_out=8,
            trace_id="trace-123"
        )
        
        assert response.text == "Hello there!"
        assert response.citations is None
        assert response.cost_usd == 0.0  # Default value
        
        # With citations
        citations = [
            CitationResponse(
                id=1,
                url="https://example.com",
                title="Example",
                start_index=0,
                end_index=10
            )
        ]
        
        response = ChatResponse(
            text="Based on sources...",
            citations=citations,
            model="gpt-4",
            tokens_in=20,
            tokens_out=15,
            cost_usd=0.001,
            trace_id="trace-456"
        )
        
        assert len(response.citations) == 1
        assert response.citations[0].url == "https://example.com"