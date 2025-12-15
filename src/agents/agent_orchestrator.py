# NEW MULTI-AGENT FEATURE
"""
Agent Orchestrator for Pipeline Coordination

Coordinates multiple agents in sequence for complex tasks.
"""

import os
from typing import List, Dict, Any, Optional
from src.agents.base_agent import AgentType, AgentResponse
from src.agents.agent_config import get_agent_config
from src.agents.research_agent import ResearchAgent
from src.agents.fact_check_agent import FactCheckAgent
from src.agents.business_analyst_agent import BusinessAnalystAgent
from src.agents.writing_agent import WritingAgent
from src.providers import create_provider
from src.search_service import SearchService


class AgentOrchestrator:
    """
    Orchestrates multiple agents in a pipeline.
    
    Example pipeline: Research → Fact-Check → Business Analyst → Writer
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the orchestrator.
        
        Args:
            api_key: OpenAI API key (falls back to env var)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key required for agent orchestrator")
        
        # Initialize shared services
        self.llm_provider = create_provider()
        self.search_service = SearchService(api_key=self.api_key)
        
        # Initialize agents (lazy loading)
        self._agents = {}
    
    def _get_agent(self, agent_type: AgentType):
        """Get or create an agent instance."""
        if agent_type not in self._agents:
            config = get_agent_config(agent_type)
            
            # Create agent based on type
            if agent_type == AgentType.RESEARCH:
                self._agents[agent_type] = ResearchAgent(
                    config, self.llm_provider, self.search_service
                )
            elif agent_type == AgentType.FACT_CHECK:
                self._agents[agent_type] = FactCheckAgent(
                    config, self.llm_provider, self.search_service
                )
            elif agent_type == AgentType.BUSINESS_ANALYST:
                self._agents[agent_type] = BusinessAnalystAgent(
                    config, self.llm_provider, self.search_service
                )
            elif agent_type == AgentType.WRITING:
                self._agents[agent_type] = WritingAgent(
                    config, self.llm_provider, None  # Writing agent doesn't need search
                )
        
        return self._agents[agent_type]
    
    def run_single_agent(
        self, 
        agent_type: AgentType, 
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """
        Run a single agent.
        
        Args:
            agent_type: Type of agent to run
            query: Query or instruction for the agent
            context: Optional context from previous agents
            
        Returns:
            AgentResponse from the agent
        """
        agent = self._get_agent(agent_type)
        return agent.process(query, context)
    
    def run_pipeline(
        self,
        pipeline: List[Dict[str, Any]],
        initial_query: str
    ) -> List[AgentResponse]:
        """
        Run a pipeline of agents in sequence.
        
        Args:
            pipeline: List of agent configs with queries
                Example: [
                    {"agent": AgentType.RESEARCH, "query": "research X"},
                    {"agent": AgentType.FACT_CHECK, "query": "verify Y"},
                    {"agent": AgentType.WRITING, "query": "write report"}
                ]
            initial_query: Initial user query
            
        Returns:
            List of AgentResponse objects from each agent
        """
        responses = []
        context = {}
        
        for i, step in enumerate(pipeline):
            agent_type = step["agent"]
            query = step.get("query", initial_query)
            
            # Run agent with accumulated context
            response = self.run_single_agent(agent_type, query, context)
            responses.append(response)
            
            # Update context for next agent
            context = {
                "content": response.content,
                "sources": response.sources,
                "agent_type": response.agent_type.value,
                "metadata": response.metadata,
                "previous_agents": [r.agent_name for r in responses]
            }
            
            # Special handling for specific agent types
            if agent_type == AgentType.RESEARCH:
                context["research_summary"] = response.content
            elif agent_type == AgentType.FACT_CHECK:
                context["fact_check_confidence"] = response.confidence_score
        
        return responses
    
    def run_standard_pipeline(self, query: str, output_format: str = "report") -> List[AgentResponse]:
        """
        Run the standard Research → Fact-Check → Business Analyst → Writer pipeline.
        
        Args:
            query: User query
            output_format: Final document format (report/email/summary)
            
        Returns:
            List of responses from all agents
        """
        pipeline = [
            {
                "agent": AgentType.RESEARCH,
                "query": query
            },
            {
                "agent": AgentType.FACT_CHECK,
                "query": f"Verify the key claims about: {query}"
            },
            {
                "agent": AgentType.BUSINESS_ANALYST,
                "query": f"Analyze the business implications of: {query}"
            },
            {
                "agent": AgentType.WRITING,
                "query": f"Write a professional {output_format} summarizing the findings"
            }
        ]
        
        return self.run_pipeline(pipeline, query)


# Convenience function for simple agent execution
def run_agent(
    agent_name: str,
    query: str,
    api_key: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> AgentResponse:
    """
    Simple function to run a single agent by name.
    
    Args:
        agent_name: Name of agent ("research", "fact_check", "business_analyst", "writing")
        query: Query or instruction
        api_key: Optional API key (uses env var if not provided)
        context: Optional context dict
        
    Returns:
        AgentResponse
        
    Example:
        >>> result = run_agent("research", "What is quantum computing?")
        >>> print(result.content)
    """
    # Map string names to AgentType enum
    agent_map = {
        "research": AgentType.RESEARCH,
        "fact_check": AgentType.FACT_CHECK,
        "fact-check": AgentType.FACT_CHECK,
        "business_analyst": AgentType.BUSINESS_ANALYST,
        "business-analyst": AgentType.BUSINESS_ANALYST,
        "writing": AgentType.WRITING,
        "writer": AgentType.WRITING
    }
    
    agent_type = agent_map.get(agent_name.lower())
    if not agent_type:
        raise ValueError(
            f"Unknown agent: {agent_name}. "
            f"Available: {list(agent_map.keys())}"
        )
    
    orchestrator = AgentOrchestrator(api_key=api_key)
    return orchestrator.run_single_agent(agent_type, query, context)
