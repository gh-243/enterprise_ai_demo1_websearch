"""
Social models for collaborative learning features.

This module defines data models for users, study groups, discussions,
and other social features in Phase 9.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User roles in the system"""
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"


class User(BaseModel):
    """
    User profile for collaborative features.
    
    Represents a student or instructor using the platform.
    Includes profile information and activity tracking.
    """
    id: str = Field(..., description="Unique user identifier")
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: str = Field(..., description="User email address")
    display_name: str = Field(..., max_length=100, description="Display name")
    avatar_url: Optional[str] = Field(None, description="Profile picture URL")
    bio: Optional[str] = Field(None, max_length=500, description="User biography")
    role: UserRole = Field(default=UserRole.STUDENT, description="User role")
    created_at: datetime = Field(default_factory=datetime.now, description="Account creation timestamp")
    last_active: datetime = Field(default_factory=datetime.now, description="Last activity timestamp")
    
    # Statistics
    total_groups: int = Field(default=0, description="Number of groups joined")
    total_discussions: int = Field(default=0, description="Number of discussions created")
    total_replies: int = Field(default=0, description="Number of replies posted")
    reputation_score: int = Field(default=0, description="Reputation points")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "user_123",
                "username": "johndoe",
                "email": "john@example.com",
                "display_name": "John Doe",
                "bio": "Computer Science student",
                "role": "student",
                "reputation_score": 150
            }
        }


class GroupRole(str, Enum):
    """Roles within a study group"""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class GroupVisibility(str, Enum):
    """Group visibility settings"""
    PUBLIC = "public"      # Anyone can see and join
    PRIVATE = "private"    # Only invited members can see
    HIDDEN = "hidden"      # Only members can see


class StudyGroup(BaseModel):
    """
    Study group for collaborative learning.
    
    Groups allow students to collaborate, share resources,
    and discuss topics together.
    """
    id: str = Field(..., description="Unique group identifier")
    name: str = Field(..., min_length=3, max_length=100, description="Group name")
    description: str = Field(..., max_length=1000, description="Group description")
    created_by: str = Field(..., description="User ID of group creator")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    # Settings
    visibility: GroupVisibility = Field(default=GroupVisibility.PUBLIC, description="Group visibility")
    max_members: int = Field(default=50, ge=2, le=500, description="Maximum number of members")
    tags: List[str] = Field(default_factory=list, description="Group tags/topics")
    
    # Statistics
    member_count: int = Field(default=1, description="Current number of members")
    discussion_count: int = Field(default=0, description="Number of discussions")
    shared_resource_count: int = Field(default=0, description="Number of shared resources")
    
    # Features
    allow_discussions: bool = Field(default=True, description="Allow discussions")
    allow_resource_sharing: bool = Field(default=True, description="Allow resource sharing")
    allow_peer_reviews: bool = Field(default=True, description="Allow peer reviews")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "group_123",
                "name": "CS101 Study Group",
                "description": "Study group for Computer Science 101",
                "created_by": "user_123",
                "visibility": "public",
                "tags": ["computer-science", "programming", "python"],
                "member_count": 15
            }
        }


class MembershipStatus(str, Enum):
    """Status of group membership"""
    ACTIVE = "active"
    INVITED = "invited"
    BANNED = "banned"
    LEFT = "left"


class GroupMembership(BaseModel):
    """
    User membership in a study group.
    
    Tracks which users belong to which groups and their roles.
    """
    id: str = Field(..., description="Unique membership identifier")
    group_id: str = Field(..., description="Study group ID")
    user_id: str = Field(..., description="User ID")
    role: GroupRole = Field(default=GroupRole.MEMBER, description="Member role")
    status: MembershipStatus = Field(default=MembershipStatus.ACTIVE, description="Membership status")
    joined_at: datetime = Field(default_factory=datetime.now, description="Join timestamp")
    invited_by: Optional[str] = Field(None, description="User ID of inviter")
    
    # Activity
    last_read_at: datetime = Field(default_factory=datetime.now, description="Last read timestamp")
    message_count: int = Field(default=0, description="Number of messages sent")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "membership_456",
                "group_id": "group_123",
                "user_id": "user_789",
                "role": "member",
                "status": "active"
            }
        }


