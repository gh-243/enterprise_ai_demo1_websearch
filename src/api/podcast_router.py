# STUDENT ASSISTANT FEATURE - PHASE 5
"""
Podcast Generation API Router

Provides REST API endpoints for podcast generation from documents.
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from pathlib import Path
import logging

from src.agents import AgentConfig, AgentType
from src.agents.podcast_agent import PodcastAgent, SUPPORTED_VOICES, SUPPORTED_FORMATS, PODCAST_STYLES
from src.providers.openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/podcasts", tags=["podcasts"])


# Request/Response Models
class PodcastGenerationRequest(BaseModel):
    """Request model for podcast generation."""
    query: str = Field(..., description="Podcast topic or content query")
    document_id: Optional[str] = Field(None, description="Specific document ID to use")
    chapter_id: Optional[str] = Field(None, description="Specific chapter ID to use")
    style: Literal["conversational", "lecture", "summary", "storytelling"] = Field(
        "conversational",
        description="Podcast style"
    )
    voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"] = Field(
        "nova",
        description="TTS voice to use"
    )
    format: Literal["mp3", "opus", "aac", "flac"] = Field(
        "mp3",
        description="Audio format"
    )
    duration_target: int = Field(
        5,
        ge=1,
        le=30,
        description="Target duration in minutes (1-30)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Explain the fundamentals of machine learning",
                "style": "conversational",
                "voice": "nova",
                "format": "mp3",
                "duration_target": 5
            }
        }


class PodcastSource(BaseModel):
    """Source information for podcast content."""
    type: str = Field(..., description="Source type (document or web)")
    title: Optional[str] = Field(None, description="Source title")
    document_id: Optional[str] = Field(None, description="Document ID if applicable")
    page: Optional[int] = Field(None, description="Page number if applicable")
    url: Optional[str] = Field(None, description="URL if web source")


class PodcastResponse(BaseModel):
    """Response model for generated podcast."""
    podcast_id: str = Field(..., description="Unique podcast ID")
    query: str = Field(..., description="Original query")
    script: str = Field(..., description="Generated podcast script")
    audio_file: Optional[str] = Field(None, description="Path to audio file")
    audio_url: Optional[str] = Field(None, description="URL to download audio")
    style: str = Field(..., description="Podcast style used")
    voice: str = Field(..., description="TTS voice used")
    format: str = Field(..., description="Audio format")
    duration_target: int = Field(..., description="Target duration in minutes")
    sources: List[PodcastSource] = Field(default_factory=list, description="Content sources")
    used_documents: bool = Field(..., description="Whether documents were used")
    
    class Config:
        json_schema_extra = {
            "example": {
                "podcast_id": "podcast_20250113_142030",
                "query": "Explain machine learning",
                "script": "Welcome to today's episode where we'll explore...",
                "audio_file": "podcasts/podcast_20250113_142030.mp3",
                "audio_url": "/v1/podcasts/download/podcast_20250113_142030.mp3",
                "style": "conversational",
                "voice": "nova",
                "format": "mp3",
                "duration_target": 5,
                "sources": [],
                "used_documents": True
            }
        }


class PodcastMetadata(BaseModel):
    """Metadata for a generated podcast."""
    podcast_id: str
    query: str
    style: str
    voice: str
    format: str
    duration_target: int
    file_path: str
    file_size: Optional[int] = None
    created_at: str


class AvailableOptions(BaseModel):
    """Available podcast generation options."""
    voices: List[str] = Field(default_factory=lambda: SUPPORTED_VOICES)
    formats: List[str] = Field(default_factory=lambda: SUPPORTED_FORMATS)
    styles: List[str] = Field(default_factory=lambda: PODCAST_STYLES)


# Initialize agent config (reused across requests)
agent_config = AgentConfig(
    name="Podcast Generator",
    agent_type=AgentType.PODCAST,
    description="Generate educational podcasts from documents",
    system_prompt="You are an expert podcast script writer.",
    personality="Engaging and educational",
    temperature=0.7
)

# Initialize LLM provider
llm_provider = OpenAIProvider()


@router.post("/generate", response_model=PodcastResponse)
async def generate_podcast(request: PodcastGenerationRequest):
    """
    Generate a podcast from content.
    
    Creates an audio podcast from the specified topic, optionally using
    uploaded documents as source material.
    
    Steps:
    1. Gather content from documents and/or web
    2. Generate conversational script in specified style
    3. Create audio using OpenAI TTS
    4. Return script and audio file path
    """
    try:
        # Create podcast agent
        agent = PodcastAgent(agent_config, llm_provider)
        
        # Build context
        context = {
            "document_id": request.document_id,
            "chapter_id": request.chapter_id,
            "style": request.style,
            "voice": request.voice,
            "format": request.format,
            "duration_target": request.duration_target
        }
        
        # Generate podcast
        logger.info(f"Generating podcast: {request.query}")
        result = agent.process(request.query, context)
        
        # Extract metadata
        audio_file = result.metadata.get("audio_file")
        podcast_id = Path(audio_file).stem if audio_file else f"podcast_{request.query[:20]}"
        
        # Build audio URL
        audio_url = None
        if audio_file:
            filename = Path(audio_file).name
            audio_url = f"/v1/podcasts/download/{filename}"
        
        # Format sources
        sources = [
            PodcastSource(
                type=s["type"],
                title=s.get("title"),
                document_id=s.get("document_id"),
                page=s.get("page"),
                url=s.get("url")
            )
            for s in result.sources
        ]
        
        return PodcastResponse(
            podcast_id=podcast_id,
            query=request.query,
            script=result.content,
            audio_file=audio_file,
            audio_url=audio_url,
            style=request.style,
            voice=request.voice,
            format=request.format,
            duration_target=request.duration_target,
            sources=sources,
            used_documents=result.metadata.get("used_documents", False)
        )
        
    except Exception as e:
        logger.error(f"Podcast generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Podcast generation failed: {str(e)}")


@router.get("/download/{filename}")
async def download_podcast(filename: str):
    """
    Download a generated podcast audio file.
    
    Returns the audio file for playback or download.
    """
    try:
        # Construct file path
        file_path = Path("podcasts") / filename
        
        # Validate file exists
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Podcast not found")
        
        # Determine media type
        ext = file_path.suffix.lower()
        media_types = {
            ".mp3": "audio/mpeg",
            ".opus": "audio/opus",
            ".aac": "audio/aac",
            ".flac": "audio/flac"
        }
        media_type = media_types.get(ext, "audio/mpeg")
        
        return FileResponse(
            path=str(file_path),
            media_type=media_type,
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Podcast download failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")


@router.get("/list", response_model=List[PodcastMetadata])
async def list_podcasts():
    """
    List all generated podcasts.
    
    Returns metadata for all podcasts in the podcasts directory.
    """
    try:
        podcast_dir = Path("podcasts")
        
        if not podcast_dir.exists():
            return []
        
        podcasts = []
        for file_path in podcast_dir.glob("*"):
            if file_path.is_file() and file_path.suffix in [".mp3", ".opus", ".aac", ".flac"]:
                stat = file_path.stat()
                
                # Parse filename for metadata
                podcast_id = file_path.stem
                
                podcasts.append(
                    PodcastMetadata(
                        podcast_id=podcast_id,
                        query="[Unknown]",  # Could store this in metadata file
                        style="conversational",
                        voice="nova",
                        format=file_path.suffix[1:],
                        duration_target=5,
                        file_path=str(file_path),
                        file_size=stat.st_size,
                        created_at=str(stat.st_mtime)
                    )
                )
        
        return sorted(podcasts, key=lambda x: x.created_at, reverse=True)
        
    except Exception as e:
        logger.error(f"Failed to list podcasts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list podcasts: {str(e)}")


@router.delete("/{podcast_id}")
async def delete_podcast(podcast_id: str):
    """
    Delete a generated podcast.
    
    Removes the audio file from the server.
    """
    try:
        # Find matching file
        podcast_dir = Path("podcasts")
        
        deleted = False
        for file_path in podcast_dir.glob(f"{podcast_id}.*"):
            if file_path.is_file():
                file_path.unlink()
                deleted = True
                logger.info(f"Deleted podcast: {file_path}")
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Podcast not found")
        
        return {"status": "success", "message": f"Podcast {podcast_id} deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete podcast: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


@router.get("/options", response_model=AvailableOptions)
async def get_podcast_options():
    """
    Get available podcast generation options.
    
    Returns lists of supported voices, formats, and styles.
    """
    return AvailableOptions()


@router.get("/health")
async def podcast_health():
    """
    Check podcast service health.
    
    Verifies TTS availability and podcast directory.
    """
    # Check OpenAI availability
    tts_available = False
    try:
        from openai import OpenAI
        import os
        if os.getenv("OPENAI_API_KEY"):
            tts_available = True
    except ImportError:
        pass
    
    # Check podcast directory
    podcast_dir = Path("podcasts")
    podcast_dir_exists = podcast_dir.exists()
    
    # Check document search
    doc_search_available = False
    try:
        from src.documents import get_document_search_service
        doc_search_available = True
    except ImportError:
        pass
    
    status = "healthy" if tts_available else "degraded"
    
    return {
        "status": status,
        "tts_available": tts_available,
        "podcast_directory": str(podcast_dir),
        "podcast_directory_exists": podcast_dir_exists,
        "document_search_available": doc_search_available,
        "supported_voices": SUPPORTED_VOICES,
        "supported_formats": SUPPORTED_FORMATS,
        "supported_styles": PODCAST_STYLES
    }
