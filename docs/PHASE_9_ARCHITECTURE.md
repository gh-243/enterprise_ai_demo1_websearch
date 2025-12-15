# 🤝 Phase 9: Collaborative Learning & Social Features

## Overview

Phase 9 transforms the Student Assistant from an individual learning tool into a **collaborative learning platform** where students can form study groups, participate in discussions, share resources, and provide peer feedback.

### Key Features

1. **Study Groups** 👥
   - Create and join study groups
   - Group-specific document libraries
   - Shared notes and resources
   - Group chat and collaboration

2. **Discussion Forums** 💬
   - Threaded discussions on topics
   - Question & Answer format
   - Upvoting and reactions
   - Best answer selection

3. **Peer Review** ⭐
   - Rate and review shared content
   - Comment on notes and study guides
   - Collaborative quiz creation
   - Feedback and suggestions

4. **Resource Sharing** 📚
   - Share documents within groups
   - Share study guides and notes
   - Collaborative annotations
   - Access control and permissions

---

## Architecture

### Database Schema

#### Users Table
```python
class User(BaseModel):
    """User profile for collaborative features"""
    id: str
    username: str
    email: str
    display_name: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    created_at: datetime
    last_active: datetime
```

#### Study Groups
```python
class StudyGroup(BaseModel):
    """Study group for collaborative learning"""
    id: str
    name: str
    description: str
    created_by: str  # user_id
    created_at: datetime
    updated_at: datetime
    is_public: bool = False
    max_members: int = 50
    tags: List[str] = []
    
class GroupMembership(BaseModel):
    """User membership in a study group"""
    id: str
    group_id: str
    user_id: str
    role: str  # 'owner', 'admin', 'member'
    joined_at: datetime
    status: str  # 'active', 'invited', 'banned'
```

#### Discussions
```python
class Discussion(BaseModel):
    """Discussion thread in a study group"""
    id: str
    group_id: str
    author_id: str
    title: str
    content: str
    category: str  # 'question', 'discussion', 'announcement'
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime
    is_pinned: bool = False
    is_locked: bool = False
    views: int = 0
    
class DiscussionReply(BaseModel):
    """Reply to a discussion"""
    id: str
    discussion_id: str
    author_id: str
    content: str
    created_at: datetime
    updated_at: datetime
    is_accepted_answer: bool = False
    upvotes: int = 0
    downvotes: int = 0
```

#### Peer Reviews
```python
class PeerReview(BaseModel):
    """Peer review for shared content"""
    id: str
    content_type: str  # 'note', 'study_guide', 'quiz'
    content_id: str
    reviewer_id: str
    rating: int  # 1-5 stars
    comment: str
    helpful_count: int = 0
    created_at: datetime
    updated_at: datetime
    
class ContentShare(BaseModel):
    """Shared content in a group"""
    id: str
    group_id: str
    owner_id: str
    content_type: str  # 'note', 'study_guide', 'quiz', 'document'
    content_id: str
    shared_at: datetime
    permissions: str  # 'view', 'comment', 'edit'
```

---

## API Endpoints

### Study Groups

```
POST   /v1/social/groups                    # Create group
GET    /v1/social/groups                    # List all public groups
GET    /v1/social/groups/{group_id}         # Get group details
PUT    /v1/social/groups/{group_id}         # Update group
DELETE /v1/social/groups/{group_id}         # Delete group

POST   /v1/social/groups/{group_id}/join    # Join group
POST   /v1/social/groups/{group_id}/leave   # Leave group
GET    /v1/social/groups/{group_id}/members # List members
POST   /v1/social/groups/{group_id}/invite  # Invite user
DELETE /v1/social/groups/{group_id}/members/{user_id}  # Remove member
```

### Discussions

