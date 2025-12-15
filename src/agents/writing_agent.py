# NEW MULTI-AGENT FEATURE
"""
Writing Agent Implementation

Transforms research and analysis into polished documents.
"""

from typing import Dict, Any, Optional, List
from src.agents.base_agent import BaseAgent, AgentResponse
from src.providers.base import LLMMessage


class WritingAgent(BaseAgent):
    """
    Writing Agent that crafts polished documents from research/analysis.
    
    Friendly professional tone, adapts to different formats.
    """
    
    def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Transform content into a polished document.
        
        Args:
            query: Writing instruction (e.g., "write an email", "create a report")
            context: Optional - content from previous agents to transform
            
        Returns:
            AgentResponse with polished document
        """
        # Determine document format from query
        doc_format = self._determine_format(query)
        
        # Check if we have context from other agents
        if context and "content" in context:
            # Transform existing content
            source_content = context.get("content", "")
            sources = context.get("sources", [])
            agent_type = context.get("agent_type", "previous agent")
            
            messages = [
                self._build_system_message(),
                LLMMessage(
                    role="user",
                    content=f"""Writing Task: {query}
Document Format: {doc_format}

Source Content to Transform:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{source_content}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Transform this content into a {doc_format} that is:
- Clear and well-structured
- Professional yet friendly
- Appropriate for the target audience
- Includes key points from the source material
- Properly formatted for {doc_format}

Maintain any important citations or data points."""
                )
            ]
            
            transformation_type = "analysis_to_document"
            
        else:
            # Generate original content based on query
            sources = []
            agent_type = "direct"
            
            messages = [
                self._build_system_message(),
                LLMMessage(
                    role="user",
                    content=f"""Writing Task: {query}
Document Format: {doc_format}

Create a {doc_format} that addresses the following:
{query}

The document should be:
- Clear and well-structured
- Professional yet friendly
- Appropriate for the target audience
- Properly formatted for {doc_format}
- Complete and actionable

Generate high-quality content that fully addresses the request."""
                )
            ]
            
            transformation_type = "original_content"
        
        llm_response = self._generate_llm_response(messages)
        
        return AgentResponse(
            agent_name=self.config.name,
            agent_type=self.config.agent_type,
            content=llm_response.text,
            sources=sources,
            tokens_used=llm_response.tokens_in + llm_response.tokens_out,
            metadata={
                "task": query,
                "document_format": doc_format,
                "source_agent": agent_type,
                "model": llm_response.model,
                "transformation": transformation_type
            }
        )
    
    def _determine_format(self, query: str) -> str:
        """Determine document format from query."""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["email", "message", "letter"]):
            return "Professional Email"
        elif any(word in query_lower for word in ["executive", "summary", "brief"]):
            return "Executive Summary"
        elif any(word in query_lower for word in ["report", "document", "analysis"]):
            return "Comprehensive Report"
        elif any(word in query_lower for word in ["memo", "memorandum"]):
            return "Business Memo"
        elif any(word in query_lower for word in ["presentation", "slide", "deck"]):
            return "Presentation Brief"
        else:
            return "Professional Report"
    
    def format_as_email(self, content: str, recipient: str = "Team") -> str:
        """
        Helper method to format content as an email.
        
        Args:
            content: Content to format
            recipient: Email recipient
            
        Returns:
            Formatted email string
        """
        return f"""To: {recipient}
Subject: [Generated from Analysis]

{content}

Best regards,
[Your Name]"""
    
    def format_as_executive_summary(self, content: str) -> str:
        """
        Helper method to format content as executive summary.
        
        Args:
            content: Content to format
            
        Returns:
            Formatted executive summary
        """
        return f"""EXECUTIVE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{content}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generated: {self._get_timestamp()}"""
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for documents."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M")
