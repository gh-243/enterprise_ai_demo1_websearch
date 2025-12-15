# STUDENT ASSISTANT FEATURE - PHASE 8
"""
Study Guide Agent Implementation

Generates structured study guides from documents and topics.
Creates comprehensive learning materials with key concepts, summaries, and practice questions.
"""

from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

from src.agents.base_agent import BaseAgent, AgentResponse
from src.providers.base import LLMMessage

# Try to import document search (optional)
try:
    from src.documents import get_document_search_service
    DOCUMENT_SEARCH_AVAILABLE = True
except ImportError:
    DOCUMENT_SEARCH_AVAILABLE = False


logger = logging.getLogger(__name__)


class StudyGuideAgent(BaseAgent):
    """
    Study Guide Agent that generates comprehensive learning materials.
    
    Features:
    - Generates structured study guides from documents
    - Identifies key concepts and learning objectives
    - Creates summaries and detailed explanations
    - Suggests practice activities
    - Organizes content hierarchically
    """
    
    def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Generate a study guide for the given topic.
        
        Args:
            query: Topic or document to create study guide for
            context: Optional context with document_id, chapter_id, difficulty level
            
        Returns:
            AgentResponse with structured study guide
        """
        context = context or {}
        
        logger.info(f"Generating study guide for: {query}")
        
        # Step 1: Gather content from documents
        document_context = ""
        sources = []
        
        if DOCUMENT_SEARCH_AVAILABLE and self.search_service:
            try:
                doc_service = get_document_search_service()
                
                # Search for relevant content
                search_results = doc_service.search(
                    query=query,
                    top_k=5,
                    document_id=context.get("document_id")
                )
                
                if search_results:
                    document_context = "\n\n".join([
                        f"Source {i+1}: {result.content}"
                        for i, result in enumerate(search_results)
                    ])
                    
                    sources = [{
                        "type": "document",
                        "document_id": result.metadata.get("document_id"),
                        "page": result.metadata.get("page_number"),
                        "relevance": result.score
                    } for result in search_results]
                    
                    logger.info(f"Found {len(search_results)} relevant document sections")
            except Exception as e:
                logger.warning(f"Document search failed: {e}")
        
        # Step 2: Build study guide generation prompt
        difficulty = context.get("difficulty", "intermediate")
        include_questions = context.get("include_questions", True)
        
        system_prompt = """You are an expert educational content creator specializing in study guides.

Your task is to create comprehensive, well-structured study guides that help students master topics effectively.

Study guides should include:
1. **Learning Objectives** - What students will be able to do after studying
2. **Key Concepts** - Core ideas and terminology with clear definitions
3. **Detailed Explanations** - In-depth coverage of main topics
4. **Examples** - Concrete examples to illustrate concepts
5. **Summary** - Concise recap of main points
6. **Practice Questions** - Questions to test understanding (if requested)
7. **Further Reading** - Suggestions for deeper exploration

Format your response in clear markdown with proper headers and bullet points."""

        # Build the prompt
        user_prompt = f"""Create a comprehensive study guide for: {query}

Difficulty Level: {difficulty}
Include Practice Questions: {'Yes' if include_questions else 'No'}"""

        if document_context:
            user_prompt += f"\n\nRelevant Source Material:\n{document_context}"
        else:
            user_prompt += "\n\nNote: Generate study guide based on general knowledge of this topic."
        
        user_prompt += """

Please structure the study guide with:
- Clear section headers
- Bullet points for key concepts
- Numbered steps for processes
- Examples in code blocks or quotes where appropriate
- Practice questions at the end (if requested)

Make it engaging and student-friendly!"""

        # Step 3: Generate study guide
        messages = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=user_prompt)
        ]
        
        try:
            response = self.provider.generate(
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            
            study_guide_content = response.text
            
            # Step 4: Extract metadata
            metadata = {
                "topic": query,
                "difficulty": difficulty,
                "includes_questions": include_questions,
                "generated_at": datetime.now().isoformat(),
                "word_count": len(study_guide_content.split()),
                "used_documents": len(sources) > 0,
                "source_count": len(sources)
            }
            
            return AgentResponse(
                agent_name=self.config.name,
                agent_type=self.config.agent_type,
                content=study_guide_content,
                sources=sources if sources else None,
                metadata=metadata,
                tokens_used=response.tokens_in + response.tokens_out,
                cost_usd=0.0  # Calculate based on model pricing if needed
            )
            
        except Exception as e:
            logger.error(f"Study guide generation failed: {e}")
            raise Exception(f"Failed to generate study guide: {str(e)}")


def generate_study_guide(
    topic: str,
    document_id: Optional[str] = None,
    difficulty: str = "intermediate",
    include_questions: bool = True
) -> Dict[str, Any]:
    """
    Convenience function to generate a study guide.
    
    Args:
        topic: Topic to create study guide for
        document_id: Optional specific document to use
        difficulty: Difficulty level (beginner, intermediate, advanced)
        include_questions: Whether to include practice questions
        
    Returns:
        Dictionary with study guide content and metadata
    """
    from src.agents import AgentConfig, AgentType
    from src.providers.openai_provider import OpenAIProvider
    
    # Initialize agent
    config = AgentConfig(
        name="Study Guide Generator",
        agent_type=AgentType.RESEARCH,  # Reuse RESEARCH type
        description="Generate comprehensive study guides",
        system_prompt="You are an expert educational content creator.",
        personality="Clear, structured, and pedagogical",
        temperature=0.7,
        max_tokens=3000
    )
    
    llm_provider = OpenAIProvider()
    
    # Get document search service if available
    search_service = None
    if DOCUMENT_SEARCH_AVAILABLE:
        try:
            from src.search_service import SearchService
            search_service = SearchService()
        except:
            pass
    
    agent = StudyGuideAgent(config, llm_provider, search_service)
    
    # Generate study guide
    context = {
        "document_id": document_id,
        "difficulty": difficulty,
        "include_questions": include_questions
    }
    
    result = agent.process(topic, context)
    
    return {
        "content": result.content,
        "metadata": result.metadata,
        "sources": result.sources,
        "tokens_used": result.tokens_used,
        "cost_usd": result.cost_usd
    }
