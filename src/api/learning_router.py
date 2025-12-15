# STUDENT ASSISTANT FEATURE - PHASE 8
"""
Learning Features API Router

Provides REST API endpoints for study guides, quizzes, notes, and progress tracking.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
import logging
from datetime import datetime

from src.agents.study_guide_agent import generate_study_guide
from src.agents.quiz_agent import generate_quiz
from src.notes import get_note_manager, Note
from src.progress import get_progress_tracker

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/learning", tags=["learning"])


# ============================================================================
# STUDY GUIDES
# ============================================================================

class StudyGuideRequest(BaseModel):
    """Request model for study guide generation."""
    topic: str = Field(..., description="Topic to create study guide for")
    document_id: Optional[str] = Field(None, description="Specific document to use")
    difficulty: Literal["beginner", "intermediate", "advanced"] = Field(
        "intermediate",
        description="Difficulty level"
    )
    include_questions: bool = Field(True, description="Include practice questions")


class StudyGuideResponse(BaseModel):
    """Response model for study guide."""
    content: str
    metadata: Dict[str, Any]
    sources: Optional[List[Dict[str, Any]]] = None


@router.post("/study-guides/generate", response_model=StudyGuideResponse)
async def create_study_guide(request: StudyGuideRequest):
    """
    Generate a study guide for a topic.
    
    Creates a comprehensive study guide with key concepts, explanations,
    and practice questions based on uploaded documents or general knowledge.
    """
    try:
        logger.info(f"Generating study guide: {request.topic}")
        
        result = generate_study_guide(
            topic=request.topic,
            document_id=request.document_id,
            difficulty=request.difficulty,
            include_questions=request.include_questions
        )
        
        return StudyGuideResponse(
            content=result["content"],
            metadata=result["metadata"],
            sources=result.get("sources")
        )
        
    except Exception as e:
        logger.error(f"Study guide generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# QUIZZES
# ============================================================================

class QuizRequest(BaseModel):
    """Request model for quiz generation."""
    topic: str = Field(..., description="Topic to create quiz for")
    num_questions: int = Field(5, ge=1, le=20, description="Number of questions")
    question_types: List[Literal["multiple_choice", "true_false", "short_answer"]] = Field(
        ["multiple_choice"],
        description="Types of questions to generate"
    )
    difficulty: Literal["beginner", "intermediate", "advanced"] = Field(
        "intermediate",
        description="Difficulty level"
    )
    document_id: Optional[str] = Field(None, description="Specific document to use")


class QuizResponse(BaseModel):
    """Response model for quiz."""
    quiz: Dict[str, Any]
    metadata: Dict[str, Any]
    sources: Optional[List[Dict[str, Any]]] = None


class QuizSubmission(BaseModel):
    """Request model for quiz submission."""
    quiz: Dict[str, Any]  # The entire quiz object with questions
    answers: List[Dict[str, Any]]  # List of {question_id, answer}
    time_taken: int  # Time in seconds


class QuizResultResponse(BaseModel):
    """Response model for quiz results."""
    score: float
    correct: int
    total: int
    details: List[Dict[str, Any]]


@router.post("/quizzes/generate", response_model=QuizResponse)
async def create_quiz(request: QuizRequest):
    """
    Generate a practice quiz for a topic.
    
    Creates multiple-choice, true/false, or short-answer questions
    based on uploaded documents or general knowledge.
    """
    try:
        logger.info(f"Generating quiz: {request.topic}")
        
        result = generate_quiz(
            topic=request.topic,
            num_questions=request.num_questions,
            question_types=request.question_types,
            difficulty=request.difficulty,
            document_id=request.document_id
        )
        
        return QuizResponse(
            quiz=result["quiz"],
            metadata=result["metadata"],
            sources=result.get("sources")
        )
        
    except Exception as e:
        logger.error(f"Quiz generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quizzes/submit", response_model=QuizResultResponse)
async def submit_quiz(submission: QuizSubmission):
    """
    Submit quiz answers and get results.
    
    Calculates score and records in progress tracking.
    """
    try:
        quiz = submission.quiz
        questions = quiz.get('questions', [])
        user_answers = {str(ans['question_id']): ans['answer'] for ans in submission.answers}
        
        # Grade each question
        correct_count = 0
        details = []
        
        for question in questions:
            q_id = str(question.get('id', question.get('question_id', '')))
            correct_answer = question.get('correct_answer', '')
            user_answer = user_answers.get(q_id, '')
            
            # Check if answer is correct
            is_correct = False
            if question.get('type') == 'multiple_choice':
                # For multiple choice, compare the letter (A, B, C, D)
                is_correct = user_answer.upper() == correct_answer.upper()
            elif question.get('type') == 'true_false':
                is_correct = user_answer.lower() == correct_answer.lower()
            else:
                # For short answer, do basic comparison (would need AI in production)
                is_correct = user_answer.lower().strip() in correct_answer.lower().strip()
            
            if is_correct:
                correct_count += 1
            
            details.append({
                'question_id': q_id,
                'question': question.get('question', ''),
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'is_correct': is_correct,
                'explanation': question.get('explanation', '')
            })
        
        total_questions = len(questions)
        score = correct_count
        
        # Record in progress tracker
        tracker = get_progress_tracker()
        tracker.record_quiz_result(
            quiz_id=quiz.get('id', 'quiz_' + str(datetime.now().timestamp())),
            topic=quiz.get('topic', submission.quiz.get('metadata', {}).get('topic', 'Unknown')),
            correct=correct_count,
            total=total_questions,
            time_spent=submission.time_taken
        )
        
        return QuizResultResponse(
            score=score,
            correct=correct_count,
            total=total_questions,
            details=details
        )
        
    except Exception as e:
        logger.error(f"Quiz submission failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# NOTES
# ============================================================================

class NoteCreate(BaseModel):
    """Request model for note creation."""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    tags: Optional[List[str]] = Field(default_factory=list)
    document_id: Optional[str] = None
    podcast_id: Optional[str] = None
    color: str = Field("#667eea", pattern="^#[0-9A-Fa-f]{6}$")


class NoteUpdate(BaseModel):
    """Request model for note update."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    tags: Optional[List[str]] = None
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    pinned: Optional[bool] = None


