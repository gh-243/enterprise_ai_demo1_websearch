"""
LLM Provider Factory

Factory for creating LLM provider instances based on environment configuration.
Follows the Factory pattern to abstract provider selection from client code.
"""

import os
from typing import Union

from .base import LLMProvider
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider


def create_provider(
    provider_name: str = None,
    model: str = None,
    **kwargs
) -> Union[OpenAIProvider, AnthropicProvider]:
    """
    Create an LLM provider instance based on configuration.
    
    Args:
        provider_name: Provider name ("openai" or "anthropic"). 
                      If None, uses LLM_PROVIDER env var
        model: Model name to use. If None, uses LLM_MODEL env var or provider default
        **kwargs: Additional provider-specific arguments (api_key, base_url, etc.)
        
    Returns:
        Configured LLM provider instance
        
    Raises:
        ValueError: If provider name is invalid or required config is missing
        
    Example:
        # Using environment variables
        os.environ["LLM_PROVIDER"] = "openai"
        os.environ["LLM_MODEL"] = "gpt-4o"
        provider = create_provider()
        
        # Explicit configuration
        provider = create_provider(
            provider_name="anthropic",
            model="claude-3-sonnet-20240229",
            api_key="your-key"
        )
    """
    # Get provider name from parameter or environment
    provider_name = provider_name or os.getenv("LLM_PROVIDER")
    
    if not provider_name:
        raise ValueError(
            "Provider name is required. Set LLM_PROVIDER environment variable "
            "or pass provider_name parameter. Valid values: 'openai', 'anthropic'"
        )
    
    provider_name = provider_name.lower().strip()
    
    # Get model from parameter or environment
    model = model or os.getenv("LLM_MODEL")
    
    # Create provider instance
    if provider_name == "openai":
        provider = OpenAIProvider(**kwargs)
        if model:
            provider.default_model = model
        return provider
    
    elif provider_name == "anthropic":
        provider = AnthropicProvider(**kwargs)
        if model:
            provider.default_model = model
        return provider
    
    else:
        raise ValueError(
            f"Unsupported provider '{provider_name}'. "
            "Valid providers: 'openai', 'anthropic'"
        )


def get_available_providers() -> list[str]:
    """
    Get list of available provider names.
    
    Returns:
        List of provider names that can be used with create_provider()
    """
    return ["openai", "anthropic"]


def validate_environment() -> dict[str, str]:
    """
    Validate environment configuration for LLM providers.
    
    Returns:
        Dictionary with validation results and recommendations
        
    Example:
        validation = validate_environment()
        if validation["status"] == "error":
            print(validation["message"])
    """
    provider = os.getenv("LLM_PROVIDER", "").lower().strip()
    model = os.getenv("LLM_MODEL", "")
    
    # Check if provider is set
    if not provider:
        return {
            "status": "error",
            "message": "LLM_PROVIDER environment variable is not set",
            "recommendations": [
                "Set LLM_PROVIDER to 'openai' or 'anthropic'",
                "Example: export LLM_PROVIDER=openai"
            ]
        }
    
    # Check if provider is valid
    if provider not in get_available_providers():
        return {
            "status": "error",
            "message": f"Invalid LLM_PROVIDER '{provider}'",
            "recommendations": [
                f"Set LLM_PROVIDER to one of: {', '.join(get_available_providers())}",
                "Example: export LLM_PROVIDER=openai"
            ]
        }
    
    # Check provider-specific requirements
    missing_keys = []
    
    if provider == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            missing_keys.append("OPENAI_API_KEY")
    
    elif provider == "anthropic":
        if not os.getenv("ANTHROPIC_API_KEY"):
            missing_keys.append("ANTHROPIC_API_KEY")
    
    if missing_keys:
        return {
            "status": "error",
            "message": f"Missing required environment variables: {', '.join(missing_keys)}",
            "recommendations": [
                f"Set {key} with your API key" for key in missing_keys
            ]
        }
    
    # All good
    recommendations = []
    if not model:
        recommendations.append("Consider setting LLM_MODEL for explicit model selection")
    
    return {
        "status": "ok",
        "message": f"Configuration valid for {provider} provider",
        "provider": provider,
        "model": model or f"default ({provider})",
        "recommendations": recommendations
    }