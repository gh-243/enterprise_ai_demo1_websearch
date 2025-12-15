# STUDENT ASSISTANT FEATURE - PHASE 8
"""
Progress Tracking System Implementation

Tracks student learning progress including documents read, quizzes taken,
study time, and achievement milestones.
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class QuizResult:
    """Represents a quiz attempt result."""
    quiz_id: str
    topic: str
    score: float  # 0-100
    total_questions: int
    correct_answers: int
    completed_at: str
    time_spent_seconds: int


@dataclass
class StudySession:
    """Represents a study session."""
    session_id: str
    activity_type: str  # 'reading', 'quiz', 'notes', 'podcast'
    topic: Optional[str]
    duration_seconds: int
    started_at: str
    ended_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Achievement:
    """Represents a learning achievement/milestone."""
    achievement_id: str
    title: str
    description: str
    icon: str
    earned_at: str
    category: str  # 'documents', 'quizzes', 'study_time', 'streaks'


@dataclass
class StudentProgress:
    """Comprehensive student progress tracking."""
    student_id: str
    
    # Document progress
    documents_uploaded: int = 0
    documents_read: List[str] = field(default_factory=list)
    pages_read: int = 0
    
    # Quiz progress
    quizzes_taken: List[QuizResult] = field(default_factory=list)
    total_quiz_score: float = 0.0
    quiz_attempts: int = 0
    
    # Study time
    study_sessions: List[StudySession] = field(default_factory=list)
    total_study_time_seconds: int = 0
    
    # Podcasts
    podcasts_generated: int = 0
    podcasts_listened: List[str] = field(default_factory=list)
    
    # Notes
    notes_created: int = 0
    
    # Achievements
    achievements: List[Achievement] = field(default_factory=list)
    
    # Streaks
    current_streak_days: int = 0
    longest_streak_days: int = 0
    last_activity_date: Optional[str] = None
    
    # Timestamps
    created_at: str = ""
    updated_at: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class ProgressTracker:
    """
    Manages student progress tracking and analytics.
    
    Features:
    - Track documents read and pages covered
    - Record quiz attempts and scores
    - Monitor study time and sessions
    - Award achievements for milestones
    - Calculate learning streaks
    - Generate progress reports
    """
    
    def __init__(self, storage_path: str = "data/progress"):
        """
        Initialize progress tracker.
        
        Args:
            storage_path: Directory to store progress data
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.progress_file = self.storage_path / "progress.json"
        self._load_progress()
    
    def _load_progress(self):
        """Load progress from storage."""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    data = json.load(f)
                    # Convert lists back to dataclass instances
                    if 'quizzes_taken' in data:
                        data['quizzes_taken'] = [QuizResult(**q) for q in data['quizzes_taken']]
                    if 'study_sessions' in data:
                        data['study_sessions'] = [StudySession(**s) for s in data['study_sessions']]
                    if 'achievements' in data:
                        data['achievements'] = [Achievement(**a) for a in data['achievements']]
                    
                    self.progress = StudentProgress(**data)
                logger.info("Loaded progress data")
            except Exception as e:
                logger.error(f"Failed to load progress: {e}")
                self.progress = StudentProgress(student_id="default", created_at=datetime.now().isoformat())
        else:
            self.progress = StudentProgress(student_id="default", created_at=datetime.now().isoformat())
    
    def _save_progress(self):
        """Save progress to storage."""
        try:
            self.progress.updated_at = datetime.now().isoformat()
            data = self.progress.to_dict()
            
            with open(self.progress_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info("Saved progress data")
        except Exception as e:
            logger.error(f"Failed to save progress: {e}")
            raise
    
    def record_document_upload(self, document_id: str):
        """Record a document upload."""
        self.progress.documents_uploaded += 1
        self._check_achievements()
        self._save_progress()
    
    def record_document_read(self, document_id: str, pages: int = 1):
        """Record document reading progress."""
        if document_id not in self.progress.documents_read:
            self.progress.documents_read.append(document_id)
        self.progress.pages_read += pages
        self._update_streak()
        self._check_achievements()
        self._save_progress()
    
    def record_quiz_result(
        self,
        quiz_id: str,
        topic: str,
        correct: int,
        total: int,
        time_spent: int
    ) -> QuizResult:
        """
        Record a quiz attempt.
        
        Args:
            quiz_id: Unique quiz identifier
            topic: Quiz topic
            correct: Number of correct answers
            total: Total number of questions
            time_spent: Time spent in seconds
            
        Returns:
            QuizResult object
        """
        score = (correct / total) * 100 if total > 0 else 0
        
        result = QuizResult(
            quiz_id=quiz_id,
            topic=topic,
            score=score,
            total_questions=total,
            correct_answers=correct,
            completed_at=datetime.now().isoformat(),
            time_spent_seconds=time_spent
        )
        
        self.progress.quizzes_taken.append(result)
        self.progress.quiz_attempts += 1
        self.progress.total_quiz_score += score
        
        self._update_streak()
        self._check_achievements()
        self._save_progress()
        
        return result
    
    def start_study_session(
        self,
        activity_type: str,
        topic: Optional[str] = None
    ) -> str:
        """
        Start a new study session.
        
        Args:
            activity_type: Type of activity (reading, quiz, notes, podcast)
            topic: Optional topic being studied
            
        Returns:
            Session ID
        """
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        session = StudySession(
            session_id=session_id,
            activity_type=activity_type,
            topic=topic,
            duration_seconds=0,
            started_at=datetime.now().isoformat(),
            ended_at=""
        )
        
        self.progress.study_sessions.append(session)
        self._save_progress()
        
        return session_id
    
    def end_study_session(self, session_id: str):
        """End a study session and calculate duration."""
        for session in self.progress.study_sessions:
            if session.session_id == session_id and not session.ended_at:
                session.ended_at = datetime.now().isoformat()
                
                # Calculate duration
                started = datetime.fromisoformat(session.started_at)
                ended = datetime.fromisoformat(session.ended_at)
                session.duration_seconds = int((ended - started).total_seconds())
                
                self.progress.total_study_time_seconds += session.duration_seconds
                
                self._update_streak()
                self._check_achievements()
                self._save_progress()
                break
    
    def record_podcast_generated(self, podcast_id: str):
        """Record a podcast generation."""
        self.progress.podcasts_generated += 1
        self._check_achievements()
        self._save_progress()
    
    def record_podcast_listened(self, podcast_id: str):
        """Record podcast listening."""
        if podcast_id not in self.progress.podcasts_listened:
            self.progress.podcasts_listened.append(podcast_id)
        self._update_streak()
        self._check_achievements()
        self._save_progress()
    
    def record_note_created(self):
        """Record a note creation."""
        self.progress.notes_created += 1
        self._check_achievements()
        self._save_progress()
    
    def _update_streak(self):
        """Update learning streak."""
        today = datetime.now().date().isoformat()
        
        if self.progress.last_activity_date:
            last_date = datetime.fromisoformat(self.progress.last_activity_date).date()
            today_date = datetime.now().date()
            
            if last_date == today_date:
                # Same day, no change
                return
            elif last_date == today_date - timedelta(days=1):
                # Consecutive day
                self.progress.current_streak_days += 1
            else:
                # Streak broken
                self.progress.current_streak_days = 1
        else:
            # First activity
            self.progress.current_streak_days = 1
        
        # Update longest streak
        if self.progress.current_streak_days > self.progress.longest_streak_days:
            self.progress.longest_streak_days = self.progress.current_streak_days
        
        self.progress.last_activity_date = today
    
    def _check_achievements(self):
        """Check and award new achievements."""
        earned_ids = {a.achievement_id for a in self.progress.achievements}
        
        # Define achievements
        potential_achievements = [
            ("first_doc", "First Document", "Uploaded your first document", "📄", "documents", 
             self.progress.documents_uploaded >= 1),
            ("doc_master", "Document Master", "Uploaded 10 documents", "📚", "documents",
             self.progress.documents_uploaded >= 10),
            ("first_quiz", "Quiz Novice", "Completed your first quiz", "📝", "quizzes",
             self.progress.quiz_attempts >= 1),
            ("quiz_master", "Quiz Master", "Completed 10 quizzes", "🎓", "quizzes",
             self.progress.quiz_attempts >= 10),
            ("perfect_score", "Perfect Score", "Got 100% on a quiz", "⭐", "quizzes",
             any(q.score == 100 for q in self.progress.quizzes_taken)),
            ("study_hour", "Dedicated Learner", "Studied for 1 hour", "⏰", "study_time",
             self.progress.total_study_time_seconds >= 3600),
            ("study_marathon", "Study Marathon", "Studied for 10 hours total", "🏃", "study_time",
             self.progress.total_study_time_seconds >= 36000),
            ("week_streak", "Week Warrior", "7-day learning streak", "🔥", "streaks",
             self.progress.current_streak_days >= 7),
            ("month_streak", "Consistency King", "30-day learning streak", "👑", "streaks",
             self.progress.current_streak_days >= 30),
            ("first_podcast", "Podcast Pioneer", "Generated your first podcast", "🎙️", "podcasts",
             self.progress.podcasts_generated >= 1),
            ("note_taker", "Note Taker", "Created 10 notes", "📔", "notes",
             self.progress.notes_created >= 10),
        ]
        
        for achievement_id, title, description, icon, category, condition in potential_achievements:
            if condition and achievement_id not in earned_ids:
                achievement = Achievement(
                    achievement_id=achievement_id,
                    title=title,
                    description=description,
                    icon=icon,
                    earned_at=datetime.now().isoformat(),
                    category=category
                )
                self.progress.achievements.append(achievement)
                logger.info(f"Achievement earned: {title}")
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Get a summary of student progress."""
        avg_quiz_score = (
            self.progress.total_quiz_score / self.progress.quiz_attempts
            if self.progress.quiz_attempts > 0 else 0
        )
        
        study_hours = self.progress.total_study_time_seconds / 3600
        
        return {
            "documents": {
                "uploaded": self.progress.documents_uploaded,
                "read": len(self.progress.documents_read),
                "pages_read": self.progress.pages_read
            },
            "quizzes": {
                "attempts": self.progress.quiz_attempts,
                "average_score": round(avg_quiz_score, 1),
                "perfect_scores": sum(1 for q in self.progress.quizzes_taken if q.score == 100)
            },
            "study_time": {
                "total_hours": round(study_hours, 1),
                "sessions": len(self.progress.study_sessions)
            },
            "podcasts": {
                "generated": self.progress.podcasts_generated,
                "listened": len(self.progress.podcasts_listened)
            },
            "notes": {
                "created": self.progress.notes_created
            },
            "streaks": {
                "current": self.progress.current_streak_days,
                "longest": self.progress.longest_streak_days
            },
            "achievements": {
                "earned": len(self.progress.achievements),
                "recent": [a.title for a in sorted(self.progress.achievements, key=lambda x: x.earned_at, reverse=True)[:3]]
            }
        }


# Global progress tracker instance
_progress_tracker = None


def get_progress_tracker() -> ProgressTracker:
    """Get the global progress tracker instance."""
    global _progress_tracker
    if _progress_tracker is None:
        _progress_tracker = ProgressTracker()
    return _progress_tracker
