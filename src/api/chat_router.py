"""
Chat API Router

Implements the chat endpoint that integrates LLM providers with web search capabilities.
"""

import uuid
import time
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status, Request
from pydantic import BaseModel, Field, field_validator

from src.providers import create_provider
from src.providers.base import LLMMessage, LLMResponse
from src.search_service import SearchService
from src.models import SearchOptions, SearchError, Citation as ModelCitation


# Request/Response Models
class ChatMessage(BaseModel):
    """A single message in a chat conversation."""
    role: str = Field(..., description="Role of the message sender", pattern="^(user|assistant|system)$")
    content: str = Field(..., description="Content of the message", min_length=1)


class ChatOptions(BaseModel):
    """Options for chat request."""
    use_search: bool = Field(False, description="Whether to enable web search augmentation")
    domains: Optional[List[str]] = Field(None, description="Allowed domains for search")
    temperature: float = Field(0.7, description="Sampling temperature", ge=0.0, le=2.0)
    max_tokens: int = Field(1000, description="Maximum tokens to generate", gt=0)
    
    @field_validator('domains')
    @classmethod
    def validate_domains(cls, v):
        """Validate domain list."""
        if v is not None:
            if len(v) > 20:
                raise ValueError("Too many domains (max 20 allowed)")
            for domain in v:
                if not domain or " " in domain or domain.startswith(("http://", "https://")):
                    raise ValueError(f"Invalid domain format: '{domain}'")
        return v


class ChatRequest(BaseModel):
    """Chat request payload."""
    messages: List[ChatMessage] = Field(..., description="List of conversation messages", min_length=1)
    options: ChatOptions = Field(default_factory=ChatOptions, description="Chat options")


class CitationResponse(BaseModel):
    """Citation information for API responses."""
    id: int = Field(..., description="Citation ID")
    url: str = Field(..., description="Source URL")
    title: str = Field(..., description="Source title")
    start_index: int = Field(..., description="Start index in response text")
    end_index: int = Field(..., description="End index in response text")


class ChatResponse(BaseModel):
    """Chat response payload."""
    text: str = Field(..., description="Generated response text")
    citations: Optional[List[CitationResponse]] = Field(None, description="Source citations if search was used")
    model: str = Field(..., description="Model used for generation")
    tokens_in: int = Field(..., description="Input tokens used")
    tokens_out: int = Field(..., description="Output tokens generated")
    cost_usd: float = Field(0.0, description="Cost in USD (placeholder)")
    trace_id: str = Field(..., description="Unique trace ID for request")


# Router
chat_router = APIRouter(prefix="/v1", tags=["chat"])


@chat_router.post("/chat", response_model=ChatResponse)
async def chat(chat_request: ChatRequest, request: Request) -> ChatResponse:
    """
    Generate a chat response with optional web search augmentation.
    
    Args:
        chat_request: Chat request with messages and options
        request: FastAPI request object (for middleware context)
        
    Returns:
        Chat response with generated text and metadata
        
    Raises:
        HTTPException: For various error conditions
    """
    trace_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
    start_time = time.time()
    
    try:
        # Create LLM provider
        provider = create_provider()
        
        # Convert request messages to provider format
        llm_messages = [
            LLMMessage(role=msg.role, content=msg.content)
            for msg in chat_request.messages
        ]
        
        citations = None
        
        # Handle web search augmentation
        if chat_request.options.use_search:
            citations = await _perform_web_search_augmentation(
                llm_messages, chat_request.options, trace_id
            )
        
        # Generate response using LLM provider
        llm_response = provider.generate(
            messages=llm_messages,
            temperature=chat_request.options.temperature,
            max_tokens=chat_request.options.max_tokens
        )
        
        # Pass LLM metrics to middleware
        request.state.llm_metrics = {
            'model': llm_response.model,
            'tokens_in': llm_response.tokens_in,
            'tokens_out': llm_response.tokens_out
        }
        
        # Convert citations if we performed search
        response_citations = None
        if citations:
            response_citations = [
                CitationResponse(
                    id=i + 1,
                    url=citation.url,
                    title=citation.title,
                    start_index=citation.start_index,
                    end_index=citation.end_index
                )
                for i, citation in enumerate(citations)
            ]
        
        return ChatResponse(
            text=llm_response.text,
            citations=response_citations,
            model=llm_response.model,
            tokens_in=llm_response.tokens_in,
            tokens_out=llm_response.tokens_out,
            cost_usd=0.0,  # Placeholder for now
            trace_id=trace_id
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input: {str(e)}"
        )
    except SearchError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Search service error: {e.message}"
        )
    except ConnectionError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Provider connection error: {str(e)}"
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Provider error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


async def _perform_web_search_augmentation(
    llm_messages: List[LLMMessage],
    options: ChatOptions,
    trace_id: str
) -> List[ModelCitation]:
    """
    Perform web search and augment messages with search context.
    
    Args:
        llm_messages: List of LLM messages to augment
        options: Chat options including domain filtering
        trace_id: Trace ID for logging
        
    Returns:
        List of citations from search results
    """
    try:
        # Get the last user message as search query
        user_messages = [msg for msg in llm_messages if msg.role == "user"]
        if not user_messages:
            return []
        
        query = user_messages[-1].content
        
        # Create search service (assumes API key available)
        import os
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise SearchError(
                code="MISSING_API_KEY",
                message="OpenAI API key required for search"
            )
        
        search_service = SearchService(api_key=api_key)
        
        # Configure search options
        search_options = SearchOptions()
        if options.domains:
            search_options.allowed_domains = options.domains
        
        # Perform search
        search_result = search_service.search(query, search_options)
        
        # Inject search context as system message
        if search_result.text and search_result.citations:
            context_message = LLMMessage(
                role="system",
                content=f"Use the following web search information to help answer the user's question:\n\n{search_result.text}"
            )
            # Insert at the beginning (after any existing system messages)
            system_count = sum(1 for msg in llm_messages if msg.role == "system")
            llm_messages.insert(system_count, context_message)
            
            return search_result.citations
        
        return []
        
    except SearchError:
        # Re-raise search errors
        raise
    except Exception as e:
        raise SearchError(
            code="SEARCH_FAILED",
            message=f"Web search failed: {str(e)}"
        )