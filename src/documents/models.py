# STUDENT ASSISTANT FEATURE
"""
Document Models

Data models for the student assistant document processing system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class DocumentType(Enum):
    """Supported document types."""
    PDF = "pdf"
    EPUB = "epub"
    DOCX = "docx"
    TXT = "txt"


class ProcessingStatus(Enum):
    """Document processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class Chapter:
    """Represents a chapter or section within a document."""
    id: str
    title: str
    start_page: Optional[int] = None
    end_page: Optional[int] = None
    start_chunk_id: Optional[str] = None
    end_chunk_id: Optional[str] = None
    content_preview: Optional[str] = None  # First 200 chars
    
    
@dataclass
class Document:
    """Represents an uploaded document in the student library."""
    id: str
    title: str
    file_type: DocumentType
    file_path: str
    file_size: int  # bytes
    upload_date: datetime
    
    # Optional metadata
    author: Optional[str] = None
    description: Optional[str] = None
    isbn: Optional[str] = None
    publication_year: Optional[int] = None
    subject: Optional[str] = None
    
    # Processing status
    processing_status: ProcessingStatus = ProcessingStatus.PENDING
    error_message: Optional[str] = None
    
    # Content structure
    total_pages: Optional[int] = None
    total_chunks: int = 0
    chapters: List[Chapter] = field(default_factory=list)
    
    # Search metadata
    embedding_model: Optional[str] = None
    last_processed: Optional[datetime] = None
    
    # User metadata
    tags: List[str] = field(default_factory=list)
    notes: Optional[str] = None
    reading_progress: float = 0.0  # 0.0 to 1.0
    
    @property
    def file_extension(self) -> str:
        """Get file extension from type."""
        return self.file_type.value
    
    @property
    def is_processed(self) -> bool:
        """Check if document is fully processed."""
        return self.processing_status == ProcessingStatus.COMPLETED
    
    @property
    def size_mb(self) -> float:
        """Get file size in MB."""
        return self.file_size / (1024 * 1024)


@dataclass
class DocumentChunk:
    """Represents a chunk of text from a document for vector search."""
    id: str
    document_id: str
    chunk_index: int  # Order within document
    text: str
    
    # Location metadata
    chapter_id: Optional[str] = None
    page_number: Optional[int] = None
    start_char: Optional[int] = None
    end_char: Optional[int] = None
    
    # Vector embedding
    embedding: Optional[List[float]] = None
    embedding_model: Optional[str] = None
    
    # Content metadata
    word_count: int = 0
    language: str = "en"
    
    # Processing metadata
    created_date: datetime = field(default_factory=datetime.now)
    
    @property
    def preview(self) -> str:
        """Get first 100 characters of chunk."""
        return self.text[:100] + "..." if len(self.text) > 100 else self.text


@dataclass
class SearchResult:
    """Result from document search."""
    chunk: DocumentChunk
    document: Document
    relevance_score: float
    
    # Context
    surrounding_chunks: List[DocumentChunk] = field(default_factory=list)
    
    @property
    def citation(self) -> str:
        """Generate citation for this result."""
        parts = [self.document.title]
        
        if self.document.author:
            parts.append(f"by {self.document.author}")
        
        if self.chunk.chapter_id:
            chapter = next((c for c in self.document.chapters if c.id == self.chunk.chapter_id), None)
            if chapter:
                parts.append(f"Chapter: {chapter.title}")
        
        if self.chunk.page_number:
            parts.append(f"Page {self.chunk.page_number}")
        
        return ", ".join(parts)


@dataclass
class DocumentLibrary:
    """Represents a user's document library."""
    user_id: str
    documents: List[Document] = field(default_factory=list)
    created_date: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    
    # Library statistics
    total_documents: int = 0
    total_size_bytes: int = 0
    total_chunks: int = 0
    
    # Organization
    collections: Dict[str, List[str]] = field(default_factory=dict)  # collection_name -> doc_ids
    favorites: List[str] = field(default_factory=list)  # doc_ids
    
    def add_document(self, document: Document) -> None:
        """Add document to library."""
        self.documents.append(document)
        self.total_documents += 1
        self.total_size_bytes += document.file_size
        self.last_accessed = datetime.now()
    
    def get_document(self, doc_id: str) -> Optional[Document]:
        """Get document by ID."""
        return next((doc for doc in self.documents if doc.id == doc_id), None)
    
    def search_by_title(self, query: str) -> List[Document]:
        """Search documents by title."""
        query_lower = query.lower()
        return [doc for doc in self.documents if query_lower in doc.title.lower()]
    
    def get_by_subject(self, subject: str) -> List[Document]:
        """Get documents by subject."""
        return [doc for doc in self.documents if doc.subject == subject]
    
    def get_recent(self, limit: int = 10) -> List[Document]:
        """Get recently uploaded documents."""
        return sorted(self.documents, key=lambda d: d.upload_date, reverse=True)[:limit]


@dataclass
class DocumentSearchQuery:
    """Query for searching within documents."""
    text: str
    document_ids: Optional[List[str]] = None  # Limit to specific documents
    chapter_ids: Optional[List[str]] = None   # Limit to specific chapters
    max_results: int = 10
    min_relevance_score: float = 0.7
    include_context: bool = True  # Include surrounding chunks
    
    # Filters
    document_types: Optional[List[DocumentType]] = None
    subjects: Optional[List[str]] = None
    authors: Optional[List[str]] = None


# Exception classes
class DocumentError(Exception):
    """Base exception for document processing errors."""
    pass


class UnsupportedFileTypeError(DocumentError):
    """Raised when file type is not supported."""
    pass


class DocumentParsingError(DocumentError):
    """Raised when document cannot be parsed."""
    pass


class EmbeddingError(DocumentError):
    """Raised when embedding generation fails."""
    pass