"""
Comprehensive tests for Phase 8 Learning Features

Tests study guides, quizzes, notes, and progress tracking.
"""

import pytest
import json
import time
from datetime import datetime
from fastapi.testclient import TestClient
from src.app.app import app

client = TestClient(app)


# ============================================================================
# STUDY GUIDE TESTS
# ============================================================================

class TestStudyGuides:
    """Test study guide generation"""
    
    def test_generate_study_guide_success(self):
        """Test successful study guide generation"""
        response = client.post(
            "/v1/learning/study-guides/generate",
            json={
                "topic": "Python Functions",
                "difficulty": "intermediate",
                "include_questions": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "content" in data
        assert "metadata" in data
        assert isinstance(data["content"], str)
        assert len(data["content"]) > 100  # Should have substantial content
        
        # Verify metadata
        metadata = data["metadata"]
        assert metadata["topic"] == "Python Functions"
        assert metadata["difficulty"] == "intermediate"
        assert "generated_at" in metadata
        assert "word_count" in metadata
        assert metadata["word_count"] > 0
        
    def test_generate_study_guide_beginner(self):
        """Test beginner level study guide"""
        response = client.post(
            "/v1/learning/study-guides/generate",
            json={
                "topic": "Variables",
                "difficulty": "beginner",
                "include_questions": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["metadata"]["difficulty"] == "beginner"
        
    def test_generate_study_guide_advanced(self):
        """Test advanced level study guide"""
        response = client.post(
            "/v1/learning/study-guides/generate",
            json={
                "topic": "Decorators and Metaclasses",
                "difficulty": "advanced",
                "include_questions": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["metadata"]["difficulty"] == "advanced"
        
    def test_generate_study_guide_invalid_difficulty(self):
        """Test with invalid difficulty level"""
        response = client.post(
            "/v1/learning/study-guides/generate",
            json={
                "topic": "Python",
                "difficulty": "invalid"
            }
        )
        
        assert response.status_code == 422  # Validation error
        
    def test_generate_study_guide_empty_topic(self):
        """Test with empty topic"""
        response = client.post(
            "/v1/learning/study-guides/generate",
            json={
                "topic": "",
                "difficulty": "intermediate"
            }
        )
        
        assert response.status_code == 422  # Validation error
        
    def test_study_guide_performance(self):
        """Test study guide generation performance"""
        start_time = time.time()
        
        response = client.post(
            "/v1/learning/study-guides/generate",
            json={
                "topic": "Loops",
                "difficulty": "beginner",
                "include_questions": False
            }
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        assert response.status_code == 200
        assert duration < 30  # Should complete within 30 seconds
        print(f"Study guide generation took {duration:.2f} seconds")


# ============================================================================
# QUIZ TESTS
# ============================================================================

class TestQuizzes:
    """Test quiz generation and submission"""
    
    def test_generate_quiz_success(self):
        """Test successful quiz generation"""
        response = client.post(
            "/v1/learning/quizzes/generate",
            json={
                "topic": "Basic Math",
                "num_questions": 3,
                "difficulty": "beginner"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "quiz" in data
        assert "metadata" in data
        assert "questions" in data["quiz"]
        
        # Verify questions
        questions = data["quiz"]["questions"]
        assert len(questions) == 3
        
        for q in questions:
            assert "id" in q
            assert "type" in q
            assert "question" in q
            assert "correct_answer" in q
            
            if q["type"] == "multiple_choice":
                assert "options" in q
                assert len(q["options"]) >= 2
                
    def test_generate_quiz_different_counts(self):
        """Test generating quizzes with different question counts"""
        for num_questions in [1, 5, 10]:
            response = client.post(
                "/v1/learning/quizzes/generate",
                json={
                    "topic": "Science",
                    "num_questions": num_questions,
                    "difficulty": "intermediate"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["quiz"]["questions"]) == num_questions
            
    def test_generate_quiz_max_questions(self):
        """Test maximum question limit"""
        response = client.post(
            "/v1/learning/quizzes/generate",
            json={
                "topic": "History",
                "num_questions": 20,  # Maximum
                "difficulty": "intermediate"
            }
        )
        
        assert response.status_code == 200
        
    def test_generate_quiz_too_many_questions(self):
        """Test exceeding maximum questions"""
        response = client.post(
            "/v1/learning/quizzes/generate",
            json={
                "topic": "History",
                "num_questions": 25,  # Over maximum
                "difficulty": "intermediate"
            }
        )
        
        assert response.status_code == 422  # Validation error
        
    def test_submit_quiz_all_correct(self):
        """Test submitting quiz with all correct answers"""
        # First generate a quiz
        gen_response = client.post(
            "/v1/learning/quizzes/generate",
            json={
                "topic": "Simple Addition",
                "num_questions": 3,
                "difficulty": "beginner"
            }
        )
        
        assert gen_response.status_code == 200
        quiz_data = gen_response.json()
        
        # Create submission with all correct answers
        quiz = quiz_data["quiz"]
        answers = [
            {"question_id": q["id"], "answer": q["correct_answer"]}
            for q in quiz["questions"]
        ]
        
        submit_response = client.post(
            "/v1/learning/quizzes/submit",
            json={
                "quiz": quiz,
                "answers": answers,
                "time_taken": 60
            }
        )
        
        assert submit_response.status_code == 200
        result = submit_response.json()
        
        # Verify results
        assert result["correct"] == 3
        assert result["total"] == 3
        assert result["score"] == 3
        assert len(result["details"]) == 3
        
        # All should be correct
        for detail in result["details"]:
            assert detail["is_correct"] is True
            
    def test_submit_quiz_all_wrong(self):
        """Test submitting quiz with all wrong answers"""
        # Generate quiz
        gen_response = client.post(
            "/v1/learning/quizzes/generate",
            json={
                "topic": "Math",
                "num_questions": 2,
                "difficulty": "beginner"
            }
        )
        
        quiz_data = gen_response.json()
        quiz = quiz_data["quiz"]
        
        # Submit wrong answers (just use "Z" which won't match)
        answers = [
            {"question_id": q["id"], "answer": "Z"}
            for q in quiz["questions"]
        ]
        
        submit_response = client.post(
            "/v1/learning/quizzes/submit",
            json={
                "quiz": quiz,
                "answers": answers,
                "time_taken": 30
            }
        )
        
        assert submit_response.status_code == 200
        result = submit_response.json()
        
        assert result["correct"] == 0
        assert result["total"] == 2
        
    def test_submit_quiz_partial_correct(self):
        """Test submitting quiz with some correct answers"""
        # Generate quiz
        gen_response = client.post(
            "/v1/learning/quizzes/generate",
            json={
                "topic": "Geography",
                "num_questions": 4,
                "difficulty": "intermediate"
            }
        )
        
        quiz_data = gen_response.json()
        quiz = quiz_data["quiz"]
        
        # Answer first 2 correct, last 2 wrong
        answers = []
        for i, q in enumerate(quiz["questions"]):
            if i < 2:
                answers.append({"question_id": q["id"], "answer": q["correct_answer"]})
            else:
                answers.append({"question_id": q["id"], "answer": "WRONG"})
                
        submit_response = client.post(
            "/v1/learning/quizzes/submit",
            json={
                "quiz": quiz,
                "answers": answers,
                "time_taken": 120
            }
        )
        
        assert submit_response.status_code == 200
        result = submit_response.json()
        
        assert result["correct"] == 2
        assert result["total"] == 4
        
    def test_quiz_performance(self):
        """Test quiz generation performance"""
        start_time = time.time()
        
        response = client.post(
            "/v1/learning/quizzes/generate",
            json={
                "topic": "Programming",
                "num_questions": 5,
                "difficulty": "intermediate"
            }
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        assert response.status_code == 200
        assert duration < 20  # Should complete within 20 seconds
        print(f"Quiz generation took {duration:.2f} seconds")


# ============================================================================
# NOTES TESTS
# ============================================================================

class TestNotes:
    """Test notes CRUD operations"""
    
    def test_create_note(self):
        """Test creating a new note"""
        response = client.post(
            "/v1/learning/notes",
            json={
                "title": "Test Note",
                "content": "This is test content",
                "tags": ["test", "demo"],
                "color": "#667eea"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "note_id" in data
        assert data["title"] == "Test Note"
        assert data["content"] == "This is test content"
        assert "test" in data["tags"]
        assert data["color"] == "#667eea"
        assert "created_at" in data
        
        return data["note_id"]
        
    def test_list_notes(self):
        """Test listing all notes"""
        # Create a note first
        client.post(
            "/v1/learning/notes",
            json={
                "title": "List Test Note",
                "content": "Content for list test",
                "tags": ["list-test"]
            }
        )
        
        # List notes
        response = client.get("/v1/learning/notes")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
    def test_get_note_by_id(self):
        """Test retrieving a specific note"""
        # Create note
        create_response = client.post(
            "/v1/learning/notes",
            json={
                "title": "Get Test",
                "content": "Content",
                "tags": []
            }
        )
        note_id = create_response.json()["note_id"]
        
        # Get note
        response = client.get(f"/v1/learning/notes/{note_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["note_id"] == note_id
        assert data["title"] == "Get Test"
        
    def test_update_note(self):
        """Test updating a note"""
        # Create note
        create_response = client.post(
            "/v1/learning/notes",
            json={
                "title": "Original Title",
                "content": "Original Content",
                "tags": ["original"]
            }
        )
        note_id = create_response.json()["note_id"]
        
        # Update note
        update_response = client.patch(
            f"/v1/learning/notes/{note_id}",
            json={
                "title": "Updated Title",
                "tags": ["updated", "modified"]
            }
        )
        
        assert update_response.status_code == 200
        data = update_response.json()
        assert data["title"] == "Updated Title"
        assert "updated" in data["tags"]
        assert data["content"] == "Original Content"  # Not updated
        
    def test_delete_note(self):
        """Test deleting a note"""
        # Create note
        create_response = client.post(
            "/v1/learning/notes",
            json={
                "title": "To Delete",
                "content": "Will be deleted",
                "tags": []
            }
        )
        note_id = create_response.json()["note_id"]
        
        # Delete note
        delete_response = client.delete(f"/v1/learning/notes/{note_id}")
        assert delete_response.status_code == 200
        
        # Verify deleted
        get_response = client.get(f"/v1/learning/notes/{note_id}")
        assert get_response.status_code == 404
        
    def test_search_notes_by_tag(self):
        """Test searching notes by tag"""
        # Create notes with specific tag
        tag = "search-test-unique"
        for i in range(3):
            client.post(
                "/v1/learning/notes",
                json={
                    "title": f"Search Note {i}",
                    "content": f"Content {i}",
                    "tags": [tag, f"tag{i}"]
                }
            )
            
        # Search by tag
        response = client.get(f"/v1/learning/notes?tag={tag}")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3
        
    def test_search_notes_by_query(self):
        """Test searching notes by text query"""
        # Create note with unique content
        unique_word = f"uniqueword{int(time.time())}"
        client.post(
            "/v1/learning/notes",
            json={
                "title": f"Note with {unique_word}",
                "content": f"This contains {unique_word}",
                "tags": []
            }
        )
        
        # Search
        response = client.get(f"/v1/learning/notes?q={unique_word}")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        
    def test_pin_note(self):
        """Test pinning a note"""
        # Create note
        create_response = client.post(
            "/v1/learning/notes",
            json={
                "title": "To Pin",
                "content": "Content",
                "tags": []
            }
        )
        note_id = create_response.json()["note_id"]
        
        # Pin note
        update_response = client.patch(
            f"/v1/learning/notes/{note_id}",
            json={"pinned": True}
        )
        
        assert update_response.status_code == 200
        assert update_response.json()["pinned"] is True


# ============================================================================
# PROGRESS TRACKING TESTS
# ============================================================================

class TestProgress:
    """Test progress tracking"""
    
    def test_get_progress_summary(self):
        """Test retrieving progress summary"""
        response = client.get("/v1/learning/progress/summary")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "total_study_time" in data
        assert "notes_created" in data
        assert "quizzes_completed" in data
        assert "achievements" in data
        assert "streak" in data
        
    def test_get_achievements(self):
        """Test retrieving achievements"""
        response = client.get("/v1/learning/progress/achievements")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        
    def test_quiz_records_progress(self):
        """Test that completing quiz updates progress"""
        # Get initial progress
        initial_response = client.get("/v1/learning/progress/summary")
        initial_data = initial_response.json()
        initial_quizzes = initial_data.get("quizzes_completed", 0)
        
        # Generate and submit quiz
        gen_response = client.post(
            "/v1/learning/quizzes/generate",
            json={
                "topic": "Progress Test",
                "num_questions": 2,
                "difficulty": "beginner"
            }
        )
        
        quiz_data = gen_response.json()
        quiz = quiz_data["quiz"]
        
        answers = [
            {"question_id": q["id"], "answer": q["correct_answer"]}
            for q in quiz["questions"]
        ]
        
        client.post(
            "/v1/learning/quizzes/submit",
            json={
                "quiz": quiz,
                "answers": answers,
                "time_taken": 30
            }
        )
        
        # Get updated progress
        updated_response = client.get("/v1/learning/progress/summary")
        updated_data = updated_response.json()
        updated_quizzes = updated_data.get("quizzes_completed", 0)
        
        # Should have increased
        assert updated_quizzes > initial_quizzes


# ============================================================================
# PERFORMANCE & LOAD TESTS
# ============================================================================

class TestPerformance:
    """Test system performance under load"""
    
    def test_concurrent_note_creation(self):
        """Test creating multiple notes quickly"""
        start_time = time.time()
        
        for i in range(10):
            response = client.post(
                "/v1/learning/notes",
                json={
                    "title": f"Concurrent Note {i}",
                    "content": f"Content {i}",
                    "tags": [f"batch-{i}"]
                }
            )
            assert response.status_code == 200
            
        end_time = time.time()
        duration = end_time - start_time
        
        assert duration < 5  # Should complete within 5 seconds
        print(f"Created 10 notes in {duration:.2f} seconds")
        
    def test_list_performance_with_many_notes(self):
        """Test listing performance with many notes"""
        # Create multiple notes if needed
        for i in range(5):
            client.post(
                "/v1/learning/notes",
                json={
                    "title": f"Perf Test {i}",
                    "content": f"Content {i}",
                    "tags": ["performance"]
                }
            )
            
        start_time = time.time()
        response = client.get("/v1/learning/notes")
        end_time = time.time()
        
        duration = end_time - start_time
        
        assert response.status_code == 200
        assert duration < 1  # Should be very fast
        print(f"Listed notes in {duration:.3f} seconds")
        
    def test_search_performance(self):
        """Test search performance"""
        start_time = time.time()
        response = client.get("/v1/learning/notes?q=test")
        end_time = time.time()
        
        duration = end_time - start_time
        
        assert response.status_code == 200
        assert duration < 2  # Search should be fast
        print(f"Search completed in {duration:.3f} seconds")


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Test integrated workflows"""
    
    def test_complete_learning_workflow(self):
        """Test a complete learning session workflow"""
        # 1. Generate study guide
        study_response = client.post(
            "/v1/learning/study-guides/generate",
            json={
                "topic": "Workflow Test Topic",
                "difficulty": "intermediate",
                "include_questions": True
            }
        )
        assert study_response.status_code == 200
        
        # 2. Create notes about the topic
        note_response = client.post(
            "/v1/learning/notes",
            json={
                "title": "Notes on Workflow Test Topic",
                "content": "Key points learned from study guide",
                "tags": ["workflow", "test"]
            }
        )
        assert note_response.status_code == 200
        note_id = note_response.json()["note_id"]
        
        # 3. Take a quiz
        quiz_response = client.post(
            "/v1/learning/quizzes/generate",
            json={
                "topic": "Workflow Test Topic",
                "num_questions": 3,
                "difficulty": "intermediate"
            }
        )
        assert quiz_response.status_code == 200
        
        quiz_data = quiz_response.json()
        quiz = quiz_data["quiz"]
        
        # 4. Submit quiz
        answers = [
            {"question_id": q["id"], "answer": q["correct_answer"]}
            for q in quiz["questions"]
        ]
        
        submit_response = client.post(
            "/v1/learning/quizzes/submit",
            json={
                "quiz": quiz,
                "answers": answers,
                "time_taken": 90
            }
        )
        assert submit_response.status_code == 200
        
        # 5. Check progress
        progress_response = client.get("/v1/learning/progress/summary")
        assert progress_response.status_code == 200
        
        # 6. Update notes based on quiz
        update_response = client.patch(
            f"/v1/learning/notes/{note_id}",
            json={
                "content": "Updated after quiz completion"
            }
        )
        assert update_response.status_code == 200
        
        print("✅ Complete workflow test passed!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
