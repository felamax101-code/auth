
from django.urls import path
from . import views

app_name = 'smartpythonists'

urlpatterns = [
    # ========================================================================
    # POST ENDPOINTS
    # ========================================================================
    # List and create posts
    path(
        'posts/',
        views.PostListCreateView.as_view(),
        name='post-list-create'
    ),
    
    # Post detail, update, delete
    path(
        'posts/<uuid:post_id>/',
        views.PostDetailView.as_view(),
        name='post-detail'
    ),
    
    # Featured posts
    path(
        'posts/featured/',
        views.PostFeaturedView.as_view(),
        name='post-featured'
    ),
    
    # ========================================================================
    # COMMENT ENDPOINTS
    # ========================================================================
    # List and create comments on a post
    path(
        'posts/<uuid:post_id>/comments/',
        views.CommentListCreateView.as_view(),
        name='comment-list-create'
    ),
    
    # Comment detail, update, delete
    path(
        'posts/<uuid:post_id>/comments/<uuid:comment_id>/',
        views.CommentDetailView.as_view(),
        name='comment-detail'
    ),
    
    # Like/unlike comment
    path(
        'posts/<uuid:post_id>/comments/<uuid:comment_id>/like/',
        views.CommentLikeView.as_view(),
        name='comment-like'
    ),
    
    # ========================================================================
    # NOTIFICATION ENDPOINTS
    # ========================================================================
    # List user notifications
    path(
        'notifications/',
        views.NotificationListView.as_view(),
        name='notification-list'
    ),
    
    # Mark notifications as read
    path(
        'notifications/mark-read/',
        views.NotificationMarkReadView.as_view(),
        name='notification-mark-read'
    ),
    
    # Notification detail and delete
    path(
        'notifications/<uuid:notification_id>/',
        views.NotificationDetailView.as_view(),
        name='notification-detail'
    ),
    
    # ========================================================================
    # RESOURCE ENDPOINTS
    # ========================================================================
    # List and create resources
    path(
        'resources/',
        views.ResourceListCreateView.as_view(),
        name='resource-list-create'
    ),
    
    # Resources by topic
    path(
        'resources/topic/<str:topic>/',
        views.ResourceTopicView.as_view(),
        name='resource-topic'
    ),
    
    # ========================================================================
    # AD ENDPOINTS
    # ========================================================================
    # List ads
    path(
        'ads/',
        views.AdListView.as_view(),
        name='ad-list'
    ),
    
    # Track ad click
    path(
        'ads/click/',
        views.AdClickTrackView.as_view(),
        name='ad-click'
    ),
    
    # ========================================================================
    # USER PROGRESS ENDPOINTS
    # ========================================================================
    # Get user progress
    path(
        'progress/',
        views.UserProgressView.as_view(),
        name='user-progress'
    ),
    
    # Get specific user progress
    path(
        'progress/<int:user_id>/',
        views.UserProgressView.as_view(),
        name='user-progress-detail'
    ),
    
    # Update user skill level
    path(
        'progress/update/',
        views.UserProgressUpdateView.as_view(),
        name='user-progress-update'
    ),
    
    # ========================================================================
    # UTILITY ENDPOINTS
    # ========================================================================
    # List all topics
    path(
        'topics/',
        views.TopicListView.as_view(),
        name='topic-list'
    ),
    
    # Dashboard statistics
    path(
        'stats/',
        views.DashboardStatsView.as_view(),
        name='dashboard-stats'
    ),
]


