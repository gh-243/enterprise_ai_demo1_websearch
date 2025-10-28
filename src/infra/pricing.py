"""
Pricing calculations for LLM providers.

This module provides cost calculations for different LLM providers based on
current pricing as of October 2024.
"""

from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class ModelPricing:
    """Pricing information for a specific model."""
    input_cost_per_1k_tokens: float
    output_cost_per_1k_tokens: float
    provider: str
    model_name: str


# Pricing table based on current rates (USD per 1K tokens)
# Prices as of October 2024
PRICING_TABLE: Dict[str, ModelPricing] = {
    # OpenAI Models
    "gpt-4o": ModelPricing(
        input_cost_per_1k_tokens=0.0025,
        output_cost_per_1k_tokens=0.010,
        provider="openai",
        model_name="gpt-4o"
    ),
    "gpt-4o-mini": ModelPricing(
        input_cost_per_1k_tokens=0.000150,
        output_cost_per_1k_tokens=0.000600,
        provider="openai",
        model_name="gpt-4o-mini"
    ),
    "gpt-4": ModelPricing(
        input_cost_per_1k_tokens=0.03,
        output_cost_per_1k_tokens=0.06,
        provider="openai",
        model_name="gpt-4"
    ),
    "gpt-3.5-turbo": ModelPricing(
        input_cost_per_1k_tokens=0.0015,
        output_cost_per_1k_tokens=0.002,
        provider="openai",
        model_name="gpt-3.5-turbo"
    ),
    
    # Anthropic Models
    "claude-3-5-sonnet-20241022": ModelPricing(
        input_cost_per_1k_tokens=0.003,
        output_cost_per_1k_tokens=0.015,
        provider="anthropic",
        model_name="claude-3-5-sonnet-20241022"
    ),
    "claude-3-haiku-20240307": ModelPricing(
        input_cost_per_1k_tokens=0.00025,
        output_cost_per_1k_tokens=0.00125,
        provider="anthropic",
        model_name="claude-3-haiku-20240307"
    ),
    "claude-3-sonnet-20240229": ModelPricing(
        input_cost_per_1k_tokens=0.003,
        output_cost_per_1k_tokens=0.015,
        provider="anthropic",
        model_name="claude-3-sonnet-20240229"
    ),
}


def calculate_cost(model: str, tokens_in: int, tokens_out: int) -> float:
    """
    Calculate the cost for a given model and token usage.
    
    Args:
        model: The model name (e.g., "gpt-4o-mini")
        tokens_in: Number of input tokens
        tokens_out: Number of output tokens
        
    Returns:
        Cost in USD
        
    Raises:
        ValueError: If model is not found in pricing table
    """
    if not model:
        return 0.0
        
    # Normalize model name (remove provider prefixes if present)
    normalized_model = _normalize_model_name(model)
    
    pricing = PRICING_TABLE.get(normalized_model)
    if not pricing:
        # Return 0 for unknown models instead of raising exception
        # This allows the system to continue working with new/custom models
        return 0.0
    
    input_cost = (tokens_in / 1000.0) * pricing.input_cost_per_1k_tokens
    output_cost = (tokens_out / 1000.0) * pricing.output_cost_per_1k_tokens
    
    return round(input_cost + output_cost, 6)  # Round to 6 decimal places


def _normalize_model_name(model: str) -> str:
    """
    Normalize model name by removing common prefixes and variations.
    
    Args:
        model: Raw model name from provider
        
    Returns:
        Normalized model name for pricing lookup
    """
    # Remove common prefixes
    prefixes_to_remove = [
        "openai/",
        "anthropic/",
    ]
    
    normalized = model.lower().strip()
    
    for prefix in prefixes_to_remove:
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix):]
    
    # Handle specific model name variations
    model_mappings = {
        "gpt-4-turbo": "gpt-4o",
        "gpt-4-1106-preview": "gpt-4",
        "gpt-4-0613": "gpt-4",
        "gpt-3.5-turbo-1106": "gpt-3.5-turbo",
        "gpt-3.5-turbo-0613": "gpt-3.5-turbo",
    }
    
    return model_mappings.get(normalized, normalized)


def get_supported_models() -> Dict[str, ModelPricing]:
    """
    Get all supported models and their pricing information.
    
    Returns:
        Dictionary mapping model names to pricing information
    """
    return PRICING_TABLE.copy()


def get_model_pricing(model: str) -> Optional[ModelPricing]:
    """
    Get pricing information for a specific model.
    
    Args:
        model: The model name
        
    Returns:
        ModelPricing object or None if model not found
    """
    normalized_model = _normalize_model_name(model)
    return PRICING_TABLE.get(normalized_model)