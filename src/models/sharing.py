"""
Peer review and content sharing models.

This module defines models for peer reviews, content sharing,
and collaborative features in Phase 9.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ContentType(str, Enum):
    """Types of shareable content"""
    NOTE = "note"
    STUDY_GUIDE = "study_guide"
    QUIZ = "quiz"
    DOCUMENT = "document"
    PODCAST = "podcast"


class SharePermission(str, Enum):
    """Permission levels for shared content"""
    VIEW = "view"           # Can only view
    COMMENT = "comment"     # Can view and comment
    EDIT = "edit"           # Can view, comment, and edit


class PeerReview(BaseModel):
    """
    Peer review for shared content.
    
    Allows students to rate and provide feedback on
    shared study materials, notes, and resources.
    """
    id: str = Field(..., description="Unique review identifier")
    content_type: ContentType = Field(..., description="Type of content being reviewed")
    content_id: str = Field(..., description="ID of content being reviewed")
    reviewer_id: str = Field(..., description="User ID of reviewer")
    
    # Review content
    rating: int = Field(..., ge=1, le=5, description="Rating (1-5 stars)")
    title: Optional[str] = Field(None, max_length=100, description="Review title")
    comment: str = Field(..., min_length=10, max_length=2000, description="Review comment")
    
    # Specific feedback
    strengths: List[str] = Field(default_factory=list, description="Identified strengths")
    suggestions: List[str] = Field(default_factory=list, description="Suggestions for improvement")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now, description="Review creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    # Engagement
    helpful_count: int = Field(default=0, description="Number of users who found this helpful")
    report_count: int = Field(default=0, description="Number of reports (spam/inappropriate)")
    
    # State
    is_verified: bool = Field(default=False, description="Verified review (by instructor)")
    is_hidden: bool = Field(default=False, description="Hidden by moderator")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "review_123",
                "content_type": "study_guide",
                "content_id": "guide_789",
                "reviewer_id": "user_456",
                "rating": 5,
                "title": "Excellent study guide!",
                "comment": "Very comprehensive and well-organized. Helped me ace the exam!",
                "strengths": ["Clear explanations", "Good examples", "Well structured"],
                "helpful_count": 15
            }
        }


class ContentShare(BaseModel):
    """
    Shared content within a study group.
    
    Represents content shared by one user with a group,
    including permissions and access control.
    """
    id: str = Field(..., description="Unique share identifier")
    group_id: str = Field(..., description="Study group ID")
    owner_id: str = Field(..., description="User ID of content owner")
    
    # Content reference
    content_type: ContentType = Field(..., description="Type of content")
    content_id: str = Field(..., description="ID of content")
    
    # Metadata
    title: str = Field(..., description="Content title")
    description: Optional[str] = Field(None, max_length=500, description="Share description")
    tags: List[str] = Field(default_factory=list, description="Content tags")
    
    # Permissions
    permission: SharePermission = Field(..., description="Permission level")
    allow_downloads: bool = Field(default=True, description="Allow downloads")
    allow_reshare: bool = Field(default=False, description="Allow re-sharing to other groups")
    
    # Timestamps
    shared_at: datetime = Field(default_factory=datetime.now, description="Share timestamp")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")
    
    # Statistics
    view_count: int = Field(default=0, description="Number of views")
    download_count: int = Field(default=0, description="Number of downloads")
    comment_count: int = Field(default=0, description="Number of comments")
    average_rating: float = Field(default=0.0, ge=0.0, le=5.0, description="Average review rating")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "share_123",
                "group_id": "group_456",
                "owner_id": "user_789",
                "content_type": "note",
                "content_id": "note_012",
                "title": "Chapter 5 Notes - Data Structures",
                "permission": "view",
                "view_count": 42,
                "average_rating": 4.5
            }
        }


class ShareComment(BaseModel):
    """
    Comment on shared content.
    
    Allows group members to discuss and ask questions
    about shared resources.
    """
    id: str = Field(..., description="Unique comment identifier")
    share_id: str = Field(..., description="Share ID")
    author_id: str = Field(..., description="Comment author user ID")
    
    # Content
    content: str = Field(..., min_length=1, max_length=1000, description="Comment text")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    # Threading
    parent_comment_id: Optional[str] = Field(None, description="Parent comment ID for replies")
    
    # Engagement
    upvotes: int = Field(default=0, description="Number of upvotes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "comment_123",
                "share_id": "share_456",
                "author_id": "user_789",
                "content": "Great notes! Could you explain the section on binary trees more?",
                "upvotes": 3
            }
        }


class CollaborativeEdit(BaseModel):
    """
    Collaborative edit to shared content.
    
    Tracks edits made to shared content when edit permission
    is granted.
    """
    id: str = Field(..., description="Unique edit identifier")
    share_id: str = Field(..., description="Share ID")
    editor_id: str = Field(..., description="User ID of editor")
    
    # Edit details
    edit_type: str = Field(..., description="Type of edit (add/modify/delete)")
    section: str = Field(..., description="Section edited")
    before_content: str = Field(..., description="Content before edit")
    after_content: str = Field(..., description="Content after edit")
    
    # Timestamps
    edited_at: datetime = Field(default_factory=datetime.now, description="Edit timestamp")
    
    # State
    is_approved: bool = Field(default=False, description="Approved by content owner")
    is_rejected: bool = Field(default=False, description="Rejected by content owner")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "edit_123",
                "share_id": "share_456",
                "editor_id": "user_789",
                "edit_type": "modify",
                "section": "Section 2",
                "is_approved": True
            }
        }


class NotificationType(str, Enum):
    """Types of notifications"""
    GROUP_INVITE = "group_invite"
    DISCUSSION_REPLY = "discussion_reply"
    MENTION = "mention"
    REVIEW_RECEIVED = "review_received"
    CONTENT_SHARED = "content_shared"
    UPVOTE = "upvote"
    ACCEPTED_ANSWER = "accepted_answer"
    GROUP_ANNOUNCEMENT = "group_announcement"


class Notification(BaseModel):
    """
    User notification for social activities.
    
    Notifies users of important events like replies,
    mentions, and group activities.
    """
    id: str = Field(..., description="Unique notification identifier")
    user_id: str = Field(..., description="Recipient user ID")
    
    # Content
    type: NotificationType = Field(..., description="Notification type")
    title: str = Field(..., max_length=200, description="Notification title")
    message: str = Field(..., max_length=500, description="Notification message")
    
    # References
    link_url: Optional[str] = Field(None, description="URL to related content")
    source_user_id: Optional[str] = Field(None, description="User who triggered notification")
    group_id: Optional[str] = Field(None, description="Related group ID")
    discussion_id: Optional[str] = Field(None, description="Related discussion ID")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    read_at: Optional[datetime] = Field(None, description="Read timestamp")
    
    # State
    is_read: bool = Field(default=False, description="Has been read")
    is_dismissed: bool = Field(default=False, description="Has been dismissed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "notification_123",
                "user_id": "user_456",
                "type": "discussion_reply",
                "title": "New reply to your discussion",
                "message": "John Doe replied to 'How do I implement binary search?'",
                "link_url": "/discussions/789",
                "is_read": False
            }
        }


class ActivityType(str, Enum):
    """Types of user activities"""
    CREATED_GROUP = "created_group"
    JOINED_GROUP = "joined_group"
    POSTED_DISCUSSION = "posted_discussion"
    POSTED_REPLY = "posted_reply"
    SHARED_CONTENT = "shared_content"
    GAVE_REVIEW = "gave_review"
    EARNED_ACHIEVEMENT = "earned_achievement"


class UserActivity(BaseModel):
    """
    User activity log for social features.
    
    Tracks user actions for activity feed and analytics.
    """
    id: str = Field(..., description="Unique activity identifier")
    user_id: str = Field(..., description="User ID")
    
    # Activity details
    activity_type: ActivityType = Field(..., description="Type of activity")
    description: str = Field(..., description="Activity description")
    
    # References
    group_id: Optional[str] = Field(None, description="Related group ID")
    discussion_id: Optional[str] = Field(None, description="Related discussion ID")
    content_id: Optional[str] = Field(None, description="Related content ID")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now, description="Activity timestamp")
    
    # Visibility
    is_public: bool = Field(default=True, description="Visible to others")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "activity_123",
                "user_id": "user_456",
                "activity_type": "posted_discussion",
                "description": "Posted a new question in CS101 Study Group",
                "group_id": "group_789",
                "discussion_id": "discussion_012"
            }
        }


class Badge(BaseModel):
    """
    Achievement badge for user accomplishments.
    
    Rewards users for participation and contributions.
    """
    id: str = Field(..., description="Unique badge identifier")
    name: str = Field(..., description="Badge name")
    description: str = Field(..., description="Badge description")
    icon: str = Field(..., description="Badge icon/emoji")
    
    # Criteria
    criteria_type: str = Field(..., description="Type of criteria (e.g., 'discussion_count')")
    criteria_value: int = Field(..., description="Required value to earn badge")
    
    # Rarity
    rarity: str = Field(..., description="Badge rarity (common/rare/epic/legendary)")
    points: int = Field(..., description="Reputation points awarded")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "badge_123",
                "name": "Helpful Helper",
                "description": "Received 10 helpful votes on your replies",
                "icon": "🌟",
                "criteria_type": "helpful_votes",
                "criteria_value": 10,
                "rarity": "rare",
                "points": 50
            }
        }


class UserBadge(BaseModel):
    """
    Badge earned by a user.
    
    Tracks which badges users have earned.
    """
    id: str = Field(..., description="Unique user badge identifier")
    user_id: str = Field(..., description="User ID")
    badge_id: str = Field(..., description="Badge ID")
    earned_at: datetime = Field(default_factory=datetime.now, description="Earned timestamp")
    
    # Display
    is_displayed: bool = Field(default=False, description="Shown on user profile")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "user_badge_123",
                "user_id": "user_456",
                "badge_id": "badge_789",
                "is_displayed": True
            }
        }
