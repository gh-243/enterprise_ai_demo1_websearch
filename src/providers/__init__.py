"""
LLM Provider Strategy Layer

This module provides a pluggable interface for different LLM providers
following the Strategy pattern and SOLID principles.
"""

from .base import LLMProvider
from .factory import create_provider

__all__ = ["LLMProvider", "create_provider"]