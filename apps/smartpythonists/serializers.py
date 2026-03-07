from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import (
    Post, Comment, Notification, Resource, Ad,
    CommentLike, UserProgress
)

User = get_user_model()

# ============================================================================
# USER SERIALIZERS
# ============================================================================
class UserBasicSerializer(serializers.ModelSerializer):
    """
    Basic user info (used in nested serializers).
    Don't expose sensitive data.
    """
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'role']
        read_only_fields = ['id', 'email', 'username', 'role']


class UserProfileSerializer(serializers.ModelSerializer):
    """
    User profile with learning progress.
    """
    progress = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'phone',
            'profile_picture', 'role', 'date_joined',
            'last_login_at', 'progress'
        ]
        read_only_fields = ['id', 'email', 'username', 'date_joined', 'last_login_at']
    
    def get_progress(self, obj):
        """Get user's progress if it exists"""
        try:
            progress = obj.progress
            return UserProgressSerializer(progress).data
        except UserProgress.DoesNotExist:
            return None


# ============================================================================
# POST SERIALIZERS
# ============================================================================
class PostListSerializer(serializers.ModelSerializer):
    """
    Simplified post for listing (home page).
    """
    author = UserBasicSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'excerpt', 'topic',
            'difficulty', 'author', 'views_count',
            'comments_count', 'is_featured', 'published_at'
        ]
        read_only_fields = ['id', 'views_count', 'published_at']
    
    def get_comments_count(self, obj):
        """Get comment count"""
        return obj.comments.count()


class PostDetailSerializer(serializers.ModelSerializer):
    """
    Full post detail with all information.
    """
    author = UserBasicSerializer(read_only=True)
    comments = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    ads = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'content', 'excerpt',
            'topic', 'difficulty', 'tags', 'author',
            'views_count', 'is_featured', 'is_published',
            'created_at', 'updated_at', 'published_at',
            'comments_count', 'comments', 'ads'
        ]
        read_only_fields = [
            'id', 'slug', 'views_count', 'created_at',
            'updated_at', 'published_at'
        ]
    
    def get_comments(self, obj):
        """Get top-level comments (not replies)"""
        comments = obj.comments.filter(parent_comment__isnull=True)
        return CommentDetailSerializer(comments, many=True).data
    
    def get_comments_count(self, obj):
        """Get total comment count (including replies)"""
        return obj.comments.count()
    
    def get_ads(self, obj):
        """Get relevant ads for this post"""
        ads = Ad.objects.filter(
            topic=obj.topic,
            difficulty=obj.difficulty,
            is_active=True
        )
        return AdSerializer(ads, many=True).data


class PostCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating posts (admin only).
    """
    class Meta:
        model = Post
        fields = [
            'title', 'slug', 'content', 'excerpt',
            'topic', 'difficulty', 'tags', 'is_published',
            'is_featured'
        ]
    
    def validate_slug(self, value):
        """Ensure slug is unique"""
        if self.instance:
            # Editing: allow same slug
            if Post.objects.filter(slug=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("This slug already exists.")
        else:
            # Creating: must be unique
            if Post.objects.filter(slug=value).exists():
                raise serializers.ValidationError("This slug already exists.")
        return value
    
    def validate_content(self, value):
        """Ensure content is not empty"""
        if not value or len(value.strip()) < 100:
            raise serializers.ValidationError("Content must be at least 100 characters.")
        return value
    
    def create(self, validated_data):
        """Create post with current user as author"""
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


# ============================================================================
# COMMENT SERIALIZERS
# ============================================================================
class CommentLikeSerializer(serializers.ModelSerializer):
    """
    Serializer for comment likes.
    """
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = CommentLike
        fields = ['id', 'user', 'created_at']
        read_only_fields = ['id', 'created_at']


class CommentReplySerializer(serializers.ModelSerializer):
    """
    Serializer for comment replies (simplified).
    """
    author = UserBasicSerializer(read_only=True)
    user_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'author', 'content', 'is_question',
            'is_answer', 'is_pinned', 'likes_count',
            'is_edited', 'created_at', 'updated_at',
            'user_liked'
        ]
        read_only_fields = [
            'id', 'author', 'likes_count', 'is_edited',
            'created_at', 'updated_at'
        ]
    
    def get_user_liked(self, obj):
        """Did current user like this comment?"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.liked_by.filter(user=request.user).exists()
        return False


