
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q
import uuid

User = get_user_model()

# ============================================================================
# POSTS - Admin-only content
# ============================================================================
class Post(models.Model):
    """
    DRF content posts created by admins.
    Users can comment and interact.
    """
    TOPIC_CHOICES = [
        ('serializers', 'Serializers'),
        ('views', 'Views & ViewSets'),
        ('authentication', 'Authentication & JWT'),
        ('permissions', 'Permissions & Throttling'),
        ('pagination', 'Pagination'),
        ('filtering', 'Filtering & Searching'),
        ('validation', 'Validation'),
        ('advanced', 'Advanced Topics'),
        ('best_practices', 'Best Practices'),
        ('troubleshooting', 'Troubleshooting'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic info
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()  # Markdown supported
    excerpt = models.CharField(max_length=500, blank=True)
    
    # Organization
    topic = models.CharField(max_length=50, choices=TOPIC_CHOICES)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags")
    
    # Author (admin)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    
    # Status
    is_published = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)  # Featured on homepage
    
    # Metadata
    views_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['topic', '-published_at']),
            models.Index(fields=['difficulty', '-published_at']),
            models.Index(fields=['is_published', '-published_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Auto-set published_at
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)


# ============================================================================
# COMMENTS - User interactions (threaded)
# ============================================================================
class Comment(models.Model):
    """
    Comments on posts with reply threading.
    Users can ask questions, get answers, reply to each other.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relationship
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    parent_comment = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies'
    )
    
    # Content
    content = models.TextField()
    
    # Metadata
    is_question = models.BooleanField(default=False)  # Is this a question?
    is_answer = models.BooleanField(default=False)    # Is this an answer?
    
    # Engagement
    likes_count = models.IntegerField(default=0)
    is_pinned = models.BooleanField(default=False)    # Admin pins important answers
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Editing
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-likes_count', 'created_at']
        indexes = [
            models.Index(fields=['post', 'created_at']),
            models.Index(fields=['author', 'created_at']),
            models.Index(fields=['parent_comment', 'created_at']),
        ]
    
    def __str__(self):
        return f"Comment by {self.author} on {self.post.title}"
    
    def get_replies(self):
        """Get all direct replies to this comment"""
        return self.replies.all().order_by('-likes_count', 'created_at')
    
    def is_top_level(self):
        """Is this a top-level comment (not a reply)?"""
        return self.parent_comment is None


# ============================================================================
# NOTIFICATIONS - User notifications
# ============================================================================
class Notification(models.Model):
    """
    Notifications for user interactions.
    """
    NOTIFICATION_TYPES = [
        ('reply_to_comment', 'Someone replied to your comment'),
        ('answer_to_question', 'Someone answered your question'),
        ('mention', 'You were mentioned'),
        ('new_post', 'New post in your favorite topic'),
        ('post_update', 'A post you commented on was updated'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # User receiving notification
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    
    # What triggered the notification
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    
    # Who triggered it
    triggered_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='triggered_notifications',
        null=True,
        blank=True
    )
    
    # Content
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.notification_type} - {self.title}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.read_at = timezone.now()
        self.save()


# ============================================================================
# RESOURCES - Learning paths
# ============================================================================
class Resource(models.Model):
    """
    Learning resources for each topic.
    Links to YouTube, courses, docs, etc.
    """
    RESOURCE_TYPES = [
        ('documentation', 'Official Documentation'),
        ('youtube', 'YouTube Tutorial'),
        ('course', 'Online Course'),
        ('book', 'Book'),
        ('article', 'Article/Blog'),
        ('github', 'GitHub Repository'),
        ('tool', 'Tool/Library'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Topic this resource covers
    topic = models.CharField(
        max_length=50,
        choices=Post.TOPIC_CHOICES
    )
    difficulty = models.CharField(
        max_length=20,
        choices=Post.DIFFICULTY_CHOICES
    )
    
    # Resource info
    title = models.CharField(max_length=200)
    description = models.TextField()
    resource_type = models.CharField(max_length=50, choices=RESOURCE_TYPES)
    url = models.URLField()
    
    # Creator/Author
    author = models.CharField(max_length=200)
    
    # Metadata
    estimated_hours = models.FloatField(null=True, blank=True)  # How long to complete
    is_free = models.BooleanField(default=True)
    language = models.CharField(max_length=50, default='English')
    
    # Rating
    rating = models.FloatField(null=True, blank=True, help_text="1-5 stars")
    reviews_count = models.IntegerField(default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-rating', '-reviews_count', 'title']
        indexes = [
            models.Index(fields=['topic', 'difficulty']),
            models.Index(fields=['topic', '-rating']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_resource_type_display()})"


# ============================================================================
# ADS - Advertising system
# ============================================================================
class Ad(models.Model):
    """
    Ads displayed below posts.
    Contextual ads for learning resources.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Ad info
    title = models.CharField(max_length=200)
    description = models.TextField()
    cta_text = models.CharField(max_length=100, default="Learn More")  # Call-to-action
    url = models.URLField()
    
    # Where to show
    topic = models.CharField(
        max_length=50,
        choices=Post.TOPIC_CHOICES
    )
    difficulty = models.CharField(
        max_length=20,
        choices=Post.DIFFICULTY_CHOICES
    )
    
    # Media
    image_url = models.URLField(blank=True)
    
    # Stats
    impressions = models.IntegerField(default=0)  # Times shown
    clicks = models.IntegerField(default=0)        # Times clicked
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['topic', 'is_active']),
            models.Index(fields=['difficulty', 'is_active']),
        ]
    
    def __str__(self):
        return self.title
    
    def click_through_rate(self):
        """Calculate CTR"""
        if self.impressions == 0:
            return 0
        return (self.clicks / self.impressions) * 100


# ============================================================================
# LIKES/VOTES - User reactions
# ============================================================================
class CommentLike(models.Model):
    """
    Tracks which users liked which comments.
    Prevents duplicate likes.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='liked_by')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('comment', 'user')  # One like per user per comment
        indexes = [
            models.Index(fields=['comment', 'user']),
        ]
    
    def __str__(self):
        return f"{self.user} liked comment by {self.comment.author}"


# ============================================================================
# USER PROGRESS - Track what users know
# ============================================================================
class UserProgress(models.Model):
    """
    Track user's learning progress and skill level.
    """
    SKILL_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='progress')
    
    # Overall skill
    overall_level = models.CharField(
        max_length=20,
        choices=SKILL_LEVELS,
        default='beginner'
    )
    
    # Skills by topic
    learned_topics = models.JSONField(default=list)  # Topics user has learned
    # Format: [{'topic': 'serializers', 'level': 'intermediate', 'timestamp': '2024-01-01'}]
    
    # Stats
    posts_read = models.IntegerField(default=0)
    comments_made = models.IntegerField(default=0)
    questions_asked = models.IntegerField(default=0)
    answers_given = models.IntegerField(default=0)
    reputation = models.IntegerField(default=0)  # Like Stack Overflow
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "User Progress"
    
    def __str__(self):
        return f"{self.user}'s Progress - {self.overall_level}"
    
    def update_skill(self, topic, level):
        """Update a skill/topic level"""
        # Find if topic already exists
        for skill in self.learned_topics:
            if skill['topic'] == topic:
                skill['level'] = level
                skill['timestamp'] = timezone.now().isoformat()
                self.save()
                return
        
        # Add new topic
        self.learned_topics.append({
            'topic': topic,
            'level': level,
            'timestamp': timezone.now().isoformat()
        })
        self.save()