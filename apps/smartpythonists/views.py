from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone
from django.core.paginator import Paginator

from .models import (
    Post, Comment, Notification, Resource, Ad,
    CommentLike, UserProgress
)
from .serializers import (
    PostListSerializer, PostDetailSerializer, PostCreateSerializer,
    CommentDetailSerializer, CommentCreateSerializer, CommentUpdateSerializer,
    NotificationSerializer, NotificationMarkReadSerializer,
    ResourceSerializer, ResourceCreateSerializer,
    AdSerializer, AdCreateSerializer, AdClickSerializer,
    UserProgressSerializer, UserProgressUpdateSerializer,
    PostWithCommentsSerializer
)
from .permissions import (
    IsAdminOrReadOnly, IsPostAuthorOrAdmin, IsCommentAuthorOrAdmin,
    IsAuthenticatedForComments, IsAdminOnly, CanEditComment, CanDeleteComment
)


# ============================================================================
# POST VIEWS
# ============================================================================
class PostListCreateView(APIView):
    """
    GET: List all published posts (paginated)
    POST: Create new post (admin only)
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """List posts with pagination and filters"""
        # Get query parameters
        topic = request.query_params.get('topic')
        difficulty = request.query_params.get('difficulty')
        search = request.query_params.get('search')
        page = request.query_params.get('page', 1)
        per_page = int(request.query_params.get('per_page', 10))
        
        # Build query
        queryset = Post.objects.filter(is_published=True).order_by('-published_at')
        
        # Apply filters
        if topic:
            queryset = queryset.filter(topic=topic)
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search) |
                Q(tags__icontains=search)
            )
        
        # Pagination
        try:
            paginator = Paginator(queryset, per_page)
            posts_page = paginator.get_page(page)
            
            serializer = PostListSerializer(posts_page, many=True)
            
            return Response({
                'count': paginator.count,
                'total_pages': paginator.num_pages,
                'current_page': int(page),
                'results': serializer.data
            })
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def post(self, request):
        """Create new post (admin only)"""
        # Check permission
        if not request.user.is_authenticated or not request.user.is_staff:
            return Response(
                {'detail': 'Only admins can create posts.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = PostCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetailView(APIView):
    """
    GET: Retrieve single post with comments
    PUT: Update post (author or admin only)
    DELETE: Delete post (author or admin only)
    """
    def get(self, request, post_id):
        """Get post detail with comments"""
        post = get_object_or_404(Post, id=post_id, is_published=True)
        
        # Increment views count
        post.views_count += 1
        post.save(update_fields=['views_count'])
        
        serializer = PostWithCommentsSerializer(post, context={'request': request})
        return Response(serializer.data)
    
    def put(self, request, post_id):
        """Update post (author or admin only)"""
        post = get_object_or_404(Post, id=post_id)
        
        # Check permission
        if post.author != request.user and not request.user.is_staff:
            return Response(
                {'detail': 'You do not have permission to edit this post.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = PostCreateSerializer(
            post,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, post_id):
        """Delete post (author or admin only)"""
        post = get_object_or_404(Post, id=post_id)
        
        # Check permission
        if post.author != request.user and not request.user.is_staff:
            return Response(
                {'detail': 'You do not have permission to delete this post.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        post_title = post.title
        post.delete()
        
        return Response(
            {'detail': f'Post "{post_title}" deleted successfully.'},
            status=status.HTTP_204_NO_CONTENT
        )


class PostFeaturedView(APIView):
    """
    GET: List featured posts
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get featured posts"""
        posts = Post.objects.filter(
            is_published=True,
            is_featured=True
        ).order_by('-published_at')[:5]
        
        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data)


# ============================================================================
# COMMENT VIEWS
# ============================================================================
class CommentListCreateView(APIView):
    """
    GET: List comments for a post
    POST: Create comment on post (authenticated users)
    """
    def get(self, request, post_id):
        """Get all comments for a post"""
        post = get_object_or_404(Post, id=post_id)
        
        # Get top-level comments (not replies)
        comments = post.comments.filter(parent_comment__isnull=True).order_by(
            '-is_pinned', '-likes_count', 'created_at'
        )
        
        serializer = CommentDetailSerializer(
            comments,
            many=True,
            context={'request': request}
        )
        
        return Response({
            'post_id': str(post_id),
            'total_comments': post.comments.count(),
            'comments': serializer.data
        })
    
    def post(self, request, post_id):
        """Create comment on post"""
        # Check authentication
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'You must be logged in to comment.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Verify post exists
        post = get_object_or_404(Post, id=post_id)
        
        serializer = CommentCreateSerializer(
            data=request.data,
            context={
                'request': request,
                'view': self,
                'post_id': post_id
            }
        )
        
        if serializer.is_valid():
            comment = serializer.save()
            return Response(
                CommentDetailSerializer(comment, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDetailView(APIView):
    """
    GET: Retrieve comment with replies
    PUT: Update comment (author or admin only)
    DELETE: Delete comment (author or admin only)
    """
    def get(self, request, post_id, comment_id):
        """Get comment with replies"""
        comment = get_object_or_404(
            Comment,
            id=comment_id,
            post_id=post_id,
            parent_comment__isnull=True
        )
        
        serializer = CommentDetailSerializer(comment, context={'request': request})
        return Response(serializer.data)
    
    def put(self, request, post_id, comment_id):
        """Update comment"""
        comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)
        
        # Check permission
        if comment.author != request.user and not request.user.is_staff:
            return Response(
                {'detail': 'You can only edit your own comments.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = CommentUpdateSerializer(
            comment,
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                CommentDetailSerializer(comment, context={'request': request}).data
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, post_id, comment_id):
        """Delete comment"""
        comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)
        
        # Check permission
        if comment.author != request.user and not request.user.is_staff:
            return Response(
                {'detail': 'You can only delete your own comments.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        comment.delete()
        
        return Response(
            {'detail': 'Comment deleted successfully.'},
            status=status.HTTP_204_NO_CONTENT
        )


class CommentLikeView(APIView):
    """
    POST: Like a comment (authenticated users)
    DELETE: Unlike a comment
    """
   # permission_classes = [IsAuthenticated]
    
    def post(self, request, post_id, comment_id):
        """Like a comment"""
        comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)
        
        # Check if already liked
        like, created = CommentLike.objects.get_or_create(
            comment=comment,
            user=request.user
        )
        
        if created:
            # Increment likes count
            comment.likes_count += 1
            comment.save(update_fields=['likes_count'])
            
            return Response(
                {'detail': 'Comment liked.', 'likes_count': comment.likes_count},
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            {'detail': 'You already liked this comment.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def delete(self, request, post_id, comment_id):
        """Unlike a comment"""
        comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)
        
        try:
            like = CommentLike.objects.get(comment=comment, user=request.user)
            like.delete()
            
            # Decrement likes count
            comment.likes_count = max(0, comment.likes_count - 1)
            comment.save(update_fields=['likes_count'])
            
            return Response(
                {'detail': 'Comment unliked.', 'likes_count': comment.likes_count},
                status=status.HTTP_204_NO_CONTENT
            )
        except CommentLike.DoesNotExist:
            return Response(
                {'detail': 'You did not like this comment.'},
                status=status.HTTP_400_BAD_REQUEST
            )


# ============================================================================
# NOTIFICATION VIEWS
# ============================================================================
class NotificationListView(APIView):
    """
    GET: List user's notifications
    """
    #permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get user's notifications"""
        unread_only = request.query_params.get('unread', 'false').lower() == 'true'
        
        notifications = request.user.notifications.all().order_by('-created_at')
        
        if unread_only:
            notifications = notifications.filter(is_read=False)
        
        serializer = NotificationSerializer(notifications, many=True)
        
        return Response({
            'unread_count': request.user.notifications.filter(is_read=False).count(),
            'total_count': request.user.notifications.count(),
            'notifications': serializer.data
        })