class CommentDetailSerializer(serializers.ModelSerializer):
    """
    Full comment with nested replies.
    """
    author = UserBasicSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    user_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'author', 'content', 'is_question',
            'is_answer', 'is_pinned', 'likes_count',
            'is_edited', 'edited_at', 'created_at',
            'updated_at', 'replies', 'user_liked'
        ]
        read_only_fields = [
            'id', 'author', 'likes_count', 'is_edited',
            'edited_at', 'created_at', 'updated_at'
        ]
    
    def get_replies(self, obj):
        """Get all replies to this comment (recursively)"""
        replies = obj.get_replies()
        return CommentReplySerializer(replies, many=True, context=self.context).data
    
    def get_user_liked(self, obj):
        """Did current user like this comment?"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.liked_by.filter(user=request.user).exists()
        return False


class CommentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating comments.
    """
    class Meta:
        model = Comment
        fields = [
            'content', 'parent_comment', 'is_question', 'is_answer'
        ]
    
    def validate_content(self, value):
        """Ensure comment is not empty"""
        if not value or len(value.strip()) < 5:
            raise serializers.ValidationError("Comment must be at least 5 characters.")
        if len(value) > 5000:
            raise serializers.ValidationError("Comment cannot exceed 5000 characters.")
        return value
    
    def create(self, validated_data):
        """Create comment with current user as author"""
        # Get post from context
        request = self.context['request']
        post_id = self.context['view'].kwargs.get('post_id')
        
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise serializers.ValidationError("Post not found.")
        
        validated_data['author'] = request.user
        validated_data['post'] = post
        
        comment = super().create(validated_data)
        
        # Create notification if replying to someone
        if comment.parent_comment:
            # Notify parent comment author
            Notification.objects.create(
                user=comment.parent_comment.author,
                notification_type='reply_to_comment',
                post=post,
                comment=comment,
                triggered_by=request.user,
                title=f"{request.user.username} replied to your comment",
                description=f"On post: {post.title}"
            )
            
            # If this comment answers the parent question, notify
            if comment.parent_comment.is_question and comment.is_answer:
                Notification.objects.create(
                    user=comment.parent_comment.author,
                    notification_type='answer_to_question',
                    post=post,
                    comment=comment,
                    triggered_by=request.user,
                    title=f"{request.user.username} answered your question",
                    description=comment.content[:200]
                )
        
        return comment


class CommentUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating comments (users can only edit their own).
    """
    class Meta:
        model = Comment
        fields = ['content']
    
    def validate_content(self, value):
        """Ensure content is valid"""
        if not value or len(value.strip()) < 5:
            raise serializers.ValidationError("Comment must be at least 5 characters.")
        if len(value) > 5000:
            raise serializers.ValidationError("Comment cannot exceed 5000 characters.")
        return value
    
    def update(self, instance, validated_data):
        """Update comment and mark as edited"""
        instance.content = validated_data['content']
        instance.is_edited = True
        instance.edited_at = timezone.now()
        instance.save()
        return instance


# ============================================================================
# NOTIFICATION SERIALIZERS
# ============================================================================
class NotificationSerializer(serializers.ModelSerializer):
    """
    Notification serializer.
    """
    triggered_by = UserBasicSerializer(read_only=True)
    post_title = serializers.SerializerMethodField()
    comment_content = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'title', 'description',
            'triggered_by', 'post_title', 'comment_content',
            'is_read', 'created_at', 'read_at'
        ]
        read_only_fields = [
            'id', 'notification_type', 'title', 'description',
            'triggered_by', 'created_at', 'read_at'
        ]
    
    def get_post_title(self, obj):
        """Get related post title if exists"""
        if obj.post:
            return obj.post.title
        return None
    
    def get_comment_content(self, obj):
        """Get related comment content if exists"""
        if obj.comment:
            return obj.comment.content[:100]  # First 100 chars
        return None


class NotificationMarkReadSerializer(serializers.Serializer):
    """
    Serializer for marking notifications as read.
    """
    notification_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False
    )
    mark_all = serializers.BooleanField(required=False, default=False)
    
    def validate(self, data):
        """Ensure either notification_ids or mark_all is provided"""
        if not data.get('notification_ids') and not data.get('mark_all'):
            raise serializers.ValidationError(
                "Either provide notification_ids or set mark_all to True."
            )
        return data


# ============================================================================
# RESOURCE SERIALIZERS
# ============================================================================
class ResourceSerializer(serializers.ModelSerializer):
    """
    Serializer for learning resources.
    """
    added_by = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = Resource
        fields = [
            'id', 'topic', 'difficulty', 'title', 'description',
            'resource_type', 'url', 'author', 'estimated_hours',
            'is_free', 'language', 'rating', 'reviews_count',
            'added_by', 'created_at'
        ]
        read_only_fields = [
            'id', 'added_by', 'created_at'
        ]


class ResourceCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating resources (admin only).
    """
    class Meta:
        model = Resource
        fields = [
            'topic', 'difficulty', 'title', 'description',
            'resource_type', 'url', 'author', 'estimated_hours',
            'is_free', 'language', 'rating', 'reviews_count'
        ]
    
    def validate_url(self, value):
        """Ensure URL is valid"""
        if not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError("URL must start with http:// or https://")
        return value


