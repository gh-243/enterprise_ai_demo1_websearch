# STUDENT ASSISTANT FEATURE
"""
Document Processing Module for Student Assistant

This module provides comprehensive document processing capabilities including:
- File upload and validation
- Text extraction from PDF, DOCX, EPUB, and TXT files  
- Document chunking and embedding generation
- Vector database integration for semantic search
- Metadata management and indexing

The module is designed to transform uploaded documents into searchable knowledge bases
that can be queried by the student assistant's agents.
"""

from .models import (
    Document,
    DocumentChunk,
    Chapter,
    DocumentLibrary,
    SearchResult,
    DocumentType,
    ProcessingStatus,
    DocumentError,
    UnsupportedFileTypeError,
    DocumentParsingError,
    EmbeddingError
)

from .processor import (
    DocumentProcessor,
    TextExtractor
)

from .vector_service import (
    VectorDatabaseService,
    DocumentChunker
)

from .search_service import (
    DocumentSearchService,
    get_document_search_service,
    search_documents
)


def check_dependencies() -> dict:
    """
    Check which document processing dependencies are available.
    
    Returns:
        Dict indicating which file types can be processed
    """
    dependencies = {
        'txt': True,  # Built-in support
        'pdf': False,
        'docx': False,
        'epub': False,
        'vector_db': False,
        'embeddings': False
    }
    
    try:
        import PyPDF2
        dependencies['pdf'] = True
    except ImportError:
        pass
    
    try:
        import docx
        dependencies['docx'] = True
    except ImportError:
        pass
    
    try:
        import ebooklib
        dependencies['epub'] = True
    except ImportError:
        pass
    
    try:
        import chromadb
        dependencies['vector_db'] = True
    except ImportError:
        pass
    
    try:
        import sentence_transformers
        dependencies['embeddings'] = True
    except ImportError:
        pass
    
    return dependencies


__all__ = [
    # Models
    'Document',
    'DocumentChunk', 
    'Chapter',
    'DocumentLibrary',
    'SearchResult',
    'DocumentType',
    'ProcessingStatus',
    
    # Exceptions
    'DocumentError',
    'UnsupportedFileTypeError',
    'DocumentParsingError',
    'EmbeddingError',
    
    # Processors
    'DocumentProcessor',
    'TextExtractor',
    
    # Vector Services
    'VectorDatabaseService',
    'DocumentChunker',
    
    # Search Services
    'DocumentSearchService',
    'get_document_search_service',
    'search_documents',
    
    # Utilities
    'check_dependencies'
]

from .models import (
    Document,
    DocumentChunk,
    DocumentType,
    ProcessingStatus,
    Chapter,
    SearchResult,
    DocumentLibrary,
    DocumentSearchQuery,
    DocumentError,
    UnsupportedFileTypeError,
    DocumentParsingError,
    EmbeddingError
)

from .processor import (
    DocumentProcessor,
    TextExtractor
)

__all__ = [
    # Models
    "Document",
    "DocumentChunk", 
    "DocumentType",
    "ProcessingStatus",
    "Chapter",
    "SearchResult",
    "DocumentLibrary",
    "DocumentSearchQuery",
    
    # Exceptions
    "DocumentError",
    "UnsupportedFileTypeError",
    "DocumentParsingError", 
    "EmbeddingError",
    
    # Processors
    "DocumentProcessor",
    "TextExtractor",
    "check_dependencies"
]