class DiscussionCategory(str, Enum):
    """Categories for discussions"""
    QUESTION = "question"
    DISCUSSION = "discussion"
    ANNOUNCEMENT = "announcement"
    RESOURCE = "resource"
    STUDY_TIP = "study_tip"


class Discussion(BaseModel):
    """
    Discussion thread in a study group.
    
    Represents a question, announcement, or general discussion
    within a study group.
    """
    id: str = Field(..., description="Unique discussion identifier")
    group_id: str = Field(..., description="Study group ID")
    author_id: str = Field(..., description="Author user ID")
    
    # Content
    title: str = Field(..., min_length=5, max_length=200, description="Discussion title")
    content: str = Field(..., min_length=10, description="Discussion content (markdown supported)")
    category: DiscussionCategory = Field(..., description="Discussion category")
    tags: List[str] = Field(default_factory=list, description="Discussion tags")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    last_activity_at: datetime = Field(default_factory=datetime.now, description="Last activity timestamp")
    
    # State
    is_pinned: bool = Field(default=False, description="Is pinned to top")
    is_locked: bool = Field(default=False, description="Is locked from replies")
    is_resolved: bool = Field(default=False, description="Is marked as resolved (for questions)")
    
    # Statistics
    views: int = Field(default=0, description="View count")
    reply_count: int = Field(default=0, description="Number of replies")
    upvote_count: int = Field(default=0, description="Number of upvotes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "discussion_789",
                "group_id": "group_123",
                "author_id": "user_456",
                "title": "How do I implement binary search?",
                "content": "I'm struggling with the recursive approach...",
                "category": "question",
                "tags": ["algorithms", "python"],
                "reply_count": 5
            }
        }


class DiscussionReply(BaseModel):
    """
    Reply to a discussion thread.
    
    Represents a response or answer to a discussion.
    """
    id: str = Field(..., description="Unique reply identifier")
    discussion_id: str = Field(..., description="Parent discussion ID")
    author_id: str = Field(..., description="Author user ID")
    
    # Content
    content: str = Field(..., min_length=1, description="Reply content (markdown supported)")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    # State
    is_accepted_answer: bool = Field(default=False, description="Is marked as accepted answer")
    is_edited: bool = Field(default=False, description="Has been edited")
    
    # Voting
    upvotes: int = Field(default=0, description="Number of upvotes")
    downvotes: int = Field(default=0, description="Number of downvotes")
    
    # Threading
    parent_reply_id: Optional[str] = Field(None, description="Parent reply ID for nested replies")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "reply_123",
                "discussion_id": "discussion_789",
                "author_id": "user_456",
                "content": "Here's how I implemented it...",
                "is_accepted_answer": True,
                "upvotes": 12
            }
        }


class ReactionType(str, Enum):
    """Types of reactions"""
    LIKE = "like"
    LOVE = "love"
    HELPFUL = "helpful"
    INSIGHTFUL = "insightful"
    FUNNY = "funny"


class Reaction(BaseModel):
    """
    Reaction to a discussion or reply.
    
    Allows users to quickly respond with emoji reactions.
    """
    id: str = Field(..., description="Unique reaction identifier")
    target_type: str = Field(..., description="Type of target (discussion/reply)")
    target_id: str = Field(..., description="Target ID")
    user_id: str = Field(..., description="User who reacted")
    reaction_type: ReactionType = Field(..., description="Type of reaction")
    created_at: datetime = Field(default_factory=datetime.now, description="Reaction timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "reaction_123",
                "target_type": "reply",
                "target_id": "reply_456",
                "user_id": "user_789",
                "reaction_type": "helpful"
            }
        }
