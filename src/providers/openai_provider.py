"""
OpenAI Provider Implementation

Implements the LLM provider interface for OpenAI models using httpx.
"""

import os
import json
from typing import List, Dict, Any, Optional
import httpx

from .base import LLMProvider, LLMMessage, LLMResponse


class OpenAIProvider:
    """
    OpenAI implementation of the LLM provider interface.
    
    Uses httpx for HTTP calls to maintain minimal dependencies.
    Supports GPT-4, GPT-4o, GPT-3.5-turbo, and other OpenAI models.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.openai.com/v1"):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key. If None, loads from OPENAI_API_KEY env var
            base_url: OpenAI API base URL
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url
        self.default_model = "gpt-4o-mini"
        
        # Validate configuration on initialization
        self.validate_config()

    def validate_config(self) -> None:
        """Validate OpenAI configuration."""
        if not self.api_key:
            raise ValueError(
                "OpenAI API key is required. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        if not self.api_key.startswith("sk-"):
            raise ValueError(
                "Invalid OpenAI API key format. Key should start with 'sk-'"
            )

    def generate(
        self,
        messages: List[LLMMessage],
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> LLMResponse:
        """Generate response using OpenAI API."""
        if not messages:
            raise ValueError("Messages list cannot be empty")

        # Use default model if none specified
        model = model or self.default_model

        # Validate temperature range
        if not 0.0 <= temperature <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")

        # Validate max_tokens
        if max_tokens <= 0:
            raise ValueError("max_tokens must be positive")

        # Convert messages to OpenAI format
        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        # Prepare request payload
        payload = {
            "model": model,
            "messages": openai_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        # Add any additional kwargs (stream, stop, etc.)
        for key, value in kwargs.items():
            if key not in payload:  # Don't override core parameters
                payload[key] = value

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()

            # Extract response data
            choice = data["choices"][0]
            usage = data["usage"]
            
            return LLMResponse(
                text=choice["message"]["content"],
                tokens_in=usage["prompt_tokens"],
                tokens_out=usage["completion_tokens"],
                model=data["model"],
                metadata={
                    "finish_reason": choice["finish_reason"],
                    "total_tokens": usage["total_tokens"],
                    "provider": "openai"
                }
            )

        except httpx.TimeoutException as e:
            raise ConnectionError(f"OpenAI API timeout: {e}")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise RuntimeError("Invalid OpenAI API key")
            elif e.response.status_code == 429:
                raise RuntimeError("OpenAI API rate limit exceeded")
            elif e.response.status_code >= 500:
                raise ConnectionError(f"OpenAI API server error: {e.response.status_code}")
            else:
                error_detail = "Unknown error"
                try:
                    error_data = e.response.json()
                    error_detail = error_data.get("error", {}).get("message", error_detail)
                except:
                    pass
                raise RuntimeError(f"OpenAI API error: {error_detail}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON response from OpenAI API: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error calling OpenAI API: {e}")