class NotificationMarkReadView(APIView):
    """
    POST: Mark notifications as read
    """
    #permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Mark notifications as read"""
        serializer = NotificationMarkReadSerializer(data=request.data)
        
        if serializer.is_valid():
            if serializer.validated_data.get('mark_all'):
                # Mark all as read
                request.user.notifications.filter(is_read=False).update(
                    is_read=True,
                    read_at=timezone.now()
                )
                return Response(
                    {'detail': 'All notifications marked as read.'}
                )
            else:
                # Mark specific notifications
                notification_ids = serializer.validated_data.get('notification_ids', [])
                updated = request.user.notifications.filter(
                    id__in=notification_ids,
                    is_read=False
                ).update(
                    is_read=True,
                    read_at=timezone.now()
                )
                
                return Response({
                    'detail': f'{updated} notifications marked as read.'
                })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NotificationDetailView(APIView):
    """
    GET: Get single notification
    DELETE: Delete notification
    """
    #permission_classes = [IsAuthenticated]
    
    def get(self, request, notification_id):
        """Get single notification"""
        notification = get_object_or_404(
            Notification,
            id=notification_id,
            user=request.user
        )
        
        # Mark as read
        if not notification.is_read:
            notification.mark_as_read()
        
        serializer = NotificationSerializer(notification)
        return Response(serializer.data)
    
    def delete(self, request, notification_id):
        """Delete notification"""
        notification = get_object_or_404(
            Notification,
            id=notification_id,
            user=request.user
        )
        
        notification.delete()
        
        return Response(
            {'detail': 'Notification deleted.'},
            status=status.HTTP_204_NO_CONTENT
        )


