"""
Base LLM Provider Interface

Defines the contract that all LLM providers must implement.
Following the Strategy pattern to allow pluggable provider implementations.
"""

from typing import Protocol, Dict, Any, List
from dataclasses import dataclass


@dataclass
class LLMMessage:
    """Represents a message in the conversation."""
    role: str  # "user", "assistant", "system"
    content: str


@dataclass
class LLMResponse:
    """Standardized response from any LLM provider."""
    text: str
    tokens_in: int
    tokens_out: int
    model: str
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class LLMProvider(Protocol):
    """
    Protocol defining the interface for LLM providers.
    
    This follows the Strategy pattern, allowing different LLM providers
    (OpenAI, Anthropic, etc.) to be used interchangeably without changing
    the application code.
    
    Example usage:
        provider = OpenAIProvider(api_key="sk-...")
        messages = [LLMMessage(role="user", content="Hello")]
        response = provider.generate(messages, temperature=0.7)
        print(response.text)  # AI response
        print(response.tokens_in)  # Input tokens used
        print(response.tokens_out)  # Output tokens generated
    """

    def generate(
        self,
        messages: List[LLMMessage],
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> LLMResponse:
        """
        Generate a response from the LLM provider.
        
        Args:
            messages: List of conversation messages
            model: Model name (provider-specific, e.g., "gpt-4o", "claude-3-sonnet")
            temperature: Randomness in response (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific options
            
        Returns:
            LLMResponse with generated text, token counts, and metadata
            
        Raises:
            ValueError: If inputs are invalid
            ConnectionError: If provider is unreachable
            RuntimeError: If provider returns an error
        """
        ...

    def validate_config(self) -> None:
        """
        Validate provider configuration (API keys, etc.).
        
        Raises:
            ValueError: If configuration is invalid or missing
        """
        ...