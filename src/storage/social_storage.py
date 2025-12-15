"""
Social data storage manager.

Handles persistence of users, groups, discussions, and social features.
Uses JSON file storage with in-memory caching.
"""

import json
import os
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime

from src.models.social import (
    User, StudyGroup, GroupMembership, Discussion, DiscussionReply,
    Reaction, GroupRole, MembershipStatus, DiscussionCategory
)
from src.models.sharing import (
    PeerReview, ContentShare, ShareComment, Notification,
    UserActivity, Badge, UserBadge
)


class SocialStorage:
    """
    Storage manager for social/collaborative features.
    
    Provides CRUD operations for all social data with JSON persistence.
    """
    
    def __init__(self, base_dir: str = "data/social"):
        """Initialize storage with data directory"""
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Storage files
        self.users_file = self.base_dir / "users.json"
        self.groups_file = self.base_dir / "groups.json"
        self.memberships_file = self.base_dir / "memberships.json"
        self.discussions_file = self.base_dir / "discussions.json"
        self.replies_file = self.base_dir / "replies.json"
        self.reactions_file = self.base_dir / "reactions.json"
        self.reviews_file = self.base_dir / "reviews.json"
        self.shares_file = self.base_dir / "shares.json"
        self.comments_file = self.base_dir / "comments.json"
        self.notifications_file = self.base_dir / "notifications.json"
        self.activities_file = self.base_dir / "activities.json"
        self.badges_file = self.base_dir / "badges.json"
        self.user_badges_file = self.base_dir / "user_badges.json"
        
        # Initialize files if they don't exist
        self._init_storage()
    
    def _init_storage(self):
        """Initialize all storage files"""
        files = [
            self.users_file, self.groups_file, self.memberships_file,
            self.discussions_file, self.replies_file, self.reactions_file,
            self.reviews_file, self.shares_file, self.comments_file,
            self.notifications_file, self.activities_file, self.badges_file,
            self.user_badges_file
        ]
        
        for file_path in files:
            if not file_path.exists():
                with open(file_path, 'w') as f:
                    json.dump([], f)
    
    # ==================== USER OPERATIONS ====================
    
    def save_user(self, user: User) -> User:
        """Save or update a user"""
        users = self._load_json(self.users_file)
        
        # Update existing or append new
        found = False
        for i, u in enumerate(users):
            if u['id'] == user.id:
                users[i] = user.model_dump()
                found = True
                break
        
        if not found:
            users.append(user.model_dump())
        
        self._save_json(self.users_file, users)
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        users = self._load_json(self.users_file)
        for u in users:
            if u['id'] == user_id:
                return User(**u)
        return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        users = self._load_json(self.users_file)
        for u in users:
            if u['username'] == username:
                return User(**u)
        return None
    
    def list_users(self, limit: int = 100, offset: int = 0) -> List[User]:
        """List all users with pagination"""
        users = self._load_json(self.users_file)
        return [User(**u) for u in users[offset:offset + limit]]
    
    # ==================== GROUP OPERATIONS ====================
    
    def save_group(self, group: StudyGroup) -> StudyGroup:
        """Save or update a study group"""
        groups = self._load_json(self.groups_file)
        
        found = False
        for i, g in enumerate(groups):
            if g['id'] == group.id:
                group.updated_at = datetime.now()
                groups[i] = group.model_dump()
                found = True
                break
        
        if not found:
            groups.append(group.model_dump())
        
        self._save_json(self.groups_file, groups)
        return group
    
    def get_group(self, group_id: str) -> Optional[StudyGroup]:
        """Get group by ID"""
        groups = self._load_json(self.groups_file)
        for g in groups:
            if g['id'] == group_id:
                return StudyGroup(**g)
        return None
    
    def list_groups(
        self,
        visibility: Optional[str] = None,
        tag: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[StudyGroup]:
        """List groups with optional filtering"""
        groups = self._load_json(self.groups_file)
        
        # Filter by visibility
        if visibility:
            groups = [g for g in groups if g.get('visibility') == visibility]
        
        # Filter by tag
        if tag:
            groups = [g for g in groups if tag in g.get('tags', [])]
        
        return [StudyGroup(**g) for g in groups[offset:offset + limit]]
    
    def delete_group(self, group_id: str) -> bool:
        """Delete a group"""
        groups = self._load_json(self.groups_file)
        original_len = len(groups)
        groups = [g for g in groups if g['id'] != group_id]
        
        if len(groups) < original_len:
            self._save_json(self.groups_file, groups)
            # Also delete all memberships
            self._delete_group_memberships(group_id)
            return True
        return False
    
    # ==================== MEMBERSHIP OPERATIONS ====================
    
    def save_membership(self, membership: GroupMembership) -> GroupMembership:
        """Save or update a group membership"""
        memberships = self._load_json(self.memberships_file)
        
        found = False
        for i, m in enumerate(memberships):
            if m['id'] == membership.id:
                memberships[i] = membership.model_dump()
                found = True
                break
        
        if not found:
            memberships.append(membership.model_dump())
        
        self._save_json(self.memberships_file, memberships)
        
        # Update group member count
        self._update_group_member_count(membership.group_id)
        
        return membership
    
    def get_membership(self, membership_id: str) -> Optional[GroupMembership]:
        """Get membership by ID"""
        memberships = self._load_json(self.memberships_file)
        for m in memberships:
            if m['id'] == membership_id:
                return GroupMembership(**m)
        return None
    
    def get_user_membership(self, user_id: str, group_id: str) -> Optional[GroupMembership]:
        """Get user's membership in a group"""
        memberships = self._load_json(self.memberships_file)
        for m in memberships:
            if m['user_id'] == user_id and m['group_id'] == group_id:
                return GroupMembership(**m)
        return None
    
    def list_group_members(self, group_id: str, status: str = "active") -> List[GroupMembership]:
        """List all members of a group"""
        memberships = self._load_json(self.memberships_file)
        return [
            GroupMembership(**m) for m in memberships
            if m['group_id'] == group_id and m['status'] == status
        ]
    
    def list_user_groups(self, user_id: str, status: str = "active") -> List[str]:
        """List all groups a user is a member of"""
        memberships = self._load_json(self.memberships_file)
        return [
            m['group_id'] for m in memberships
            if m['user_id'] == user_id and m['status'] == status
        ]
    
    def delete_membership(self, membership_id: str) -> bool:
        """Delete a membership"""
        memberships = self._load_json(self.memberships_file)
        original_len = len(memberships)
        group_id = None
        
        for m in memberships:
            if m['id'] == membership_id:
                group_id = m['group_id']
                break
        
        memberships = [m for m in memberships if m['id'] != membership_id]
        
        if len(memberships) < original_len:
            self._save_json(self.memberships_file, memberships)
            if group_id:
                self._update_group_member_count(group_id)
            return True
        return False
    
    def _delete_group_memberships(self, group_id: str):
        """Delete all memberships for a group"""
        memberships = self._load_json(self.memberships_file)
        memberships = [m for m in memberships if m['group_id'] != group_id]
        self._save_json(self.memberships_file, memberships)
    
    def _update_group_member_count(self, group_id: str):
        """Update the member count for a group"""
        memberships = self.list_group_members(group_id, status="active")
        group = self.get_group(group_id)
        if group:
            group.member_count = len(memberships)
            self.save_group(group)
    
    # ==================== DISCUSSION OPERATIONS ====================
    
    def save_discussion(self, discussion: Discussion) -> Discussion:
        """Save or update a discussion"""
        discussions = self._load_json(self.discussions_file)
        
        found = False
        for i, d in enumerate(discussions):
            if d['id'] == discussion.id:
                discussion.updated_at = datetime.now()
                discussions[i] = discussion.model_dump()
                found = True
                break
        
        if not found:
            discussions.append(discussion.model_dump())
        
        self._save_json(self.discussions_file, discussions)
        
        # Update group discussion count
        self._update_group_discussion_count(discussion.group_id)
        
        return discussion
    
    def get_discussion(self, discussion_id: str) -> Optional[Discussion]:
        """Get discussion by ID"""
        discussions = self._load_json(self.discussions_file)
        for d in discussions:
            if d['id'] == discussion_id:
                return Discussion(**d)
        return None
    
    def list_group_discussions(
        self,
        group_id: str,
        category: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Discussion]:
        """List discussions in a group"""
        discussions = self._load_json(self.discussions_file)
        
        # Filter by group
        discussions = [d for d in discussions if d['group_id'] == group_id]
        
        # Filter by category
        if category:
            discussions = [d for d in discussions if d.get('category') == category]
        
        # Sort by last activity (pinned first)
        discussions.sort(
            key=lambda x: (not x.get('is_pinned', False), x.get('last_activity_at', '')),
            reverse=True
        )
        
        return [Discussion(**d) for d in discussions[offset:offset + limit]]
    
    def delete_discussion(self, discussion_id: str) -> bool:
        """Delete a discussion"""
        discussions = self._load_json(self.discussions_file)
        original_len = len(discussions)
        group_id = None
        
        for d in discussions:
            if d['id'] == discussion_id:
                group_id = d['group_id']
                break
        
        discussions = [d for d in discussions if d['id'] != discussion_id]
        
        if len(discussions) < original_len:
            self._save_json(self.discussions_file, discussions)
            # Also delete all replies
            self._delete_discussion_replies(discussion_id)
            if group_id:
                self._update_group_discussion_count(group_id)
            return True
        return False
    
    def _update_group_discussion_count(self, group_id: str):
        """Update discussion count for a group"""
        discussions = self.list_group_discussions(group_id)
        group = self.get_group(group_id)
        if group:
            group.discussion_count = len(discussions)
            self.save_group(group)
    
    # ==================== REPLY OPERATIONS ====================
    
    def save_reply(self, reply: DiscussionReply) -> DiscussionReply:
        """Save or update a reply"""
        replies = self._load_json(self.replies_file)
        
        found = False
        for i, r in enumerate(replies):
            if r['id'] == reply.id:
                reply.updated_at = datetime.now()
                replies[i] = reply.model_dump()
                found = True
                break
        
        if not found:
            replies.append(reply.model_dump())
        
        self._save_json(self.replies_file, replies)
        
        # Update discussion reply count and last activity
        self._update_discussion_replies(reply.discussion_id)
        
        return reply
    
    def get_reply(self, reply_id: str) -> Optional[DiscussionReply]:
        """Get reply by ID"""
        replies = self._load_json(self.replies_file)
        for r in replies:
            if r['id'] == reply_id:
                return DiscussionReply(**r)
        return None
    
    def list_discussion_replies(
        self,
        discussion_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[DiscussionReply]:
        """List replies for a discussion"""
        replies = self._load_json(self.replies_file)
        
        # Filter by discussion
        replies = [r for r in replies if r['discussion_id'] == discussion_id]
        
        # Sort by creation time (accepted answer first)
        replies.sort(
            key=lambda x: (not x.get('is_accepted_answer', False), x.get('created_at', '')),
            reverse=False
        )
        
        return [DiscussionReply(**r) for r in replies[offset:offset + limit]]
    
    def delete_reply(self, reply_id: str) -> bool:
        """Delete a reply"""
        replies = self._load_json(self.replies_file)
        original_len = len(replies)
        discussion_id = None
        
        for r in replies:
            if r['id'] == reply_id:
                discussion_id = r['discussion_id']
                break
        
        replies = [r for r in replies if r['id'] != reply_id]
        
        if len(replies) < original_len:
            self._save_json(self.replies_file, replies)
            if discussion_id:
                self._update_discussion_replies(discussion_id)
            return True
        return False
    
    def _delete_discussion_replies(self, discussion_id: str):
        """Delete all replies for a discussion"""
        replies = self._load_json(self.replies_file)
        replies = [r for r in replies if r['discussion_id'] != discussion_id]
        self._save_json(self.replies_file, replies)
    
    def _update_discussion_replies(self, discussion_id: str):
        """Update reply count and last activity for a discussion"""
        replies = self.list_discussion_replies(discussion_id)
        discussion = self.get_discussion(discussion_id)
        if discussion:
            discussion.reply_count = len(replies)
            discussion.last_activity_at = datetime.now()
            self.save_discussion(discussion)
    
    # ==================== UTILITY METHODS ====================
    
    def _load_json(self, file_path: Path) -> List[Dict]:
        """Load JSON data from file"""
        if not file_path.exists():
            return []
        
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def _save_json(self, file_path: Path, data: List[Dict]):
        """Save JSON data to file"""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)


# Global storage instance
social_storage = SocialStorage()
