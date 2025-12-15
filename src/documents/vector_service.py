# STUDENT ASSISTANT FEATURE
"""
Vector Database Service

ChromaDB integration for semantic search within uploaded documents.
"""

import os
import json
import uuid
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import numpy as np

from .models import Document, DocumentChunk, SearchResult


logger = logging.getLogger(__name__)


class VectorDatabaseService:
    """
    Service for managing document embeddings and semantic search.
    
    Uses ChromaDB for vector storage and sentence-transformers for embeddings.
    """
    
    def __init__(
        self,
        db_path: str = "./data/chroma_db",
        embedding_model: str = "all-MiniLM-L6-v2",
        collection_name: str = "documents"
    ):
        """
        Initialize the vector database service.
        
        Args:
            db_path: Path to store ChromaDB data
            embedding_model: HuggingFace model for embeddings
            collection_name: ChromaDB collection name
        """
        self.db_path = db_path
        self.embedding_model_name = embedding_model
        self.collection_name = collection_name
        
        # Initialize ChromaDB client
        self._init_chroma_client()
        
        # Initialize embedding model
        self._init_embedding_model()
        
        # Get or create collection
        self.collection = self._get_or_create_collection()
        
        logger.info(f"VectorDatabaseService initialized with {embedding_model}")
    
    def _init_chroma_client(self):
        """Initialize ChromaDB client."""
        try:
            # Ensure db directory exists
            os.makedirs(self.db_path, exist_ok=True)
            
            # Create ChromaDB client with persistent storage
            self.client = chromadb.PersistentClient(
                path=self.db_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            logger.info(f"ChromaDB client initialized at {self.db_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB client: {e}")
            raise
    
    def _init_embedding_model(self):
        """Initialize sentence transformer model."""
        try:
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            
            # Test embedding generation
            test_text = "Test embedding generation"
            test_embedding = self.embedding_model.encode([test_text])
            self.embedding_dimension = len(test_embedding[0])
            
            logger.info(
                f"Embedding model {self.embedding_model_name} loaded "
                f"(dimension: {self.embedding_dimension})"
            )
            
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def _get_or_create_collection(self):
        """Get or create ChromaDB collection."""
        try:
            # Try to get existing collection
            collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"Using existing collection: {self.collection_name}")
            
        except ValueError:
            # Collection doesn't exist, create it
            collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Student Assistant Document Chunks"}
            )
            logger.info(f"Created new collection: {self.collection_name}")
        
        return collection
    
    def add_document_chunks(self, document: Document, chunks: List[DocumentChunk]) -> bool:
        """
        Add document chunks to the vector database.
        
        Args:
            document: Document metadata
            chunks: List of document chunks to add
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not chunks:
                logger.warning(f"No chunks provided for document {document.id}")
                return True
            
            # Prepare data for ChromaDB
            chunk_ids = []
            chunk_texts = []
            chunk_embeddings = []
            chunk_metadatas = []
            
            for chunk in chunks:
                chunk_ids.append(chunk.id)
                chunk_texts.append(chunk.content)
                
                # Add metadata
                metadata = {
                    "document_id": document.id,
                    "document_title": document.title,
                    "chunk_index": chunk.chunk_index,
                    "page_number": chunk.page_number,
                    "chapter_id": chunk.chapter_id or "",
                    "chunk_type": chunk.chunk_type,
                    "upload_date": document.upload_date.isoformat(),
                    "file_type": document.file_type.value,
                    "author": document.author or "",
                    "subject": document.subject or ""
                }
                chunk_metadatas.append(metadata)
            
            # Generate embeddings
            logger.info(f"Generating embeddings for {len(chunks)} chunks...")
            embeddings = self.embedding_model.encode(
                chunk_texts,
                show_progress_bar=True,
                batch_size=32
            )
            
            # Convert to list for ChromaDB
            chunk_embeddings = embeddings.tolist()
            
            # Add to ChromaDB
            self.collection.add(
                ids=chunk_ids,
                documents=chunk_texts,
                embeddings=chunk_embeddings,
                metadatas=chunk_metadatas
            )
            
            logger.info(
                f"Successfully added {len(chunks)} chunks for document "
                f"{document.title} to vector database"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add document chunks: {e}")
            return False
    
    def search_documents(
        self,
        query: str,
        n_results: int = 10,
        document_ids: Optional[List[str]] = None,
        document_types: Optional[List[str]] = None,
        similarity_threshold: float = 0.0
    ) -> List[SearchResult]:
        """
        Search for relevant document chunks.
        
        Args:
            query: Search query
            n_results: Maximum number of results
            document_ids: Filter by specific document IDs
            document_types: Filter by document types
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of search results
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query]).tolist()[0]
            
            # Build where clause for filtering
            where_clause = {}
            
            if document_ids:
                where_clause["document_id"] = {"$in": document_ids}
            
            if document_types:
                where_clause["file_type"] = {"$in": document_types}
            
            # Search ChromaDB
            search_kwargs = {
                "query_embeddings": [query_embedding],
                "n_results": n_results
            }
            
            if where_clause:
                search_kwargs["where"] = where_clause
            
            results = self.collection.query(**search_kwargs)
            
            # Process results
            search_results = []
            
            if results["ids"] and results["ids"][0]:
                for i, chunk_id in enumerate(results["ids"][0]):
                    distance = results["distances"][0][i]
                    similarity = 1 - distance  # Convert distance to similarity
                    
                    if similarity >= similarity_threshold:
                        metadata = results["metadatas"][0][i]
                        content = results["documents"][0][i]
                        
                        result = SearchResult(
                            chunk_id=chunk_id,
                            document_id=metadata["document_id"],
                            document_title=metadata["document_title"],
                            content=content,
                            similarity_score=similarity,
                            page_number=metadata.get("page_number"),
                            chapter_id=metadata.get("chapter_id") or None,
                            chunk_type=metadata["chunk_type"],
                            metadata=metadata
                        )
                        
                        search_results.append(result)
            
            logger.info(
                f"Search for '{query}' returned {len(search_results)} results "
                f"(threshold: {similarity_threshold})"
            )
            
            return search_results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def search_similar_chunks(
        self,
        chunk_id: str,
        n_results: int = 5,
        same_document_only: bool = True
    ) -> List[SearchResult]:
        """
        Find chunks similar to a given chunk.
        
        Args:
            chunk_id: ID of the reference chunk
            n_results: Maximum number of results
            same_document_only: Whether to search only within the same document
            
        Returns:
            List of similar chunks
        """
        try:
            # Get the reference chunk
            ref_result = self.collection.get(ids=[chunk_id])
            
            if not ref_result["embeddings"] or not ref_result["embeddings"][0]:
                logger.warning(f"Chunk {chunk_id} not found")
                return []
            
            ref_embedding = ref_result["embeddings"][0]
            ref_metadata = ref_result["metadatas"][0]
            
            # Build search criteria
            search_kwargs = {
                "query_embeddings": [ref_embedding],
                "n_results": n_results + 1  # +1 to exclude self
            }
            
            if same_document_only:
                search_kwargs["where"] = {
                    "document_id": ref_metadata["document_id"]
                }
            
            # Search
            results = self.collection.query(**search_kwargs)
            
            # Process results (excluding the reference chunk itself)
            similar_results = []
            
            if results["ids"] and results["ids"][0]:
                for i, found_id in enumerate(results["ids"][0]):
                    if found_id != chunk_id:  # Exclude self
                        distance = results["distances"][0][i]
                        similarity = 1 - distance
                        
                        metadata = results["metadatas"][0][i]
                        content = results["documents"][0][i]
                        
                        result = SearchResult(
                            chunk_id=found_id,
                            document_id=metadata["document_id"],
                            document_title=metadata["document_title"],
                            content=content,
                            similarity_score=similarity,
                            page_number=metadata.get("page_number"),
                            chapter_id=metadata.get("chapter_id") or None,
                            chunk_type=metadata["chunk_type"],
                            metadata=metadata
                        )
                        
                        similar_results.append(result)
                        
                        if len(similar_results) >= n_results:
                            break
            
            return similar_results
            
        except Exception as e:
            logger.error(f"Similar chunk search failed: {e}")
            return []
    
    def get_document_stats(self, document_id: str) -> Dict[str, Any]:
        """
        Get statistics for a document in the vector database.
        
        Args:
            document_id: Document ID
            
        Returns:
            Document statistics
        """
        try:
            # Get all chunks for the document
            results = self.collection.get(
                where={"document_id": document_id}
            )
            
            if not results["ids"]:
                return {"chunk_count": 0, "document_id": document_id}
            
            chunk_count = len(results["ids"])
            metadatas = results["metadatas"]
            
            # Extract statistics
            page_numbers = [m.get("page_number") for m in metadatas if m.get("page_number")]
            chapters = list(set(m.get("chapter_id") for m in metadatas if m.get("chapter_id")))
            chunk_types = list(set(m["chunk_type"] for m in metadatas))
            
            stats = {
                "document_id": document_id,
                "chunk_count": chunk_count,
                "page_range": {
                    "min": min(page_numbers) if page_numbers else None,
                    "max": max(page_numbers) if page_numbers else None
                },
                "chapter_count": len(chapters),
                "chunk_types": chunk_types,
                "embedding_dimension": self.embedding_dimension
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get document stats: {e}")
            return {"error": str(e), "document_id": document_id}
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete all chunks for a document from the vector database.
        
        Args:
            document_id: Document ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get all chunk IDs for the document
            results = self.collection.get(
                where={"document_id": document_id}
            )
            
            if results["ids"]:
                self.collection.delete(ids=results["ids"])
                logger.info(f"Deleted {len(results['ids'])} chunks for document {document_id}")
            else:
                logger.info(f"No chunks found for document {document_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document chunks: {e}")
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get overall collection statistics.
        
        Returns:
            Collection statistics
        """
        try:
            # Get collection info
            collection_info = self.collection.count()
            
            # Get sample of documents
            sample_results = self.collection.get(limit=1000)
            
            if sample_results["metadatas"]:
                metadatas = sample_results["metadatas"]
                
                # Extract statistics
                document_ids = list(set(m["document_id"] for m in metadatas))
                file_types = list(set(m["file_type"] for m in metadatas))
                authors = list(set(m.get("author", "") for m in metadatas if m.get("author")))
                subjects = list(set(m.get("subject", "") for m in metadatas if m.get("subject")))
                
                stats = {
                    "total_chunks": collection_info,
                    "unique_documents": len(document_ids),
                    "file_types": file_types,
                    "unique_authors": len(authors),
                    "unique_subjects": len(subjects),
                    "embedding_model": self.embedding_model_name,
                    "embedding_dimension": self.embedding_dimension,
                    "db_path": self.db_path
                }
            else:
                stats = {
                    "total_chunks": 0,
                    "unique_documents": 0,
                    "embedding_model": self.embedding_model_name,
                    "embedding_dimension": self.embedding_dimension,
                    "db_path": self.db_path
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {"error": str(e)}
    
    def reset_collection(self) -> bool:
        """
        Reset the entire collection (delete all data).
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete collection
            self.client.delete_collection(name=self.collection_name)
            
            # Recreate collection
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Student Assistant Document Chunks"}
            )
            
            logger.info(f"Collection {self.collection_name} reset successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reset collection: {e}")
            return False


