# STUDENT ASSISTANT FEATURE - PHASE 8
"""
Quiz Agent Implementation

Generates practice quizzes from documents and topics.
Creates multiple-choice, tru        # Step 3: Generate quiz
        messages = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=user_prompt)
        ]
        
        try:
            response = self.provider.chat_completion(
                messages=messages,
                temperature=0.7,  # Some creativity for question variety
                max_tokens=2500
            ) short-answer questions with explanations.
"""

from typing import Dict, Any, Optional, List, Literal
import logging
import json
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


class QuizAgent(BaseAgent):
    """
    Quiz Agent that generates practice questions from content.
    
    Features:
    - Generates multiple-choice questions
    - Creates true/false questions
    - Generates short-answer questions
    - Provides correct answers and explanations
    - Adjusts difficulty level
    - Tags questions by topic
    """
    
    def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Generate a quiz for the given topic.
        
        Args:
            query: Topic or content to create quiz from
            context: Optional context with num_questions, question_types, difficulty
            
        Returns:
            AgentResponse with quiz questions in JSON format
        """
        context = context or {}
        
        logger.info(f"Generating quiz for: {query}")
        
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
        
        # Step 2: Build quiz generation prompt
        num_questions = context.get("num_questions", 5)
        question_types = context.get("question_types", ["multiple_choice", "true_false"])
        difficulty = context.get("difficulty", "intermediate")
        
        system_prompt = """You are an expert educational assessment creator.

Your task is to create high-quality quiz questions that effectively test student understanding.

Guidelines:
- Questions should be clear and unambiguous
- Correct answers must be definitively correct
- Distractors (wrong answers) should be plausible but clearly incorrect
- Explanations should teach, not just confirm correctness
- Questions should test understanding, not just memorization
- Vary difficulty and cognitive levels

Return ONLY valid JSON in this exact format:
{
  "questions": [
    {
      "id": 1,
      "type": "multiple_choice",
      "question": "Question text here?",
      "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
      "correct_answer": "B",
      "explanation": "Explanation of why B is correct and others are wrong",
      "difficulty": "intermediate",
      "topic": "Specific topic"
    }
  ]
}"""

        # Build the prompt
        user_prompt = f"""Create a quiz with {num_questions} questions about: {query}

Question Types: {', '.join(question_types)}
Difficulty Level: {difficulty}"""

        if document_context:
            user_prompt += f"\n\nBased on this content:\n{document_context}"
        else:
            user_prompt += "\n\nGenerate questions based on general knowledge of this topic."
        
        user_prompt += f"""

Create {num_questions} questions total.

For multiple_choice questions:
- Provide 4 options (A, B, C, D)
- One correct answer
- Include clear explanation

For true_false questions:
- Clear statement that is definitively true or false
- Include explanation

For short_answer questions:
- Question requiring 1-3 sentence answer
- Provide model answer
- Key points that should be included

Return ONLY valid JSON. No additional text before or after."""

        # Step 3: Generate quiz
        messages = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=user_prompt)
        ]
        
        try:
            response = self.provider.generate(
                messages=messages,
                temperature=0.7,  # Some creativity for question variety
                max_tokens=2500
            )
            
            quiz_content = response.text.strip()
            
            # Try to parse JSON
            try:
                # Remove markdown code blocks if present
                if quiz_content.startswith("```"):
                    quiz_content = quiz_content.split("```")[1]
                    if quiz_content.startswith("json"):
                        quiz_content = quiz_content[4:]
                
                quiz_data = json.loads(quiz_content)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse quiz JSON: {e}")
                # Return formatted text instead
                quiz_data = {
                    "questions": [],
                    "raw_content": quiz_content
                }
            
            # Step 4: Extract metadata
            metadata = {
                "topic": query,
                "num_questions": num_questions,
                "question_types": question_types,
                "difficulty": difficulty,
                "generated_at": datetime.now().isoformat(),
                "used_documents": len(sources) > 0,
                "source_count": len(sources),
                "quiz_data": quiz_data
            }
            
            # Format response
            formatted_content = json.dumps(quiz_data, indent=2)
            
            return AgentResponse(
                agent_name=self.config.name,
                agent_type=self.config.agent_type,
                content=formatted_content,
                sources=sources if sources else None,
                metadata=metadata,
                tokens_used=response.tokens_in + response.tokens_out,
                cost_usd=0.0  # Calculate based on model pricing if needed
            )
            
        except Exception as e:
            logger.error(f"Quiz generation failed: {e}")
            raise Exception(f"Failed to generate quiz: {str(e)}")


def generate_quiz(
    topic: str,
    num_questions: int = 5,
    question_types: Optional[List[str]] = None,
    difficulty: str = "intermediate",
    document_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to generate a quiz.
    
    Args:
        topic: Topic to create quiz for
        num_questions: Number of questions to generate
        question_types: Types of questions (multiple_choice, true_false, short_answer)
        difficulty: Difficulty level (beginner, intermediate, advanced)
        document_id: Optional specific document to use
        
    Returns:
        Dictionary with quiz questions and metadata
    """
    from src.agents import AgentConfig, AgentType
    from src.providers.openai_provider import OpenAIProvider
    
    if question_types is None:
        question_types = ["multiple_choice", "true_false"]
    
    # Initialize agent
    config = AgentConfig(
        name="Quiz Generator",
        agent_type=AgentType.RESEARCH,  # Reuse RESEARCH type
        description="Generate practice quizzes",
        system_prompt="You are an expert educational assessment creator.",
        personality="Precise, pedagogical, and fair",
        temperature=0.7,
        max_tokens=2500
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
    
    agent = QuizAgent(config, llm_provider, search_service)
    
    # Generate quiz
    context = {
        "num_questions": num_questions,
        "question_types": question_types,
        "difficulty": difficulty,
        "document_id": document_id
    }
    
    result = agent.process(topic, context)
    
    return {
        "quiz": result.metadata.get("quiz_data"),
        "metadata": {k: v for k, v in result.metadata.items() if k != "quiz_data"},
        "sources": result.sources,
        "tokens_used": result.tokens_used,
        "cost_usd": result.cost_usd
    }