# ============================================================================
# RESOURCE VIEWS
# ============================================================================
class ResourceListCreateView(APIView):
    """
    GET: List learning resources
    POST: Create resource (admin only)
    """
    def get(self, request):
        """List resources"""
        topic = request.query_params.get('topic')
        difficulty = request.query_params.get('difficulty')
        resource_type = request.query_params.get('type')
        
        resources = Resource.objects.filter(is_active=True).order_by(
            '-rating', '-reviews_count'
        )
        
        # Apply filters
        if topic:
            resources = resources.filter(topic=topic)
        if difficulty:
            resources = resources.filter(difficulty=difficulty)
        if resource_type:
            resources = resources.filter(resource_type=resource_type)
        
        serializer = ResourceSerializer(resources, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """Create resource (admin only)"""
        if not request.user.is_authenticated or not request.user.is_staff:
            return Response(
                {'detail': 'Only admins can create resources.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ResourceCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(added_by=request.user)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResourceTopicView(APIView):
    """
    GET: Get all resources for a specific topic
    """
    def get(self, request, topic):
        """Get resources by topic"""
        resources = Resource.objects.filter(
            topic=topic,
            is_active=True
        ).order_by('-rating', '-reviews_count')
        
        if not resources.exists():
            return Response(
                {'detail': f'No resources found for topic: {topic}'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ResourceSerializer(resources, many=True)
        return Response({
            'topic': topic,
            'total': resources.count(),
            'resources': serializer.data
        })


# ============================================================================
# AD VIEWS
# ============================================================================
class AdListView(APIView):
    """
    GET: List ads (contextual)
    """
    def get(self, request):
        """Get relevant ads"""
        topic = request.query_params.get('topic')
        difficulty = request.query_params.get('difficulty')
        
        ads = Ad.objects.filter(is_active=True)
        
        if topic and difficulty:
            ads = ads.filter(topic=topic, difficulty=difficulty)
        
        serializer = AdSerializer(ads, many=True)
        return Response(serializer.data)


class AdClickTrackView(APIView):
    """
    POST: Track ad click
    """
    def post(self, request):
        """Track ad click"""
        serializer = AdClickSerializer(data=request.data)
        
        if serializer.is_valid():
            ad = get_object_or_404(Ad, id=serializer.validated_data['ad_id'])
            
            # Increment click count
            ad.clicks += 1
            ad.save(update_fields=['clicks'])
            
            return Response({
                'detail': 'Ad click recorded.',
                'clicks': ad.clicks,
                'ctr': round(ad.click_through_rate(), 2)
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================================
# USER PROGRESS VIEWS
# ============================================================================
class UserProgressView(APIView):
    """
    GET: Get user's progress
    """
    #permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id=None):
        """Get user progress"""
        if user_id:
            # Get specific user's progress
            user = get_object_or_404(request.user.__class__, id=user_id)
        else:
            # Get current user's progress
            user = request.user
        
        # Create progress if doesn't exist
        progress, created = UserProgress.objects.get_or_create(user=user)
        
        serializer = UserProgressSerializer(progress)
        return Response(serializer.data)


class UserProgressUpdateView(APIView):
    """
    POST: Update user skill level
    """
   # permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Update skill level"""
        serializer = UserProgressUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            # Get or create progress
            progress, created = UserProgress.objects.get_or_create(
                user=request.user
            )
            
            # Update skill
            progress.update_skill(
                serializer.validated_data['topic'],
                serializer.validated_data['level']
            )
            
            return Response({
                'detail': 'Skill updated.',
                'progress': UserProgressSerializer(progress).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================================
# TOPIC/STATISTICS VIEWS
# ============================================================================
class TopicListView(APIView):
    """
    GET: List all topics with post counts
    """
    def get(self, request):
        """Get all topics"""
        topics = []
        for topic_choice, topic_name in Post.TOPIC_CHOICES:
            count = Post.objects.filter(
                topic=topic_choice,
                is_published=True
            ).count()
            topics.append({
                'id': topic_choice,
                'name': topic_name,
                'post_count': count
            })
        
        return Response(topics)


class DashboardStatsView(APIView):
    """
    GET: Get overall platform statistics
    """
    def get(self, request):
        """Get dashboard stats"""
        stats = {
            'total_posts': Post.objects.filter(is_published=True).count(),
            'total_comments': Comment.objects.count(),
            'total_resources': Resource.objects.filter(is_active=True).count(),
            'total_users': request.user.__class__.objects.count(),
            'active_discussions': Comment.objects.filter(is_question=True).count(),
        }
        
        return Response(stats)