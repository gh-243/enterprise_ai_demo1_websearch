"""
Anthropic Provider Implementation

Implements the LLM provider interface for Anthropic Claude models using httpx.
"""

import os
import json
from typing import List, Dict, Any, Optional
import httpx

from .base import LLMProvider, LLMMessage, LLMResponse


class AnthropicProvider:
    """
    Anthropic Claude implementation of the LLM provider interface.
    
    Uses httpx for HTTP calls to maintain minimal dependencies.
    Supports Claude-3 Sonnet, Claude-3 Haiku, and other Claude models.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.anthropic.com"):
        """
        Initialize Anthropic provider.
        
        Args:
            api_key: Anthropic API key. If None, loads from ANTHROPIC_API_KEY env var
            base_url: Anthropic API base URL
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.base_url = base_url
        self.default_model = "claude-3-sonnet-20240229"
        self.api_version = "2023-06-01"
        
        # Validate configuration on initialization
        self.validate_config()

    def validate_config(self) -> None:
        """Validate Anthropic configuration."""
        if not self.api_key:
            raise ValueError(
                "Anthropic API key is required. Set ANTHROPIC_API_KEY environment variable "
                "or pass api_key parameter."
            )

    def generate(
        self,
        messages: List[LLMMessage],
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> LLMResponse:
        """Generate response using Anthropic API."""
        if not messages:
            raise ValueError("Messages list cannot be empty")

        # Use default model if none specified
        model = model or self.default_model

        # Validate temperature range
        if not 0.0 <= temperature <= 1.0:
            raise ValueError("Temperature must be between 0.0 and 1.0 for Anthropic")

        # Validate max_tokens
        if max_tokens <= 0:
            raise ValueError("max_tokens must be positive")

        # Convert messages to Anthropic format
        # Anthropic expects system messages separately and user/assistant alternating
        system_messages = [msg.content for msg in messages if msg.role == "system"]
        conversation_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
            if msg.role in ["user", "assistant"]
        ]

        if not conversation_messages:
            raise ValueError("At least one user or assistant message is required")

        # Prepare request payload
        payload = {
            "model": model,
            "messages": conversation_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        # Add system message if present
        if system_messages:
            payload["system"] = "\n".join(system_messages)

        # Add any additional kwargs
        for key, value in kwargs.items():
            if key not in payload:  # Don't override core parameters
                payload[key] = value

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": self.api_version,
            "Content-Type": "application/json"
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{self.base_url}/v1/messages",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()

            # Extract response data from Anthropic format
            content = data["content"][0]["text"] if data["content"] else ""
            usage = data["usage"]
            
            return LLMResponse(
                text=content,
                tokens_in=usage["input_tokens"],
                tokens_out=usage["output_tokens"],
                model=data["model"],
                metadata={
                    "stop_reason": data.get("stop_reason"),
                    "stop_sequence": data.get("stop_sequence"),
                    "provider": "anthropic"
                }
            )

        except httpx.TimeoutException as e:
            raise ConnectionError(f"Anthropic API timeout: {e}")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise RuntimeError("Invalid Anthropic API key")
            elif e.response.status_code == 429:
                raise RuntimeError("Anthropic API rate limit exceeded")
            elif e.response.status_code >= 500:
                raise ConnectionError(f"Anthropic API server error: {e.response.status_code}")
            else:
                error_detail = "Unknown error"
                try:
                    error_data = e.response.json()
                    error_detail = error_data.get("error", {}).get("message", error_detail)
                except:
                    pass
                raise RuntimeError(f"Anthropic API error: {error_detail}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON response from Anthropic API: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error calling Anthropic API: {e}")