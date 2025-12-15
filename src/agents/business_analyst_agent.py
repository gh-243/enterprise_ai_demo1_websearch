# NEW MULTI-AGENT FEATURE
"""
Business Analyst Agent Implementation

Provides strategic business insights using frameworks like SWOT and PESTEL.
"""

from typing import Dict, Any, Optional, List
from src.agents.base_agent import BaseAgent, AgentResponse
from src.providers.base import LLMMessage


class BusinessAnalystAgent(BaseAgent):
    """
    Business Analyst Agent that provides McKinsey-style strategic analysis.
    
    Uses frameworks like SWOT, PESTEL, Porter's Five Forces.
    """
    
    def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Analyze business situation using strategic frameworks.
        
        Args:
            query: Business question or situation to analyze
            context: Optional context (e.g., from research agent with market data)
            
        Returns:
            AgentResponse with strategic analysis
        """
        # Step 1: Gather market/business data via search
        search_result = self._search(query)
        
        # Step 2: Search for competitive/market context
        market_query = f"{query} market analysis competitors trends"
        market_result = self._search(market_query)
        
        # Step 3: Build business context
        business_context = self._format_business_context(
            search_result, 
            market_result,
            context
        )
        
        # Step 4: Generate strategic analysis
        messages = [
            self._build_system_message(),
            LLMMessage(
                role="user",
                content=f"""Business Question: {query}

Market & Business Data:
{business_context}

Provide a strategic analysis with:
1. Executive Summary (2-3 sentences)
2. SWOT Analysis (or other appropriate framework)
3. Key Strategic Insights backed by data
4. Actionable Recommendations
5. Risk Assessment

Use consulting-quality structure and cite data sources."""
            )
        ]
        
        llm_response = self._generate_llm_response(messages)
        
        # Step 5: Build sources list
        sources = self._build_business_sources(search_result, market_result)
        
        return AgentResponse(
            agent_name=self.config.name,
            agent_type=self.config.agent_type,
            content=llm_response.text,
            sources=sources,
            tokens_used=llm_response.tokens_in + llm_response.tokens_out,
            metadata={
                "query": query,
                "framework": "SWOT + Strategic Analysis",
                "num_sources": len(sources),
                "model": llm_response.model,
                "analysis_type": "consulting-style"
            }
        )
    
    def _format_business_context(
        self, 
        primary_result, 
        market_result,
        prior_context: Optional[Dict[str, Any]]
    ) -> str:
        """Format business intelligence for strategic analysis."""
        formatted = []
        
        # Include prior context if from research agent
        if prior_context and "research_summary" in prior_context:
            formatted.append("PRIOR RESEARCH FINDINGS:")
            formatted.append(prior_context["research_summary"])
            formatted.append("\n")
        
        formatted.append("PRIMARY BUSINESS DATA:")
        for i, result in enumerate(primary_result.results[:5], 1):
            formatted.append(
                f"[{i}] {result.title}\n"
                f"    {result.snippet}\n"
                f"    Source: {result.url}\n"
            )
        
        formatted.append("\nMARKET & COMPETITIVE INTELLIGENCE:")
        for i, result in enumerate(market_result.results[:5], 6):
            formatted.append(
                f"[{i}] {result.title}\n"
                f"    {result.snippet}\n"
                f"    Source: {result.url}\n"
            )
        
        return "\n".join(formatted)
    
    def _build_business_sources(self, primary_result, market_result) -> List[Dict[str, Any]]:
        """Build sources list with business intelligence attribution."""
        sources = []
        
        for i, result in enumerate(primary_result.results[:5], 1):
            sources.append({
                "id": i,
                "url": result.url,
                "title": result.title,
                "snippet": result.snippet,
                "category": "business_data"
            })
        
        for i, result in enumerate(market_result.results[:5], 6):
            sources.append({
                "id": i,
                "url": result.url,
                "title": result.title,
                "snippet": result.snippet,
                "category": "market_intelligence"
            })
        
        return sources