```
POST   /v1/social/groups/{group_id}/discussions              # Create discussion
GET    /v1/social/groups/{group_id}/discussions              # List discussions
GET    /v1/social/discussions/{discussion_id}                # Get discussion
PUT    /v1/social/discussions/{discussion_id}                # Update discussion
DELETE /v1/social/discussions/{discussion_id}                # Delete discussion

POST   /v1/social/discussions/{discussion_id}/replies        # Add reply
GET    /v1/social/discussions/{discussion_id}/replies        # List replies
PUT    /v1/social/replies/{reply_id}                        # Update reply
DELETE /v1/social/replies/{reply_id}                        # Delete reply

POST   /v1/social/replies/{reply_id}/upvote                 # Upvote reply
POST   /v1/social/replies/{reply_id}/downvote               # Downvote reply
POST   /v1/social/replies/{reply_id}/accept                 # Mark as answer
```

### Peer Reviews

```
POST   /v1/social/reviews                   # Create review
GET    /v1/social/reviews                   # List reviews for content
GET    /v1/social/reviews/{review_id}       # Get review
PUT    /v1/social/reviews/{review_id}       # Update review
DELETE /v1/social/reviews/{review_id}       # Delete review

POST   /v1/social/reviews/{review_id}/helpful  # Mark review helpful
```

### Resource Sharing

```
POST   /v1/social/groups/{group_id}/share   # Share content
GET    /v1/social/groups/{group_id}/shared  # List shared content
DELETE /v1/social/shares/{share_id}         # Unshare content

GET    /v1/social/shares/{share_id}         # Access shared content
POST   /v1/social/shares/{share_id}/comment # Comment on shared content
```

### User Profile

```
GET    /v1/social/users/{user_id}           # Get user profile
PUT    /v1/social/users/{user_id}           # Update profile
GET    /v1/social/users/{user_id}/activity  # Get user activity
GET    /v1/social/users/{user_id}/groups    # Get user's groups
```

---

## Real-time Features (WebSockets)

### WebSocket Events

```python
# Client -> Server
{
    "type": "join_group",
    "group_id": "group_123"
}

{
    "type": "send_message",
    "group_id": "group_123",
    "content": "Hello everyone!"
}

{
    "type": "typing",
    "group_id": "group_123"
}

# Server -> Client
{
    "type": "message",
    "group_id": "group_123",
    "author": {...},
    "content": "Hello!",
    "timestamp": "2025-11-05T12:00:00Z"
}

{
    "type": "user_joined",
    "group_id": "group_123",
    "user": {...}
}

{
    "type": "typing_indicator",
    "group_id": "group_123",
    "user_id": "user_456"
}

{
    "type": "notification",
    "message": "New reply to your discussion",
    "link": "/discussions/123"
}
```

---

## Implementation Files

### Backend Structure

```
src/
├── models/
│   ├── social.py              # User, Group, Discussion models
│   ├── membership.py          # GroupMembership, Role models
│   └── review.py              # PeerReview, ContentShare models
│
├── services/
│   ├── group_service.py       # Study group logic
│   ├── discussion_service.py # Discussion management
│   ├── review_service.py      # Peer review logic
│   └── notification_service.py # Notifications
│
├── api/
│   ├── social_router.py       # REST API endpoints
│   └── websocket_router.py    # WebSocket handler
│
├── storage/
│   ├── social_db.py           # Social data persistence
│   └── cache.py               # Redis cache for real-time
│
└── websockets/
    ├── connection_manager.py  # WebSocket connections
    ├── group_chat.py          # Group chat handler
    └── notifications.py       # Push notifications
```

### Data Storage

```
data/
├── social/
│   ├── users.json            # User profiles
│   ├── groups.json           # Study groups
│   ├── memberships.json      # Group memberships
│   ├── discussions.json      # Discussion threads
│   ├── replies.json          # Discussion replies
│   ├── reviews.json          # Peer reviews
│   └── shares.json           # Shared content
```

---

## Features in Detail

### 1. Study Groups

