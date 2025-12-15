# NEW MULTI-AGENT FEATURE
"""
Fact-Check Agent Implementation

Verifies claims using uploaded documents and multiple web sources.
Enhanced with document search capability for student assistant.
"""

from typing import Dict, Any, Optional, List
import re
from src.agents.base_agent import BaseAgent, AgentResponse
from src.providers.base import LLMMessage

# STUDENT ASSISTANT ENHANCEMENT
try:
    from src.documents import get_document_search_service
    DOCUMENT_SEARCH_AVAILABLE = True
except ImportError:
    DOCUMENT_SEARCH_AVAILABLE = False


class FactCheckAgent(BaseAgent):
    """
    Fact-Check Agent that verifies claims using documents first, then web sources.
    
    STUDENT ASSISTANT ENHANCEMENT:
    - Checks uploaded documents for verification
    - Uses web sources for additional verification
    - Shows clear evidence from both sources
    """
    
    def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Verify a claim or statement using documents and multiple web sources.
        
        Args:
            query: Claim to fact-check
            context: Optional context
            
        Returns:
            AgentResponse with fact-check verdict and confidence score
        """
        # STEP 1: Search documents for relevant information (STUDENT ASSISTANT)
        document_results = self._search_documents(query)
        document_evidence = ""
        used_documents = False
        
        if document_results:
            used_documents = True
            document_evidence = self._format_document_evidence(document_results)
        
        # STEP 2: Search web for verification
        search_result = self._search(query)
        
        # STEP 3: Search web for counter-evidence
        counter_query = f"{query} debunked false myth"
        counter_result = self._search(counter_query)
        
        # STEP 4: Build combined evidence context
        evidence_context = self._build_combined_evidence(
            document_evidence, search_result, counter_result, used_documents
        )
        
        # STEP 5: Generate fact-check analysis
        messages = [
            self._build_system_message(),
            LLMMessage(
                role="user",
                content=evidence_context
            )
        ]
        
        llm_response = self._generate_llm_response(messages)
        
        # STEP 6: Extract confidence score
        confidence_score = self._extract_confidence_score(llm_response.text)
        
        # STEP 7: Build sources list (documents + web)
        sources = []
        
        # Add document sources
        if document_results:
            for i, result in enumerate(document_results[:3], 1):
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
        web_sources = self._build_sources_list(search_result, counter_result)
        for source in web_sources:
            source["id"] = source_offset + source["id"]
            sources.append(source)
        
        return AgentResponse(
            agent_name=self.config.name,
            agent_type=self.config.agent_type,
            content=llm_response.text,
            sources=sources,
            confidence_score=confidence_score,
            tokens_used=llm_response.tokens_in + llm_response.tokens_out,
            metadata={
                "claim": query,
                "num_sources_checked": len(sources),
                "model": llm_response.model,
                "used_documents": used_documents,
                "document_results": len(document_results) if document_results else 0,
                "web_sources": len(web_sources)
            }
        )
    
    def _search_documents(self, query: str) -> List[Any]:
        """Search uploaded documents for fact-checking information."""
        if not DOCUMENT_SEARCH_AVAILABLE:
            return []
        
        try:
            doc_service = get_document_search_service()
            
            if not doc_service.has_documents():
                return []
            
            results = doc_service.search(
                query=query,
                max_results=3,
                similarity_threshold=0.65  # High threshold for fact-checking
            )
            
            return results
            
        except Exception as e:
            print(f"Document search failed: {e}")
            return []
    
    def _format_document_evidence(self, results: List[Any]) -> str:
        """Format document evidence for fact-checking."""
        if not results:
            return ""
        
        formatted = [f"\n=== EVIDENCE FROM UPLOADED DOCUMENTS ({len(results)} passages) ===\n"]
        
        for i, result in enumerate(results, 1):
            formatted.append(f"\n[Document Evidence {i}: {result.document_title}]")
            if result.page_number:
                formatted.append(f"(Page {result.page_number})")
            formatted.append(f"\n{result.content}\n")
            formatted.append(f"Relevance: {result.similarity_score:.2f}\n")
        
        return "\n".join(formatted)
    
    def _build_combined_evidence(
        self,
        document_evidence: str,
        search_result: Any,
        counter_result: Any,
        used_documents: bool
    ) -> str:
        """Build combined evidence from documents and web sources."""
        parts = []
        
        parts.append("Claim to Verify: " + (self.config.description or "Unknown claim"))
        
        if used_documents and document_evidence:
            parts.append(document_evidence)
            parts.append("\n=== ADDITIONAL WEB EVIDENCE ===\n")
        else:
            parts.append("\n=== WEB EVIDENCE ===\n")
        
        # Add web evidence
        parts.append(self._format_evidence(search_result, counter_result))
        
        parts.append("""
Provide a fact-check report with:
1. Clear verdict (TRUE/FALSE/UNCERTAIN)
2. Confidence score (0-100%)
3. Supporting evidence with quotes and sources
4. Any contradictions or caveats
5. Show your receipts - be specific about evidence

IMPORTANT:
- If evidence came from uploaded documents, explicitly mention it
- Documents may contain course-specific or authoritative information
- Consider both document evidence and web sources in your verdict
- Prioritize document evidence if it's from authoritative sources

Use the structured format from your system prompt.""")
        
        return "\n".join(parts)
        
        return AgentResponse(
            agent_name=self.config.name,
            agent_type=self.config.agent_type,
            content=llm_response.text,
            sources=sources,
            confidence_score=confidence_score,
            tokens_used=llm_response.tokens_in + llm_response.tokens_out,
            metadata={
                "claim": query,
                "num_sources_checked": len(sources),
                "model": llm_response.model,
                "verification_approach": "multi-source cross-reference"
            }
        )
    
    def _format_evidence(self, primary_result, counter_result) -> str:
        """Format evidence from multiple search perspectives."""
        formatted = ["PRIMARY EVIDENCE:"]
        formatted.append(f"Answer: {primary_result.text}\n")
        
        if primary_result.citations:
            formatted.append("Citations:")
            for i, citation in enumerate(primary_result.citations, 1):
                formatted.append(f"[{i}] {citation.title}: {citation.url}")
        
        formatted.append("\nCOUNTER-EVIDENCE / ALTERNATIVE VIEWS:")
        formatted.append(f"Answer: {counter_result.text}\n")
        
        if counter_result.citations:
            formatted.append("Citations:")
            for i, citation in enumerate(counter_result.citations, 1):
                formatted.append(f"[{i+5}] {citation.title}: {citation.url}")
        
        return "\n".join(formatted)
    
    def _extract_confidence_score(self, text: str) -> Optional[float]:
        """Extract confidence score from response text."""
        # Look for patterns like "95%" or "Confidence: 85%"
        patterns = [
            r'Confidence[:\s]+(\d+)%',
            r'(\d+)%\s+confidence',
            r'Score[:\s]+(\d+)%',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return float(match.group(1))
        
        return None
    
    def _build_sources_list(self, primary_result, counter_result) -> List[Dict[str, Any]]:
        """Build comprehensive sources list from both searches."""
        sources = []
        
        # Add sources from primary search
        for i, source in enumerate(primary_result.sources[:5], 1):
            sources.append({
                "id": i,
                "url": source.url,
                "type": f"primary-{source.type}",
                "category": "supporting"
            })
        
        # Add sources from counter search
        for i, source in enumerate(counter_result.sources[:5], 6):
            sources.append({
                "id": i,
                "url": source.url,
                "type": f"counter-{source.type}",
                "category": "alternative"
            })
        
        return sources
