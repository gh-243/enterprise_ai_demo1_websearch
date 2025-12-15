# STUDENT ASSISTANT FEATURE - PHASE 8
"""
Note-Taking System Implementation

Provides note storage, retrieval, and management for students.
Supports markdown formatting, tags, and linking to documents/podcasts.
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class Note:
    """Represents a student note."""
    note_id: str
    title: str
    content: str
    tags: List[str]
    created_at: str
    updated_at: str
    document_id: Optional[str] = None
    podcast_id: Optional[str] = None
    color: str = "#667eea"  # Default purple
    pinned: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert note to dictionary."""
        return asdict(self)


class NoteManager:
    """
    Manages student notes with persistence.
    
    Features:
    - Create, read, update, delete notes
    - Tag-based organization
    - Search by content or tags
    - Link notes to documents and podcasts
    - Pin important notes
    - Export/import functionality
    """
    
    def __init__(self, storage_path: str = "data/notes"):
        """
        Initialize note manager.
        
        Args:
            storage_path: Directory to store notes
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.notes_file = self.storage_path / "notes.json"
        self._load_notes()
    
    def _load_notes(self):
        """Load notes from storage."""
        if self.notes_file.exists():
            try:
                with open(self.notes_file, 'r') as f:
                    data = json.load(f)
                    self.notes = {
                        note_id: Note(**note_data)
                        for note_id, note_data in data.items()
                    }
                logger.info(f"Loaded {len(self.notes)} notes")
            except Exception as e:
                logger.error(f"Failed to load notes: {e}")
                self.notes = {}
        else:
            self.notes = {}
    
    def _save_notes(self):
        """Save notes to storage."""
        try:
            data = {
                note_id: note.to_dict()
                for note_id, note in self.notes.items()
            }
            with open(self.notes_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved {len(self.notes)} notes")
        except Exception as e:
            logger.error(f"Failed to save notes: {e}")
            raise
    
    def create_note(
        self,
        title: str,
        content: str,
        tags: Optional[List[str]] = None,
        document_id: Optional[str] = None,
        podcast_id: Optional[str] = None,
        color: str = "#667eea"
    ) -> Note:
        """
        Create a new note.
        
        Args:
            title: Note title
            content: Note content (markdown supported)
            tags: Optional list of tags
            document_id: Optional linked document ID
            podcast_id: Optional linked podcast ID
            color: Color code for note
            
        Returns:
            Created Note object
        """
        # Generate unique ID
        note_id = f"note_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        now = datetime.now().isoformat()
        
        note = Note(
            note_id=note_id,
            title=title,
            content=content,
            tags=tags or [],
            created_at=now,
            updated_at=now,
            document_id=document_id,
            podcast_id=podcast_id,
            color=color,
            pinned=False
        )
        
        self.notes[note_id] = note
        self._save_notes()
        
        logger.info(f"Created note: {note_id}")
        return note
    
    def get_note(self, note_id: str) -> Optional[Note]:
        """Get a note by ID."""
        return self.notes.get(note_id)
    
    def list_notes(
        self,
        tag: Optional[str] = None,
        document_id: Optional[str] = None,
        podcast_id: Optional[str] = None,
        pinned_only: bool = False
    ) -> List[Note]:
        """
        List notes with optional filters.
        
        Args:
            tag: Filter by tag
            document_id: Filter by linked document
            podcast_id: Filter by linked podcast
            pinned_only: Show only pinned notes
            
        Returns:
            List of matching notes, sorted by updated_at (newest first)
        """
        notes = list(self.notes.values())
        
        # Apply filters
        if tag:
            notes = [n for n in notes if tag in n.tags]
        
        if document_id:
            notes = [n for n in notes if n.document_id == document_id]
        
        if podcast_id:
            notes = [n for n in notes if n.podcast_id == podcast_id]
        
        if pinned_only:
            notes = [n for n in notes if n.pinned]
        
        # Sort by updated_at (newest first)
        notes.sort(key=lambda n: n.updated_at, reverse=True)
        
        return notes
    
    def update_note(
        self,
        note_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        tags: Optional[List[str]] = None,
        color: Optional[str] = None,
        pinned: Optional[bool] = None
    ) -> Note:
        """
        Update an existing note.
        
        Args:
            note_id: ID of note to update
            title: New title (optional)
            content: New content (optional)
            tags: New tags (optional)
            color: New color (optional)
            pinned: Pin/unpin note (optional)
            
        Returns:
            Updated Note object
            
        Raises:
            ValueError: If note not found
        """
        note = self.notes.get(note_id)
        if not note:
            raise ValueError(f"Note not found: {note_id}")
        
        # Update fields
        if title is not None:
            note.title = title
        if content is not None:
            note.content = content
        if tags is not None:
            note.tags = tags
        if color is not None:
            note.color = color
        if pinned is not None:
            note.pinned = pinned
        
        note.updated_at = datetime.now().isoformat()
        
        self._save_notes()
        logger.info(f"Updated note: {note_id}")
        
        return note
    
    def delete_note(self, note_id: str) -> bool:
        """
        Delete a note.
        
        Args:
            note_id: ID of note to delete
            
        Returns:
            True if deleted, False if not found
        """
        if note_id in self.notes:
            del self.notes[note_id]
            self._save_notes()
            logger.info(f"Deleted note: {note_id}")
            return True
        return False
    
    def search_notes(self, query: str) -> List[Note]:
        """
        Search notes by content or title.
        
        Args:
            query: Search query (case-insensitive)
            
        Returns:
            List of matching notes
        """
        query_lower = query.lower()
        
        matching_notes = [
            note for note in self.notes.values()
            if query_lower in note.title.lower() or query_lower in note.content.lower()
        ]
        
        # Sort by updated_at
        matching_notes.sort(key=lambda n: n.updated_at, reverse=True)
        
        return matching_notes
    
    def get_all_tags(self) -> List[str]:
        """Get all unique tags across all notes."""
        tags = set()
        for note in self.notes.values():
            tags.update(note.tags)
        return sorted(list(tags))
    
    def export_notes(self, output_path: str):
        """
        Export all notes to JSON file.
        
        Args:
            output_path: Path to export file
        """
        data = {
            note_id: note.to_dict()
            for note_id, note in self.notes.items()
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Exported {len(self.notes)} notes to {output_path}")
    
    def import_notes(self, input_path: str):
        """
        Import notes from JSON file.
        
        Args:
            input_path: Path to import file
        """
        with open(input_path, 'r') as f:
            data = json.load(f)
        
        imported_count = 0
        for note_id, note_data in data.items():
            if note_id not in self.notes:
                self.notes[note_id] = Note(**note_data)
                imported_count += 1
        
        self._save_notes()
        logger.info(f"Imported {imported_count} new notes")


# Global note manager instance
_note_manager = None


def get_note_manager() -> NoteManager:
    """Get the global note manager instance."""
    global _note_manager
    if _note_manager is None:
        _note_manager = NoteManager()
    return _note_manager
