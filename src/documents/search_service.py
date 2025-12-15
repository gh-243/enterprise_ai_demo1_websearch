# STUDENT ASSISTANT FEATURE
"""
Document Search Service

Provides a unified interface for agents to search uploaded documents.
Integrates with the vector database for semantic search.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from .vector_service import VectorDatabaseService
from .models import SearchResult


logger = logging.getLogger(__name__)


class DocumentSearchService:
    """
    Service for searching uploaded documents.
    
    Provides a simple interface for agents to query the document library.
    """
    
    def __init__(
        self,
        vector_service: Optional[VectorDatabaseService] = None,
        db_path: str = "./data/chroma_db",
        collection_name: str = "documents"
    ):
        """
        Initialize the document search service.
        
        Args:
            vector_service: Existing VectorDatabaseService instance (optional)
            db_path: Path to ChromaDB storage
            collection_name: ChromaDB collection name
        """
        if vector_service:
            self.vector_service = vector_service
        else:
            try:
                self.vector_service = VectorDatabaseService(
                    db_path=db_path,
                    collection_name=collection_name
                )
                logger.info("Document search service initialized")
            except Exception as e:
                logger.error(f"Failed to initialize vector service: {e}")
                self.vector_service = None
    
    def is_available(self) -> bool:
        """
        Check if document search is available.
        
        Returns:
            True if the service is ready to search documents
        """
        return self.vector_service is not None
    
    def has_documents(self) -> bool:
        """
        Check if there are any documents in the library.
        
        Returns:
            True if documents are available for search
        """
        if not self.is_available():
            return False
        
        try:
            stats = self.vector_service.get_collection_stats()
            return stats.get("total_chunks", 0) > 0
        except Exception as e:
            logger.error(f"Failed to check document availability: {e}")
            return False
    
    def search(
        self,
        query: str,
        max_results: int = 5,
        similarity_threshold: float = 0.5,
        document_ids: Optional[List[str]] = None
    ) -> List[SearchResult]:
        """
        Search for relevant content in uploaded documents.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            similarity_threshold: Minimum similarity score (0.0 to 1.0)
            document_ids: Optional list of document IDs to search within
            
        Returns:
            List of search results, sorted by relevance
        """
        if not self.is_available():
            logger.warning("Document search not available")
            return []
        
        try:
            results = self.vector_service.search_documents(
                query=query,
                n_results=max_results,
                document_ids=document_ids,
                similarity_threshold=similarity_threshold
            )
            
            logger.info(
                f"Document search for '{query}' returned {len(results)} results "
                f"(threshold: {similarity_threshold})"
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Document search failed: {e}")
            return []
    
    def search_by_document(
        self,
        query: str,
        document_id: str,
        max_results: int = 5
    ) -> List[SearchResult]:
        """
        Search within a specific document.
        
        Args:
            query: Search query
            document_id: Document ID to search within
            max_results: Maximum number of results
            
        Returns:
            List of search results from the specified document
        """
        return self.search(
            query=query,
            max_results=max_results,
            document_ids=[document_id]
        )
    
    def get_document_summary(self, document_id: str) -> Dict[str, Any]:
        """
        Get summary information about a document.
        
        Args:
            document_id: Document ID
            
        Returns:
            Document statistics and metadata
        """
        if not self.is_available():
            return {"error": "Service not available"}
        
        try:
            return self.vector_service.get_document_stats(document_id)
        except Exception as e:
            logger.error(f"Failed to get document summary: {e}")
            return {"error": str(e)}
    
    def list_available_documents(self) -> List[Dict[str, Any]]:
        """
        Get list of available documents for search.
        
        Returns:
            List of document metadata
        """
        if not self.is_available():
            return []
        
        try:
            stats = self.vector_service.get_collection_stats()
            return [{
                "total_documents": stats.get("unique_documents", 0),
                "total_chunks": stats.get("total_chunks", 0),
                "embedding_model": stats.get("embedding_model", "unknown")
            }]
        except Exception as e:
            logger.error(f"Failed to list documents: {e}")
            return []
    
    def format_search_results_for_agent(
        self,
        results: List[SearchResult],
        include_metadata: bool = False
    ) -> str:
        """
        Format search results in a way that's easy for agents to consume.
        
        Args:
            results: List of search results
            include_metadata: Whether to include detailed metadata
            
        Returns:
            Formatted string with search results
        """
        if not results:
            return "No relevant information found in uploaded documents."
        
        formatted_parts = []
        formatted_parts.append(f"Found {len(results)} relevant passages from uploaded documents:\n")
        
        for i, result in enumerate(results, 1):
            formatted_parts.append(f"\n[Source {i}: {result.document_title}]")
            
            if result.page_number:
                formatted_parts.append(f"(Page {result.page_number})")
            
            formatted_parts.append(f"\n{result.content}\n")
            
            if include_metadata:
                formatted_parts.append(f"Relevance Score: {result.similarity_score:.2f}")
                if result.chapter_id:
                    formatted_parts.append(f"Chapter ID: {result.chapter_id}")
        
        return "\n".join(formatted_parts)


# Global instance for easy access
_global_search_service: Optional[DocumentSearchService] = None


def get_document_search_service(
    db_path: str = "./data/chroma_db",
    collection_name: str = "documents"
) -> DocumentSearchService:
    """
    Get or create the global document search service instance.
    
    Args:
        db_path: Path to ChromaDB storage
        collection_name: ChromaDB collection name
        
    Returns:
        DocumentSearchService instance
    """
    global _global_search_service
    
    if _global_search_service is None:
        try:
            _global_search_service = DocumentSearchService(
                db_path=db_path,
                collection_name=collection_name
            )
            logger.info("Global document search service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize global search service: {e}")
            # Create a dummy instance that returns empty results
            _global_search_service = DocumentSearchService(vector_service=None)
    
    return _global_search_service


def search_documents(
    query: str,
    max_results: int = 5,
    similarity_threshold: float = 0.5
) -> List[SearchResult]:
    """
    Quick helper function to search documents.
    
    Args:
        query: Search query
        max_results: Maximum number of results
        similarity_threshold: Minimum similarity score
        
    Returns:
        List of search results
    """
    service = get_document_search_service()
    return service.search(query, max_results, similarity_threshold)