# ============================================================================
# AD SERIALIZERS
# ============================================================================
class AdSerializer(serializers.ModelSerializer):
    """
    Serializer for ads.
    """
    ctr = serializers.SerializerMethodField()
    
    class Meta:
        model = Ad
        fields = [
            'id', 'title', 'description', 'cta_text', 'url',
            'topic', 'difficulty', 'image_url', 'impressions',
            'clicks', 'ctr', 'is_active', 'created_at'
        ]
        read_only_fields = [
            'id', 'impressions', 'clicks', 'ctr', 'created_at'
        ]
    
    def get_ctr(self, obj):
        """Get click-through rate"""
        return round(obj.click_through_rate(), 2)


class AdCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating ads (admin only).
    """
    class Meta:
        model = Ad
        fields = [
            'title', 'description', 'cta_text', 'url',
            'topic', 'difficulty', 'image_url', 'is_active'
        ]


class AdClickSerializer(serializers.Serializer):
    """
    Serializer for tracking ad clicks.
    """
    ad_id = serializers.UUIDField()
    
    def validate_ad_id(self, value):
        """Ensure ad exists"""
        if not Ad.objects.filter(id=value).exists():
            raise serializers.ValidationError("Ad not found.")
        return value


# ============================================================================
# USER PROGRESS SERIALIZERS
# ============================================================================
class UserProgressSerializer(serializers.ModelSerializer):
    """
    Serializer for user progress tracking.
    """
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = UserProgress
        fields = [
            'id', 'user', 'overall_level', 'learned_topics',
            'posts_read', 'comments_made', 'questions_asked',
            'answers_given', 'reputation', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'posts_read', 'comments_made',
            'questions_asked', 'answers_given', 'reputation',
            'created_at', 'updated_at'
        ]


class UserProgressUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating user skill/topic level.
    """
    topic = serializers.ChoiceField(
        choices=[choice[0] for choice in Post.TOPIC_CHOICES]
    )
    level = serializers.ChoiceField(
        choices=[choice[0] for choice in UserProgress.SKILL_LEVELS]
    )


# ============================================================================
# COMBINED SERIALIZERS
# ============================================================================
class PostWithCommentsSerializer(serializers.ModelSerializer):
    """
    Full post detail with comments - used for detail view.
    """
    author = UserBasicSerializer(read_only=True)
    top_comments = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    ads = serializers.SerializerMethodField()
    user_can_edit = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'content', 'excerpt',
            'topic', 'difficulty', 'tags', 'author',
            'views_count', 'is_featured', 'published_at',
            'comments_count', 'top_comments', 'ads',
            'user_can_edit'
        ]
        read_only_fields = [
            'id', 'views_count', 'published_at'
        ]
    
    def get_top_comments(self, obj):
        """Get top-level comments sorted by likes"""
        comments = obj.comments.filter(
            parent_comment__isnull=True
        ).order_by('-is_pinned', '-likes_count', 'created_at')
        return CommentDetailSerializer(comments, many=True, context=self.context).data
    
    def get_comments_count(self, obj):
        """Total comment count"""
        return obj.comments.count()
    
    def get_ads(self, obj):
        """Get relevant ads"""
        ads = Ad.objects.filter(
            topic=obj.topic,
            difficulty=obj.difficulty,
            is_active=True
        )
        return AdSerializer(ads, many=True).data
    
    def get_user_can_edit(self, obj):
        """Can current user edit this post?"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.is_staff and obj.author == request.user
        return False


# ============================================================================
# UTILITY SERIALIZERS
# ============================================================================
class BulkActionSerializer(serializers.Serializer):
    """
    Serializer for bulk actions on comments/posts.
    """
    ids = serializers.ListField(
        child=serializers.UUIDField()
    )
    action = serializers.ChoiceField(
        choices=['delete', 'pin', 'unpin', 'hide', 'unhide']
    )
    
    def validate_ids(self, value):
        """Ensure at least one ID"""
        if not value:
            raise serializers.ValidationError("At least one ID is required.")
        if len(value) > 100:
            raise serializers.ValidationError("Maximum 100 items per action.")
        return value