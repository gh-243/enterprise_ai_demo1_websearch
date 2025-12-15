# NEW MULTI-AGENT FEATURE
"""
Multi-Agent System Module

Provides specialized AI agents for research, fact-checking, business analysis, and writing.
Uses existing search and LLM infrastructure without modifications.
"""

from src.agents.base_agent import (
    BaseAgent,
    AgentType,
    AgentConfig,
    AgentResponse
)
from src.agents.agent_config import (
    get_agent_config,
    list_available_agents,
    RESEARCH_AGENT_CONFIG,
    FACT_CHECK_AGENT_CONFIG,
    BUSINESS_ANALYST_CONFIG,
    WRITING_AGENT_CONFIG
)
from src.agents.research_agent import ResearchAgent
from src.agents.fact_check_agent import FactCheckAgent
from src.agents.business_analyst_agent import BusinessAnalystAgent
from src.agents.writing_agent import WritingAgent
from src.agents.podcast_agent import PodcastAgent, generate_podcast
from src.agents.agent_orchestrator import (
    AgentOrchestrator,
    run_agent
)

__all__ = [
    # Base classes
    "BaseAgent",
    "AgentType",
    "AgentConfig",
    "AgentResponse",
    
    # Agent implementations
    "ResearchAgent",
    "FactCheckAgent",
    "BusinessAnalystAgent",
    "WritingAgent",
    "PodcastAgent",
    
    # Helper functions
    "generate_podcast",
    
    # Configuration
    "get_agent_config",
    "list_available_agents",
    "RESEARCH_AGENT_CONFIG",
    "FACT_CHECK_AGENT_CONFIG",
    "BUSINESS_ANALYST_CONFIG",
    "WRITING_AGENT_CONFIG",
    
    # Orchestration
    "AgentOrchestrator",
    "run_agent"
]
