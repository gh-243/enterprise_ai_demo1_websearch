# STUDENT ASSISTANT FEATURE
"""
Document Upload API Router

FastAPI endpoints for document management in the student assistant.
"""

import os
import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, status, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from datetime import datetime

from src.documents import (
    DocumentProcessor,
    TextExtractor,
    Document,
    DocumentType,
    ProcessingStatus,
    UnsupportedFileTypeError,
    DocumentParsingError,
    check_dependencies
)


# Request/Response Models
class DocumentMetadata(BaseModel):
    """Metadata for document upload."""
    title: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None
    subject: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class DocumentResponse(BaseModel):
    """Document response model."""
    id: str
    title: str
    file_type: str
    file_size: int
    upload_date: datetime
    author: Optional[str] = None
    description: Optional[str] = None
    subject: Optional[str] = None
    processing_status: str
    total_pages: Optional[int] = None
    total_chunks: int
    chapters_count: int
    tags: List[str]
    size_mb: float


class LibraryResponse(BaseModel):
    """Library overview response."""
    total_documents: int
    total_size_mb: float
    processing_count: int
    completed_count: int
    recent_uploads: List[DocumentResponse]


class ProcessingStatusResponse(BaseModel):
    """Document processing status."""
    document_id: str
    status: str
    progress: float  # 0.0 to 1.0
    error_message: Optional[str] = None
    estimated_completion: Optional[datetime] = None


# Router
document_router = APIRouter(prefix="/v1/documents", tags=["documents"])

# Initialize processors
document_processor = DocumentProcessor()
text_extractor = TextExtractor()

# In-memory storage for demo (replace with database in production)
document_library: Dict[str, Document] = {}


@document_router.get("/dependencies")
async def check_document_dependencies():
    """
    Check which document processing dependencies are available.
    
    Returns:
        Dict indicating which file types can be processed
    """
    deps = check_dependencies()
    return {
        "available_processors": deps,
        "supported_types": [
            {"type": "txt", "mime": "text/plain", "available": deps["txt"]},
            {"type": "pdf", "mime": "application/pdf", "available": deps["pdf"]},
            {"type": "docx", "mime": "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "available": deps["docx"]},
            {"type": "epub", "mime": "application/epub+zip", "available": deps["epub"]},
        ],
        "max_file_size_mb": 100,
        "note": "Install missing dependencies with: pip install PyPDF2 python-docx ebooklib"
    }


@document_router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    author: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    subject: Optional[str] = Form(None),
    tags: str = Form(""),  # Comma-separated tags
    user_id: str = Form("default_user")  # TODO: Get from auth
):
    """
    Upload a new document to the library.
    
    Args:
        file: Document file (PDF, EPUB, DOCX, TXT)
        title: Document title (optional, uses filename if not provided)
        author: Document author
        description: Document description
        subject: Subject/category
        tags: Comma-separated tags
        user_id: User ID (from authentication)
        
    Returns:
        Document information
        
    Raises:
        HTTPException: If upload fails or file type not supported
    """
    try:
        # Parse metadata
        metadata = {}
        if title:
            metadata["title"] = title
        if author:
            metadata["author"] = author
        if description:
            metadata["description"] = description
        if subject:
            metadata["subject"] = subject
        
        # Parse tags
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []
        
        # Upload document
        document = await document_processor.upload_document(file, user_id, metadata)
        
        # Add tags
        document.tags = tag_list
        
        # Store in library
        document_library[document.id] = document
        
        # Start background processing (simplified for demo)
        # In production, this would be an async task
        try:
            await process_document_background(document.id)
        except Exception as e:
            # Don't fail upload if processing fails
            document.processing_status = ProcessingStatus.ERROR
            document.error_message = str(e)
        
        return DocumentResponse(
            id=document.id,
            title=document.title,
            file_type=document.file_type.value,
            file_size=document.file_size,
            upload_date=document.upload_date,
            author=document.author,
            description=document.description,
            subject=document.subject,
            processing_status=document.processing_status.value,
            total_pages=document.total_pages,
            total_chunks=document.total_chunks,
            chapters_count=len(document.chapters),
            tags=document.tags,
            size_mb=document.size_mb
        )
        
    except UnsupportedFileTypeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@document_router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    user_id: str = "default_user",  # TODO: Get from auth
    subject: Optional[str] = None,
    author: Optional[str] = None,
    processing_status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """
    List documents in the user's library.
    
    Args:
        user_id: User ID
        subject: Filter by subject
        author: Filter by author
        processing_status: Filter by processing status
        limit: Maximum results
        offset: Results offset
        
    Returns:
        List of documents
    """
    documents = list(document_library.values())
    
    # Apply filters
    if subject:
        documents = [d for d in documents if d.subject == subject]
    if author:
        documents = [d for d in documents if d.author and author.lower() in d.author.lower()]
    if processing_status:
        documents = [d for d in documents if d.processing_status.value == processing_status]
    
    # Sort by upload date (newest first)
    documents.sort(key=lambda d: d.upload_date, reverse=True)
    
    # Apply pagination
    documents = documents[offset:offset + limit]
    
    return [
        DocumentResponse(
            id=doc.id,
            title=doc.title,
            file_type=doc.file_type.value,
            file_size=doc.file_size,
            upload_date=doc.upload_date,
            author=doc.author,
            description=doc.description,
            subject=doc.subject,
            processing_status=doc.processing_status.value,
            total_pages=doc.total_pages,
            total_chunks=doc.total_chunks,
            chapters_count=len(doc.chapters),
            tags=doc.tags,
            size_mb=doc.size_mb
        )
        for doc in documents
    ]


