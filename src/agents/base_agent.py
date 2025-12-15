# NEW MULTI-AGENT FEATURE
"""
Base Agent Class for Multi-Agent System

This module provides the foundation for all specialized agents.
Does NOT modify existing search or chat functionality.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

from src.providers.base import LLMMessage, LLMResponse
from src.search_service import SearchService
from src.models import SearchOptions, SearchResult


class AgentType(Enum):
    """Available agent types."""
    RESEARCH = "research"
    FACT_CHECK = "fact_check"
    BUSINESS_ANALYST = "business_analyst"
    WRITING = "writing"
    PODCAST = "podcast"


@dataclass
class AgentConfig:
    """Configuration for an agent."""
    name: str
    agent_type: AgentType
    description: str
    system_prompt: str
    personality: str
    temperature: float = 0.7
    max_tokens: int = 2000
    use_search: bool = True
    avatar_emoji: str = "🤖"
    color: str = "#667eea"


@dataclass
class AgentResponse:
    """Response from an agent."""
    agent_name: str
    agent_type: AgentType
    content: str
    sources: Optional[List[Dict[str, Any]]] = None
    confidence_score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    tokens_used: int = 0
    cost_usd: float = 0.0


class BaseAgent(ABC):
    """
    Base class for all agents in the multi-agent system.
    
    Each agent:
    - Has a unique personality and prompt
    - Can use existing search functionality
    - Returns structured AgentResponse
    - Does NOT modify core chat/search logic
    """
    
    def __init__(
        self,
        config: AgentConfig,
        llm_provider,
        search_service: Optional[SearchService] = None
    ):
        """
        Initialize the base agent.
        
        Args:
            config: Agent configuration
            llm_provider: LLM provider instance (from existing providers)
            search_service: Optional search service (uses existing search)
        """
        self.config = config
        self.provider = llm_provider
        self.search_service = search_service
    
    @abstractmethod
    def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Process a query and return agent-specific response.
        
        Args:
            query: User query or instruction
            context: Optional context from previous agents in pipeline
            
        Returns:
            AgentResponse with processed content
        """
        pass
    
    def _search(self, query: str, options: Optional[SearchOptions] = None) -> SearchResult:
        """
        Use existing search functionality (DOES NOT MODIFY CORE LOGIC).
        
        Args:
            query: Search query
            options: Search options
            
        Returns:
            SearchResult from existing search service
        """
        if not self.search_service:
            raise ValueError(f"{self.config.name} requires search service")
        
        return self.search_service.search(query, options)
    
    def _generate_llm_response(
        self,
        messages: List[LLMMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> LLMResponse:
        """
        Generate LLM response using existing provider (DOES NOT MODIFY CORE LOGIC).
        
        Args:
            messages: List of messages
            temperature: Override default temperature
            max_tokens: Override default max tokens
            
        Returns:
            LLMResponse from existing provider
        """
        temp = temperature if temperature is not None else self.config.temperature
        tokens = max_tokens if max_tokens is not None else self.config.max_tokens
        
        return self.provider.generate(
            messages=messages,
            temperature=temp,
            max_tokens=tokens
        )
    
    def _build_system_message(self, additional_context: str = "") -> LLMMessage:
        """
        Build system message with agent personality.
        
        Args:
            additional_context: Additional context to add
            
        Returns:
            LLMMessage with system prompt
        """
        prompt = self.config.system_prompt
        if additional_context:
            prompt += f"\n\n{additional_context}"
        
        return LLMMessage(role="system", content=prompt)
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get agent information for UI/API.
        
        Returns:
            Dict with agent metadata
        """
        return {
            "name": self.config.name,
            "type": self.config.agent_type.value,
            "description": self.config.description,
            "personality": self.config.personality,
            "avatar": self.config.avatar_emoji,
            "color": self.config.color,
            "capabilities": {
                "search_enabled": self.config.use_search,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens
            }
        }