# Text chunking utilities
class DocumentChunker:
    """
    Utility class for chunking documents into manageable pieces.
    """
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        min_chunk_size: int = 100
    ):
        """
        Initialize the document chunker.
        
        Args:
            chunk_size: Target size for each chunk (in characters)
            chunk_overlap: Overlap between chunks (in characters)
            min_chunk_size: Minimum chunk size (smaller chunks are merged)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
    
    def chunk_text(
        self,
        text: str,
        document: Document,
        chapter_id: Optional[str] = None,
        page_number: Optional[int] = None
    ) -> List[DocumentChunk]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            document: Document metadata
            chapter_id: Chapter ID (if applicable)
            page_number: Page number (if applicable)
            
        Returns:
            List of document chunks
        """
        chunks = []
        
        if len(text) <= self.chunk_size:
            # Text is small enough to be a single chunk
            chunk = DocumentChunk(
                id=str(uuid.uuid4()),
                document_id=document.id,
                content=text.strip(),
                chunk_index=0,
                start_char=0,
                end_char=len(text),
                page_number=page_number,
                chapter_id=chapter_id,
                chunk_type="content"
            )
            chunks.append(chunk)
            return chunks
        
        # Split into overlapping chunks
        start = 0
        chunk_index = 0
        
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            
            # Try to find a good break point (sentence or paragraph end)
            if end < len(text):
                # Look for sentence endings
                sentence_ends = ['.', '!', '?', '\n\n']
                best_end = end
                
                for i in range(end - 50, end + 50):
                    if i < len(text) and text[i] in sentence_ends:
                        best_end = i + 1
                        break
                
                end = best_end
            
            chunk_text = text[start:end].strip()
            
            if len(chunk_text) >= self.min_chunk_size:
                chunk = DocumentChunk(
                    id=str(uuid.uuid4()),
                    document_id=document.id,
                    content=chunk_text,
                    chunk_index=chunk_index,
                    start_char=start,
                    end_char=end,
                    page_number=page_number,
                    chapter_id=chapter_id,
                    chunk_type="content"
                )
                chunks.append(chunk)
                chunk_index += 1
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            
            # Prevent infinite loop
            if start <= chunks[-1].start_char if chunks else 0:
                start = end
        
        return chunks
    
    def chunk_document(self, document: Document, text_content: str) -> List[DocumentChunk]:
        """
        Chunk an entire document, handling chapters if available.
        
        Args:
            document: Document to chunk
            text_content: Full text content
            
        Returns:
            List of all document chunks
        """
        all_chunks = []
        
        if document.chapters:
            # Chunk by chapters
            for chapter in document.chapters:
                chapter_chunks = self.chunk_text(
                    text=chapter.content,
                    document=document,
                    chapter_id=chapter.id,
                    page_number=chapter.start_page
                )
                all_chunks.extend(chapter_chunks)
        else:
            # Chunk entire document
            chunks = self.chunk_text(
                text=text_content,
                document=document
            )
            all_chunks.extend(chunks)
        
        # Update chunk indices
        for i, chunk in enumerate(all_chunks):
            chunk.chunk_index = i
        
        return all_chunks