@document_router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str):
    """
    Get detailed information about a specific document.
    
    Args:
        document_id: Document ID
        
    Returns:
        Document details
        
    Raises:
        HTTPException: If document not found
    """
    if document_id not in document_library:
        raise HTTPException(status_code=404, detail="Document not found")
    
    document = document_library[document_id]
    
    return DocumentResponse(
        id=document.id,
        title=document.title,
        file_type=document.file_type.value,
        file_size=document.file_size,
        upload_date=document.upload_date,
        author=document.author,
        description=document.description,
        subject=document.subject,
        processing_status=document.processing_status.value,
        total_pages=document.total_pages,
        total_chunks=document.total_chunks,
        chapters_count=len(document.chapters),
        tags=document.tags,
        size_mb=document.size_mb
    )


@document_router.get("/{document_id}/status", response_model=ProcessingStatusResponse)
async def get_processing_status(document_id: str):
    """
    Get processing status for a document.
    
    Args:
        document_id: Document ID
        
    Returns:
        Processing status information
    """
    if document_id not in document_library:
        raise HTTPException(status_code=404, detail="Document not found")
    
    document = document_library[document_id]
    
    # Calculate progress based on status
    progress_map = {
        ProcessingStatus.PENDING: 0.0,
        ProcessingStatus.PROCESSING: 0.5,
        ProcessingStatus.COMPLETED: 1.0,
        ProcessingStatus.ERROR: 0.0
    }
    
    return ProcessingStatusResponse(
        document_id=document.id,
        status=document.processing_status.value,
        progress=progress_map[document.processing_status],
        error_message=document.error_message
    )


@document_router.get("/{document_id}/chapters")
async def get_document_chapters(document_id: str):
    """
    Get chapters/sections for a document.
    
    Args:
        document_id: Document ID
        
    Returns:
        List of chapters with metadata
    """
    if document_id not in document_library:
        raise HTTPException(status_code=404, detail="Document not found")
    
    document = document_library[document_id]
    
    return {
        "document_id": document.id,
        "document_title": document.title,
        "chapters": [
            {
                "id": chapter.id,
                "title": chapter.title,
                "start_page": chapter.start_page,
                "end_page": chapter.end_page,
                "preview": chapter.content_preview
            }
            for chapter in document.chapters
        ]
    }


@document_router.delete("/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document from the library.
    
    Args:
        document_id: Document ID
        
    Returns:
        Success message
    """
    if document_id not in document_library:
        raise HTTPException(status_code=404, detail="Document not found")
    
    document = document_library[document_id]
    
    # Delete physical file
    try:
        file_deleted = document_processor.delete_document_file(document)
    except Exception:
        file_deleted = False
    
    # Remove from library
    del document_library[document_id]
    
    return {
        "message": "Document deleted successfully",
        "document_id": document_id,
        "file_deleted": file_deleted
    }


@document_router.get("/library/overview", response_model=LibraryResponse)
async def get_library_overview(user_id: str = "default_user"):
    """
    Get overview of user's document library.
    
    Args:
        user_id: User ID
        
    Returns:
        Library statistics and recent uploads
    """
    documents = list(document_library.values())
    
    total_size_bytes = sum(doc.file_size for doc in documents)
    processing_count = len([d for d in documents if d.processing_status == ProcessingStatus.PROCESSING])
    completed_count = len([d for d in documents if d.processing_status == ProcessingStatus.COMPLETED])
    
    # Get 5 most recent uploads
    recent = sorted(documents, key=lambda d: d.upload_date, reverse=True)[:5]
    
    return LibraryResponse(
        total_documents=len(documents),
        total_size_mb=total_size_bytes / (1024 * 1024),
        processing_count=processing_count,
        completed_count=completed_count,
        recent_uploads=[
            DocumentResponse(
                id=doc.id,
                title=doc.title,
                file_type=doc.file_type.value,
                file_size=doc.file_size,
                upload_date=doc.upload_date,
                author=doc.author,
                description=doc.description,
                subject=doc.subject,
                processing_status=doc.processing_status.value,
                total_pages=doc.total_pages,
                total_chunks=doc.total_chunks,
                chapters_count=len(doc.chapters),
                tags=doc.tags,
                size_mb=doc.size_mb
            )
            for doc in recent
        ]
    )


# Background processing function
async def process_document_background(document_id: str):
    """
    Process document in background (extract text, create chunks, etc.).
    
    In production, this would be an async task queue job.
    """
    if document_id not in document_library:
        return
    
    document = document_library[document_id]
    
    try:
        # Update status
        document.processing_status = ProcessingStatus.PROCESSING
        
        # Extract text
        extraction_result = text_extractor.extract_text(document)
        
        # Update document with extracted data
        document.chapters = extraction_result["chapters"]
        document.total_pages = extraction_result["page_count"]
        
        # Update metadata if available
        if extraction_result["metadata"]:
            metadata = extraction_result["metadata"]
            if not document.author and metadata.get("author"):
                document.author = metadata["author"]
            if not document.title and metadata.get("title"):
                document.title = metadata["title"]
        
        # For now, just mark as completed
        # In full implementation, would also:
        # 1. Chunk the text
        # 2. Generate embeddings
        # 3. Store in vector database
        document.processing_status = ProcessingStatus.COMPLETED
        document.last_processed = datetime.now()
        
    except Exception as e:
        document.processing_status = ProcessingStatus.ERROR
        document.error_message = str(e)