**Create Group:**
```python
POST /v1/social/groups
{
    "name": "CS101 Study Group",
    "description": "Study group for Computer Science 101",
    "is_public": true,
    "tags": ["computer-science", "programming", "python"]
}
```

**Join Group:**
```python
POST /v1/social/groups/{group_id}/join
# Adds current user to group
```

**Group Chat (WebSocket):**
```javascript
ws.send(JSON.stringify({
    type: 'send_message',
    group_id: 'group_123',
    content: 'Anyone want to study for the exam?'
}));
```

### 2. Discussions

**Create Discussion:**
```python
POST /v1/social/groups/{group_id}/discussions
{
    "title": "How do I implement binary search?",
    "content": "I'm struggling with the recursive approach...",
    "category": "question",
    "tags": ["algorithms", "python"]
}
```

**Reply to Discussion:**
```python
POST /v1/social/discussions/{discussion_id}/replies
{
    "content": "Here's how I did it...\n```python\ndef binary_search..."
}
```

**Mark Best Answer:**
```python
POST /v1/social/replies/{reply_id}/accept
# Marks reply as accepted answer
```

### 3. Peer Reviews

**Review Study Guide:**
```python
POST /v1/social/reviews
{
    "content_type": "study_guide",
    "content_id": "guide_789",
    "rating": 5,
    "comment": "Excellent summary! Very helpful for exam prep."
}
```

**View Reviews:**
```python
GET /v1/social/reviews?content_type=study_guide&content_id=guide_789
```

### 4. Resource Sharing

**Share Note with Group:**
```python
POST /v1/social/groups/{group_id}/share
{
    "content_type": "note",
    "content_id": "note_456",
    "permissions": "view"  # 'view', 'comment', or 'edit'
}
```

**Access Shared Content:**
```python
GET /v1/social/shares/{share_id}
# Returns the shared content if user has permission
```

---

## UI Components

### Study Groups Tab

```html
<!-- Group List -->
<div class="groups-grid">
    <div class="group-card">
        <h3>CS101 Study Group</h3>
        <p>23 members • 45 discussions</p>
        <button onclick="joinGroup('group_123')">Join Group</button>
    </div>
</div>

<!-- Group Chat -->
<div class="group-chat">
    <div class="chat-messages" id="chat-messages"></div>
    <input type="text" id="message-input" placeholder="Type a message...">
</div>
```

### Discussions Tab

```html
<!-- Discussion List -->
<div class="discussion-list">
    <div class="discussion-item">
        <h4>How do I implement binary search?</h4>
        <p>5 replies • Asked by @john • 2 hours ago</p>
        <span class="badge">Question</span>
    </div>
</div>

<!-- Discussion View -->
<div class="discussion-view">
    <div class="discussion-content">
        <h2>How do I implement binary search?</h2>
        <p>I'm struggling with the recursive approach...</p>
    </div>
    <div class="replies">
        <!-- Replies here -->
    </div>
</div>
```

### Peer Reviews

```html
<!-- Review Form -->
<div class="review-form">
    <h3>Review this Study Guide</h3>
    <div class="star-rating" id="rating"></div>
    <textarea placeholder="Leave a comment..."></textarea>
    <button onclick="submitReview()">Submit Review</button>
</div>

<!-- Reviews List -->
<div class="reviews-list">
    <div class="review-card">
        <div class="review-header">
            <span class="stars">⭐⭐⭐⭐⭐</span>
            <span class="author">@alice</span>
        </div>
        <p>Excellent summary! Very helpful for exam prep.</p>
    </div>