class NoteResponse(BaseModel):
    """Response model for note."""
    note_id: str
    title: str
    content: str
    tags: List[str]
    created_at: str
    updated_at: str
    document_id: Optional[str]
    podcast_id: Optional[str]
    color: str
    pinned: bool


@router.post("/notes", response_model=NoteResponse)
async def create_note(note: NoteCreate):
    """Create a new note."""
    try:
        manager = get_note_manager()
        created_note = manager.create_note(
            title=note.title,
            content=note.content,
            tags=note.tags or [],
            document_id=note.document_id,
            podcast_id=note.podcast_id,
            color=note.color
        )
        
        # Record in progress
        tracker = get_progress_tracker()
        tracker.record_note_created()
        
        return NoteResponse(**created_note.to_dict())
        
    except Exception as e:
        logger.error(f"Note creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/notes", response_model=List[NoteResponse])
async def list_notes(
    tag: Optional[str] = Query(None),
    document_id: Optional[str] = Query(None),
    podcast_id: Optional[str] = Query(None),
    pinned_only: bool = Query(False)
):
    """List notes with optional filters."""
    try:
        manager = get_note_manager()
        notes = manager.list_notes(
            tag=tag,
            document_id=document_id,
            podcast_id=podcast_id,
            pinned_only=pinned_only
        )
        
        return [NoteResponse(**note.to_dict()) for note in notes]
        
    except Exception as e:
        logger.error(f"Failed to list notes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/notes/{note_id}", response_model=NoteResponse)
async def get_note(note_id: str):
    """Get a specific note by ID."""
    try:
        manager = get_note_manager()
        note = manager.get_note(note_id)
        
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        return NoteResponse(**note.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get note: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/notes/{note_id}", response_model=NoteResponse)
async def update_note(note_id: str, update: NoteUpdate):
    """Update an existing note."""
    try:
        manager = get_note_manager()
        updated_note = manager.update_note(
            note_id=note_id,
            title=update.title,
            content=update.content,
            tags=update.tags,
            color=update.color,
            pinned=update.pinned
        )
        
        return NoteResponse(**updated_note.to_dict())
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Note update failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/notes/{note_id}")
async def delete_note(note_id: str):
    """Delete a note."""
    try:
        manager = get_note_manager()
        deleted = manager.delete_note(note_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Note not found")
        
        return {"message": "Note deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Note deletion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/notes/search/{query}", response_model=List[NoteResponse])
async def search_notes(query: str):
    """Search notes by content or title."""
    try:
        manager = get_note_manager()
        notes = manager.search_notes(query)
        
        return [NoteResponse(**note.to_dict()) for note in notes]
        
    except Exception as e:
        logger.error(f"Note search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/notes/tags/all", response_model=List[str])
async def get_all_tags():
    """Get all unique tags across all notes."""
    try:
        manager = get_note_manager()
        return manager.get_all_tags()
        
    except Exception as e:
        logger.error(f"Failed to get tags: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PROGRESS TRACKING
# ============================================================================

class ProgressSummary(BaseModel):
    """Response model for progress summary."""
    documents: Dict[str, Any]
    quizzes: Dict[str, Any]
    study_time: Dict[str, Any]
    podcasts: Dict[str, Any]
    notes: Dict[str, Any]
    streaks: Dict[str, Any]
    achievements: Dict[str, Any]


class AchievementResponse(BaseModel):
    """Response model for achievement."""
    achievement_id: str
    title: str
    description: str
    icon: str
    earned_at: str
    category: str


@router.get("/progress/summary", response_model=ProgressSummary)
async def get_progress_summary():
    """Get a summary of student progress."""
    try:
        tracker = get_progress_tracker()
        summary = tracker.get_progress_summary()
        
        return ProgressSummary(**summary)
        
    except Exception as e:
        logger.error(f"Failed to get progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/progress/achievements", response_model=List[AchievementResponse])
async def get_achievements():
    """Get all earned achievements."""
    try:
        tracker = get_progress_tracker()
        achievements = tracker.progress.achievements
        
        return [
            AchievementResponse(
                achievement_id=a.achievement_id,
                title=a.title,
                description=a.description,
                icon=a.icon,
                earned_at=a.earned_at,
                category=a.category
            )
            for a in sorted(achievements, key=lambda x: x.earned_at, reverse=True)
        ]
        
    except Exception as e:
        logger.error(f"Failed to get achievements: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/progress/study-session/start")
async def start_study_session(
    activity_type: str = Query(..., description="Type of activity"),
    topic: Optional[str] = Query(None, description="Topic being studied")
):
    """Start a new study session."""
    try:
        tracker = get_progress_tracker()
        session_id = tracker.start_study_session(activity_type, topic)
        
        return {"session_id": session_id, "message": "Study session started"}
        
    except Exception as e:
        logger.error(f"Failed to start session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/progress/study-session/end/{session_id}")
async def end_study_session(session_id: str):
    """End a study session."""
    try:
        tracker = get_progress_tracker()
        tracker.end_study_session(session_id)
        
        return {"message": "Study session ended"}
        
    except Exception as e:
        logger.error(f"Failed to end session: {e}")
        raise HTTPException(status_code=500, detail=str(e))
