# STUDENT ASSISTANT FEATURE - PHASE 5
"""
Podcast Agent Implementation

Generates educational podcasts from documents using OpenAI TTS.
Converts chapters, summaries, or custom content into conversational audio.
"""

from typing import Dict, Any, Optional, List, Literal
import os
import tempfile
from pathlib import Path
from datetime import datetime
import logging

from src.agents.base_agent import BaseAgent, AgentResponse
from src.providers.base import LLMMessage

# Try to import document search (optional)
try:
    from src.documents import get_document_search_service
    DOCUMENT_SEARCH_AVAILABLE = True
except ImportError:
    DOCUMENT_SEARCH_AVAILABLE = False

# OpenAI client for TTS
try:
    from openai import OpenAI
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False


logger = logging.getLogger(__name__)


# Supported voices and formats
SUPPORTED_VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
SUPPORTED_FORMATS = ["mp3", "opus", "aac", "flac"]
PODCAST_STYLES = ["conversational", "lecture", "summary", "storytelling"]


class PodcastAgent(BaseAgent):
    """
    Podcast Agent that generates audio content from documents and text.
    
    Features:
    - Generates conversational scripts from document content
    - Creates audio using OpenAI TTS
    - Supports multiple voices and styles
    - Can generate podcasts from chapters or custom queries
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize the Podcast Agent."""
        super().__init__(*args, **kwargs)
        
        # Initialize OpenAI client for TTS
        if TTS_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)
            else:
                logger.warning("OpenAI API key not found - TTS unavailable")
                self.openai_client = None
        else:
            logger.warning("OpenAI library not available - TTS unavailable")
            self.openai_client = None
    
    def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Generate a podcast from content.
        
        Args:
            query: Podcast topic or chapter to convert
            context: Optional context with settings:
                - document_id: Specific document to use
                - chapter_id: Specific chapter to use
                - style: Podcast style (conversational, lecture, summary, storytelling)
                - voice: TTS voice to use
                - format: Audio format (mp3, opus, aac, flac)
                - duration_target: Target duration in minutes
                
        Returns:
            AgentResponse with podcast script and audio file path
        """
        # Extract context parameters
        context = context or {}
        document_id = context.get("document_id")
        chapter_id = context.get("chapter_id")
        style = context.get("style", "conversational")
        voice = context.get("voice", "nova")
        audio_format = context.get("format", "mp3")
        duration_target = context.get("duration_target", 5)  # minutes
        
        # Validate parameters
        if style not in PODCAST_STYLES:
            style = "conversational"
        if voice not in SUPPORTED_VOICES:
            voice = "nova"
        if audio_format not in SUPPORTED_FORMATS:
            audio_format = "mp3"
        
        # Step 1: Gather content for podcast
        content = self._gather_podcast_content(query, document_id, chapter_id)
        
        # Step 2: Generate podcast script
        script = self._generate_podcast_script(
            query=query,
            content=content,
            style=style,
            duration_target=duration_target
        )
        
        # Step 3: Generate audio from script
        audio_file = self._generate_audio(
            script=script,
            voice=voice,
            format=audio_format
        )
        
        # Step 4: Build response
        return AgentResponse(
            agent_name=self.config.name,
            agent_type=self.config.agent_type,
            content=script,
            sources=content.get("sources", []),
            tokens_used=content.get("tokens_used", 0),
            metadata={
                "podcast_query": query,
                "style": style,
                "voice": voice,
                "format": audio_format,
                "audio_file": audio_file,
                "duration_target": duration_target,
                "used_documents": content.get("used_documents", False),
                "document_id": document_id,
                "chapter_id": chapter_id
            }
        )
    
    def _gather_podcast_content(
        self,
        query: str,
        document_id: Optional[str] = None,
        chapter_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Gather content for the podcast from documents and/or web.
        
        Args:
            query: Podcast topic
            document_id: Optional specific document
            chapter_id: Optional specific chapter
            
        Returns:
            Dictionary with content, sources, and metadata
        """
        content_parts = []
        sources = []
        used_documents = False
        
        # Try to get content from documents
        if DOCUMENT_SEARCH_AVAILABLE and document_id:
            try:
                doc_service = get_document_search_service()
                
                # Search specific document or all documents
                doc_results = doc_service.search(
                    query=query,
                    max_results=10,
                    document_ids=[document_id] if document_id else None
                )
                
                if doc_results:
                    used_documents = True
                    content_parts.append("=== Content from Uploaded Documents ===\n")
                    
                    for result in doc_results:
                        content_parts.append(f"\n[{result.document_title}]")
                        if result.page_number:
                            content_parts.append(f" - Page {result.page_number}")
                        content_parts.append(f"\n{result.content}\n")
                        
                        sources.append({
                            "type": "document",
                            "title": result.document_title,
                            "document_id": result.document_id,
                            "page": result.page_number
                        })
                
            except Exception as e:
                logger.warning(f"Document search failed: {e}")
        
        # Get supplementary web content if needed
        if not content_parts or len(content_parts) < 3:
            try:
                search_result = self._search(query)
                
                content_parts.append("\n=== Additional Context from Web ===\n")
                content_parts.append(search_result.text)
                
                for source in search_result.sources[:5]:
                    sources.append({
                        "type": "web",
                        "url": source.url,
                        "title": source.url.split('/')[2] if source.url else "Web Source"
                    })
                    
            except Exception as e:
                logger.warning(f"Web search failed: {e}")
        
        return {
            "content": "\n".join(content_parts),
            "sources": sources,
            "used_documents": used_documents,
            "tokens_used": 0
        }
    
    def _generate_podcast_script(
        self,
        query: str,
        content: Dict[str, Any],
        style: str,
        duration_target: int
    ) -> str:
        """
        Generate a conversational podcast script from content.
        
        Args:
            query: Podcast topic
            content: Content dictionary with text and sources
            style: Podcast style
            duration_target: Target duration in minutes
            
        Returns:
            Podcast script text
        """
        # Calculate approximate word count target
        # Average speaking rate: 150 words per minute
        word_target = duration_target * 150
        
        # Build style-specific prompt
        style_prompts = {
            "conversational": """Create a friendly, engaging podcast script as if explaining to a friend.
Use natural language, occasional questions, and relatable examples.""",
            
            "lecture": """Create an educational lecture-style script with clear structure:
introduction, main points, examples, and conclusion. Formal but accessible.""",
            
            "summary": """Create a concise summary script hitting the key points.
Brief, clear, and well-organized. Perfect for quick review.""",
            
            "storytelling": """Create an engaging narrative that tells a story.
Use vivid descriptions, build interest, and make it memorable."""
        }
        
        style_prompt = style_prompts.get(style, style_prompts["conversational"])
        
        # Generate script using LLM
        messages = [
            self._build_system_message(),
            LLMMessage(
                role="user",
                content=f"""Generate a podcast script about: {query}

Style: {style}
Target Duration: {duration_target} minutes (~{word_target} words)

Source Content:
{content['content']}

Instructions:
{style_prompt}

Format:
- Write as spoken word (not an article)
- Include natural pauses and transitions
- Make it engaging and easy to follow
- Target approximately {word_target} words
- Add [PAUSE] markers where natural breaks occur
- Don't include speaker labels or stage directions

Create the podcast script now:"""
            )
        ]
        
        llm_response = self._generate_llm_response(messages)
        
        return llm_response.text
    
    def _generate_audio(
        self,
        script: str,
        voice: str,
        format: str
    ) -> Optional[str]:
        """
        Generate audio file from script using OpenAI TTS.
        
        Args:
            script: Podcast script text
            voice: Voice to use
            format: Audio format
            
        Returns:
            Path to generated audio file, or None if failed
        """
        if not self.openai_client or not TTS_AVAILABLE:
            logger.warning("TTS not available - skipping audio generation")
            return None
        
        try:
            # Clean script for TTS (remove pause markers)
            clean_script = script.replace("[PAUSE]", ". ")
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"podcast_{timestamp}.{format}"
            
            # Create podcasts directory if it doesn't exist
            podcast_dir = Path("podcasts")
            podcast_dir.mkdir(exist_ok=True)
            
            output_path = podcast_dir / filename
            
            # Generate audio using OpenAI TTS
            logger.info(f"Generating audio: {output_path}")
            
            response = self.openai_client.audio.speech.create(
                model="tts-1",  # or "tts-1-hd" for higher quality
                voice=voice,
                input=clean_script,
                response_format=format
            )
            
            # Stream to file
            response.stream_to_file(str(output_path))
            
            logger.info(f"Audio generated successfully: {output_path}")
            
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Audio generation failed: {e}")
            return None
    
    def _build_system_message(self) -> LLMMessage:
        """Build system message for podcast generation."""
        return LLMMessage(
            role="system",
            content="""You are an expert podcast script writer and educator.

Your role is to:
1. Transform educational content into engaging podcast scripts
2. Write in natural, spoken language (not written article style)
3. Make complex topics accessible and interesting
4. Use conversational tone while maintaining accuracy
5. Include natural transitions and pacing
6. Consider the listening experience (not reading)

Remember:
- Podcasts are heard, not read - write accordingly
- Use shorter sentences than written content
- Include rhetorical questions to engage listeners
- Add emphasis and variation in pacing
- Make it enjoyable to listen to while being informative

You excel at making learning enjoyable through audio!"""
        )


