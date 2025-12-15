# NEW MULTI-AGENT FEATURE
"""
Research Agent Implementation

Conducts thorough research using uploaded documents first, then web search.
Enhanced with document search capability for student assistant.
"""

from typing import Dict, Any, Optional, List
from src.agents.base_agent import BaseAgent, AgentResponse
from src.providers.base import LLMMessage

# STUDENT ASSISTANT ENHANCEMENT
try:
    from src.documents import get_document_search_service
    DOCUMENT_SEARCH_AVAILABLE = True
except ImportError:
    DOCUMENT_SEARCH_AVAILABLE = False


class ResearchAgent(BaseAgent):
    """
    Research Agent that searches uploaded documents first, then uses web search.
    
    STUDENT ASSISTANT ENHANCEMENT:
    - Searches uploaded documents for relevant information
    - Falls back to web search if documents don't contain answers
    - Clearly indicates source of information (documents vs web)
    """
    
    def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Research a topic using documents first, then web search if needed.
        
        Args:
            query: Research question or topic
            context: Optional context
            
        Returns:
            AgentResponse with research summary
        """
        # STEP 1: Try document search first (STUDENT ASSISTANT)
        document_results = self._search_documents(query)
        document_context = ""
        used_documents = False
        
        if document_results:
            used_documents = True
            document_context = self._format_document_results(document_results)
        
        # STEP 2: Use web search (always or as fallback)
        search_result = self._search(query)
        web_context = self._format_search_results(search_result)
        
        # STEP 3: Combine contexts and generate research summary
        combined_context = self._build_combined_context(
            query, document_context, web_context, used_documents
        )
        
        messages = [
            self._build_system_message(),
            LLMMessage(
                role="user",
                content=combined_context
            )
        ]
        
        llm_response = self._generate_llm_response(messages)
        
        # STEP 4: Build sources list (documents + web)
        sources = []
        
        # Add document sources
        if document_results:
            for i, result in enumerate(document_results[:5], 1):
                sources.append({
                    "id": i,
                    "title": f"{result.document_title} (Uploaded Document)",
                    "type": "document",
                    "url": f"document://{result.document_id}",
                    "page": result.page_number,
                    "relevance": f"{result.similarity_score:.2f}"
                })
        
        # Add web sources
        source_offset = len(sources)
        for i, source in enumerate(search_result.sources[:10], source_offset + 1):
            sources.append({
                "id": i,
                "url": source.url,
                "title": source.url.split('/')[2] if source.url else source.type,
                "type": "web"
            })
        
        return AgentResponse(
            agent_name=self.config.name,
            agent_type=self.config.agent_type,
            content=llm_response.text,
            sources=sources,
            tokens_used=llm_response.tokens_in + llm_response.tokens_out,
            metadata={
                "search_query": query,
                "num_sources": len(sources),
                "model": llm_response.model,
                "used_documents": used_documents,
                "document_results": len(document_results) if document_results else 0,
                "web_sources": len(search_result.sources),
                "has_citations": search_result.has_citations
            }
        )
    
    def _search_documents(self, query: str) -> List[Any]:
        """
        Search uploaded documents for relevant information.
        
        Args:
            query: Search query
            
        Returns:
            List of search results from documents
        """
        if not DOCUMENT_SEARCH_AVAILABLE:
            return []
        
        try:
            doc_service = get_document_search_service()
            
            if not doc_service.has_documents():
                return []
            
            results = doc_service.search(
                query=query,
                max_results=5,
                similarity_threshold=0.6  # Higher threshold for quality
            )
            
            return results
            
        except Exception as e:
            # Don't fail if document search fails - just continue with web search
            print(f"Document search failed: {e}")
            return []
    
    def _format_document_results(self, results: List[Any]) -> str:
        """Format document search results for LLM context."""
        if not results:
            return ""
        
        formatted = [f"\n=== INFORMATION FROM UPLOADED DOCUMENTS ({len(results)} passages) ===\n"]
        
        for i, result in enumerate(results, 1):
            formatted.append(f"\n[Document Source {i}: {result.document_title}]")
            if result.page_number:
                formatted.append(f"(Page {result.page_number})")
            formatted.append(f"\n{result.content}\n")
            formatted.append(f"Relevance: {result.similarity_score:.2f}\n")
        
        return "\n".join(formatted)
    
    def _build_combined_context(
        self,
        query: str,
        document_context: str,
        web_context: str,
        used_documents: bool
    ) -> str:
        """Build combined research context from documents and web."""
        parts = [f"Research Question: {query}\n"]
        
        if used_documents and document_context:
            parts.append(document_context)
            parts.append("\n=== ADDITIONAL WEB SEARCH RESULTS ===\n")
        else:
            parts.append("\n=== WEB SEARCH RESULTS ===\n")
        
        parts.append(web_context)
        
        parts.append("""
Provide a comprehensive research summary with:
1. Key findings (clearly cite whether from documents or web)
2. Main themes and patterns
3. Important statistics or data points
4. Areas of consensus and disagreement
5. Gaps or areas needing further investigation

IMPORTANT: 
- If information came from uploaded documents, mention it explicitly
- Prioritize information from uploaded documents as it may be more relevant to the student
- Use web sources to supplement or provide additional context
""")
        
        return "\n".join(parts)
    
    def _format_search_results(self, search_result) -> str:
        """Format search results for LLM context."""
        formatted = [f"Search Answer: {search_result.text}\n"]
        
        if search_result.citations:
            formatted.append("\nCitations:")
            for i, citation in enumerate(search_result.citations, 1):
                formatted.append(f"[{i}] {citation.title}: {citation.url}")
        
        if search_result.sources:
            formatted.append("\nSources Consulted:")
            for i, source in enumerate(search_result.sources, 1):
                formatted.append(f"  {i}. {source.url} ({source.type})")
        
        return "\n".join(formatted)