</div>
```

---

## Security & Permissions

### Permission Levels

1. **Group Owner**
   - Full control over group
   - Can delete group
   - Can promote/demote admins

2. **Group Admin**
   - Can manage members
   - Can moderate discussions
   - Can pin/lock threads

3. **Group Member**
   - Can post discussions
   - Can reply to threads
   - Can share content

### Access Control

```python
def check_group_access(user_id: str, group_id: str, required_role: str = "member"):
    """Check if user has required access to group"""
    membership = get_membership(user_id, group_id)
    if not membership:
        raise PermissionError("Not a member of this group")
    
    role_hierarchy = {"owner": 3, "admin": 2, "member": 1}
    if role_hierarchy[membership.role] < role_hierarchy[required_role]:
        raise PermissionError(f"Requires {required_role} role")
    
    return True
```

---

## Testing Strategy

### Unit Tests

```python
# Test group creation
def test_create_study_group():
    group = create_group(
        user_id="user_123",
        name="Test Group",
        description="Test"
    )
    assert group.created_by == "user_123"
    assert group.name == "Test Group"

# Test permissions
def test_group_permissions():
    # Only group owner can delete
    with pytest.raises(PermissionError):
        delete_group(group_id="group_123", user_id="non_owner")
```

### Integration Tests

```python
# Test discussion workflow
def test_discussion_workflow():
    # Create discussion
    discussion = create_discussion(...)
    
    # Add reply
    reply = add_reply(discussion.id, ...)
    
    # Upvote reply
    upvote_reply(reply.id, user_id=...)
    
    # Mark as answer
    mark_answer(reply.id, discussion.author_id)
    
    assert reply.is_accepted_answer == True
```

### WebSocket Tests

```python
# Test real-time messaging
async def test_group_chat():
    async with websocket_connect("/ws") as ws:
        # Join group
        await ws.send_json({"type": "join_group", "group_id": "group_123"})
        
        # Send message
        await ws.send_json({"type": "send_message", "content": "Hello"})
        
        # Receive message
        msg = await ws.receive_json()
        assert msg["type"] == "message"
        assert msg["content"] == "Hello"
```

---

## Performance Considerations

### Caching Strategy

```python
# Cache frequently accessed data
@cache(ttl=300)  # 5 minutes
def get_group_members(group_id: str):
    """Cache group members list"""
    return load_group_members(group_id)

@cache(ttl=60)  # 1 minute
def get_discussion_replies(discussion_id: str):
    """Cache discussion replies"""
    return load_replies(discussion_id)
```

### Pagination

```python
GET /v1/social/groups/{group_id}/discussions?page=1&limit=20
GET /v1/social/discussions/{id}/replies?page=1&limit=50
```

### Real-time Optimization

- Use Redis pub/sub for WebSocket broadcasting
- Batch notifications to reduce database writes
- Throttle typing indicators (max 1 per 3 seconds)
- Limit concurrent WebSocket connections per user

---

## Metrics & Analytics

### Track Key Metrics

1. **Engagement**
   - Active groups
   - Messages per day
   - Discussion participation rate

2. **Content Quality**
   - Average review ratings
   - Helpful content count
   - Most shared resources

3. **User Activity**
   - Active users per group
   - Average session time
   - Reply response time

---

## Phase 9 Roadmap

### Week 1: Foundation
- ✅ Design architecture
- ✅ Create database schema
- ✅ Build data models
- ⬜ Implement basic CRUD

### Week 2: Core Features
- ⬜ Study groups backend
- ⬜ Discussion system
- ⬜ Peer reviews
- ⬜ REST API

### Week 3: Real-time
- ⬜ WebSocket infrastructure
- ⬜ Group chat
- ⬜ Live notifications
- ⬜ Presence indicators

### Week 4: Frontend & Testing
- ⬜ UI components
- ⬜ Integration tests
- ⬜ Load testing
- ⬜ Documentation

---

## Success Criteria

✅ **Phase 9 Complete When:**
1. Students can create and join study groups
2. Real-time group chat works smoothly
3. Discussions support threaded replies
4. Peer reviews and ratings functional
5. Resource sharing with permissions
6. WebSocket notifications working
7. All features tested and documented
8. UI integrated in student.html

---

**Next Steps:** Let's start building the data models and database schema! 🚀