def generate_podcast(
    query: str,
    document_id: Optional[str] = None,
    chapter_id: Optional[str] = None,
    style: str = "conversational",
    voice: str = "nova",
    format: str = "mp3",
    duration_target: int = 5
) -> Dict[str, Any]:
    """
    Quick helper function to generate a podcast.
    
    Args:
        query: Podcast topic
        document_id: Optional document ID
        chapter_id: Optional chapter ID
        style: Podcast style
        voice: TTS voice
        format: Audio format
        duration_target: Target duration in minutes
        
    Returns:
        Dictionary with script and audio file path
    """
    from src.agents import AgentConfig, AgentType
    
    config = AgentConfig(
        name="Podcast Generator",
        agent_type=AgentType.PODCAST,
        description="Generate educational podcasts",
        system_prompt="You are an expert podcast script writer.",
        personality="Engaging and educational"
    )
    
    agent = PodcastAgent(config)
    
    context = {
        "document_id": document_id,
        "chapter_id": chapter_id,
        "style": style,
        "voice": voice,
        "format": format,
        "duration_target": duration_target
    }
    
    result = agent.process(query, context)
    
    return {
        "script": result.content,
        "audio_file": result.metadata.get("audio_file"),
        "sources": result.sources,
        "metadata": result.metadata
    }
